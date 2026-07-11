from enum import Enum

from google import genai
from pydantic import BaseModel, Field 
from typing import List, Optional
from dotenv import load_dotenv
import os
import asyncio
from agent.functions.extract_claims import Claim
from agent.functions.research_claim import Evidence, research_claim

#takes one Claim and a list[Evidence] and returns one Verdict (label + justification + sources cited)
#v1: decide on source reliability purely with some prompt
#v2: use a source reliability model to score the sources and use that to HELP inform the verdict (not fully automate it)
#later (in orchestator): need a evidence dedupe before this step
class Label(str, Enum):
    SUPPORTED = "supported"
    REFUTED = "refuted"
    INSUFFICIENT = "not enough information"

class Verdict(BaseModel):
    label: Label = Field(description="The label assigned to the claim based on the evidence provided")
    justification: str = Field(description="A short explanation of why the claim was labeled as such, citing the evidence used to reach this conclusion")
    sources_cited: List[int] = Field(description="A list of source indices from the evidence list that were cited in the justification, indicating which pieces of evidence were used to support the verdict")
load_dotenv()
client = genai.Client()


async def evaluate_claim(input_claim: Claim, evidence_list: List[Evidence]) -> Verdict:
    #first, turn the evidence list into a string to feed into the prompt
    evidence_text = "\n".join([f"{i+1}. {evidence.content} (Source: {evidence.title}, URL: {evidence.url})" for i, evidence in enumerate(evidence_list)])
    evaluate_prompt = f"""
    You are a careful fact-checker. You will be given a single claim and a list of evidence snippets gathered from web searches. Your job is to decide whether the evidence supports the claim, refutes it, or is insufficient to decide.

    Assign exactly one label:
    - "supported": the evidence clearly confirms the claim is true.
    - "refuted": the evidence clearly shows the claim is false.
    - "not enough information": the evidence is missing, irrelevant, or too weak to decide either way.

    Important instructions for weighing evidence:
    - The evidence may contradict itself. Some snippets may repeat a popular myth or error as if it were true. Do not simply count how many snippets agree. Weigh the quality of the sources.
    - Prefer authoritative, primary, or expert sources (for example government agencies, encyclopedias, scientific organizations, established news outlets) over blogs, forums, social media posts, and commercial or promotional sites.
    - A claim being widely repeated does not make it true. If reliable sources contradict a common belief, trust the reliable sources.
    - If the claim is an opinion or value judgment rather than a checkable factual statement, use "not enough information".

    In your justification, explain your reasoning in two or three sentences. State which evidence led to your decision, and if the sources conflicted, say so and explain which you trusted and why.
    Your response fields shoudld be:
    - label: one of "supported", "refuted", or "not enough information"
    - justification: your above reasoning, with citations to the evidence you used  
    - sources_cited: a list of the indices of the evidence you cited in your justification, in the order you cited them. Use 1-based indexing (the first piece of evidence is 1, the second is 2, etc.)

    The claim:
    {input_claim.claim_text}

    The evidence:
    {evidence_text}
    """
    
    response = await client.aio.models.generate_content(
        model="gemini-2.5-flash", #change when not using free
        contents=[evaluate_prompt],
        config={
            "response_mime_type": "application/json",
            "response_schema": Verdict,
        }
    )
    return response.parsed


if __name__ == "__main__":
    test_claim = Claim(
        claim_text="The Great Wall of China is the only man-made structure visible from space with the naked eye",
        source_span="the Great Wall is the only man-made thing you can see from space"
    )
    test_evidence = asyncio.run(research_claim(test_claim, num_queries_per_claim=3))
    print("Evidence retrieved:")
    for i, evidence in enumerate(test_evidence):
        print(f"{i+1}. {evidence.content} (Source: {evidence.title}, URL: {evidence.url})")
    verdict = asyncio.run(evaluate_claim(test_claim, test_evidence))
    print(verdict)
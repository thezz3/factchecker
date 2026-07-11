#V1: base two-field object response, one field is the model attempting to send verbatim

#planned future versions: track where the claims are using offsets, use the source_spans (verbatims) from the model to idenity these offsets.
# solve the error from the source spans using fuzzy matching
from google import genai
from pydantic import BaseModel, Field 
from typing import List, Optional
from dotenv import load_dotenv
import asyncio




#structured response schema for claims

class Claim(BaseModel):
    claim_text: str = Field(description="A self-contained version of the claim, with pronouns and vague references resolved to what they refer to")
    source_span: str = Field(description="The claim copied exactly and verbatim from the input text, as an exact substring")

class Claims(BaseModel):
    claims: list[Claim] = Field(description="List of all claims found in the input text")
    #later: add the thing for v2 where it can reword the verbatim and STIL return the verbatim

load_dotenv()
client = genai.Client()
async def extract_claims(input_text: str) -> Claims:
    
    claim_prompt = """
    Extract every factual claim from the text below. A claim is a statement that asserts something is true and could in principle be checked against evidence. Include opinions and value judgments as claims too for now; do not filter them out.

    A claim may span multiple sentences. If a single claim is spread across parts of consecutive sentences, treat it as one claim.

    For each claim, return two fields:

    - source_span: the claim copied EXACTLY and VERBATIM from the text, character for character, with no rewording, no fixed typos, no added or removed words. This must be an exact substring of the original text so it can be located in the source.

    - claim_text: a clean, self-contained version of the same claim that makes sense on its own. Resolve pronouns and vague references (for example "it", "this", "the whole thing") into the specific thing they refer to, based on the surrounding context. The claim should be understandable without reading the rest of the text.

    Example: if the text says "Mount Everest is the tallest mountain. It's overrated.", the second claim's source_span is "It's overrated" and its claim_text is "Mount Everest is overrated".

    Do not add claims that are not in the text. Do not merge separate claims together.
    """
    #for v2 - make it return an object with claim_text (cleaned up claims text) and source_span - exact substring of where it's being pulled from
    response = await client.aio.models.generate_content(   #parallel - added asyncio
        model="gemini-2.5-flash", #change when not using free
        contents=[claim_prompt, input_text],
        config={
        "response_mime_type": "application/json",
        "response_schema": Claims,
        }
    )
    print("claims response:", response.parsed)
    return response.parsed


if __name__ == "__main__":
    with open("claims_test.txt", "r", encoding="utf-8") as file:
        content = file.read()
    input_text = content
    claims = []
    claims_response = asyncio.run(extract_claims(input_text))
    print(claims_response)
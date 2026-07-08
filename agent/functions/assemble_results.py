from google import genai
from pydantic import BaseModel, Field 
from typing import List, Optional
from dotenv import load_dotenv
import os 
from agent.functions.extract_claims import Claim
from agent.functions.research_claim import Evidence
from agent.functions.evaluate_claim import Verdict, Label


class Result(BaseModel):
    claim: Claim
    source_urls: List[str]
    label: str 
    justification: str

def assemble_result(claim: Claim, verdict: Verdict, evidence_list: List[Evidence]) -> Result:
    source_urls = [evidence_list[n-1].url for n in verdict.sources_cited]
    
    return Result(
        claim=claim,
        source_urls=source_urls,
        label=verdict.label.value,
        justification=verdict.justification
    )
from google import genai
from pydantic import BaseModel, Field 
from typing import List, Optional
from dotenv import load_dotenv

# RESEARCH_CLAIM: takes ONE claim and returns the vidence

class Evidence(BaseModel):
    evidence: list[str] = Field(description="")
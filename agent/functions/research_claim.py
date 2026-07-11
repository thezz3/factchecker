from google import genai
from pydantic import BaseModel, Field 
from typing import List, Optional
from dotenv import load_dotenv
from tavily import TavilyClient, AsyncTavilyClient
import os
import asyncio
#change WHEN RUNNING ON ORCHESTRATOR:
from agent.functions.extract_claims import Claim
# RESEARCH_CLAIM: takes ONE claim and returns the vidence
load_dotenv()
gemini_client = genai.Client()

tavily_client = AsyncTavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

class SearchQueries(BaseModel):
    search_queries: List[str]

class Evidence(BaseModel):
    query: str
    content: str
    title: str
    url: str
    score: float

async def research_claim(input_claim: Claim, num_queries_per_claim: int) -> List[Evidence]:
    print("input claim:", input_claim.claim_text)
    #first, turn the claim into searchable queries
    evidence_list = []
    input_claim = input_claim.claim_text
    query_prompt = f"""You are helping verify a factual claim by searching the web. Given the claim below, generate {num_queries_per_claim} distinct search queries that would surface evidence to confirm or refute it.

Make the queries different from each other so they cover different angles or sub-facts of the claim, rather than rephrasings of the same search. Each query should read like something a person would type into a search engine: short, keyword-focused, no full sentences or question marks needed.

Do not try to answer the claim yourself. Only produce search queries."""
    queries = []

    
    gemini_response = await gemini_client.aio.models.generate_content(
        model="gemini-2.5-flash", #change when not using free
        contents=[query_prompt, input_claim],
        config={
        "response_mime_type": "application/json",
        "response_schema": SearchQueries,
        }
    )
    queries.extend(gemini_response.parsed.search_queries)
    #for testing:
    print(queries)
    
    #next, search for each query and return the evidence
    async def search_query(query: str) -> List[Evidence]: #instead of doing for i in range num queries per claim in case the gemini model returns fewer than the requested number of queries, we just do it for however many it returns
        query_evidence_list = []
        tavily_response = await tavily_client.search(query)
        for result in tavily_response["results"]:
            query_evidence_list.append(Evidence(
                query=query,
                content=result["content"],
                title=result["title"],
                url=result["url"],
                score=result["score"]
            ))
        return query_evidence_list

    #run the searches in parallel
    tasks = [search_query(query) for query in queries]
    evidence_list =await asyncio.gather(*tasks)
    #flatten the list of lists into a single list
    evidence_list = [e for sublist in evidence_list for e in sublist]
    return evidence_list



if __name__ == "__main__":
    test_claim = Claim(
        claim_text="The Great Wall of China is the only man-made structure visible from space with the naked eye",
        source_span="the Great Wall is the only man-made thing you can see from space"
    )
    evidence = asyncio.run(research_claim(test_claim, num_queries_per_claim=3))
    for e in evidence:
        print(e)
        print("---")
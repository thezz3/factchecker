from google import genai
from pydantic import BaseModel, Field 
from typing import List, Optional
from dotenv import load_dotenv
import os
import json

from agent.functions.extract_claims import Claim, Claims, extract_claims
from agent.functions.research_claim import Evidence, research_claim
from agent.functions.evaluate_claim import Verdict, evaluate_claim
from agent.functions.assemble_results import Result, assemble_result

load_dotenv()


def orchestrate_fact_checking(input_text: str, num_queries_per_claim: int) -> List[Result]:
    results_list = []
    #1. extract claims
    claims_response = extract_claims(input_text)
    #loop for each claim
    for claim in claims_response.claims:
        #2 research the claim
        evidence_list = research_claim(claim, num_queries_per_claim)

        #dedupe the evidence list based on content (remove duplicates)
        # we dedupe by url for consistency, but we could also dedupe by content if we wanted to be more aggressive
        #lowk just do the simplest method possible
        seen = set()
        deduped = []
        for evidence in evidence_list:
            if evidence.url not in seen:
                deduped.append(evidence)
                seen.add(evidence.url)
        print("number removed by dedupe:", len(evidence_list) - len(deduped))
        #3 evaluate the claim
        verdict = evaluate_claim(claim, deduped)
        #4 assemble the result
        result = assemble_result(claim, verdict, deduped)
        results_list.append(result)
    return results_list

    # need dedup after research_claim and before evaluate_claim in orchestrator


if __name__ == "__main__":
    with open("claims_test.txt", "r", encoding="utf-8") as file:
        input_text = file.read()

    results = orchestrate_fact_checking(input_text, num_queries_per_claim=3)

    with open("results.json", "w", encoding="utf-8") as f:
        json.dump([result.model_dump() for result in results], f, indent=2)

    print(f"Done. Wrote {len(results)} results to results.json")
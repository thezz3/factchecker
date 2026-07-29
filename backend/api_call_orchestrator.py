from fastapi import FastAPI
from agent.functions.assemble_results import Result
from agent.orchestrator import orchestrate_fact_checking
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware


class FactCheckRequest(BaseModel):
    input_text: str
    num_queries_per_claim: int = 3  # Default value if not provided

class FactCheckResponse(BaseModel):
    results: list[Result]

app = FastAPI()
#add CORS middleware to allow requests from the extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=False,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

@app.post("/factcheck")




async def read_fact_check(request: FactCheckRequest):
    results = await orchestrate_fact_checking(request.input_text, request.num_queries_per_claim)
    return FactCheckResponse(results=results)
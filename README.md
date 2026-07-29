Architecture:


Agent:

Functions:
extract_claims: from the raw text (which would be from a website), extracts a list of the claims made in the text. input: raw text, output: list of claims (claims type would likely also be text)

filter_worth_checking: OPTIONAL FOR V1, using a small fine-tuned model, evaluate the list of claims and remove the ones that aren't worth checking, input: list of text, output: list of text


research_claim: this function needs to somehow search the internet (search API) and return evidence regarding the claim, input: one claim (one entry in the list of text from b4), output: list of tuples (tuples contain not only the evidence texts but also authors, etc.)

    - for final: this needs to first send each claim to another api call to actualy turn the claims into thign sthat can be searched up 
 ->from the claims, turn each claim into a list of 3 queries that are more useful to search online with Tavily

IN BETWEEN: NEED AN EVIDENCE DEDUPLICATOR BECAUSE THE QUEIRES WILL USE A LOT OF HTE SAME VIDENCE FOR OBVIOUS REASONS
evaluate_claim: calls LLM api and uses the internet evidence to evaluate original claim, input: claim text + evidence text, output: verdict flag (requires a very strong prompt). for the ones that were flagged as misinformation then ask LLM for a justification summary of sorts, and POTENTIALLY sources (depending on if we can get those in the return from research_claim)

assemble_results: relatively simple, collect all the verdicts from all the claims, and return the claims with data on which was are flagged, also NEW: needs to also do the number-> URL mapping

ORHCESTRATOR:
this is the main function, the file in which the agentic loop will be in
the input will be in some json format, in which will be the raw text
it takes the raw text, and calls extrac claims on it, then basically just goes in the sequence in order as decsribed above

note about formatting  (like json and stuff):
- i think when i write the functions first, which I will, I will not worry about formatting and stuff like the function .py needs to accept a json, I'll jsut ahve it accept text, but then later on when I'm more clear on exactly what format comes out of each thing, then I'll make a file that is specifically for managing the functions and converting things for them



RESOURCES USED:

Gemini API:

https://ai.google.dev/gemini-api/docs/quickstart  
https://ai.google.dev/gemini-api/docs/structured-output
https://ai.google.dev/gemini-api/docs/function-calling

LATER FOR EXTRACT CLAIMS:
 - use "fuzzy matching"

 SEARCH APII:
 https://docs.tavily.com/documentation/quickstart


Parallelism:
https://ai.google.dev/gemini-api/docs/migrate    - aio for asyncio
https://docs.tavily.com/sdk/python/reference    - AsyncTavilyClient

https://mmantratech.com/threading-vs-asyncio-in-python-easy-examples-when-to-use-each - for learning and decision
developer.chrome.com/docs/extensions/develop/concepts/content-scripts   -for loading readability in manifest v3

fastapi.tiangolo.com/tutorial/first-steps/

developer.mozilla.org/en-US/docs/Web/HTTP/Overview
developer.chrome.com/docs/extensions/get-started
github.com/mozilla/readability

ERRORS:
- decieded to handle in the orchestrator, not in each individual function



07/07:
finished basic first agent
things to do next:
0. error handling in orchestrator  - DONE
1. parallelism - these claims don't have to be processed sequentially  - DONE
    reasoning: eveyrting else builds on the agent and this makes it much faster/usable
    - decide on threads or async https://mmantratech.com/threading-vs-asyncio-in-python-easy-examples-when-to-use-each

    speedup on our Mt. Everest test:
    no parallelism: 181s
    parllelism basic: 32.27s
    parallelism advanced (research claim internal asyncio): 27.04s

2. global evidence -SKIP for now
3. extension + DOM reading 
    IMMEDIATE/Short-term:
   conceptual: extension/frontend is JS in browser, agent is Python elsewhere; they ONLY talk over HTTP
   - a. FastAPI backend: wrap orchestrator in an HTTP endpoint (text in -> results JSON out) - DONE
   - b. simple test client: paste text -> hit endpoint -> see results (proves the round-trip works) - DONE

4. extension + DOM reading (LATER)
   - c. browser extension (manifest v3): content script reads page DOM, sends text to backend
   - d. clean article extraction (strip nav/ads/footer) via Readability

5. verdict rendering (MUCH LATER - known hard, like Grammarly's hardest part)
   - e. draw verdicts inline on the page without breaking layout

6. cloud/deploy


notes to do later:
- add error field to resutls object



how to call fastapi:
uv run fastapi dev

this works because we set entrypoint in pyproject.toml ("#fastapi 
[tool.fastapi]
entrypoint = "backend.api_call_orchestrator:app"
)


07/18

- got first Readability extension working (console logging)

immediate next:
- connect this to backend (add button so we don't accidentally start sending on every single page we're on)

future:
- we've seen that for sites like reddit that aren't articles that Readability expects, its makes it very hard, so we likely need to do it ourselves for reddit and twitter as the main two forum websites
- obviously frontend parts underlining parts


for 7/25 weekend: 
- check the full pipeline works
- begin work on highlighting


07/28 
- initially tried extension: this error happens:
"Access to fetch at 'http://127.0.0.1:8000/factcheck' from origin 'https://www.naturalnews.com' has been blocked by CORS policy: Response to preflight request doesn't pass access control check: No 'Access-Control-Allow-Origin' header is present."
this is in console log
The browser has a blanket rule — "web-page JavaScript may not read responses from a different origin unless that other server explicitly permits it."
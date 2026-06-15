Architecture:


Agent:

Functions:
extract_claims: from the raw text (which would be from a website), extracts a list of the claims made in the text. input: raw text, output: list of claims (claims type would likely also be text)

filter_worth_checking: OPTIONAL FOR V1, using a small fine-tuned model, evaluate the list of claims and remove the ones that aren't worth checking, input: list of text, output: list of text

research_claim: this function needs to somehow search the internet (search API) and return evidence regarding the claim, input: one claim (one entry in the list of text from b4), output: list of tuples (tuples contain not only the evidence texts but also authors, etc.)

evaluate_claim: calls LLM api and uses the internet evidence to evaluate original claim, input: claim text + evidence text, output: verdict flag (requires a very strong prompt). for the ones that were flagged as misinformation then ask LLM for a justification summary of sorts, and POTENTIALLY sources (depending on if we can get those in the return from research_claim)

assemble_results: relatively simple, collect all the verdicts from all the claims, and return the claims with data on which was are flagged

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
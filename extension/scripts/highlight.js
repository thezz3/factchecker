async function highlightClaims(results) {
    // remember: results is an array of objects, each with a claim and a source_span

    console.log("Total results:", results.length);
    console.log("Refuted claims:", results.filter(r => r.label === "refuted").length);

    if (!results || results.length === 0) {
        console.log("No claims to highlight.");
        return;
    }

    // first, create the css style element for the underlining to be injected into the page
    const style = document.createElement("style");
    style.textContent = "::highlight(fact-check) { text-decoration: underline wavy red; }";
    document.head.appendChild(style);

    // find all text nodes in the article
    const treeWalker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    const allTextNodes = [];
    let currentNode = treeWalker.nextNode();
    while (currentNode) {
        allTextNodes.push(currentNode);
        currentNode = treeWalker.nextNode();
    } // simple loop
    const allRanges = []; // array to hold all ranges for this claim

    for (let i = 0; i < results.length; i++) {
        const result = results[i];
        // only highlight if the claim is not verified
        if (result.label !== "refuted") continue; // skip this claim if it's not refuted

        const source_span = result.claim.source_span.toLowerCase(); // to lower case to match the below text nodes
        
        // find all matches of the source_span in the text nodes and create ranges for them
        const ranges = allTextNodes
            .map((el) => ({ el, text: el.textContent.toLowerCase() }))
            .map(({ text, el }) => {
                const indices = [];
                let startPos = 0;
                while (startPos < text.length) {
                    const index = text.indexOf(source_span, startPos);
                    // if there's no match it returns -1, so we break the loop
                    if (index === -1) break;
                    // otherwise, we push the index to the indices array and continue searching
                    indices.push(index);
                    startPos = index + source_span.length;
                }

                // now create a range for each match found
                return indices.map((index) => {
                    const range = new Range(); //create the range object
                    range.setStart(el, index);
                    range.setEnd(el, index + source_span.length);
                    return range;
                });

                // we use ranges to find where to do underlines
            });
            //unpack the array of arrays of ranges and push to allRanges
            allRanges.push(...ranges.flat()); //flatten the array of arrays and push to allRanges
    };
    console.log("Total ranges to highlight:", allRanges.length);
    //create the highlight object for the ranges found
    const factCheckHighlight = new Highlight(...allRanges); 
    CSS.highlights.set("fact-check", factCheckHighlight);
};
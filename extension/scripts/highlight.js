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
    // for text that crosses multiple nodes, build an offset map and a big flat text
    let flatText = "";
    let nodeOffsets = [];
    let counter = 0;
    for (let textnode of allTextNodes) {
        nodeOffsets.push({node: textnode, offset: counter})
        flatText += textnode.textContent;
        counter += textnode.textContent.length;
    }
    flatText = flatText.toLowerCase();
    const dmp = new diff_match_patch();
    dmp.Match_Threshold = 0.5;   // start at default, tune later
    dmp.Match_Distance = 100000; // effectively ignore location
    function globalToNode(index) {
        for (let i = nodeOffsets.length - 1; i >= 0; i--) {
            //takes in an index in the full text and returns which node it's in and the offset within that node
            let nod = nodeOffsets[i].node;
            if (index >= nodeOffsets[i].offset) {
                return {node: nod, offset: (index - nodeOffsets[i].offset)};
            }
        }
        return null;
    }
    
    const allRanges = []; // array to hold all ranges for this claim

    for (let i = 0; i < results.length; i++) {
        const result = results[i];
        // only highlight if the claim is not verified
        if (result.label !== "refuted") continue; // skip this claim if it's not refuted

        const source_span = result.claim.source_span.toLowerCase(); // to lower case to match the below text nodes

        let startPos = 0;
        
        // find all matches of the source_span in the text nodes and create ranges for them
        while (startPos < flatText.length) {
            // replaced indexOf with fuzzy matching using diff_match_patch
            const pattern = source_span.slice(0, 30);
            const index = dmp.match_main(flatText, pattern, startPos);
            // if there's no match it returns -1, so we break the loop
            if (index === -1) break;
            //also, prevent infinite loop from fuzzy matchin
            if (index < startPos) {
                console.warn("Fuzzy match returned index less than startPos, breaking loop to avoid infinite loop.");
                break;
            }
            // otherwise, we push the range
            let startnodepair = globalToNode(index);
            let endnodepair = globalToNode(index + source_span.length);
            if (!startnodepair || !endnodepair) break;
            
            const range = new Range();
            range.setStart(startnodepair.node, startnodepair.offset);
            range.setEnd(endnodepair.node, endnodepair.offset);
            // setStart/setEnd take (node, offset) since DOM positions are a node plus a local offset, not a global index
            allRanges.push(range);
            
            startPos = index + source_span.length;
        }
    };
    console.log("Total ranges to highlight:", allRanges.length);
    console.log("flat text length", flatText.length);
    console.log("counter:", counter);
    //create the highlight object for the ranges found
    const factCheckHighlight = new Highlight(...allRanges); 
    CSS.highlights.set("fact-check", factCheckHighlight);
};

const article = document.querySelector('article');

// Find all text nodes in the article

const treeWalker = document.createTreeWalker(article, NodeFilter.SHOW_TEXT)
const allTextNodes = [];

let currentNode = treeWalker.nextNode();
while (currentNode) {
  allTextNodes.push(currentNode);
  currentNode = treeWalker.nextNode();
}
// The string we want to find and highlight.
// (Later this will be a claim's source_span from the backend.)
const str = "confirmed summit was in".toLowerCase();

// We'll build up a list of Range objects (one per match found).
const ranges = allTextNodes
  // For each text node, pair it with a lowercased copy of its text.
  // el = the actual text node; text = its lowercased string (for matching).
  .map((el) => ({ el, text: el.textContent.toLowerCase() }))

  // Now search each text node's text for our target string.
  .map(({ text, el }) => {
    const indices = [];      // character positions where str is found
    let startPos = 0;        // where to start searching from

    // Keep finding every occurrence of str in this text node.
    while (startPos < text.length) {
      // indexOf returns the character position of the next match,
      // or -1 if there are no more matches.
      const index = text.indexOf(str, startPos);
      if (index === -1) break;        // no more matches, stop
      indices.push(index);            // record where this match starts
      startPos = index + str.length;  // continue searching AFTER this match
    }

    // For each match position, build a Range covering that text.
    return indices.map((index) => {
      const range = new Range();
      range.setStart(el, index);              // start at the match position
      range.setEnd(el, index + str.length);   // end after the matched text
      return range;
    });
  });

// ranges is currently a list-of-lists (one list per text node).
// .flat() merges them into one flat list of all ranges.
// new Highlight(...) bundles them into a single highlight object.
const factCheckHighlight = new Highlight(...ranges.flat());

// Register the highlight under the name "fact-check".
// This connects to the CSS rule ::highlight(fact-check) in the HTML.
CSS.highlights.set("fact-check", factCheckHighlight);
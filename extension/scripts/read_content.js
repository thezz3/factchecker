// v1: parse contents of page with readability library and console log (testing it out)

// first clone because parse() modifies the DOM
//import Readability from "./readability.js";
// ^ no need for an important statement because Readability is already included in the manifest.json file
const documentClone = document.cloneNode(true);

const article = new Readability(documentClone).parse();
console.log(article);


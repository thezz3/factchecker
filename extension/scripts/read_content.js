// v1: parse contents of page with readability library and console log (testing it out)

// first clone because parse() modifies the DOM
//import Readability from "./readability.js";
// ^ no need for an important statement because Readability is already included in the manifest.json file

//console.log(article);

// send the article content to the background script

// v1: parse contents of page with readability library and send to backend

async function sendArticleContent() {
    // clone first because parse() modifies the DOM
    const documentClone = document.cloneNode(true);
    const article = new Readability(documentClone).parse();

    const url = "http://127.0.0.1:8000/factcheck";
    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ input_text: article.textContent }),
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const results = await response.json();
        console.log("Fact-check results:", results);
        // highlight the claims in the article
        highlightClaims(results.results); // fixes the issue of passing the entire response object instead of just the results array
    } catch (error) {
        console.error("Error sending article content:", error);
    }
}

sendArticleContent();
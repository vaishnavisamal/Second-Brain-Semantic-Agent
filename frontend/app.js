const API_URL = "http://localhost:8000";

document.addEventListener("DOMContentLoaded", () => {
    const analyzeBtn = document.getElementById("analyze-btn");
    const markdownInput = document.getElementById("markdown-input");
    
    // UI Elements
    const placeholderState = document.querySelector(".placeholder-state");
    const loadingState = document.getElementById("loading-state");
    const resultsContainer = document.getElementById("results-container");
    
    // Output Elements
    const outCategory = document.getElementById("out-category");
    const outTags = document.getElementById("out-tags");
    const outLinks = document.getElementById("out-links");
    const outSummary = document.getElementById("out-summary");
    const outJson = document.getElementById("out-json");
    
    // Metrics
    const ttftEl = document.getElementById("metric-ttft");
    const tpsEl = document.getElementById("metric-tps");

    let isAnalyzing = false;

    // Fetch metrics periodically
    setInterval(async () => {
        try {
            const res = await fetch(`${API_URL}/metrics`);
            const data = await res.json();
            
            ttftEl.textContent = `${data.last_ttft_ms} ms`;
            tpsEl.textContent = `${data.last_tps}`;
        } catch (e) {
            // Backend might be down, ignore quietly
        }
    }, 2000);

    analyzeBtn.addEventListener("click", async () => {
        const content = markdownInput.value.trim();
        if (!content || isAnalyzing) return;
        
        isAnalyzing = true;
        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = '<div class="spinner" style="width:16px;height:16px;border-width:2px;"></div> Analyzing...';
        
        // UI transitions
        placeholderState.classList.add("hidden");
        resultsContainer.classList.add("hidden");
        loadingState.classList.remove("hidden");
        
        // Reset outputs
        outJson.textContent = "";
        outTags.innerHTML = "";
        outLinks.innerHTML = "";
        
        let accumulatedJsonStr = "";
        
        try {
            const response = await fetch(`${API_URL}/analyze`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ content })
            });
            
            if (!response.ok) throw new Error("Network response was not ok");
            
            loadingState.classList.add("hidden");
            resultsContainer.classList.remove("hidden");
            
            const reader = response.body.getReader();
            const decoder = new TextDecoder("utf-8");
            
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                
                const chunk = decoder.decode(value);
                const lines = chunk.split("\n\n");
                
                for (const line of lines) {
                    if (line.startsWith("data: ")) {
                        const dataStr = line.substring(6);
                        if (dataStr === "[DONE]") {
                            finalizeUI(accumulatedJsonStr);
                            break;
                        }
                        
                        try {
                            const dataObj = JSON.parse(dataStr);
                            if (dataObj.text) {
                                accumulatedJsonStr += dataObj.text;
                                outJson.textContent = accumulatedJsonStr;
                                
                                // Attempt partial parse to populate UI early if possible
                                attemptPartialParse(accumulatedJsonStr);
                            }
                        } catch (e) {
                            console.error("Error parsing JSON chunk", e);
                        }
                    }
                }
            }
        } catch (error) {
            console.error("Error calling semantic agent:", error);
            outJson.textContent = `Error: ${error.message}`;
            loadingState.classList.add("hidden");
            resultsContainer.classList.remove("hidden");
        } finally {
            isAnalyzing = false;
            analyzeBtn.disabled = false;
            analyzeBtn.innerHTML = 'Ask Agent ✨';
        }
    });

    function attemptPartialParse(jsonStr) {
        // Since it's streaming, it might not be valid JSON yet.
        // We can use regex to extract some fields early for a cool effect.
        
        // Try exact match first
        try {
            const fullObj = JSON.parse(jsonStr);
            populateUI(fullObj);
        } catch (e) {
            // Regex fallback for partial fields
            const catMatch = jsonStr.match(/"folder_category":\s*"([^"]+)"/);
            if (catMatch) outCategory.textContent = catMatch[1];
            
            const sumMatch = jsonStr.match(/"brief_summary":\s*"([^"]+)"/);
            if (sumMatch) outSummary.textContent = sumMatch[1];
            
            // For tags, just look for anything starting with # in quotes
            const tagMatches = [...jsonStr.matchAll(/"(#[a-zA-Z0-9_-]+)"/g)];
            if (tagMatches.length > 0) {
                outTags.innerHTML = tagMatches.map(m => `<span class="tag">${m[1]}</span>`).join('');
            }
        }
    }

    function finalizeUI(jsonStr) {
        try {
            const result = JSON.parse(jsonStr);
            populateUI(result);
            
            // Add a little highlight animation to json block
            outJson.style.color = '#fff';
            setTimeout(() => { outJson.style.color = '#ce9178'; }, 300);
        } catch (e) {
            console.error("Failed to parse final JSON", e);
        }
    }
    
    function populateUI(obj) {
        if (obj.folder_category) outCategory.textContent = obj.folder_category;
        
        if (obj.brief_summary) outSummary.textContent = obj.brief_summary;
        
        if (obj.semantic_tags && Array.isArray(obj.semantic_tags)) {
            outTags.innerHTML = obj.semantic_tags.map(t => `<span class="tag">${t}</span>`).join('');
        }
        
        if (obj.suggested_backlinks && Array.isArray(obj.suggested_backlinks)) {
            outLinks.innerHTML = obj.suggested_backlinks.map(l => `<span class="backlink">${l}</span>`).join('');
        }
    }
});

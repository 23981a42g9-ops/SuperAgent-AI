const API = "http://127.0.0.1:8000/ai";
let currentUrls = [];
let currentIndex = 0;

// 1. MAIN SEND LOGIC
async function sendMessage() {
    const input = document.getElementById("msg");
    const text = input.value.trim();
    if (!text) return;

    appendMessage(text, "user");
    input.value = "";
    const botMsg = appendMessage("⚡ Scanning Global Networks...", "bot");

    try {
        const res = await fetch(API, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text })
        });
        
        if (!res.ok) throw new Error("Backend Unreachable");
        
        const data = await res.json();
        
        currentUrls = data.urls || [];
        currentIndex = 0;
        
        // Update Bot UI
        botMsg.innerHTML = `<div class="bubble">${data.reply}</div>`;
        
        // EXECUTE CONDITIONS
        speak(data.reply);
        if (data.is_sale) showSaleNotification();
        if (currentUrls.length > 0) navigateToNext();

    } catch (e) { 
        botMsg.innerText = "Connection Error: Ensure Uvicorn is running on Port 8000.";
        console.error(e);
    }
}

// 2. MULTI-TAB SATISFACTION LOOP
function navigateToNext() {
    if (currentIndex < currentUrls.length) {
        window.open(currentUrls[currentIndex], "_blank");
        currentIndex++;
        // Show the satisfaction bar if there are more links available
        const sBar = document.getElementById("satisfactionBar");
        if(sBar) sBar.style.display = "block";
    } else {
        const sBar = document.getElementById("satisfactionBar");
        if(sBar) sBar.style.display = "none";
        appendMessage("Maximum global platforms reached for this search.", "bot");
    }
}

// 3. UI HELPERS
function appendMessage(text, who) {
    const chat = document.getElementById("chat");
    const div = document.createElement("div");
    div.className = `msg ${who}`;
    div.innerHTML = `<div class="bubble">${text}</div>`;
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
    return div;
}

// 4. VOICE SYNTHESIS (Supersonic Voice)
function speak(t) {
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(t);
    u.lang = "en-IN"; // Indian English Accent
    u.rate = 1.1;     // Slightly faster "Supersonic" speed
    window.speechSynthesis.speak(u);
}

// 5. SALE NOTIFICATION
function showSaleNotification() {
    const n = document.getElementById("saleNote");
    if(n) {
        n.style.display = "block";
        setTimeout(() => n.style.display = "none", 6000);
    }
}

// 6. VOICE RECOGNITION (MIC)
function startVoice() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        alert("Voice recognition not supported in this browser.");
        return;
    }
    const recognition = new SpeechRecognition();
    recognition.onresult = (e) => {
        const transcript = e.results[0][0].transcript;
        document.getElementById("msg").value = transcript;
        sendMessage();
    };
    recognition.start();
}

// 7. REAL-TIME BACKEND STATUS CHECKER
setInterval(async () => {
    try {
        const response = await fetch("http://127.0.0.1:8000/");
        // Update any element showing status (e.g., a span or header)
        const statusDisplay = document.body.innerText.includes("Backend:") ? true : false;
        if (response.ok) {
            console.log("SuperAgent Backend: Connected");
            // If you have a specific 'offline' text in HTML, you can target it here
        }
    } catch (e) {
        console.warn("SuperAgent Backend: Disconnected");
    }
}, 5000);

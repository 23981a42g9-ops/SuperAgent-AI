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
    const botMsg = appendMessage("⚡ AI is thinking... (Initializing GPU)", "bot");

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
        
        botMsg.innerHTML = `<div class="bubble">${data.reply}</div>`;
        
        speak(data.reply);
        if (data.is_sale) showSaleNotification();
        if (currentUrls.length > 0) navigateToNext();

    } catch (e) { 
        botMsg.innerText = "Connection Error: Ensure Uvicorn and Ollama are running.";
        console.error(e);
    }
}

// 2. MULTI-TAB SATISFACTION LOOP
function navigateToNext() {
    if (currentIndex < currentUrls.length) {
        window.open(currentUrls[currentIndex], "_blank");
        currentIndex++;
        const sBar = document.getElementById("satisfactionBar");
        if(sBar) sBar.style.display = "block";
    } else {
        const sBar = document.getElementById("satisfactionBar");
        if(sBar) sBar.style.display = "none";
        appendMessage("Maximum results reached.", "bot");
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

// 4. VOICE SYNTHESIS
function speak(t) {
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(t);
    u.lang = "en-IN";
    u.rate = 1.1;
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

// 6. VOICE MIC
function startVoice() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.onresult = (e) => {
        document.getElementById("msg").value = e.results[0][0].transcript;
        sendMessage();
    };
    recognition.start();
}

// 7. STATUS CHECKER
setInterval(async () => {
    try {
        const response = await fetch("http://127.0.0.1:8000/");
        const statusSpan = document.getElementById("status");
        if (response.ok && statusSpan) {
            statusSpan.innerText = "online";
            statusSpan.style.color = "#00ff00";
        }
    } catch (e) {
        const statusSpan = document.getElementById("status");
        if(statusSpan) {
            statusSpan.innerText = "offline";
            statusSpan.style.color = "#ff4444";
        }
    }
}, 3000);

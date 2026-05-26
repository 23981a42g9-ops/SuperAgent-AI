const API = "http://127.0.0.1:8000/ai";
let currentUrls = [];
let currentIndex = 0;

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
        const data = await res.json();
        
        currentUrls = data.urls;
        currentIndex = 0;
        botMsg.innerHTML = `<div class="bubble">${data.reply}</div>`;
        
        speak(data.reply);
        if (data.is_sale) showSaleNotification();
        if (currentUrls.length > 0) navigateToNext();

    } catch (e) { 
        botMsg.innerText = "Error: Check if Uvicorn terminal shows activity."; 
    }
}

function navigateToNext() {
    if (currentIndex < currentUrls.length) {
        window.open(currentUrls[currentIndex], "_blank");
        currentIndex++;
        document.getElementById("satisfactionBar").style.display = "block";
    } else {
        document.getElementById("satisfactionBar").style.display = "none";
    }
}

function appendMessage(text, who) {
    const chat = document.getElementById("chat");
    const div = document.createElement("div");
    div.className = `msg ${who}`;
    div.innerHTML = `<div class="bubble">${text}</div>`;
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
    return div;
}

function speak(t) {
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(t);
    u.lang = "en-IN";
    window.speechSynthesis.speak(u);
}

function showSaleNotification() {
    const n = document.getElementById("saleNote");
    n.style.display = "block";
    setTimeout(() => n.style.display = "none", 6000);
}

function startVoice() {
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.onresult = (e) => {
        document.getElementById("msg").value = e.results[0][0].transcript;
        sendMessage();
    };
    recognition.start();
}

let isListening = false;
let recognition = null;
let currentSessionId = "sess_" + Math.random().toString(36).substring(2, 9);
let callerPhone = "9876543210";
let selectedLanguage = "ml"; // 'ml' or 'en'

document.addEventListener("DOMContentLoaded", () => {
    initSpeechRecognition();
});

function setLanguage(lang) {
    selectedLanguage = lang;
    document.querySelectorAll(".lang-btn").forEach(btn => btn.classList.remove("active"));
    const activeBtn = document.getElementById(`langBtn_${lang}`);
    if (activeBtn) activeBtn.classList.add("active");
    if (recognition) {
        recognition.lang = lang === "en" ? "en-IN" : "ml-IN";
    }
}

function initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = selectedLanguage === "en" ? "en-IN" : "ml-IN";

        recognition.onstart = () => {
            isListening = true;
            updateMicButtonUI(true);
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            console.log("STT Result:", transcript);
            sendSpeechToBackend(transcript);
        };

        recognition.onerror = (event) => {
            console.warn("Speech Recognition error:", event.error);
            updateMicButtonUI(false);
        };

        recognition.onend = () => {
            isListening = false;
            updateMicButtonUI(false);
        };
    } else {
        console.warn("Web Speech API not supported in this browser. Fallback to manual text entry.");
    }
}

function toggleMicrophone() {
    if (!recognition) {
        alert("Web Speech API is unavailable in this browser. Please type your query below.");
        return;
    }
    if (isListening) {
        recognition.stop();
    } else {
        try {
            recognition.lang = selectedLanguage === "en" ? "en-IN" : "ml-IN";
            recognition.start();
        } catch (e) {
            console.error("Mic start failed:", e);
        }
    }
}

function updateMicButtonUI(active) {
    const btn = document.getElementById("micBtn");
    const label = document.getElementById("micBtnLabel");
    if (btn && label) {
        if (active) {
            btn.classList.add("listening");
            label.innerText = selectedLanguage === "en" ? "Listening..." : "ശ്രദ്ധിക്കുന്നു...";
        } else {
            btn.classList.remove("listening");
            label.innerText = selectedLanguage === "en" ? "Speak (Click to Speak)" : "സംസാരിക്കുക (Click to Speak)";
        }
    }
}

async function sendManualText() {
    const input = document.getElementById("userTextInput");
    if (!input || !input.value.trim()) return;
    const text = input.value.trim();
    input.value = "";
    await sendSpeechToBackend(text);
}

async function sendSpeechToBackend(userText) {
    appendMessage("USER", userText);
    
    try {
        const phoneInput = document.getElementById("phoneInput");
        if (phoneInput && phoneInput.value.trim()) {
            callerPhone = phoneInput.value.trim();
        }

        const res = await fetch("/api/voice/process", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                session_id: currentSessionId,
                caller_phone: callerPhone,
                user_speech_text: userText,
                language: selectedLanguage
            })
        });

        const data = await res.json();
        console.log("Backend response:", data);

        const responseText = data.bot_response || data.bot_response_ml;
        appendMessage("SYSTEM", responseText);
        updateTelemetry(data);
        speakResponse(responseText, data.language || selectedLanguage);

    } catch (err) {
        console.error("Failed to connect to Voice Assistant API:", err);
        appendMessage("SYSTEM", "Sorry, could not connect due to a network error.");
    }
}

function appendMessage(sender, text) {
    const container = document.getElementById("liveTranscript");
    if (!container) return;

    const bubble = document.createElement("div");
    bubble.className = `msg-bubble ${sender === "USER" ? "msg-user" : "msg-bot"}`;
    bubble.innerHTML = `<strong>${sender === "USER" ? "Patient" : "KMC Voice Assistant"}:</strong> ${text}`;
    container.appendChild(bubble);
    container.scrollTop = container.scrollHeight;
}

function updateTelemetry(data) {
    const intentBadge = document.getElementById("intentBadge");
    const emergencyAlert = document.getElementById("emergencyAlert");
    
    if (intentBadge) {
        intentBadge.innerText = `Intent: ${data.intent}`;
    }

    if (emergencyAlert) {
        if (data.is_emergency) {
            emergencyAlert.style.display = "block";
            emergencyAlert.innerText = `🚨 EMERGENCY DETECTED! Transferred to Trauma Care Desk (108)`;
        } else {
            emergencyAlert.style.display = "none";
        }
    }
}

function speakResponse(text, lang) {
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = lang === "en" ? 'en-IN' : 'ml-IN';
        utterance.rate = 0.95;
        
        const voices = window.speechSynthesis.getVoices();
        const matchVoice = voices.find(v => (lang === "en" ? v.lang.includes('en') : (v.lang.includes('ml') || v.name.includes('Malayalam'))));
        if (matchVoice) {
            utterance.voice = matchVoice;
        }
        
        window.speechSynthesis.speak(utterance);
    } else {
        const audio = new Audio(`/api/voice/tts?text=${encodeURIComponent(text)}&lang=${lang}`);
        audio.play().catch(e => console.log("Audio playback deferred:", e));
    }
}

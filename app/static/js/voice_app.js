let isListening = false;
let recognition = null;
let ws = null;
let audioContext = null;
let analyser = null;
let micStream = null;
let currentSessionId = "ws_sess_" + Math.random().toString(36).substring(2, 9);
let callerPhone = "9876543210";
let selectedLanguage = "ml"; // 'ml' or 'en'
let isAssistantSpeaking = false;

document.addEventListener("DOMContentLoaded", () => {
    initSpeechRecognition();
    initWebSocket();
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

function initWebSocket() {
    const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    const wsUrl = `${wsProtocol}//${window.location.host}/ws/voice`;
    
    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        console.log("WebSocket connected to real-time voice engine.");
    };

    ws.onmessage = (event) => {
        const frame = JSON.parse(event.data);
        console.log("WS Frame:", frame);

        if (frame.type === "ASSISTANT_RESPONSE") {
            const responseText = frame.bot_response || frame.bot_response_ml;
            appendMessage("SYSTEM", responseText);
            updateTelemetryData(frame);
            speakResponse(responseText, frame.language || selectedLanguage);
        } else if (frame.type === "BARGE_IN_ACK") {
            console.log("Barge-in acknowledged by server.");
        }
    };

    ws.onclose = () => {
        console.warn("WS Disconnected. Reconnecting in 3s...");
        setTimeout(initWebSocket, 3000);
    };
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
            startAudioVADMeter();

            // INSTANT BARGE-IN: If assistant is currently speaking, abort immediately!
            if (isAssistantSpeaking) {
                triggerBargeInInterruption();
            }
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            console.log("STT Stream Transcript:", transcript);
            sendSpeechInput(transcript);
        };

        recognition.onerror = (event) => {
            console.warn("STT Error:", event.error);
            updateMicButtonUI(false);
            stopAudioVADMeter();
        };

        recognition.onend = () => {
            isListening = false;
            updateMicButtonUI(false);
            stopAudioVADMeter();
        };
    }
}

function triggerBargeInInterruption() {
    console.log("🛑 BARGE-IN DETECTED! Interrupting assistant audio...");
    isAssistantSpeaking = false;
    
    // Stop Web Speech Synthesis
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
    }
    
    // Notify server via WebSocket
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: "BARGE_IN_INTERRUPT" }));
    }

    const bargeBadge = document.getElementById("bargeInBadge");
    if (bargeBadge) {
        bargeBadge.style.display = "inline-block";
        bargeBadge.innerText = "🛑 BARGE-IN: Assistant Aborted";
        setTimeout(() => { bargeBadge.style.display = "none"; }, 3000);
    }
}

function toggleMicrophone() {
    if (!recognition) {
        alert("Speech Recognition API unavailable in this browser. Please type below.");
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
            label.innerText = selectedLanguage === "en" ? "Listening (VAD Active)..." : "ശ്രദ്ധിക്കുന്നു (VAD Active)...";
        } else {
            btn.classList.remove("listening");
            label.innerText = selectedLanguage === "en" ? "Speak (Click to Speak)" : "സംസാരിക്കുക (Click to Speak)";
        }
    }
}

/* Audio VAD Meter & Wave Visualizer */
async function startAudioVADMeter() {
    try {
        if (!navigator.mediaDevices) return;
        micStream = await navigator.mediaDevices.getUserMedia({ audio: true });
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        analyser = audioContext.createAnalyser();
        const source = audioContext.createMediaStreamSource(micStream);
        source.connect(analyser);
        analyser.fftSize = 64;

        const dataArray = new Uint8Array(analyser.frequencyBinCount);
        const vadMeter = document.getElementById("vadVolumeBar");

        function renderVAD() {
            if (!isListening) return;
            analyser.getByteFrequencyData(dataArray);
            let sum = 0;
            for (let i = 0; i < dataArray.length; i++) sum += dataArray[i];
            let average = sum / dataArray.length;
            let percentage = Math.min(100, Math.round((average / 128) * 100));

            if (vadMeter) {
                vadMeter.style.width = `${percentage}%`;
            }

            // VAD Speech Start Detection during assistant speech
            if (percentage > 25 && isAssistantSpeaking) {
                triggerBargeInInterruption();
            }

            requestAnimationFrame(renderVAD);
        }
        renderVAD();
    } catch (e) {
        console.log("VAD Meter initialization skipped:", e);
    }
}

function stopAudioVADMeter() {
    if (micStream) {
        micStream.getTracks().forEach(t => t.stop());
    }
    const vadMeter = document.getElementById("vadVolumeBar");
    if (vadMeter) vadMeter.style.width = "0%";
}

async function sendManualText() {
    const input = document.getElementById("userTextInput");
    if (!input || !input.value.trim()) return;
    const text = input.value.trim();
    input.value = "";
    await sendSpeechInput(text);
}

async function sendSpeechInput(userText) {
    appendMessage("USER", userText);
    
    const phoneInput = document.getElementById("phoneInput");
    if (phoneInput && phoneInput.value.trim()) {
        callerPhone = phoneInput.value.trim();
    }

    const payload = {
        type: "SPEECH_INPUT",
        session_id: currentSessionId,
        caller_phone: callerPhone,
        user_speech_text: userText,
        language: selectedLanguage
    };

    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify(payload));
    } else {
        // Fallback HTTP POST
        try {
            const res = await fetch("/api/voice/process", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            appendMessage("SYSTEM", data.bot_response);
            speakResponse(data.bot_response, selectedLanguage);
        } catch (err) {
            console.error(err);
        }
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

function updateTelemetryData(data) {
    const intentBadge = document.getElementById("intentBadge");
    const emergencyAlert = document.getElementById("emergencyAlert");
    const toolBadge = document.getElementById("toolCallBadge");
    const latencyBox = document.getElementById("latencyBreakdown");
    
    if (intentBadge) intentBadge.innerText = `Intent: ${data.intent}`;

    if (toolBadge) {
        if (data.tool_called) {
            toolBadge.style.display = "inline-block";
            toolBadge.innerText = `⚡ Tool: ${data.tool_called}`;
        } else {
            toolBadge.style.display = "none";
        }
    }

    if (latencyBox && data.latency) {
        const l = data.latency;
        latencyBox.innerHTML = `
            <div style="font-size:0.8rem; color:var(--accent-teal); display:flex; gap:12px; font-family:monospace;">
                <span>STT: ${l.stt_ms}ms</span>
                <span>LLM: ${l.llm_ms}ms</span>
                <span>Tool: ${l.tool_ms}ms</span>
                <span>TTS: ${l.tts_ms}ms</span>
                <strong style="color:var(--accent-emerald);">Total: ${l.total_ms}ms</strong>
            </div>
        `;
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
        isAssistantSpeaking = true;

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = lang === "en" ? 'en-IN' : 'ml-IN';
        utterance.rate = 0.95;
        
        utterance.onend = () => { isAssistantSpeaking = false; };
        utterance.onerror = () => { isAssistantSpeaking = false; };

        const voices = window.speechSynthesis.getVoices();
        const matchVoice = voices.find(v => (lang === "en" ? v.lang.includes('en') : (v.lang.includes('ml') || v.name.includes('Malayalam'))));
        if (matchVoice) utterance.voice = matchVoice;
        
        window.speechSynthesis.speak(utterance);
    } else {
        const audio = new Audio(`/api/voice/tts?text=${encodeURIComponent(text)}&lang=${lang}`);
        audio.onended = () => { isAssistantSpeaking = false; };
        audio.play().catch(e => console.log(e));
    }
}

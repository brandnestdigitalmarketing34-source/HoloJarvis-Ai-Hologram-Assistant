const backendUrl = `http://${window.location.hostname || '127.0.0.1'}:8000`;

document.addEventListener('DOMContentLoaded', () => {
    const startBtn = document.getElementById('start-btn');
    const startupScreen = document.getElementById('startup-screen');
    const videoContainer = document.getElementById('video-container');
    const introVideo = document.getElementById('intro-video');
    const hologramInterface = document.getElementById('hologram-interface');
    const transcriptEl = document.getElementById('transcript');
    const aiStateBox = document.getElementById('ai-state-box');
    const aiStateIndicator = document.getElementById('ai-state-indicator');
    const statusMessage = document.getElementById('status-message');
    const canvas = document.getElementById('waveform');
    const ctx = canvas.getContext('2d');

    // Internal State
    let currentState = 'STANDBY';
    let isSpeaking = false;
    let waveAnimFrame;
    let time = 0;

    // Set canvas dimensions explicitly for drawing
    canvas.width = 400;
    canvas.height = 150;

    // Simulate system metrics
    setInterval(() => {
        document.getElementById('cpu-load').innerText = Math.floor(Math.random() * 20 + 5) + '%';
        document.getElementById('mem-usage').innerText = Math.floor(Math.random() * 10 + 40) + '%';
    }, 2000);

    // Initialization Sequence
    startBtn.addEventListener('click', () => {
        introVideo.muted = false;
        startupScreen.style.display = 'none';
        videoContainer.style.display = 'block';
        
        introVideo.play().catch(e => {
            console.error("Autoplay prevented:", e);
            skipIntro();
        });
    });

    introVideo.addEventListener('ended', skipIntro);
    videoContainer.addEventListener('click', skipIntro);
    document.addEventListener('keydown', (e) => {
        if(e.key === "Escape" && videoContainer.style.display === 'block') skipIntro();
    });

    function skipIntro() {
        introVideo.pause();
        videoContainer.style.display = 'none';
        hologramInterface.style.display = 'flex';
        setAiState('LISTENING');
        initSpeechRecognition();
        speak("System online. Hologram interface activated. Awaiting commands.");
        startHealthCheck();
    }
    
    // Automatic Backend Health-Check
    function startHealthCheck() {
        fetch(`${backendUrl}/`)
            .then(res => {
                if(res.ok) {
                    console.log("Backend health check passed.");
                }
            })
            .catch(err => {
                console.error("Backend not reachable. Retrying in 5 seconds...");
                setAiState('STANDBY');
                statusMessage.innerText = 'WAITING FOR SERVER CONNECTION...';
                setTimeout(startHealthCheck, 5000);
            });
    }

    // State Management
    function setAiState(state) {
        currentState = state;
        
        // Remove old classes
        aiStateBox.classList.remove('state-standby', 'state-listening', 'state-processing', 'state-speaking', 'executing-shake');
        
        if (state === 'STANDBY') {
            aiStateIndicator.innerText = '[STANDBY]';
            aiStateBox.classList.add('state-standby');
            statusMessage.innerText = 'SYSTEM ON STANDBY';
        } else if (state === 'LISTENING') {
            aiStateIndicator.innerText = '[LISTENING...]';
            aiStateBox.classList.add('state-listening');
            statusMessage.innerText = 'LISTENING FOR "JARVIS"...';
        } else if (state === 'PROCESSING') {
            aiStateIndicator.innerText = '[PROCESSING]';
            aiStateBox.classList.add('state-processing');
            statusMessage.innerText = 'ANALYZING INTENT...';
            playChirp('processing');
        } else if (state === 'SPEAKING') {
            aiStateIndicator.innerText = '[SPEAKING]';
            aiStateBox.classList.add('state-speaking');
            statusMessage.innerText = 'TRANSMITTING RESPONSE...';
        }
    }

    // Web Audio API Context (HoloJarvice SFX)
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

    function playChirp(type = 'processing') {
        if (audioCtx.state === 'suspended') audioCtx.resume();
        
        const osc = audioCtx.createOscillator();
        const gainNode = audioCtx.createGain();
        
        osc.connect(gainNode);
        gainNode.connect(audioCtx.destination);
        
        if (type === 'processing') {
            // Quick high-tech chirp
            osc.type = 'sine';
            osc.frequency.setValueAtTime(800, audioCtx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(1200, audioCtx.currentTime + 0.1);
            
            gainNode.gain.setValueAtTime(0, audioCtx.currentTime);
            gainNode.gain.linearRampToValueAtTime(0.1, audioCtx.currentTime + 0.02);
            gainNode.gain.linearRampToValueAtTime(0, audioCtx.currentTime + 0.1);
            
            osc.start(audioCtx.currentTime);
            osc.stop(audioCtx.currentTime + 0.1);
        } else if (type === 'execute') {
            // Low confirmation rumble/blip
            osc.type = 'square';
            osc.frequency.setValueAtTime(150, audioCtx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(50, audioCtx.currentTime + 0.3);
            
            gainNode.gain.setValueAtTime(0, audioCtx.currentTime);
            gainNode.gain.linearRampToValueAtTime(0.1, audioCtx.currentTime + 0.05);
            gainNode.gain.linearRampToValueAtTime(0, audioCtx.currentTime + 0.3);
            
            osc.start();
            osc.stop(audioCtx.currentTime + 0.3);
        }
    }

    // Waveform Animator
    function drawWaveform() {
        if (!isSpeaking) {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            return;
        }

        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        const width = canvas.width;
        const height = canvas.height;
        const centerY = height / 2;
        
        ctx.lineWidth = 2;
        ctx.shadowBlur = 15;
        ctx.shadowColor = '#00f3ff';

        time += 1;

        // Draw 3 overlapping neon waves for the hologram effect
        for(let j = 0; j < 3; j++) {
            ctx.beginPath();
            ctx.strokeStyle = j === 0 ? '#00f3ff' : (j === 1 ? 'rgba(0,243,255,0.7)' : 'rgba(0,243,255,0.3)');
            
            for (let i = 0; i < width; i++) {
                // Amplitude modulation over time + static variance based on layer
                const amplitude = (25 + Math.sin(time * 0.1) * 15) * (1 - j*0.2);
                
                // Taper effect so the wave fades out at the edges of the canvas
                const taper = Math.sin((i / width) * Math.PI);
                const actualAmplitude = amplitude * taper;
                
                // Frequency variation
                const y = centerY + Math.sin(i * 0.03 + time * 0.1 + j) * actualAmplitude;
                
                if (i === 0) ctx.moveTo(i, y);
                else ctx.lineTo(i, y);
            }
            ctx.stroke();
        }

        waveAnimFrame = requestAnimationFrame(drawWaveform);
    }

    function startWaveform() {
        if (!isSpeaking) {
            isSpeaking = true;
            time = 0; // Reset time for smooth start
            waveAnimFrame = requestAnimationFrame(drawWaveform);
        }
    }

    function stopWaveform() {
        isSpeaking = false;
        if (waveAnimFrame) cancelAnimationFrame(waveAnimFrame);
        ctx.clearRect(0, 0, canvas.width, canvas.height);
    }

    // Web Speech API Integration
    let recognition;
    function initSpeechRecognition() {
        window.SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!window.SpeechRecognition) {
            transcriptEl.innerText = "Speech Recognition API not supported in this browser.";
            return;
        }

        recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onresult = function(event) {
            const current = event.resultIndex;
            const transcript = event.results[current][0].transcript.trim().toLowerCase();
            
            // Process everything heard directly (Wake word is optional)
            transcriptEl.innerText = `"${transcript}"`;
            console.log("Heard:", transcript);
            handleCommand(transcript);
        };

        recognition.onerror = function(event) {
            console.error('Speech recognition error', event.error);
        };

        recognition.onend = function() {
            // Auto-restart recognition to keep listening indefinitely
            setTimeout(() => {
                try {
                    recognition.start();
                } catch(e) {}
            }, 1000);
        };

        recognition.start();
    }

    // Speech Synthesis
    function speak(text) {
        if (!window.speechSynthesis) return;
        
        const utterance = new SpeechSynthesisUtterance(text);
        const voices = window.speechSynthesis.getVoices();
        
        // Prefer Female voices for HoloJarvice
        const femaleVoice = voices.find(v => v.name.includes('Female') || v.name.includes('Zira') || v.name.includes('Google US English'));
        if (femaleVoice) {
            utterance.voice = femaleVoice;
        }
        
        utterance.pitch = 1.1; // Slightly higher pitch for female AI
        utterance.rate = 1.0;
        
        utterance.onstart = () => {
            if (!aiStateIndicator.innerText.includes("EXECUTING")) {
                setAiState('SPEAKING');
            }
            startWaveform();
        };

        utterance.onend = () => {
            stopWaveform();
            setAiState('LISTENING');
        };

        utterance.onerror = () => {
            stopWaveform();
            setAiState('LISTENING');
        };
        
        window.speechSynthesis.speak(utterance);
    }

    // Command Handling & Backend Communication
    function handleCommand(command) {
        setAiState('PROCESSING');
        
        fetch(`${backendUrl}/api/command`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ command: command })
        })
        .then(res => res.json())
        .then(data => {
            console.log("Backend response:", data);
            
            // Render execution action tag in HUD if present
            if (data.action_tag && data.action_tag !== "") {
                aiStateIndicator.innerText = `[EXECUTING: ${data.action_tag}]`;
                aiStateBox.classList.remove('state-processing');
                aiStateBox.classList.add('state-speaking', 'executing-shake'); // Makes it glow green and shake while executing
                playChirp('execute');
                
                // Camera logic
                if (data.action_tag === "ACTIVATE_CAMERA") {
                    const camViewport = document.getElementById('camera-viewport');
                    const camStream = document.getElementById('camera-stream');
                    // Add a cache buster timestamp to ensure the browser fetches the new stream
                    camStream.src = `${backendUrl}/video_feed?t=${new Date().getTime()}`;
                    camViewport.style.display = 'block';
                } else if (data.action_tag === "DEACTIVATE_CAMERA") {
                    const camViewport = document.getElementById('camera-viewport');
                    const camStream = document.getElementById('camera-stream');
                    camViewport.style.display = 'none';
                    camStream.src = "";
                }
            }
            
            if(data.reply) {
                speak(data.reply);
            } else {
                setAiState('LISTENING');
            }
        })
        .catch(err => {
            console.error("API Error:", err);
            speak("I'm sorry, I cannot connect to the core server.");
            setAiState('LISTENING');
        });
    }
});

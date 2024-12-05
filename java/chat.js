document.addEventListener("DOMContentLoaded", function() {
    const microphoneButton = document.getElementById("microphone-button");
    const frequencyCanvas = document.getElementById("frequency-canvas");
    const canvasContext = frequencyCanvas.getContext("2d");
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const imageInput = document.getElementById("image-input");
    const imagePreview = document.getElementById("image-preview");
    const videoPreview = document.getElementById("video-preview");
    const canvas = document.getElementById("canvas");
    const captureButton = document.getElementById("capture-button");
    let selectedModel = '{{ domain }}';
    let recognition;
    let analyser;
    let isListening = false;
    let isBotSpeaking = false;

    function startVoiceRecognition() {
        if (!recognition) {
            recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = 'es-ES';
            recognition.continuous = false;
            recognition.interimResults = false;
        }

        recognition.onresult = function(event) {
            if (!isBotSpeaking) {
                const userInput = event.results[0][0].transcript;
                document.getElementById("user-input").value = userInput;
                sendMessage(userInput);
            }
        };

        recognition.onerror = function(event) {
            console.error("Error en el reconocimiento de voz: ", event.error);
        };

        recognition.onend = function() {
            if (isListening && !isBotSpeaking) {
                recognition.start();
            }
        };

        recognition.start();
        startFrequencySpectrum();
    }

    microphoneButton.onclick = function() {
        if (!isListening) {
            isListening = true;
            microphoneButton.innerText = "Stop Conversation";
            startVoiceRecognition();
        } else {
            isListening = false;
            microphoneButton.innerText = "Start Conversation";
            if (recognition) {
                recognition.stop();
            }
            stopFrequencySpectrum();
        }
    };

    function startFrequencySpectrum() {
        navigator.mediaDevices.getUserMedia({ audio: true }).then((stream) => {
            const source = audioContext.createMediaStreamSource(stream);
            analyser = audioContext.createAnalyser();
            source.connect(analyser);
            analyser.fftSize = 256;

            frequencyCanvas.style.display = "block";
            drawFrequencySpectrum();
        }).catch((error) => {
            console.error("Error al acceder al micrófono: ", error);
        });
    }

    function stopFrequencySpectrum() {
        frequencyCanvas.style.display = "none";
    }

    function drawFrequencySpectrum() {
        if (!isListening) return;

        requestAnimationFrame(drawFrequencySpectrum);

        const bufferLength = analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        analyser.getByteFrequencyData(dataArray);

        canvasContext.clearRect(0, 0, frequencyCanvas.width, frequencyCanvas.height);
        const barWidth = (frequencyCanvas.width / bufferLength) * 2.5;
        let barHeight;
        let x = 0;

        for (let i = 0; i < bufferLength; i++) {
            barHeight = dataArray[i] / 2;
            canvasContext.fillStyle = `rgb(${barHeight + 100}, 50, 50)`;
            canvasContext.fillRect(x, frequencyCanvas.height - barHeight, barWidth, barHeight);
            x += barWidth + 1;
        }
    }

    function sendMessage(userInput) {
        if (userInput.trim() !== "") {
            document.getElementById("chat-box").innerHTML += `<div>Usuario: ${userInput}</div>`;
            document.getElementById("user-input").value = ''; // Limpiar el input después de enviar
        }
    }
});

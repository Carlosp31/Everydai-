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
    let isBotSpeaking = false; // Variable para saber si el bot está hablando

    // Función para iniciar el reconocimiento de voz y el espectro de frecuencias
    function startVoiceRecognition() {
        if (!recognition) {
            recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = 'es-ES';
            recognition.continuous = false;
            recognition.interimResults = false;
        }

        recognition.onresult = function(event) {
            if (!isBotSpeaking) { // Solo procesar si el bot no está hablando
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
                recognition.start(); // Reiniciar reconocimiento si sigue en modo escucha
            }
        };

        recognition.start();
        startFrequencySpectrum(); // Iniciar el espectro de frecuencias
    }

    // Evento para iniciar o detener el reconocimiento de voz con el botón de 'Start Conversation'
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

    // Función para iniciar el espectro de frecuencias
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

    // Función para detener el espectro de frecuencias
    function stopFrequencySpectrum() {
        frequencyCanvas.style.display = "none";
    }

    // Función para dibujar el espectro de frecuencias
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

    // Función para enviar mensajes (tanto por texto como por voz)
   function sendMessage(userInput) {
if (userInput.trim() !== "") {
document.getElementById("chat-box").innerHTML += `<div>Usuario: ${userInput}</div>`;
document.getElementById("user-input").value = ''; // Limpiar el input después de enviar

// Detener temporalmente el reconocimiento de voz mientras se obtiene la respuesta del bot
if (recognition) recognition.stop();
isBotSpeaking = true;

fetch('/chat', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message: userInput, model: selectedModel }),
})
.then(response => response.json())
.then(data => {
    document.getElementById("chat-box").innerHTML += `<div>AI: ${data.text_response}</div>`;
    speakResponse(data.text_response);

    // Mostrar las recomendaciones en el cuadro de recomendaciones
    const recommendationsList = document.getElementById("recommendations-list");
    recommendationsList.innerHTML = '';  // Limpiar la lista existente

    // Verificar si data.recipes es un array antes de recorrerlo
    if (Array.isArray(data.recipes)) {
        data.recipes.forEach(receta => {
            const listItem = document.createElement("li");
            listItem.innerHTML = `<a href="${receta.link}" target="_blank">${receta.title}</a>`;
            recommendationsList.appendChild(listItem);
        });
    } else {
        recommendationsList.innerHTML = '<li>No se encontraron recomendaciones.</li>';
    }
})
.catch(error => console.error('Error:', error));
}
}

    // Función para sintetizar y reproducir el audio de la respuesta
    function speakResponse(responseText) {
        fetch('/synthesize-audio', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: responseText, modelo: selectedModel}),
        })
        .then(audioResponse => {
            if (audioResponse.ok) return audioResponse.blob();
            throw new Error('Error al obtener el audio.');
        })
        .then(audioBlob => {
            const audioUrl = URL.createObjectURL(audioBlob);
            const audio = new Audio(audioUrl);
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const analyser = audioContext.createAnalyser();
            const source = audioContext.createMediaElementSource(audio);
            source.connect(analyser);
            analyser.connect(audioContext.destination);

            const dataArray = new Uint8Array(analyser.frequencyBinCount);

            function emitAudioLevels() {
                analyser.getByteFrequencyData(dataArray);
                const avgAmplitude = dataArray.reduce((a, b) => a + b, 0) / dataArray.length;

                const event = new CustomEvent('audio-level', { detail: { amplitude: avgAmplitude / 255 } });
                window.dispatchEvent(event);

                if (!audio.paused && !audio.ended) {
                    requestAnimationFrame(emitAudioLevels);
                }
            }

            audio.onplay = function() {
                isBotSpeaking = true;
                emitAudioLevels();
                if (recognition) recognition.stop(); 
            };

            audio.onended = function() {
                isBotSpeaking = false;
                if (isListening) recognition.start();
                const event = new CustomEvent('audio-level', { detail: { amplitude: 0 } });
                window.dispatchEvent(event);
            };

            audio.play();
        })
        .catch(error => console.error('Error:', error));
    }

    // Evento al hacer clic en el botón de enviar texto manualmente
    document.getElementById("send-button").onclick = function() {
        const userInput = document.getElementById("user-input").value;
        sendMessage(userInput);
    };

    // Funcionalidad para abrir la cámara
    document.getElementById("camera-button").onclick = function() {
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            navigator.mediaDevices.getUserMedia({ video: true }).then(function(stream) {
                videoPreview.srcObject = stream;
                videoPreview.style.display = "block";
                document.getElementById("capture-button").style.display = "block";
            }).catch(function(error) {
                console.error("Error al acceder a la cámara: ", error);
            });
        }
    };

    // Funcionalidad para capturar imagen de la cámara
    captureButton.onclick = function() {
        const context = canvas.getContext('2d');
        canvas.width = videoPreview.videoWidth;
        canvas.height = videoPreview.videoHeight;
        context.drawImage(videoPreview, 0, 0);
        const imageData = canvas.toDataURL('image/png');
        imagePreview.src = imageData;
        imagePreview.style.display = "block";

        // Detener el stream de video
        const stream = videoPreview.srcObject;
        const tracks = stream.getTracks();
        tracks.forEach(track => track.stop());
        videoPreview.srcObject = null;
        videoPreview.style.display = "none";
        captureButton.style.display = "none";

        // Enviar la imagen capturada al servidor
        canvas.toBlob(function(blob) {
            const formData = new FormData();
            formData.append('image', blob, 'captured-image.png');
            formData.append('model', selectedModel);

            fetch('/upload-image', {
                method: 'POST',
                body: formData,
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById("chat-box").innerHTML += `<div>Modelo: ${data.response}</div>`;
                speakResponse(data.response);
            })
            .catch(error => console.error('Error:', error));
        }, 'image/png');
    };

    // Evento al hacer clic en el botón de cargar imagen
    document.getElementById("upload-button").onclick = function() {
        const file = imageInput.files[0];

        if (file) {
            const formData = new FormData();
            formData.append('image', file);
            formData.append('model', selectedModel);

            fetch('/upload-image', {
                method: 'POST',
                body: formData,
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById("chat-box").innerHTML += `<div>Modelo: ${data.response}</div>`;
                speakResponse(data.response);
            })
            .catch(error => console.error('Error:', error));
        }
    };

    // Vista previa de la imagen cargada
    imageInput.onchange = function() {
        const file = imageInput.files[0];
        const reader = new FileReader();
        reader.onload = function(e) {
            imagePreview.src = e.target.result;
            imagePreview.style.display = "block";
        };
        reader.readAsDataURL(file);
    };
});
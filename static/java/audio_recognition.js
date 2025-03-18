const microphoneButton = document.getElementById("microphone-button");
const frequencyCanvas = document.getElementById("frequency-canvas");
const canvasContext = frequencyCanvas.getContext("2d");
const audioContext = new (window.AudioContext || window.webkitAudioContext)();
let recognition;
let analyser;
let selectedModel = domain;
let isListening = false;
let isBotSpeaking = false; // Variable para saber si el bot está hablando
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
            dots.style.opacity = 1; // Mostrar los puntos
            const event5 = new CustomEvent('pensar');
            window.dispatchEvent(event5);
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

        // Verificar si data.recipes es un array antes de recorrerlo
        if (Array.isArray(data.recipes)) {
            data.recipes.forEach(item => {
                const listItem = document.createElement("li");

                // Verificamos si el objeto tiene las llaves 'nombre' y 'precio'
                if (item.nombre && item.precio) {
                    listItem.innerHTML = `<div class="producto">
                            <span class="producto-nombre">${item.nombre}</span> - 
                            <span class="producto-precio">${item.precio}</span>
                            <button onclick="addToCart({nombre: '${item.nombre}', precio: '${item.precio}'})">Add to list</button>
                        </div>`;

                    // Verificamos si también tiene la URL de la imagen
                    if (item.imagen_url) {
                        // Crear un elemento de imagen y asignarle la URL
                        const imgElement = document.createElement("img");
                        imgElement.src = item.imagen_url;
                        imgElement.alt = item.nombre;
                        imgElement.classList.add("producto-imagen");  // Añadir clase CSS

                        // Añadir la miniatura de la imagen al `listItem`
                        listItem.prepend(imgElement);
                    }

                    // Agregar una clase para dar estilo a los productos con nombre y precio
                    listItem.classList.add("producto-con-precio");
                } else if (item.link && item.title) {
                    // Si tiene 'link' y 'title', mostramos la receta
                    listItem.innerHTML = `<div>
                                            <a href="${item.link}" target="_blank">${item.title}</a>
                                            <button onclick="addToCart({link: '${item.link}', title: '${item.title}'})">Add to cart</button>
                                        </div>`;
                } else {
                    // Si no tiene 'nombre' y 'precio' ni 'link' y 'title', mostramos un mensaje por defecto
                    listItem.innerHTML = "Información no válida";
                }

                // Añadir cada item a la lista de recomendaciones
                recommendationsList.appendChild(listItem);
            });
        } else {
            recommendationsList.innerHTML = '<li>No se encontraron recomendaciones.</li>';
        }

        })
        .catch(error => console.error('Error:', error));
    }
}
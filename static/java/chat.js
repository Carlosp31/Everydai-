const urlParams = new URLSearchParams(window.location.search);
const domain = urlParams.get('domain');

           window.onload = function() {
            setTimeout(() => {
                document.getElementById("loading-screen").style.opacity = "0";
            }, 2000);
            setTimeout(() => {
                    document.getElementById("loading-screen").style.display = "none";
                    document.getElementById("content").style.display = "block";
                }, 500);
        };
        function redirectToRealidad() {
            let selectedModel = domain;

            window.location.href = `/augmented experience?domain=${encodeURIComponent(selectedModel)}`;
        }

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
            let selectedModel = domain;
            let recognition;
            let analyser;
            let isListening = false;
            let isBotSpeaking = false; // Variable para saber si el bot está hablando
            document.getElementById("user-input").addEventListener("keypress", function(event) {
                if (event.key === "Enter") {
                    event.preventDefault(); // Evita que se agregue una nueva línea en el input
                    const userInput = document.getElementById("user-input").value.trim(); // Elimina espacios en blanco
                    if (userInput) { 
                        sendMessage(userInput);

                        const dots = document.getElementById("dots");
                        const event3 = new CustomEvent('pensar');
                        window.dispatchEvent(event3);
                        dots.style.opacity = 1; // Mostrar los puntos
                    } else {
                        alert("Please enter a message before sending.");
                    }
                }
            });
            let storedMessage = sessionStorage.getItem("pendingMessage");

            if (storedMessage) {
                sendMessage(storedMessage, "detection"); // Enviamos directamente como string
                        // Cambiar la opacidad de los puntos
        const dots = document.getElementById("dots");
        const event6 = new CustomEvent('pensar');
        window.dispatchEvent(event6);
        dots.style.opacity = 1; // Mostrar los puntos
                sessionStorage.removeItem("pendingMessage"); // Eliminamos el mensaje después de enviarlo
            }



            
// Seleccionar el contenedor del chat
            const chatContainer = document.querySelector('.chat-container');

            // Verificar el valor de `domain` y cambiar el fondo dinámicamente
            if (domain === "Cooking") {
                chatContainer.style.backgroundImage = "url('static/css/kitchen.jpg')";
            } else if (domain === "fashion") {
                chatContainer.style.backgroundImage = "url('static/css/clothes.jpg')";
            } else if (domain === "Fitness") {
                chatContainer.style.backgroundImage = "url('static/css/gym.png')";
            }
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
                        sendMessage(userInput , "voice");
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




     // Función para enviar mensajes (tanto por texto como por voz)
function sendMessage(userInput, type = "text") {

    console.log("mensaje",userInput);
    if (userInput.trim() !== "") {
        let interaction = startTimer(type);  // Registrar inicio de interacción
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
            logResponse(interaction);  // Registrar el tiempo de respuesta

        // Verificar si data.recipes es un array antes de recorrerlo
        if (Array.isArray(data.recipes)) {
            data.recipes.forEach(item => {
                const listItem = document.createElement("li");

                // Verificamos si el objeto tiene las llaves 'nombre' y 'precio'
                if (item.nombre && item.precio) {
                    listItem.innerHTML = `<div class="producto">
                            <span class="producto-nombre">${item.nombre}</span> - 
                            <span class="producto-precio">${item.precio}</span>
                            <button onclick="addToCart('${selectedModel}', {nombre: '${item.nombre}', precio: '${item.precio}'})">Add to list</button>
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
                                
                                        </div>`;
                } else {
                    // Si no tiene 'nombre' y 'precio' ni 'link' y 'title', mostramos un mensaje por defecto
                    listItem.innerHTML = "Información no válida";
                }

                // Añadir cada item a la lista de recomendaciones
                recommendationsList.appendChild(listItem);
            });
        } else {
            recommendationsList.innerHTML = '<li>.</li>';
        }

        })
        .catch(error => console.error('Error:', error));
    }
}

            // Mostrar las recomendaciones en el cuadro de recomendaciones
            const recommendationsList = document.getElementById("recommendations-list");
            recommendationsList.innerHTML = '';  // Limpiar la lista existente


            // Función para sintetizar y reproducir el audio de la respuesta
            function speakResponse(responseText) {
                const subtitulosContainer = document.getElementById("subtitulos-container");
                if (!subtitulosContainer) {
                    console.error("El contenedor de subtítulos no existe.");
                    return;
                }


                fetch('/synthesize-audio', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ text: responseText, modelo: selectedModel  }),
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
                        const event2 = new CustomEvent('hablar');
                        window.dispatchEvent(event2);
                        isBotSpeaking = true;
                        emitAudioLevels();
                        if (recognition) recognition.stop(); 
                        mostrarSubtitulosProgresivos(responseText, audio.duration, subtitulosContainer);
                    };

                    audio.onended = function() {
                        const event3 = new CustomEvent('parar');
                        window.dispatchEvent(event3);
                        isBotSpeaking = false;
                        if (isListening) recognition.start();
                        const event = new CustomEvent('audio-level', { detail: { amplitude: 0 } });
                        window.dispatchEvent(event);
                        subtitulosContainer.style.display = "none"; 
                    };

                    audio.play();
                })
                .catch(error => {
                    console.error('Error:', error);
                    subtitulosContainer.style.display = "none"; // Ocultar subtítulos en caso de error
                });
            }




            // Función para mostrar subtítulos progresivamente
            function mostrarSubtitulosProgresivos(textoCompleto, duracionAudio, contenedor) {
                const palabras = textoCompleto.split(" ");
                const tiempoPorPalabra = duracionAudio / palabras.length;

                contenedor.textContent = ""; // Limpia los subtítulos previos
                contenedor.style.display = "block";

                let indice = 0;

                const intervalo = setInterval(() => {
                    if (indice < palabras.length) {
                        contenedor.textContent += palabras[indice] + " "; // Añade palabra actual
                        indice++;
                    } else {
                        clearInterval(intervalo); // Detén el intervalo cuando terminen las palabras
                    }
                }, tiempoPorPalabra * 50001); // Convierte el tiempo por palabra a milisegundos
            }



            const dots = document.getElementById("dots");
            // Evento al hacer clic en el botón de enviar texto manualmente
            document.getElementById("send-button").onclick = function() {
    const userInput = document.getElementById("user-input").value.trim(); // Elimina espacios en blanco
    if (userInput) { // Si el input no está vacío
        sendMessage(userInput);
        
        // Cambiar la opacidad de los puntos
        const dots = document.getElementById("dots");
        const event3 = new CustomEvent('pensar');
        window.dispatchEvent(event3);
        dots.style.opacity = 1; // Mostrar los puntos
    } else {
        alert("Please enter a message before sending.");
    }
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
                dots.style.opacity = 1; // Mostrar los puntos

                const event4 = new CustomEvent('pensar');
                window.dispatchEvent(event4);
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
                let interaction = startTimer("image2");
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
                        // Muestra la alerta SweetAlert2
                        Swal.fire({
                            title: 'Success!',
                            text: 'Image uploaded successfully',
                            icon: 'success',
                            confirmButtonText: 'OK'
                        });

                        document.getElementById("chat-box").innerHTML += `<div>Modelo: ${data.response}</div>`;
                        speakResponse(data.response);
                        logResponse(interaction);  
                    })
                    .catch(error => console.error('Error:', error));
                }, 'image/png');
            };

            // Evento al hacer clic en el botón de cargar imagen
            document.getElementById("image-input").addEventListener("change", function() {
                const file = this.files[0];  // Obtener el archivo seleccionado
        
                if (file) {
                    let interaction = startTimer("image1");
                    const formData = new FormData();
                    formData.append('image', file);
                    formData.append('model', selectedModel);
        
                    dots.style.opacity = 1; // Mostrar los puntos
        
                    const event4 = new CustomEvent('pensar');
                    window.dispatchEvent(event4);
        
                    fetch('/upload-image', {
                        method: 'POST',
                        body: formData,
                    })
                    .then(response => response.json())
                    .then(data => {
                        // Muestra la alerta SweetAlert2
                        Swal.fire({
                            title: 'Success!',
                            text: 'Image uploaded successfully',
                            icon: 'success',
                            confirmButtonText: 'OK'
                        });
        
                        document.getElementById("chat-box").innerHTML += `<div>Modelo: ${data.response}</div>`;
                        speakResponse(data.response);
                        logResponse(interaction);  // Registrar el tiempo de respuesta
                    })
                    .catch(error => console.error('Error:', error));
                }
            });

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

            // Función para guardar el tiempo de inicio
            function startTimer(type) {
                return { type: type, startTime: Date.now() };
            }
            
            // Función para registrar el tiempo de respuesta
            function logResponse(interaction) {
                interaction.endTime = Date.now();
                interaction.responseTime = interaction.endTime - interaction.startTime;
            
                fetch('/log-interaction', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(interaction),
                })
                .then(response => response.json())
                .catch(error => console.error('Error al guardar interacción:', error));
            }
        });

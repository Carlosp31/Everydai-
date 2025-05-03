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

        document.addEventListener("DOMContentLoaded", function() {
            
            const microphoneButton = document.getElementById("microphone-button");
            const imageInput = document.getElementById("image-input");
            const imagePreview = document.getElementById("image-preview");
            const videoPreview = document.getElementById("video-preview");
            const captureButton = document.getElementById("capture-button");
            let selectedModel = domain;
            let recognition;
            let isListening = false;
            let isBotSpeaking = false; // Variable para saber si el bot está hablando
            const event_thinking = new CustomEvent('Pensar', { detail: { currentStatus: "Thinking" } });
            document.getElementById("user-input").addEventListener("keypress", function(event) {
                if (event.key === "Enter") {
                    event.preventDefault(); // Evita que se agregue una nueva línea en el input
                    const userInput = document.getElementById("user-input").value.trim().toLowerCase(); // Convertir a minúsculas y eliminar espacios
            
                    if (userInput) { 
                        sendMessage(userInput);
            
                        const dots = document.getElementById("dots");
                        let eventToDispatch = event_thinking;

                        if (userInput.includes("internet") || userInput.includes("web")) {
                            eventToDispatch = new CustomEvent('WebSearching', { detail: { currentStatus: "Web Searching" } });
                        } else if (userInput.includes("comprar") || userInput.includes("buy") || userInput.includes("purchase")) {
                            eventToDispatch = new CustomEvent('SearchingProducts', { detail: { currentStatus: "Searching Products" } });
                        } else if (userInput.includes("inventario") || userInput.includes("inventory") || userInput.includes("stock")) {
                            eventToDispatch = new CustomEvent('UpdatingInventory', { detail: { currentStatus: "Updating Inventory" } });
                        }
                        
                        window.dispatchEvent(eventToDispatch);
            
                        dots.style.opacity = 1; // Mostrar los puntos
                    } else {
                        alert("Please enter a message before sending.");
                    }
                }
            });
            
            

            
            const chatContainer = document.querySelector('.chat-container');

            // Verificar el valor de `domain` y cambiar el fondo dinámicamente
            if (domain === "Cooking") {
                chatContainer.style.backgroundImage = "url('static/css/kitchen.jpg')";
            } else if (domain === "fashion") {
                chatContainer.style.backgroundImage = "url('static/css/clothes.jpg')";
            } else if (domain === "Fitness") {
                chatContainer.style.backgroundImage = "url('static/css/gym.png')";
            }
            let audioDetected = false; // Variable para verificar si hubo audio reconocido
            // Función para iniciar el reconocimiento de voz y el espectro de frecuencias
            function startVoiceRecognition() {
                if (!recognition) {
                    recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
                    recognition.lang = 'es-ES';
                    recognition.continuous = false;
                    recognition.interimResults = false;
                }

                recognition.onresult = function(event) {
                    if (!isBotSpeaking) { // Solo procesar si el bot no está 
                        audioDetected = true; // Se detectó voz
                        const userInput = event.results[0][0].transcript;
                        document.getElementById("user-input").value = userInput;
                        sendMessage(userInput , "voice");
                        dots.style.opacity = 1; // Mostrar los puntos
                        let eventToDispatch = event_thinking;

                        if (userInput.includes("internet") || userInput.includes("web")) {
                            eventToDispatch = new CustomEvent('WebSearching', { detail: { currentStatus: "Web Searching" } });
                        } else if (userInput.includes("comprar") || userInput.includes("buy") || userInput.includes("purchase")) {
                            eventToDispatch = new CustomEvent('SearchingProducts', { detail: { currentStatus: "Searching Products" } });
                        } else if (userInput.includes("inventario") || userInput.includes("inventory") || userInput.includes("stock")) {
                            eventToDispatch = new CustomEvent('UpdatingInventory', { detail: { currentStatus: "Updating Inventory" } });
                        }
                        
                        window.dispatchEvent(eventToDispatch);
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
                audioDetected = false; // Se detectó voz
            }

            // Evento para iniciar o detener el reconocimiento de voz con el botón de 'Start Conversation'
            microphoneButton.onclick = function() {
                if (!isListening) {
                    isListening = true;
                    document.getElementById("mic-icon").style.color = "green";
                    startVoiceRecognition();
                    if (!isBotSpeaking) {
                        const event_listening = new CustomEvent('Listening', { detail: { currentStatus: "Listening" } });
                        window.dispatchEvent(event_listening);
                    }
                } else {
                    isListening = false;
                    document.getElementById("mic-icon").style.color = "white";
                    if (recognition) {
                        recognition.stop();
                    }
                    if (!audioDetected && !isBotSpeaking) {
                        const event_stop_listening = new CustomEvent('Stop', { detail: { currentStatus: "Ready" } });
                        window.dispatchEvent(event_stop_listening);
                    }
                }
            };





     // Función para enviar mensajes (tanto por texto como por voz)
     window.sendMessage= function(userInput, type = "text") {
        console.log(userInput)
        if (type == "detection"){
            const dots = document.getElementById("dots");
                    dots.style.opacity = 1; // Mostrar los puntos
                    const event_detection = new CustomEvent('Detección', { detail: { currentStatus: "Processing detections" } });
                    window.dispatchEvent(event_detection);
        }

        if (userInput.trim() !== "") {
            let interaction = startTimer(type);
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
                let responseType = (data.response_3 && data.response_3.trim() !== "") ? data.response_3 : type;
                document.getElementById("chat-box").innerHTML += `<div>AI: ${data.text_response}</div>`;
                speakResponse(data.text_response);
                logResponse(interaction, responseType);  // Registrar el tiempo de respuesta
    
        if (Array.isArray(data.recipes) && !responseType.includes("inventory")) {
            data.recipes.forEach(item => {
                const listItem = document.createElement("li");

                if (item.nombre && item.precio) {
                    // Generar el nombre del producto, opcionalmente con enlace
                    const nombreProducto = item.enlace
                        ? `<a href="${item.enlace}" target="_blank" rel="noopener noreferrer">${item.nombre}</a>`
                        : item.nombre;
        
                    listItem.innerHTML = `<div class="producto">
                            <span class="producto-nombre">${nombreProducto}</span> - 
                            <span class="producto-precio">${item.precio}</span>
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
                } 
                // Añadir cada item a la lista de recomendaciones
                recommendationsList.appendChild(listItem);
            });
        }else if (
            typeof data.recipes === "object" &&
            data.recipes !== null &&
            !responseType.includes("inventory") &&
            Object.entries(data.recipes).every(([key, value]) => 
                typeof key === "string" && typeof value === "string"
            )
        ) {
            // CASO 2: Diccionario válido { nombre: link }
            Object.entries(data.recipes).forEach(([nombre, link]) => {
                const listItem = document.createElement("li");
                listItem.innerHTML = `<div class="image-preview">
                        <p class="image-title">${nombre}</p>
                        <a href="${link}" target="_blank" rel="noopener noreferrer">
                            <img src="${link}" alt="${nombre}" class="thumbnail">
                        </a>
                      </div>`;
                recommendationsList.appendChild(listItem);
            });
        }

        })
        .catch(error => console.error('Error:', error));
    }
}

// Mostrar las recomendaciones en el cuadro de recomendaciones
const recommendationsList = document.getElementById("recommendations-list");
recommendationsList.innerHTML = '';  // Limpiar la lista existente


            // Función para sintetizar y reproducir el audio de la respuesta
            window.speakResponse = function (responseText) {
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
                        const event_hablar = new CustomEvent('Hablar', { detail: { currentStatus: "Speaking" } });
                        window.dispatchEvent(event_hablar);
                        isBotSpeaking = true;
                        emitAudioLevels();
                        if (recognition) recognition.stop(); 
                        mostrarSubtitulosProgresivos(responseText, audio.duration, subtitulosContainer);
                    };

                    audio.onended = function() {
                        const event_parar = new CustomEvent('Parar', { detail: { currentStatus: "Ready" } });
                        window.dispatchEvent(event_parar);
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
                const event_pensar_captura = new CustomEvent('Pensar', { detail: { currentStatus: "Analyzing Photo" } });
                window.dispatchEvent(event_pensar_captura);
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
                        credentials: 'include',  // 👈 SUPER importante
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
        
                    const event_pensar_imagen = new CustomEvent('Pensar', { detail: { currentStatus: "Analyzing Image" } });
                    window.dispatchEvent(event_pensar_imagen);
                    fetch('/upload-image', {
                        method: 'POST',
                        credentials: 'include',  // 👈 SUPER importante
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
            window.startTimer = function(type) {
                return { type: type, startTime: Date.now() };
            }
            window.sendMessage("Hola")
            // Función para registrar el tiempo de respuesta
            window.logResponse = function(interaction, responseType) {
                interaction.endTime = Date.now();
                interaction.responseTime = interaction.endTime - interaction.startTime;
                interaction.responseType = responseType; // ✅ Agregamos responseType al objeto
            
                fetch('/log-interaction', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(interaction),
                })
                .then(response => response.json())
                .catch(error => console.error('Error al guardar interacción:', error));
            }
        });

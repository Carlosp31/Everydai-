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
            window.location.href = `/realidadpro3?domain=${encodeURIComponent(domain)}`;
        }
        document.addEventListener("DOMContentLoaded", function() {
            const imageInput = document.getElementById("image-input");
            let selectedModel = domain;
            const imagePreview = document.getElementById("image-preview");
            const videoPreview = document.getElementById("video-preview");
            const canvas = document.getElementById("canvas");
            const captureButton = document.getElementById("capture-button");
            let recognition;
            let isListening = false;
            let isBotSpeaking = false; // Variable para saber si el bot está hablando
            // Función para iniciar el reconocimiento de voz y el espectro de frecuencias
            

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
                    // Mostrar subtítulos
                //subtitulosContainer.textContent = responseText;
                //subtitulosContainer.style.display = "block";

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
                        // Muestra la alerta SweetAlert2
                        Swal.fire({
                            title: 'Success!',
                            text: 'Image uploaded successfully',
                            icon: 'success',
                            confirmButtonText: 'OK'
                        });

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

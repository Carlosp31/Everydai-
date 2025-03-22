let animations
let mixer; // AnimationMixer
let animationActions = {}; // Guardará las animaciones por nombre
let activeAction; // Animación activa
let animationpath;
// Cargar el archivo GLB

// Crear la escena y la cámara
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(65, 500 / 500, 0.1, 1000);
camera.position.set(0, 3.1, 0.9); // Ajustamos la altura para estar a nivel de los ojos del avatar

// Configurar el renderizador
const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
renderer.setSize(600, 500);
document.getElementById("avatar-container").appendChild(renderer.domElement);

// Añadir luces a la escena
const ambientLight = new THREE.AmbientLight(0xffffff, 1.5);
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 1.3);
directionalLight.position.set(1, 1, 1).normalize();
scene.add(directionalLight);

// Obtener el parámetro 'domain' desde la URL

// Definir la ruta del modelo en función del dominio
let modelPath;
function getModelPaths(domain) {
    if (models[domain]) {
        return models[domain];
    } else {
        console.error("Dominio no encontrado:", domain);
        return null;
    }
}
avatarpath = getModelPaths(domain);
modelPath = avatarpath.modelPath
animationpath= avatarpath.animationPath
// Cargar el modelo 3D seleccionado
const loader = new THREE.GLTFLoader();
let model;

if (modelPath) {
loader.load(modelPath, function(gltf) {
model = gltf.scene;
scene.add(model);
model.traverse((child) => {
    if (child.isMesh && child.name === 'Wolf3D_Head') {
        jawOpenTarget = child.morphTargetDictionary['jawOpen'];

        // Establecer el valor de jawOpen al 1 por defecto
        if (jawOpenTarget !== undefined) {
            child.morphTargetInfluences[jawOpenTarget] = 0; // 1 representa la apertura total de la mandíbula
        }
    }
    
});
loadAnimations()

// Asegurarse de que el avatar esté mirando hacia la cámara
model.rotation.y = 0;  // Asegura que el modelo esté mirando hacia la cámara desde el inicio
model.rotation.x = 0;

// Centrar el modelo en la escena (en el centro del div)
let yPosition = (domain === "Fitness") ? 1.6 : 1.66;
model.position.set(0, yPosition, 0);

// Animar el modelo
function animate() {
    requestAnimationFrame(animate);
    if (mixer) {

        mixer.update(0.01); // Actualizar el mixer
    }
    renderer.render(scene, camera);
}
animate();

});

function loadAnimations() {
loader.load(
animationpath,
function (gltf) {
    animations = gltf.animations; // Extraer los clips de animación
    mixer = new THREE.AnimationMixer(model); // Vincular el mixer al avatar
    
    animations.forEach((clip) => {
        clip.tracks = clip.tracks.filter((track) => {
            return !track.name.includes('position'); // Ignora canales de posición
        });
       
        const action = mixer.clipAction(clip);
        animationActions[clip.name] = action; // Guardar la acción por su nombre
    });
    playAnimationSequence("salute", "pose")
    
},

undefined,
function (error) {
    console.error('Error al cargar las animaciones:', error);
} 
);   
}
function playAnimationSequence(firstAnimationName, secondAnimationName) {
if (activeAction) {
activeAction.fadeOut(0.5);
}

// Aplicar los morph targets de la sonrisa
if (model) {
model.traverse((child) => {
    if (child.isMesh && child.name === 'Wolf3D_Head') {
        const morphs = {
            browInnerUp: 0.17,
            eyeSquintLeft: 0.4,
            eyeSquintRight: 0.44,
            noseSneerLeft: 0.17,
            noseSneerRight: 0.14,
            mouthPressLeft: 0.61,
            mouthPressRight: 0.41
        };

        Object.keys(morphs).forEach((key) => {
            if (child.morphTargetDictionary[key] !== undefined) {
                child.morphTargetInfluences[child.morphTargetDictionary[key]] = morphs[key];
            }
        });
    }
});
}

// Configurar la primera animación
const firstAction = animationActions[firstAnimationName];
firstAction.reset();
firstAction.setLoop(THREE.LoopOnce);
firstAction.timeScale = 0.8;
firstAction.clampWhenFinished = true;

// Configurar la segunda animación
const secondAction = animationActions[secondAnimationName];
secondAction.reset();
secondAction.setLoop(THREE.LoopRepeat);

activeAction = firstAction;
firstAction.fadeIn(0.5).play();

mixer.addEventListener('finished', (event) => {
if (event.action === firstAction) {
    activeAction.fadeOut(0.8);
    activeAction = secondAction;
    secondAction.fadeIn(0.6).play();
}
});
}

function playAnimationLoop(animationName, speed) {
// Detener cualquier animación activa (incluidas las de playAnimationSequence)
if (activeAction) {
activeAction.fadeOut(0.5); // Transición suave al detener
}

// Aplicar los morph targets de la sonrisa
if (model) {
model.traverse((child) => {
    if (child.isMesh && child.name === 'Wolf3D_Head') {
        const morphs = {
            browInnerUp: 0.17,
            eyeSquintLeft: 0.4,
            eyeSquintRight: 0.44,
            noseSneerLeft: 0.17,
            noseSneerRight: 0.14,
            mouthPressLeft: 0.61,
            mouthPressRight: 0.41
        };

        Object.keys(morphs).forEach((key) => {
            if (child.morphTargetDictionary[key] !== undefined) {
                child.morphTargetInfluences[child.morphTargetDictionary[key]] = morphs[key];
            }
        });
    }
});
}

// Configurar y reproducir la nueva animación
const loopAction = animationActions[animationName];
loopAction.reset();
loopAction.setLoop(THREE.LoopRepeat); // Repetir en bucle
loopAction.timeScale = speed; // Ajustar la velocidad de reproducción
activeAction = loopAction;
loopAction.fadeIn(0.5).play();
}

function playAnimationOnce(animationName) {
if (activeAction) {
activeAction.stop(); // Detener la animación activa actual
}
activeAction = animationActions[animationName];
activeAction.reset();
activeAction.fadeIn(1);
activeAction.play(); // Reiniciar y reproducir la nueva animación
activeAction.setLoop(THREE.LoopOnce, 1); // Asegurarse de que la animación se ejecute solo una vez
}

window.addEventListener('hablar', () => {
dots.style.opacity = 0;
playAnimationLoop("talking", 1);
});
window.addEventListener('pensar', () => {

playAnimationLoop("thinking", 0.5);
});

window.addEventListener('parar', () => {
playAnimationLoop("pose")
});

let jawResetTimeout;

window.addEventListener('audio-level', (event) => {
    const amplitude = event.detail.amplitude;

    if (jawOpenTarget !== null && model) {
        model.traverse((child) => {
            if (child.isMesh && child.name === 'Wolf3D_Head') {
                child.morphTargetInfluences[jawOpenTarget] = amplitude;
            }
        });
    }

    // Reinicia el temporizador cada vez que hay audio
    clearTimeout(jawResetTimeout);
    jawResetTimeout = setTimeout(() => {
        if (jawOpenTarget !== null && model) {
            model.traverse((child) => {
                if (child.isMesh && child.name === 'Wolf3D_Head') {
                    child.morphTargetInfluences[jawOpenTarget] = 0;
                }
            });
        }
    }, 100); // Se resetea después de 200ms sin eventos
});



// Función para realizar el parpadeo
function blink() {
model.traverse((child) => {
if (child.isMesh && child.name === 'Wolf3D_Head') {
let blinkProgress = 0;
let direction = 1; // 1 para cerrar el ojo, -1 para abrirlo
const blinkSpeed = 0.1; // Velocidad del parpadeo

function animateBlink() {
blinkProgress += direction * blinkSpeed;
if (blinkProgress >= 1) {
direction = -1; // Cambiar dirección para abrir el ojo
} else if (blinkProgress <= 0) {
cancelAnimationFrame(animateBlinkId); // Finalizar la animación
return;
}
// Actualizar los morphTargets
child.morphTargetInfluences[child.morphTargetDictionary['eyeBlinkLeft']] = blinkProgress;
child.morphTargetInfluences[child.morphTargetDictionary['eyeBlinkRight']] = blinkProgress;

// Continuar la animación
animateBlinkId = requestAnimationFrame(animateBlink);
}

let animateBlinkId = requestAnimationFrame(animateBlink);
}
});
}

// Función para iniciar parpadeos aleatorios
function startRandomBlinks() {
function scheduleNextBlink() {
const randomDelay = Math.random() * 3000 + 2000; // Entre 2 y 5 segundos
setTimeout(() => {
blink();
scheduleNextBlink(); // Planificar el siguiente parpadeo
}, randomDelay);
}

scheduleNextBlink(); // Iniciar el primer parpadeo
}

// Iniciar parpadeos aleatorios
startRandomBlinks();
}






// Variables para el control del mouse
let isMouseDown = false;
let previousMousePosition = { x: 0, y: 0 };

// Detectar cuando el mouse se presiona
document.addEventListener('mousedown', (event) => {
    isMouseDown = true;
    previousMousePosition.x = event.clientX;
    previousMousePosition.y = event.clientY;
});

// Detectar cuando el mouse se mueve mientras está presionado
document.addEventListener('mousemove', (event) => {
    if (!isMouseDown || !model) return;

    const deltaX = event.clientX - previousMousePosition.x;
    model.rotation.y += deltaX * 0.01;

    previousMousePosition.x = event.clientX;
});

// Detectar cuando el mouse se libera
document.addEventListener('mouseup', () => {
    isMouseDown = false;
});

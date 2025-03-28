document.getElementById('openModalButton').addEventListener('click', function() {
    Swal.fire({
        title: 'User Guide',
        html: `
            <p>Welcome to EverydAI user guide. Here you can:</p>
            <ul>
                <li>Select the domain for your daily activities.</li>
                <li>Talk with the avatars to receive help on your daily tasks.</li>
                <li>Receive information based on the elements you share to our avatars.</li>
            </ul>
        `,
        icon: 'info',
        confirmButtonText: 'Close'
    });
});


// Crear la escena y la cámara
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, 500 / 500, 0.1, 1000);
camera.position.z = 2.5; // Colocar la cámara a cierta distancia

// Configurar el renderizador
const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
renderer.setSize(1000, 1000);
document.getElementById("avatar-container").appendChild(renderer.domElement);

// Añadir luces a la escena
const ambientLight = new THREE.AmbientLight(0xffffff, 1.5); // Aumentar la intensidad de la luz ambiental
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 1.2); // Aumentar la intensidad de la luz direccional
directionalLight.position.set(1, 1, 1).normalize();
scene.add(directionalLight);

// Cargar el primer modelo 3D (avatar1) - avatar en la escena
const loader = new THREE.GLTFLoader();
let model1;
const modelUrl3 = document.getElementById('model-url3').getAttribute('data-url3');
loader.load(modelUrl3, function(gltf) {
    model1 = gltf.scene;
    scene.add(model1);
    model1.position.set(0, 0, 0);
    // Asegurarse de que el avatar esté mirando hacia la cámara
    model1.rotation.y = 0;
    model1.rotation.x = 0;

        // Aplicar morph targets al rostro
        model1.traverse((child) => {
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


// Cargar la animación desde animationschef.glb para avatar1
let animations1;
const animationLoader1 = new THREE.GLTFLoader();
const modelURLani3 = document.getElementById('model-urlani3').getAttribute('data-urlani3');
animationLoader1.load(modelURLani3, function(gltf) {
    animations1 = gltf.animations;

    // Buscar la animación llamada "pose"
    const poseAnimation = animations1.find(animation => animation.name === "pose");

    if (poseAnimation) {
        // Eliminar las pistas de posición de la animación
        poseAnimation.tracks = poseAnimation.tracks.filter(track => !track.name.includes('.position'));

        // Crear un Action de animación y reproducirla
        const mixer = new THREE.AnimationMixer(model1);  // Usamos model1 porque es el que tiene el avatar
        const action = mixer.clipAction(poseAnimation);
        action.fadeIn(0.5).play();

        // Animar la escena con la animación
        function animate() {
            requestAnimationFrame(animate);
            mixer.update(0.01);  // Actualizar la animación
            renderer.render(scene, camera);
        }
        animate();
    }
});
});
// Cargar el segundo modelo 3D (avatar2) y su animación (animationsgym.glb)
let model2;
const modelUrl2 = document.getElementById('model-url2').getAttribute('data-url2');
loader.load(modelUrl2, function(gltf) {
    model2 = gltf.scene;
    scene.add(model2);
    model2.position.set(1.2, 0, 0);
    model2.rotation.y = 0;
    model2.rotation.x = 0;

    // Aplicar morph targets al rostro
    model2.traverse((child) => {
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

    // Cargar la animación desde animationsgym.glb
    let animations2;
    const modelURLani2 = document.getElementById('model-urlani2').getAttribute('data-urlani2');
    const animationLoader2 = new THREE.GLTFLoader();
    animationLoader2.load(modelURLani2, function(gltf) {
        animations2 = gltf.animations;

        // Buscar la animación llamada "pose"
        const gymAnimation = animations2.find(animation => animation.name === "pose");

        if (gymAnimation) {
            // Eliminar las pistas de posición de la animación
            gymAnimation.tracks = gymAnimation.tracks.filter(track => !track.name.includes('.position'));

            // Crear un Action de animación y reproducirla
            const mixer = new THREE.AnimationMixer(model2);
            const action = mixer.clipAction(gymAnimation);
            action.fadeIn(0.5).play();

            // Animar la escena con la animación
            function animate() {
                requestAnimationFrame(animate);
                mixer.update(0.01);
                renderer.render(scene, camera);
            }
            animate();
        }
    });
});


// Cargar el tercer modelo 3D (avatar3) y su animación (animationsfashion.glb)
let model3;
const modelUrl = document.getElementById('model-url').getAttribute('data-url');
loader.load(modelUrl, function(gltf) {
    model3 = gltf.scene;
    scene.add(model3);
    model3.position.set(-1.2, 0, 0);
    model3.rotation.y = 0;
    model3.rotation.x = 0;
    // Aplicar morph targets al rostro
    model3.traverse((child) => {
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
    // Cargar la animación desde animationsfashion.glb
    let animations3;
    const modelURLani = document.getElementById('model-urlani').getAttribute('data-urlani');
    const animationLoader3 = new THREE.GLTFLoader();
    animationLoader3.load(modelURLani, function(gltf) {
        animations3 = gltf.animations;

        // Buscar la animación llamada "pose" (o la animación que deseas aplicar)
        const fashionAnimation = animations3.find(animation => animation.name === "dash_pose");

        if (fashionAnimation) {
            // Eliminar las pistas de posición de la animación
            fashionAnimation.tracks = fashionAnimation.tracks.filter(track => !track.name.includes('.position'));

            // Crear un Action de animación y reproducirla
            const mixer = new THREE.AnimationMixer(model3);  // Usamos model3 porque es el avatar3
            const action = mixer.clipAction(fashionAnimation);
            action.fadeIn(0.5).play();

            // Animar la escena con la animación
            function animate() {
                requestAnimationFrame(animate);
                mixer.update(0.01);  // Actualizar la animación
                renderer.render(scene, camera);
            }
            animate();
        }
    });
});

// Variables para el control del mouse
let isMouseDown = false;
let previousMousePosition = { x: 0, y: 0 };

document.addEventListener('mousedown', (event) => {
    isMouseDown = true;
    previousMousePosition.x = event.clientX;
    previousMousePosition.y = event.clientY;
});

document.addEventListener('mousemove', (event) => {
    if (!isMouseDown) return;

    const deltaX = event.clientX - previousMousePosition.x;
    const deltaY = event.clientY - previousMousePosition.y;

    if (model1) model1.rotation.y += deltaX * 0.01;
    if (model2) model2.rotation.y += deltaX * 0.01;
    if (model3) model3.rotation.y += deltaX * 0.01;

    previousMousePosition.x = event.clientX;
    previousMousePosition.y = event.clientY;
});

document.addEventListener('mouseup', () => {
    isMouseDown = false;
});

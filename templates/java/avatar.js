        // Crear la escena y la cámara
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(65, 500 / 500, 0.1, 1000);
        camera.position.set(0, 3.1, 0.9); // Ajustamos la altura para estar a nivel de los ojos del avatar
        
        // Configurar el renderizador
        const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
        renderer.setSize(600, 500);
        document.getElementById("avatar-container").appendChild(renderer.domElement);
    
        // Añadir luces a la escena
        const ambientLight = new THREE.AmbientLight(0xffffff, 1.0);
        scene.add(ambientLight);
    
        const directionalLight = new THREE.DirectionalLight(0xffffff, 1.2);
        directionalLight.position.set(1, 1, 1).normalize();
        scene.add(directionalLight);
    
        // Obtener el parámetro 'domain' desde la URL
        const urlParams = new URLSearchParams(window.location.search);
        const domain = urlParams.get('domain');
    
        // Definir la ruta del modelo en función del dominio
        let modelPath;
        switch (domain) {
            case 'culinary':
                modelPath = '{{ url_for("static", filename="models/avatar1.glb") }}';
                break;
            case 'fashion':
                modelPath = '{{ url_for("static", filename="models/avatar3.glb") }}';
                break;
            case 'gym':
                modelPath = '{{ url_for("static", filename="models/avatar2.glb") }}';
                break;
            default:
                console.error('Dominio no reconocido.');
        }
    
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
        
        // Asegurarse de que el avatar esté mirando hacia la cámara
        model.rotation.y = 0;  // Asegura que el modelo esté mirando hacia la cámara desde el inicio
        model.rotation.x = 0;
    
        // Centrar el modelo en la escena (en el centro del div)
        model.position.set(0, 1.6, 0);  // Coloca el modelo en el origen (0, 0, 0)
        
        // Animar el modelo
        function animate() {
            requestAnimationFrame(animate);
            renderer.render(scene, camera);
        }
        animate();
    });
    
    window.addEventListener('audio-level', (event) => {
        const amplitude = event.detail.amplitude;

        if (jawOpenTarget !== null && model) {
            model.traverse((child) => {
                if (child.isMesh && child.name === 'Wolf3D_Head') {
                    child.morphTargetInfluences[jawOpenTarget] = amplitude;
                }
            });
        }
    });
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
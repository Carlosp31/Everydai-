let detectionInterval;
let detectedClasses = new Set(); // Guarda solo los nombres de las clases detectadas

let videoStream = null;

async function sendFrameToRoboflow(frameBase64) {
const apiKey = "ASM9d0x59Igg7FJzi6fu";

let model, version;

if (domain === "Cooking") {
    model = "food-ingredients-detection-qfit7";
    version = "48";
} else if (domain === "fashion") {
    model = "main-fashion-wmyfk";  // Completa con el modelo correspondiente
    version = "1";  // Completa con la versión correspondiente
} else if (domain === "Fitness") {
    model = "all-gym-equipment";  // Completa con el modelo correspondiente
    version = "2";  // Completa con la versión correspondiente
} else {
    console.error("❌ Dominio no reconocido");
    return;
}

const url = `https://detect.roboflow.com/${model}/${version}?api_key=${apiKey}`;

try {
    const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: frameBase64 
    });

    const data = await response.json();
    console.log(data.predictions.map(p => p.class));

    if (data.predictions && data.predictions.length > 0) {
        drawBoundingBoxes(data.predictions);
        saveDetections(data.predictions);
    }
} catch (error) {
    console.error("❌ Error al enviar imagen a Roboflow:", error);
}
}


function drawBoundingBoxes(predictions) {
    const canvas = document.getElementById('canvas');
    const video = document.getElementById('video');
    const ctx = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    predictions.forEach(pred => {
        const x = pred.x - pred.width / 2;
        const y = pred.y - pred.height / 2;
        ctx.beginPath();
        ctx.rect(x, y, pred.width, pred.height);
        ctx.strokeStyle = 'red';
        ctx.lineWidth = 3;
        ctx.stroke();
        ctx.font = '16px Arial';
        ctx.fillStyle = 'red';
        ctx.fillText(pred.class, x, y - 10);
    });
}
function clearBoundingBoxes() {
const canvas = document.getElementById('canvas');
if (canvas) {
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
}
}
function saveDetections(predictions) {
    let batchDetected = new Set();

    predictions.forEach(pred => {
        if (!detectedClasses.has(pred.class) || batchDetected.has(pred.class)) {
            detectedClasses.add(pred.class);
            batchDetected.add(pred.class);
            updateDetectionList(pred.class);
        }
    });
}

function updateDetectionList(objectName) {
    const ul = document.getElementById("detections-list");
    const li = document.createElement("li");
    li.textContent = objectName;
    ul.appendChild(li);
}

async function captureFrame() {
    const videoElement = document.getElementById('video');
    const canvas = document.createElement('canvas');
    canvas.width = videoElement.videoWidth || 640;
    canvas.height = videoElement.videoHeight || 480;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
    const imageBase64 = canvas.toDataURL('image/jpeg').split(",")[1]; 
    sendFrameToRoboflow(imageBase64);
}

function startDetection() {
    if (!detectionInterval) {
        startCamera()
        detectedClasses.clear();
        document.getElementById("detections-list").innerHTML = "";
        detectionInterval = setInterval(captureFrame, 2000);
    }
}

async function stopDetection() {
if (detectionInterval !== null) {
    clearInterval(detectionInterval);
    detectionInterval = null;
}
stopCamera();
clearBoundingBoxes();

if (detectedClasses.size === 0) {
    alert("No hay detecciones para enviar.");
    return;
}

let message = [
    { type: "text", text: "Los elementos escaneados son los siguientes:" },
    ...Array.from(detectedClasses).map(item => ({
        type: "text",
        text: item
    }))
];

// Guardamos el mensaje en sessionStorage antes de redirigir
sendMessage(JSON.stringify(message), "detection")
document.getElementById("content").style.display = "block";
document.getElementById("detection-styles").href = ""; // Quitar CSS
}



function startCamera() {
    const videoElement = document.getElementById('video');
    return navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } })
        .then(stream => {
            videoStream = stream;
            videoElement.srcObject = stream;
        })
        .catch(error => console.error("Error al acceder a la cámara:", error));
}
function stopCamera() {
    if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
        videoStream = null;
    }
    document.getElementById('video').srcObject = null;
}


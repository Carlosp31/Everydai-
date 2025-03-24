window.currentStatus = "Ready"; // Variable global accesible desde cualquier parte

function updateStatus(status) {
    window.currentStatus = status; // Actualizar la variable global en window
    const statusIndicator = document.getElementById("status-indicator");
    if (statusIndicator) {
        statusIndicator.textContent = window.currentStatus;
        statusIndicator.style.display = "block"; // Asegura que sea visible
    }
}

// Escuchar el evento 'Listening' y actualizar el estado
window.addEventListener("Listening", (event) => {
    updateStatus(event.detail.currentStatus);
});
window.addEventListener("Pensar", (event) => {
    updateStatus(event.detail.currentStatus);
});
window.addEventListener("Hablar", (event) => {
    updateStatus(event.detail.currentStatus);
});
window.addEventListener("Parar", (event) => {
    updateStatus(event.detail.currentStatus);
});
window.addEventListener("Stop", (event) => {
    updateStatus(event.detail.currentStatus);
});
// Mostrar el estado inicial al cargar la página
document.addEventListener("DOMContentLoaded", () => {
    updateStatus(window.currentStatus);
});



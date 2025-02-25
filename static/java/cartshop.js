const cart = [];
const cartButton = document.getElementById("cart-button");
const cartDropdown = document.getElementById("cart-dropdown");
const cartItemsList = document.getElementById("cart-items");

// ✅ Función para añadir items al carrito y enviarlos al backend
window.addToCart = function(item) {
    cart.push(item);  // Añadir al carrito en el frontend
    updateCartDropdown();  // Actualizar la interfaz

    // Enviar el item al backend para guardarlo en la base de datos
    const domainId = 1; // ⚠️ Asegúrate de obtener el dominio correcto
    sendCartToBackend(domainId, item);
};

// ✅ Función para actualizar la visualización del carrito en el frontend
function updateCartDropdown() {
    cartItemsList.innerHTML = ''; // Limpiar el contenido actual

    cart.forEach(item => {
        const listItem = document.createElement("li");

        // Si es un producto con 'nombre' y 'precio'
        if (item.nombre && item.precio) {
            listItem.textContent = `${item.nombre} - $${item.precio}`;
        
        // Si es una receta con 'link' y 'title'
        } else if (item.link && item.title) {
            listItem.textContent = item.title;
            listItem.onclick = () => window.open(item.link, "_blank"); // Abrir enlace en nueva pestaña
            listItem.style.cursor = "pointer"; // Indicar que es clickeable
        }

        cartItemsList.appendChild(listItem);
    });
}

// ✅ Toggle del desplegable del carrito
cartButton.onclick = function() {
    cartDropdown.style.display = cartDropdown.style.display === 'none' ? 'block' : 'none';
};

// ✅ Función para cargar el carrito desde la base de datos
function loadCart(domainId) {
    fetch(`/get_shopping_list?domain_id=${domainId}`)
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error("Error al obtener la lista de compras:", data.error);
            return;
        }

        cart.length = 0; // Vaciar el carrito local
        cart.push(...data.items); // Cargar los items desde la base de datos
        updateCartDropdown(); // Refrescar la interfaz
    })
    .catch(error => console.error("Error al cargar el carrito:", error));
}

function sendCartToBackend(domainName, item) {
    fetch('/add_to_cart', {
        method: 'POST',
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
            domain_name: domainName, // Enviar domain_name en lugar de domain_id
            item: item 
        })
    })

    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error("Error al añadir al carrito:", data.error);
        } else {
            console.log("Carrito actualizado en la base de datos:", data.items);
        }
    })
    .catch(error => console.error("Error al enviar carrito:", error));
}

// ✅ Cargar el carrito al iniciar la página
document.addEventListener("DOMContentLoaded", function () {
    const domainId = 1; // ⚠️ Asegúrate de obtener el dominio correcto
    loadCart(domainId);
});


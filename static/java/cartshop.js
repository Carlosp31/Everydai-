const cart = [];
const cartButton = document.getElementById("cart-button");
const cartDropdown = document.getElementById("cart-dropdown");
const cartItemsList = document.getElementById("cart-items");

// Función para añadir items al carrito
window.addToCart = function(item) {
    cart.push(item);
    updateCartDropdown();
};

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

// Toggle del desplegable del carrito
cartButton.onclick = function() {
    cartDropdown.style.display = cartDropdown.style.display === 'none' ? 'block' : 'none';
};



function loadCart(domainId) {
    fetch(`/get_cart?domain_id=${domainId}`)
    .then(response => response.json())
    .then(data => {
        console.log("Carrito cargado:", data.items);
    })
    .catch(error => console.error("Error al cargar el carrito:", error));
}



function sendCartToBackend(domainId, item) {
    fetch('/add_to_cart', {
        method: 'POST',
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            domain_id: domainId,
            item: item
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log("Carrito actualizado:", data);
    })
    .catch(error => console.error("Error al enviar carrito:", error));
}

// Ejemplo: Añadir una manzana al carrito del usuario autenticado
const domainId = 1;  // Identificador del dominio en el que trabaja el usuario
const newItem = { nombre: "Manzana", precio: 2000 };

sendCartToBackend(domainId, newItem);


document.addEventListener("DOMContentLoaded", function () {
    fetch("/get_shopping_list")
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error("Error al obtener la lista de compras:", data.error);
                return;
            }

            const cartContainer = document.getElementById("cart-items"); // Ajusta este ID según tu HTML

            data.items.forEach(item => {
                const itemElement = document.createElement("div");
                itemElement.classList.add("cart-item");
                itemElement.innerHTML = `
                    <p>${item.nombre} - $${item.precio}</p>
                `;
                cartContainer.appendChild(itemElement);
            });
        })
        .catch(error => console.error("Error al cargar el carrito:", error));
});

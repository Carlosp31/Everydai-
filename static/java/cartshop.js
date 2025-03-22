const wishList = [];
const wishButton = document.getElementById("wish-button");
const wishDropdown = document.getElementById("wish-dropdown");
const wishItemsList = document.getElementById("wish-items");

// Obtener el nombre del dominio desde la URL
const urlParams = new URLSearchParams(window.location.search);
const domain = urlParams.get('domain') || 'Dominio no disponible';
// ✅ Función para obtener la lista de deseos del usuario
function fetchWishList() {
    fetch('/get_wish_list')
        .then(response => response.json())
        .then(data => {
            console.log("Respuesta del backend (Wish List):", data);
            if (data.error) {
                console.error("Error al obtener la lista de deseos:", data.error);
                return;
            }
            wishList.length = 0;
            wishList.push(...data.items);
            updateWishDropdown();
        })
        .catch(error => console.error("Error al obtener la lista de deseos:", error));
}

function updateWishDropdown() {
    wishItemsList.innerHTML = ''; // Limpiar la lista

    wishList.forEach((item) => {
        const listItem = document.createElement("li");
        
        const name = item.name || 'Nombre no disponible';
        const price = item.price || 'Precio no disponible';
        
        listItem.textContent = `${name} - ${price} `;

        // Botón para eliminar el elemento
        const deleteButton = document.createElement("button");
        deleteButton.textContent = "Eliminar";
        deleteButton.onclick = () => removeFromWishList(name);

        listItem.appendChild(deleteButton);
        wishItemsList.appendChild(listItem);
    });
}

// ✅ Función para eliminar un ítem de la lista de deseos
function removeFromWishList(itemName) {
    fetch('/remove_from_wish_list', {
        method: 'POST',
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ domain_name: domain, item_name: itemName })
    })
    .then(response => response.json())
    .then(data => {
        console.log("✅ Respuesta del backend:", data);
        if (!data.error) {
            // Eliminar el ítem localmente y actualizar la lista
            const index = wishList.findIndex(item => item.name === itemName);
            if (index !== -1) {
                wishList.splice(index, 1);
                updateWishDropdown();
            }
        }
    })
    .catch(error => console.error("❌ Error en la petición:", error));
}

// ✅ Mostrar/Ocultar la lista de deseos
wishButton.addEventListener("click", () => {
    if (wishDropdown.style.display === "none" || wishDropdown.style.display === "") {
        fetchWishList(); // Cargar los datos cuando se abre
        wishDropdown.style.display = "block";
    } else {
        wishDropdown.style.display = "none";
    }
});

function addToCart(domainName, item) {
    const normalizedItem = {
        name: item.nombre || item.name,  // Convertir 'nombre' a 'name'
        price: item.precio || item.price // Convertir 'precio' a 'price'
    };

    fetch('/add_to_cart', {
        method: 'POST',
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
            domain_name: domainName,  
            item: normalizedItem  
        })
    })
    .then(response => response.json())
    .then(data => console.log("✅ Respuesta del backend:", data))
    .catch(error => console.error("❌ Error en la petición:", error));
}




function removeFromWishList(index) {
    wishList.splice(index, 1);
    updateWishDropdown();
}
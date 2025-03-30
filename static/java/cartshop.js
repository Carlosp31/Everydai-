let wishList = [];  // Usa let para evitar la redeclaración
const wishButton = document.getElementById("wish-button");
const wishDropdown = document.getElementById("wish-dropdown");
const wishItemsList = document.getElementById("wish-items");

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
        deleteButton.textContent = "❌";
        // Botón para mover al inventario
        const moveButton = document.createElement("button");
        moveButton.textContent = "➕ ";
        moveButton.onclick = () => addToInventory(name);

        
        deleteButton.onclick = () => {
            console.log("🛑 Botón clickeado para eliminar:", name); // Verificar si el botón detecta el clic
            removeFromWishList(name);
        };

        listItem.appendChild(deleteButton);
        listItem.appendChild(moveButton);
        wishItemsList.appendChild(listItem);
    });
}


function removeFromWishList(itemName) {
    console.log(`🛑 Intentando eliminar: ${itemName} del dominio: ${domain}`);

    fetch('/remove_from_wish_list', {
        method: 'POST',
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ domain_name: domain, item_name: itemName }) 
    })
    .then(response => response.json())
    .then(data => {
        console.log("✅ Respuesta del backend:", data);
        fetchWishList(); // Recargar la lista después de eliminar
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
    .then(data => {
        console.log("✅ Respuesta del backend:", data);
        fetchWishList(); // Actualizar la lista de deseos
    })
    .catch(error => console.error("❌ Error en la petición:", error));
}

// ✅ Función para agregar un elemento al inventario
function addToInventory(name) {
    fetch('/add_to_inventory_from_wl', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ items: [name] })  // Enviar el nombre del producto como lista
    })
    .then(response => response.json())
    .then(data => {
        console.log("✅ Item agregado al inventario:", data);
        removeFromWishList(name); // Elimina el item de la lista de deseos
    })
    .catch(error => console.error("❌ Error al agregar al inventario:", error));
}



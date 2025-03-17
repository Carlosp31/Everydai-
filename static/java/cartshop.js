const wishList = [];
const wishButton = document.getElementById("wish-button");
const wishDropdown = document.getElementById("wish-dropdown");
const wishItemsList = document.getElementById("wish-items");

// ✅ Función para obtener la lista de deseos del usuario
function fetchWishList() {
    fetch('/get_wish_list')
        .then(response => response.json())
        .then(data => {
            console.log("Respuesta del backend (Wish List):", data); // 👉 Verifica que los datos llegan
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

// ✅ Función para actualizar la UI de la lista de deseos
function updateWishDropdown() {
    wishItemsList.innerHTML = ''; // Limpiar la lista

    // Mostrar nombre y precio de cada item
    wishList.forEach(item => {
        const listItem = document.createElement("li");
        // Asegurarse de que cada item tenga 'name' y 'price'
        const name = item.name || 'Nombre no disponible';
        const price = item.price !== undefined ? `$${item.price.toFixed(2)}` : 'Precio no disponible';

        listItem.textContent = `- ${name} : ${price}`;
        wishItemsList.appendChild(listItem);
    });
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


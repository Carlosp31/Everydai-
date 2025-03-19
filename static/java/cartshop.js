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

function updateWishDropdown() {
    wishItemsList.innerHTML = ''; // Limpiar la lista

    console.log("Lista de deseos actualizada:", wishList); // 🔍 Verificar los elementos

    // Mostrar nombre y precio de cada item
    wishList.forEach(item => {
        const listItem = document.createElement("li");

        // Asegurar que cada item tenga 'name' y 'price'
        const name = item.name || 'Nombre no disponible';

        // Si el precio es string, convertirlo a número sin alterar su precisión original
        let price = item.price;
        if (typeof price === "string") {
            price = parseFloat(price.replace(",", "").replace("$", ""));
        }

        // Mostrar el precio tal cual sin formatear decimales
        const priceText = isNaN(price) ? 'Precio no disponible' : `$${price}`;

        listItem.textContent = `${name} : ${priceText}`;
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




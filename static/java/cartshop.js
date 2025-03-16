const wishList = [];
const wishListButton = document.getElementById("wishlist-button");
const wishListDropdown = document.getElementById("wishlist-dropdown");
const wishListItemsList = document.getElementById("wishlist-items");

// ✅ Función para obtener la wish list cuando se presiona el botón
wishListButton.addEventListener("click", () => {
    if (wishListDropdown.style.display === "none" || wishListDropdown.style.display === "") {
        fetchWishList();
        wishListDropdown.style.display = "block";
    } else {
        wishListDropdown.style.display = "none";
    }
});

// ✅ Función para obtener la wish list del usuario
function fetchWishList() {
    fetch('/get_wish_list')
        .then(response => response.json())
        .then(data => {
            console.log("Respuesta del backend (Wish List):", data);
            if (data.error) {
                console.error("Error al obtener la wish list:", data.error);
                return;
            }
            wishList.length = 0;
            wishList.push(...Object.entries(data.wish_list).map(([name, quantity]) => ({ name, quantity }))); 
            updateWishListDropdown();
        })
        .catch(error => console.error("Error al obtener la wish list:", error));
}

// ✅ Función para actualizar la UI de la wish list
function updateWishListDropdown() {
    wishListItemsList.innerHTML = "";
    wishList.forEach(item => {
        const listItem = document.createElement("li");
        listItem.textContent = `- ${item.name}`;
        wishListItemsList.appendChild(listItem);
    });
}

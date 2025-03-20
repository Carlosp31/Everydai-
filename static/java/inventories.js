const inventory = [];
const inventoryButton = document.getElementById("inventory-button");
const inventoryDropdown = document.getElementById("inventory-dropdown");
const inventoryItemsList = document.getElementById("inventory-items");

// ✅ Función para obtener el inventario cuando se presiona el botón
inventoryButton.addEventListener("click", () => {
    if (inventoryDropdown.style.display === "none" || inventoryDropdown.style.display === "") {
        fetchInventory(); // Solo carga el inventario cuando se presiona el botón
        inventoryDropdown.style.display = "block"; // Muestra el cuadro
    } else {
        inventoryDropdown.style.display = "none"; // Oculta el cuadro si ya está abierto
    }
});

function fetchInventory() {
    fetch('/get_inventory')
        .then(response => response.json())
        .then(data => {
            console.log("Respuesta del backend:", data); // 👉 Verifica que los datos llegan
            if (data.error) {
                console.error("Error al obtener el inventario:", data.error);
                return;
            }

            inventory.length = 0;
            inventory.push(...data.items);  // ✅ Guardar la lista correctamente
            updateInventoryDropdown();
        })
        .catch(error => console.error("Error al obtener inventario:", error));
}

// ✅ Función para actualizar la UI del inventario
function updateInventoryDropdown() {
    inventoryItemsList.innerHTML = ''; // Limpia el contenido antes de actualizar

    // 📌 Agregar el título "Inventories" dentro del cuadro
    const title = document.createElement("h3");
    title.textContent = "Inventory";
    title.style.textAlign = "center";
    inventoryItemsList.appendChild(title);

    if (inventory.length === 0) {
        const emptyMessage = document.createElement("li");
        emptyMessage.textContent = "No hay items en el inventario.";
        emptyMessage.style.color = "gray";
        inventoryItemsList.appendChild(emptyMessage);
        return;
    }

    inventory.forEach(item => {
        const listItem = document.createElement("li");
        listItem.textContent = `- ${item}`; // ✅ Ahora muestra "- NombreDelItem"
        inventoryItemsList.appendChild(listItem);
    });
}
    


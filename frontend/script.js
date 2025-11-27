// 👉 Cambia esta URL por la salida de Terraform (API Gateway endpoint)
const API_BASE = "https://0jdcbjbem9.execute-api.us-east-1.amazonaws.com/dev";

document.getElementById("checkHealth").addEventListener("click", async () => {
    const el = document.getElementById("healthStatus");
    el.innerText = "Consultando...";

    try {
        const res = await fetch(`${API_BASE}/health`);
        const data = await res.json();
        el.innerText = JSON.stringify(data);
    } catch (e) {
        el.innerText = "Error consultando el backend";
    }
});


async function loadItems() {
    const list = document.getElementById("itemList");
    list.innerHTML = "<li>Cargando...</li>";

    try {
        const res = await fetch(`${API_BASE}/items`);
        const data = await res.json();

        if (!data.items || data.items.length === 0) {
            list.innerHTML = "<li>No hay items</li>";
            return;
        }

        list.innerHTML = "";
        data.items.forEach(item => {
            const li = document.createElement("li");
            li.innerText = `${item.name} – $${item.price}`;
            list.appendChild(li);
        });

    } catch (e) {
        list.innerHTML = "<li>Error cargando items</li>";
    }
}

document.getElementById("itemForm").addEventListener("submit", async (e) => {
    e.preventDefault();

    const name = document.getElementById("name").value;
    const price = document.getElementById("price").value;

    try {
        await fetch(`${API_BASE}/items`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name, price })
        });

        loadItems(); // refrescar lista
        e.target.reset();

    } catch (e) {
        alert("Error creando item");
    }
});

// Cargar lista inicial
loadItems();

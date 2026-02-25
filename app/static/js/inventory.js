const token = localStorage.getItem("token");
if (!token) window.location.href = "/";

const auth = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };
const form = document.getElementById("product-form");
const tbody = document.querySelector("#products-table tbody");
const search = document.getElementById("search");

async function loadProducts(keyword = "") {
  const res = await fetch(`/api/products?search=${encodeURIComponent(keyword)}`, { headers: auth });
  const rows = await res.json();
  tbody.innerHTML = "";
  rows.forEach((p) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${p.barcode}</td><td>${p.name}</td><td>${p.cost_price}</td><td>${p.selling_price}</td><td>${p.stock_qty}</td>
      <td><button data-del="${p.id}">Delete</button></td>`;
    tbody.appendChild(tr);
  });
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const payload = Object.fromEntries(new FormData(form).entries());
  payload.cost_price = Number(payload.cost_price);
  payload.selling_price = Number(payload.selling_price);
  payload.stock_qty = Number(payload.stock_qty);

  const res = await fetch("/api/products", { method: "POST", headers: auth, body: JSON.stringify(payload) });
  if (!res.ok) return alert("Cannot save product");
  form.reset();
  loadProducts(search.value);
});

search.addEventListener("input", () => loadProducts(search.value));

tbody.addEventListener("click", async (e) => {
  const id = e.target.dataset.del;
  if (!id) return;
  if (!confirm("Delete this product?")) return;
  await fetch(`/api/products/${id}`, { method: "DELETE", headers: auth });
  loadProducts(search.value);
});

loadProducts();

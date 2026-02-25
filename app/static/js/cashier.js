const token = localStorage.getItem("token");
if (!token) window.location.href = "/";

const auth = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };
const cart = [];
let lastTransactionId = null;

const barcodeInput = document.getElementById("barcode-input");
const tbody = document.querySelector("#cart-table tbody");
const totalEl = document.getElementById("total");
const paymentEl = document.getElementById("payment");
const changeEl = document.getElementById("change");
const receiptEl = document.getElementById("receipt");

function money(v) { return Number(v).toFixed(2); }

function recalc() {
  const total = cart.reduce((sum, row) => sum + row.qty * Number(row.selling_price), 0);
  totalEl.textContent = money(total);
  const payment = Number(paymentEl.value || 0);
  changeEl.textContent = money(payment - total);
}

function renderCart() {
  tbody.innerHTML = "";
  cart.forEach((row, idx) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${row.name}</td>
      <td><input type="number" min="1" value="${row.qty}" data-idx="${idx}" class="qty-input"/></td>
      <td>${money(row.selling_price)}</td>
      <td>${money(row.qty * Number(row.selling_price))}</td>
      <td><button data-rm="${idx}">x</button></td>`;
    tbody.appendChild(tr);
  });
  recalc();
}

async function addByBarcode() {
  const barcode = barcodeInput.value.trim();
  if (!barcode) return;

  const res = await fetch(`/api/products/barcode/${encodeURIComponent(barcode)}`, { headers: auth });
  if (!res.ok) {
    alert("Barcode not found");
    return;
  }
  const product = await res.json();
  const existing = cart.find((i) => i.product_id === product.id);
  if (existing) existing.qty += 1;
  else cart.push({ product_id: product.id, name: product.name, qty: 1, selling_price: product.selling_price });
  barcodeInput.value = "";
  renderCart();
}

document.getElementById("add-barcode").addEventListener("click", addByBarcode);
barcodeInput.addEventListener("keydown", (e) => { if (e.key === "Enter") addByBarcode(); });
paymentEl.addEventListener("input", recalc);
document.addEventListener("keydown", (e) => { if (e.ctrlKey && e.key === "Enter") document.getElementById("checkout").click(); });

tbody.addEventListener("input", (e) => {
  if (!e.target.classList.contains("qty-input")) return;
  cart[Number(e.target.dataset.idx)].qty = Number(e.target.value || 1);
  renderCart();
});

tbody.addEventListener("click", (e) => {
  const idx = e.target.dataset.rm;
  if (idx === undefined) return;
  cart.splice(Number(idx), 1);
  renderCart();
});

document.getElementById("checkout").addEventListener("click", async () => {
  const payload = {
    items: cart.map((item) => ({ product_id: item.product_id, qty: item.qty })),
    payment_amount: Number(paymentEl.value || 0),
  };

  const res = await fetch("/api/transactions", { method: "POST", headers: auth, body: JSON.stringify(payload) });
  const data = await res.json();
  if (!res.ok) return alert(data.detail || "Checkout failed");

  lastTransactionId = data.id;
  const lines = [
    window.POS_STORE_NAME,
    `Invoice: ${data.invoice_no}`,
    `Date: ${new Date(data.created_at).toLocaleString()}`,
    "-------------------------",
    ...data.items.map((i) => `${i.name} x${i.qty} @ ${money(i.price)} = ${money(i.subtotal)}`),
    "-------------------------",
    `Total: ${money(data.total_amount)}`,
    `Payment: ${money(data.payment_amount)}`,
    `Change: ${money(data.change_amount)}`,
  ];
  receiptEl.textContent = lines.join("\n");
  cart.length = 0;
  renderCart();
  paymentEl.value = "";
});

document.getElementById("print-receipt").addEventListener("click", () => window.print());

document.getElementById("print-thermal").addEventListener("click", async () => {
  if (!lastTransactionId) {
    alert("Complete a transaction first");
    return;
  }

  const res = await fetch(`/api/transactions/${lastTransactionId}/print`, { method: "POST", headers: auth });
  const data = await res.json();
  if (!res.ok) {
    alert(data.detail || "Thermal print failed");
    return;
  }
  alert(data.message || "Sent to thermal printer");
});

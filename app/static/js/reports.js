const token = localStorage.getItem("token");
if (!token) window.location.href = "/";

const auth = { Authorization: `Bearer ${token}` };
const periodEl = document.getElementById("period");
const tbody = document.querySelector("#report-table tbody");

function money(v) { return Number(v).toFixed(2); }

async function loadReport() {
  const period = periodEl.value;
  const [summaryRes, breakdownRes] = await Promise.all([
    fetch(`/api/reports/summary?period=${period}`, { headers: auth }),
    fetch(`/api/reports/breakdown?period=${period}`, { headers: auth }),
  ]);

  if (!summaryRes.ok || !breakdownRes.ok) {
    alert("Failed to load report (admin role required)");
    return;
  }

  const summary = await summaryRes.json();
  const breakdown = await breakdownRes.json();

  document.getElementById("sum-tx").textContent = summary.total_transactions;
  document.getElementById("sum-rev").textContent = money(summary.total_revenue);
  document.getElementById("sum-cost").textContent = money(summary.total_cost);
  document.getElementById("sum-profit").textContent = money(summary.gross_profit);

  tbody.innerHTML = "";
  breakdown.rows.forEach((row) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${row.bucket}</td><td>${row.transactions}</td><td>${money(row.revenue)}</td><td>${money(row.cost)}</td><td>${money(row.profit)}</td>`;
    tbody.appendChild(tr);
  });
}

document.getElementById("load-report").addEventListener("click", loadReport);
loadReport();

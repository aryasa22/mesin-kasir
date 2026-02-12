const form = document.getElementById("login-form");
const msg = document.getElementById("msg");

form?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const data = Object.fromEntries(new FormData(form).entries());

  const res = await fetch("/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });

  if (!res.ok) {
    msg.textContent = "Login failed";
    return;
  }

  const payload = await res.json();
  localStorage.setItem("token", payload.access_token);
  localStorage.setItem("role", payload.role);
  window.location.href = "/cashier";
});

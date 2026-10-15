async function checkHealth() {
  const el = document.getElementById("service-status");
  try {
    const res = await fetch("/health");
    const data = await res.json();
    el.textContent = `сервіс працює, версія ${data.version}`;
    el.className = "status ok";
  } catch (err) {
    el.textContent = "сервіс недоступний";
    el.className = "status fail";
  }
}

checkHealth();

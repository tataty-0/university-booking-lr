const ERROR_TEXT = {
  FORBIDDEN: "Лише адміністратор може приймати рішення",
  INVALID_TRANSITION: "Рішення вже прийнято або запит скасовано",
  NOT_FOUND: "Запит не знайдено",
  UNAUTHORIZED: "Потрібно вибрати користувача",
  INTERNAL_ERROR: "Технічна помилка сервісу, спробуйте пізніше",
};

const $ = (id) => document.getElementById(id);

function showMessage(text, kind) {
  const el = $("message");
  el.textContent = text;
  el.className = kind;
  el.hidden = false;
}

async function api(path, options = {}) {
  const res = await fetch(path, {
    ...options,
    headers: { "X-User-Id": $("user").value, ...(options.headers || {}) },
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    const code = body.error ? body.error.code : "INTERNAL_ERROR";
    throw new Error(ERROR_TEXT[code] || (body.error && body.error.message) || "Помилка");
  }
  return body;
}

const fmt = (iso) => new Date(iso).toLocaleString("uk-UA", { dateStyle: "short", timeStyle: "short" });

async function decide(id, action) {
  try {
    const result = await api(`/api/admin/bookings/${id}/${action}`, { method: "POST" });
    showMessage(`Запит №${id}: ${result.status}`, "ok");
  } catch (err) {
    showMessage(err.message, "error");
  }
  load();
}

async function load() {
  const tbody = $("pending").querySelector("tbody");
  tbody.innerHTML = "";
  let items = [];
  try {
    items = await api("/api/admin/bookings/pending");
  } catch (err) {
    showMessage(err.message, "error");
  }
  $("empty").hidden = items.length > 0;
  for (const b of items) {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${b.id}</td><td>${b.applicant}</td><td>${b.room_name} (${b.room_capacity})</td>` +
      `<td>${fmt(b.start)}</td><td>${fmt(b.end)}</td>` +
      `<td><span class="badge ${b.status}">${b.status}</span></td><td></td>`;
    const approve = document.createElement("button");
    approve.textContent = "Підтвердити";
    approve.addEventListener("click", () => decide(b.id, "approve"));
    const reject = document.createElement("button");
    reject.textContent = "Відхилити";
    reject.className = "danger";
    reject.addEventListener("click", () => decide(b.id, "reject"));
    tr.lastElementChild.append(approve, " ", reject);
    tbody.appendChild(tr);
  }
}

$("user").addEventListener("change", load);
load();

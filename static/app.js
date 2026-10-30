const ERROR_TEXT = {
  INVALID_INTERVAL: "Некоректний інтервал: початок має бути раніше за кінець",
  SLOT_CONFLICT: "Аудиторія вже заброньована на цей час",
  FORBIDDEN: "Ця дія недоступна для вашого користувача",
  NOT_FOUND: "Об'єкт не знайдено",
  UNAUTHORIZED: "Потрібно вибрати користувача",
  INVALID_TRANSITION: "Ця дія вже неможлива для поточного стану бронювання",
  VALIDATION_ERROR: "Перевірте введені дані",
  INTERNAL_ERROR: "Технічна помилка сервісу, спробуйте пізніше",
};

const $ = (id) => document.getElementById(id);
let rooms = [];

function userId() {
  return $("user").value;
}

function showMessage(text, kind) {
  const el = $("message");
  el.textContent = text;
  el.className = kind;
  el.hidden = false;
}

async function api(path, options = {}) {
  const res = await fetch(path, {
    ...options,
    headers: { "Content-Type": "application/json", "X-User-Id": userId(), ...(options.headers || {}) },
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    const code = body.error ? body.error.code : "INTERNAL_ERROR";
    const err = new Error(ERROR_TEXT[code] || (body.error && body.error.message) || "Помилка");
    err.code = code;
    throw err;
  }
  return body;
}

function fmt(iso) {
  return new Date(iso).toLocaleString("uk-UA", { dateStyle: "short", timeStyle: "short" });
}

function toUtcIso(localValue) {
  return new Date(localValue).toISOString();
}

async function checkHealth() {
  const el = $("service-status");
  try {
    const data = await (await fetch("/health")).json();
    el.textContent = `сервіс працює, версія ${data.version}`;
    el.className = "status ok";
  } catch (err) {
    el.textContent = "сервіс недоступний";
    el.className = "status fail";
  }
}

async function loadRooms() {
  rooms = await api("/api/rooms");
  const tbody = $("rooms").querySelector("tbody");
  tbody.innerHTML = "";
  $("room").innerHTML = "";
  for (const room of rooms) {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${room.name}</td><td>${room.capacity}</td><td></td>`;
    tbody.appendChild(tr);
    const option = document.createElement("option");
    option.value = room.id;
    option.textContent = `${room.name} (${room.capacity})`;
    $("room").appendChild(option);
  }
}

async function loadMyBookings() {
  const tbody = $("my-bookings").querySelector("tbody");
  tbody.innerHTML = "";
  let bookings = [];
  try {
    bookings = await api("/api/bookings/my");
  } catch (err) {
    showMessage(err.message, "error");
    return;
  }
  const names = Object.fromEntries(rooms.map((r) => [r.id, r.name]));
  for (const b of bookings) {
    const tr = document.createElement("tr");
    const cancellable = b.status === "ACTIVE" || b.status === "PENDING";
    tr.innerHTML = `<td>${b.id}</td><td>${names[b.room_id] || b.room_id}</td>` +
      `<td>${fmt(b.start)}</td><td>${fmt(b.end)}</td>` +
      `<td><span class="badge ${b.status}">${b.status}</span></td><td></td>`;
    if (cancellable) {
      const button = document.createElement("button");
      button.textContent = "Скасувати";
      button.className = "danger";
      button.addEventListener("click", () => cancel(b.id));
      tr.lastElementChild.appendChild(button);
    }
    tbody.appendChild(tr);
  }
}

async function cancel(id) {
  try {
    await api(`/api/bookings/${id}/cancel`, { method: "POST" });
    showMessage("Бронювання скасовано", "ok");
  } catch (err) {
    showMessage(err.message, "error");
  }
  loadMyBookings();
}

function intervalQuery() {
  return `start=${encodeURIComponent(toUtcIso($("start").value))}&end=${encodeURIComponent(toUtcIso($("end").value))}`;
}

$("check").addEventListener("click", async () => {
  try {
    const data = await api(`/api/rooms/${$("room").value}/availability?${intervalQuery()}`);
    showMessage(data.available ? "Аудиторія вільна" : "Аудиторія зайнята на цей час", data.available ? "ok" : "error");
  } catch (err) {
    showMessage(err.message, "error");
  }
});

$("booking-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const body = {
      room_id: Number($("room").value),
      start: toUtcIso($("start").value),
      end: toUtcIso($("end").value),
    };
    const created = await api("/api/bookings", { method: "POST", body: JSON.stringify(body) });
    const note = created.status === "PENDING" ? " — очікує підтвердження адміністратора" : "";
    showMessage(`Бронювання №${created.id} створено, статус ${created.status}${note}`, "ok");
  } catch (err) {
    showMessage(err.message, "error");
  }
  loadMyBookings();
});

$("user").addEventListener("change", loadMyBookings);

(async function init() {
  checkHealth();
  try {
    await loadRooms();
  } catch (err) {
    showMessage(err.message, "error");
  }
  loadMyBookings();
})();

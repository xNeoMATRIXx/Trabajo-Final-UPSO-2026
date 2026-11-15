/* main.js — todo el frontend en JS puro, sin build. Sirve para index.html y public.html. */

/* API helper — fetch wrapper con token y manejo de errores. */
(function (global) {
  "use strict";

  // Cambiá esta constante si el backend corre en otro host/puerto.
  const isLocal = ["localhost", "127.0.0.1", ""].includes(location.hostname) || location.protocol === "file:";
  const DEFAULT_URL = isLocal ? "http://localhost:5000" : location.origin + "/api";
  const BASE_URL = (localStorage.getItem("API_BASE_URL") || DEFAULT_URL).replace(/\/$/, "");

  function getToken() { return localStorage.getItem("token"); }
  function setToken(t) { localStorage.setItem("token", t); }
  function clearToken() { localStorage.removeItem("token"); localStorage.removeItem("user"); }
  function getUser() { try { return JSON.parse(localStorage.getItem("user") || "null"); } catch (e) { return null; } }
  function setUser(u) { localStorage.setItem("user", JSON.stringify(u)); }

  async function request(path, { method = "GET", body, auth = true, headers } = {}) {
    const h = Object.assign({ "Content-Type": "application/json" }, headers || {});
    if (auth && getToken()) h["Authorization"] = "Bearer " + getToken();

    const res = await fetch(BASE_URL + path, {
      method,
      headers: h,
      body: body ? JSON.stringify(body) : undefined,
    });

    const text = await res.text();
    let data; try { data = text ? JSON.parse(text) : null; } catch (e) { data = { raw: text }; }
    if (!res.ok) {
      const err = new Error((data && (data.error || data.mensaje)) || ("HTTP " + res.status));
      err.status = res.status;
      err.payload = data;
      throw err;
    }
    return data;
  }

  global.API = {
    BASE_URL,
    getToken, setToken, clearToken,
    getUser, setUser,
    get:    (p, opts) => request(p, Object.assign({ method: "GET" }, opts || {})),
    post:   (p, body, opts) => request(p, Object.assign({ method: "POST", body }, opts || {})),
    put:    (p, body, opts) => request(p, Object.assign({ method: "PUT", body }, opts || {})),
    del:    (p, opts) => request(p, Object.assign({ method: "DELETE" }, opts || {})),
  };

  // Toast helper
  global.toast = function (msg, kind) {
    const el = document.getElementById("toast");
    if (!el) return alert(msg);
    el.textContent = msg;
    el.className = "toast " + (kind || "");
    el.classList.remove("hidden");
    clearTimeout(global.__toastTimer);
    global.__toastTimer = setTimeout(() => el.classList.add("hidden"), 2800);
  };
})(window);


/* Autenticación: tabs, login, register, logout, delete account. */
(function () {
  "use strict";
  if (!document.getElementById("view-panel")) return;

  const viewAuth = document.getElementById("view-auth");
  const viewPanel = document.getElementById("view-panel");
  const userChip = document.getElementById("user-chip");
  const btnLogout = document.getElementById("btn-logout");
  const btnDeleteAccount = document.getElementById("btn-delete-account");

  const tabs = document.querySelectorAll(".auth-tabs .tab");
  const formLogin = document.getElementById("form-login");
  const formRegister = document.getElementById("form-register");
  const authMsg = document.getElementById("auth-msg");

  function setMsg(text, kind) {
    authMsg.textContent = text || "";
    authMsg.className = "form-msg " + (kind || "");
  }

  tabs.forEach((t) => t.addEventListener("click", () => {
    tabs.forEach(x => x.classList.toggle("active", x === t));
    const which = t.dataset.tab;
    formLogin.classList.toggle("hidden", which !== "login");
    formRegister.classList.toggle("hidden", which !== "register");
    setMsg("");
  }));

  formLogin.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(formLogin);
    setMsg("Iniciando sesión...", "");
    try {
      const data = await window.API.post("/auth/login", {
        email: fd.get("email"),
        password: fd.get("password"),
      }, { auth: false });
      window.API.setToken(data.token);
      window.API.setUser(data.user);
      showPanel();
    } catch (err) {
      setMsg(traducirError(err), "error");
    }
  });

  formRegister.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(formRegister);
    setMsg("Creando cuenta...", "");
    try {
      const data = await window.API.post("/auth/register", {
        email: fd.get("email"),
        username: fd.get("username"),
        password: fd.get("password"),
        nombre: fd.get("nombre") || null,
        bio: fd.get("bio") || null,
      }, { auth: false });
      window.API.setToken(data.token);
      window.API.setUser(data.user);
      showPanel();
    } catch (err) {
      setMsg(traducirError(err), "error");
    }
  });

  btnLogout.addEventListener("click", () => {
    window.API.clearToken();
    showAuth();
  });

  btnDeleteAccount.addEventListener("click", async () => {
    if (!confirm("¿Seguro que querés eliminar tu cuenta? Esta acción es irreversible.")) return;
    try {
      await window.API.del("/auth/me");
      window.toast("Cuenta eliminada", "ok");
      window.API.clearToken();
      showAuth();
    } catch (err) {
      window.toast("Error: " + err.message, "error");
    }
  });

  function traducirError(err) {
    const m = (err.payload && (err.payload.error || err.payload.mensaje)) || err.message;
    const map = {
      email_invalido: "El email no es válido.",
      username_invalido: "Username inválido (3-30 caracteres, letras/números/_/-).",
      password_invalido: "La contraseña debe tener al menos 6 caracteres.",
      email_ya_registrado: "Ese email ya está registrado.",
      username_ya_usado: "Ese username ya está en uso.",
      credenciales_invalidas: "Email o contraseña incorrectos.",
      token_expired: "Tu sesión expiró, ingresá otra vez.",
    };
    return map[m] || m;
  }

  function showPanel() {
    viewAuth.classList.add("hidden");
    viewPanel.classList.remove("hidden");
    const u = window.API.getUser();
    userChip.textContent = "@" + u.username;
    userChip.classList.remove("hidden");
    btnLogout.classList.remove("hidden");
    document.getElementById("panel-username").textContent = (u.nombre || u.username);
    document.getElementById("panel-email").textContent = u.email;
    const link = document.getElementById("panel-public-link");
    link.href = "public.html?u=" + encodeURIComponent(u.username);
    // Inicializar secciones.
    window.Skills.init();
    window.Projects.init();
  }

  function showAuth() {
    viewPanel.classList.add("hidden");
    viewAuth.classList.remove("hidden");
    userChip.classList.add("hidden");
    btnLogout.classList.add("hidden");
    setMsg("");
    formLogin.reset();
    formRegister.reset();
  }

  // Auto-login si hay token guardado.
  window.addEventListener("DOMContentLoaded", async () => {
    if (!window.API.getToken()) return;
    try {
      const data = await window.API.get("/auth/me");
      window.API.setUser(data.user);
      showPanel();
    } catch (e) {
      window.API.clearToken();
    }
  });

  window.Auth = { showAuth, showPanel };
})();


/* Gestión de habilidades: agregar, cambiar nivel, eliminar. */
(function () {
  "use strict";
  if (!document.getElementById("view-panel")) return;

  const selector = document.getElementById("sel-habilidad");
  const formSkill = document.getElementById("form-skill");
  const list = document.getElementById("list-skills");
  const addButton = formSkill.querySelector('button[type="submit"]');

  const NIVELES = ["basico", "intermedio", "avanzado"];
  let tecnologias = [];
  let habilidades = [];
  let lenguajes = [];

  function key(h) {
    return h.tipo + ":" + h.elemento_id;
  }

  function path(h) {
    return "/habilidades/" + h.tipo + "/" + h.elemento_id;
  }

  async function init() {
    try {
      [lenguajes, tecnologias, habilidades] = await Promise.all([
        window.API.get("/lenguajes", { auth: false }),
        window.API.get("/tecnologias", { auth: false }),
        window.API.get("/habilidades"),
      ]);
      render();
    } catch (err) {
      selector.replaceChildren();
      addButton.disabled = true;
      list.textContent = "No se pudieron cargar las habilidades.";
      window.toast(err.message, "error");
    }
  }

  function render() {
    const used = new Set(habilidades.map(key));
    selector.replaceChildren();
    for (const [tipo, label, items] of [
      ["lenguaje", "Lenguajes", lenguajes],
      ["tecnologia", "Tecnologías", tecnologias],
    ]) {
      const group = document.createElement("optgroup");
      group.label = label;
      for (const item of items) {
        const value = tipo + ":" + item.id;
        if (!used.has(value)) group.appendChild(new Option(item.nombre, value));
      }
      if (group.children.length) selector.appendChild(group);
    }
    addButton.disabled = selector.options.length === 0;
    list.replaceChildren();
    if (!habilidades.length) {
      list.textContent = "Aún no agregaste habilidades.";
      return;
    }
    for (const h of habilidades) {
      const li = document.createElement("li");
      li.className = "skill-chip";
      const name = document.createElement("span");
      name.textContent = (h.tipo === "lenguaje" ? "Lenguaje: " : "Tecnología: ") + h.nombre;
      const level = document.createElement("select");
      level.setAttribute("aria-label", "Nivel de " + h.nombre);
      for (const value of NIVELES) level.appendChild(new Option(value, value));
      level.value = h.nivel;
      const remove = document.createElement("button");
      remove.type = "button";
      remove.className = "remove";
      remove.textContent = "×";
      remove.setAttribute("aria-label", "Eliminar " + h.nombre);
      li.append(name, level, remove);
      list.appendChild(li);

      level.addEventListener("change", async () => {
        const previous = h.nivel;
        level.disabled = true;
        try {
          const updated = await window.API.put(path(h), { nivel: level.value });
          h.nivel = updated.nivel;
          window.toast("Nivel actualizado", "ok");
        } catch (err) {
          level.value = previous;
          window.toast(err.message, "error");
        } finally {
          level.disabled = false;
        }
      });
      remove.addEventListener("click", async () => {
        if (!confirm("¿Eliminar esta habilidad?")) return;
        remove.disabled = true;
        try {
          await window.API.del(path(h));
          habilidades = habilidades.filter(item => key(item) !== key(h));
          render();
          window.toast("Habilidad eliminada", "ok");
        } catch (err) {
          remove.disabled = false;
          window.toast(err.message, "error");
        }
      });
    }
  }

  formSkill.addEventListener("submit", async (e) => {
    e.preventDefault();
    const [tipo, rawId] = selector.value.split(":");
    const elementId = Number(rawId);
    if (!["lenguaje", "tecnologia"].includes(tipo) || !Number.isInteger(elementId) || elementId <= 0) return;
    addButton.disabled = true;
    try {
      const nueva = await window.API.post("/habilidades", {
        tipo, elemento_id: elementId, nivel: new FormData(formSkill).get("nivel"),
      });
      habilidades.push(nueva);
      render();
      window.toast("Habilidad agregada", "ok");
    } catch (err) {
      window.toast(err.message, "error");
    } finally {
      addButton.disabled = selector.options.length === 0;
    }
  });

  window.Skills = { init };
})();


/* Gestión de proyectos: listado, crear, editar, eliminar. */
(function () {
  "use strict";
  if (!document.getElementById("view-panel")) return;

  const listEl = document.getElementById("list-projects");
  const modal = document.getElementById("modal-project");
  const form = document.getElementById("form-project");
  const btnNew = document.getElementById("btn-new-project");
  const btnClose = document.getElementById("modal-close");
  const btnDelete = document.getElementById("btn-delete-project");
  const btnAddLink = document.getElementById("btn-add-link");
  const listLinks = document.getElementById("list-links");
  const chkLenguajes = document.getElementById("chk-lenguajes");
  const chkTec = document.getElementById("chk-tecnologias");
  const modalTitle = document.getElementById("modal-title");
  const msg = document.getElementById("project-msg");

  const ETAPAS = {
    formulacion: "Formulación", modelado: "Modelado",
    implementacion: "Implementación", testing: "Testing",
    produccion: "Producción", mantenimiento: "Mantenimiento",
  };
  const TIPOS = ["repositorio", "demo", "documentacion", "video", "otro"];

  let proyectos = [];
  let lenguajesCat = [];
  let tecnologiasCat = [];

  async function init() {
    await Promise.all([loadCatalogos(), loadProyectos()]);
    renderList();
  }

  async function loadCatalogos() {
    [lenguajesCat, tecnologiasCat] = await Promise.all([
      window.API.get("/lenguajes", { auth: false }),
      window.API.get("/tecnologias", { auth: false }),
    ]);
  }

  async function loadProyectos() {
    proyectos = await window.API.get("/proyectos");
  }

  function renderList() {
    listEl.innerHTML = "";
    if (!proyectos.length) {
      listEl.innerHTML = '<div class="empty">Todavía no tenés proyectos. Creá el primero desde "+ Nuevo proyecto".</div>';
      return;
    }
    proyectos.forEach(p => {
      const card = document.createElement("div");
      card.className = "project-card";
      card.innerHTML = `
        <span class="project-stage">${ETAPAS[p.etapa] || p.etapa}</span>
        <h3>${escapeHtml(p.nombre)}</h3>
        <p class="muted small">${p.descripcion ? escapeHtml(p.descripcion).slice(0, 110) + (p.descripcion.length > 110 ? "…" : "") : "Sin descripción"}</p>
        <div class="project-tags">
          ${p.lenguajes.map(l => `<span class="tag">${escapeHtml(l.nombre)}</span>`).join("")}
          ${p.tecnologias.map(t => `<span class="tag">${escapeHtml(t.nombre)}</span>`).join("")}
        </div>
      `;
      card.addEventListener("click", () => openModal(p));
      listEl.appendChild(card);
    });
  }

  function openModal(proyecto) {
    msg.textContent = "";
    form.reset();
    listLinks.innerHTML = "";
    renderCheckboxes(chkLenguajes, "lenguaje", lenguajesCat, proyecto ? proyecto.lenguajes.map(x => x.id) : []);
    renderCheckboxes(chkTec, "tecnologia", tecnologiasCat, proyecto ? proyecto.tecnologias.map(x => x.id) : []);

    if (proyecto) {
      modalTitle.textContent = "Editar proyecto";
      form.id.value = proyecto.id;
      form.nombre.value = proyecto.nombre;
      form.descripcion.value = proyecto.descripcion || "";
      form.etapa.value = proyecto.etapa;
      form.fecha_deadline.value = (proyecto.fecha_deadline || "").slice(0, 10);
      form.fecha_finalizacion.value = (proyecto.fecha_finalizacion || "").slice(0, 10);
      proyecto.links.forEach(l => addLinkRow(l.tipo, l.url));
      btnDelete.classList.remove("hidden");
    } else {
      modalTitle.textContent = "Nuevo proyecto";
      form.id.value = "";
      btnDelete.classList.add("hidden");
      addLinkRow();
    }
    modal.classList.remove("hidden");
  }

  function closeModal() { modal.classList.add("hidden"); }

  function renderCheckboxes(container, name, items, selectedIds) {
    container.innerHTML = items.map(it => `
      <label><input type="checkbox" name="${name}" value="${it.id}"
        ${selectedIds.includes(it.id) ? "checked" : ""}/> ${it.nombre}</label>
    `).join("");
  }

  function addLinkRow(tipo, url) {
    const row = document.createElement("div");
    row.className = "link-row";
    row.innerHTML = `
      <select class="link-tipo">
        ${TIPOS.map(t => `<option value="${t}" ${t===tipo?"selected":""}>${t}</option>`).join("")}
      </select>
      <input class="link-url" type="url" placeholder="https://..." value="${url ? escapeAttr(url) : ""}" />
      <button type="button" class="icon-btn" aria-label="Quitar">×</button>
    `;
    row.querySelector(".icon-btn").addEventListener("click", () => row.remove());
    listLinks.appendChild(row);
  }

  function collectLinks() {
    return Array.from(listLinks.querySelectorAll(".link-row"))
      .map(r => ({
        tipo: r.querySelector(".link-tipo").value,
        url: r.querySelector(".link-url").value.trim(),
      }))
      .filter(l => l.url);
  }

  function collectChecked(container) {
    return Array.from(container.querySelectorAll("input:checked"))
      .map(i => parseInt(i.value, 10));
  }

  btnNew.addEventListener("click", () => openModal(null));
  btnClose.addEventListener("click", closeModal);
  btnAddLink.addEventListener("click", () => addLinkRow());
  modal.addEventListener("click", (e) => { if (e.target === modal) closeModal(); });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const id = form.id.value;
    const payload = {
      nombre: form.nombre.value.trim(),
      descripcion: form.descripcion.value.trim() || null,
      etapa: form.etapa.value,
      fecha_deadline: form.fecha_deadline.value || null,
      fecha_finalizacion: form.fecha_finalizacion.value || null,
      lenguajes: collectChecked(chkLenguajes),
      tecnologias: collectChecked(chkTec),
      links: collectLinks(),
    };
    if (payload.lenguajes.length === 0) {
      msg.textContent = "Seleccioná al menos un lenguaje para el proyecto.";
      msg.className = "form-msg error";
      return;
    }

    if (payload.tecnologias.length === 0) {
      msg.textContent = "Seleccioná al menos una tecnología para el proyecto.";
      msg.className = "form-msg error";
      return;
    }
    msg.textContent = "Guardando..."; 
    msg.className = "form-msg";
    try {
      if (id) await window.API.put("/proyectos/" + id, payload);
      else await window.API.post("/proyectos", payload);
      await loadProyectos();
      renderList();
      closeModal();
      window.toast(id ? "Proyecto actualizado" : "Proyecto creado", "ok");
    } catch (err) {
      const det = err.payload && err.payload.detalles;
      msg.textContent = det ? (Array.isArray(det) ? det.join(" · ") : typeof det === "object" ? Object.values(det).join(" · ") : String(det)) : err.message;
      msg.className = "form-msg error";
    }
  });

  btnDelete.addEventListener("click", async () => {
    const id = form.id.value;
    if (!id) return;
    if (!confirm("¿Eliminar este proyecto?")) return;
    try {
      await window.API.del("/proyectos/" + id);
      proyectos = proyectos.filter(p => p.id != id);
      renderList();
      closeModal();
      window.toast("Proyecto eliminado", "ok");
    } catch (err) {
      window.toast("Error: " + err.message, "error");
    }
  });

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, c => ({ "&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;" }[c]));
  }
  function escapeAttr(s) { return escapeHtml(s); }

  window.Projects = { init };
})();


/* Vista pública: lee ?u=username o /u/<username> y renderiza portafolio. */
(function () {
  "use strict";
  if (!document.getElementById("public-root")) return;

  const root = document.getElementById("public-root");

  function getUsername() {
    const p = new URLSearchParams(location.search);
    if (p.get("u")) return p.get("u");
    const m = location.pathname.match(/\/u\/([^\/?#]+)/);
    return m ? decodeURIComponent(m[1]) : null;
  }

  const ETAPAS = {
    formulacion: "Formulación", modelado: "Modelado",
    implementacion: "Implementación", testing: "Testing",
    produccion: "Producción", mantenimiento: "Mantenimiento",
  };

  function escapeHtml(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, c =>
      ({ "&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;" }[c]));
  }

  function fmtDate(iso) {
    if (!iso) return "—";
    try { return new Date(iso).toLocaleDateString("es-ES", { year: "numeric", month: "short", day: "numeric" }); }
    catch (e) { return iso; }
  }

  async function run() {
    const username = getUsername();
    if (!username) {
      root.innerHTML = '<div class="not-found"><h2>Usá /u/username o ?u=username</h2></div>';
      return;
    }

    let data;
    try {
      data = await window.API.get("/u/" + encodeURIComponent(username), { auth: false });
    } catch (err) {
      if (err.status === 404) {
        root.innerHTML = `<div class="not-found"><h2>No existe <code>@${escapeHtml(username)}</code></h2>
          <p class="muted">Verificá el nombre de usuario.</p></div>`;
      } else {
        root.innerHTML = `<div class="not-found"><h2>Error al cargar</h2><p class="muted">${escapeHtml(err.message)}</p></div>`;
      }
      return;
    }

    const { perfil, habilidades, proyectos } = data;
    document.title = (perfil.nombre || perfil.username) + " — Portfolio";

    root.innerHTML = `
      <section class="profile-header">
        <div class="avatar-initial">${(perfil.nombre || perfil.username || "?").slice(0,1).toUpperCase()}</div>
        <div class="profile-meta">
          <h1>${escapeHtml(perfil.nombre || perfil.username)}</h1>
          <div class="profile-handle">@${escapeHtml(perfil.username)}</div>
          ${perfil.bio ? `<p class="profile-bio">${escapeHtml(perfil.bio)}</p>` : ""}
        </div>
      </section>

      <section class="section-public">
        <h2>Habilidades</h2>
        ${habilidades.length
          ? `<div class="public-skills">${habilidades.map(h => `
              <span class="public-skill">
                ${escapeHtml(h.nombre)}
                <span class="level ${h.nivel}">${h.nivel}</span>
              </span>`).join("")}</div>`
          : `<p class="muted">Sin habilidades cargadas.</p>`}
      </section>

      <section class="section-public">
        <h2>Proyectos (${proyectos.length})</h2>
        ${proyectos.length
          ? `<div class="public-projects">${proyectos.map(p => renderProject(p)).join("")}</div>`
          : `<p class="muted">Sin proyectos cargados.</p>`}
      </section>
    `;
  }

  function renderProject(p) {
    const links = (p.links || []).map(l => `
      <a class="link-pill" href="${escapeHtml(l.url)}" target="_blank" rel="noopener">
        <span class="link-type">${l.tipo}</span> · ${escapeHtml(l.url.replace(/^https?:\/\//, ""))}
      </a>`).join("");
    const lenguajes = (p.lenguajes || []).map(l => `<span class="tag">${escapeHtml(l.nombre)}</span>`).join("");
    const tecnologias = (p.tecnologias || []).map(t => `<span class="tag">${escapeHtml(t.nombre)}</span>`).join("");

    return `
      <article class="public-project">
        <span class="project-stage">${ETAPAS[p.etapa] || p.etapa}</span>
        <h3>${escapeHtml(p.nombre)}</h3>
        ${p.descripcion ? `<p class="project-desc">${escapeHtml(p.descripcion)}</p>` : ""}

        ${lenguajes ? `<div class="project-section-title">Lenguajes</div><div class="project-tags">${lenguajes}</div>` : ""}
        ${tecnologias ? `<div class="project-section-title">Tecnologías</div><div class="project-tags">${tecnologias}</div>` : ""}

        ${links ? `<div class="project-section-title">Links</div><div class="links-list">${links}</div>` : ""}

        <div class="meta-row">
          <span><strong>Creado:</strong> ${fmtDate(p.fecha_creacion)}</span>
          <span><strong>Actualizado:</strong> ${fmtDate(p.fecha_actualizacion)}</span>
          <span><strong>Deadline:</strong> ${fmtDate(p.fecha_deadline)}</span>
          <span><strong>Finalizado:</strong> ${fmtDate(p.fecha_finalizacion)}</span>
        </div>
      </article>
    `;
  }

  window.addEventListener("DOMContentLoaded", run);
})();
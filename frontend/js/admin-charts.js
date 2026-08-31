// Utilidades compartidas del panel admin: contador animado y gráficas de barras
// hechas con CSS/SVG puro (sin librerías externas).

function animateCounter(el, targetValue, { prefix = "", suffix = "", duration = 900 } = {}) {
  const start = 0;
  const startTime = performance.now();
  function tick(now) {
    const progress = Math.min((now - startTime) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);
    const value = Math.round(start + (targetValue - start) * eased);
    el.textContent = `${prefix}${value.toLocaleString("es-CO")}${suffix}`;
    if (progress < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

const WEEKDAY_LABELS = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"];

function renderSalesBarChart(container, salesByDay) {
  const maxTotal = Math.max(...salesByDay.map((d) => d.total), 1);
  container.innerHTML = salesByDay.map((d) => {
    const date = new Date(`${d.date}T00:00:00`);
    const label = WEEKDAY_LABELS[date.getDay()];
    return `
      <div class="bar-col">
        <span class="bar-value">${d.total > 0 ? formatMoney(d.total) : ""}</span>
        <div class="bar" data-height="${Math.max((d.total / maxTotal) * 100, 2)}"></div>
        <span class="bar-label">${label}</span>
      </div>`;
  }).join("");

  requestAnimationFrame(() => {
    container.querySelectorAll(".bar-col").forEach((col) => {
      const bar = col.querySelector(".bar");
      bar.style.height = `${bar.dataset.height}%`;
      setTimeout(() => col.classList.add("is-in"), 400);
    });
  });
}

function renderTopProductsChart(container, topProducts) {
  if (!topProducts.length) {
    container.innerHTML = '<p style="color:var(--text-secondary);font-size:0.85rem;">Aún no hay ventas registradas.</p>';
    return;
  }
  const maxQty = Math.max(...topProducts.map((p) => p.quantity), 1);
  container.innerHTML = topProducts.map((p) => `
    <div class="hbar-row">
      <span class="hbar-name" title="${p.name}">${p.name}</span>
      <div class="hbar-track"><div class="hbar-fill" data-width="${(p.quantity / maxQty) * 100}"></div></div>
      <span class="hbar-qty">${p.quantity}</span>
    </div>
  `).join("");

  requestAnimationFrame(() => {
    container.querySelectorAll(".hbar-fill").forEach((fill) => {
      fill.style.width = `${fill.dataset.width}%`;
    });
  });
}

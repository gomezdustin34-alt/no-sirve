// Pétalos discretos: detalle de lujo, no una animación infantil.
// Se colocan solo en contenedores marcados [data-petals], en cantidad moderada.
function scatterPetals(container, count = 4) {
  const sizes = [22, 30, 26, 18, 34];
  for (let i = 0; i < count; i++) {
    const petal = document.createElement("img");
    petal.src = "/assets/img/petal.svg";
    petal.alt = "";
    petal.setAttribute("aria-hidden", "true");
    petal.className = "petal";

    const size = sizes[i % sizes.length];
    petal.style.width = `${size}px`;
    petal.style.top = `${8 + Math.random() * 78}%`;
    petal.style.left = `${Math.random() * 92}%`;
    petal.style.setProperty("--r0", `${-10 + Math.random() * 20}deg`);
    petal.style.setProperty("--r1", `${-10 + Math.random() * 20}deg`);
    petal.style.animationDelay = `${Math.random() * 4}s`;
    petal.style.animationDuration = `${8 + Math.random() * 4}s`;

    container.appendChild(petal);
  }
}

function initPetals() {
  document.querySelectorAll("[data-petals]").forEach((container) => {
    const count = Number(container.dataset.petals) || 4;
    scatterPetals(container, count);
  });
}

document.addEventListener("DOMContentLoaded", initPetals);

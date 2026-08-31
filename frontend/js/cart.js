// Carrito en localStorage. El precio mostrado aquí es solo referencial:
// el backend SIEMPRE vuelve a calcular el precio real en /api/orders/price
// y al crear el pedido, así que nunca se confía en lo guardado localmente.
const CART_KEY = "dcf_cart";

const Cart = {
  getLines() {
    try {
      const raw = localStorage.getItem(CART_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch {
      return [];
    }
  },

  saveLines(lines) {
    localStorage.setItem(CART_KEY, JSON.stringify(lines));
    Cart.updateBadge();
  },

  add(line) {
    const lines = Cart.getLines();
    lines.push(line);
    Cart.saveLines(lines);
  },

  removeAt(index) {
    const lines = Cart.getLines();
    lines.splice(index, 1);
    Cart.saveLines(lines);
  },

  updateQuantityAt(index, quantity) {
    const lines = Cart.getLines();
    if (lines[index]) lines[index].quantity = Math.max(1, Math.min(20, quantity));
    Cart.saveLines(lines);
  },

  clear() {
    localStorage.removeItem(CART_KEY);
    Cart.updateBadge();
  },

  count() {
    return Cart.getLines().reduce((sum, l) => sum + l.quantity, 0);
  },

  updateBadge() {
    document.querySelectorAll("[data-cart-count]").forEach((el) => {
      el.textContent = String(Cart.count());
    });
  },
};

document.addEventListener("DOMContentLoaded", () => Cart.updateBadge());

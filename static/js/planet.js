export function initPlanetEvents() {
  const btn = document.getElementById('walk-btn');
  if (!btn) return;

  btn.addEventListener('click', () => {
    console.log('walk');
  });
}
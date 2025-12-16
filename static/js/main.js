document.addEventListener('DOMContentLoaded', () => {
  console.log('main.js loaded');
  init();
});

async function init() {
  if (!window.userState) {
    window.userState = await fetch('/api/user_state').then(r => r.json());
  }

  if (!window.planetTiles) {
    await showLanding();
  } else {
    await showPlanet();
  }

  updateUI();
}

function updateUI() {
  setText('.planet-name', window.userState.planet_name);
  setText('.user-name', window.userState.user_name);
  // setText('.stardust', window.userState.stardust);
  // setText('.days-alive', window.userState.days_alive);
}

function setText(selector, value) {
  document.querySelectorAll(selector).forEach(el => {
    el.textContent = value ?? '';
  });
}




async function showLanding() {
  const html = await fetch('/partial/landing').then(r => r.text());
  document.querySelector('main').innerHTML = html;
  initLandingEvents(); 
}

function initLandingEvents() {
  const btn = document.getElementById('land-btn');
  if (!btn) return;

  btn.addEventListener('click', async () => {
    // 惑星データ取得
    window.planetTiles = await fetch('/planet/tiles').then(r => r.json());

    // 惑星画面へ
    await showPlanet();
    updateUI();
  });
}




async function showPlanet() {
  const html = await fetch('/partial/planet').then(r => r.text());
  document.querySelector('main').innerHTML = html;

  const module = await import('/static/js/planet.js');
  await module.initPlanet();
}



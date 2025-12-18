document.addEventListener('DOMContentLoaded', () => {
  console.log('main.js loaded');
  init();
});

async function init() {
  if (!window.userState) {
    window.userState = await fetch('/api/user_state').then((r) => r.json());
  }

  if (!window.planetData) {
    await showLanding();
  } else {
    await showPlanet();
  }

  updateUI();
}

import { calcSurviveDays as calcAge } from './time.js';

function updateUI() {
  document.querySelectorAll('[data-bind]').forEach((el) => {
    const key = el.dataset.bind;

    if (key === 'user_age') {
      el.textContent = calcAge(window.userState.created_at);
      return;
    }

    if (key === 'planet_age') {
      el.textContent = calcAge(window.planetData.created_at);
      return;
    }

    if (window.userState[key] !== undefined) {
      el.textContent = window.userState[key];
    }
  });
}

async function showLanding() {
  const html = await fetch('/partial/landing').then((r) => r.text());
  document.querySelector('main').innerHTML = html;
  initLandingEvents();
}

function initLandingEvents() {
  document.addEventListener('click', async (e) => {
    const btn = e.target.closest('[data-action="landing"]');
    if (!btn) return;

    // 惑星データ取得
    window.planetData = await fetch('/planet/data').then((r) => r.json());

    // 惑星画面へ
    await showPlanet();
    updateUI();
  });
}

async function showPlanet() {
  const html = await fetch('/partial/planet').then((r) => r.text());
  document.querySelector('main').innerHTML = html;

  const module = await import('/static/js/planet.js');
  await module.initPlanet();
}

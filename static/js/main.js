document.addEventListener('DOMContentLoaded', () => {
  console.log('main.js loaded');
  init();
});

async function init() {
  if (!window.selfData) {
    window.selfData = await fetch('/data/user').then((r) => r.json());
  }

  if (!window.planetData) {
    window.planetData = await fetch('/data/planet').then((r) => r.json());
    await showLanding();
  } else {
    await showPlanet();
  }

  updateUI();
}

import { calcAge as calcAge } from './time.js';

function updateUI() {
  document.querySelectorAll('[data-bind]').forEach((el) => {
    const bind = el.dataset.bind;

    // 特殊計算系は最優先で拾う
    if (bind === 'self_age') {
      el.textContent = calcAge(window.selfData.created_at);
      return;
    }
    if (bind === 'planet_age') {
      el.textContent = calcAge(window.planetData.planet.created_at);
      return;
    }

    // 通常バインド: "user.xxx" / "planet.xxx"
    const [scope, key] = bind.split('.');

    let source = null;
    if (scope === 'self') source = window.selfData;
    if (scope === 'planet') source = window.planetData.planet;
    if (scope === 'here') source = window.hereData;

    if (source && source[key] !== undefined) {
      el.textContent = source[key];
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

    // 惑星画面へ
    await init();
  });
}

async function showPlanet() {
  const html = await fetch('/partial/planet').then((r) => r.text());
  document.querySelector('main').innerHTML = html;

  const module = await import('/static/js/planet.js');
  await module.initPlanet();
}

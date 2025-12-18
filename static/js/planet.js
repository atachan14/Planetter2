export async function initPlanet() {
  initPlanetEvents();
  await renderPlanet();
}
export async function renderPlanet() {
  renderSurround();
  await renderHere();
}

export function initPlanetEvents() {
  document.addEventListener('click', async (e) => {
    if (e.target.dataset.action) {
      await handleAction(e.target.dataset.action);
      return;
    }

    if (e.target.dataset.ui) {
      handleUI(e.target.dataset.ui);
      return;
    }
  });
}

async function handleAction(action) {
  switch (action) {
    case 'walk':
      await onWalk();
      break;
    case 'turn-left':
      await onTurn(-1);
      break;
    case 'turn-right':
      await onTurn(1);
      break;
    case 'post':
      await onPost();
      break;
  }

  await renderPlanet();
}

function handleUI(ui) {
  switch (ui) {
    case 'open-menu':
      openMenu();
      break;
    case 'close-menu':
      closeMenu();
      break;
  }
}

// surround
function rotate(dx, dy, dir) {
  switch (dir) {
    case 0:
      return { dx, dy }; // 上
    case 1:
      return { dx: -dy, dy: dx }; // 右
    case 2:
      return { dx: -dx, dy: -dy }; // 下
    case 3:
      return { dx: dy, dy: -dx }; // 左
    default:
      return { dx, dy };
  }
}

const SURROUND_BASE = {
  7: { dx: -1, dy: -1 },
  8: { dx: 0, dy: -1 },
  9: { dx: 1, dy: -1 },
  4: { dx: -1, dy: 0 },
  6: { dx: 1, dy: 0 },
};

export function renderSurround() {
  const { x: cx, y: cy, direction: dir } = window.userState;
  const objects = window.planetData.objects; // {"x,y": {object:{id,kind,surround_text}}}

  const posList = [7, 8, 9, 4, 6]; // 123は無し、5はhereで描く

  for (const pos of posList) {
    const el = document.querySelector(`[data-pos="${pos}"]`);
    if (!el) continue;

    el.textContent = '';

    const base = SURROUND_BASE[pos];
    const off = rotate(base.dx, base.dy, dir);

    const tx = cx + off.dx;
    const ty = cy + off.dy;
    const key = `${tx},${ty}`;

    const obj = objects[key]?.object ?? null;

    if (!obj) {
      el.classList.add('none');
      el.textContent = 'none';
      continue;
    }

    // kindをclassに入れる
    el.classList.add(obj.kind ?? 'none');

    // surround_textは「表示するだけ」
    const st = obj.surround_text;

    el.textContent = st ?? 'none';

  }
}

// here
export async function renderHere() {
  const { x, y } = window.userState;
  const key = `${x},${y}`;
  const obj = window.planetData.objects[key]?.object ?? null;

  if (!obj || obj.kind === "none") {
    const html = await fetch('/partial/here/none').then((r) => r.text());
    document.querySelector(`[data-pos="5"]`).innerHTML = html;
    return;
  }

  if (obj.kind === "post") {
    const html = await fetch('/partial/here/post').then((r) => r.text());
    document.querySelector(`[data-pos="5"]`).innerHTML = html;
    return;
  }

  // 将来用（shelf / book など）
  const here = await fetch("/planet/here").then(r => r.json());
  renderHereByKind(here);
}

/* 
========== action =========
*/

async function onWalk() {
  const res = await fetch('/planet/walk', {
    method: 'POST',
  });

  const data = await res.json();
  window.userState = data.surroundings;

  console.log('walk result', data);
}

async function onTurn(turn) {
  const form = new URLSearchParams();
  form.append('turn', turn);

  const res = await fetch('/planet/turn', {
    method: 'POST',
    body: form,
  });
  const data = await res.json();

  window.planetData = data.surroundings;

  console.log('turn result', data);
  // TODO: 周囲UI更新
}

async function onPost() {
  const res = await fetch('/planet/post', {
    method: 'POST',
  });

  const data = await res.json();
  window.planetData = data.surroundings;

  console.log('walk result', data);
}

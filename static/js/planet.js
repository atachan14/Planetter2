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
    case 'post-to-tile':
      await onPostToTile();
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
  const { x: cx, y: cy, direction: dir } = window.selfData;
  const tiles = window.planetData.tiles; // {"x,y": {object:{id,kind,content}}}

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

    const obj = tiles[key] ?? null;

    el.classList.add(obj?.kind ?? 'none');
    el.textContent = obj?.content ?? 'none';
  }
}

// here
export async function renderHere() {
  const HERE_POS = '5';
  const { x, y } = window.selfData;
  const key = `${x},${y}`;
  const obj = window.planetData.tiles[key] ?? null;

  if (!obj) {
    const html = await fetch('/partial/here/none').then((r) => r.text());
    document.querySelector(`[data-pos="5"]`).innerHTML = html;
    return;
  }

  window.hereData = await fetch('/data/here').then((r) => r.json());
  console.log('hereData:', window.hereData);

  const res = await fetch(`/partial/here/${obj.kind}`);
  if (!res.ok) {
    throw new Error(`unknown here kind: ${obj.kind}`);
  }

  const html = await res.text();
  document.querySelector(`[data-pos="${HERE_POS}"]`).innerHTML = html;
}

/* 
========== action =========
*/

async function onWalk() {
  const res = await fetch('/action/move/walk', {
    method: 'POST',
  });

  const data = await res.json();
  window.selfData = data.surroundings;

  console.log('walk result', data);
}

async function onTurn(turn) {
  const form = new URLSearchParams();
  form.append('turn', turn);

  const res = await fetch('/action/move//turn', {
    method: 'POST',
    body: form,
  });
  const data = await res.json();

  window.planetData = data.surroundings;

  console.log('turn result', data);
}

async function onPostToTile() {
  const textarea = document.querySelector('[data-field="post-textarea"]');
  if (!textarea) return;

  const text = textarea.value.trim();
  if (!text) return; // 空投稿は黙って無視

  const res = await fetch('/action/create/post/to-tile', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }),
  });

  const data = await res.json();
  const key = `${data.x},${data.y}`;

  window.planetData.tiles[key] = {
    id: data.object_id,
    kind: data.kind,
    content: data.content,
  };

  console.log('post result', data);
}

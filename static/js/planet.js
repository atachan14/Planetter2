export async function initPlanet() {
  initPlanetEvents();

  await Promise.all([refreshSurroundData(), refreshJustPos()]);
}

export function initPlanetEvents() {
  const walkBtn = document.querySelector('.walk-btn');
  const leftBtn = document.querySelector('.left-turn-btn');
  const rightBtn = document.querySelector('.right-turn-btn');

  if (walkBtn) {
    walkBtn.addEventListener('click', onWalk);
  }
  if (leftBtn) {
    leftBtn.addEventListener('click', () => onTurn(-1));
  }
  if (rightBtn) {
    rightBtn.addEventListener('click', () => onTurn(1));
  }
}

// surround
async function refreshSurroundData() {
  const data = await fetch('/planet/surround').then((r) => r.json());
  window.surroundData = data;
  renderSurroundData(data);
}

function renderSurroundData(data) {
  const tiles = data.tiles;

  document.querySelectorAll('[data-pos]').forEach((el) => {
    const key = el.dataset.pos;
    const tile = tiles[key] ?? { type: 'none' };

    resetCell(el);
    renderTile(el, tile);
  });
}

// now-pos
async function refreshJustPos() {
  const data = await fetch('/planet/just-pos').then((r) => r.json());
  window.nowPosData = data;
  renderJustPos(data);
}

function renderJustPos(data) {}

function resetCell(el) {
  el.textContent = '';
  el.className = el.className.replace(/tile-\w+/g, '');
}
function renderTile(el, tile) {
  el.classList.add(`tile-${tile.type}`);

  switch (tile.type) {
    case 'none':
      el.textContent = 'None';
      break;

    case 'post':
      el.textContent = tile.value;
      break;

    case 'page':
      el.textContent = tile.name;
      break;

    case 'book':
      el.textContent = tile.name;
      break;

    case 'player':
      el.textContent = 'YOU';
      break;

    default:
      el.textContent = '?';
  }
}

/* 
========== action =========
*/

async function onWalk() {
  const res = await fetch('/planet/walk', {
    method: 'POST',
  });

  const data = await res.json();
  window.surroundings = data.surroundings;

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

  window.surroundings = data.surroundings;

  console.log('turn result', data);
  // TODO: 周囲UI更新
}

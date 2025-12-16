async function init() {
  // ① ユーザー状態は必ず取る
  if (!window.userState) {
    window.userState = await fetch('/services/user_state').then((r) =>
      r.json()
    );
  }

  // ② 惑星データがあるかで分岐
  if (!window.planetTiles) {
    showLanding();
  } else {
    showPlanet();
  }
}
async function showLanding() {
  const html = await fetch('/partial/landing').then((r) => r.text());
  document.querySelector('main').innerHTML = html;
}
async function showPlanet() {
  const html = await fetch('/partial/planet').then((r) => r.text());
  document.querySelector('main').innerHTML = html;
}

async function onLanding() {
  window.planetTiles = await fetch('/planet/tiles').then((r) => r.json());
  showPlanet();
}

// time.js
export function calcSurviveDays(createdAt, now = new Date()) {
  if (!createdAt) return 0;

  const created = new Date(createdAt);
  if (isNaN(created)) return 0;

  const diffMs = now - created;
  if (diffMs < 0) return 0;

  return Math.floor(diffMs / (1000 * 60 * 60 * 24));
}

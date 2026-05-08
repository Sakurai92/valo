const API_URL = 'https://valorant-api.com/v1/agents?isPlayableCharacter=true&language=ja-JP';

let allAgents   = [];
let playerCount = 1;

function showScreen(id) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
}

function shuffle(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

// 人数ボタン
document.getElementById('count-btns').addEventListener('click', e => {
  const btn = e.target.closest('.count-btn');
  if (!btn) return;
  playerCount = Number(btn.dataset.n);
  document.querySelectorAll('.count-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  renderNameInputs(playerCount);
});

function renderNameInputs(n) {
  const wrap = document.getElementById('name-inputs');
  // 既存の値を保持
  const old = [...wrap.querySelectorAll('.name-input')].map(el => el.value);
  wrap.innerHTML = '';
  for (let i = 0; i < n; i++) {
    const input = document.createElement('input');
    input.type        = 'text';
    input.className   = 'name-input';
    input.placeholder = `Player ${i + 1}`;
    input.maxLength   = 20;
    input.value       = old[i] ?? '';
    wrap.appendChild(input);
  }
}

function getPlayerNames() {
  return [...document.querySelectorAll('.name-input')].map((el, i) =>
    el.value.trim() || `Player ${i + 1}`
  );
}

function doPick() {
  const names   = getPlayerNames();
  const picked  = shuffle(allAgents).slice(0, names.length);
  renderResult(names, picked);
  showScreen('screen-result');
}

function renderResult(names, agents) {
  const container = document.getElementById('pick-cards');
  container.className = 'pick-cards' + (names.length === 1 ? ' solo' : '');
  container.innerHTML = names.map((name, i) => `
    <div class="pick-card" style="animation-delay:${i * 0.1}s">
      <img class="agent-img" src="${agents[i].image}" alt="${agents[i].name}">
      <div class="agent-name">${agents[i].name}</div>
      <div class="agent-role">${agents[i].role}</div>
      <div class="player-label">${name}</div>
    </div>
  `).join('');
}

document.getElementById('btn-pick').addEventListener('click', doPick);

document.getElementById('btn-repick').addEventListener('click', () => {
  const names  = getPlayerNames();
  const picked = shuffle(allAgents).slice(0, names.length);
  renderResult(names, picked);
});

document.getElementById('btn-back').addEventListener('click', () => {
  showScreen('screen-setup');
});

// 初期化
renderNameInputs(1);

(async () => {
  try {
    const res  = await fetch(API_URL);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    allAgents  = json.data
      .filter(a => a.role)
      .map(a => ({
        name:  a.displayName,
        image: a.displayIcon,
        role:  a.role.displayName,
      }));
    showScreen('screen-setup');
  } catch (e) {
    document.getElementById('screen-loading').innerHTML = `
      <p style="color:#ff4655">⚠️ データの読み込みに失敗しました</p>
      <p style="color:#7a8a99;margin-top:8px;font-size:.85rem">インターネット接続を確認してください</p>
      <button onclick="location.reload()" style="margin-top:20px;padding:10px 28px;background:#ff4655;color:#fff;border:none;border-radius:8px;font-size:.9rem;cursor:pointer">再試行</button>
    `;
  }
})();

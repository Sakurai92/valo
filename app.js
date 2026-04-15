const API_URL =
  'https://valorant-api.com/v1/agents?isPlayableCharacter=true&language=ja-JP';

const ROLE_ORDER = ['Duelist', 'Sentinel', 'Controller', 'Initiator'];

const ROLE_TO_EN = {
  'Duelist':      'Duelist',
  'Controller':   'Controller',
  'Sentinel':     'Sentinel',
  'Initiator':    'Initiator',
  'デュエリスト':  'Duelist',
  'コントローラー':'Controller',
  'センチネル':    'Sentinel',
  'イニシエーター':'Initiator',
};

let agents = [];
const eliminated = new Set();
let currentFilter = 'all';

async function loadAgents() {
  const res = await fetch(API_URL);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const json = await res.json();

  return json.data
    .filter(a => a.role)
    .sort((a, b) => {
      const ra = ROLE_ORDER.indexOf(ROLE_TO_EN[a.role.displayName] ?? a.role.displayName);
      const rb = ROLE_ORDER.indexOf(ROLE_TO_EN[b.role.displayName] ?? b.role.displayName);
      if (ra !== rb) return ra - rb;
      return a.displayName.localeCompare(b.displayName, 'ja');
    })
    .map(a => ({
      uuid:        a.uuid,
      displayName: a.displayName,
      displayIcon: a.displayIcon,
      role:        ROLE_TO_EN[a.role.displayName] ?? a.role.displayName,
    }));
}

function getFiltered() {
  if (currentFilter === 'all') return agents;
  return agents.filter(a => a.role === currentFilter);
}

function renderGrid() {
  const grid = document.getElementById('grid');
  const filtered = getFiltered();

  grid.innerHTML = '';

  filtered.forEach(agent => {
    const isElim = eliminated.has(agent.uuid);
    const card = document.createElement('div');
    card.className = 'agent-card' + (isElim ? ' eliminated' : '');
    card.dataset.uuid = agent.uuid;

    card.innerHTML = `
      <div class="card-img-wrap">
        <img
          src="${agent.displayIcon}"
          alt="${agent.displayName}"
          loading="lazy"
          draggable="false"
        >
        <div class="elim-overlay"><span>✕</span></div>
      </div>
      <div class="card-name">${agent.displayName}</div>
    `;

    card.addEventListener('click', () => toggleCard(agent.uuid));
    grid.appendChild(card);
  });

  updateCounter();
}

function toggleCard(uuid) {
  if (eliminated.has(uuid)) {
    eliminated.delete(uuid);
  } else {
    eliminated.add(uuid);
  }

  const card = document.querySelector(`.agent-card[data-uuid="${uuid}"]`);
  if (card) card.classList.toggle('eliminated');

  updateCounter();
}

function updateCounter() {
  const filtered = getFiltered();
  const total     = filtered.length;
  const remaining = filtered.filter(a => !eliminated.has(a.uuid)).length;

  document.getElementById('count-num').textContent   = remaining;
  document.getElementById('count-total').textContent = total;
}

function showError() {
  document.getElementById('grid').innerHTML = `
    <div class="error">
      <p>⚠️ エージェントデータの読み込みに失敗しました</p>
      <p>インターネット接続を確認してから再試行してください</p>
      <button onclick="init()">再試行</button>
    </div>
  `;
}

async function init() {
  document.getElementById('grid').innerHTML = `
    <div class="loading" id="loading">
      <div class="spinner"></div>
      <p>エージェントデータを読み込み中…</p>
    </div>
  `;

  try {
    agents = await loadAgents();
    renderGrid();
  } catch (e) {
    console.error('Failed to load agents:', e);
    showError();
  }
}

document.getElementById('role-filter').addEventListener('click', e => {
  const btn = e.target.closest('.filter-btn');
  if (!btn) return;

  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  currentFilter = btn.dataset.role;
  renderGrid();
});

document.getElementById('reset-btn').addEventListener('click', () => {
  eliminated.clear();
  document.querySelectorAll('.agent-card.eliminated').forEach(card => {
    card.classList.remove('eliminated');
  });
  updateCounter();
});

init();

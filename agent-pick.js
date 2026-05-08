const API_URL    = 'https://valorant-api.com/v1/agents?isPlayableCharacter=true&language=ja-JP';
const ROLE_ORDER = ['デュエリスト', 'イニシエーター', 'センチネル', 'コントローラー'];

let allAgents   = [];
let selectedSet = new Set();
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

// ── フィルター ──────────────────────────

function getUniqueRoles() {
  const seen = new Set();
  return ROLE_ORDER.filter(r => allAgents.some(a => a.role === r));
}

function renderRoleFilter() {
  const container = document.getElementById('role-filter');
  container.innerHTML = '';

  // 全員ボタン
  const allBtn = document.createElement('button');
  allBtn.className   = 'role-btn';
  allBtn.id          = 'role-btn-all';
  allBtn.textContent = '全員';
  allBtn.addEventListener('click', () => {
    if (selectedSet.size === allAgents.length) {
      selectedSet.clear();
    } else {
      allAgents.forEach(a => selectedSet.add(a.name));
    }
    updateFilter();
  });
  container.appendChild(allBtn);

  getUniqueRoles().forEach(role => {
    const btn = document.createElement('button');
    btn.className   = 'role-btn';
    btn.dataset.role = role;
    btn.textContent  = role;
    btn.addEventListener('click', () => {
      const inRole      = allAgents.filter(a => a.role === role).map(a => a.name);
      const allSelected = inRole.every(n => selectedSet.has(n));
      if (allSelected) {
        inRole.forEach(n => selectedSet.delete(n));
      } else {
        inRole.forEach(n => selectedSet.add(n));
      }
      updateFilter();
    });
    container.appendChild(btn);
  });
}

function renderAgentChips() {
  const container = document.getElementById('agent-chips');
  container.innerHTML = '';

  // ロール順に並べる
  const sorted = [...allAgents].sort((a, b) => {
    const ri = r => ROLE_ORDER.indexOf(r);
    return ri(a.role) - ri(b.role) || a.name.localeCompare(b.name);
  });

  sorted.forEach(agent => {
    const chip = document.createElement('button');
    chip.className   = 'agent-chip' + (selectedSet.has(agent.name) ? ' on' : '');
    chip.dataset.name = agent.name;
    chip.innerHTML    = `<img src="${agent.image}" alt="${agent.name}"><span class="chip-name">${agent.name}</span>`;
    chip.addEventListener('click', () => {
      if (selectedSet.has(agent.name)) {
        selectedSet.delete(agent.name);
      } else {
        selectedSet.add(agent.name);
      }
      updateFilter();
    });
    container.appendChild(chip);
  });
}

function updateFilter() {
  // ロールボタンの状態更新
  document.querySelectorAll('.role-btn[data-role]').forEach(btn => {
    const inRole = allAgents.filter(a => a.role === btn.dataset.role);
    const n      = inRole.filter(a => selectedSet.has(a.name)).length;
    btn.classList.remove('active', 'partial');
    if (n === inRole.length) btn.classList.add('active');
    else if (n > 0)          btn.classList.add('partial');
  });

  // 全員ボタン
  const allBtn = document.getElementById('role-btn-all');
  if (allBtn) {
    allBtn.classList.toggle('active', selectedSet.size === allAgents.length);
  }

  // チップの on/off
  document.querySelectorAll('.agent-chip').forEach(chip => {
    chip.classList.toggle('on', selectedSet.has(chip.dataset.name));
  });

  // カウント表示 & ピックボタン
  const count   = selectedSet.size;
  const countEl = document.getElementById('filter-count');
  countEl.textContent = `${count} / ${allAgents.length} 人を選択中`;
  countEl.classList.toggle('warn', count < playerCount);

  const pickBtn = document.getElementById('btn-pick');
  pickBtn.disabled = count < playerCount;
}

// ── 人数・名前 ───────────────────────────

document.getElementById('count-btns').addEventListener('click', e => {
  const btn = e.target.closest('.count-btn');
  if (!btn) return;
  playerCount = Number(btn.dataset.n);
  document.querySelectorAll('.count-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  renderNameInputs(playerCount);
  updateFilter();
});

function renderNameInputs(n) {
  const wrap = document.getElementById('name-inputs');
  const old  = [...wrap.querySelectorAll('.name-input')].map(el => el.value);
  wrap.innerHTML = '';
  for (let i = 0; i < n; i++) {
    const input       = document.createElement('input');
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

// ── ピック ──────────────────────────────

function doPick() {
  const names  = getPlayerNames();
  const pool   = allAgents.filter(a => selectedSet.has(a.name));
  const picked = shuffle(pool).slice(0, names.length);
  renderResult(names, picked);
  showScreen('screen-result');
}

function renderResult(names, agents) {
  const container = document.getElementById('pick-cards');
  container.className = 'pick-cards' + (names.length === 1 ? ' solo' : '');
  container.innerHTML = names.map((name, i) => `
    <div class="pick-card" style="animation-delay:${i * 0.1}s">
      <img class="agent-img" src="${agents[i].image}" alt="${agents[i].name}" crossorigin="anonymous">
      <div class="agent-name">${agents[i].name}</div>
      <div class="agent-role">${agents[i].role}</div>
      <div class="player-label">${name}</div>
    </div>
  `).join('');
}

document.getElementById('btn-pick').addEventListener('click', doPick);

document.getElementById('btn-repick').addEventListener('click', () => {
  const names  = getPlayerNames();
  const pool   = allAgents.filter(a => selectedSet.has(a.name));
  const picked = shuffle(pool).slice(0, names.length);
  renderResult(names, picked);
});

document.getElementById('btn-back').addEventListener('click', () => {
  showScreen('screen-setup');
});


// ── 初期化 ──────────────────────────────

renderNameInputs(1);

(async () => {
  try {
    const res  = await fetch(API_URL);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();

    allAgents = json.data
      .filter(a => a.role)
      .map(a => ({
        name:  a.displayName,
        image: a.displayIcon,
        role:  a.role.displayName,
      }));

    selectedSet = new Set(allAgents.map(a => a.name));

    renderRoleFilter();
    renderAgentChips();
    updateFilter();
    showScreen('screen-setup');
  } catch (e) {
    document.getElementById('screen-loading').innerHTML = `
      <p style="color:#ff4655">⚠️ データの読み込みに失敗しました</p>
      <p style="color:#7a8a99;margin-top:8px;font-size:.85rem">インターネット接続を確認してください</p>
      <button onclick="location.reload()" style="margin-top:20px;padding:10px 28px;background:#ff4655;color:#fff;border:none;border-radius:8px;font-size:.9rem;cursor:pointer">再試行</button>
    `;
  }
})();

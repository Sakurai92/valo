const GAME_DURATION = 30000;
const FEEDBACK_MS   = 350;
const SKIP_SKIN_KW  = ['スタンダード', 'Standard', 'デフォルト', 'Default', 'ランダムお気に入りスキン', 'Random Favorite', '近接武器'];
const SKIP_MAP_URLS = ['Range', 'HURM', 'Tutorial', 'Poveglia', 'Skirmish', 'NPEV2'];

const CATEGORIES = [
  { id: 'ability', label: 'スキル当て',     icon: '⚡', qLabel: 'スキル名は？' },
  { id: 'spray',   label: 'スプレー当て',   icon: '🎨', qLabel: 'スプレー名は？' },
  { id: 'buddy',   label: 'ガンバディ当て', icon: '🧸', qLabel: 'ガンバディ名は？' },
  { id: 'skin',    label: 'スキン当て',     icon: '🔫', qLabel: 'スキン名は？' },
  { id: 'card',    label: 'カード当て',     icon: '🪪', qLabel: 'カード名は？' },
  { id: 'map',     label: 'マップ当て',     icon: '🗺️', qLabel: 'マップ名は？' },
];

let pools       = {};
let selectedCat = null;
let score       = 0;
let cntCorrect  = 0;
let cntWrong    = 0;
let cntPass     = 0;
let startTime   = 0;
let timerHandle = null;
let gameActive  = false;

async function fetchJSON(url) {
  const ctrl = new AbortController();
  const tid  = setTimeout(() => ctrl.abort(), 15000);
  try {
    const res = await fetch(url, { signal: ctrl.signal });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } finally {
    clearTimeout(tid);
  }
}

async function buildPools() {
  const [agents, sprays, buddies, weapons, cards, maps] = await Promise.all([
    fetchJSON('https://valorant-api.com/v1/agents?isPlayableCharacter=true&language=ja-JP'),
    fetchJSON('https://valorant-api.com/v1/sprays?language=ja-JP'),
    fetchJSON('https://valorant-api.com/v1/buddies?language=ja-JP'),
    fetchJSON('https://valorant-api.com/v1/weapons?language=ja-JP'),
    fetchJSON('https://valorant-api.com/v1/playercards?language=ja-JP'),
    fetchJSON('https://valorant-api.com/v1/maps?language=ja-JP'),
  ]);

  const abilityItems = [];
  for (const agent of agents.data) {
    if (!agent.role) continue;
    for (const ab of agent.abilities) {
      if (!ab.displayIcon) continue;
      abilityItems.push({ image: ab.displayIcon, answer: ab.displayName });
    }
  }
  const abilityNames = abilityItems.map(i => i.answer);
  pools.ability = abilityItems.map(i => ({ ...i, wrongPool: abilityNames }));

  const sprayItems = sprays.data
    .filter(s => s.displayName !== 'なし' && (s.animationGif || s.fullIcon || s.displayIcon))
    .map(s => ({ image: s.animationGif ?? s.fullIcon ?? s.displayIcon, answer: s.displayName }));
  const sprayNames = sprayItems.map(i => i.answer);
  pools.spray = sprayItems.map(i => ({ ...i, wrongPool: sprayNames }));

  const buddyItems = buddies.data
    .filter(b => b.displayIcon)
    .map(b => ({ image: b.displayIcon, answer: b.displayName }));
  const buddyNames = buddyItems.map(i => i.answer);
  pools.buddy = buddyItems.map(i => ({ ...i, wrongPool: buddyNames }));

  const skinItems = [];
  for (const weapon of weapons.data) {
    for (const skin of weapon.skins) {
      if (SKIP_SKIN_KW.some(kw => skin.displayName.includes(kw))) continue;
      const img = skin.displayIcon ?? skin.levels?.[0]?.displayIcon;
      if (!img) continue;
      skinItems.push({ image: img, answer: skin.displayName });
    }
  }
  const skinNames = skinItems.map(i => i.answer);
  pools.skin = skinItems.map(i => ({ ...i, wrongPool: skinNames }));

  const cardItems = cards.data
    .filter(c => c.largeArt || c.wideArt)
    .map(c => ({ image: c.animationGif ?? c.largeArt ?? c.wideArt, answer: c.displayName }));
  const cardNames = cardItems.map(i => i.answer);
  pools.card = cardItems.map(i => ({ ...i, wrongPool: cardNames }));

  const mapItems = maps.data
    .filter(m => {
      if (SKIP_MAP_URLS.some(kw => (m.mapUrl ?? '').includes(kw))) return false;
      return m.displayIcon || m.splash;
    })
    .map(m => ({ image: m.displayIcon ?? m.splash, answer: m.displayName }));
  const mapNames = mapItems.map(i => i.answer);
  pools.map = mapItems.map(i => ({ ...i, wrongPool: mapNames }));
}

function shuffle(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function pickRandom(arr, n) {
  return shuffle(arr).slice(0, n);
}

function showScreen(id) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
}

function updateScoreDisplay() {
  const el = document.getElementById('score');
  el.textContent  = score;
  el.style.color  = score < 0 ? 'var(--wrong)' : 'var(--correct)';
}

function updateTimerColor(left) {
  const el = document.getElementById('timer-num');
  if (left <= 5) {
    el.style.color     = '#ff4655';
    el.style.animation = 'pulse 0.5s ease infinite';
  } else if (left <= 10) {
    el.style.color     = '#ff4655';
    el.style.animation = '';
  } else {
    el.style.color     = '';
    el.style.animation = '';
  }
}

function lockButtons() {
  document.querySelectorAll('.choice-btn').forEach(b => b.disabled = true);
  document.getElementById('btn-pass').disabled = true;
}

function nextQuestion() {
  const pool   = pools[selectedCat.id];
  const item   = pool[Math.floor(Math.random() * pool.length)];
  const wrongs = pickRandom(item.wrongPool.filter(n => n !== item.answer), 3);
  const choices = shuffle([item.answer, ...wrongs]);

  const img = document.getElementById('q-image');
  img.src = item.image;
  img.alt = item.answer;

  const choicesEl = document.getElementById('choices');
  choicesEl.innerHTML = '';
  choices.forEach(name => {
    const btn = document.createElement('button');
    btn.className = 'choice-btn';
    btn.textContent = name;
    btn.addEventListener('click', () => onAnswer(btn, name, item.answer));
    choicesEl.appendChild(btn);
  });

  document.getElementById('btn-pass').disabled = false;
}

function onAnswer(btn, selected, correct) {
  if (!gameActive) return;
  lockButtons();

  const isCorrect = selected === correct;
  if (isCorrect) {
    score++;
    cntCorrect++;
    btn.classList.add('correct');
  } else {
    score--;
    cntWrong++;
    btn.classList.add('wrong');
    document.querySelectorAll('.choice-btn').forEach(b => {
      if (b.textContent === correct) b.classList.add('correct');
    });
  }

  updateScoreDisplay();
  setTimeout(() => { if (gameActive) nextQuestion(); }, FEEDBACK_MS);
}

function onPass() {
  if (!gameActive) return;
  lockButtons();
  cntPass++;
  setTimeout(() => { if (gameActive) nextQuestion(); }, 100);
}

function startTimer() {
  startTime  = Date.now();
  gameActive = true;

  const bar = document.getElementById('timer-bar');
  bar.style.transition = 'none';
  bar.style.width = '100%';
  bar.offsetWidth;
  bar.style.transition = `width ${GAME_DURATION / 1000}s linear`;
  bar.style.width = '0%';

  timerHandle = setInterval(() => {
    const elapsed = Date.now() - startTime;
    const left    = Math.max(0, Math.ceil((GAME_DURATION - elapsed) / 1000));
    document.getElementById('timer-num').textContent = left;
    updateTimerColor(left);
    if (elapsed >= GAME_DURATION) endGame();
  }, 100);
}

function endGame() {
  gameActive = false;
  clearInterval(timerHandle);

  const el = document.getElementById('result-score');
  el.textContent  = score;
  el.style.color  = score < 0 ? 'var(--wrong)' : 'var(--accent)';

  document.getElementById('stat-correct').textContent = cntCorrect;
  document.getElementById('stat-wrong').textContent   = cntWrong;
  document.getElementById('stat-pass').textContent    = cntPass;

  const messages = [
    [15, '神速！反射神経が違いすぎる👑'],
    [10, 'すごい！かなりの知識と速さだ👏'],
    [5,  'なかなかやるね！もう一回挑戦してみよう'],
    [1,  'まだまだこれから。たくさんプレイしよう'],
    [-Infinity, 'ノーヒント…次は慎重に！'],
  ];
  const msg = messages.find(([t]) => score >= t)?.[1] ?? '';
  document.getElementById('result-msg').textContent = msg;

  showScreen('screen-result');
}

function stopGame() {
  gameActive = false;
  clearInterval(timerHandle);
}

function startGame(cat) {
  selectedCat = cat;
  score       = 0;
  cntCorrect  = 0;
  cntWrong    = 0;
  cntPass     = 0;

  document.getElementById('timer-num').textContent = GAME_DURATION / 1000;
  document.getElementById('q-label').textContent   = cat.qLabel;
  updateScoreDisplay();
  updateTimerColor(GAME_DURATION / 1000);

  showScreen('screen-quiz');
  nextQuestion();
  startTimer();
}

function buildCategoryList() {
  const list = document.getElementById('category-list');
  CATEGORIES.forEach(cat => {
    const btn = document.createElement('button');
    btn.className = 'cat-btn';
    btn.innerHTML = `<span class="cat-icon">${cat.icon}</span><span class="cat-label">${cat.label}</span>`;
    btn.addEventListener('click', () => startGame(cat));
    list.appendChild(btn);
  });
}

document.getElementById('btn-pass').addEventListener('click', onPass);
document.getElementById('btn-retry').addEventListener('click', () => startGame(selectedCat));
document.getElementById('btn-change').addEventListener('click', () => showScreen('screen-start'));
document.getElementById('btn-back').addEventListener('click', () => {
  stopGame();
  showScreen('screen-start');
});

buildCategoryList();

(async () => {
  try {
    await buildPools();
    showScreen('screen-start');
  } catch (e) {
    console.error('Failed to load:', e);
    document.getElementById('screen-loading').innerHTML = `
      <p style="color:#ff4655">⚠️ データの読み込みに失敗しました</p>
      <p style="color:#7a8a99;margin-top:8px;font-size:.85rem">インターネット接続を確認してください</p>
      <button onclick="location.reload()" style="margin-top:20px;padding:10px 28px;background:#ff4655;color:#fff;border:none;border-radius:8px;font-size:.9rem;cursor:pointer">再試行</button>
    `;
  }
})();

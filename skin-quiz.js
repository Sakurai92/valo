const API_URL = 'https://valorant-api.com/v1/weapons?language=ja-JP';
const TOTAL_QUESTIONS = 10;

const SKIP_KEYWORDS = ['スタンダード', 'Standard', 'デフォルト', 'Default', 'ランダムお気に入りスキン', 'Random Favorite', '近接武器'];

let allSkins = [];

let questions      = [];
let currentIdx     = 0;
let score          = 0;
let selectedChoice = null;

async function loadSkins() {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 15000);

  let res;
  try {
    res = await fetch(API_URL, { signal: controller.signal });
  } catch (e) {
    throw new Error('タイムアウトまたはネットワークエラー');
  } finally {
    clearTimeout(timeout);
  }

  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const json = await res.json();

  const skins = [];
  for (const weapon of json.data) {
    for (const skin of weapon.skins) {
      if (SKIP_KEYWORDS.some(kw => skin.displayName.includes(kw))) continue;

      const image =
        skin.displayIcon ??
        skin.levels?.[0]?.displayIcon ??
        null;

      if (!image) continue;

      skins.push({
        name:   skin.displayName,
        image:  image,
        weapon: weapon.displayName,
      });
    }
  }
  return skins;
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

function createQuestion(correctSkin) {
  const sameWeapon = allSkins.filter(
    s => s.weapon === correctSkin.weapon && s.name !== correctSkin.name
  );
  let wrongs = pickRandom(sameWeapon, 3);

  if (wrongs.length < 3) {
    const others = allSkins.filter(
      s => s.name !== correctSkin.name && !wrongs.includes(s)
    );
    wrongs = [...wrongs, ...pickRandom(others, 3 - wrongs.length)];
  }

  return {
    correct: correctSkin,
    choices: shuffle([correctSkin, ...wrongs]),
  };
}

function buildQuestions() {
  const picked = pickRandom(allSkins, TOTAL_QUESTIONS);
  return picked.map(skin => createQuestion(skin));
}

function showScreen(id) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
}

function showQuestion() {
  const q = questions[currentIdx];

  document.getElementById('q-progress').textContent =
    `${currentIdx + 1} / ${TOTAL_QUESTIONS}`;
  document.getElementById('q-score').textContent = `${score}点`;

  document.getElementById('weapon-name').textContent = q.correct.weapon;
  const img = document.getElementById('skin-image');
  img.src = q.correct.image;
  img.alt = q.correct.name;

  const choicesEl = document.getElementById('choices');
  choicesEl.innerHTML = '';
  q.choices.forEach(skin => {
    const btn = document.createElement('button');
    btn.className = 'choice-btn';
    btn.textContent = skin.name;
    btn.addEventListener('click', () => onSelect(skin.name));
    choicesEl.appendChild(btn);
  });

  selectedChoice = null;
  const btnAnswer = document.getElementById('btn-answer');
  btnAnswer.disabled = true;
  btnAnswer.classList.remove('hidden');
  document.getElementById('btn-next').classList.remove('visible');
  document.getElementById('feedback').className = 'feedback';
}

function onSelect(name) {
  selectedChoice = name;
  document.querySelectorAll('.choice-btn').forEach(btn => {
    btn.classList.toggle('selected', btn.textContent === name);
  });
  document.getElementById('btn-answer').disabled = false;
}

function onAnswer(selected, correct) {
  document.querySelectorAll('.choice-btn').forEach(btn => {
    btn.disabled = true;
    btn.classList.remove('selected');
    if (btn.textContent === correct) {
      btn.classList.add('correct');
    } else if (btn.textContent === selected && selected !== correct) {
      btn.classList.add('wrong');
    }
  });

  const isCorrect = selected === correct;
  if (isCorrect) score++;

  const feedback = document.getElementById('feedback');
  if (isCorrect) {
    feedback.textContent = '✓ 正解！';
    feedback.className = 'feedback correct';
  } else {
    feedback.textContent = `✗ 不正解… 正解は「${correct}」`;
    feedback.className = 'feedback wrong';
  }

  document.getElementById('btn-answer').classList.add('hidden');

  const btnNext = document.getElementById('btn-next');
  btnNext.textContent =
    currentIdx + 1 < TOTAL_QUESTIONS ? '次の問題 →' : '結果を見る';
  btnNext.classList.add('visible');
}

function nextQuestion() {
  currentIdx++;
  if (currentIdx < TOTAL_QUESTIONS) {
    showQuestion();
  } else {
    showResult();
  }
}

function showResult() {
  document.getElementById('result-num').textContent = score;

  const messages = [
    [10, 'パーフェクト！スキン博士すぎる🏆'],
    [8,  'すごい！かなりのスキン知識だ👏'],
    [6,  'なかなかやるね！もう一回挑戦してみよう'],
    [4,  'まだまだこれから。スキンをもっと見てみよう'],
    [0,  'スキンを買ってもらうしかないね…'],
  ];
  const msg = messages.find(([threshold]) => score >= threshold)?.[1] ?? '';
  document.getElementById('result-msg').textContent = msg;

  showScreen('screen-result');
}

function startGame() {
  questions  = buildQuestions();
  currentIdx = 0;
  score      = 0;
  showScreen('screen-quiz');
  showQuestion();
}

document.getElementById('btn-start').addEventListener('click', startGame);
document.getElementById('btn-retry').addEventListener('click', startGame);
document.getElementById('btn-next').addEventListener('click', nextQuestion);
document.getElementById('btn-answer').addEventListener('click', () => {
  if (selectedChoice !== null) {
    onAnswer(selectedChoice, questions[currentIdx].correct.name);
  }
});

(async () => {
  try {
    allSkins = await loadSkins();
    showScreen('screen-start');
  } catch (e) {
    console.error('Failed to load skins:', e);
    document.getElementById('screen-loading').innerHTML = `
      <p style="color:#ff4655">⚠️ データの読み込みに失敗しました</p>
      <p style="color:#7a8a99;margin-top:8px;font-size:.85rem">インターネット接続を確認してください</p>
      <button onclick="location.reload()" style="margin-top:20px;padding:10px 28px;background:#ff4655;color:#fff;border:none;border-radius:8px;font-size:.9rem;cursor:pointer">再試行</button>
    `;
  }
})();

// ── Animated money counter ────────────────────────────
const moneyEl = document.getElementById('hud-money');
const targets = [
  847_230_000, 839_441_200, 826_000_000, 812_500_000,
  1_203_000_000, 1_190_000_000, 1_178_400_000, 955_000_000,
];
let idx = 0;

function animateMoney(from, to, duration) {
  const start = performance.now();
  function step(now) {
    const t = Math.min((now - start) / duration, 1);
    const ease = t < 0.5 ? 2 * t * t : -1 + (4 - 2 * t) * t;
    const val = Math.round(from + (to - from) * ease);
    moneyEl.textContent = '$' + val.toLocaleString();
    moneyEl.style.color = val < from ? '#ff4444' : '#00ff90';
    if (t < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}

setInterval(() => {
  const prev = targets[idx];
  idx = (idx + 1) % targets.length;
  animateMoney(prev, targets[idx], 1800);
}, 3000);

// ── Bar pulse on hover ────────────────────────────────
document.querySelectorAll('.feature-card').forEach(card => {
  card.addEventListener('mouseenter', () => {
    card.style.boxShadow = '0 0 24px rgba(255,34,34,0.12)';
  });
  card.addEventListener('mouseleave', () => {
    card.style.boxShadow = '';
  });
});

// ── Fade-in on scroll ─────────────────────────────────
const observer = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.style.opacity = '1';
      e.target.style.transform = 'translateY(0)';
    }
  });
}, { threshold: 0.12 });

document.querySelectorAll(
  '.feature-card, .sys-item, .death-card, .stat'
).forEach(el => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(20px)';
  el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
  observer.observe(el);
});

// ── Duplicate ticker text for seamless loop ───────────
const ticker = document.querySelector('.ticker-inner');
if (ticker) {
  ticker.innerHTML += ticker.innerHTML;
}

// ── Live download count from GitHub API ───────────────
const dlEl = document.getElementById('dl-count');
if (dlEl) {
  fetch('https://api.github.com/repos/waterloolou/Debt-Clicker/releases')
    .then(r => r.json())
    .then(data => {
      const total = data.reduce((sum, release) =>
        sum + (release.assets || []).reduce((s, a) => s + a.download_count, 0), 0);
      // Animate count up
      const target = total;
      const duration = 1200;
      const start = performance.now();
      function countUp(now) {
        const t = Math.min((now - start) / duration, 1);
        const ease = 1 - Math.pow(1 - t, 3);
        dlEl.textContent = Math.round(ease * target).toLocaleString();
        if (t < 1) requestAnimationFrame(countUp);
      }
      requestAnimationFrame(countUp);
    })
    .catch(() => { dlEl.textContent = '—'; });
}

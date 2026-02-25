const canvas = document.getElementById('radar');
const ctx = canvas.getContext('2d');
const modeEl = document.getElementById('mode');
const statsEl = document.getElementById('stats');
const panelEl = document.getElementById('panel');

const bgParticles = [];
const particleCount = 45000;
let entities = [];

function resize() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
}

function initParticles() {
  bgParticles.length = 0;
  for (let i = 0; i < particleCount; i += 1) {
    bgParticles.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.18,
      vy: (Math.random() - 0.5) * 0.18,
      z: Math.random(),
    });
  }
}

function drawGrid() {
  ctx.strokeStyle = 'rgba(80,180,255,0.08)';
  ctx.lineWidth = 1;
  const cx = canvas.width / 2;
  const cy = canvas.height / 2;
  const maxR = Math.min(cx, cy) * 0.95;
  for (let r = 60; r < maxR; r += 80) {
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.stroke();
  }
}

function drawParticles() {
  for (const p of bgParticles) {
    p.x += p.vx;
    p.y += p.vy;
    if (p.x < 0) p.x = canvas.width;
    if (p.x > canvas.width) p.x = 0;
    if (p.y < 0) p.y = canvas.height;
    if (p.y > canvas.height) p.y = 0;

    const alpha = 0.04 + p.z * 0.3;
    ctx.fillStyle = `rgba(90, 215, 255, ${alpha})`;
    const size = 0.5 + p.z * 1.2;
    ctx.fillRect(p.x, p.y, size, size);
  }
}

function drawEntities() {
  for (const entity of entities) {
    const x = (entity.x / 100) * canvas.width;
    const y = (entity.y / 100) * canvas.height;
    const base = Math.max(4, 16 - entity.distance_m / 2);
    const moving = entity.movement > 0.3;

    ctx.beginPath();
    ctx.fillStyle = moving ? 'rgba(255, 75, 75, 0.9)' : 'rgba(120, 255, 140, 0.9)';
    ctx.arc(x, y, base, 0, Math.PI * 2);
    ctx.fill();

    if (moving) {
      const pulse = (Date.now() % 1000) / 1000;
      const radius = base + pulse * 25;
      ctx.beginPath();
      ctx.strokeStyle = `rgba(255,70,70,${1 - pulse})`;
      ctx.lineWidth = 2;
      ctx.arc(x, y, radius, 0, Math.PI * 2);
      ctx.stroke();
    }
  }
}

function render() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawGrid();
  drawParticles();
  drawEntities();
  requestAnimationFrame(render);
}

function renderPanel() {
  panelEl.innerHTML = entities
    .map((e) => {
      const cls = e.movement > 0.3 ? 'entity move' : 'entity';
      return `<div class="${cls}">
        <strong>${e.name}</strong><br/>
        Source: ${e.source}<br/>
        RSSI: ${e.rssi} dBm · Distance: ~${e.distance_m} m<br/>
        Motion: ${Math.round(e.movement * 100)}%
      </div>`;
    })
    .join('');
}

function connect() {
  const ws = new WebSocket(`${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/ws/live`);

  ws.onmessage = (event) => {
    const payload = JSON.parse(event.data);
    entities = payload.entities || [];
    modeEl.textContent = `Mode: ${payload.mode === 'live' ? 'LIVE SCAN' : 'SYNTHETIC DEMO'} (${new Date(payload.timestamp * 1000).toLocaleTimeString()})`;
    statsEl.textContent = `Devices: ${payload.device_count} · Moving: ${payload.moving_count} · Motion: ${payload.motion_level}`;
    renderPanel();
  };

  ws.onclose = () => {
    modeEl.textContent = 'Mode: disconnected, retrying...';
    setTimeout(connect, 1200);
  };
}

window.addEventListener('resize', () => {
  resize();
  initParticles();
});

resize();
initParticles();
render();
connect();

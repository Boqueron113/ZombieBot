"""
webapp.py — Servidor web Flask para el dashboard del bot zombie
Se ejecuta en paralelo con el bot en Railway.
"""
from flask import Flask, render_template_string, jsonify, abort
import threading
import os
import json
import time

app = Flask(__name__)

# ── TOKEN STORE ───────────────────────────────────────────────────────────────
# {token: {"discord_id": str, "expires": float}}
_tokens = {}
TOKEN_DURACION = 900  # 15 minutos

def crear_token(discord_id):
    """Genera un token temporal para un jugador."""
    # Limpiar tokens expirados
    ahora = time.time()
    expirados = [t for t, d in _tokens.items() if d["expires"] < ahora]
    for t in expirados:
        del _tokens[t]
    # Crear nuevo token
    import secrets
    token = secrets.token_urlsafe(16)
    _tokens[token] = {"discord_id": str(discord_id), "expires": ahora + TOKEN_DURACION}
    return token

def validar_token(token):
    """Devuelve discord_id si el token es válido, None si no."""
    datos = _tokens.get(token)
    if not datos:
        return None
    if time.time() > datos["expires"]:
        del _tokens[token]
        return None
    return datos["discord_id"]

# Referencia global a la DB del bot (se inyecta desde bot.py)
_db = None

def init_webapp(db):
    global _db
    _db = db

# ── HTML TEMPLATE ─────────────────────────────────────────────────────────────
HTML = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{ nombre }} — Apocalipsis Zombie</title>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Share+Tech+Mono&family=Barlow:wght@400;600;700&display=swap" rel="stylesheet">
<style>
  :root {
    --rojo: #c0392b;
    --rojo-dark: #96281b;
    --verde: #2d5a1b;
    --verde-bright: #4caf50;
    --naranja: #e67e22;
    --gris: #1a1a1a;
    --gris-mid: #2a2a2a;
    --gris-light: #3a3a3a;
    --texto: #e8e0d0;
    --texto-dim: #8a8070;
    --oro: #c9a84c;
    --morado: #8e44ad;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: var(--gris);
    color: var(--texto);
    font-family: 'Barlow', sans-serif;
    min-height: 100vh;
    background-image:
      radial-gradient(ellipse at 20% 50%, rgba(192,57,43,0.05) 0%, transparent 60%),
      radial-gradient(ellipse at 80% 20%, rgba(45,90,27,0.05) 0%, transparent 60%);
  }

  /* ── HEADER ── */
  .header {
    background: linear-gradient(135deg, #0d0d0d 0%, #1a0a0a 100%);
    border-bottom: 2px solid var(--rojo);
    padding: 1.5rem 2rem;
    display: flex;
    align-items: center;
    gap: 1.5rem;
    position: relative;
    overflow: hidden;
  }
  .header::before {
    content: '🧟';
    font-size: 8rem;
    position: absolute;
    right: -1rem;
    top: -1rem;
    opacity: 0.06;
    transform: rotate(-15deg);
  }
  .header-avatar {
    width: 70px; height: 70px;
    border-radius: 50%;
    border: 3px solid var(--rojo);
    background: var(--gris-mid);
    display: flex; align-items: center; justify-content: center;
    font-size: 2rem;
    flex-shrink: 0;
  }
  .header-info h1 {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2.4rem;
    letter-spacing: 0.1em;
    color: #fff;
    line-height: 1;
  }
  .header-info .subtitle {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.8rem;
    color: var(--rojo);
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-top: 4px;
  }
  .header-badge {
    margin-left: auto;
    background: var(--verde);
    color: #fff;
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.1rem;
    padding: 6px 16px;
    border-radius: 4px;
    letter-spacing: 0.1em;
  }

  /* ── TABS ── */
  .tabs {
    display: flex;
    gap: 0;
    background: #0d0d0d;
    border-bottom: 1px solid #333;
    overflow-x: auto;
    scrollbar-width: none;
  }
  .tab-btn {
    padding: 1rem 1.5rem;
    background: none;
    border: none;
    color: var(--texto-dim);
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1rem;
    letter-spacing: 0.15em;
    cursor: pointer;
    border-bottom: 3px solid transparent;
    transition: all 0.2s;
    white-space: nowrap;
  }
  .tab-btn:hover { color: var(--texto); background: rgba(255,255,255,0.03); }
  .tab-btn.active { color: var(--rojo); border-bottom-color: var(--rojo); }

  /* ── CONTENT ── */
  .content { padding: 1.5rem 2rem; max-width: 1100px; margin: 0 auto; }
  .panel { display: none; }
  .panel.active { display: block; }

  /* ── CARDS ── */
  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
  .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }
  @media(max-width: 700px) {
    .grid-2, .grid-3 { grid-template-columns: 1fr; }
    .content { padding: 1rem; }
  }

  .card {
    background: var(--gris-mid);
    border: 1px solid #333;
    border-radius: 8px;
    padding: 1.25rem;
    position: relative;
    overflow: hidden;
  }
  .card-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 0.85rem;
    letter-spacing: 0.2em;
    color: var(--texto-dim);
    text-transform: uppercase;
    margin-bottom: 0.75rem;
  }
  .card-value {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2.5rem;
    line-height: 1;
    color: #fff;
  }
  .card-sub { font-size: 0.8rem; color: var(--texto-dim); margin-top: 4px; }

  /* ── BARRAS ── */
  .bar-wrap { margin: 0.5rem 0; }
  .bar-label {
    display: flex; justify-content: space-between;
    font-size: 0.8rem; color: var(--texto-dim);
    margin-bottom: 4px;
  }
  .bar-track {
    height: 8px; background: #111;
    border-radius: 4px; overflow: hidden;
  }
  .bar-fill {
    height: 100%; border-radius: 4px;
    transition: width 0.8s cubic-bezier(0.4,0,0.2,1);
  }
  .bar-vida .bar-fill { background: linear-gradient(90deg, #c0392b, #e74c3c); }
  .bar-exp .bar-fill { background: linear-gradient(90deg, #c9a84c, #f1c40f); }
  .bar-cansancio .bar-fill { background: linear-gradient(90deg, #8e44ad, #9b59b6); }

  /* ── STATS GRID ── */
  .stat-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.75rem; margin-top: 1rem; }
  .stat-item {
    background: #111;
    border-radius: 6px;
    padding: 0.75rem;
    text-align: center;
  }
  .stat-item .val {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.8rem;
    color: #fff;
    display: block;
  }
  .stat-item .lbl { font-size: 0.7rem; color: var(--texto-dim); letter-spacing: 0.1em; }

  /* ── INVENTARIO ── */
  .inv-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 0.75rem;
    margin-top: 1rem;
  }
  .inv-item {
    background: #111;
    border: 1px solid #333;
    border-radius: 8px;
    padding: 0.75rem;
    text-align: center;
    position: relative;
    transition: border-color 0.2s;
  }
  .inv-item:hover { border-color: var(--rojo); }
  .inv-item .item-emoji { font-size: 1.8rem; display: block; }
  .inv-item .item-name { font-size: 0.65rem; color: var(--texto-dim); margin-top: 4px; line-height: 1.3; }
  .inv-item .item-qty {
    position: absolute; top: 4px; right: 6px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.75rem; color: var(--oro);
    font-weight: bold;
  }
  .cat-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 0.9rem;
    letter-spacing: 0.2em;
    color: var(--texto-dim);
    margin: 1.25rem 0 0.5rem;
    padding-bottom: 4px;
    border-bottom: 1px solid #333;
  }

  /* ── MAPA ── */
  .zona-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem; margin-top: 1rem; }
  .zona-card {
    background: #111;
    border: 1px solid #333;
    border-radius: 8px;
    padding: 1rem;
    position: relative;
    transition: all 0.2s;
  }
  .zona-card.actual { border-color: var(--verde-bright); box-shadow: 0 0 12px rgba(76,175,80,0.2); }
  .zona-card.bloqueada { opacity: 0.45; }
  .zona-emoji { font-size: 2rem; display: block; margin-bottom: 6px; }
  .zona-nombre { font-family: 'Bebas Neue', sans-serif; font-size: 1rem; letter-spacing: 0.05em; }
  .zona-desc { font-size: 0.72rem; color: var(--texto-dim); margin-top: 4px; line-height: 1.4; }
  .zona-peligro { margin-top: 8px; font-size: 0.7rem; color: var(--rojo); }
  .zona-badge {
    position: absolute; top: 8px; right: 8px;
    font-size: 0.6rem; padding: 2px 6px;
    border-radius: 3px; font-weight: 700;
    letter-spacing: 0.05em;
  }
  .badge-actual { background: var(--verde); color: #fff; }
  .badge-bloqueada { background: #333; color: var(--texto-dim); }
  .badge-secreta { background: var(--morado); color: #fff; }

  /* ── BASE ── */
  .estructura-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 1rem; margin-top: 1rem; }
  .estructura-card {
    background: #111;
    border: 1px solid #333;
    border-radius: 8px;
    padding: 1rem;
    text-align: center;
  }
  .est-emoji { font-size: 2.2rem; display: block; margin-bottom: 8px; }
  .est-nombre { font-family: 'Bebas Neue', sans-serif; font-size: 1rem; letter-spacing: 0.05em; }
  .est-nivel { font-family: 'Share Tech Mono', monospace; font-size: 0.75rem; color: var(--oro); margin-top: 4px; }
  .est-desc { font-size: 0.7rem; color: var(--texto-dim); margin-top: 6px; line-height: 1.4; }
  .nivel-dots { display: flex; justify-content: center; gap: 4px; margin-top: 8px; }
  .nivel-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: #333;
  }
  .nivel-dot.lleno { background: var(--verde-bright); }

  /* ── LOADING ── */
  .loading {
    display: flex; align-items: center; justify-content: center;
    height: 200px; color: var(--texto-dim);
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.9rem;
    letter-spacing: 0.2em;
  }
  .loading::after {
    content: '';
    animation: dots 1.5s infinite;
  }
  @keyframes dots {
    0%,20% { content: '.'; }
    40%,60% { content: '..'; }
    80%,100% { content: '...'; }
  }

  /* ── SEPARADOR ── */
  .sep { height: 1px; background: #333; margin: 1.25rem 0; }

  /* ── FOOTER ── */
  .footer {
    text-align: center;
    padding: 1rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.7rem;
    color: var(--texto-dim);
    border-top: 1px solid #222;
    margin-top: 2rem;
  }
  .footer span { color: var(--rojo); }
</style>
</head>
<body>

<div class="header">
  <div class="header-avatar">🧟</div>
  <div class="header-info">
    <h1>{{ nombre }}</h1>
    <div class="subtitle">Superviviente del Apocalipsis • Nivel {{ nivel }}</div>
  </div>
  <div class="header-badge">⚔️ {{ kills }} KILLS</div>
</div>

<div class="tabs">
  <button class="tab-btn active" onclick="tab('perfil',this)">👤 PERFIL</button>
  <button class="tab-btn" onclick="tab('inventario',this)">🎒 INVENTARIO</button>
  <button class="tab-btn" onclick="tab('mapa',this)">🗺️ MAPA</button>
  <button class="tab-btn" onclick="tab('base',this)">🏠 BASE</button>
</div>

<div class="content">

  <!-- ── PERFIL ── -->
  <div id="panel-perfil" class="panel active">
    <div class="grid-2" style="margin-top:1rem">
      <div>
        <div class="card">
          <div class="card-title">Estado vital</div>
          <div class="bar-wrap bar-vida">
            <div class="bar-label"><span>❤️ Vida</span><span>{{ vida }}/{{ vida_max }}</span></div>
            <div class="bar-track"><div class="bar-fill" style="width:{{ vida_pct }}%"></div></div>
          </div>
          <div class="bar-wrap bar-exp">
            <div class="bar-label"><span>⭐ EXP</span><span>{{ exp }}/{{ exp_max }}</span></div>
            <div class="bar-track"><div class="bar-fill" style="width:{{ exp_pct }}%"></div></div>
          </div>
          <div class="bar-wrap bar-cansancio">
            <div class="bar-label"><span>😴 Cansancio</span><span>{{ cansancio }}%</span></div>
            <div class="bar-track"><div class="bar-fill" style="width:{{ cansancio }}%"></div></div>
          </div>
        </div>

        <div class="card" style="margin-top:1rem">
          <div class="card-title">Ubicación</div>
          <div style="font-size:1.1rem; margin-top:4px">📍 <strong>{{ zona }}</strong></div>
          <div class="card-sub" style="margin-top:6px">Estado: <strong style="color:{{ estado_color }}">{{ estado }}</strong></div>
        </div>
      </div>

      <div>
        <div class="card">
          <div class="card-title">Estadísticas de combate</div>
          <div class="stat-grid">
            <div class="stat-item"><span class="val">{{ ataque }}</span><span class="lbl">⚔️ ATAQUE</span></div>
            <div class="stat-item"><span class="val">{{ defensa }}</span><span class="lbl">🛡️ DEFENSA</span></div>
            <div class="stat-item"><span class="val">{{ velocidad }}</span><span class="lbl">💨 VELOCIDAD</span></div>
            <div class="stat-item"><span class="val">{{ kills }}</span><span class="lbl">🧟 KILLS</span></div>
            <div class="stat-item"><span class="val">{{ muertes }}</span><span class="lbl">💀 MUERTES</span></div>
            <div class="stat-item"><span class="val">{{ tapas }}</span><span class="lbl">💰 TAPAS</span></div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- ── INVENTARIO ── -->
  <div id="panel-inventario" class="panel">
    {% for cat_nombre, cat_items in inventario_cats.items() %}
      {% if cat_items %}
        <div class="cat-title">{{ cat_nombre }}</div>
        <div class="inv-grid">
          {% for item in cat_items %}
          <div class="inv-item">
            <span class="item-qty">×{{ item.cantidad }}</span>
            <span class="item-emoji">{{ item.emoji }}</span>
            <div class="item-name">{{ item.nombre }}</div>
          </div>
          {% endfor %}
        </div>
      {% endif %}
    {% endfor %}
    {% if not inventario_cats %}
      <div class="loading">MOCHILA VACÍA</div>
    {% endif %}
  </div>

  <!-- ── MAPA ── -->
  <div id="panel-mapa" class="panel">
    <div class="zona-grid" style="margin-top:1rem">
      {% for zona in zonas %}
      <div class="zona-card {{ 'actual' if zona.actual else '' }} {{ 'bloqueada' if zona.bloqueada else '' }}">
        {% if zona.actual %}<span class="zona-badge badge-actual">AQUÍ</span>{% endif %}
        {% if zona.bloqueada %}<span class="zona-badge badge-bloqueada">🔒</span>{% endif %}
        {% if zona.secreta and not zona.bloqueada %}<span class="zona-badge badge-secreta">SECRETO</span>{% endif %}
        <span class="zona-emoji">{{ zona.emoji }}</span>
        <div class="zona-nombre">{{ zona.nombre }}</div>
        <div class="zona-desc">{{ zona.descripcion }}</div>
        <div class="zona-peligro">{{ '⚠️' * zona.peligro if zona.peligro > 0 else '🟢 Seguro' }}</div>
      </div>
      {% endfor %}
    </div>
  </div>

  <!-- ── BASE ── -->
  <div id="panel-base" class="panel">
    {% if base %}
    <div class="card" style="margin-top:1rem">
      <div class="card-title">{{ base.nombre }}</div>
      <div style="display:flex; gap:2rem; margin-top:8px">
        <div><span style="color:var(--texto-dim);font-size:0.8rem">✅ Repelidos</span><br><strong>{{ base.repelidos }}</strong></div>
        <div><span style="color:var(--texto-dim);font-size:0.8rem">💥 Recibidos</span><br><strong>{{ base.recibidos }}</strong></div>
      </div>
    </div>

    <div class="estructura-grid" style="margin-top:1rem">
      {% for est in estructuras %}
      <div class="estructura-card">
        <span class="est-emoji">{{ est.emoji }}</span>
        <div class="est-nombre">{{ est.nombre }}</div>
        <div class="est-nivel">NIVEL {{ est.nivel }}/5</div>
        <div class="est-desc">{{ est.desc }}</div>
        <div class="nivel-dots">
          {% for i in range(5) %}
          <div class="nivel-dot {{ 'lleno' if i < est.nivel else '' }}"></div>
          {% endfor %}
        </div>
      </div>
      {% endfor %}
    </div>
    {% else %}
    <div class="loading">SIN BASE — USA !fundarbase</div>
    {% endif %}
  </div>

</div>

<div class="footer">
  APOCALIPSIS ZOMBIE • SUPERVIVIENTE <span>{{ nombre }}</span> • ACTUALIZADO EN TIEMPO REAL
</div>

<script>
function tab(id, btn) {
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('panel-' + id).classList.add('active');
  btn.classList.add('active');
}
</script>
</body>
</html>"""

HTML_TIENDA = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Tienda — Apocalipsis Zombie</title>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Share+Tech+Mono&family=Barlow:wght@400;600;700&display=swap" rel="stylesheet">
<style>
  :root {
    --rojo:#c0392b; --verde:#2d5a1b; --naranja:#e67e22;
    --gris:#1a1a1a; --gris-mid:#2a2a2a; --gris-light:#333;
    --texto:#e8e0d0; --texto-dim:#8a8070; --oro:#c9a84c;
  }
  * { box-sizing:border-box; margin:0; padding:0; }
  body { background:var(--gris); color:var(--texto); font-family:'Barlow',sans-serif; min-height:100vh; }
  .header {
    background:linear-gradient(135deg,#0d0d0d,#1a0a0a);
    border-bottom:2px solid var(--naranja);
    padding:1.2rem 2rem;
    display:flex; align-items:center; gap:1rem;
  }
  .header h1 { font-family:'Bebas Neue',sans-serif; font-size:2rem; letter-spacing:0.1em; }
  .header .tapas { margin-left:auto; background:var(--verde); padding:6px 14px; border-radius:4px; font-family:'Bebas Neue',sans-serif; font-size:1.1rem; }
  .tabs { display:flex; gap:0; background:#0d0d0d; border-bottom:1px solid #333; overflow-x:auto; scrollbar-width:none; }
  .tab-btn { padding:0.9rem 1.2rem; background:none; border:none; color:var(--texto-dim); font-family:'Bebas Neue',sans-serif; font-size:0.9rem; letter-spacing:0.15em; cursor:pointer; border-bottom:3px solid transparent; white-space:nowrap; transition:all 0.2s; }
  .tab-btn:hover { color:var(--texto); background:rgba(255,255,255,0.03); }
  .tab-btn.active { color:var(--naranja); border-bottom-color:var(--naranja); }
  .content { padding:1.5rem 2rem; max-width:1200px; margin:0 auto; }
  .panel { display:none; }
  .panel.active { display:block; }
  .shop-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(200px,1fr)); gap:1rem; margin-top:1rem; }
  .shop-card {
    background:var(--gris-mid); border:1px solid #333; border-radius:8px;
    padding:1rem; text-align:center; transition:border-color 0.2s;
    display:flex; flex-direction:column; gap:6px;
  }
  .shop-card:hover { border-color:var(--naranja); }
  .shop-card .emoji { font-size:2rem; }
  .shop-card .nombre { font-family:'Bebas Neue',sans-serif; font-size:1rem; letter-spacing:0.05em; }
  .shop-card .desc { font-size:0.7rem; color:var(--texto-dim); line-height:1.4; flex:1; }
  .shop-card .precios { display:flex; justify-content:center; gap:12px; margin-top:6px; }
  .shop-card .precio-c { color:#4caf50; font-size:0.8rem; font-weight:700; }
  .shop-card .precio-v { color:#e74c3c; font-size:0.8rem; font-weight:700; }
  .shop-card .id-tag { font-family:'Share Tech Mono',monospace; font-size:0.65rem; color:var(--texto-dim); background:#111; padding:2px 6px; border-radius:3px; }
  .shop-card .tiene-tag { background:var(--verde); color:#fff; font-size:0.65rem; padding:2px 6px; border-radius:3px; }
  .cmd-box { background:#111; border:1px solid #333; border-radius:6px; padding:1rem; margin-top:1rem; font-family:'Share Tech Mono',monospace; font-size:0.8rem; color:var(--texto-dim); }
  .cmd-box span { color:var(--naranja); }
  .footer { text-align:center; padding:1rem; font-family:'Share Tech Mono',monospace; font-size:0.7rem; color:var(--texto-dim); border-top:1px solid #222; margin-top:2rem; }
  @media(max-width:600px) { .content { padding:1rem; } .shop-grid { grid-template-columns:repeat(auto-fill,minmax(150px,1fr)); } }
</style>
</head>
<body>
<div class="header">
  <div style="font-size:2rem">🏪</div>
  <div>
    <h1>TIENDA DEL REFUGIO</h1>
    <div style="font-family:'Share Tech Mono',monospace;font-size:0.75rem;color:var(--naranja)">{{ nombre }} — Nivel {{ nivel }}</div>
  </div>
  <div class="tapas">💰 {{ tapas }} TAPAS</div>
</div>

<div class="tabs">
  {% for cat_key, (cat_emoji, cat_nombre) in cats.items() %}
    {% if items_por_cat[cat_key] %}
      <button class="tab-btn {% if loop.first %}active{% endif %}" onclick="tab('{{ cat_key }}',this)">{{ cat_emoji }} {{ cat_nombre|upper }}</button>
    {% endif %}
  {% endfor %}
</div>

<div class="content">
  <div class="cmd-box">
    Usa <span>!comprar &lt;id&gt;</span> en Discord para comprar · <span>!vender &lt;id&gt;</span> para vender · <span>!saldo</span> para ver tus tapas
  </div>

  {% for cat_key, (cat_emoji, cat_nombre) in cats.items() %}
    {% if items_por_cat[cat_key] %}
    <div id="panel-{{ cat_key }}" class="panel {% if loop.first %}active{% endif %}">
      <div class="shop-grid">
        {% for item in items_por_cat[cat_key] %}
        <div class="shop-card">
          <div class="emoji">{{ item.emoji }}</div>
          <div class="nombre">{{ item.nombre }}</div>
          <div class="desc">{{ item.descripcion }}</div>
          <div class="precios">
            <span class="precio-c">🛒 {{ item.precio_compra }}💰</span>
            <span class="precio-v">💸 {{ item.precio_venta }}💰</span>
          </div>
          <div style="display:flex;gap:4px;justify-content:center;flex-wrap:wrap">
            <span class="id-tag">{{ item.id }}</span>
            {% if item.tiene > 0 %}<span class="tiene-tag">✅ ×{{ item.tiene }}</span>{% endif %}
          </div>
        </div>
        {% endfor %}
      </div>
    </div>
    {% endif %}
  {% endfor %}
</div>

<div class="footer">TIENDA DEL REFUGIO · APOCALIPSIS ZOMBIE · {{ nombre }}</div>
<script>
function tab(id, btn) {
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('panel-' + id).classList.add('active');
  btn.classList.add('active');
}
</script>
</body>
</html>"""


# ── RUTAS ─────────────────────────────────────────────────────────────────────


TIENDA_HTML = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Tienda del Refugio — Apocalipsis Zombie</title>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Share+Tech+Mono&family=Barlow:wght@400;600;700&display=swap" rel="stylesheet">
<style>
  :root {
    --rojo:#c0392b;--verde:#2d5a1b;--naranja:#e67e22;
    --gris:#1a1a1a;--gris-mid:#2a2a2a;--gris-light:#3a3a3a;
    --texto:#e8e0d0;--texto-dim:#8a8070;--oro:#c9a84c;
  }
  *{box-sizing:border-box;margin:0;padding:0}
  body{background:var(--gris);color:var(--texto);font-family:'Barlow',sans-serif;min-height:100vh}
  .header{background:linear-gradient(135deg,#0d0d0d,#1a0808);border-bottom:2px solid var(--rojo);padding:1.2rem 2rem;display:flex;align-items:center;gap:1rem}
  .header h1{font-family:'Bebas Neue',sans-serif;font-size:2rem;letter-spacing:.1em}
  .header .sub{font-family:'Share Tech Mono',monospace;font-size:.75rem;color:var(--rojo);letter-spacing:.2em}
  .search-bar{padding:.8rem 2rem;background:#111;border-bottom:1px solid #333;display:flex;gap:.75rem;flex-wrap:wrap}
  .search-bar input{background:#1a1a1a;border:1px solid #444;color:var(--texto);padding:.5rem 1rem;border-radius:6px;font-family:'Share Tech Mono',monospace;font-size:.85rem;flex:1;min-width:200px}
  .search-bar input:focus{outline:none;border-color:var(--rojo)}
  .filter-btn{background:var(--gris-mid);border:1px solid #444;color:var(--texto-dim);padding:.4rem 1rem;border-radius:6px;cursor:pointer;font-family:'Bebas Neue',sans-serif;font-size:.85rem;letter-spacing:.1em;transition:all .2s}
  .filter-btn.active,.filter-btn:hover{background:var(--rojo);color:#fff;border-color:var(--rojo)}
  .content{padding:1.5rem 2rem;max-width:1200px;margin:0 auto}
  .cat-title{font-family:'Bebas Neue',sans-serif;font-size:1rem;letter-spacing:.2em;color:var(--texto-dim);margin:1.25rem 0 .75rem;padding-bottom:4px;border-bottom:1px solid #333;text-transform:uppercase}
  .items-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:.75rem}
  .item-card{background:var(--gris-mid);border:1px solid #333;border-radius:8px;padding:1rem;transition:border-color .2s;position:relative}
  .item-card:hover{border-color:var(--rojo)}
  .item-card .emoji{font-size:1.6rem;display:block;margin-bottom:6px}
  .item-card .nombre{font-family:'Bebas Neue',sans-serif;font-size:.95rem;letter-spacing:.05em}
  .item-card .desc{font-size:.7rem;color:var(--texto-dim);margin-top:4px;line-height:1.4}
  .item-card .precios{display:flex;gap:.75rem;margin-top:.6rem;font-family:'Share Tech Mono',monospace;font-size:.75rem}
  .precio-compra{color:#4caf50}
  .precio-venta{color:#ef5350}
  .item-id{position:absolute;top:6px;right:8px;font-family:'Share Tech Mono',monospace;font-size:.65rem;color:var(--texto-dim);background:#111;padding:2px 6px;border-radius:3px}
  .hidden{display:none!important}
  .footer{text-align:center;padding:1rem;font-family:'Share Tech Mono',monospace;font-size:.7rem;color:var(--texto-dim);border-top:1px solid #222;margin-top:2rem}
  @media(max-width:600px){.content{padding:1rem}.items-grid{grid-template-columns:1fr 1fr}}
</style>
</head>
<body>
<div class="header">
  <div>
    <h1>🏪 Tienda del Refugio</h1>
    <div class="sub">COMERCIO SEGURO EN EL APOCALIPSIS</div>
  </div>
</div>
<div class="search-bar">
  <input type="text" id="search" placeholder="Buscar item..." oninput="filtrar()">
  <button class="filter-btn active" onclick="setFiltro('todos',this)">TODOS</button>
  <button class="filter-btn" onclick="setFiltro('consumible',this)">💊 CONSUMIBLES</button>
  <button class="filter-btn" onclick="setFiltro('arma',this)">⚔️ ARMAS</button>
  <button class="filter-btn" onclick="setFiltro('armadura',this)">🛡️ ARMADURAS</button>
  <button class="filter-btn" onclick="setFiltro('material',this)">🔧 MATERIALES</button>
</div>
<div class="content" id="content">
{% for cat_nombre, items in categorias.items() %}
  <div class="cat-title cat-section" data-cat="{{ cat_nombre }}">{{ cat_nombre }}</div>
  <div class="items-grid cat-grid" data-cat="{{ cat_nombre }}">
    {% for item in items %}
    <div class="item-card" data-tipo="{{ item.tipo }}" data-nombre="{{ item.nombre|lower }}">
      <span class="item-id">{{ item.id }}</span>
      <span class="emoji">{{ item.emoji }}</span>
      <div class="nombre">{{ item.nombre }}</div>
      <div class="desc">{{ item.descripcion }}</div>
      <div class="precios">
        {% if item.precio_compra > 0 %}
        <span class="precio-compra">🛒 {{ item.precio_compra }}💰</span>
        {% endif %}
        {% if item.precio_venta > 0 %}
        <span class="precio-venta">💸 {{ item.precio_venta }}💰</span>
        {% endif %}
      </div>
    </div>
    {% endfor %}
  </div>
{% endfor %}
</div>
<div class="footer">APOCALIPSIS ZOMBIE • Usa <strong>!comprar &lt;id&gt;</strong> en Discord para comprar</div>
<script>
let filtroActivo = 'todos';
function setFiltro(f, btn) {
  filtroActivo = f;
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  filtrar();
}
function filtrar() {
  const q = document.getElementById('search').value.toLowerCase();
  document.querySelectorAll('.item-card').forEach(card => {
    const matchTipo = filtroActivo === 'todos' || card.dataset.tipo === filtroActivo;
    const matchSearch = !q || card.dataset.nombre.includes(q) || card.querySelector('.item-id').textContent.includes(q);
    card.classList.toggle('hidden', !(matchTipo && matchSearch));
  });
  // Hide empty sections
  document.querySelectorAll('.cat-grid').forEach(grid => {
    const visible = [...grid.querySelectorAll('.item-card')].some(c => !c.classList.contains('hidden'));
    grid.classList.toggle('hidden', !visible);
    const title = document.querySelector('.cat-title[data-cat="' + grid.dataset.cat + '"]');
    if(title) title.classList.toggle('hidden', !visible);
  });
}
</script>
</body>
</html>"""


@app.route('/perfil/<discord_id>')
def perfil(discord_id):
    if not _db:
        abort(503)

    jugador = _db.get_jugador(discord_id)
    if not jugador:
        abort(404)

    from game_data import ITEMS, ZONAS
    from base_data import ESTRUCTURAS as EST_DATA

    # Stats
    nivel = jugador['nivel']
    exp_max = nivel * 100
    vida_pct = int((jugador['vida'] / max(jugador['vida_max'], 1)) * 100)
    exp_pct = int((jugador['exp'] / max(exp_max, 1)) * 100)
    cansancio = jugador.get('cansancio', 0)

    estado_map = {
        'vivo': ('#4caf50', '🟢 Vivo'),
        'muerto': ('#e74c3c', '💀 Muerto'),
        'en_combate': ('#e67e22', '⚔️ En combate'),
        'atrincherado': ('#c0392b', '🛡️ Atrincherado'),
        'entrenando': ('#3498db', '🏋️ Entrenando'),
    }
    estado_color, estado_txt = estado_map.get(jugador['estado'], ('#aaa', jugador['estado']))

    # Zona actual
    zona_actual = ZONAS.get(jugador['zona'], {})
    zona_nombre = zona_actual.get('nombre', jugador['zona'])

    # Inventario categorizado
    inv = jugador['inventario']
    cats_def = {
        '⚔️ Armas': ['arma', 'arma_fuego', 'cac', 'arma_especial', 'arma_especial'],
        '🛡️ Armaduras': ['armadura'],
        '💊 Consumibles': ['consumible'],
        '🧪 Drogas': ['droga'],
        '🔧 Materiales': ['material'],
        '📡 Gadgets': ['gadget'],
        '🚗 Vehículos': ['vehiculo'],
        '👢 Ropa': ['accesorio'],
        '⭐ Legendarios': ['legendario'],
        '🎁 Eventos': ['evento'],
        '🗺️ Mapas': ['mapa_secreto'],
        '🗃️ Equipamiento': ['equipamiento'],
    }

    inventario_cats = {}
    for cat_nombre, tipos in cats_def.items():
        items_cat = []
        for item_id, cantidad in inv.items():
            if '_dur' in item_id:
                continue
            item_data = ITEMS.get(item_id, {})
            tipo = item_data.get('tipo', '')
            subtipo = item_data.get('subtipo', '')
            if tipo in tipos or subtipo in tipos:
                items_cat.append({
                    'emoji': item_data.get('emoji', '📦'),
                    'nombre': item_data.get('nombre', item_id),
                    'cantidad': cantidad,
                })
        if items_cat:
            inventario_cats[cat_nombre] = items_cat

    # Mapa
    zonas_list = []
    for zona_id, zona_data in ZONAS.items():
        requiere = zona_data.get('requiere_item')
        bloqueada = bool(requiere and inv.get(requiere, 0) == 0)
        zonas_list.append({
            'emoji': zona_data.get('emoji', '📍'),
            'nombre': zona_data.get('nombre', zona_id),
            'descripcion': zona_data.get('descripcion', ''),
            'peligro': zona_data.get('peligro', 0),
            'actual': zona_id == jugador['zona'],
            'bloqueada': bloqueada,
            'secreta': requiere is not None,
        })

    # Base
    base = _db.get_base(discord_id)
    estructuras_render = []
    base_data = None

    if base:
        base_data = {
            'nombre': base['nombre'],
            'repelidos': base['ataques_repelidos'],
            'recibidos': base['ataques_recibidos'],
        }
        est_info = {
            'muro': ('🧱', 'Muro Perimetral', 'Protege de ataques zombie.'),
            'torretas': ('🔫', 'Torretas', 'Disparan automáticamente.'),
            'almacen': ('📦', 'Almacén', 'Protege recursos del robo.'),
            'generador': ('⚡', 'Generador', 'Produce tapas pasivamente.'),
            'hospital_base': ('🏥', 'Enfermería', 'Curación automática al volver.'),
            'laboratorio': ('🔬', 'Laboratorio', 'Bonus de EXP en combate.'),
        }
        for est_id, (emoji, nombre, desc) in est_info.items():
            nivel_est = base['estructuras'].get(est_id, 0)
            estructuras_render.append({
                'emoji': emoji,
                'nombre': nombre,
                'nivel': nivel_est,
                'desc': desc,
            })

    return render_template_string(HTML,
        nombre=jugador['nombre'],
        nivel=nivel,
        vida=jugador['vida'],
        vida_max=jugador['vida_max'],
        vida_pct=vida_pct,
        exp=jugador['exp'],
        exp_max=exp_max,
        exp_pct=exp_pct,
        cansancio=cansancio,
        ataque=jugador['ataque'],
        defensa=jugador['defensa'],
        velocidad=jugador['velocidad'],
        kills=jugador['kills'],
        muertes=jugador['muertes'],
        tapas=jugador['tapas'],
        zona=zona_nombre,
        estado=estado_txt,
        estado_color=estado_color,
        inventario_cats=inventario_cats,
        zonas=zonas_list,
        base=base_data,
        estructuras=estructuras_render,
    )

@app.route('/tienda/<discord_id>')
def tienda(discord_id):
    if not _db:
        abort(503)
    jugador = _db.get_jugador(discord_id)
    if not jugador:
        abort(404)

    from game_data import ITEMS, TIENDA_ITEMS

    cats = {
        "consumible": ("💊", "Consumibles"),
        "arma":       ("⚔️", "Armas"),
        "armadura":   ("🛡️", "Armaduras"),
        "material":   ("🔧", "Materiales"),
        "equipamiento":("🗃️","Equipamiento"),
        "droga":      ("💉", "Drogas"),
        "gadget":     ("📡", "Gadgets"),
        "vehiculo":   ("🚗", "Vehículos"),
        "accesorio":  ("👢", "Accesorios"),
    }

    items_por_cat = {k: [] for k in cats}
    for item_id in TIENDA_ITEMS:
        item = ITEMS.get(item_id)
        if not item:
            continue
        tipo = item.get("tipo", "otro")
        if tipo in items_por_cat:
            tiene = jugador["inventario"].get(item_id, 0)
            items_por_cat[tipo].append({
                "id": item_id,
                "nombre": item.get("nombre", item_id),
                "emoji": item.get("emoji", "📦"),
                "descripcion": item.get("descripcion", ""),
                "precio_compra": item.get("precio_compra", 0),
                "precio_venta": item.get("precio_venta", 0),
                "tiene": tiene,
            })

    return render_template_string(HTML_TIENDA,
        nombre=jugador["nombre"],
        tapas=jugador["tapas"],
        nivel=jugador["nivel"],
        discord_id=discord_id,
        items_por_cat=items_por_cat,
        cats=cats,
    )



@app.route('/tienda')
def tienda():
    from game_data import ITEMS, TIENDA_ITEMS

    cats_order = [
        ("💊 Consumibles", ["consumible"]),
        ("⚔️ Armas", ["arma"]),
        ("🛡️ Armaduras", ["armadura"]),
        ("🔧 Materiales", ["material"]),
        ("🎒 Equipamiento", ["equipamiento", "accesorio", "vehiculo", "gadget"]),
        ("💊 Drogas", ["droga"]),
    ]

    categorias = {}
    for cat_nombre, tipos in cats_order:
        items_lista = []
        for item_id in TIENDA_ITEMS:
            item = ITEMS.get(item_id)
            if not item:
                continue
            tipo = item.get("tipo", "")
            subtipo = item.get("subtipo", "")
            if tipo in tipos or subtipo in tipos:
                precio_c = item.get("precio_compra", 0)
                if precio_c > 0:
                    items_lista.append({
                        "id": item_id,
                        "emoji": item.get("emoji", "📦"),
                        "nombre": item.get("nombre", item_id),
                        "descripcion": item.get("descripcion", ""),
                        "precio_compra": precio_c,
                        "precio_venta": item.get("precio_venta", 0),
                        "tipo": tipo,
                    })
        if items_lista:
            categorias[cat_nombre] = items_lista

    return render_template_string(TIENDA_HTML, categorias=categorias)



@app.route('/tienda/<token>')
def tienda_auth(token):
    """Tienda con token de autenticación."""
    discord_id = validar_token(token)
    if not discord_id:
        return render_template_string(ERROR_HTML, mensaje="Token inválido o expirado. Usa !tienda en Discord para obtener uno nuevo."), 403

    from game_data import ITEMS, TIENDA_ITEMS
    jugador = _db.get_jugador(discord_id) if _db else None

    cats_order = [
        ("💊 Consumibles", ["consumible"]),
        ("⚔️ Armas", ["arma"]),
        ("🛡️ Armaduras", ["armadura"]),
        ("🔧 Materiales", ["material"]),
        ("🎒 Equipamiento", ["equipamiento", "accesorio", "vehiculo", "gadget"]),
        ("💊 Drogas", ["droga"]),
    ]

    categorias = {}
    for cat_nombre, tipos in cats_order:
        items_lista = []
        for item_id in TIENDA_ITEMS:
            item = ITEMS.get(item_id)
            if not item:
                continue
            tipo = item.get("tipo", "")
            subtipo = item.get("subtipo", "")
            if tipo in tipos or subtipo in tipos:
                precio_c = item.get("precio_compra", 0)
                if precio_c > 0:
                    items_lista.append({
                        "id": item_id,
                        "emoji": item.get("emoji", "📦"),
                        "nombre": item.get("nombre", item_id),
                        "descripcion": item.get("descripcion", ""),
                        "precio_compra": precio_c,
                        "precio_venta": item.get("precio_venta", 0),
                        "tipo": tipo,
                    })
        if items_lista:
            categorias[cat_nombre] = items_lista

    tapas = jugador["tapas"] if jugador else 0
    nombre = jugador["nombre"] if jugador else "Superviviente"
    zona = jugador["zona"] if jugador else "?"

    return render_template_string(
        TIENDA_AUTH_HTML,
        categorias=categorias,
        tapas=tapas,
        nombre=nombre,
        zona=zona,
        token=token,
        puede_comprar=(zona == "refugio"),
    )


@app.route('/api/comprar', methods=['POST'])
def api_comprar():
    """API para comprar desde la web."""
    from flask import request, jsonify
    from game_data import ITEMS, TIENDA_ITEMS

    data = request.get_json()
    if not data:
        return jsonify({"ok": False, "error": "Datos inválidos"}), 400

    token = data.get("token", "")
    item_id = data.get("item_id", "").lower()
    cantidad = int(data.get("cantidad", 1))

    discord_id = validar_token(token)
    if not discord_id:
        return jsonify({"ok": False, "error": "Token inválido o expirado"}), 403

    if not _db:
        return jsonify({"ok": False, "error": "Base de datos no disponible"}), 503

    jugador = _db.get_jugador(discord_id)
    if not jugador:
        return jsonify({"ok": False, "error": "Jugador no encontrado"}), 404

    if jugador["zona"] != "refugio":
        return jsonify({"ok": False, "error": "Solo puedes comprar en el Refugio Central"}), 400

    if item_id not in TIENDA_ITEMS:
        return jsonify({"ok": False, "error": "Item no disponible en tienda"}), 400

    item = ITEMS.get(item_id)
    if not item:
        return jsonify({"ok": False, "error": "Item no encontrado"}), 400

    precio_total = item.get("precio_compra", 0) * cantidad
    if precio_total == 0:
        return jsonify({"ok": False, "error": "Este item no se puede comprar"}), 400

    if jugador["tapas"] < precio_total:
        return jsonify({"ok": False, "error": f"Tapas insuficientes. Necesitas {precio_total}, tienes {jugador['tapas']}"}), 400

    _db.update_jugador(discord_id, tapas=jugador["tapas"] - precio_total)
    _db.add_item_inventario(discord_id, item_id, cantidad)

    jugador_nuevo = _db.get_jugador(discord_id)
    return jsonify({
        "ok": True,
        "mensaje": f"Compraste {item.get('nombre', item_id)} x{cantidad}",
        "tapas_restantes": jugador_nuevo["tapas"],
    })


@app.route('/api/jugador/<discord_id>')
def api_jugador(discord_id):
    """API JSON para el jugador (uso interno)."""
    if not _db:
        abort(503)
    jugador = _db.get_jugador(discord_id)
    if not jugador:
        abort(404)
    # No devolver inventario completo por seguridad
    return jsonify({
        'nombre': jugador['nombre'],
        'nivel': jugador['nivel'],
        'vida': jugador['vida'],
        'vida_max': jugador['vida_max'],
        'tapas': jugador['tapas'],
        'kills': jugador['kills'],
        'zona': jugador['zona'],
        'estado': jugador['estado'],
    })


ERROR_HTML = r"""<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8"><title>Error</title>
<style>body{background:#111;color:#e8e0d0;font-family:monospace;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}
.box{background:#1a1a1a;border:1px solid #c0392b;padding:2rem;border-radius:8px;text-align:center;max-width:400px}
h2{color:#c0392b;font-size:1.5rem;margin-bottom:1rem}p{color:#8a8070;line-height:1.6}</style>
</head><body><div class="box"><h2>⚠️ {{ mensaje }}</h2>
<p>Vuelve a Discord y usa <strong>!tienda</strong> para obtener un enlace válido.</p></div></body></html>"""

TIENDA_AUTH_HTML = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Tienda del Refugio</title>
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Share+Tech+Mono&family=Barlow:wght@400;600;700&display=swap" rel="stylesheet">
<style>
  :root{--rojo:#c0392b;--verde:#27ae60;--gris:#1a1a1a;--gris-mid:#2a2a2a;--texto:#e8e0d0;--texto-dim:#8a8070;--oro:#c9a84c}
  *{box-sizing:border-box;margin:0;padding:0}
  body{background:var(--gris);color:var(--texto);font-family:'Barlow',sans-serif;min-height:100vh}
  .header{background:linear-gradient(135deg,#0d0d0d,#1a0808);border-bottom:2px solid var(--rojo);padding:1rem 1.5rem;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:.75rem}
  .header-left h1{font-family:'Bebas Neue',sans-serif;font-size:1.8rem;letter-spacing:.1em}
  .header-left .sub{font-family:'Share Tech Mono',monospace;font-size:.7rem;color:var(--rojo);letter-spacing:.15em}
  .header-right{background:#111;border:1px solid #333;border-radius:8px;padding:.6rem 1rem;font-family:'Share Tech Mono',monospace;font-size:.8rem;text-align:right}
  .tapas{color:var(--oro);font-size:1.1rem;font-weight:bold}
  .zona-ok{color:var(--verde);font-size:.7rem;margin-top:2px}
  .zona-no{color:var(--rojo);font-size:.7rem;margin-top:2px}
  .search-bar{padding:.75rem 1.5rem;background:#111;border-bottom:1px solid #333;display:flex;gap:.5rem;flex-wrap:wrap}
  .search-bar input{background:#1a1a1a;border:1px solid #444;color:var(--texto);padding:.45rem .9rem;border-radius:6px;font-family:'Share Tech Mono',monospace;font-size:.8rem;flex:1;min-width:160px}
  .search-bar input:focus{outline:none;border-color:var(--rojo)}
  .filter-btn{background:var(--gris-mid);border:1px solid #444;color:var(--texto-dim);padding:.35rem .8rem;border-radius:6px;cursor:pointer;font-family:'Bebas Neue',sans-serif;font-size:.8rem;letter-spacing:.1em;transition:all .15s}
  .filter-btn.active,.filter-btn:hover{background:var(--rojo);color:#fff;border-color:var(--rojo)}
  .content{padding:1rem 1.5rem;max-width:1200px;margin:0 auto}
  .cat-title{font-family:'Bebas Neue',sans-serif;font-size:.9rem;letter-spacing:.2em;color:var(--texto-dim);margin:1rem 0 .5rem;padding-bottom:3px;border-bottom:1px solid #333}
  .items-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:.6rem}
  .item-card{background:var(--gris-mid);border:1px solid #333;border-radius:8px;padding:.85rem;transition:border-color .2s;position:relative}
  .item-card:hover{border-color:var(--rojo)}
  .item-card .emoji{font-size:1.5rem;display:block;margin-bottom:4px}
  .item-card .nombre{font-family:'Bebas Neue',sans-serif;font-size:.9rem;letter-spacing:.04em}
  .item-card .desc{font-size:.68rem;color:var(--texto-dim);margin-top:3px;line-height:1.35}
  .item-card .precio-row{display:flex;align-items:center;justify-content:space-between;margin-top:.6rem}
  .precio{font-family:'Share Tech Mono',monospace;font-size:.8rem;color:var(--oro)}
  .btn-comprar{background:var(--rojo);color:#fff;border:none;padding:.3rem .7rem;border-radius:5px;font-family:'Bebas Neue',sans-serif;font-size:.8rem;letter-spacing:.08em;cursor:pointer;transition:background .15s}
  .btn-comprar:hover{background:#96281b}
  .btn-comprar:disabled{background:#444;cursor:not-allowed;color:#666}
  .item-id{position:absolute;top:5px;right:7px;font-family:'Share Tech Mono',monospace;font-size:.6rem;color:var(--texto-dim);background:#111;padding:1px 5px;border-radius:3px}
  .hidden{display:none!important}
  /* Toast */
  #toast{position:fixed;bottom:1.5rem;right:1.5rem;background:#1a1a1a;border:1px solid var(--verde);color:var(--texto);padding:.75rem 1.25rem;border-radius:8px;font-family:'Share Tech Mono',monospace;font-size:.8rem;opacity:0;transition:opacity .3s;pointer-events:none;max-width:300px;z-index:999}
  #toast.error{border-color:var(--rojo)}
  #toast.show{opacity:1}
  .footer{text-align:center;padding:1rem;font-family:'Share Tech Mono',monospace;font-size:.65rem;color:var(--texto-dim);border-top:1px solid #222;margin-top:1.5rem}
  @media(max-width:580px){.items-grid{grid-template-columns:1fr 1fr}.header{padding:.75rem 1rem}}
</style>
</head>
<body>
<div class="header">
  <div class="header-left">
    <h1>🏪 Tienda del Refugio</h1>
    <div class="sub">SESIÓN: {{ nombre }} • TOKEN VÁLIDO 15 MIN</div>
  </div>
  <div class="header-right">
    <div class="tapas" id="tapas-display">💰 {{ tapas }} tapas</div>
    {% if puede_comprar %}
    <div class="zona-ok">✅ En el refugio — puedes comprar</div>
    {% else %}
    <div class="zona-no">❌ No estás en el refugio — ve a !explorar refugio</div>
    {% endif %}
  </div>
</div>

<div class="search-bar">
  <input type="text" id="search" placeholder="Buscar item o ID..." oninput="filtrar()">
  <button class="filter-btn active" onclick="setFiltro('todos',this)">TODOS</button>
  <button class="filter-btn" onclick="setFiltro('consumible',this)">💊</button>
  <button class="filter-btn" onclick="setFiltro('arma',this)">⚔️</button>
  <button class="filter-btn" onclick="setFiltro('armadura',this)">🛡️</button>
  <button class="filter-btn" onclick="setFiltro('material',this)">🔧</button>
</div>

<div class="content">
{% for cat_nombre, items in categorias.items() %}
  <div class="cat-title cat-hdr" data-cat="{{ loop.index }}">{{ cat_nombre }}</div>
  <div class="items-grid cat-grid" data-cat="{{ loop.index }}">
    {% for item in items %}
    <div class="item-card" data-tipo="{{ item.tipo }}" data-nombre="{{ item.nombre|lower }}" data-id="{{ item.id }}">
      <span class="item-id">{{ item.id }}</span>
      <span class="emoji">{{ item.emoji }}</span>
      <div class="nombre">{{ item.nombre }}</div>
      <div class="desc">{{ item.descripcion }}</div>
      <div class="precio-row">
        <span class="precio">{{ item.precio_compra }}💰</span>
        {% if puede_comprar %}
        <button class="btn-comprar" onclick="comprar('{{ item.id }}','{{ item.nombre }}',{{ item.precio_compra }})">COMPRAR</button>
        {% else %}
        <button class="btn-comprar" disabled>NO DISPONIBLE</button>
        {% endif %}
      </div>
    </div>
    {% endfor %}
  </div>
{% endfor %}
</div>

<div id="toast"></div>
<div class="footer">APOCALIPSIS ZOMBIE • Sesión expira en 15 min • Recarga la página si expira</div>

<script>
const TOKEN = "{{ token }}";
let tapasActuales = {{ tapas }};

async function comprar(itemId, nombre, precio) {
  if(tapasActuales < precio) {
    showToast("❌ No tienes suficientes tapas", true);
    return;
  }
  const btn = event.target;
  btn.disabled = true;
  btn.textContent = "...";
  try {
    const r = await fetch('/api/comprar', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({token: TOKEN, item_id: itemId, cantidad: 1})
    });
    const data = await r.json();
    if(data.ok) {
      tapasActuales = data.tapas_restantes;
      document.getElementById('tapas-display').textContent = "💰 " + tapasActuales + " tapas";
      showToast("✅ " + data.mensaje);
    } else {
      showToast("❌ " + data.error, true);
    }
  } catch(e) {
    showToast("❌ Error de conexión", true);
  }
  btn.disabled = false;
  btn.textContent = "COMPRAR";
}

let filtroActivo = 'todos';
function setFiltro(f, btn) {
  filtroActivo = f;
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  filtrar();
}
function filtrar() {
  const q = document.getElementById('search').value.toLowerCase();
  document.querySelectorAll('.item-card').forEach(c => {
    const matchTipo = filtroActivo === 'todos' || c.dataset.tipo === filtroActivo;
    const matchQ = !q || c.dataset.nombre.includes(q) || c.dataset.id.includes(q);
    c.classList.toggle('hidden', !(matchTipo && matchQ));
  });
  document.querySelectorAll('.cat-grid').forEach(g => {
    const vis = [...g.querySelectorAll('.item-card')].some(c => !c.classList.contains('hidden'));
    g.classList.toggle('hidden', !vis);
    const h = document.querySelector('.cat-hdr[data-cat="' + g.dataset.cat + '"]');
    if(h) h.classList.toggle('hidden', !vis);
  });
}

let toastTimer;
function showToast(msg, isError=false) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = 'show' + (isError ? ' error' : '');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.className = '', 3000);
}
</script>
</body>
</html>"""


@app.route('/')
def index():
    return '<h2 style="font-family:monospace;padding:2rem;background:#111;color:#c0392b;min-height:100vh">🧟 Apocalipsis Zombie — Bot activo.<br><br><small style="color:#666">Usa !perfil_web en Discord para ver tu ficha.</small></h2>'


def run_webapp():
    port = int(os.environ.get('WEB_PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)


def start_in_thread():
    t = threading.Thread(target=run_webapp, daemon=True)
    t.start()

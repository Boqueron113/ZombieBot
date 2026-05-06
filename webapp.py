"""
webapp.py — Servidor web Flask para el dashboard del bot zombie
Se ejecuta en paralelo con el bot en Railway.
"""
from flask import Flask, render_template_string, jsonify, abort
import threading
import os
import json

app = Flask(__name__)

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

# ── RUTAS ─────────────────────────────────────────────────────────────────────

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

@app.route('/')
def index():
    return '<h2 style="font-family:monospace;padding:2rem;background:#111;color:#c0392b;min-height:100vh">🧟 Apocalipsis Zombie — Bot activo.<br><br><small style="color:#666">Usa !perfil_web en Discord para ver tu ficha.</small></h2>'


def run_webapp():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)


def start_in_thread():
    t = threading.Thread(target=run_webapp, daemon=True)
    t.start()

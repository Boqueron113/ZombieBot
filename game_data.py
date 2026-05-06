"""
game_data.py — Datos completos del juego
Zonas, Zombies, Items (base + extra), Tienda, Drops, Eventos
"""
import random

# ═══════════════════════════════════════════════════════════════════════════════
# ZONAS DEL MAPA
# ═══════════════════════════════════════════════════════════════════════════════

ZONAS = {
    "refugio": {
        "nombre": "🏚️ Refugio Central",
        "descripcion": "El único lugar seguro que queda. Aquí puedes comerciar y descansar.",
        "peligro": 0,
        "zombies": [],
        "recursos": ["venda", "comida"],
        "color": 0x2d5a1b,
        "emoji": "🏚️",
        "nivel_min": 1,
        "requiere_item": None,
    },
    "hospital": {
        "nombre": "🏥 Hospital San Rafael",
        "descripcion": "Lleno de suministros médicos, pero infestado de zombies mutados.",
        "peligro": 2,
        "zombies": ["zombie_caminante", "zombie_enfermero", "zombie_doctor"],
        "recursos": ["venda", "morfina", "jeringilla"],
        "color": 0xc0392b,
        "emoji": "🏥",
        "nivel_min": 1,
        "requiere_item": None,
    },
    "supermercado": {
        "nombre": "🛒 Supermercado Vivo+",
        "descripcion": "Un antiguo supermercado con comida en conserva. Peligro moderado.",
        "peligro": 2,
        "zombies": ["zombie_caminante", "zombie_gordo", "zombie_corredor"],
        "recursos": ["comida", "agua", "conservas"],
        "color": 0xe67e22,
        "emoji": "🛒",
        "nivel_min": 1,
        "requiere_item": None,
    },
    "armeria": {
        "nombre": "🔫 Armería Municipal",
        "descripcion": "Antigua armería policial. Munición y armas, pero muy peligrosa.",
        "peligro": 3,
        "zombies": ["zombie_policia", "zombie_corredor", "zombie_blindado"],
        "recursos": ["municion", "pistola", "rifle"],
        "color": 0x7f8c8d,
        "emoji": "🔫",
        "nivel_min": 2,
        "requiere_item": None,
    },
    "universidad": {
        "nombre": "🏛️ Universidad Muerta",
        "descripcion": "Campus lleno de zombies estudiantes. Hay materiales de laboratorio.",
        "peligro": 3,
        "zombies": ["zombie_caminante", "zombie_corredor", "zombie_quimico"],
        "recursos": ["municion", "explosivo", "venda"],
        "color": 0x8e44ad,
        "emoji": "🏛️",
        "nivel_min": 2,
        "requiere_item": None,
    },
    "fabrica": {
        "nombre": "🏭 Fábrica Abandonada",
        "descripcion": "Zona industrial peligrosísima. Solo para supervivientes experimentados.",
        "peligro": 5,
        "zombies": ["zombie_industrial", "zombie_blindado", "zombie_titan"],
        "recursos": ["piezas_metal", "explosivo", "rifle"],
        "color": 0x2c3e50,
        "emoji": "🏭",
        "nivel_min": 3,
        "requiere_item": None,
    },
    "cementerio": {
        "nombre": "⚰️ Cementerio de los Olvidados",
        "descripcion": "El origen del brote. Zombies de todo tipo, algunos de hace años.",
        "peligro": 5,
        "zombies": ["zombie_anciano", "zombie_titan", "zombie_jefe"],
        "recursos": ["reliquia", "municion", "morfina"],
        "color": 0x1a252f,
        "emoji": "⚰️",
        "nivel_min": 4,
        "requiere_item": None,
    },

    # ── ZONAS SECRETAS — requieren mapa para acceder ──────────────────────────
    "bunker": {
        "nombre": "🔒 Búnker Secreto",
        "descripcion": "Un refugio subterráneo del gobierno. Sellado desde el día cero. Hay recursos únicos dentro.",
        "peligro": 4,
        "zombies": ["zombie_blindado", "zombie_quimico", "zombie_titan"],
        "recursos": ["morfina", "explosivo", "piezas_metal", "jeringilla"],
        "color": 0x4a235a,
        "emoji": "🔒",
        "nivel_min": 3,
        "requiere_item": "mapa_bunker",
    },
    "base_militar": {
        "nombre": "🪖 Base Militar Abandonada",
        "descripcion": "Instalación militar al norte de la ciudad. Armamento pesado y zombies soldado.",
        "peligro": 5,
        "zombies": ["zombie_policia", "zombie_blindado", "zombie_titan", "zombie_jefe"],
        "recursos": ["rifle", "explosivo", "municion", "chaleco_kevlar"],
        "color": 0x1e4d2b,
        "emoji": "🪖",
        "nivel_min": 4,
        "requiere_item": "mapa_militar",
    },
    "laboratorio": {
        "nombre": "🧬 Laboratorio Secreto",
        "descripcion": "Aquí comenzó todo. El laboratorio donde se creó el virus. Peligro extremo.",
        "peligro": 5,
        "zombies": ["zombie_quimico", "zombie_doctor", "zombie_titan", "zombie_jefe"],
        "recursos": ["jeringilla", "morfina", "reliquia", "explosivo"],
        "color": 0x0d3b47,
        "emoji": "🧬",
        "nivel_min": 5,
        "requiere_item": "mapa_laboratorio",
    },
    "aeropuerto": {
        "nombre": "✈️ Aeropuerto Internacional",
        "descripcion": "Terminal sellada desde el primer día. Miles de infectados atrapados dentro.",
        "peligro": 4,
        "zombies": ["zombie_corredor", "zombie_gordo", "zombie_blindado"],
        "recursos": ["municion", "comida", "piezas_metal", "conservas"],
        "color": 0x1a6b8a,
        "emoji": "✈️",
        "nivel_min": 3,
        "requiere_item": "mapa_aeropuerto",
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# ZOMBIES
# ═══════════════════════════════════════════════════════════════════════════════

ZOMBIES = {
    "zombie_caminante": {
        "nombre": "🧟 Caminante",
        "vida": 30,
        "ataque": 8,
        "defensa": 2,
        "exp": 15,
        "tapas": (2, 8),
        "drop": {"municion": 0.3, "venda": 0.2, "comida": 0.25, "tornillos": 0.2, "madera": 0.15},
        "descripcion": "Lento pero implacable. El zombie más común."
    },
    "zombie_corredor": {
        "nombre": "💨 Corredor",
        "vida": 25,
        "ataque": 14,
        "defensa": 1,
        "exp": 25,
        "tapas": (5, 15),
        "drop": {"municion": 0.4, "comida": 0.2, "cinta_adhesiva": 0.2, "tela": 0.15},
        "descripcion": "Rápido y agresivo. Ataca antes de que puedas reaccionar."
    },
    "zombie_gordo": {
        "nombre": "🐷 Barrigón",
        "vida": 70,
        "ataque": 12,
        "defensa": 8,
        "exp": 35,
        "tapas": (8, 20),
        "drop": {"comida": 0.5, "conservas": 0.3, "venda": 0.2, "cuero": 0.25, "tela": 0.2},
        "descripcion": "Lento pero con mucha vida. Muy difícil de matar."
    },
    "zombie_policia": {
        "nombre": "👮 Poli Zombie",
        "vida": 45,
        "ataque": 16,
        "defensa": 6,
        "exp": 40,
        "tapas": (10, 25),
        "drop": {"municion": 0.6, "revolver": 0.08, "pistola": 0.05, "venda": 0.2, "municion_pesada": 0.3},
        "descripcion": "Aún lleva el chaleco antibalas. Armado y peligroso."
    },
    "zombie_enfermero": {
        "nombre": "🩺 Enfermero Zombie",
        "vida": 35,
        "ataque": 10,
        "defensa": 3,
        "exp": 30,
        "tapas": (6, 18),
        "drop": {"venda": 0.6, "morfina": 0.3, "jeringilla": 0.2, "botiquin": 0.25, "quimico_base": 0.15},
        "descripcion": "Fue médico. Ahora infecta en lugar de curar."
    },
    "zombie_doctor": {
        "nombre": "🥼 Doctor Zombie",
        "vida": 50,
        "ataque": 18,
        "defensa": 5,
        "exp": 50,
        "tapas": (12, 30),
        "drop": {"morfina": 0.5, "jeringilla": 0.4, "adrenalina": 0.2, "antidoto": 0.15},
        "descripcion": "El jefe del hospital. Muy peligroso."
    },
    "zombie_blindado": {
        "nombre": "🛡️ Blindado",
        "vida": 90,
        "ataque": 20,
        "defensa": 15,
        "exp": 70,
        "tapas": (20, 40),
        "drop": {"piezas_metal": 0.4, "municion_pesada": 0.35, "escopeta": 0.05, "cable": 0.2, "tornillos": 0.3},
        "descripcion": "Cubierto de metal. Necesitas buenas armas para atravesarlo."
    },
    "zombie_quimico": {
        "nombre": "☢️ Químico",
        "vida": 40,
        "ataque": 22,
        "defensa": 4,
        "exp": 55,
        "tapas": (15, 35),
        "drop": {"explosivo": 0.3, "quimico_base": 0.4, "gasolina": 0.3, "polvo_negro": 0.35},
        "descripcion": "Mutado por químicos. Sus ataques envenenan."
    },
    "zombie_industrial": {
        "nombre": "⚙️ Industrial",
        "vida": 80,
        "ataque": 25,
        "defensa": 10,
        "exp": 80,
        "tapas": (25, 50),
        "drop": {"piezas_metal": 0.6, "cable": 0.4, "bateria": 0.3, "sierra_circular": 0.04, "tornillos": 0.4},
        "descripcion": "Enorme obrero zombificado. Fuerza brutal."
    },
    "zombie_anciano": {
        "nombre": "💀 Anciano Zombie",
        "vida": 60,
        "ataque": 15,
        "defensa": 5,
        "exp": 60,
        "tapas": (10, 30),
        "drop": {"reliquia": 0.4, "venda": 0.3, "morfina": 0.2, "katana": 0.03, "cuero": 0.3},
        "descripcion": "Lleva años muerto. Muy resistente a la descomposición."
    },
    "zombie_titan": {
        "nombre": "👹 Titán",
        "vida": 150,
        "ataque": 35,
        "defensa": 20,
        "exp": 150,
        "tapas": (50, 100),
        "drop": {"francotirador": 0.08, "subfusil": 0.06, "explosivo": 0.4, "piezas_metal": 0.5, "componentes_electronicos": 0.3},
        "descripcion": "Una bestia enorme. Solo los más fuertes pueden sobrevivir."
    },
    "zombie_jefe": {
        "nombre": "☠️ Paciente Cero",
        "vida": 300,
        "ataque": 50,
        "defensa": 30,
        "exp": 400,
        "tapas": (150, 300),
        "drop": {"francotirador": 0.3, "exotraje": 0.1, "chaleco_kevlar": 0.3, "adrenalina": 0.5, "minigun": 0.05, "mapa_laboratorio": 0.15},
        "descripcion": "El primer infectado. El origen de todo. Solo para héroes."
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# ITEMS — BASE
# ═══════════════════════════════════════════════════════════════════════════════

ITEMS = {
    # Consumibles
    "venda": {
        "nombre": "🩹 Venda",
        "tipo": "consumible",
        "efecto": "vida",
        "valor": 25,
        "descripcion": "Recupera 25 puntos de vida.",
        "precio_compra": 15,
        "precio_venta": 7,
        "emoji": "🩹"
    },
    "morfina": {
        "nombre": "💉 Morfina",
        "tipo": "consumible",
        "efecto": "vida",
        "valor": 60,
        "descripcion": "Recupera 60 puntos de vida.",
        "precio_compra": 40,
        "precio_venta": 20,
        "emoji": "💉"
    },
    "jeringilla": {
        "nombre": "🔬 Jeringilla Experimental",
        "tipo": "consumible",
        "efecto": "vida",
        "valor": 100,
        "descripcion": "Recupera toda la vida. Muy rara.",
        "precio_compra": 100,
        "precio_venta": 50,
        "emoji": "🔬"
    },
    "comida": {
        "nombre": "🥫 Comida",
        "tipo": "consumible",
        "efecto": "vida",
        "valor": 10,
        "descripcion": "Recupera 10 puntos de vida.",
        "precio_compra": 8,
        "precio_venta": 3,
        "emoji": "🥫"
    },
    "conservas": {
        "nombre": "🫙 Conservas",
        "tipo": "consumible",
        "efecto": "vida",
        "valor": 20,
        "descripcion": "Recupera 20 puntos de vida.",
        "precio_compra": 12,
        "precio_venta": 5,
        "emoji": "🫙"
    },
    "agua": {
        "nombre": "💧 Agua Purificada",
        "tipo": "consumible",
        "efecto": "vida",
        "valor": 15,
        "descripcion": "Recupera 15 puntos de vida.",
        "precio_compra": 10,
        "precio_venta": 4,
        "emoji": "💧"
    },
    # Armas
    "pistola": {
        "nombre": "🔫 Pistola",
        "tipo": "arma",
        "bonus_ataque": 10,
        "descripcion": "Arma básica de fuego. +10 ataque.",
        "precio_compra": 80,
        "precio_venta": 40,
        "emoji": "🔫"
    },
    "hacha": {
        "nombre": "🪓 Hacha",
        "tipo": "arma",
        "bonus_ataque": 15,
        "descripcion": "Arma cuerpo a cuerpo potente. +15 ataque.",
        "precio_compra": 60,
        "precio_venta": 30,
        "emoji": "🪓"
    },
    "rifle": {
        "nombre": "🎯 Rifle",
        "tipo": "arma",
        "bonus_ataque": 25,
        "descripcion": "Arma larga de alta potencia. +25 ataque.",
        "precio_compra": 200,
        "precio_venta": 100,
        "emoji": "🎯"
    },
    "explosivo": {
        "nombre": "💣 Explosivo",
        "tipo": "arma_especial",
        "bonus_ataque": 50,
        "descripcion": "Daño masivo de área. Un solo uso.",
        "precio_compra": 150,
        "precio_venta": 75,
        "emoji": "💣"
    },
    # Armaduras
    "chaleco_kevlar": {
        "nombre": "🦺 Chaleco Kevlar",
        "tipo": "armadura",
        "bonus_defensa": 15,
        "descripcion": "Chaleco antibalas. +15 defensa.",
        "precio_compra": 180,
        "precio_venta": 90,
        "emoji": "🦺"
    },
    # Materiales
    "municion": {
        "nombre": "🔶 Munición",
        "tipo": "material",
        "descripcion": "Balas para armas de fuego.",
        "precio_compra": 5,
        "precio_venta": 2,
        "emoji": "🔶"
    },
    "piezas_metal": {
        "nombre": "⚙️ Piezas de Metal",
        "tipo": "material",
        "descripcion": "Útiles para mejoras y trueques.",
        "precio_compra": 10,
        "precio_venta": 5,
        "emoji": "⚙️"
    },
    "reliquia": {
        "nombre": "🏺 Reliquia del Cementerio",
        "tipo": "material",
        "descripcion": "Objeto misterioso de alto valor.",
        "precio_compra": 0,
        "precio_venta": 60,
        "emoji": "🏺"
    },
    # Equipamiento normal
    "mochila_grande": {
        "nombre": "🎒 Mochila Grande",
        "tipo": "equipamiento",
        "descripcion": "Permite llevar más objetos.",
        "precio_compra": 100,
        "precio_venta": 50,
        "emoji": "🎒"
    },
    "mochila_tactica": {
        "nombre": "🪖 Mochila Táctica",
        "tipo": "equipamiento",
        "descripcion": "Mochila militar de alta capacidad.",
        "precio_compra": 200,
        "precio_venta": 100,
        "emoji": "🪖"
    },
    "mapa_detallado": {
        "nombre": "🗺️ Mapa Detallado",
        "tipo": "equipamiento",
        "descripcion": "Mejora las recompensas de exploración.",
        "precio_compra": 120,
        "precio_venta": 60,
        "emoji": "🗺️"
    },


    # ── ARMAS DE FUEGO ────────────────────────────────────────────────────────
    "revolver": {
        "nombre": "🔫 Revólver",
        "tipo": "arma",
        "subtipo": "arma_fuego",
        "bonus_ataque": 12,
        "descripcion": "Revólver de 6 balas. Fiable y silencioso. +12 ataque.",
        "precio_compra": 90,
        "precio_venta": 45,
        "emoji": "🔫"
    },
    "escopeta": {
        "nombre": "💥 Escopeta",
        "tipo": "arma",
        "subtipo": "arma_fuego",
        "bonus_ataque": 30,
        "descripcion": "Devastadora a corta distancia. +30 ataque.",
        "precio_compra": 250,
        "precio_venta": 125,
        "emoji": "💥"
    },
    "subfusil": {
        "nombre": "🔰 Subfusil",
        "tipo": "arma",
        "subtipo": "arma_fuego",
        "bonus_ataque": 28,
        "descripcion": "Cadencia altísima. Ideal para hordas. +28 ataque.",
        "precio_compra": 280,
        "precio_venta": 140,
        "emoji": "🔰"
    },
    "francotirador": {
        "nombre": "🎯 Francotirador",
        "tipo": "arma",
        "subtipo": "arma_fuego",
        "bonus_ataque": 40,
        "descripcion": "Elimina zombies desde lejos. +40 ataque. Crafteado.",
        "precio_compra": 0,
        "precio_venta": 200,
        "emoji": "🎯"
    },
    "pistola_mod": {
        "nombre": "🔫 Pistola Modificada",
        "tipo": "arma",
        "subtipo": "arma_fuego",
        "bonus_ataque": 20,
        "descripcion": "Pistola con silenciador y mira. +20 ataque. Crafteada.",
        "precio_compra": 0,
        "precio_venta": 100,
        "emoji": "🔫"
    },
    "lanzallamas": {
        "nombre": "🔥 Lanzallamas",
        "tipo": "arma",
        "subtipo": "arma_fuego",
        "bonus_ataque": 45,
        "descripcion": "Quema todo a su paso. Crafteado. +45 ataque.",
        "precio_compra": 0,
        "precio_venta": 220,
        "emoji": "🔥"
    },
    "minigun": {
        "nombre": "🌀 Minigun",
        "tipo": "arma",
        "subtipo": "arma_fuego",
        "bonus_ataque": 60,
        "descripcion": "El arma más destructiva del apocalipsis. Crafteada. +60 ataque.",
        "precio_compra": 0,
        "precio_venta": 350,
        "emoji": "🌀"
    },

    # ── ARMAS CUERPO A CUERPO ─────────────────────────────────────────────────
    "cuchillo": {
        "nombre": "🔪 Cuchillo de Caza",
        "tipo": "arma",
        "subtipo": "cac",
        "bonus_ataque": 8,
        "descripcion": "Rápido y silencioso. +8 ataque.",
        "precio_compra": 40,
        "precio_venta": 20,
        "emoji": "🔪"
    },
    "machete": {
        "nombre": "⚔️ Machete",
        "tipo": "arma",
        "subtipo": "cac",
        "bonus_ataque": 18,
        "descripcion": "Hoja larga y afilada. Muy efectivo contra hordas. +18 ataque.",
        "precio_compra": 110,
        "precio_venta": 55,
        "emoji": "⚔️"
    },
    "bate_clavos": {
        "nombre": "🏏 Bate con Clavos",
        "tipo": "arma",
        "subtipo": "cac",
        "bonus_ataque": 22,
        "descripcion": "Bate de béisbol con clavos incrustados. Brutal. +22 ataque. Crafteado.",
        "precio_compra": 0,
        "precio_venta": 80,
        "emoji": "🏏"
    },
    "lanza": {
        "nombre": "🗡️ Lanza Improvisada",
        "tipo": "arma",
        "subtipo": "cac",
        "bonus_ataque": 16,
        "descripcion": "Tubo de metal afilado. Larga distancia cuerpo a cuerpo. +16 ataque.",
        "precio_compra": 70,
        "precio_venta": 35,
        "emoji": "🗡️"
    },
    "sierra_circular": {
        "nombre": "🔄 Sierra Circular",
        "tipo": "arma",
        "subtipo": "cac",
        "bonus_ataque": 35,
        "descripcion": "Herramienta industrial convertida en arma. Crafteada. +35 ataque.",
        "precio_compra": 0,
        "precio_venta": 175,
        "emoji": "🔄"
    },
    "katana": {
        "nombre": "⚔️ Katana",
        "tipo": "arma",
        "subtipo": "cac",
        "bonus_ataque": 32,
        "descripcion": "Hoja japonesa. Rara de encontrar. +32 ataque.",
        "precio_compra": 0,
        "precio_venta": 160,
        "emoji": "⚔️"
    },

    # ── ARMAS ESPECIALES / CRAFTEO ────────────────────────────────────────────
    "granada": {
        "nombre": "💣 Granada",
        "tipo": "arma_especial",
        "bonus_ataque": 45,
        "descripcion": "Explosión en área. Un solo uso. Crafteada.",
        "precio_compra": 0,
        "precio_venta": 90,
        "emoji": "💣"
    },
    "molotov": {
        "nombre": "🍾 Cóctel Molotov",
        "tipo": "arma_especial",
        "bonus_ataque": 35,
        "descripcion": "Botella incendiaria. Daño por fuego. Crafteado.",
        "precio_compra": 0,
        "precio_venta": 60,
        "emoji": "🍾"
    },
    "mina": {
        "nombre": "💥 Mina Trampa",
        "tipo": "arma_especial",
        "bonus_ataque": 55,
        "descripcion": "Se coloca en el suelo. Útil para la base. Crafteada.",
        "precio_compra": 0,
        "precio_venta": 110,
        "emoji": "💥"
    },

    # ── ARMADURAS ─────────────────────────────────────────────────────────────
    "casco_militar": {
        "nombre": "⛑️ Casco Militar",
        "tipo": "armadura",
        "bonus_defensa": 8,
        "descripcion": "Protege la cabeza. +8 defensa.",
        "precio_compra": 90,
        "precio_venta": 45,
        "emoji": "⛑️"
    },
    "armadura_cuero": {
        "nombre": "🧥 Armadura de Cuero",
        "tipo": "armadura",
        "bonus_defensa": 10,
        "descripcion": "Protección básica artesanal. +10 defensa. Crafteada.",
        "precio_compra": 0,
        "precio_venta": 50,
        "emoji": "🧥"
    },
    "traje_tatico": {
        "nombre": "🪖 Traje Táctico",
        "tipo": "armadura",
        "bonus_defensa": 20,
        "descripcion": "Traje militar completo. +20 defensa.",
        "precio_compra": 350,
        "precio_venta": 175,
        "emoji": "🪖"
    },
    "escudo_improvisado": {
        "nombre": "🛡️ Escudo Improvisado",
        "tipo": "armadura",
        "bonus_defensa": 12,
        "descripcion": "Señal de tráfico convertida en escudo. +12 defensa. Crafteado.",
        "precio_compra": 0,
        "precio_venta": 55,
        "emoji": "🛡️"
    },
    "exotraje": {
        "nombre": "🦾 Exotraje Experimental",
        "tipo": "armadura",
        "bonus_defensa": 35,
        "descripcion": "Traje del laboratorio secreto. +35 defensa. Rarísimo.",
        "precio_compra": 0,
        "precio_venta": 400,
        "emoji": "🦾"
    },

    # ── CONSUMIBLES NUEVOS ────────────────────────────────────────────────────
    "botiquin": {
        "nombre": "🧰 Botiquín",
        "tipo": "consumible",
        "efecto": "vida",
        "valor": 45,
        "descripcion": "Kit médico completo. Recupera 45 de vida.",
        "precio_compra": 35,
        "precio_venta": 17,
        "emoji": "🧰"
    },
    "adrenalina": {
        "nombre": "⚡ Adrenalina",
        "tipo": "consumible",
        "efecto": "vida",
        "valor": 80,
        "descripcion": "Inyección de emergencia. Recupera 80 de vida.",
        "precio_compra": 65,
        "precio_venta": 32,
        "emoji": "⚡"
    },
    "racion_militar": {
        "nombre": "🪖 Ración Militar",
        "tipo": "consumible",
        "efecto": "vida",
        "valor": 35,
        "descripcion": "Comida de alta energía. Recupera 35 de vida.",
        "precio_compra": 25,
        "precio_venta": 12,
        "emoji": "🪖"
    },
    "antidoto": {
        "nombre": "🧪 Antídoto",
        "tipo": "consumible",
        "efecto": "vida",
        "valor": 50,
        "descripcion": "Neutraliza venenos y recupera 50 vida. Crafteado.",
        "precio_compra": 0,
        "precio_venta": 40,
        "emoji": "🧪"
    },
    "energia_plus": {
        "nombre": "⚡ Energía Plus",
        "tipo": "consumible",
        "efecto": "cansancio",
        "valor": 50,
        "descripcion": "Bebida energética. Reduce el cansancio a la mitad.",
        "precio_compra": 30,
        "precio_venta": 15,
        "emoji": "⚡"
    },
    "comida_enlatada": {
        "nombre": "🥩 Comida Enlatada",
        "tipo": "consumible",
        "efecto": "vida",
        "valor": 30,
        "descripcion": "Carne en lata. Mejor que nada. Recupera 30 vida.",
        "precio_compra": 20,
        "precio_venta": 10,
        "emoji": "🥩"
    },

    # ── MATERIALES BÁSICOS ────────────────────────────────────────────────────
    "tornillos": {
        "nombre": "🔩 Tornillos",
        "tipo": "material",
        "descripcion": "Pequeños pero esenciales para crafting.",
        "precio_compra": 3,
        "precio_venta": 1,
        "emoji": "🔩"
    },
    "cable": {
        "nombre": "🔌 Cable Eléctrico",
        "tipo": "material",
        "descripcion": "Cable para circuitos y trampas.",
        "precio_compra": 5,
        "precio_venta": 2,
        "emoji": "🔌"
    },
    "tela": {
        "nombre": "🧵 Tela Resistente",
        "tipo": "material",
        "descripcion": "Para fabricar armaduras y vendas.",
        "precio_compra": 4,
        "precio_venta": 2,
        "emoji": "🧵"
    },
    "madera": {
        "nombre": "🪵 Madera",
        "tipo": "material",
        "descripcion": "Para construcción y armas improvisadas.",
        "precio_compra": 3,
        "precio_venta": 1,
        "emoji": "🪵"
    },
    "gasolina": {
        "nombre": "⛽ Gasolina",
        "tipo": "material",
        "descripcion": "Combustible. Necesaria para el lanzallamas y molotov.",
        "precio_compra": 8,
        "precio_venta": 4,
        "emoji": "⛽"
    },
    "bateria": {
        "nombre": "🔋 Batería",
        "tipo": "material",
        "descripcion": "Fuente de energía para dispositivos.",
        "precio_compra": 10,
        "precio_venta": 5,
        "emoji": "🔋"
    },
    "cristal": {
        "nombre": "🔭 Vidrio de Mira",
        "tipo": "material",
        "descripcion": "Cristal óptico para miras y telescopios.",
        "precio_compra": 15,
        "precio_venta": 7,
        "emoji": "🔭"
    },
    "quimico_base": {
        "nombre": "⚗️ Químico Base",
        "tipo": "material",
        "descripcion": "Reactivo para explosivos y antídotos.",
        "precio_compra": 12,
        "precio_venta": 6,
        "emoji": "⚗️"
    },
    "cuero": {
        "nombre": "🐄 Cuero",
        "tipo": "material",
        "descripcion": "Para armaduras artesanales.",
        "precio_compra": 8,
        "precio_venta": 4,
        "emoji": "🐄"
    },
    "cinta_adhesiva": {
        "nombre": "🖤 Cinta Adhesiva",
        "tipo": "material",
        "descripcion": "Esencial en cualquier taller improvisado.",
        "precio_compra": 4,
        "precio_venta": 2,
        "emoji": "🖤"
    },
    "polvo_negro": {
        "nombre": "🖤 Pólvora",
        "tipo": "material",
        "descripcion": "Para fabricar munición y explosivos.",
        "precio_compra": 10,
        "precio_venta": 5,
        "emoji": "🖤"
    },
    "municion_pesada": {
        "nombre": "🔴 Munición Pesada",
        "tipo": "material",
        "descripcion": "Para rifles y armas de alto calibre.",
        "precio_compra": 12,
        "precio_venta": 6,
        "emoji": "🔴"
    },
    "componentes_electronicos": {
        "nombre": "💾 Componentes Electrónicos",
        "tipo": "material",
        "descripcion": "Circuitos y chips para craftear gadgets.",
        "precio_compra": 20,
        "precio_venta": 10,
        "emoji": "💾"
    },

    # ── MAPAS SECRETOS — desbloquean zonas ocultas ────────────────────────────
    "mapa_bunker": {
        "nombre": "📜 Mapa del Búnker",
        "tipo": "mapa_secreto",
        "zona_desbloquea": "bunker",
        "descripcion": "Coordenadas de un búnker secreto del gobierno. Guárdalo bien.",
        "precio_compra": 0,
        "precio_venta": 0,
        "emoji": "📜"
    },
    "mapa_militar": {
        "nombre": "🗂️ Mapa Militar Clasificado",
        "tipo": "mapa_secreto",
        "zona_desbloquea": "base_militar",
        "descripcion": "Planos de una base militar secreta. Nivel de acceso: RESTRINGIDO.",
        "precio_compra": 0,
        "precio_venta": 0,
        "emoji": "🗂️"
    },
    "mapa_laboratorio": {
        "nombre": "🧪 Coordenadas del Laboratorio",
        "tipo": "mapa_secreto",
        "zona_desbloquea": "laboratorio",
        "descripcion": "La ubicación exacta del laboratorio donde empezó todo.",
        "precio_compra": 0,
        "precio_venta": 0,
        "emoji": "🧪"
    },
    "mapa_aeropuerto": {
        "nombre": "✈️ Mapa del Aeropuerto",
        "tipo": "mapa_secreto",
        "zona_desbloquea": "aeropuerto",
        "descripcion": "Acceso al aeropuerto sellado. Hay suministros dentro.",
        "precio_compra": 0,
        "precio_venta": 0,
        "emoji": "✈️"
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# ITEMS — DROGAS Y ESTIMULANTES
# ═══════════════════════════════════════════════════════════════════════════════

ITEMS_DROGAS = {
    "estimulante": {
        "nombre": "💊 Estimulante",
        "tipo": "droga",
        "efecto_temporal": {"ataque": 10, "duracion_combates": 3},
        "descripcion": "+10 ataque durante 3 combates. Riesgo de adicción.",
        "precio_compra": 50,
        "precio_venta": 25,
        "emoji": "💊"
    },
    "serum_berserker": {
        "nombre": "🩸 Sérum Berserker",
        "tipo": "droga",
        "efecto_temporal": {"ataque": 25, "defensa": -10, "duracion_combates": 2},
        "descripcion": "+25 ataque pero -10 defensa. Muy agresivo.",
        "precio_compra": 0,
        "precio_venta": 60,
        "emoji": "🩸"
    },
    "escudo_quimico": {
        "nombre": "🧪 Escudo Químico",
        "tipo": "droga",
        "efecto_temporal": {"defensa": 15, "duracion_combates": 3},
        "descripcion": "+15 defensa durante 3 combates.",
        "precio_compra": 0,
        "precio_venta": 55,
        "emoji": "🧪"
    },
    "vision_nocturna_quimica": {
        "nombre": "👁️ Visión Química",
        "tipo": "droga",
        "efecto_temporal": {"velocidad": 10, "critico_bonus": 15, "duracion_combates": 2},
        "descripcion": "+10 velocidad y +15% probabilidad de crítico.",
        "precio_compra": 0,
        "precio_venta": 70,
        "emoji": "👁️"
    },
    "dolor_cero": {
        "nombre": "❄️ Dolor Cero",
        "tipo": "droga",
        "efecto_temporal": {"reduccion_dano": 30, "duracion_combates": 4},
        "descripcion": "Reduce el daño recibido un 30% durante 4 combates.",
        "precio_compra": 80,
        "precio_venta": 40,
        "emoji": "❄️"
    },
    "anfetamina": {
        "nombre": "⚡ Anfetamina",
        "tipo": "droga",
        "efecto_temporal": {"ataque": 15, "velocidad": 15, "duracion_combates": 2},
        "descripcion": "+15 ataque y velocidad. Duración corta pero potente.",
        "precio_compra": 0,
        "precio_venta": 65,
        "emoji": "⚡"
    },
    "calmante": {
        "nombre": "😴 Calmante",
        "tipo": "droga",
        "efecto_temporal": {"cansancio_reduce": 40, "duracion_combates": 0},
        "descripcion": "Reduce el cansancio en 40 puntos inmediatamente.",
        "precio_compra": 35,
        "precio_venta": 17,
        "emoji": "😴"
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# ITEMS — TRAMPAS Y GADGETS
# ═══════════════════════════════════════════════════════════════════════════════

ITEMS_GADGETS = {
    "camara_vigilancia": {
        "nombre": "📷 Cámara de Vigilancia",
        "tipo": "gadget",
        "subtipo": "base",
        "efecto": "alerta_ataque",
        "descripcion": "Instalada en la base avisa con antelación de ataques zombie.",
        "precio_compra": 0,
        "precio_venta": 80,
        "emoji": "📷"
    },
    "detector_movimiento": {
        "nombre": "📡 Detector de Movimiento",
        "tipo": "gadget",
        "subtipo": "base",
        "efecto": "reduce_dano_ataque_pct",
        "efecto_valor": 10,
        "descripcion": "Reduce el daño de ataques a la base un 10%.",
        "precio_compra": 0,
        "precio_venta": 90,
        "emoji": "📡"
    },
    "alarma_perimetral": {
        "nombre": "🔔 Alarma Perimetral",
        "tipo": "gadget",
        "subtipo": "base",
        "efecto": "reduce_dano_ataque_pct",
        "efecto_valor": 15,
        "descripcion": "Alarma que desorienta a los zombies. -15% daño en ataques.",
        "precio_compra": 0,
        "precio_venta": 110,
        "emoji": "🔔"
    },
    "trampa_puas": {
        "nombre": "⚠️ Trampa de Púas",
        "tipo": "gadget",
        "subtipo": "explorar",
        "efecto": "dano_zombie_automatico",
        "efecto_valor": 30,
        "descripcion": "Al explorar, daña automáticamente al zombie antes del combate.",
        "precio_compra": 0,
        "precio_venta": 55,
        "emoji": "⚠️"
    },
    "bengala": {
        "nombre": "🔴 Bengala",
        "tipo": "gadget",
        "subtipo": "explorar",
        "efecto": "huida_garantizada",
        "descripcion": "Garantiza la huida del combate sin recibir daño.",
        "precio_compra": 30,
        "precio_venta": 15,
        "emoji": "🔴"
    },
    "walkie_talkie": {
        "nombre": "📻 Walkie Talkie",
        "tipo": "gadget",
        "subtipo": "explorar",
        "efecto": "doble_recursos",
        "descripcion": "Coordinas con otros supervivientes. Dobla recursos encontrados.",
        "precio_compra": 0,
        "precio_venta": 95,
        "emoji": "📻"
    },
    "linterna_tactica": {
        "nombre": "🔦 Linterna Táctica",
        "tipo": "gadget",
        "subtipo": "explorar",
        "efecto": "bonus_exp_explorar",
        "efecto_valor": 20,
        "descripcion": "+20% EXP en zonas oscuras (fábrica, bunker, cementerio).",
        "precio_compra": 45,
        "precio_venta": 22,
        "emoji": "🔦"
    },
    "drone": {
        "nombre": "🚁 Dron de Reconocimiento",
        "tipo": "gadget",
        "subtipo": "explorar",
        "efecto": "previsualizar_zona",
        "descripcion": "Muestra los recursos disponibles antes de explorar.",
        "precio_compra": 0,
        "precio_venta": 150,
        "emoji": "🚁"
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# ITEMS — VEHÍCULOS
# ═══════════════════════════════════════════════════════════════════════════════

ITEMS_VEHICULOS = {
    "bicicleta": {
        "nombre": "🚲 Bicicleta",
        "tipo": "vehiculo",
        "bonus_velocidad": 5,
        "reduccion_cansancio": 10,
        "descripcion": "Silenciosa y rápida. +5 velocidad, -10% cansancio al explorar.",
        "precio_compra": 120,
        "precio_venta": 60,
        "emoji": "🚲",
        "durabilidad_max": 30,
    },
    "moto": {
        "nombre": "🏍️ Moto",
        "tipo": "vehiculo",
        "bonus_velocidad": 12,
        "reduccion_cansancio": 20,
        "descripcion": "Rápida y maniobrable. +12 velocidad, -20% cansancio.",
        "precio_compra": 0,
        "precio_venta": 200,
        "emoji": "🏍️",
        "durabilidad_max": 50,
    },
    "camioneta": {
        "nombre": "🚗 Camioneta 4x4",
        "tipo": "vehiculo",
        "bonus_velocidad": 8,
        "reduccion_cansancio": 15,
        "bonus_recursos": 2,
        "descripcion": "Puedes llevar más recursos. +8 velocidad, +2 recursos extra.",
        "precio_compra": 0,
        "precio_venta": 300,
        "emoji": "🚗",
        "durabilidad_max": 80,
    },
    "blindado_militar": {
        "nombre": "🚛 Vehículo Blindado",
        "tipo": "vehiculo",
        "bonus_velocidad": 5,
        "bonus_defensa": 10,
        "reduccion_cansancio": 25,
        "descripcion": "Protección total. +5 velocidad, +10 defensa al explorar.",
        "precio_compra": 0,
        "precio_venta": 500,
        "emoji": "🚛",
        "durabilidad_max": 100,
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# ITEMS — ROPA Y ACCESORIOS
# ═══════════════════════════════════════════════════════════════════════════════

ITEMS_ROPA = {
    "guantes_tacticos": {
        "nombre": "🥊 Guantes Tácticos",
        "tipo": "accesorio",
        "slot": "manos",
        "bonus_ataque": 5,
        "descripcion": "Mejora el agarre y el golpe. +5 ataque.",
        "precio_compra": 60,
        "precio_venta": 30,
        "emoji": "🥊"
    },
    "botas_militares": {
        "nombre": "👢 Botas Militares",
        "tipo": "accesorio",
        "slot": "pies",
        "bonus_velocidad": 5,
        "descripcion": "Suelas reforzadas. +5 velocidad.",
        "precio_compra": 70,
        "precio_venta": 35,
        "emoji": "👢"
    },
    "gafas_vision_nocturna": {
        "nombre": "🥽 Gafas de Visión Nocturna",
        "tipo": "accesorio",
        "slot": "cabeza",
        "bonus_critico": 10,
        "descripcion": "+10% probabilidad de golpe crítico.",
        "precio_compra": 0,
        "precio_venta": 120,
        "emoji": "🥽"
    },
    "guantes_cuero": {
        "nombre": "🧤 Guantes de Cuero",
        "tipo": "accesorio",
        "slot": "manos",
        "bonus_ataque": 3,
        "descripcion": "Guantes básicos de cuero. +3 ataque.",
        "precio_compra": 30,
        "precio_venta": 15,
        "emoji": "🧤"
    },
    "cinturon_supervivencia": {
        "nombre": "🪢 Cinturón de Supervivencia",
        "tipo": "accesorio",
        "slot": "cintura",
        "bonus_inventario": 3,
        "descripcion": "Lleva 3 items extra sin peso adicional.",
        "precio_compra": 0,
        "precio_venta": 85,
        "emoji": "🪢"
    },
    "mascara_gas": {
        "nombre": "😷 Máscara de Gas",
        "tipo": "accesorio",
        "slot": "cara",
        "bonus_defensa": 8,
        "descripcion": "Protege de venenos y químicos. +8 defensa.",
        "precio_compra": 90,
        "precio_venta": 45,
        "emoji": "😷"
    },
    "chaleco_municion": {
        "nombre": "🎽 Chaleco de Munición",
        "tipo": "accesorio",
        "slot": "pecho",
        "bonus_municion_drop": 20,
        "descripcion": "+20% probabilidad de drop de munición.",
        "precio_compra": 0,
        "precio_venta": 75,
        "emoji": "🎽"
    },
    "capa_sigilo": {
        "nombre": "🧥 Capa de Sigilo",
        "tipo": "accesorio",
        "slot": "espalda",
        "reduce_encuentros": 20,
        "descripcion": "-20% probabilidad de encuentro con zombies al explorar.",
        "precio_compra": 0,
        "precio_venta": 130,
        "emoji": "🧥"
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# ITEMS — COMIDA COCINADA
# ═══════════════════════════════════════════════════════════════════════════════

ITEMS_COMIDA_COCINADA = {
    "sopa_supervivencia": {
        "nombre": "🍲 Sopa de Supervivencia",
        "tipo": "consumible",
        "efecto": "vida",
        "valor": 50,
        "descripcion": "Sopa caliente hecha con lo que había. Recupera 50 vida.",
        "precio_compra": 0,
        "precio_venta": 20,
        "emoji": "🍲"
    },
    "estofado_carne": {
        "nombre": "🥘 Estofado de Carne",
        "tipo": "consumible",
        "efecto": "vida",
        "valor": 70,
        "descripcion": "Nutritivo y reconfortante. Recupera 70 vida.",
        "precio_compra": 0,
        "precio_venta": 30,
        "emoji": "🥘"
    },
    "barra_energia": {
        "nombre": "🍫 Barra de Energía",
        "tipo": "consumible",
        "efecto_doble": {"vida": 20, "cansancio_reduce": 25},
        "descripcion": "Recupera 20 vida y reduce el cansancio 25 puntos.",
        "precio_compra": 0,
        "precio_venta": 25,
        "emoji": "🍫"
    },
    "festin_apocalipsis": {
        "nombre": "🍖 Festín del Apocalipsis",
        "tipo": "consumible",
        "efecto": "vida",
        "valor": 100,
        "descripcion": "Un banquete en el fin del mundo. Recupera 100 vida.",
        "precio_compra": 0,
        "precio_venta": 45,
        "emoji": "🍖"
    },
    "cafe_negro": {
        "nombre": "☕ Café Negro",
        "tipo": "consumible",
        "efecto_doble": {"cansancio_reduce": 50, "vida": 5},
        "descripcion": "Café fuerte del refugio. Elimina el 50% del cansancio.",
        "precio_compra": 20,
        "precio_venta": 10,
        "emoji": "☕"
    },
    "pan_duro": {
        "nombre": "🍞 Pan Duro",
        "tipo": "consumible",
        "efecto": "vida",
        "valor": 15,
        "descripcion": "No está bueno pero es comida. Recupera 15 vida.",
        "precio_compra": 5,
        "precio_venta": 2,
        "emoji": "🍞"
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# ITEMS — LEGENDARIOS
# ═══════════════════════════════════════════════════════════════════════════════

ITEMS_LEGENDARIOS = {
    "corona_paciente_cero": {
        "nombre": "☠️ Corona del Paciente Cero",
        "tipo": "legendario",
        "rareza": "legendario",
        "bonus_ataque": 50,
        "bonus_defensa": 20,
        "descripcion": "La corona del primer infectado. Emana un aura de terror. +50 ataque, +20 defensa.",
        "precio_compra": 0,
        "precio_venta": 1000,
        "emoji": "☠️",
        "drop_source": "zombie_jefe",
        "drop_prob": 0.02,
    },
    "suero_origen": {
        "nombre": "🧬 Suero del Origen",
        "tipo": "legendario",
        "rareza": "legendario",
        "efecto": "vida_completa_y_stats",
        "bonus_permanente": {"ataque": 5, "defensa": 5, "velocidad": 5},
        "descripcion": "El suero original del laboratorio. Cura toda la vida y da +5 a todos los stats PERMANENTEMENTE.",
        "precio_compra": 0,
        "precio_venta": 500,
        "emoji": "🧬",
        "drop_source": "laboratorio",
        "drop_prob": 0.03,
    },
    "rifle_sniper_militar": {
        "nombre": "🎯 Sniper Militar XM2010",
        "tipo": "legendario",
        "rareza": "legendario",
        "subtipo": "arma_fuego",
        "bonus_ataque": 70,
        "descripcion": "El rifle de francotirador más potente del ejército. +70 ataque.",
        "precio_compra": 0,
        "precio_venta": 800,
        "emoji": "🎯",
        "drop_source": "base_militar",
        "drop_prob": 0.02,
    },
    "armadura_titan": {
        "nombre": "🦾 Armadura del Titán",
        "tipo": "legendario",
        "rareza": "legendario",
        "bonus_defensa": 50,
        "bonus_vida_max": 50,
        "descripcion": "Forjada con restos del Titán. +50 defensa y +50 vida máxima.",
        "precio_compra": 0,
        "precio_venta": 900,
        "emoji": "🦾",
        "drop_source": "zombie_titan",
        "drop_prob": 0.03,
    },
    "reloj_apocalipsis": {
        "nombre": "⌚ Reloj del Apocalipsis",
        "tipo": "legendario",
        "rareza": "legendario",
        "efecto": "cooldown_reduccion_50pct",
        "descripcion": "Reloj de laboratorio que distorsiona el tiempo. Reduce todos los cooldowns a la mitad.",
        "precio_compra": 0,
        "precio_venta": 600,
        "emoji": "⌚",
        "drop_source": "bunker",
        "drop_prob": 0.02,
    },
    "diario_paciente_cero": {
        "nombre": "📖 Diario del Paciente Cero",
        "tipo": "legendario",
        "rareza": "legendario",
        "efecto": "desbloquea_todo",
        "descripcion": "El diario original. Contiene las coordenadas de todas las zonas secretas.",
        "precio_compra": 0,
        "precio_venta": 400,
        "emoji": "📖",
        "drop_source": "cementerio",
        "drop_prob": 0.01,
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# ITEMS — EVENTOS ESPECIALES
# ═══════════════════════════════════════════════════════════════════════════════

ITEMS_EVENTO = {
    "caja_navidad_zombie": {
        "nombre": "🎁 Caja de Navidad Zombie",
        "tipo": "evento",
        "evento": "navidad",
        "efecto": "abrir_caja",
        "descripcion": "Una caja envuelta en vendas y tripas. Contiene un item aleatorio.",
        "precio_compra": 0,
        "precio_venta": 0,
        "emoji": "🎁"
    },
    "huevo_zombie": {
        "nombre": "🥚 Huevo Zombie",
        "tipo": "evento",
        "evento": "pascua",
        "efecto": "item_aleatorio_raro",
        "descripcion": "¿Qué habrá dentro? Solo en Pascua.",
        "precio_compra": 0,
        "precio_venta": 0,
        "emoji": "🥚"
    },
    "mascara_halloween": {
        "nombre": "🎃 Máscara de Halloween",
        "tipo": "evento",
        "evento": "halloween",
        "bonus_critico": 20,
        "descripcion": "Los zombies te confunden con uno de los suyos. +20% crítico. Solo en Halloween.",
        "precio_compra": 0,
        "precio_venta": 0,
        "emoji": "🎃"
    },
    "cohete_aniversario": {
        "nombre": "🎆 Cohete de Aniversario",
        "tipo": "evento",
        "evento": "aniversario",
        "efecto": "daño_masivo",
        "bonus_ataque": 100,
        "descripcion": "Cohete de celebración reconvertido. +100 ataque. Un solo uso.",
        "precio_compra": 0,
        "precio_venta": 0,
        "emoji": "🎆"
    },
    "champan_apocalipsis": {
        "nombre": "🍾 Champán del Apocalipsis",
        "tipo": "evento",
        "evento": "anio_nuevo",
        "efecto_doble": {"vida": 150, "cansancio_reduce": 100},
        "descripcion": "Para el año nuevo en el fin del mundo. Cura 150 vida y elimina el cansancio.",
        "precio_compra": 0,
        "precio_venta": 0,
        "emoji": "🍾"
    },
    "trofeo_superviviente": {
        "nombre": "🏆 Trofeo del Superviviente",
        "tipo": "evento",
        "evento": "ranking",
        "efecto": "cosmético",
        "descripcion": "Para el mejor superviviente del mes. Solo estético pero muy prestigioso.",
        "precio_compra": 0,
        "precio_venta": 0,
        "emoji": "🏆"
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# ITEMS — DEGRADABLES (tienen durabilidad)
# ═══════════════════════════════════════════════════════════════════════════════

ITEMS_DEGRADABLES = {
    "sierra_motosierra": {
        "nombre": "⛓️ Motosierra",
        "tipo": "arma",
        "subtipo": "cac",
        "bonus_ataque": 38,
        "descripcion": "+38 ataque. Se degrada con el uso. Repara con piezas de metal.",
        "precio_compra": 0,
        "precio_venta": 180,
        "emoji": "⛓️",
        "durabilidad_max": 20,
        "dano_durabilidad_por_uso": 1,
        "reparacion": {"piezas_metal": 3, "gasolina": 1},
    },
    "arco_improvisado": {
        "nombre": "🏹 Arco Improvisado",
        "tipo": "arma",
        "subtipo": "cac",
        "bonus_ataque": 20,
        "descripcion": "+20 ataque silencioso. Cuerdas se rompen. Repara con tela.",
        "precio_compra": 60,
        "precio_venta": 30,
        "emoji": "🏹",
        "durabilidad_max": 15,
        "dano_durabilidad_por_uso": 1,
        "reparacion": {"tela": 2, "madera": 1},
    },
    "chaleco_improvisado": {
        "nombre": "🛡️ Chaleco Improvisado",
        "tipo": "armadura",
        "bonus_defensa": 18,
        "descripcion": "+18 defensa. Se daña al recibir golpes. Repara con cuero y tela.",
        "precio_compra": 0,
        "precio_venta": 85,
        "emoji": "🛡️",
        "durabilidad_max": 25,
        "dano_durabilidad_por_uso": 1,
        "reparacion": {"cuero": 2, "tela": 2, "cinta_adhesiva": 1},
    },
    "hacha_guerra": {
        "nombre": "🪓 Hacha de Guerra",
        "tipo": "arma",
        "subtipo": "cac",
        "bonus_ataque": 28,
        "descripcion": "+28 ataque. Filo que se embota. Repara con piezas de metal.",
        "precio_compra": 0,
        "precio_venta": 130,
        "emoji": "🪓",
        "durabilidad_max": 30,
        "dano_durabilidad_por_uso": 1,
        "reparacion": {"piezas_metal": 2, "tornillos": 2},
    },
    "vehiculo_oxidado": {
        "nombre": "🚗 Coche Oxidado",
        "tipo": "vehiculo",
        "bonus_velocidad": 6,
        "descripcion": "+6 velocidad. Se avería con frecuencia. Repara con piezas.",
        "precio_compra": 80,
        "precio_venta": 40,
        "emoji": "🚗",
        "durabilidad_max": 20,
        "dano_durabilidad_por_uso": 2,
        "reparacion": {"piezas_metal": 4, "gasolina": 2, "tornillos": 3},
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# ITEMS — MEJORABLES (se pueden upgradear)
# ═══════════════════════════════════════════════════════════════════════════════

ITEMS_MEJORABLES = {
    # Formato: item_id_base → mejora_1 → mejora_2 → mejora_3
    "pistola_v2": {
        "nombre": "🔫 Pistola Mejorada V2",
        "tipo": "arma",
        "subtipo": "arma_fuego",
        "bonus_ataque": 25,
        "descripcion": "Pistola con cañón extendido. +25 ataque.",
        "precio_compra": 0,
        "precio_venta": 120,
        "emoji": "🔫",
        "mejora_de": "pistola_mod",
        "coste_mejora": {"piezas_metal": 4, "cristal": 1, "tornillos": 3},
    },
    "pistola_v3": {
        "nombre": "🔫 Pistola Mejorada V3",
        "tipo": "arma",
        "subtipo": "arma_fuego",
        "bonus_ataque": 32,
        "descripcion": "La mejor pistola posible. +32 ataque.",
        "precio_compra": 0,
        "precio_venta": 180,
        "emoji": "🔫",
        "mejora_de": "pistola_v2",
        "coste_mejora": {"piezas_metal": 6, "componentes_electronicos": 2, "cristal": 2},
    },
    "hacha_reforzada": {
        "nombre": "🪓 Hacha Reforzada",
        "tipo": "arma",
        "subtipo": "cac",
        "bonus_ataque": 22,
        "descripcion": "Hacha con mango de acero. +22 ataque.",
        "precio_compra": 0,
        "precio_venta": 100,
        "emoji": "🪓",
        "mejora_de": "hacha",
        "coste_mejora": {"piezas_metal": 3, "tornillos": 4, "cinta_adhesiva": 2},
    },
    "hacha_devastadora": {
        "nombre": "🪓 Hacha Devastadora",
        "tipo": "arma",
        "subtipo": "cac",
        "bonus_ataque": 30,
        "descripcion": "El hacha definitiva. +30 ataque.",
        "precio_compra": 0,
        "precio_venta": 160,
        "emoji": "🪓",
        "mejora_de": "hacha_reforzada",
        "coste_mejora": {"piezas_metal": 5, "cable": 2, "quimico_base": 1},
    },
    "kevlar_v2": {
        "nombre": "🦺 Kevlar Avanzado",
        "tipo": "armadura",
        "bonus_defensa": 22,
        "descripcion": "Kevlar con placas de metal. +22 defensa.",
        "precio_compra": 0,
        "precio_venta": 180,
        "emoji": "🦺",
        "mejora_de": "chaleco_kevlar",
        "coste_mejora": {"piezas_metal": 5, "tela": 3, "tornillos": 4},
    },
    "kevlar_v3": {
        "nombre": "🦺 Kevlar Élite",
        "tipo": "armadura",
        "bonus_defensa": 30,
        "descripcion": "La mejor armadura accesible. +30 defensa.",
        "precio_compra": 0,
        "precio_venta": 280,
        "emoji": "🦺",
        "mejora_de": "kevlar_v2",
        "coste_mejora": {"piezas_metal": 8, "componentes_electronicos": 2, "cuero": 3},
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# FUSIÓN COMPLETA DE ITEMS
# ═══════════════════════════════════════════════════════════════════════════════

ITEMS.update(ITEMS_DROGAS)
ITEMS.update(ITEMS_GADGETS)
ITEMS.update(ITEMS_VEHICULOS)
ITEMS.update(ITEMS_ROPA)
ITEMS.update(ITEMS_COMIDA_COCINADA)
ITEMS.update(ITEMS_LEGENDARIOS)
ITEMS.update(ITEMS_EVENTO)
ITEMS.update(ITEMS_DEGRADABLES)
ITEMS.update(ITEMS_MEJORABLES)

# ═══════════════════════════════════════════════════════════════════════════════
# CONJUNTOS DE REFERENCIA RÁPIDA
# ═══════════════════════════════════════════════════════════════════════════════

ITEMS_DEGRADABLES_IDS  = set(ITEMS_DEGRADABLES.keys()) | set(ITEMS_VEHICULOS.keys())
ITEMS_MEJORABLES_IDS   = set(ITEMS_MEJORABLES.keys())
ITEMS_LEGENDARIOS_IDS  = set(ITEMS_LEGENDARIOS.keys())
ITEMS_EVENTO_IDS       = set(ITEMS_EVENTO.keys())

# ═══════════════════════════════════════════════════════════════════════════════
# TIENDA DEL REFUGIO
# ═══════════════════════════════════════════════════════════════════════════════

TIENDA_ITEMS = [
    # Consumibles
    "venda", "botiquin", "morfina", "adrenalina",
    "comida", "comida_enlatada", "racion_militar", "agua", "energia_plus",
    # Armas fuego
    "pistola", "revolver", "escopeta", "subfusil",
    # Armas CaC
    "cuchillo", "hacha", "machete", "lanza",
    # Armaduras
    "casco_militar", "chaleco_kevlar", "traje_tatico",
    # Materiales básicos
    "municion", "municion_pesada", "tornillos", "cable",
    "tela", "madera", "gasolina", "bateria",
    "cristal", "quimico_base", "cuero", "cinta_adhesiva", "polvo_negro",
    "componentes_electronicos",
    # Equipamiento
    "mochila_grande",
    # Drogas
    "estimulante", "dolor_cero", "calmante",
    # Gadgets básicos
    "bengala", "linterna_tactica",
    # Vehículos
    "bicicleta",
    # Ropa
    "guantes_cuero", "botas_militares", "mascara_gas",
    # Comida cocinada
    "cafe_negro", "pan_duro",
    # Arcos
    "arco_improvisado",
]

# ═══════════════════════════════════════════════════════════════════════════════
# DROPS ESPECIALES
# ═══════════════════════════════════════════════════════════════════════════════

DROPS_MAPAS_SECRETOS = {
    "cementerio":   ("mapa_bunker",       0.08),
    "fabrica":      ("mapa_militar",      0.06),
    "universidad":  ("mapa_laboratorio",  0.05),
    "armeria":      ("mapa_aeropuerto",   0.07),
}

DROPS_LEGENDARIOS = {
    "zombie_jefe":   [("corona_paciente_cero", 0.02), ("diario_paciente_cero", 0.01)],
    "zombie_titan":  [("armadura_titan", 0.03)],
    "bunker":        [("reloj_apocalipsis", 0.02)],
    "base_militar":  [("rifle_sniper_militar", 0.02)],
    "laboratorio":   [("suero_origen", 0.03)],
}

# ═══════════════════════════════════════════════════════════════════════════════
# EVENTOS ALEATORIOS DE EXPLORACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

EVENTOS_ALEATORIOS = [
    {
        "id": "superviviente",
        "descripcion": "🧑 Encuentras a un superviviente que te da suministros a cambio de protección.",
        "efecto": "items",
        "items": {"comida": 2, "venda": 1},
        "probabilidad": 0.12
    },
    {
        "id": "trampa",
        "descripcion": "⚠️ Caes en una trampa oxidada. Te haces daño.",
        "efecto": "daño",
        "valor": 15,
        "probabilidad": 0.10
    },
    {
        "id": "caja_suministros",
        "descripcion": "📦 ¡Encuentras una caja de suministros sellada!",
        "efecto": "items",
        "items": {"municion": 5, "comida": 2, "venda": 1},
        "probabilidad": 0.10
    },
    {
        "id": "horda",
        "descripcion": "🧟🧟🧟 ¡Una pequeña horda te sorprende! Recibes daño antes de escapar.",
        "efecto": "daño",
        "valor": 25,
        "probabilidad": 0.10
    },
    {
        "id": "tapas_escondidas",
        "descripcion": "💰 Encuentras tapas escondidas debajo de un tablón.",
        "efecto": "tapas",
        "valor": 20,
        "probabilidad": 0.08
    },
    {
        "id": "radio",
        "descripcion": "📻 Escuchas una transmisión de radio con coordenadas. Encuentras suministros.",
        "efecto": "items",
        "items": {"morfina": 1, "municion": 3},
        "probabilidad": 0.07
    },
    {
        "id": "nada",
        "descripcion": "🌫️ La zona parece despejada. Solo silencio y viento.",
        "efecto": "ninguno",
        "probabilidad": 0.43
    },
]
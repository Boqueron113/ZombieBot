"""
Datos del juego: zonas, items, zombies, tienda
"""

# ── ZONAS DEL MAPA ────────────────────────────────────────────────────────────
# "requiere_item": si está definido, el jugador necesita ese item en su inventario
# para poder entrar. Si no lo tiene, ve la zona como ??? en el mapa.

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

# ── TIPOS DE ZOMBIES ──────────────────────────────────────────────────────────
ZOMBIES = {
    "zombie_caminante": {
        "nombre": "🧟 Caminante",
        "vida": 30,
        "ataque": 8,
        "defensa": 2,
        "exp": 15,
        "tapas": (2, 8),
        "drop": {"municion": 0.3, "venda": 0.2, "comida": 0.25},
        "descripcion": "Lento pero implacable. El zombie más común."
    },
    "zombie_corredor": {
        "nombre": "💨 Corredor",
        "vida": 25,
        "ataque": 14,
        "defensa": 1,
        "exp": 25,
        "tapas": (5, 15),
        "drop": {"municion": 0.4, "comida": 0.2},
        "descripcion": "Rápido y agresivo. Ataca antes de que puedas reaccionar."
    },
    "zombie_gordo": {
        "nombre": "🐷 Barrigón",
        "vida": 70,
        "ataque": 12,
        "defensa": 8,
        "exp": 35,
        "tapas": (8, 20),
        "drop": {"comida": 0.5, "conservas": 0.3, "venda": 0.2},
        "descripcion": "Lento pero con mucha vida. Muy difícil de matar."
    },
    "zombie_policia": {
        "nombre": "👮 Poli Zombie",
        "vida": 45,
        "ataque": 16,
        "defensa": 6,
        "exp": 40,
        "tapas": (10, 25),
        "drop": {"municion": 0.6, "pistola": 0.1, "venda": 0.2},
        "descripcion": "Aún lleva el chaleco antibalas. Armado y peligroso."
    },
    "zombie_enfermero": {
        "nombre": "🩺 Enfermero Zombie",
        "vida": 35,
        "ataque": 10,
        "defensa": 3,
        "exp": 30,
        "tapas": (6, 18),
        "drop": {"venda": 0.6, "morfina": 0.3, "jeringilla": 0.2},
        "descripcion": "Fue médico. Ahora infecta en lugar de curar."
    },
    "zombie_doctor": {
        "nombre": "🥼 Doctor Zombie",
        "vida": 50,
        "ataque": 18,
        "defensa": 5,
        "exp": 50,
        "tapas": (12, 30),
        "drop": {"morfina": 0.5, "jeringilla": 0.4, "venda": 0.3},
        "descripcion": "El jefe del hospital. Muy peligroso."
    },
    "zombie_blindado": {
        "nombre": "🛡️ Blindado",
        "vida": 90,
        "ataque": 20,
        "defensa": 15,
        "exp": 70,
        "tapas": (20, 40),
        "drop": {"piezas_metal": 0.4, "municion": 0.3, "rifle": 0.05},
        "descripcion": "Cubierto de metal. Necesitas buenas armas para atravesarlo."
    },
    "zombie_quimico": {
        "nombre": "☢️ Químico",
        "vida": 40,
        "ataque": 22,
        "defensa": 4,
        "exp": 55,
        "tapas": (15, 35),
        "drop": {"explosivo": 0.3, "municion": 0.4},
        "descripcion": "Mutado por químicos. Sus ataques envenenan."
    },
    "zombie_industrial": {
        "nombre": "⚙️ Industrial",
        "vida": 80,
        "ataque": 25,
        "defensa": 10,
        "exp": 80,
        "tapas": (25, 50),
        "drop": {"piezas_metal": 0.6, "explosivo": 0.2},
        "descripcion": "Enorme obrero zombificado. Fuerza brutal."
    },
    "zombie_anciano": {
        "nombre": "💀 Anciano Zombie",
        "vida": 60,
        "ataque": 15,
        "defensa": 5,
        "exp": 60,
        "tapas": (10, 30),
        "drop": {"reliquia": 0.4, "venda": 0.3, "morfina": 0.2},
        "descripcion": "Lleva años muerto. Muy resistente a la descomposición."
    },
    "zombie_titan": {
        "nombre": "👹 Titán",
        "vida": 150,
        "ataque": 35,
        "defensa": 20,
        "exp": 150,
        "tapas": (50, 100),
        "drop": {"rifle": 0.15, "explosivo": 0.4, "piezas_metal": 0.5},
        "descripcion": "Una bestia enorme. Solo los más fuertes pueden sobrevivir."
    },
    "zombie_jefe": {
        "nombre": "☠️ Paciente Cero",
        "vida": 300,
        "ataque": 50,
        "defensa": 30,
        "exp": 400,
        "tapas": (150, 300),
        "drop": {"rifle": 0.4, "chaleco_kevlar": 0.3, "morfina": 0.5, "explosivo": 0.4},
        "descripcion": "El primer infectado. El origen de todo. Solo para héroes."
    },
}

# ── ITEMS ─────────────────────────────────────────────────────────────────────
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

# Items disponibles en la tienda del refugio
TIENDA_ITEMS = [
    "venda", "morfina", "comida", "agua",
    "pistola", "hacha", "municion",
    "mochila_grande", "chaleco_kevlar"
]

# Dónde puede caer cada mapa secreto (zona_id: mapa_id, probabilidad)
# Los mapas solo caen en zonas difíciles como drops raros
DROPS_MAPAS_SECRETOS = {
    "cementerio":   ("mapa_bunker",       0.08),
    "fabrica":      ("mapa_militar",      0.06),
    "universidad":  ("mapa_laboratorio",  0.05),
    "armeria":      ("mapa_aeropuerto",   0.07),
}

# Eventos aleatorios durante exploración
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

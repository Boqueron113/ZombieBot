"""
Datos del sistema de bases personales
"""

# ── ESTRUCTURAS CONSTRUIBLES ──────────────────────────────────────────────────
# Cada estructura tiene niveles 0 (no construida) a MAX_NIVEL
# Los costes son en tapas + materiales del inventario

ESTRUCTURAS = {
    "muro": {
        "nombre": "🧱 Muro Perimetral",
        "descripcion": "Protege tu base de los ataques zombie. Más nivel = más resistencia.",
        "emoji": "🧱",
        "niveles": {
            1: {"vida": 150, "defensa_base": 10,  "coste_tapas": 80,  "coste_items": {"piezas_metal": 5},  "descripcion": "Tablones y chatarra"},
            2: {"vida": 300, "defensa_base": 22,  "coste_tapas": 160, "coste_items": {"piezas_metal": 12}, "descripcion": "Refuerzo de metal"},
            3: {"vida": 500, "defensa_base": 38,  "coste_tapas": 300, "coste_items": {"piezas_metal": 25, "municion": 5}, "descripcion": "Hormigón y acero"},
            4: {"vida": 800, "defensa_base": 55,  "coste_tapas": 500, "coste_items": {"piezas_metal": 40, "explosivo": 2}, "descripcion": "Bunker reforzado"},
            5: {"vida": 1200,"defensa_base": 75,  "coste_tapas": 800, "coste_items": {"piezas_metal": 60, "explosivo": 5}, "descripcion": "Fortaleza inexpugnable"},
        }
    },
    "torretas": {
        "nombre": "🔫 Torretas Automáticas",
        "descripcion": "Disparan a los zombies durante los ataques, reduciendo el daño recibido.",
        "emoji": "🔫",
        "niveles": {
            1: {"daño_por_turno": 15, "coste_tapas": 120, "coste_items": {"municion": 20, "piezas_metal": 8},  "descripcion": "Pistolas montadas"},
            2: {"daño_por_turno": 30, "coste_tapas": 220, "coste_items": {"municion": 40, "piezas_metal": 15}, "descripcion": "Rifles automáticos"},
            3: {"daño_por_turno": 50, "coste_tapas": 380, "coste_items": {"municion": 70, "piezas_metal": 25}, "descripcion": "Ametralladoras"},
            4: {"daño_por_turno": 75, "coste_tapas": 600, "coste_items": {"municion": 100,"piezas_metal": 40, "explosivo": 3}, "descripcion": "Cañones automáticos"},
            5: {"daño_por_turno": 110,"coste_tapas": 900, "coste_items": {"municion": 150,"piezas_metal": 60, "explosivo": 8}, "descripcion": "Sistema CIWS zombie"},
        }
    },
    "almacen": {
        "nombre": "📦 Almacén",
        "descripcion": "Guarda recursos de forma segura. Los zombies no pueden robar lo que está aquí.",
        "emoji": "📦",
        "niveles": {
            1: {"slots": 5,  "proteccion_pct": 30, "coste_tapas": 60,  "coste_items": {"piezas_metal": 3},  "descripcion": "Armario de metal"},
            2: {"slots": 10, "proteccion_pct": 50, "coste_tapas": 120, "coste_items": {"piezas_metal": 8},  "descripcion": "Cámara acorazada básica"},
            3: {"slots": 20, "proteccion_pct": 70, "coste_tapas": 220, "coste_items": {"piezas_metal": 18}, "descripcion": "Búnker de suministros"},
            4: {"slots": 35, "proteccion_pct": 85, "coste_tapas": 380, "coste_items": {"piezas_metal": 30}, "descripcion": "Almacén blindado"},
            5: {"slots": 50, "proteccion_pct": 95, "coste_tapas": 600, "coste_items": {"piezas_metal": 50}, "descripcion": "Bóveda indestructible"},
        }
    },
    "generador": {
        "nombre": "⚡ Generador",
        "descripcion": "Produce tapas pasivamente cada hora de ataque. Cuanto mayor nivel, más produce.",
        "emoji": "⚡",
        "niveles": {
            1: {"tapas_por_hora": 5,  "coste_tapas": 100, "coste_items": {"piezas_metal": 6,  "municion": 5},  "descripcion": "Generador de gasolina"},
            2: {"tapas_por_hora": 12, "coste_tapas": 200, "coste_items": {"piezas_metal": 14, "municion": 10}, "descripcion": "Generador diésel"},
            3: {"tapas_por_hora": 22, "coste_tapas": 350, "coste_items": {"piezas_metal": 25, "municion": 20}, "descripcion": "Planta solar"},
            4: {"tapas_por_hora": 35, "coste_tapas": 550, "coste_items": {"piezas_metal": 40, "municion": 30}, "descripcion": "Turbina eólica"},
            5: {"tapas_por_hora": 55, "coste_tapas": 850, "coste_items": {"piezas_metal": 60, "municion": 50}, "descripcion": "Reactor experimental"},
        }
    },
    "hospital_base": {
        "nombre": "🏥 Enfermería",
        "descripcion": "Te cura automáticamente cada vez que vuelves a la base.",
        "emoji": "🏥",
        "niveles": {
            1: {"curacion_auto": 20, "coste_tapas": 90,  "coste_items": {"venda": 5,  "piezas_metal": 4},  "descripcion": "Botiquín básico"},
            2: {"curacion_auto": 40, "coste_tapas": 180, "coste_items": {"venda": 10, "piezas_metal": 10}, "descripcion": "Sala de curas"},
            3: {"curacion_auto": 70, "coste_tapas": 320, "coste_items": {"morfina": 5, "piezas_metal": 20}, "descripcion": "Quirófano de campo"},
            4: {"curacion_auto": 100,"coste_tapas": 520, "coste_items": {"morfina": 10,"piezas_metal": 35}, "descripcion": "UCI de emergencia"},
            5: {"curacion_auto": 150,"coste_tapas": 800, "coste_items": {"jeringilla": 5,"piezas_metal": 50}, "descripcion": "Centro médico completo"},
        }
    },
    "laboratorio": {
        "nombre": "🔬 Laboratorio",
        "descripcion": "Multiplica la EXP que ganas en combate y exploración.",
        "emoji": "🔬",
        "niveles": {
            1: {"bonus_exp_pct": 10, "coste_tapas": 150, "coste_items": {"piezas_metal": 10, "jeringilla": 2}, "descripcion": "Mesa de trabajo"},
            2: {"bonus_exp_pct": 20, "coste_tapas": 280, "coste_items": {"piezas_metal": 20, "jeringilla": 5}, "descripcion": "Laboratorio básico"},
            3: {"bonus_exp_pct": 35, "coste_tapas": 450, "coste_items": {"piezas_metal": 35, "jeringilla": 8}, "descripcion": "Centro de investigación"},
            4: {"bonus_exp_pct": 55, "coste_tapas": 700, "coste_items": {"piezas_metal": 50, "morfina": 10},  "descripcion": "Instituto científico"},
            5: {"bonus_exp_pct": 80, "coste_tapas": 1000,"coste_items": {"piezas_metal": 75, "morfina": 20},  "descripcion": "Laboratorio secreto militar"},
        }
    },
}

# ── OLEADAS DE ATAQUE ZOMBIE ──────────────────────────────────────────────────
# Escalado automático según la puntuación total de la base del jugador
# (suma de niveles de todas las estructuras × 10)

OLEADAS = {
    # (nivel_oleada): datos del ataque
    1: {
        "nombre": "🟢 Oleada Menor",
        "descripcion": "Un pequeño grupo de caminantes rondando la zona.",
        "zombies": [("zombie_caminante", 3)],
        "daño_base": 20,
        "tapas_robadas_pct": 15,   # % de tapas en inventario (NO almacén) que se pierden si la base cae
        "emoji": "🟢",
        "puntuacion_min": 0,
    },
    2: {
        "nombre": "🟡 Oleada Moderada",
        "descripcion": "Corredores y caminantes. Parecen atraídos por el ruido del generador.",
        "zombies": [("zombie_caminante", 4), ("zombie_corredor", 2)],
        "daño_base": 45,
        "tapas_robadas_pct": 20,
        "emoji": "🟡",
        "puntuacion_min": 20,
    },
    3: {
        "nombre": "🟠 Oleada Fuerte",
        "descripcion": "Una horda mezclada con un Barrigón a la cabeza.",
        "zombies": [("zombie_caminante", 5), ("zombie_corredor", 3), ("zombie_gordo", 1)],
        "daño_base": 80,
        "tapas_robadas_pct": 25,
        "emoji": "🟠",
        "puntuacion_min": 40,
    },
    4: {
        "nombre": "🔴 Oleada Peligrosa",
        "descripcion": "Zombies blindados lideran la carga. Tu muro sufrirá mucho.",
        "zombies": [("zombie_corredor", 4), ("zombie_gordo", 2), ("zombie_blindado", 1)],
        "daño_base": 130,
        "tapas_robadas_pct": 30,
        "emoji": "🔴",
        "puntuacion_min": 70,
    },
    5: {
        "nombre": "🔴 Oleada Masiva",
        "descripcion": "Una horda masiva. Hay un Titán entre ellos.",
        "zombies": [("zombie_corredor", 5), ("zombie_blindado", 2), ("zombie_titan", 1)],
        "daño_base": 200,
        "tapas_robadas_pct": 35,
        "emoji": "☠️",
        "puntuacion_min": 100,
    },
}

def calcular_nivel_oleada(puntuacion_base):
    """Devuelve el nivel de oleada adecuado según la puntuación de la base."""
    nivel = 1
    for n, datos in sorted(OLEADAS.items()):
        if puntuacion_base >= datos["puntuacion_min"]:
            nivel = n
    return nivel

def calcular_puntuacion_base(estructuras_dict):
    """Suma de (nivel × 10) de todas las estructuras. Mide cuán desarrollada está la base."""
    return sum(nivel * 10 for nivel in estructuras_dict.values() if nivel > 0)

# Intervalo entre ataques automáticos (en segundos)
# 6 horas por defecto — cambiar a gusto
INTERVALO_ATAQUE_HORAS = 6
INTERVALO_ATAQUE_SEG   = INTERVALO_ATAQUE_HORAS * 3600

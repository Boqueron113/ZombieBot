"""
Datos de NPCs del refugio, trabajos y NPCs de zonas
"""
import random

# ── NPCS DEL REFUGIO ──────────────────────────────────────────────────────────
NPCS_REFUGIO = {
    "medico": {
        "nombre": "Dr. Ramírez",
        "titulo": "🩺 El Médico",
        "descripcion": "Un cirujano de urgencias que sobrevivió al brote. Cura heridas y vende suministros médicos.",
        "emoji": "🩺",
        "saludo": [
            "Otro superviviente con heridas. Siéntate, te echo un vistazo.",
            "El refugio tiene suerte de tenerme. Tú también.",
            "Rápido, no tengo todo el día. ¿Qué necesitas?",
        ],
        "servicios": ["curar_completo", "comprar_medico", "mejorar_vida_max"],
        "color": 0x1abc9c,
    },
    "armero": {
        "nombre": "La Capitana Vega",
        "titulo": "🔫 La Armera",
        "descripcion": "Exmilitar. Conoce cada arma que existe y sabe cómo mejorarlas.",
        "emoji": "🔫",
        "saludo": [
            "¿Vienes a por armamento? Buena decisión.",
            "Mis armas no fallan. Mis clientes a veces sí.",
            "El acero habla más que las palabras. ¿Qué buscas?",
        ],
        "servicios": ["comprar_armas", "mejorar_arma", "comprar_municion"],
        "color": 0xe74c3c,
    },
    "comerciante": {
        "nombre": "Don Aurelio",
        "titulo": "💰 El Comerciante",
        "descripcion": "Un viejo mercader que tiene de todo. Sus precios son... negociables.",
        "emoji": "💰",
        "saludo": [
            "¡Bienvenido, bienvenido! ¿Qué puedo ofrecerte hoy?",
            "El comercio es lo que mantiene vivo a este refugio. Y a mí.",
            "Tengo de todo. Si no lo tengo, no lo necesitas.",
        ],
        "servicios": ["tienda_general", "vender_items", "trueque"],
        "color": 0xf39c12,
    },
    "lider": {
        "nombre": "Comandante Orozco",
        "titulo": "👑 El Líder",
        "descripcion": "Dirige el refugio con mano firme. Tiene misiones de alto riesgo y recompensas únicas.",
        "emoji": "👑",
        "saludo": [
            "No tengo tiempo para charlas. ¿Vienes a ayudar al refugio o no?",
            "Cada superviviente tiene un rol aquí. El tuyo aún está por definirse.",
            "El refugio necesita gente de acción. ¿Eres tú esa persona?",
        ],
        "servicios": ["misiones_elite", "ver_ranking", "recompensas_refugio"],
        "color": 0x8e44ad,
    },
    "informante": {
        "nombre": "La Sombra",
        "titulo": "🕵️ El Informante",
        "descripcion": "Nadie sabe su nombre real. Tiene información sobre zonas secretas y rutas seguras.",
        "emoji": "🕵️",
        "saludo": [
            "Shh. No tan alto. Hay oídos por todas partes.",
            "La información vale más que las tapas en este mundo.",
            "¿Buscas algo que otros no quieren que encuentres?",
        ],
        "servicios": ["pistas_zonas", "vender_mapas", "info_zombies"],
        "color": 0x2c3e50,
    },
    "ingeniero": {
        "nombre": "Profesora Kira",
        "titulo": "⚙️ La Ingeniera",
        "descripcion": "Exingeniera aeroespacial. Puede mejorar tu base y fabricar equipamiento especial.",
        "emoji": "⚙️",
        "saludo": [
            "La ciencia nos salvará. O nos matará. Pero primero nos salvará.",
            "¿Necesitas algo construido o reparado? Estás en el lugar correcto.",
            "El caos tiene solución. Solo hay que aplicar la ingeniería correcta.",
        ],
        "servicios": ["mejorar_base", "fabricar_items", "reparar_muro"],
        "color": 0x3498db,
    },
}

# ── TRABAJOS DEL REFUGIO ──────────────────────────────────────────────────────
# Cada trabajo tiene: nombre, descripcion, recompensa_tapas, recompensa_exp,
# recompensa_item (opcional), cooldown_horas, nivel_min, riesgo
TRABAJOS = {
    "guardia": {
        "nombre": "🛡️ Turno de guardia",
        "descripcion": "Patrullas el perímetro del refugio durante unas horas. Aburrido pero seguro.",
        "recompensa_tapas": (20, 40),
        "recompensa_exp": 15,
        "recompensa_item": None,
        "cooldown_horas": 2,
        "nivel_min": 1,
        "riesgo": "bajo",
        "npc": "lider",
    },
    "medico_ayudante": {
        "nombre": "🩹 Asistente médico",
        "descripcion": "Ayudas al Dr. Ramírez con las curas. Aprendes mucho y ganas algo.",
        "recompensa_tapas": (15, 30),
        "recompensa_exp": 25,
        "recompensa_item": "venda",
        "cooldown_horas": 3,
        "nivel_min": 1,
        "riesgo": "bajo",
        "npc": "medico",
    },
    "reparador": {
        "nombre": "⚙️ Reparador de equipos",
        "descripcion": "Ayudas a Kira a reparar generadores y estructuras. Trabajo duro pero bien pagado.",
        "recompensa_tapas": (30, 60),
        "recompensa_exp": 20,
        "recompensa_item": "piezas_metal",
        "cooldown_horas": 4,
        "nivel_min": 2,
        "riesgo": "medio",
        "npc": "ingeniero",
    },
    "comercio": {
        "nombre": "💼 Ayudante de comercio",
        "descripcion": "Gestionas el inventario de Don Aurelio. Recibes una comisión generosa.",
        "recompensa_tapas": (40, 80),
        "recompensa_exp": 10,
        "recompensa_item": None,
        "cooldown_horas": 4,
        "nivel_min": 1,
        "riesgo": "bajo",
        "npc": "comerciante",
    },
    "explorador_info": {
        "nombre": "🗺️ Recopilador de información",
        "descripcion": "La Sombra te paga por detalles de zonas que has visitado. Bien pagado.",
        "recompensa_tapas": (50, 100),
        "recompensa_exp": 30,
        "recompensa_item": None,
        "cooldown_horas": 6,
        "nivel_min": 2,
        "riesgo": "bajo",
        "npc": "informante",
    },
    "entrenador": {
        "nombre": "🎯 Instructor de combate",
        "descripcion": "Entrenas a los nuevos supervivientes. Necesitas experiencia pero la recompensa es alta.",
        "recompensa_tapas": (60, 120),
        "recompensa_exp": 40,
        "recompensa_item": "municion",
        "cooldown_horas": 8,
        "nivel_min": 3,
        "riesgo": "bajo",
        "npc": "armero",
    },
    "mision_peligrosa": {
        "nombre": "⚠️ Misión de recuperación",
        "descripcion": "El Comandante necesita que recuperes suministros de fuera. Peligroso pero muy lucrativo.",
        "recompensa_tapas": (100, 200),
        "recompensa_exp": 80,
        "recompensa_item": "morfina",
        "cooldown_horas": 12,
        "nivel_min": 4,
        "riesgo": "alto",
        "npc": "lider",
    },
}

# ── NPCS DE ZONAS ─────────────────────────────────────────────────────────────
# Aparecen aleatoriamente al explorar. Ofrecen misiones únicas de un solo uso.
NPCS_ZONAS = {
    "hospital": [
        {
            "id": "npc_enfermera",
            "nombre": "👩‍⚕️ Enfermera superviviente",
            "descripcion": "Una enfermera atrapada en el hospital te pide ayuda.",
            "dialogo": "¡Por favor! Llevo días aquí. Necesito que elimines los zombies del ala norte para poder escapar. Te daré todo lo que encontré.",
            "mision": {
                "titulo": "Rescate en el hospital",
                "tipo": "matar_zombies",
                "objetivo": 5,
                "zona": "hospital",
                "recompensa_tapas": 80,
                "recompensa_exp": 60,
                "recompensa_item": "jeringilla",
            }
        },
        {
            "id": "npc_paciente",
            "nombre": "🤒 Paciente superviviente",
            "descripcion": "Un hombre herido te pide medicinas.",
            "dialogo": "Estoy infectado... no, espera, solo es fiebre normal. Necesito morfina. Si me consigues 2 unidades te doy lo que encontré en la farmacia.",
            "mision": {
                "titulo": "Medicina urgente",
                "tipo": "recolectar_items",
                "objetivo_item": "morfina",
                "objetivo": 2,
                "zona": "hospital",
                "recompensa_tapas": 50,
                "recompensa_exp": 40,
                "recompensa_item": "venda",
            }
        },
    ],
    "supermercado": [
        {
            "id": "npc_familia",
            "nombre": "👨‍👩‍👧 Familia superviviente",
            "descripcion": "Una familia escondida en el almacén te pide comida.",
            "dialogo": "Llevamos 3 días sin comer. Si nos consigues 5 comidas te diremos dónde escondemos nuestras provisiones.",
            "mision": {
                "titulo": "Alimentar a la familia",
                "tipo": "recolectar_items",
                "objetivo_item": "comida",
                "objetivo": 5,
                "zona": "supermercado",
                "recompensa_tapas": 60,
                "recompensa_exp": 45,
                "recompensa_item": "conservas",
            }
        },
    ],
    "armeria": [
        {
            "id": "npc_soldado",
            "nombre": "💂 Soldado herido",
            "descripcion": "Un soldado atrapado necesita munición para escapar.",
            "dialogo": "Me quedé sin balas hace horas. Hay una horda bloqueando la salida. Elimínalos y te doy acceso al armero.",
            "mision": {
                "titulo": "Eliminar la horda",
                "tipo": "matar_zombies",
                "objetivo": 8,
                "zona": "armeria",
                "recompensa_tapas": 100,
                "recompensa_exp": 70,
                "recompensa_item": "rifle",
            }
        },
    ],
    "universidad": [
        {
            "id": "npc_profesor",
            "nombre": "🎓 Profesor superviviente",
            "descripcion": "Un profesor de química te ofrece un trato.",
            "dialogo": "Tengo la fórmula para un antídoto pero necesito materiales del laboratorio. Tráeme lo que encuentres y compartiré el resultado.",
            "mision": {
                "titulo": "Materiales de laboratorio",
                "tipo": "explorar_zonas",
                "objetivo": 3,
                "zona": "universidad",
                "recompensa_tapas": 90,
                "recompensa_exp": 80,
                "recompensa_item": "jeringilla",
            }
        },
    ],
    "fabrica": [
        {
            "id": "npc_obrero",
            "nombre": "👷 Obrero superviviente",
            "descripcion": "Un obrero conoce un pasaje secreto en la fábrica.",
            "dialogo": "Conozco cada rincón de esta fábrica. Te digo por dónde salir si me ayudas a recuperar mis herramientas.",
            "mision": {
                "titulo": "Las herramientas del obrero",
                "tipo": "recolectar_items",
                "objetivo_item": "piezas_metal",
                "objetivo": 8,
                "zona": "fabrica",
                "recompensa_tapas": 120,
                "recompensa_exp": 90,
                "recompensa_item": "mapa_bunker",
            }
        },
    ],
    "cementerio": [
        {
            "id": "npc_anciano",
            "nombre": "👴 Anciano misterioso",
            "descripcion": "Un anciano que parece saber demasiado sobre el brote.",
            "dialogo": "Yo lo vi todo desde el principio. El laboratorio... todo empezó ahí. Elimina al Paciente Cero y te daré las coordenadas.",
            "mision": {
                "titulo": "El origen del brote",
                "tipo": "matar_jefe",
                "objetivo_zombie": "zombie_jefe",
                "objetivo": 1,
                "zona": "cementerio",
                "recompensa_tapas": 300,
                "recompensa_exp": 400,
                "recompensa_item": "mapa_laboratorio",
            }
        },
    ],
}

# Probabilidad de encontrar un NPC al explorar cada zona
PROB_NPC_ZONA = {
    "hospital":     0.15,
    "supermercado": 0.12,
    "armeria":      0.12,
    "universidad":  0.10,
    "fabrica":      0.08,
    "cementerio":   0.06,
}

def get_npc_zona_aleatorio(zona_id):
    """Devuelve un NPC aleatorio para la zona, o None."""
    if zona_id not in NPCS_ZONAS:
        return None
    if random.random() > PROB_NPC_ZONA.get(zona_id, 0):
        return None
    return random.choice(NPCS_ZONAS[zona_id])

def get_trabajos_disponibles(nivel_jugador, n=3):
    """Devuelve N trabajos aleatorios disponibles para el nivel del jugador."""
    disponibles = [
        (tid, t) for tid, t in TRABAJOS.items()
        if t["nivel_min"] <= nivel_jugador
    ]
    if not disponibles:
        return []
    random.shuffle(disponibles)
    return disponibles[:min(n, len(disponibles))]

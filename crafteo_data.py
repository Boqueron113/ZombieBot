"""
crafteo_data.py — Sistema de crafteo completo
Incluye recetas base + comida cocinada + gadgets + vehículos + mejoras
"""

# ═══════════════════════════════════════════════════════════════════════════════
# RECETAS BASE
# ═══════════════════════════════════════════════════════════════════════════════
# Formato de cada receta:
#   "item_id": {
#       "ingredientes": {"mat_id": cantidad, ...},
#       "cantidad_resultado": int,
#       "nivel_min": int,
#       "descripcion": str,
#   }

RECETAS = {
    # ── ARMAS DE FUEGO ────────────────────────────────────────────────────────
    "pistola_mod": {
        "ingredientes": {"pistola": 1, "cristal": 1, "tornillos": 3, "cinta_adhesiva": 2},
        "cantidad_resultado": 1,
        "nivel_min": 2,
        "descripcion": "Pistola con silenciador y mira mejorada.",
    },
    "francotirador": {
        "ingredientes": {"rifle": 1, "cristal": 2, "tornillos": 5, "cable": 2, "piezas_metal": 3},
        "cantidad_resultado": 1,
        "nivel_min": 4,
        "descripcion": "Rifle de largo alcance con mira telescópica.",
    },
    "subfusil": {
        "ingredientes": {"pistola": 1, "piezas_metal": 4, "municion": 10, "cable": 3, "tornillos": 4},
        "cantidad_resultado": 1,
        "nivel_min": 3,
        "descripcion": "Arma automática de fabricación casera.",
    },
    "lanzallamas": {
        "ingredientes": {"piezas_metal": 5, "gasolina": 4, "cable": 3, "bateria": 1, "tornillos": 5},
        "cantidad_resultado": 1,
        "nivel_min": 4,
        "descripcion": "Proyecta fuego a presión. Devastador.",
    },
    "minigun": {
        "ingredientes": {
            "piezas_metal": 10, "cable": 6, "bateria": 3,
            "municion_pesada": 20, "componentes_electronicos": 4, "tornillos": 8
        },
        "cantidad_resultado": 1,
        "nivel_min": 5,
        "descripcion": "La cúspide del armamento improvisado.",
    },

    # ── ARMAS CaC ─────────────────────────────────────────────────────────────
    "bate_clavos": {
        "ingredientes": {"madera": 2, "tornillos": 6, "piezas_metal": 1, "cinta_adhesiva": 1},
        "cantidad_resultado": 1,
        "nivel_min": 1,
        "descripcion": "Bate de béisbol mejorado con clavos.",
    },
    "lanza": {
        "ingredientes": {"madera": 2, "piezas_metal": 2, "cinta_adhesiva": 2},
        "cantidad_resultado": 1,
        "nivel_min": 1,
        "descripcion": "Tubo de metal afilado montado en palo.",
    },
    "sierra_circular": {
        "ingredientes": {"piezas_metal": 4, "bateria": 1, "cable": 2, "tornillos": 4, "componentes_electronicos": 1},
        "cantidad_resultado": 1,
        "nivel_min": 3,
        "descripcion": "Sierra eléctrica adaptada para combate.",
    },

    # ── ARMAS ESPECIALES ──────────────────────────────────────────────────────
    "granada": {
        "ingredientes": {"piezas_metal": 2, "polvo_negro": 3, "tornillos": 2, "quimico_base": 1},
        "cantidad_resultado": 2,
        "nivel_min": 2,
        "descripcion": "Explosivo de fragmentación casero.",
    },
    "molotov": {
        "ingredientes": {"gasolina": 2, "tela": 1, "cinta_adhesiva": 1},
        "cantidad_resultado": 3,
        "nivel_min": 1,
        "descripcion": "Botella incendiaria. Simple y efectiva.",
    },
    "mina": {
        "ingredientes": {
            "piezas_metal": 3, "polvo_negro": 4,
            "cable": 2, "componentes_electronicos": 1, "tornillos": 3
        },
        "cantidad_resultado": 1,
        "nivel_min": 3,
        "descripcion": "Mina de presión para defender la base.",
    },
    "explosivo": {
        "ingredientes": {"polvo_negro": 5, "quimico_base": 2, "cable": 1, "tornillos": 2},
        "cantidad_resultado": 1,
        "nivel_min": 2,
        "descripcion": "Explosivo potente de fabricación casera.",
    },

    # ── ARMADURAS ─────────────────────────────────────────────────────────────
    "armadura_cuero": {
        "ingredientes": {"cuero": 4, "tela": 2, "tornillos": 3, "cinta_adhesiva": 2},
        "cantidad_resultado": 1,
        "nivel_min": 1,
        "descripcion": "Protección básica hecha con cuero curtido.",
    },
    "escudo_improvisado": {
        "ingredientes": {"piezas_metal": 3, "madera": 2, "tornillos": 4, "cinta_adhesiva": 2},
        "cantidad_resultado": 1,
        "nivel_min": 2,
        "descripcion": "Señal de tráfico reforzada.",
    },

    # ── CONSUMIBLES ───────────────────────────────────────────────────────────
    "botiquin": {
        "ingredientes": {"venda": 2, "morfina": 1, "tela": 1},
        "cantidad_resultado": 1,
        "nivel_min": 1,
        "descripcion": "Kit médico completo.",
    },
    "antidoto": {
        "ingredientes": {"quimico_base": 2, "morfina": 1, "agua": 1},
        "cantidad_resultado": 1,
        "nivel_min": 2,
        "descripcion": "Cura venenos y recupera vida.",
    },
    "adrenalina": {
        "ingredientes": {"quimico_base": 1, "jeringilla": 1, "bateria": 1},
        "cantidad_resultado": 1,
        "nivel_min": 2,
        "descripcion": "Inyección de emergencia de alta potencia.",
    },
    "racion_militar": {
        "ingredientes": {"comida": 2, "conservas": 1, "agua": 1},
        "cantidad_resultado": 2,
        "nivel_min": 1,
        "descripcion": "Ración energética compacta.",
    },
    "venda": {
        "ingredientes": {"tela": 2, "agua": 1},
        "cantidad_resultado": 3,
        "nivel_min": 1,
        "descripcion": "Vendas improvisadas con tela limpia.",
    },

    # ── MUNICIÓN ──────────────────────────────────────────────────────────────
    "municion": {
        "ingredientes": {"polvo_negro": 2, "piezas_metal": 1, "tornillos": 1},
        "cantidad_resultado": 10,
        "nivel_min": 1,
        "descripcion": "Fabricar 10 balas estándar.",
    },
    "municion_pesada": {
        "ingredientes": {"polvo_negro": 3, "piezas_metal": 2, "tornillos": 2},
        "cantidad_resultado": 5,
        "nivel_min": 2,
        "descripcion": "Fabricar 5 balas de alto calibre.",
    },

    # ── MATERIALES COMBINADOS ─────────────────────────────────────────────────
    "piezas_metal": {
        "ingredientes": {"tornillos": 5, "madera": 2, "cable": 1},
        "cantidad_resultado": 2,
        "nivel_min": 1,
        "descripcion": "Reciclar materiales en piezas de metal.",
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# RECETAS EXTRA (comida, gadgets, vehículos, mejoras, drogas)
# ═══════════════════════════════════════════════════════════════════════════════

RECETAS_COMIDA = {
    "sopa_supervivencia": {
        "ingredientes": {"comida": 2, "agua": 1},
        "cantidad_resultado": 1,
        "nivel_min": 1,
        "descripcion": "Sopa básica de supervivencia.",
    },
    "estofado_carne": {
        "ingredientes": {"comida_enlatada": 2, "conservas": 1, "agua": 1},
        "cantidad_resultado": 1,
        "nivel_min": 2,
        "descripcion": "Estofado nutritivo y caliente.",
    },
    "barra_energia": {
        "ingredientes": {"comida": 1, "agua": 1},
        "cantidad_resultado": 2,
        "nivel_min": 1,
        "descripcion": "Barrita energética compacta.",
    },
    "festin_apocalipsis": {
        "ingredientes": {"comida_enlatada": 3, "conservas": 2, "agua": 2, "racion_militar": 1},
        "cantidad_resultado": 1,
        "nivel_min": 3,
        "descripcion": "El mejor festín posible en el apocalipsis.",
    },
    "cafe_negro": {
        "ingredientes": {"agua": 2, "comida": 1},
        "cantidad_resultado": 2,
        "nivel_min": 1,
        "descripcion": "Café fuerte que despierta a cualquiera.",
    },
    # Drogas crafteables
    "serum_berserker": {
        "ingredientes": {"quimico_base": 2, "morfina": 1, "bateria": 1, "jeringilla": 1},
        "cantidad_resultado": 1,
        "nivel_min": 3,
        "descripcion": "Sérum que potencia la agresividad.",
    },
    "escudo_quimico": {
        "ingredientes": {"quimico_base": 2, "agua": 1, "jeringilla": 1, "tela": 1},
        "cantidad_resultado": 1,
        "nivel_min": 3,
        "descripcion": "Compuesto que endurece la piel temporalmente.",
    },
    "anfetamina": {
        "ingredientes": {"quimico_base": 3, "bateria": 1, "jeringilla": 1},
        "cantidad_resultado": 1,
        "nivel_min": 4,
        "descripcion": "Estimulante de combate extremo.",
    },
    # Gadgets crafteables
    "camara_vigilancia": {
        "ingredientes": {"componentes_electronicos": 2, "cable": 2, "bateria": 1, "cristal": 1},
        "cantidad_resultado": 1,
        "nivel_min": 2,
        "descripcion": "Cámara de seguridad reciclada.",
    },
    "detector_movimiento": {
        "ingredientes": {"componentes_electronicos": 3, "cable": 3, "bateria": 2},
        "cantidad_resultado": 1,
        "nivel_min": 3,
        "descripcion": "Sensor de infrarrojos improvisado.",
    },
    "alarma_perimetral": {
        "ingredientes": {"componentes_electronicos": 2, "cable": 4, "bateria": 2, "tornillos": 3},
        "cantidad_resultado": 1,
        "nivel_min": 2,
        "descripcion": "Sistema de alarma para el perímetro.",
    },
    "trampa_puas": {
        "ingredientes": {"piezas_metal": 3, "tornillos": 5, "madera": 2},
        "cantidad_resultado": 2,
        "nivel_min": 1,
        "descripcion": "Trampa simple de púas metálicas.",
    },
    "drone": {
        "ingredientes": {
            "componentes_electronicos": 4, "bateria": 3,
            "cable": 3, "piezas_metal": 3, "tornillos": 6
        },
        "cantidad_resultado": 1,
        "nivel_min": 4,
        "descripcion": "Dron de reconocimiento casero.",
    },
    # Vehículos crafteables
    "moto": {
        "ingredientes": {
            "piezas_metal": 8, "gasolina": 4, "cable": 3,
            "bateria": 2, "tornillos": 8, "componentes_electronicos": 2
        },
        "cantidad_resultado": 1,
        "nivel_min": 3,
        "descripcion": "Moto reconstruida de piezas.",
    },
    "camioneta": {
        "ingredientes": {
            "piezas_metal": 15, "gasolina": 6, "cable": 5,
            "bateria": 3, "tornillos": 12, "componentes_electronicos": 4, "cuero": 2
        },
        "cantidad_resultado": 1,
        "nivel_min": 4,
        "descripcion": "Camioneta reconstruida y blindada.",
    },
    # Ropa crafteables
    "guantes_tacticos": {
        "ingredientes": {"cuero": 2, "tela": 1, "tornillos": 2},
        "cantidad_resultado": 1,
        "nivel_min": 1,
        "descripcion": "Guantes de combate con refuerzo.",
    },
    "capa_sigilo": {
        "ingredientes": {"tela": 4, "cuero": 2, "cinta_adhesiva": 2, "cable": 1},
        "cantidad_resultado": 1,
        "nivel_min": 3,
        "descripcion": "Capa con propiedades anti-ruido.",
    },
    # Items mejorables
    "hacha_reforzada": {
        "ingredientes": {"hacha": 1, "piezas_metal": 3, "tornillos": 4, "cinta_adhesiva": 2},
        "cantidad_resultado": 1,
        "nivel_min": 2,
        "descripcion": "Hacha con mango de acero reforzado.",
    },
    "hacha_devastadora": {
        "ingredientes": {"hacha_reforzada": 1, "piezas_metal": 5, "cable": 2, "quimico_base": 1},
        "cantidad_resultado": 1,
        "nivel_min": 3,
        "descripcion": "Hacha definitiva.",
    },
    "pistola_v2": {
        "ingredientes": {"pistola_mod": 1, "piezas_metal": 4, "cristal": 1, "tornillos": 3},
        "cantidad_resultado": 1,
        "nivel_min": 3,
        "descripcion": "Pistola con cañón extendido.",
    },
    "pistola_v3": {
        "ingredientes": {"pistola_v2": 1, "piezas_metal": 6, "componentes_electronicos": 2, "cristal": 2},
        "cantidad_resultado": 1,
        "nivel_min": 4,
        "descripcion": "Pistola al límite de lo posible.",
    },
    "kevlar_v2": {
        "ingredientes": {"chaleco_kevlar": 1, "piezas_metal": 5, "tela": 3, "tornillos": 4},
        "cantidad_resultado": 1,
        "nivel_min": 3,
        "descripcion": "Kevlar con refuerzo de metal.",
    },
    "kevlar_v3": {
        "ingredientes": {"kevlar_v2": 1, "piezas_metal": 8, "componentes_electronicos": 2, "cuero": 3},
        "cantidad_resultado": 1,
        "nivel_min": 4,
        "descripcion": "La mejor armadura posible.",
    },
    # Armas degradables crafteables
    "sierra_motosierra": {
        "ingredientes": {
            "piezas_metal": 5, "cable": 3, "bateria": 2,
            "gasolina": 2, "tornillos": 5, "componentes_electronicos": 1
        },
        "cantidad_resultado": 1,
        "nivel_min": 3,
        "descripcion": "Motosierra improvisada de combate.",
    },
    "arco_improvisado": {
        "ingredientes": {"madera": 3, "tela": 2, "cinta_adhesiva": 2, "cuero": 1},
        "cantidad_resultado": 1,
        "nivel_min": 1,
        "descripcion": "Arco silencioso de madera y cuerda.",
    },
    "chaleco_improvisado": {
        "ingredientes": {"cuero": 3, "tela": 3, "piezas_metal": 2, "tornillos": 3},
        "cantidad_resultado": 1,
        "nivel_min": 2,
        "descripcion": "Chaleco de protección artesanal.",
    },
    "hacha_guerra": {
        "ingredientes": {"piezas_metal": 4, "madera": 2, "tornillos": 5, "cinta_adhesiva": 2},
        "cantidad_resultado": 1,
        "nivel_min": 2,
        "descripcion": "Hacha de doble filo para combate.",
    },
}

# Fusionar todas las recetas en un solo diccionario
RECETAS.update(RECETAS_COMIDA)


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES DE CONSULTA
# ═══════════════════════════════════════════════════════════════════════════════

def get_receta(item_id):
    """Devuelve la receta de un item o None si no existe."""
    return RECETAS.get(item_id)


def get_recetas_disponibles(nivel_jugador):
    """Devuelve todas las recetas accesibles para el nivel dado."""
    return {k: v for k, v in RECETAS.items() if v["nivel_min"] <= nivel_jugador}

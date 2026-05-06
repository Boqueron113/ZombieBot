import discord
from discord.ext import commands
import random
from game_data import ZONAS, ZOMBIES, ITEMS, EVENTOS_ALEATORIOS, DROPS_MAPAS_SECRETOS
from npc_data import get_npc_zona_aleatorio
from base_data import ESTRUCTURAS

IMAGENES_ZONAS = {
    "refugio": [
        "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80",
        "https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=800&q=80",
        "https://images.unsplash.com/photo-1517999144091-3d9dca6d1e43?w=800&q=80",
    ],
    "hospital": [
        "https://images.unsplash.com/photo-1587351021759-3e566b3db4f1?w=800&q=80",
        "https://images.unsplash.com/photo-1516549655169-df83a0774514?w=800&q=80",
        "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?w=800&q=80",
    ],
    "supermercado": [
        "https://images.unsplash.com/photo-1542838132-92c53300491e?w=800&q=80",
        "https://images.unsplash.com/photo-1578916171728-46686eac8d58?w=800&q=80",
        "https://images.unsplash.com/photo-1604719312566-8912e9227c6a?w=800&q=80",
    ],
    "armeria": [
        "https://images.unsplash.com/photo-1595590424283-b8f17842773f?w=800&q=80",
        "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=800&q=80",
        "https://images.unsplash.com/photo-1509726697960-b95fc52e5b8b?w=800&q=80",
    ],
    "universidad": [
        "https://images.unsplash.com/photo-1562774053-701939374585?w=800&q=80",
        "https://images.unsplash.com/photo-1541339907198-e08756dedf3f?w=800&q=80",
        "https://images.unsplash.com/photo-1498243691581-b145c3f54a5a?w=800&q=80",
    ],
    "fabrica": [
        "https://images.unsplash.com/photo-1513828583688-c52646db42da?w=800&q=80",
        "https://images.unsplash.com/photo-1565688534245-05d6b5be184a?w=800&q=80",
        "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=800&q=80",
    ],
    "cementerio": [
        "https://images.unsplash.com/photo-1509128841709-6c13b25058a3?w=800&q=80",
        "https://images.unsplash.com/photo-1508739773434-c26b3d09e071?w=800&q=80",
        "https://images.unsplash.com/photo-1604076913837-52ab5629fbc9?w=800&q=80",
    ],
    "bunker": [
        "https://images.unsplash.com/photo-1608501078713-8e445a709b39?w=800&q=80",
        "https://images.unsplash.com/photo-1587382668141-f3ca17e69b19?w=800&q=80",
        "https://images.unsplash.com/photo-1518709414768-a88981a4515d?w=800&q=80",
    ],
    "base_militar": [
        "https://images.unsplash.com/photo-1580901368919-7738efb0f87e?w=800&q=80",
        "https://images.unsplash.com/photo-1533430803441-4e96867bc4c8?w=800&q=80",
        "https://images.unsplash.com/photo-1547483238-f400e65ccd56?w=800&q=80",
    ],
    "laboratorio": [
        "https://images.unsplash.com/photo-1576086213369-97a306d36557?w=800&q=80",
        "https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?w=800&q=80",
        "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=800&q=80",
    ],
    "aeropuerto": [
        "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=800&q=80",
        "https://images.unsplash.com/photo-1544098485-2a2f6dbe1f20?w=800&q=80",
        "https://images.unsplash.com/photo-1530521954074-e64f6810b32d?w=800&q=80",
    ],
    "metro": [
        "https://images.unsplash.com/photo-1555636222-cae831e670b3?w=800&q=80",
        "https://images.unsplash.com/photo-1565043589221-1a6fd9ae45c7?w=800&q=80",
    ],
    "estadio": [
        "https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=800&q=80",
        "https://images.unsplash.com/photo-1540747913346-19212a4b9859?w=800&q=80",
    ],
    "parque_atracciones": [
        "https://images.unsplash.com/photo-1567552890835-2c9c6ad82e63?w=800&q=80",
        "https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=800&q=80",
    ],
    "centro_comercial": [
        "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=800&q=80",
        "https://images.unsplash.com/photo-1519566335946-e6f65f0f4fdf?w=800&q=80",
    ],
    "bosque": [
        "https://images.unsplash.com/photo-1448375240586-882707db888b?w=800&q=80",
        "https://images.unsplash.com/photo-1542273917363-3b1817f69a2d?w=800&q=80",
    ],
    "rio": [
        "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80",
        "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=800&q=80",
    ],
    "montana": [
        "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800&q=80",
        "https://images.unsplash.com/photo-1486870591958-9b9d0d1dda99?w=800&q=80",
    ],
    "granja": [
        "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=800&q=80",
        "https://images.unsplash.com/photo-1574943320219-553eb213f72d?w=800&q=80",
    ],
    "prision": [
        "https://images.unsplash.com/photo-1572803487765-ae9b6e7cf8db?w=800&q=80",
        "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=800&q=80",
    ],
    "base_naval": [
        "https://images.unsplash.com/photo-1529253355930-ddbe423a2ac7?w=800&q=80",
        "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=800&q=80",
    ],
    "bunker_gobierno": [
        "https://images.unsplash.com/photo-1518709414768-a88981a4515d?w=800&q=80",
        "https://images.unsplash.com/photo-1587382668141-f3ca17e69b19?w=800&q=80",
    ],
    "nave_caida": [
        "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&q=80",
        "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=800&q=80",
    ],
    "catacumbas": [
        "https://images.unsplash.com/photo-1509128841709-6c13b25058a3?w=800&q=80",
        "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800&q=80",
    ],
    "torre_control": [
        "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800&q=80",
        "https://images.unsplash.com/photo-1569163139599-0f4517e36f51?w=800&q=80",
    ],
}

# ── IMÁGENES DE ZOMBIES ───────────────────────────────────────────────────────
IMAGENES_ZOMBIES = {
    "zombie_caminante":   "https://images.unsplash.com/photo-1509248961158-e54f6934749c?w=800&q=80",
    "zombie_corredor":    "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800&q=80",
    "zombie_gordo":       "https://images.unsplash.com/photo-1604076913837-52ab5629fbc9?w=800&q=80",
    "zombie_policia":     "https://images.unsplash.com/photo-1568572933382-74d440642117?w=800&q=80",
    "zombie_enfermero":   "https://images.unsplash.com/photo-1587351021759-3e566b3db4f1?w=800&q=80",
    "zombie_doctor":      "https://images.unsplash.com/photo-1516549655169-df83a0774514?w=800&q=80",
    "zombie_blindado":    "https://images.unsplash.com/photo-1533430803441-4e96867bc4c8?w=800&q=80",
    "zombie_quimico":     "https://images.unsplash.com/photo-1576086213369-97a306d36557?w=800&q=80",
    "zombie_industrial":  "https://images.unsplash.com/photo-1565688534245-05d6b5be184a?w=800&q=80",
    "zombie_anciano":     "https://images.unsplash.com/photo-1508739773434-c26b3d09e071?w=800&q=80",
    "zombie_titan":       "https://images.unsplash.com/photo-1547483238-f400e65ccd56?w=800&q=80",
    "zombie_jefe":        "https://images.unsplash.com/photo-1509128841709-6c13b25058a3?w=800&q=80",
    "zombie_subterraneo": "https://images.unsplash.com/photo-1555636222-cae831e670b3?w=800&q=80",
    "zombie_payaso":      "https://images.unsplash.com/photo-1567552890835-2c9c6ad82e63?w=800&q=80",
    "zombie_salvaje":     "https://images.unsplash.com/photo-1448375240586-882707db888b?w=800&q=80",
    "zombie_acuatico":    "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800&q=80",
    "zombie_congelado":   "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800&q=80",
    "zombie_granjero":    "https://images.unsplash.com/photo-1574943320219-553eb213f72d?w=800&q=80",
    "zombie_preso":       "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=800&q=80",
    "zombie_guardia":     "https://images.unsplash.com/photo-1572803487765-ae9b6e7cf8db?w=800&q=80",
    "zombie_marinero":    "https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=800&q=80",
    "zombie_agente":      "https://images.unsplash.com/photo-1587382668141-f3ca17e69b19?w=800&q=80",
    "zombie_mutado":      "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=800&q=80",
    "zombie_alien":       "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&q=80",
    "zombie_esqueleto":   "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800&q=80",
    "zombie_tecnico":     "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800&q=80",
    # fallback
    "_default":           "https://images.unsplash.com/photo-1509248961158-e54f6934749c?w=800&q=80",
}

# ── IMÁGENES DE EVENTOS ───────────────────────────────────────────────────────
IMAGENES_EVENTOS = {
    "superviviente":    "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80",
    "trampa":           "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=800&q=80",
    "caja_suministros": "https://images.unsplash.com/photo-1607082348824-0a96f2a4b9da?w=800&q=80",
    "horda":            "https://images.unsplash.com/photo-1604076913837-52ab5629fbc9?w=800&q=80",
    "tapas_escondidas": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&q=80",
    "radio":            "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&q=80",
    "nada":             None,  # sin imagen especial, usa la de la zona
}

# ── IMÁGENES DE MAPAS SECRETOS ────────────────────────────────────────────────
IMAGENES_MAPAS = {
    "mapa_bunker":       "https://images.unsplash.com/photo-1608501078713-8e445a709b39?w=800&q=80",
    "mapa_militar":      "https://images.unsplash.com/photo-1580901368919-7738efb0f87e?w=800&q=80",
    "mapa_laboratorio":  "https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?w=800&q=80",
    "mapa_aeropuerto":   "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=800&q=80",
    "mapa_naval":        "https://images.unsplash.com/photo-1529253355930-ddbe423a2ac7?w=800&q=80",
    "mapa_gobierno":     "https://images.unsplash.com/photo-1518709414768-a88981a4515d?w=800&q=80",
    "mapa_nave":         "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&q=80",
    "mapa_catacumbas":   "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800&q=80",
}


class Mapa(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _jugador_tiene_item(self, jugador, item_id):
        return jugador["inventario"].get(item_id, 0) > 0

    @commands.command(name="mapa")
    async def mapa(self, ctx):
        """Muestra el mapa de zonas disponibles"""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)
        nivel_jugador = jugador["nivel"] if jugador else 1
        inv = jugador["inventario"] if jugador else {}

        embed = discord.Embed(
            title="🗺️ MAPA DEL APOCALIPSIS",
            description="Zonas disponibles para explorar. Las zonas 🔐 requieren un mapa especial.",
            color=0x2c3e50
        )

        zonas_normales = []
        zonas_secretas = []
        for zona_id, zona in ZONAS.items():
            if zona.get("requiere_item"):
                zonas_secretas.append((zona_id, zona))
            else:
                zonas_normales.append((zona_id, zona))

        for zona_id, zona in zonas_normales:
            peligro_str = "🟢 Seguro" if zona["peligro"] == 0 else "⚠️" * min(zona["peligro"], 5)
            accesible = nivel_jugador >= zona["nivel_min"]
            bloqueo = "" if accesible else f" *(Nivel {zona['nivel_min']} requerido)*"
            recursos_str = ", ".join(zona["recursos"]) if zona["recursos"] else "Ninguno"
            embed.add_field(
                name=f"{zona['emoji']} {zona['nombre']}{bloqueo}",
                value=(
                    f"*{zona['descripcion']}*\n"
                    f"Peligro: {peligro_str} | Recursos: `{recursos_str}`\n"
                    f"`!explorar {zona_id}`"
                ),
                inline=False
            )

        embed.add_field(
            name="━━━━━━━━━━━━━━━━━━━━━━━",
            value="**🔐 ZONAS SECRETAS** — Requieren mapa especial",
            inline=False
        )
        for zona_id, zona in zonas_secretas:
            requiere = zona["requiere_item"]
            tiene_mapa = inv.get(requiere, 0) > 0
            item_mapa = ITEMS.get(requiere, {})
            if tiene_mapa:
                peligro_str = "⚠️" * min(zona["peligro"], 5)
                recursos_str = ", ".join(zona["recursos"])
                embed.add_field(
                    name=f"{zona['emoji']} {zona['nombre']} ✅ DESBLOQUEADA",
                    value=(
                        f"*{zona['descripcion']}*\n"
                        f"Peligro: {peligro_str} | Recursos: `{recursos_str}`\n"
                        f"`!explorar {zona_id}`"
                    ),
                    inline=False
                )
            else:
                embed.add_field(
                    name="❓ Zona Desconocida",
                    value=(
                        f"*Localización sin confirmar. Necesitas:* {item_mapa.get('emoji','📜')} **{item_mapa.get('nombre','Mapa Secreto')}**\n"
                        f"*Búscalo explorando zonas peligrosas.*"
                    ),
                    inline=False
                )

        embed.set_image(url="https://images.unsplash.com/photo-1590073242678-70ee3fc28e8e?w=800&q=80")
        embed.set_footer(text="💡 !explorar <zona> para explorar • Los mapas secretos caen en zonas de alto peligro")
        await ctx.send(embed=embed)

    @commands.command(name="ubicacion", aliases=["donde"])
    async def ubicacion(self, ctx):
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)
        if not jugador:
            await ctx.send("❌ Usa `!crear` para comenzar.")
            return
        zona_id = jugador["zona"]
        zona = ZONAS.get(zona_id, ZONAS["refugio"])
        embed = discord.Embed(
            title="📍 Ubicación actual",
            description=f"Estás en: **{zona['nombre']}**\n*{zona['descripcion']}*",
            color=zona["color"]
        )
        imagen = random.choice(IMAGENES_ZONAS.get(zona_id, IMAGENES_ZONAS["refugio"]))
        embed.set_image(url=imagen)
        embed.set_footer(text=f"Usa !explorar {zona_id} para buscar recursos o zombies")
        await ctx.send(embed=embed)

    @commands.command(name="explorar")
    async def explorar(self, ctx, zona_id: str = None):
        """Explora una zona del mapa"""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)

        if not jugador:
            await ctx.send("❌ Usa `!crear` para comenzar.")
            return
        if jugador["estado"] == "muerto":
            await ctx.send("💀 Estás muerto. No puedes explorar.\nUsa `!revivir` si está disponible.")
            return
        if jugador["vida"] <= 0:
            await ctx.send("❤️ No tienes suficiente vida para explorar. Cúrate primero con `!curar`.")
            return
        if jugador.get("cansancio", 0) >= 100:
            embed = discord.Embed(
                title="😴 Demasiado cansado",
                description="Llevas más de **32 horas** sin dormir. Usa `!dormir` para recuperarte.",
                color=0x6c3483
            )
            await ctx.send(embed=embed)
            return
        if jugador.get("atrincherando", 0):
            await ctx.send("⚠️ Estás atrincherado. Usa `!retirar_atrincheramiento` para volver.")
            return
        if jugador.get("entrenando", 0):
            await ctx.send("⚠️ Estás entrenando. Usa `!parar_entrenamiento` primero.")
            return

        if zona_id is None:
            zona_id = jugador["zona"]
        zona_id = zona_id.lower()

        if zona_id not in ZONAS:
            await ctx.send(f"❌ Zona no encontrada. Usa `!mapa` para ver las zonas.")
            return

        zona = ZONAS[zona_id]

        if jugador["nivel"] < zona["nivel_min"]:
            await ctx.send(
                f"❌ Necesitas **Nivel {zona['nivel_min']}** para explorar **{zona['nombre']}**.\n"
                f"Tu nivel: **{jugador['nivel']}**"
            )
            return

        requiere_item = zona.get("requiere_item")
        if requiere_item and not self._jugador_tiene_item(jugador, requiere_item):
            item_data = ITEMS.get(requiere_item, {})
            embed = discord.Embed(
                title="🔐 Zona Bloqueada",
                description=(
                    f"Necesitas: {item_data.get('emoji','📜')} **{item_data.get('nombre','Mapa Secreto')}** para acceder.\n"
                    f"*Explora zonas peligrosas para encontrarlo.*"
                ),
                color=0x4a235a
            )
            await ctx.send(embed=embed)
            return

        db.update_jugador(ctx.author.id, zona=zona_id)

        # Hospital base
        if zona_id == 'refugio':
            base = db.get_base(ctx.author.id)
            if base:
                nivel_hosp = base['estructuras'].get('hospital_base', 0)
                if nivel_hosp > 0 and jugador['vida'] < jugador['vida_max']:
                    curacion = ESTRUCTURAS['hospital_base']['niveles'][nivel_hosp]['curacion_auto']
                    nueva_vida = min(jugador['vida'] + curacion, jugador['vida_max'])
                    db.update_jugador(ctx.author.id, vida=nueva_vida)
                    jugador['vida'] = nueva_vida

        completadas = db.actualizar_progreso_mision(ctx.author.id, "explorar_zonas")

        embed = discord.Embed(
            title=f"{zona['emoji']} Explorando {zona['nombre']}",
            color=zona["color"]
        )

        # Imagen por defecto: la zona
        imagen_actual = random.choice(IMAGENES_ZONAS.get(zona_id, IMAGENES_ZONAS["refugio"]))
        resultado_texto = []
        imagen_prioridad = None  # Si hay evento/zombie especial, cambia la imagen

        # ── Evento aleatorio ──────────────────────────────────────────────────
        evento = self._elegir_evento()
        resultado_texto.append(f"📌 **Evento:** {evento['descripcion']}")

        # Imagen del evento si no es "nada"
        if evento["id"] != "nada" and evento["id"] in IMAGENES_EVENTOS:
            img_evento = IMAGENES_EVENTOS[evento["id"]]
            if img_evento:
                imagen_prioridad = img_evento

        if evento["efecto"] == "items":
            for item_id, cant in evento["items"].items():
                db.add_item_inventario(ctx.author.id, item_id, cant)
                item_nombre = ITEMS.get(item_id, {}).get("nombre", item_id)
                resultado_texto.append(f"  ➕ {item_nombre} x{cant}")
        elif evento["efecto"] == "daño":
            dano = evento["valor"]
            nueva_vida = max(jugador["vida"] - dano, 0)
            db.update_jugador(ctx.author.id, vida=nueva_vida)
            resultado_texto.append(f"  💔 Pierdes {dano} de vida. Vida restante: {nueva_vida}")
            jugador["vida"] = nueva_vida
        elif evento["efecto"] == "tapas":
            tapas = evento["valor"]
            db.update_jugador(ctx.author.id, tapas=jugador["tapas"] + tapas)
            resultado_texto.append(f"  💰 Ganas {tapas} tapas")

        # ── Recursos de la zona ───────────────────────────────────────────────
        if zona["recursos"] and zona_id != "refugio":
            recursos_encontrados = {}
            for recurso in zona["recursos"]:
                if random.random() < 0.45:
                    cant = random.randint(1, 3)
                    recursos_encontrados[recurso] = cant
                    db.add_item_inventario(ctx.author.id, recurso, cant)
            if recursos_encontrados:
                items_str = "\n".join(
                    f"  ➕ {ITEMS.get(k, {}).get('nombre', k)} x{v}"
                    for k, v in recursos_encontrados.items()
                )
                resultado_texto.append(f"\n🗃️ **Recursos recolectados:**\n{items_str}")
                if "comida" in recursos_encontrados or "conservas" in recursos_encontrados:
                    total = recursos_encontrados.get("comida",0) + recursos_encontrados.get("conservas",0)
                    db.actualizar_progreso_mision(ctx.author.id, "recolectar_comida", total)
                if "municion" in recursos_encontrados:
                    db.actualizar_progreso_mision(ctx.author.id, "recolectar_municion", recursos_encontrados["municion"])
            else:
                resultado_texto.append("\n📭 No encontraste recursos en esta exploración.")

        # ── Drop de mapa secreto ──────────────────────────────────────────────
        if zona_id in DROPS_MAPAS_SECRETOS:
            mapa_id, prob = DROPS_MAPAS_SECRETOS[zona_id]
            if random.random() < prob and not self._jugador_tiene_item(jugador, mapa_id):
                db.add_item_inventario(ctx.author.id, mapa_id)
                item_mapa = ITEMS.get(mapa_id, {})
                resultado_texto.append(
                    f"\n🌟 **¡HALLAZGO SECRETO!** {item_mapa.get('emoji','📜')} **{item_mapa.get('nombre','')}**\n"
                    f"*{item_mapa.get('descripcion','')}*\n"
                    f"Usa `!mapa` para ver la zona desbloqueada."
                )
                # Imagen del mapa secreto encontrado
                if mapa_id in IMAGENES_MAPAS:
                    imagen_prioridad = IMAGENES_MAPAS[mapa_id]

        # ── Drop legendario ───────────────────────────────────────────────────
        if zona_id != "refugio":
            try:
                from game_data import DROPS_LEGENDARIOS
                if zona_id in DROPS_LEGENDARIOS:
                    for leg_id, leg_prob in DROPS_LEGENDARIOS[zona_id]:
                        if random.random() < leg_prob and not self._jugador_tiene_item(jugador, leg_id):
                            db.add_item_inventario(ctx.author.id, leg_id)
                            leg_item = ITEMS.get(leg_id, {})
                            resultado_texto.append(
                                f"\n🌟✨ **¡¡ITEM LEGENDARIO!!** {leg_item.get('emoji','⭐')} **{leg_item.get('nombre',leg_id)}**\n"
                                f"*{leg_item.get('descripcion','')}*"
                            )
            except Exception:
                pass

        # ── NPC de zona ───────────────────────────────────────────────────────
        if zona_id != "refugio" and jugador["vida"] > 0:
            npc_zona = get_npc_zona_aleatorio(zona_id)
            if npc_zona:
                npcs_cog = self.bot.get_cog("NPCs")
                if npcs_cog:
                    npcs_cog.registrar_npc_zona(ctx.author.id, npc_zona)
                resultado_texto.append(
                    f"\n👤 **¡Encuentro!** {npc_zona['nombre']} está aquí.\n"
                    f"*{npc_zona['descripcion']}*\n"
                    f"Usa `!hablar_npc` para interactuar o `!rechazar_npc` para ignorar."
                )

        npcs_cog = self.bot.get_cog("NPCs")
        if npcs_cog:
            npcs_cog.actualizar_progreso_npc(ctx.author.id, "explorar", zona=zona_id)

        # ── Encuentro con zombie ──────────────────────────────────────────────
        zombie_id = None
        if zona["zombies"] and zona_id != "refugio" and jugador["vida"] > 0:
            if random.random() < 0.55:
                zombie_id = random.choice(zona["zombies"])
                zombie = ZOMBIES[zombie_id]
                resultado_texto.append(
                    f"\n⚠️ **¡ALERTA!** Un **{zombie['nombre']}** bloquea tu camino.\n"
                    f"*{zombie['descripcion']}*\n"
                    f"Usa `!atacar` para combatir o `!huir` para escapar."
                )
                db.update_jugador(ctx.author.id, estado="en_combate")
                if not hasattr(self.bot, "_combates"):
                    self.bot._combates = {}
                self.bot._combates[str(ctx.author.id)] = {
                    "zombie_id": zombie_id,
                    "zombie_vida": zombie["vida"]
                }
                # Imagen del zombie tiene máxima prioridad
                imagen_prioridad = IMAGENES_ZOMBIES.get(zombie_id, IMAGENES_ZOMBIES["_default"])

        # Misiones completadas
        if completadas:
            for mid in completadas:
                mision = db.get_mision(mid)
                if mision:
                    resultado_texto.append(f"\n✅ **¡Misión completada!** {mision['titulo']} — usa `!entregar`")

        embed.description = "\n".join(resultado_texto)

        # Aplicar imagen — zombie > mapa > evento > zona
        embed.set_image(url=imagen_prioridad if imagen_prioridad else imagen_actual)

        if jugador["vida"] > 0:
            db.actualizar_progreso_mision(ctx.author.id, "sobrevivir_exploraciones")

        jugador_actualizado = db.get_jugador(ctx.author.id)
        embed.set_footer(text=f"❤️ Vida: {jugador_actualizado['vida']}/{jugador_actualizado['vida_max']} | 💰 Tapas: {jugador_actualizado['tapas']}")
        await ctx.send(embed=embed)

    def _elegir_evento(self):
        rand = random.random()
        acumulado = 0
        for evento in EVENTOS_ALEATORIOS:
            acumulado += evento["probabilidad"]
            if rand <= acumulado:
                return evento
        return EVENTOS_ALEATORIOS[-1]

async def setup(bot):
    await bot.add_cog(Mapa(bot))

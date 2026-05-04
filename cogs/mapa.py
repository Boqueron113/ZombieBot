import discord
from discord.ext import commands
import random
from game_data import ZONAS, ZOMBIES, ITEMS, EVENTOS_ALEATORIOS
from base_data import ESTRUCTURAS

# ── IMÁGENES POR ZONA ────────────────────────────────────────────────────────
# Cada zona tiene varias imágenes — se elige una al azar cada vez que explores
# para que no se repita siempre la misma. Añade o cambia URLs a tu gusto.
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
}

class Mapa(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="mapa")
    async def mapa(self, ctx):
        """Muestra el mapa de zonas disponibles"""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)

        embed = discord.Embed(
            title="🗺️ MAPA DEL APOCALIPSIS",
            description="Zonas disponibles para explorar. Elige bien, la muerte es permanente.",
            color=0x2c3e50
        )

        nivel_jugador = jugador["nivel"] if jugador else 1

        for zona_id, zona in ZONAS.items():
            peligro_str = "🟢 Seguro" if zona["peligro"] == 0 else "⚠️" * min(zona["peligro"], 5)
            accesible = nivel_jugador >= zona["nivel_min"]
            bloqueo = "" if accesible else f" *(Nivel {zona['nivel_min']} requerido)*"
            recursos_str = ", ".join(zona["recursos"]) if zona["recursos"] else "Ninguno"

            embed.add_field(
                name=f"{zona['emoji']} {zona['nombre']}{bloqueo}",
                value=(
                    f"*{zona['descripcion']}*\n"
                    f"Peligro: {peligro_str}\n"
                    f"Recursos: `{recursos_str}`\n"
                    f"Comando: `!explorar {zona_id}`"
                ),
                inline=False
            )

        # Imagen del mapa general — paisaje post-apocalíptico
        embed.set_image(url="https://images.unsplash.com/photo-1590073242678-70ee3fc28e8e?w=800&q=80")
        embed.set_footer(text="💡 Usa !explorar <zona> para explorar • !ubicacion para ver dónde estás")
        await ctx.send(embed=embed)

    @commands.command(name="ubicacion", aliases=["donde"])
    async def ubicacion(self, ctx):
        """Muestra tu ubicación actual"""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)

        if not jugador:
            await ctx.send("❌ Usa `!crear` para comenzar.")
            return

        zona_id = jugador["zona"]
        zona = ZONAS.get(zona_id, ZONAS["refugio"])

        embed = discord.Embed(
            title=f"📍 Ubicación actual",
            description=f"Estás en: **{zona['nombre']}**\n*{zona['descripcion']}*",
            color=zona["color"]
        )

        # Imagen de la zona actual
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

        if zona_id is None:
            zona_id = jugador["zona"]

        zona_id = zona_id.lower()
        if zona_id not in ZONAS:
            zonas_lista = ", ".join(ZONAS.keys())
            await ctx.send(f"❌ Zona no encontrada. Zonas disponibles: `{zonas_lista}`")
            return

        zona = ZONAS[zona_id]

        if jugador["nivel"] < zona["nivel_min"]:
            await ctx.send(
                f"❌ Necesitas **Nivel {zona['nivel_min']}** para explorar **{zona['nombre']}**.\n"
                f"Tu nivel actual: **{jugador['nivel']}**"
            )
            return

        # Mover jugador a la zona
        db.update_jugador(ctx.author.id, zona=zona_id)

        # ── Hospital base: curación automática al regresar al refugio ──
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

        # ── Imagen aleatoria de la zona ────────────────────────
        imagen_zona = random.choice(IMAGENES_ZONAS.get(zona_id, IMAGENES_ZONAS["refugio"]))
        embed.set_image(url=imagen_zona)

        resultado_texto = []

        # ── Evento aleatorio ──────────────────────────────────
        evento = self._elegir_evento()
        resultado_texto.append(f"📌 **Evento:** {evento['descripcion']}")

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

        # ── Recursos de la zona ───────────────────────────────
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
                    total_comida = recursos_encontrados.get("comida", 0) + recursos_encontrados.get("conservas", 0)
                    db.actualizar_progreso_mision(ctx.author.id, "recolectar_comida", total_comida)
                if "municion" in recursos_encontrados:
                    db.actualizar_progreso_mision(ctx.author.id, "recolectar_municion", recursos_encontrados["municion"])
            else:
                resultado_texto.append("\n📭 No encontraste recursos en esta exploración.")

        # ── Posible encuentro con zombie ──────────────────────
        if zona["zombies"] and zona_id != "refugio" and jugador["vida"] > 0:
            if random.random() < 0.55:
                zombie_id = random.choice(zona["zombies"])
                zombie = ZOMBIES[zombie_id]
                resultado_texto.append(
                    f"\n⚠️ **¡ALERTA!** Un **{zombie['nombre']}** bloquea tu camino.\n"
                    f"Usa `!atacar` para combatir o `!huir` para escapar."
                )
                db.update_jugador(ctx.author.id, estado="en_combate")
                if not hasattr(self.bot, "_combates"):
                    self.bot._combates = {}
                self.bot._combates[str(ctx.author.id)] = {
                    "zombie_id": zombie_id,
                    "zombie_vida": zombie["vida"]
                }

        # ── Misiones completadas ──────────────────────────────
        if completadas:
            for mid in completadas:
                mision = db.get_mision(mid)
                if mision:
                    resultado_texto.append(f"\n✅ **¡Misión completada!** {mision['titulo']} — usa `!entregar`")

        embed.description = "\n".join(resultado_texto)

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

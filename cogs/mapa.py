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
    # Zonas secretas
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
            requiere = zona.get("requiere_item")
            if requiere:
                zonas_secretas.append((zona_id, zona))
            else:
                zonas_normales.append((zona_id, zona))

        # Zonas normales
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

        # Zonas secretas
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
                    name=f"❓ Zona Desconocida",
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

        if zona_id is None:
            zona_id = jugador["zona"]

        zona_id = zona_id.lower()
        if zona_id not in ZONAS:
            zonas_lista = ", ".join(ZONAS.keys())
            await ctx.send(f"❌ Zona no encontrada. Zonas disponibles: `{zonas_lista}`")
            return

        zona = ZONAS[zona_id]

        # ── Verificar nivel mínimo ────────────────────────────
        if jugador["nivel"] < zona["nivel_min"]:
            await ctx.send(
                f"❌ Necesitas **Nivel {zona['nivel_min']}** para explorar **{zona['nombre']}**.\n"
                f"Tu nivel actual: **{jugador['nivel']}**"
            )
            return

        # ── Verificar mapa secreto ────────────────────────────
        requiere_item = zona.get("requiere_item")
        if requiere_item and not self._jugador_tiene_item(jugador, requiere_item):
            item_data = ITEMS.get(requiere_item, {})
            embed = discord.Embed(
                title="🔐 Zona Bloqueada",
                description=(
                    f"Esta zona está oculta en el mapa.\n\n"
                    f"Necesitas: {item_data.get('emoji','📜')} **{item_data.get('nombre','Mapa Secreto')}** para acceder.\n\n"
                    f"*Explora zonas de alto peligro para encontrarlo como drop raro.*"
                ),
                color=0x4a235a
            )
            await ctx.send(embed=embed)
            return

        # Mover jugador a la zona
        db.update_jugador(ctx.author.id, zona=zona_id)

        # ── Hospital base: curación automática al refugio ─────
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

        # Imagen de la zona
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

        # ── Drop de mapa secreto ──────────────────────────────
        if zona_id in DROPS_MAPAS_SECRETOS:
            mapa_id, prob = DROPS_MAPAS_SECRETOS[zona_id]
            # Solo cae si el jugador no lo tiene ya
            if random.random() < prob and not self._jugador_tiene_item(jugador, mapa_id):
                db.add_item_inventario(ctx.author.id, mapa_id)
                item_mapa = ITEMS.get(mapa_id, {})
                resultado_texto.append(
                    f"\n🌟 **¡HALLAZGO SECRETO!** Encontraste {item_mapa.get('emoji','📜')} **{item_mapa.get('nombre','Mapa Secreto')}**\n"
                    f"*{item_mapa.get('descripcion','')}*\n"
                    f"Usa `!mapa` para ver la zona desbloqueada."
                )

        # ── Drop de items legendarios ─────────────────────
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

        # ── Posible encuentro con NPC de zona ───────────────────
        if zona_id != "refugio" and jugador["vida"] > 0:
            npc_zona = get_npc_zona_aleatorio(zona_id)
            if npc_zona:
                # Registrar NPC en el cog de NPCs
                npcs_cog = self.bot.get_cog("NPCs")
                if npcs_cog:
                    npcs_cog.registrar_npc_zona(ctx.author.id, npc_zona)
                resultado_texto.append(
                    f"\n👤 **¡Encuentro!** {npc_zona['nombre']} está aquí.\n"
                    f"*{npc_zona['descripcion']}*\n"
                    f"Usa `!hablar_npc` para interactuar o `!rechazar_npc` para ignorar."
                )

        # ── Actualizar progreso misión NPC ────────────────────
        npcs_cog = self.bot.get_cog("NPCs")
        if npcs_cog:
            npcs_cog.actualizar_progreso_npc(ctx.author.id, "explorar", zona=zona_id)

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

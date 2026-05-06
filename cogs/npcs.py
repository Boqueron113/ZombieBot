import discord
from discord.ext import commands
import random
from datetime import datetime, timezone, timedelta
from npc_data import (
    NPCS_REFUGIO, TRABAJOS, NPCS_ZONAS,
    get_trabajos_disponibles, get_npc_zona_aleatorio
)
from game_data import ITEMS, ZONAS


class NPCs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Cache de trabajos ofrecidos: {discord_id: [(trabajo_id, trabajo), ...]}
        self._trabajos_cache = {}
        # Cache de NPCs de zona activos: {discord_id: npc_data}
        self._npcs_zona_cache = {}

    # ─────────────────────────────────────────────────────────────────────────
    # REFUGIO — VER NPCS
    # ─────────────────────────────────────────────────────────────────────────

    @commands.command(name="refugio", aliases=["npcs", "habitantes"])
    async def ver_refugio(self, ctx):
        """Muestra los NPCs disponibles en el refugio."""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)

        if not jugador:
            await ctx.send("❌ Usa `!crear` para comenzar.")
            return

        if jugador["zona"] != "refugio":
            await ctx.send("❌ Tienes que estar en el **Refugio Central** para hablar con los habitantes.\nUsa `!explorar refugio`.")
            return

        embed = discord.Embed(
            title="🏚️ Habitantes del Refugio",
            description="Habla con los supervivientes del refugio. Cada uno tiene algo que ofrecerte.",
            color=0x2d5a1b
        )

        for npc_id, npc in NPCS_REFUGIO.items():
            saludo = random.choice(npc["saludo"])
            embed.add_field(
                name=f"{npc['emoji']} {npc['titulo']} — {npc['nombre']}",
                value=(
                    f"*\"{saludo}\"*\n"
                    f"{npc['descripcion']}\n"
                    f"`!hablar {npc_id}`"
                ),
                inline=False
            )

        embed.set_footer(text="!trabajar para buscar trabajo • !hablar <npc> para interactuar")
        await ctx.send(embed=embed)

    @commands.command(name="hablar")
    async def hablar(self, ctx, npc_id: str = None):
        """Habla con un NPC del refugio."""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)

        if not jugador:
            await ctx.send("❌ Usa `!crear` para comenzar.")
            return

        if jugador["zona"] != "refugio":
            await ctx.send("❌ Tienes que estar en el **Refugio Central** para hablar con los NPCs.")
            return

        if not npc_id:
            await ctx.send("❌ Indica con quién quieres hablar. Usa `!refugio` para ver los NPCs disponibles.")
            return

        npc_id = npc_id.lower()
        npc = NPCS_REFUGIO.get(npc_id)
        if not npc:
            ids = ", ".join(f"`{k}`" for k in NPCS_REFUGIO)
            await ctx.send(f"❌ NPC no encontrado. Opciones: {ids}")
            return

        saludo = random.choice(npc["saludo"])
        embed = discord.Embed(
            title=f"{npc['emoji']} {npc['titulo']} — {npc['nombre']}",
            description=f"*\"{saludo}\"*\n\n{npc['descripcion']}",
            color=npc["color"]
        )

        # Servicios del NPC
        servicios_txt = self._get_servicios_txt(npc_id, jugador)
        embed.add_field(name="📋 Servicios disponibles", value=servicios_txt, inline=False)
        embed.set_footer(text=f"Estás hablando con {npc['nombre']}")
        await ctx.send(embed=embed)

    def _get_servicios_txt(self, npc_id, jugador):
        servicios = {
            "medico": (
                "`!curarse_medico` — Curación completa (50 tapas)\n"
                "`!mejorar_vida` — +20 vida máxima permanente (200 tapas)\n"
                "`!comprar venda` — Comprar vendas en la tienda"
            ),
            "armero": (
                "`!comprar pistola` — Comprar armas\n"
                "`!comprar municion` — Comprar munición\n"
                "`!tienda` — Ver tienda completa"
            ),
            "comerciante": (
                "`!tienda` — Ver tienda general\n"
                "`!vender <item>` — Vender items\n"
                "`!trueque` — Intercambiar items (próximamente)"
            ),
            "lider": (
                "`!misiones` — Ver misiones del refugio\n"
                "`!ranking` — Ver ranking de supervivientes\n"
                "`!trabajar` — Buscar trabajo en el refugio"
            ),
            "informante": (
                "`!pistas` — Pistas sobre zonas secretas (30 tapas)\n"
                "`!comprar_mapa <zona>` — Comprar mapa secreto\n"
                "`!info_zombie <nombre>` — Info sobre un zombie"
            ),
            "ingeniero": (
                "`!estructuras` — Ver estructuras de la base\n"
                "`!construir <id>` — Mejorar estructura\n"
                "`!reparar` — Reparar el muro"
            ),
        }
        return servicios.get(npc_id, "Sin servicios disponibles.")

    # ─────────────────────────────────────────────────────────────────────────
    # SERVICIOS ESPECIALES DE NPCS
    # ─────────────────────────────────────────────────────────────────────────

    @commands.command(name="curarse_medico", aliases=["curacion_completa"])
    async def curarse_medico(self, ctx):
        """El médico te cura completamente (50 tapas)."""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)

        if not jugador:
            await ctx.send("❌ Usa `!crear` para comenzar.")
            return
        if jugador["zona"] != "refugio":
            await ctx.send("❌ El médico solo está en el refugio.")
            return
        if jugador["vida"] >= jugador["vida_max"]:
            await ctx.send("✅ Ya tienes la vida al máximo. El Dr. Ramírez te mira con desaprobación.")
            return

        costo = 50
        if jugador["tapas"] < costo:
            await ctx.send(f"❌ El Dr. Ramírez cobra **{costo} tapas**. Tienes **{jugador['tapas']}**.")
            return

        db.update_jugador(ctx.author.id,
            vida=jugador["vida_max"],
            tapas=jugador["tapas"] - costo
        )
        embed = discord.Embed(
            title="🩺 Dr. Ramírez",
            description=(
                f"*\"Listo. Procura no volver tan destrozado.\"*\n\n"
                f"❤️ Vida: **{jugador['vida']} → {jugador['vida_max']}/{jugador['vida_max']}**\n"
                f"💰 Pagaste: **{costo} tapas**"
            ),
            color=0x1abc9c
        )
        await ctx.send(embed=embed)

    @commands.command(name="mejorar_vida", aliases=["upgrade_vida"])
    async def mejorar_vida(self, ctx):
        """El médico aumenta tu vida máxima permanentemente (200 tapas)."""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)

        if not jugador:
            await ctx.send("❌ Usa `!crear` para comenzar.")
            return
        if jugador["zona"] != "refugio":
            await ctx.send("❌ El médico solo está en el refugio.")
            return

        costo = 200
        if jugador["tapas"] < costo:
            await ctx.send(f"❌ Cuesta **{costo} tapas**. Tienes **{jugador['tapas']}**.")
            return

        nueva_vida_max = jugador["vida_max"] + 20
        db.update_jugador(ctx.author.id,
            vida_max=nueva_vida_max,
            vida=min(jugador["vida"] + 20, nueva_vida_max),
            tapas=jugador["tapas"] - costo
        )
        embed = discord.Embed(
            title="💉 Mejora médica",
            description=(
                f"*\"Te he inyectado un estimulante celular. Experimental, pero funciona.\"*\n\n"
                f"❤️ Vida máxima: **{jugador['vida_max']} → {nueva_vida_max}**\n"
                f"💰 Pagaste: **{costo} tapas**"
            ),
            color=0x1abc9c
        )
        await ctx.send(embed=embed)

    @commands.command(name="pistas")
    async def pistas(self, ctx):
        """El Informante te da una pista sobre zonas secretas (30 tapas)."""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)

        if not jugador:
            await ctx.send("❌ Usa `!crear` para comenzar.")
            return
        if jugador["zona"] != "refugio":
            await ctx.send("❌ El Informante solo está en el refugio.")
            return

        costo = 30
        if jugador["tapas"] < costo:
            await ctx.send(f"❌ La Sombra cobra **{costo} tapas** por información. Tienes **{jugador['tapas']}**.")
            return

        db.update_jugador(ctx.author.id, tapas=jugador["tapas"] - costo)

        pistas_lista = [
            "He oído que en el **cementerio** hay un anciano que sabe dónde está el laboratorio secreto...",
            "Los soldados de la **armería** a veces llevan mapas militares clasificados encima.",
            "En la **fábrica** hay un obrero que conoce un pasaje hacia el búnker del gobierno.",
            "Dicen que en la **universidad** hay un profesor que investiga el origen del virus.",
            "Explora zonas de alto peligro. Los zombies más fuertes suelen llevar documentos clasificados.",
            "El **búnker** tiene suministros del gobierno que no han tocado desde el día cero.",
            "La **base militar** tiene armas que no encontrarás en ninguna tienda. Pero está muy vigilada.",
        ]

        pista = random.choice(pistas_lista)
        embed = discord.Embed(
            title="🕵️ La Sombra susurra...",
            description=f"*\"{pista}\"*",
            color=0x2c3e50
        )
        embed.set_footer(text=f"Pagaste {costo} tapas por esta información.")
        await ctx.send(embed=embed)

    @commands.command(name="comprar_mapa")
    async def comprar_mapa(self, ctx, zona: str = None):
        """Compra un mapa secreto al Informante."""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)

        if not jugador:
            await ctx.send("❌ Usa `!crear` para comenzar.")
            return
        if jugador["zona"] != "refugio":
            await ctx.send("❌ El Informante solo está en el refugio.")
            return

        mapas_disponibles = {
            "bunker":        ("mapa_bunker",       300),
            "base_militar":  ("mapa_militar",      400),
            "laboratorio":   ("mapa_laboratorio",  500),
            "aeropuerto":    ("mapa_aeropuerto",   250),
        }

        if not zona:
            embed = discord.Embed(
                title="🕵️ Mapas disponibles",
                description="*\"Tengo mapas de lugares que no encontrarás en ningún otro sitio.\"*",
                color=0x2c3e50
            )
            for zona_id, (item_id, precio) in mapas_disponibles.items():
                item = ITEMS.get(item_id, {})
                zona_data = ZONAS.get(zona_id, {})
                tiene = jugador["inventario"].get(item_id, 0) > 0
                estado = "✅ Ya lo tienes" if tiene else f"💰 {precio} tapas"
                embed.add_field(
                    name=f"{item.get('emoji','📜')} {item.get('nombre','Mapa')}",
                    value=f"Desbloquea: **{zona_data.get('nombre', zona_id)}**\n{estado} | `!comprar_mapa {zona_id}`",
                    inline=True
                )
            await ctx.send(embed=embed)
            return

        zona = zona.lower()
        if zona not in mapas_disponibles:
            await ctx.send(f"❌ No tengo ese mapa. Opciones: {', '.join(mapas_disponibles.keys())}")
            return

        item_id, precio = mapas_disponibles[zona]
        if jugador["inventario"].get(item_id, 0) > 0:
            await ctx.send("✅ Ya tienes ese mapa.")
            return
        if jugador["tapas"] < precio:
            await ctx.send(f"❌ Cuesta **{precio} tapas**. Tienes **{jugador['tapas']}**.")
            return

        db.update_jugador(ctx.author.id, tapas=jugador["tapas"] - precio)
        db.add_item_inventario(ctx.author.id, item_id)

        item = ITEMS.get(item_id, {})
        zona_data = ZONAS.get(zona, {})
        embed = discord.Embed(
            title="🗺️ Mapa adquirido",
            description=(
                f"*\"Guárdalo bien. Si alguien sabe que tienes esto...\"*\n\n"
                f"{item.get('emoji','📜')} **{item.get('nombre','Mapa')}** en tu inventario.\n"
                f"Zona desbloqueada: **{zona_data.get('nombre', zona)}**\n"
                f"💰 Pagaste: **{precio} tapas**"
            ),
            color=0x2c3e50
        )
        await ctx.send(embed=embed)

    @commands.command(name="info_zombie")
    async def info_zombie(self, ctx, *, nombre: str = None):
        """El Informante te da detalles sobre un tipo de zombie (gratis)."""
        from game_data import ZOMBIES
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)

        if not jugador:
            await ctx.send("❌ Usa `!crear` para comenzar.")
            return
        if jugador["zona"] != "refugio":
            await ctx.send("❌ El Informante solo está en el refugio.")
            return

        if not nombre:
            lista = "\n".join(f"`{k}` — {v['nombre']}" for k, v in ZOMBIES.items())
            await ctx.send(f"🕵️ Zombies conocidos:\n{lista}\n\nUsa `!info_zombie <id>`")
            return

        zombie = ZOMBIES.get(nombre.lower().replace(" ", "_"))
        if not zombie:
            await ctx.send(f"❌ No tengo información sobre `{nombre}`.")
            return

        drops_txt = "\n".join(
            f"  {ITEMS.get(k,{}).get('emoji','📦')} {ITEMS.get(k,{}).get('nombre',k)}: {int(v*100)}%"
            for k, v in zombie["drop"].items()
        )
        embed = discord.Embed(
            title=f"🕵️ Informe: {zombie['nombre']}",
            description=f"*{zombie['descripcion']}*",
            color=0x2c3e50
        )
        embed.add_field(name="📊 Stats", value=(
            f"❤️ Vida: **{zombie['vida']}**\n"
            f"⚔️ Ataque: **{zombie['ataque']}**\n"
            f"🛡️ Defensa: **{zombie['defensa']}**"
        ), inline=True)
        embed.add_field(name="🏆 Recompensas", value=(
            f"⭐ EXP: **{zombie['exp']}**\n"
            f"💰 Tapas: **{zombie['tapas'][0]}-{zombie['tapas'][1]}**"
        ), inline=True)
        embed.add_field(name="📦 Drops posibles", value=drops_txt or "Ninguno", inline=False)
        await ctx.send(embed=embed)

    # ─────────────────────────────────────────────────────────────────────────
    # TRABAJOS
    # ─────────────────────────────────────────────────────────────────────────

    @commands.command(name="trabajar", aliases=["trabajo", "trabajos"])
    async def trabajar(self, ctx):
        """Busca trabajo en el refugio. Se te ofrecen 3 opciones."""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)

        if not jugador:
            await ctx.send("❌ Usa `!crear` para comenzar.")
            return
        if jugador["zona"] != "refugio":
            await ctx.send("❌ Solo puedes buscar trabajo en el **Refugio Central**.")
            return
        if jugador.get("atrincherando", 0):
            await ctx.send("❌ Estás atrincherado. Usa `!retirar_atrincheramiento` primero.")
            return
        if jugador.get("entrenando", 0):
            await ctx.send("❌ Estás entrenando. Usa `!parar_entrenamiento` primero.")
            return

        # Obtener trabajos disponibles para el nivel
        trabajos = get_trabajos_disponibles(jugador["nivel"], n=3)
        if not trabajos:
            await ctx.send("❌ No hay trabajos disponibles para tu nivel.")
            return

        # Guardar en cache
        self._trabajos_cache[str(ctx.author.id)] = trabajos

        embed = discord.Embed(
            title="💼 Ofertas de trabajo",
            description=(
                "Los habitantes del refugio necesitan ayuda. Elige un trabajo:\n"
                "*(Usa el número para aceptar)*"
            ),
            color=0xf39c12
        )

        for i, (trabajo_id, trabajo) in enumerate(trabajos, 1):
            npc = NPCS_REFUGIO.get(trabajo["npc"], {})
            tapas_min, tapas_max = trabajo["recompensa_tapas"]
            riesgo_emoji = {"bajo": "🟢", "medio": "🟡", "alto": "🔴"}.get(trabajo["riesgo"], "⚪")
            item_txt = ""
            if trabajo["recompensa_item"]:
                item = ITEMS.get(trabajo["recompensa_item"], {})
                item_txt = f" + {item.get('emoji','📦')} {item.get('nombre', trabajo['recompensa_item'])}"

            embed.add_field(
                name=f"{i}. {trabajo['nombre']}",
                value=(
                    f"*{trabajo['descripcion']}*\n"
                    f"💰 **{tapas_min}-{tapas_max} tapas** + ⭐{trabajo['recompensa_exp']} EXP{item_txt}\n"
                    f"⏱️ Cooldown: {trabajo['cooldown_horas']}h | Riesgo: {riesgo_emoji} {trabajo['riesgo'].title()}\n"
                    f"Ofrecido por: {npc.get('emoji','')} {npc.get('nombre','')}\n"
                    f"`!aceptar_trabajo {i}`"
                ),
                inline=False
            )

        embed.set_footer(text="!aceptar_trabajo <1/2/3> para elegir")
        await ctx.send(embed=embed)

    @commands.command(name="aceptar_trabajo")
    async def aceptar_trabajo(self, ctx, numero: int = None):
        """Acepta uno de los trabajos ofrecidos."""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)

        if not jugador:
            await ctx.send("❌ Usa `!crear` para comenzar.")
            return

        trabajos = self._trabajos_cache.get(str(ctx.author.id))
        if not trabajos:
            await ctx.send("❌ No tienes trabajos pendientes. Usa `!trabajar` primero.")
            return

        if not numero or numero < 1 or numero > len(trabajos):
            await ctx.send(f"❌ Elige un número entre 1 y {len(trabajos)}.")
            return

        trabajo_id, trabajo = trabajos[numero - 1]

        # Verificar cooldown en la DB
        c = db._cur()
        c.execute(
            "SELECT fecha FROM eventos_log WHERE discord_id=%s AND tipo=%s ORDER BY fecha DESC LIMIT 1",
            (str(ctx.author.id), f"trabajo_{trabajo_id}")
        )
        ultimo = c.fetchone()
        if ultimo:
            fecha = ultimo["fecha"]
            if hasattr(fecha, 'tzinfo') and fecha.tzinfo is None:
                fecha = fecha.replace(tzinfo=timezone.utc)
            cooldown = timedelta(hours=trabajo["cooldown_horas"])
            if datetime.now(timezone.utc) - fecha < cooldown:
                restante = cooldown - (datetime.now(timezone.utc) - fecha)
                horas = int(restante.total_seconds() // 3600)
                minutos = int((restante.total_seconds() % 3600) // 60)
                await ctx.send(
                    f"⏱️ Ya hiciste este trabajo recientemente.\n"
                    f"Podrás repetirlo en **{horas}h {minutos}min**."
                )
                return

        # Ejecutar trabajo — mini evento con resultado aleatorio
        npc = NPCS_REFUGIO.get(trabajo["npc"], {})
        tapas_min, tapas_max = trabajo["recompensa_tapas"]

        # Riesgo: chance de que salga mal
        exito = True
        if trabajo["riesgo"] == "medio":
            exito = random.random() > 0.20
        elif trabajo["riesgo"] == "alto":
            exito = random.random() > 0.35

        if exito:
            tapas = random.randint(tapas_min, tapas_max)
            exp = trabajo["recompensa_exp"]
            db.update_jugador(ctx.author.id, tapas=jugador["tapas"] + tapas)
            db.add_exp(ctx.author.id, exp)

            item_txt = ""
            if trabajo["recompensa_item"]:
                db.add_item_inventario(ctx.author.id, trabajo["recompensa_item"])
                item = ITEMS.get(trabajo["recompensa_item"], {})
                item_txt = f"\n{item.get('emoji','📦')} **{item.get('nombre','')}** obtenido"

            db.log_evento(ctx.author.id, f"trabajo_{trabajo_id}", "completado")

            embed = discord.Embed(
                title=f"✅ Trabajo completado — {trabajo['nombre']}",
                description=(
                    f"{npc.get('emoji','')} *{npc.get('nombre','')} asiente satisfecho.*\n\n"
                    f"💰 Ganaste: **{tapas} tapas**\n"
                    f"⭐ EXP: **+{exp}**"
                    f"{item_txt}"
                ),
                color=0x27ae60
            )
        else:
            # Trabajo salió mal — pierdes algo de vida
            dano = random.randint(10, 25)
            nueva_vida = max(1, jugador["vida"] - dano)
            db.update_jugador(ctx.author.id, vida=nueva_vida)
            db.log_evento(ctx.author.id, f"trabajo_{trabajo_id}", "fallido")

            embed = discord.Embed(
                title=f"❌ Trabajo fallido — {trabajo['nombre']}",
                description=(
                    f"{npc.get('emoji','')} *{npc.get('nombre','')} sacude la cabeza.*\n\n"
                    f"Algo salió mal durante el trabajo. Te costó **{dano} puntos de vida**.\n"
                    f"❤️ Vida: {nueva_vida}/{jugador['vida_max']}\n\n"
                    f"*Los trabajos de riesgo {trabajo['riesgo']} a veces fallan.*"
                ),
                color=0xe74c3c
            )

        # Limpiar cache
        del self._trabajos_cache[str(ctx.author.id)]
        await ctx.send(embed=embed)

    # ─────────────────────────────────────────────────────────────────────────
    # NPCS DE ZONAS — MISIONES ÚNICAS
    # ─────────────────────────────────────────────────────────────────────────

    def registrar_npc_zona(self, discord_id, npc_data):
        """Registra un NPC de zona activo para un jugador."""
        self._npcs_zona_cache[str(discord_id)] = npc_data

    @commands.command(name="hablar_npc", aliases=["npc", "interactuar"])
    async def hablar_npc(self, ctx):
        """Habla con el NPC que encontraste en la zona."""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)

        if not jugador:
            await ctx.send("❌ Usa `!crear` para comenzar.")
            return

        npc = self._npcs_zona_cache.get(str(ctx.author.id))
        if not npc:
            await ctx.send("❌ No hay ningún NPC esperándote. Explora una zona para encontrar supervivientes.")
            return

        mision = npc.get("mision", {})
        embed = discord.Embed(
            title=f"{npc['nombre']}",
            description=(
                f"*\"{npc['dialogo']}\"*\n\n"
                f"**Misión:** {mision.get('titulo','')}\n"
                f"**Objetivo:** {self._describir_objetivo(mision)}\n"
                f"**Recompensa:**\n"
                f"💰 {mision.get('recompensa_tapas', 0)} tapas\n"
                f"⭐ {mision.get('recompensa_exp', 0)} EXP"
            ),
            color=0x8e44ad
        )
        if mision.get("recompensa_item"):
            item = ITEMS.get(mision["recompensa_item"], {})
            embed.add_field(
                name="🎁 Item especial",
                value=f"{item.get('emoji','📦')} {item.get('nombre', mision['recompensa_item'])}",
                inline=True
            )

        embed.set_footer(text="!aceptar_npc para aceptar la misión | !rechazar_npc para ignorar")
        await ctx.send(embed=embed)

    @commands.command(name="aceptar_npc")
    async def aceptar_npc(self, ctx):
        """Acepta la misión del NPC de zona."""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)

        if not jugador:
            await ctx.send("❌ Usa `!crear` para comenzar.")
            return

        npc = self._npcs_zona_cache.get(str(ctx.author.id))
        if not npc:
            await ctx.send("❌ No hay ningún NPC esperándote.")
            return

        # Verificar si ya tiene esta misión activa
        mision = npc["mision"]
        npc_id = npc["id"]
        c = db._cur()
        c.execute(
            "SELECT 1 FROM eventos_log WHERE discord_id=%s AND tipo=%s LIMIT 1",
            (str(ctx.author.id), f"npc_mision_{npc_id}")
        )
        if c.fetchone():
            await ctx.send(f"❌ Ya completaste o tienes activa la misión de **{npc['nombre']}**.")
            return

        # Registrar misión en log como activa
        db.log_evento(ctx.author.id, f"npc_mision_{npc_id}_activa", mision["titulo"])

        # Guardar datos de la misión en cache del bot para tracking
        if not hasattr(self.bot, "_misiones_npc"):
            self.bot._misiones_npc = {}
        self.bot._misiones_npc[str(ctx.author.id)] = {
            "npc_id": npc_id,
            "npc_nombre": npc["nombre"],
            "mision": mision,
            "progreso": 0
        }

        embed = discord.Embed(
            title=f"📋 Misión aceptada",
            description=(
                f"**{mision['titulo']}**\n\n"
                f"{self._describir_objetivo(mision)}\n\n"
                f"*Usa `!progreso_npc` para ver tu avance.*\n"
                f"*Usa `!entregar_npc` cuando completes el objetivo.*"
            ),
            color=0x8e44ad
        )
        del self._npcs_zona_cache[str(ctx.author.id)]
        await ctx.send(embed=embed)

    @commands.command(name="rechazar_npc")
    async def rechazar_npc(self, ctx):
        """Rechaza la misión del NPC de zona."""
        npc = self._npcs_zona_cache.pop(str(ctx.author.id), None)
        if not npc:
            await ctx.send("❌ No hay ningún NPC esperándote.")
            return
        await ctx.send(f"🚶 Ignoras a **{npc['nombre']}** y sigues tu camino.")

    @commands.command(name="progreso_npc", aliases=["mision_npc"])
    async def progreso_npc(self, ctx):
        """Ver el progreso de tu misión de NPC activa."""
        if not hasattr(self.bot, "_misiones_npc"):
            self.bot._misiones_npc = {}

        datos = self.bot._misiones_npc.get(str(ctx.author.id))
        if not datos:
            await ctx.send("❌ No tienes ninguna misión de NPC activa.")
            return

        mision = datos["mision"]
        progreso = datos["progreso"]
        objetivo = mision.get("objetivo", 1)
        barra = "🟩" * min(progreso, objetivo) + "⬛" * max(0, objetivo - progreso)

        embed = discord.Embed(
            title=f"📋 {mision['titulo']}",
            description=(
                f"Misión de: **{datos['npc_nombre']}**\n\n"
                f"Progreso: {barra} **{progreso}/{objetivo}**\n\n"
                f"{self._describir_objetivo(mision)}"
            ),
            color=0x8e44ad
        )
        embed.set_footer(text="!entregar_npc cuando completes el objetivo")
        await ctx.send(embed=embed)

    @commands.command(name="entregar_npc")
    async def entregar_npc(self, ctx):
        """Entrega la misión de NPC completada."""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)

        if not jugador:
            await ctx.send("❌ Usa `!crear` para comenzar.")
            return

        if not hasattr(self.bot, "_misiones_npc"):
            self.bot._misiones_npc = {}

        datos = self.bot._misiones_npc.get(str(ctx.author.id))
        if not datos:
            await ctx.send("❌ No tienes ninguna misión de NPC activa.")
            return

        mision = datos["mision"]
        progreso = datos["progreso"]
        objetivo = mision.get("objetivo", 1)

        # Verificar items si es misión de recolección
        if mision.get("tipo") == "recolectar_items":
            item_id = mision.get("objetivo_item")
            cantidad_inv = jugador["inventario"].get(item_id, 0)
            if cantidad_inv < objetivo:
                item = ITEMS.get(item_id, {})
                await ctx.send(
                    f"❌ Aún no tienes suficiente **{item.get('nombre', item_id)}**.\n"
                    f"Tienes: {cantidad_inv}/{objetivo}"
                )
                return
            # Consumir items
            for _ in range(objetivo):
                db.remove_item_inventario(ctx.author.id, item_id)
            progreso = objetivo

        if progreso < objetivo:
            await ctx.send(
                f"❌ Aún no completaste el objetivo.\n"
                f"Progreso: **{progreso}/{objetivo}**"
            )
            return

        # Dar recompensas
        tapas = mision.get("recompensa_tapas", 0)
        exp = mision.get("recompensa_exp", 0)
        db.update_jugador(ctx.author.id, tapas=jugador["tapas"] + tapas)
        db.add_exp(ctx.author.id, exp)

        item_txt = ""
        if mision.get("recompensa_item"):
            db.add_item_inventario(ctx.author.id, mision["recompensa_item"])
            item = ITEMS.get(mision["recompensa_item"], {})
            item_txt = f"\n{item.get('emoji','📦')} **{item.get('nombre','')}** obtenido"

        db.log_evento(ctx.author.id, f"npc_mision_{datos['npc_id']}", "completada")
        del self.bot._misiones_npc[str(ctx.author.id)]

        embed = discord.Embed(
            title=f"🏆 ¡Misión completada!",
            description=(
                f"**{mision['titulo']}**\n\n"
                f"💰 +**{tapas} tapas**\n"
                f"⭐ +**{exp} EXP**"
                f"{item_txt}"
            ),
            color=0xf1c40f
        )
        await ctx.send(embed=embed)

    # ─────────────────────────────────────────────────────────────────────────
    # UTILIDADES
    # ─────────────────────────────────────────────────────────────────────────

    def _describir_objetivo(self, mision):
        tipo = mision.get("tipo", "")
        objetivo = mision.get("objetivo", 1)
        if tipo == "matar_zombies":
            return f"⚔️ Elimina **{objetivo} zombies** en **{mision.get('zona','')}**"
        elif tipo == "recolectar_items":
            item = ITEMS.get(mision.get("objetivo_item",""), {})
            return f"📦 Consigue **{objetivo}× {item.get('nombre', mision.get('objetivo_item',''))}**"
        elif tipo == "explorar_zonas":
            return f"🗺️ Explora **{objetivo} veces** la zona **{mision.get('zona','')}**"
        elif tipo == "matar_jefe":
            from game_data import ZOMBIES
            zombie = ZOMBIES.get(mision.get("objetivo_zombie",""), {})
            return f"☠️ Elimina **{zombie.get('nombre','al jefe')}**"
        return f"Completa el objetivo: {objetivo}"

    def actualizar_progreso_npc(self, discord_id, tipo_evento, zona=None, zombie_id=None):
        """Llamado desde mapa.py/combate.py para actualizar progreso de misión NPC."""
        if not hasattr(self.bot, "_misiones_npc"):
            return
        datos = self.bot._misiones_npc.get(str(discord_id))
        if not datos:
            return

        mision = datos["mision"]
        tipo = mision.get("tipo")

        if tipo == "matar_zombies" and tipo_evento == "kill":
            if not mision.get("zona") or zona == mision.get("zona"):
                datos["progreso"] = min(datos["progreso"] + 1, mision["objetivo"])

        elif tipo == "explorar_zonas" and tipo_evento == "explorar":
            if not mision.get("zona") or zona == mision.get("zona"):
                datos["progreso"] = min(datos["progreso"] + 1, mision["objetivo"])

        elif tipo == "matar_jefe" and tipo_evento == "kill":
            if zombie_id == mision.get("objetivo_zombie"):
                datos["progreso"] = min(datos["progreso"] + 1, mision["objetivo"])


async def setup(bot):
    await bot.add_cog(NPCs(bot))

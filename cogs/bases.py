import discord
from discord.ext import commands, tasks
import asyncio
import random
from datetime import datetime, timezone
from base_data import (
    ESTRUCTURAS, OLEADAS, INTERVALO_ATAQUE_SEG,
    calcular_nivel_oleada, calcular_puntuacion_base
)
from game_data import ITEMS, ZOMBIES


class Bases(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.loop_ataque.start()

    def cog_unload(self):
        self.loop_ataque.cancel()

    # ─────────────────────────────────────────────────────────────
    # LOOP AUTOMÁTICO DE ATAQUES
    # ─────────────────────────────────────────────────────────────
    @tasks.loop(seconds=INTERVALO_ATAQUE_SEG)
    async def loop_ataque(self):
        """Lanza ataques zombie a todas las bases registradas."""
        db = self.bot.db
        bases = db.get_todas_las_bases()
        for base in bases:
            try:
                await self._ejecutar_ataque(base)
            except Exception as e:
                print(f"[ATAQUE ERROR] {base['discord_id']}: {e}")

    @loop_ataque.before_loop
    async def before_loop(self):
        await self.bot.wait_until_ready()
        # Espera 60 seg al arrancar para no atacar nada más iniciar
        await asyncio.sleep(60)

    async def _ejecutar_ataque(self, base):
        """Simula un ataque zombie a una base y notifica al jugador."""
        db = self.bot.db
        discord_id = base["discord_id"]
        jugador = db.get_jugador(discord_id)
        if not jugador:
            return

        estructuras = base["estructuras"]
        puntuacion = calcular_puntuacion_base(estructuras)
        nivel_oleada = calcular_nivel_oleada(puntuacion)
        oleada = OLEADAS[nivel_oleada]

        nivel_muro = estructuras.get("muro", 0)
        nivel_torretas = estructuras.get("torretas", 0)
        nivel_almacen = estructuras.get("almacen", 0)

        # Vida actual del muro (si no tiene muro, la base es indefensa)
        vida_muro_actual = base["vida_muro_max"] if base["vida_muro_max"] > 0 else 0

        # Daño base de la oleada
        dano_oleada = oleada["daño_base"] + random.randint(-10, 20)

        # Las torretas reducen el daño
        dano_torretas = 0
        if nivel_torretas > 0:
            datos_t = ESTRUCTURAS["torretas"]["niveles"][nivel_torretas]
            dano_torretas = datos_t["daño_por_turno"] + random.randint(0, 10)

        dano_neto = max(0, dano_oleada - dano_torretas)

        # ── Resultado del ataque ─────────────────────────────
        tapas_perdidas = 0
        recursos_perdidos = {}
        resultado = "repelido"

        if nivel_muro == 0:
            # Sin muro: la base cae siempre
            resultado = "destruida"
        else:
            vida_muro_nueva = max(0, vida_muro_actual - dano_neto)
            db.update_base(discord_id, vida_muro=vida_muro_nueva)

            if vida_muro_nueva <= 0:
                resultado = "destruida"
                # Reparar muro al 20% (queda dañado pero no a 0)
                muro_datos = ESTRUCTURAS["muro"]["niveles"][nivel_muro]
                vida_reparada = int(muro_datos["vida"] * 0.20)
                db.update_base(discord_id, vida_muro=vida_reparada)
            else:
                resultado = "repelido"

        if resultado == "destruida":
            # Robo de tapas del inventario (NO del almacén)
            pct_robo = oleada["tapas_robadas_pct"] / 100
            tapas_perdidas = int(jugador["tapas"] * pct_robo)
            nuevas_tapas = jugador["tapas"] - tapas_perdidas
            db.update_jugador(discord_id, tapas=nuevas_tapas)

            # Robo de recursos del inventario (no del almacén protegido)
            inv = jugador["inventario"]
            items_robables = [k for k, v in inv.items() if v > 0 and k not in ("venda",)]
            num_robados = min(len(items_robables), random.randint(1, 3))
            for item_id in random.sample(items_robables, num_robados):
                cant_robar = max(1, inv[item_id] // 2)
                inv[item_id] -= cant_robar
                if inv[item_id] <= 0:
                    del inv[item_id]
                recursos_perdidos[item_id] = cant_robar
            db.update_jugador(discord_id, inventario=inv)

            db.update_base(discord_id,
                ataques_recibidos=base["ataques_recibidos"] + 1,
                ultimo_ataque=datetime.now(timezone.utc).isoformat()
            )
        else:
            db.update_base(discord_id,
                ataques_repelidos=base["ataques_repelidos"] + 1,
                ultimo_ataque=datetime.now(timezone.utc).isoformat()
            )

        # Generador produce tapas pasivamente
        nivel_gen = estructuras.get("generador", 0)
        if nivel_gen > 0:
            gen_datos = ESTRUCTURAS["generador"]["niveles"][nivel_gen]
            tapas_gen = gen_datos["tapas_por_hora"] * (INTERVALO_ATAQUE_SEG // 3600)
            jugador_actualizado = db.get_jugador(discord_id)
            db.update_jugador(discord_id, tapas=jugador_actualizado["tapas"] + tapas_gen)
        else:
            tapas_gen = 0

        # Log del ataque
        db.log_ataque(discord_id, nivel_oleada, oleada["nombre"],
                      resultado, dano_neto, recursos_perdidos, tapas_perdidas)

        # Notificación al canal configurado
        canal_id = base.get("canal_notif")
        if canal_id:
            canal = self.bot.get_channel(int(canal_id))
            if canal:
                await self._enviar_notif(canal, discord_id, jugador, oleada,
                                         nivel_oleada, resultado, dano_neto,
                                         dano_torretas, tapas_perdidas,
                                         recursos_perdidos, tapas_gen, base)

    async def _enviar_notif(self, canal, discord_id, jugador, oleada,
                             nivel_oleada, resultado, dano_neto, dano_torretas,
                             tapas_perdidas, recursos_perdidos, tapas_gen, base):
        """Envía el embed de notificación de ataque al canal."""
        color = 0x2ecc71 if resultado == "repelido" else 0xe74c3c
        titulo = (
            f"{oleada['emoji']} ATAQUE REPELIDO — {oleada['nombre']}"
            if resultado == "repelido"
            else f"💥 BASE DESTRUIDA — {oleada['nombre']}"
        )

        embed = discord.Embed(title=titulo, color=color)
        embed.set_author(name=f"Base de {jugador['nombre']}")

        # Descripción de la oleada
        zombies_str = ", ".join(
            f"{ZOMBIES[zid]['nombre']} ×{n}" for zid, n in oleada["zombies"]
        )
        embed.add_field(name="🧟 Atacantes", value=zombies_str, inline=False)

        # Combate
        combate_txt = f"💥 Daño de oleada: **{dano_neto + dano_torretas}**\n"
        if dano_torretas > 0:
            combate_txt += f"🔫 Torretas neutralizaron: **{dano_torretas}**\n"
        combate_txt += f"🧱 Daño al muro: **{dano_neto}**"
        embed.add_field(name="⚔️ Combate", value=combate_txt, inline=True)

        # Resultado
        if resultado == "repelido":
            base_act = self.bot.db.get_base(discord_id)
            vida_actual = base_act["vida_muro"] if base_act else 0
            vida_max = base_act["vida_muro_max"] if base_act else 0
            res_txt = f"✅ Tu muro aguantó.\n🧱 Vida muro: **{vida_actual}/{vida_max}**"
        else:
            res_txt = "❌ Los zombies derribaron el muro.\n🧱 Muro en reparación (20% vida)."
            if tapas_perdidas:
                res_txt += f"\n💰 Tapas robadas: **{tapas_perdidas}**"
            if recursos_perdidos:
                items_str = ", ".join(
                    f"{ITEMS.get(k, {}).get('emoji','📦')} {ITEMS.get(k, {}).get('nombre', k)} ×{v}"
                    for k, v in recursos_perdidos.items()
                )
                res_txt += f"\n📦 Items robados: {items_str}"
        embed.add_field(name="📊 Resultado", value=res_txt, inline=True)

        if tapas_gen > 0:
            embed.add_field(name="⚡ Generador", value=f"+**{tapas_gen}** tapas producidas", inline=False)

        embed.set_footer(text=f"Próximo ataque en ~{INTERVALO_ATAQUE_SEG//3600}h • !base para ver tu base")
        try:
            user = await self.bot.fetch_user(int(discord_id))
            await canal.send(content=user.mention, embed=embed)
        except Exception:
            await canal.send(embed=embed)

    # ─────────────────────────────────────────────────────────────
    # COMANDOS
    # ─────────────────────────────────────────────────────────────

    @commands.command(name="fundarbase", aliases=["construirbase", "nuevabase"])
    async def fundar_base(self, ctx, *, nombre: str = None):
        """Funda tu base personal de superviviente."""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)
        if not jugador:
            await ctx.send("❌ Usa `!crear` para crear tu personaje primero.")
            return

        if db.get_base(ctx.author.id):
            await ctx.send("❌ Ya tienes una base. Usa `!base` para verla.")
            return

        nombre = nombre or f"Base de {jugador['nombre']}"
        db.crear_base(ctx.author.id, nombre)

        embed = discord.Embed(
            title="🏗️ ¡BASE FUNDADA!",
            description=(
                f"Has establecido **{nombre}** en el apocalipsis.\n\n"
                "Tu base comienza vacía y sin defensas. Los zombies atacarán periódicamente.\n"
                "Construye estructuras para sobrevivir.\n\n"
                "**Primeros pasos:**\n"
                "🧱 `!construir muro` — Construye un muro (¡primero esto!)\n"
                "⚡ `!construir generador` — Genera tapas pasivas\n"
                "📦 `!construir almacen` — Protege tus recursos\n\n"
                "⚠️ Configura dónde recibir alertas con `!base canal`"
            ),
            color=0x27ae60
        )
        embed.set_footer(text="!estructuras para ver todo lo que puedes construir")
        await ctx.send(embed=embed)

    @commands.command(name="base")
    async def ver_base(self, ctx, *, accion: str = None):
        """Ver tu base o configurarla. Uso: !base [canal]"""
        db = self.bot.db
        base = db.get_base(ctx.author.id)

        if not base:
            await ctx.send("❌ No tienes base. Usa `!fundarbase <nombre>` para crear una.")
            return

        # Subcomando: configurar canal de notificaciones
        if accion and accion.lower() == "canal":
            db.update_base(ctx.author.id, canal_notif=str(ctx.channel.id))
            await ctx.send(f"✅ Las alertas de ataque llegarán a **#{ctx.channel.name}**.")
            return

        estructuras = base["estructuras"]
        puntuacion = calcular_puntuacion_base(estructuras)
        nivel_oleada = calcular_nivel_oleada(puntuacion)
        oleada_actual = OLEADAS[nivel_oleada]

        embed = discord.Embed(
            title=f"🏠 {base['nombre']}",
            description=f"Puntuación de base: **{puntuacion}** pts | Amenaza actual: {oleada_actual['emoji']} **{oleada_actual['nombre']}**",
            color=0x2c3e50
        )

        # Estado del muro
        if estructuras.get("muro", 0) > 0:
            barra = self._barra(base["vida_muro"], base["vida_muro_max"])
            embed.add_field(
                name="🧱 Muro",
                value=f"Nv.{estructuras['muro']} | {barra} {base['vida_muro']}/{base['vida_muro_max']}",
                inline=False
            )
        else:
            embed.add_field(name="🧱 Muro", value="❌ Sin muro — ¡vulnerable!", inline=False)

        # Estructuras
        lineas = []
        for est_id, datos_est in ESTRUCTURAS.items():
            nivel = estructuras.get(est_id, 0)
            max_nivel = max(datos_est["niveles"].keys())
            if est_id == "muro":
                continue
            if nivel == 0:
                lineas.append(f"{datos_est['emoji']} **{datos_est['nombre']}** — No construida")
            elif nivel >= max_nivel:
                lineas.append(f"{datos_est['emoji']} **{datos_est['nombre']}** — Nv.{nivel} *(MAX)*")
            else:
                lineas.append(f"{datos_est['emoji']} **{datos_est['nombre']}** — Nv.{nivel}/{max_nivel}")
        embed.add_field(name="🏗️ Estructuras", value="\n".join(lineas), inline=False)

        # Almacén
        almacen = base["almacen"]
        if almacen:
            items_str = " | ".join(
                f"{ITEMS.get(k,{}).get('emoji','📦')} {ITEMS.get(k,{}).get('nombre',k)} ×{v}"
                for k, v in almacen.items()
            )
            embed.add_field(name="📦 Almacén protegido", value=items_str, inline=False)
        else:
            embed.add_field(name="📦 Almacén protegido", value="Vacío", inline=False)

        # Stats de defensa
        embed.add_field(
            name="📊 Historial",
            value=(
                f"✅ Ataques repelidos: **{base['ataques_repelidos']}**\n"
                f"💥 Ataques recibidos: **{base['ataques_recibidos']}**\n"
                f"🔔 Canal alertas: {'Configurado' if base['canal_notif'] else '❌ No configurado (`!base canal`)'}"
            ),
            inline=False
        )
        embed.set_footer(text="!estructuras • !construir <id> • !almacenar <item> <cant> • !retirar <item> <cant>")
        await ctx.send(embed=embed)

    @commands.command(name="estructuras")
    async def ver_estructuras(self, ctx):
        """Muestra todas las estructuras construibles y sus costes."""
        db = self.bot.db
        base = db.get_base(ctx.author.id)
        estructuras_jugador = base["estructuras"] if base else {e: 0 for e in ESTRUCTURAS}

        embed = discord.Embed(
            title="🏗️ CATÁLOGO DE ESTRUCTURAS",
            description="Construye y mejora estructuras para fortalecer tu base.",
            color=0x8e44ad
        )

        for est_id, datos in ESTRUCTURAS.items():
            nivel_actual = estructuras_jugador.get(est_id, 0)
            max_nivel = max(datos["niveles"].keys())
            siguiente = nivel_actual + 1

            if nivel_actual >= max_nivel:
                estado = "✅ **MÁXIMO**"
                coste_txt = "Ya está al máximo nivel."
            else:
                nivel_data = datos["niveles"][siguiente]
                items_str = " + ".join(
                    f"{ITEMS.get(k,{}).get('emoji','📦')}{v} {k}" for k, v in nivel_data["coste_items"].items()
                )
                coste_txt = f"💰 {nivel_data['coste_tapas']} tapas + {items_str}"
                estado = f"Nv.{nivel_actual}/{max_nivel}"

            embed.add_field(
                name=f"{datos['emoji']} {datos['nombre']} — {estado}",
                value=f"*{datos['descripcion']}*\n**Siguiente mejora:** {coste_txt}\nID: `{est_id}`",
                inline=False
            )

        embed.set_footer(text="!construir <id> para construir/mejorar una estructura")
        await ctx.send(embed=embed)

    @commands.command(name="construir", aliases=["mejorar"])
    async def construir(self, ctx, estructura_id: str):
        """Construye o mejora una estructura de tu base."""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)
        base = db.get_base(ctx.author.id)

        if not jugador:
            await ctx.send("❌ Usa `!crear` primero.")
            return
        if not base:
            await ctx.send("❌ Usa `!fundarbase` para crear tu base primero.")
            return

        estructura_id = estructura_id.lower()
        if estructura_id not in ESTRUCTURAS:
            ids = ", ".join(f"`{k}`" for k in ESTRUCTURAS)
            await ctx.send(f"❌ Estructura no válida. Opciones: {ids}")
            return

        datos = ESTRUCTURAS[estructura_id]
        max_nivel = max(datos["niveles"].keys())
        nivel_actual = base["estructuras"].get(estructura_id, 0)

        if nivel_actual >= max_nivel:
            await ctx.send(f"✅ **{datos['nombre']}** ya está al nivel máximo ({max_nivel}).")
            return

        siguiente = nivel_actual + 1
        nivel_data = datos["niveles"][siguiente]
        coste_tapas = nivel_data["coste_tapas"]
        coste_items = nivel_data["coste_items"]

        # Verificar tapas
        if jugador["tapas"] < coste_tapas:
            await ctx.send(
                f"❌ Necesitas **{coste_tapas} tapas**. Tienes **{jugador['tapas']}**."
            )
            return

        # Verificar items
        inv = jugador["inventario"]
        for item_id, cant_req in coste_items.items():
            if inv.get(item_id, 0) < cant_req:
                nombre_item = ITEMS.get(item_id, {}).get("nombre", item_id)
                await ctx.send(
                    f"❌ Necesitas **{cant_req}× {nombre_item}**. Tienes **{inv.get(item_id, 0)}**."
                )
                return

        # Cobrar coste
        db.update_jugador(ctx.author.id, tapas=jugador["tapas"] - coste_tapas)
        for item_id, cant in coste_items.items():
            db.remove_item_inventario(ctx.author.id, item_id, cant)

        # Actualizar estructura
        estructuras = base["estructuras"]
        estructuras[estructura_id] = siguiente
        db.update_base(ctx.author.id, estructuras=estructuras)

        # Si es el muro, actualizar vida
        if estructura_id == "muro":
            nueva_vida_max = nivel_data["vida"]
            # Mantener el porcentaje de vida al mejorar
            if base["vida_muro_max"] > 0:
                pct = base["vida_muro"] / base["vida_muro_max"]
            else:
                pct = 1.0
            nueva_vida = int(nueva_vida_max * pct)
            db.update_base(ctx.author.id, vida_muro=nueva_vida, vida_muro_max=nueva_vida_max)

        # Descripción del efecto
        efecto_txt = self._efecto_nivel(estructura_id, siguiente, nivel_data)

        embed = discord.Embed(
            title=f"🏗️ {datos['emoji']} {datos['nombre']} mejorada",
            description=(
                f"**Nivel {nivel_actual} → {siguiente}** — *{nivel_data['descripcion']}*\n\n"
                f"{efecto_txt}\n\n"
                f"💰 Gastaste: **{coste_tapas} tapas**"
            ),
            color=0x27ae60
        )
        if siguiente < max_nivel:
            sig_data = datos["niveles"][siguiente + 1]
            items_str = " + ".join(
                f"{ITEMS.get(k,{}).get('emoji','📦')}{v} {k}"
                for k, v in sig_data["coste_items"].items()
            )
            embed.set_footer(text=f"Siguiente mejora: {sig_data['coste_tapas']}💰 + {items_str}")
        else:
            embed.set_footer(text="✅ ¡Estructura al nivel máximo!")
        await ctx.send(embed=embed)

    @commands.command(name="almacenar", aliases=["depositar"])
    async def almacenar(self, ctx, item_id: str, cantidad: int = 1):
        """Mueve items de tu inventario al almacén protegido de la base."""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)
        base = db.get_base(ctx.author.id)

        if not jugador or not base:
            await ctx.send("❌ Necesitas personaje (`!crear`) y base (`!fundarbase`).")
            return

        nivel_almacen = base["estructuras"].get("almacen", 0)
        if nivel_almacen == 0:
            await ctx.send("❌ Necesitas construir un **Almacén** primero: `!construir almacen`")
            return

        # Verificar slots
        slots_max = ESTRUCTURAS["almacen"]["niveles"][nivel_almacen]["slots"]
        slots_usados = sum(base["almacen"].values())
        if slots_usados + cantidad > slots_max:
            await ctx.send(
                f"❌ El almacén está lleno. Slots: **{slots_usados}/{slots_max}**\n"
                f"Mejora el almacén con `!construir almacen` o retira items con `!retirar`."
            )
            return

        item_id = item_id.lower()
        if not db.remove_item_inventario(ctx.author.id, item_id, cantidad):
            nombre = ITEMS.get(item_id, {}).get("nombre", item_id)
            await ctx.send(f"❌ No tienes **{nombre} ×{cantidad}** en tu mochila.")
            return

        db.add_item_almacen(ctx.author.id, item_id, cantidad)
        nombre = ITEMS.get(item_id, {}).get("nombre", item_id)
        emoji = ITEMS.get(item_id, {}).get("emoji", "📦")
        prot = ESTRUCTURAS["almacen"]["niveles"][nivel_almacen]["proteccion_pct"]

        embed = discord.Embed(
            title="📦 Almacenado",
            description=(
                f"{emoji} **{nombre} ×{cantidad}** guardado en el almacén.\n"
                f"🔒 Protección: **{prot}%** contra robos de zombies."
            ),
            color=0x3498db
        )
        await ctx.send(embed=embed)

    @commands.command(name="retirar")
    async def retirar(self, ctx, item_id: str, cantidad: int = 1):
        """Retira items del almacén a tu mochila."""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)
        base = db.get_base(ctx.author.id)

        if not jugador or not base:
            await ctx.send("❌ Necesitas personaje y base.")
            return

        item_id = item_id.lower()
        if not db.remove_item_almacen(ctx.author.id, item_id, cantidad):
            nombre = ITEMS.get(item_id, {}).get("nombre", item_id)
            await ctx.send(f"❌ No tienes **{nombre} ×{cantidad}** en el almacén.")
            return

        db.add_item_inventario(ctx.author.id, item_id, cantidad)
        nombre = ITEMS.get(item_id, {}).get("nombre", item_id)
        emoji = ITEMS.get(item_id, {}).get("emoji", "📦")
        embed = discord.Embed(
            title="📤 Retirado",
            description=f"{emoji} **{nombre} ×{cantidad}** movido a tu mochila.",
            color=0x95a5a6
        )
        await ctx.send(embed=embed)

    @commands.command(name="reparar")
    async def reparar(self, ctx):
        """Repara el muro de tu base gastando piezas de metal."""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)
        base = db.get_base(ctx.author.id)

        if not jugador or not base:
            await ctx.send("❌ Necesitas personaje y base.")
            return

        if base["estructuras"].get("muro", 0) == 0:
            await ctx.send("❌ No tienes muro. Constrúyelo con `!construir muro`.")
            return

        vida_actual = base["vida_muro"]
        vida_max = base["vida_muro_max"]

        if vida_actual >= vida_max:
            await ctx.send("✅ El muro ya está en perfecto estado.")
            return

        daño = vida_max - vida_actual
        # Coste: 1 pieza de metal por cada 20 puntos de vida a reparar
        coste_piezas = max(1, daño // 20)
        coste_tapas = max(10, daño // 5)

        inv = jugador["inventario"]
        if inv.get("piezas_metal", 0) < coste_piezas:
            await ctx.send(
                f"❌ Necesitas **{coste_piezas} piezas de metal** para reparar {daño} de daño.\n"
                f"Tienes: **{inv.get('piezas_metal', 0)}**. Encuéntralas en la fábrica."
            )
            return
        if jugador["tapas"] < coste_tapas:
            await ctx.send(f"❌ Necesitas **{coste_tapas} tapas**. Tienes **{jugador['tapas']}**.")
            return

        db.remove_item_inventario(ctx.author.id, "piezas_metal", coste_piezas)
        db.update_jugador(ctx.author.id, tapas=jugador["tapas"] - coste_tapas)
        db.update_base(ctx.author.id, vida_muro=vida_max)

        embed = discord.Embed(
            title="🔧 Muro reparado",
            description=(
                f"🧱 Vida del muro: **{vida_actual} → {vida_max}/{vida_max}** ✅\n"
                f"Gastaste: **{coste_piezas} piezas de metal** + **{coste_tapas} tapas**"
            ),
            color=0x27ae60
        )
        await ctx.send(embed=embed)

    @commands.command(name="historialbase", aliases=["ataques"])
    async def historial_base(self, ctx):
        """Muestra los últimos ataques recibidos en tu base."""
        db = self.bot.db
        base = db.get_base(ctx.author.id)
        if not base:
            await ctx.send("❌ No tienes base.")
            return

        historial = db.get_historial_ataques(ctx.author.id, limit=5)
        if not historial:
            embed = discord.Embed(
                title="📜 Historial de ataques",
                description="Tu base aún no ha sido atacada.",
                color=0x95a5a6
            )
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(
            title=f"📜 Últimos ataques — {base['nombre']}",
            color=0x2c3e50
        )
        for ataque in historial:
            emoji = "✅" if ataque["resultado"] == "repelido" else "💥"
            recursos = ""
            if ataque["recursos_perdidos"]:
                recursos = " | Robado: " + ", ".join(
                    f"{ITEMS.get(k,{}).get('nombre',k)}×{v}"
                    for k, v in ataque["recursos_perdidos"].items()
                )
            embed.add_field(
                name=f"{emoji} {ataque['oleada_nombre']} — {ataque['fecha'][:10]}",
                value=(
                    f"Resultado: **{ataque['resultado'].upper()}** | "
                    f"Daño: {ataque['dano_recibido']} | "
                    f"Tapas perdidas: {ataque['tapas_perdidas']}"
                    f"{recursos}"
                ),
                inline=False
            )
        await ctx.send(embed=embed)

    @commands.command(name="renombrarbase")
    async def renombrar_base(self, ctx, *, nuevo_nombre: str):
        """Cambia el nombre de tu base."""
        db = self.bot.db
        if not db.get_base(ctx.author.id):
            await ctx.send("❌ No tienes base.")
            return
        db.update_base(ctx.author.id, nombre=nuevo_nombre[:40])
        await ctx.send(f"✅ Base renombrada a **{nuevo_nombre[:40]}**.")

    # ─────────────────────────────────────────────────────────────
    # UTILIDADES
    # ─────────────────────────────────────────────────────────────
    def _barra(self, actual, maximo, longitud=8):
        if maximo == 0:
            return "⬛" * longitud
        lleno = int((actual / maximo) * longitud)
        color = "🟩" if actual / maximo > 0.5 else ("🟨" if actual / maximo > 0.25 else "🟥")
        return color * lleno + "⬛" * (longitud - lleno)

    def _efecto_nivel(self, est_id, nivel, nivel_data):
        if est_id == "muro":
            return f"🧱 Vida del muro: **{nivel_data['vida']}** | Defensa base: **{nivel_data['defensa_base']}**"
        elif est_id == "torretas":
            return f"🔫 Daño por turno de ataque: **{nivel_data['daño_por_turno']}**"
        elif est_id == "almacen":
            return f"📦 Slots: **{nivel_data['slots']}** | Protección: **{nivel_data['proteccion_pct']}%**"
        elif est_id == "generador":
            return f"⚡ Tapas por hora: **{nivel_data['tapas_por_hora']}**"
        elif est_id == "hospital_base":
            return f"🏥 Curación automática al volver: **+{nivel_data['curacion_auto']} vida**"
        elif est_id == "laboratorio":
            return f"🔬 Bonus EXP en combate/exploración: **+{nivel_data['bonus_exp_pct']}%**"
        return ""


async def setup(bot):
    await bot.add_cog(Bases(bot))

import discord
from discord.ext import commands, tasks
import random
import asyncio
from datetime import datetime, timezone, timedelta
from game_data import ZONAS, ZOMBIES, ITEMS

# ── CONFIGURACIÓN ─────────────────────────────────────────────────────────────
HORAS_SIN_DORMIR      = 32       # Horas hasta estar exhausto
INTERVALO_CANSANCIO   = 4        # Horas entre incrementos de cansancio
CANSANCIO_POR_TICK    = 25       # Cansancio que sube cada tick (4h → lleno a las 32h aprox)

MAX_HORAS_ATRINCH     = 8        # Máximo horas de atrincheramiento AFK
TICK_ATRINCH_MIN      = 10       # Cada cuántos minutos se procesa un tick de atrincheramiento

MAX_HORAS_ENTRENA     = 4        # Máximo horas de entrenamiento
TICK_ENTRENA_MIN      = 15       # Cada cuántos minutos un tick de entrenamiento

# ── ZONAS VÁLIDAS PARA ATRINCHERARSE ─────────────────────────────────────────
ZONAS_ATRINCHERABLES = [z for z, d in ZONAS.items()
                        if d.get("zombies") and z != "refugio"]


class Supervivencia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.loop_cansancio.start()
        self.loop_atrincheramiento.start()
        self.loop_entrenamiento.start()

    def cog_unload(self):
        self.loop_cansancio.cancel()
        self.loop_atrincheramiento.cancel()
        self.loop_entrenamiento.cancel()

    # ─────────────────────────────────────────────────────────────────────────
    # LOOPS
    # ─────────────────────────────────────────────────────────────────────────

    @tasks.loop(hours=INTERVALO_CANSANCIO)
    async def loop_cansancio(self):
        """Sube el cansancio de todos los jugadores activos cada 4 horas."""
        db = self.bot.db
        try:
            c = db._cur()
            # Subir cansancio a jugadores vivos que no estén durmiendo ya al máximo
            c.execute("""
                UPDATE jugadores
                SET cansancio = LEAST(cansancio + %s, 100)
                WHERE estado != 'muerto'
            """, (CANSANCIO_POR_TICK,))
            db._commit()
        except Exception as e:
            print(f"[CANSANCIO ERROR] {e}")

    @loop_cansancio.before_loop
    async def before_cansancio(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(30)

    @tasks.loop(minutes=TICK_ATRINCH_MIN)
    async def loop_atrincheramiento(self):
        """Procesa el farm AFK de todos los jugadores atrincherados."""
        db = self.bot.db
        try:
            c = db._cur()
            c.execute("SELECT * FROM jugadores WHERE atrincherando=1")
            jugadores = c.fetchall()
        except Exception as e:
            print(f"[ATRINCH ERROR] {e}")
            return

        for jugador in jugadores:
            try:
                await self._tick_atrincheramiento(dict(jugador))
            except Exception as e:
                print(f"[ATRINCH TICK ERROR] {jugador['discord_id']}: {e}")

    @loop_atrincheramiento.before_loop
    async def before_atrinch(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(60)

    @tasks.loop(minutes=TICK_ENTRENA_MIN)
    async def loop_entrenamiento(self):
        """Procesa el entrenamiento AFK de todos los jugadores entrenando."""
        db = self.bot.db
        try:
            c = db._cur()
            c.execute("SELECT * FROM jugadores WHERE entrenando=1")
            jugadores = c.fetchall()
        except Exception as e:
            print(f"[ENTRENA ERROR] {e}")
            return

        for jugador in jugadores:
            try:
                await self._tick_entrenamiento(dict(jugador))
            except Exception as e:
                print(f"[ENTRENA TICK ERROR] {jugador['discord_id']}: {e}")

    @loop_entrenamiento.before_loop
    async def before_entrena(self):
        await self.bot.wait_until_ready()
        await asyncio.sleep(90)

    # ─────────────────────────────────────────────────────────────────────────
    # LÓGICA INTERNA
    # ─────────────────────────────────────────────────────────────────────────

    async def _tick_atrincheramiento(self, jugador):
        """Un tick de farm AFK: mata zombies, gana exp/tapas/items."""
        db = self.bot.db
        discord_id = jugador["discord_id"]
        zona_id = jugador.get("atrincherando_zona") or jugador["zona"]

        # Comprobar tiempo máximo
        inicio = jugador.get("atrincherando_inicio")
        if inicio:
            if isinstance(inicio, str):
                inicio = datetime.fromisoformat(inicio)
            if inicio.tzinfo is None:
                inicio = inicio.replace(tzinfo=timezone.utc)
            elapsed = (datetime.now(timezone.utc) - inicio).total_seconds() / 3600
            if elapsed >= MAX_HORAS_ATRINCH:
                await self._finalizar_atrincheramiento(jugador, motivo="tiempo")
                return

        zona = ZONAS.get(zona_id)
        if not zona or not zona["zombies"]:
            return

        # Simulación de combate simplificada
        zombie_id = random.choice(zona["zombies"])
        zombie = ZOMBIES[zombie_id]

        import json
        inv = json.loads(jugador["inventario"]) if isinstance(jugador["inventario"], str) else jugador["inventario"]
        bonus_ataque = max(
            (ITEMS.get(k, {}).get("bonus_ataque", 0) for k, v in inv.items() if v > 0),
            default=0
        )
        ataque_total = jugador["ataque"] + bonus_ataque
        dano_al_zombie = max(1, ataque_total - zombie["defensa"] + random.randint(-3, 5))
        rondas = max(1, zombie["vida"] // max(1, dano_al_zombie))

        # El jugador recibe daño proporcional a las rondas
        dano_recibido = max(0, (zombie["ataque"] - jugador["defensa"]) * rondas // 4 + random.randint(0, 5))
        nueva_vida = max(5, jugador["vida"] - dano_recibido)  # nunca baja de 5 en AFK

        # Recompensas
        tapas = random.randint(*zombie["tapas"])
        exp = zombie["exp"]
        drops = {}
        for item_id, prob in zombie["drop"].items():
            if random.random() < prob * 0.6:  # drop reducido en AFK
                drops[item_id] = 1

        # Guardar
        nuevas_tapas = jugador["tapas"] + tapas
        db.update_jugador(discord_id, vida=nueva_vida, tapas=nuevas_tapas, kills=jugador["kills"] + 1)
        db._cur().execute("UPDATE jugadores SET kills = kills + 1 WHERE discord_id = %s", (str(discord_id),))
        for item_id, cant in drops.items():
            db.add_item_inventario(discord_id, item_id, cant)
        db.add_exp(discord_id, exp)

        # Notificar al canal si está configurado
        canal_id = None
        base = db.get_base(discord_id)
        if base:
            canal_id = base.get("canal_notif")

        if canal_id:
            canal = self.bot.get_channel(int(canal_id))
            if canal:
                drops_txt = ""
                if drops:
                    drops_txt = " | Drop: " + ", ".join(
                        f"{ITEMS.get(k,{}).get('emoji','📦')}{ITEMS.get(k,{}).get('nombre',k)}" for k in drops
                    )
                try:
                    user = await self.bot.fetch_user(int(discord_id))
                    await canal.send(
                        f"⚔️ **{user.display_name}** (atrincherado) eliminó **{zombie['nombre']}** "
                        f"en {zona['nombre']} → +{tapas}💰 +{exp}⭐{drops_txt}"
                    )
                except Exception:
                    pass

    async def _finalizar_atrincheramiento(self, jugador, motivo="comando"):
        """Saca al jugador del modo atrincheramiento."""
        db = self.bot.db
        discord_id = jugador["discord_id"]
        db.update_jugador(discord_id,
            atrincherando=0,
            atrincherando_zona=None,
            atrincherando_inicio=None,
            estado="vivo"
        )

        canal_id = None
        base = db.get_base(discord_id)
        if base:
            canal_id = base.get("canal_notif")

        if canal_id and motivo == "tiempo":
            canal = self.bot.get_channel(int(canal_id))
            if canal:
                try:
                    user = await self.bot.fetch_user(int(discord_id))
                    await canal.send(
                        f"🏁 {user.mention} Tu atrincheramiento ha terminado automáticamente "
                        f"(máximo {MAX_HORAS_ATRINCH}h). Usa `!retirar_atrincheramiento` para ver el resumen."
                    )
                except Exception:
                    pass

    async def _tick_entrenamiento(self, jugador):
        """Un tick de entrenamiento: gana pequeños bonus de stats."""
        db = self.bot.db
        discord_id = jugador["discord_id"]

        # Comprobar tiempo máximo
        inicio = jugador.get("entrenando_inicio")
        if inicio:
            if isinstance(inicio, str):
                inicio = datetime.fromisoformat(inicio)
            if inicio.tzinfo is None:
                inicio = inicio.replace(tzinfo=timezone.utc)
            elapsed = (datetime.now(timezone.utc) - inicio).total_seconds() / 3600
            if elapsed >= MAX_HORAS_ENTRENA:
                await self._finalizar_entrenamiento(jugador, motivo="tiempo")
                return

        # Pequeño bonus de exp por entrenar
        exp_ganada = random.randint(5, 15)
        db.add_exp(discord_id, exp_ganada)

    async def _finalizar_entrenamiento(self, jugador, motivo="comando"):
        """Termina el entrenamiento y aplica el bonus final."""
        db = self.bot.db
        discord_id = jugador["discord_id"]

        # Bonus permanente al terminar: +1 en ataque o defensa aleatoriamente
        stat = random.choice(["ataque", "defensa", "velocidad"])
        jugador_actual = db.get_jugador(discord_id)
        nuevo_valor = jugador_actual[stat] + 1

        db.update_jugador(discord_id,
            entrenando=0,
            entrenando_inicio=None,
            estado="vivo",
            **{stat: nuevo_valor}
        )

        canal_id = None
        base = db.get_base(discord_id)
        if base:
            canal_id = base.get("canal_notif")

        if canal_id:
            canal = self.bot.get_channel(int(canal_id))
            if canal:
                try:
                    user = await self.bot.fetch_user(int(discord_id))
                    emoji = {"ataque": "⚔️", "defensa": "🛡️", "velocidad": "💨"}.get(stat, "📈")
                    msg = (f"🏋️ {user.mention} Tu entrenamiento ha terminado. "
                           f"Ganaste {emoji} **+1 {stat}** permanente.")
                    if motivo == "tiempo":
                        msg += f" (máximo {MAX_HORAS_ENTRENA}h alcanzado)"
                    await canal.send(msg)
                except Exception:
                    pass

    # ─────────────────────────────────────────────────────────────────────────
    # COMANDOS — DORMIR
    # ─────────────────────────────────────────────────────────────────────────

    @commands.command(name="dormir")
    async def dormir(self, ctx):
        """Duermes para recuperar energía. Necesario cada 32 horas."""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)

        if not jugador:
            await ctx.send("❌ Usa `!crear` para comenzar.")
            return

        if jugador.get("atrincherando", 0):
            await ctx.send("❌ No puedes dormir mientras estás atrincherado. Usa `!retirar_atrincheramiento` primero.")
            return

        if jugador.get("entrenando", 0):
            await ctx.send("❌ No puedes dormir mientras entrenas. Usa `!parar_entrenamiento` primero.")
            return

        # Comprobar si ya durmió hace poco (menos de 6 horas)
        ultimo = jugador.get("ultimo_sueno")
        if ultimo:
            if isinstance(ultimo, str):
                ultimo = datetime.fromisoformat(ultimo)
            if ultimo.tzinfo is None:
                ultimo = ultimo.replace(tzinfo=timezone.utc)
            diff = (datetime.now(timezone.utc) - ultimo).total_seconds() / 3600
            if diff < 6:
                horas_restantes = round(6 - diff, 1)
                await ctx.send(
                    f"😴 Ya dormiste hace poco. Podrás volver a dormir en **{horas_restantes}h**.\n"
                    f"Dormir demasiado también agota."
                )
                return

        # Curación al dormir + reset cansancio
        curacion = min(40, jugador["vida_max"] - jugador["vida"])
        nueva_vida = jugador["vida"] + curacion

        db.update_jugador(ctx.author.id,
            cansancio=0,
            ultimo_sueno=datetime.now(timezone.utc).isoformat(),
            vida=nueva_vida
        )

        cansancio_previo = jugador.get("cansancio", 0)

        embed = discord.Embed(
            title="😴 Descansando...",
            color=0x6c3483
        )

        if cansancio_previo >= 75:
            desc = "Estabas al límite del agotamiento. Duermes profundamente durante horas."
        elif cansancio_previo >= 50:
            desc = "Tu cuerpo necesitaba esto. Un sueño reparador te devuelve las fuerzas."
        else:
            desc = "Una siesta rápida. No estabas tan cansado pero siempre viene bien."

        embed.description = (
            f"{desc}\n\n"
            f"😴 Cansancio: **{cansancio_previo}% → 0%**\n"
            f"❤️ Vida recuperada: **+{curacion}** ({nueva_vida}/{jugador['vida_max']})\n\n"
            f"*Podrás dormir de nuevo en 6 horas.*\n"
            f"*El cansancio sube con el tiempo — si llegas al 100% no podrás explorar.*"
        )
        embed.set_footer(text=f"Próximo sueño obligatorio en ~{HORAS_SIN_DORMIR}h")
        await ctx.send(embed=embed)

    @commands.command(name="cansancio", aliases=["energia"])
    async def ver_cansancio(self, ctx):
        """Muestra tu nivel de cansancio actual."""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)
        if not jugador:
            await ctx.send("❌ Usa `!crear` para comenzar.")
            return

        cansancio = jugador.get("cansancio", 0)
        barra = self._barra_cansancio(cansancio)

        if cansancio == 0:
            estado_txt = "✅ Descansado y listo para la acción."
            color = 0x2ecc71
        elif cansancio < 50:
            estado_txt = "🟡 Algo cansado pero funcional."
            color = 0xf1c40f
        elif cansancio < 75:
            estado_txt = "🟠 Bastante cansado. Considera dormir pronto."
            color = 0xe67e22
        elif cansancio < 100:
            estado_txt = "🔴 Agotado. Duerme antes de seguir explorando."
            color = 0xe74c3c
        else:
            estado_txt = "💀 EXHAUSTO. No puedes explorar hasta que duermas."
            color = 0x2c3e50

        embed = discord.Embed(
            title=f"😴 Cansancio de {jugador['nombre']}",
            description=f"{barra} **{cansancio}%**\n\n{estado_txt}",
            color=color
        )
        embed.set_footer(text="!dormir para descansar | El cansancio sube ~25% cada 4 horas")
        await ctx.send(embed=embed)

    # ─────────────────────────────────────────────────────────────────────────
    # COMANDOS — ATRINCHERARSE
    # ─────────────────────────────────────────────────────────────────────────

    @commands.command(name="atrincherarse", aliases=["atrincherar", "afk"])
    async def atrincherarse(self, ctx, zona_id: str = None):
        """Modo AFK: tu personaje mata zombies solo mientras no estás."""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)

        if not jugador:
            await ctx.send("❌ Usa `!crear` para comenzar.")
            return

        if jugador["estado"] == "muerto":
            await ctx.send("💀 No puedes atrincherarte estando muerto.")
            return

        if jugador.get("cansancio", 0) >= 100:
            await ctx.send("😴 Estás demasiado cansado para atrincherarte. Usa `!dormir` primero.")
            return

        if jugador.get("atrincherando", 0):
            await ctx.send("⚠️ Ya estás atrincherado. Usa `!retirar_atrincheramiento` para ver el progreso.")
            return

        if jugador.get("entrenando", 0):
            await ctx.send("⚠️ Estás entrenando. Usa `!parar_entrenamiento` primero.")
            return

        # Elegir zona
        if zona_id:
            zona_id = zona_id.lower()
            if zona_id not in ZONAS or zona_id == "refugio" or not ZONAS[zona_id]["zombies"]:
                zonas_validas = ", ".join(f"`{z}`" for z in ZONAS_ATRINCHERABLES)
                await ctx.send(f"❌ Zona no válida para atrincherarse.\nZonas disponibles: {zonas_validas}")
                return
            # Verificar mapa secreto
            requiere = ZONAS[zona_id].get("requiere_item")
            if requiere and jugador["inventario"].get(requiere, 0) == 0:
                await ctx.send(f"❌ No tienes el mapa para acceder a **{ZONAS[zona_id]['nombre']}**.")
                return
        else:
            zona_id = jugador["zona"] if jugador["zona"] != "refugio" else "hospital"

        zona = ZONAS[zona_id]

        # Verificar nivel mínimo
        if jugador["nivel"] < zona["nivel_min"]:
            await ctx.send(
                f"❌ Necesitas **Nivel {zona['nivel_min']}** para atrincherarte en **{zona['nombre']}**."
            )
            return

        db.update_jugador(ctx.author.id,
            atrincherando=1,
            atrincherando_zona=zona_id,
            atrincherando_inicio=datetime.now(timezone.utc).isoformat(),
            estado="atrincherado",
            zona=zona_id
        )

        embed = discord.Embed(
            title=f"🛡️ Atrincherado en {zona['nombre']}",
            description=(
                f"{jugador['nombre']} se parapeta y comienza a eliminar zombies.\n\n"
                f"**Tu personaje luchará solo** cada {TICK_ATRINCH_MIN} minutos.\n"
                f"Las recompensas se acumularán automáticamente.\n\n"
                f"⏱️ Duración máxima: **{MAX_HORAS_ATRINCH} horas**\n"
                f"📍 Zona: **{zona['nombre']}**\n"
                f"⚠️ Peligro: {'⚠️' * zona['peligro']}\n\n"
                f"Usa `!retirar_atrincheramiento` cuando quieras volver."
            ),
            color=0xe74c3c
        )
        embed.set_footer(text=f"Las notificaciones llegan al canal configurado con !base canal")
        await ctx.send(embed=embed)

    @commands.command(name="retirar_atrincheramiento", aliases=["retirar", "salir_afk"])
    async def retirar_atrincheramiento(self, ctx):
        """Para el modo AFK y muestra el resumen de lo conseguido."""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)

        if not jugador:
            await ctx.send("❌ Usa `!crear` para comenzar.")
            return

        if not jugador.get("atrincherando", 0):
            await ctx.send("❌ No estás atrincherado.")
            return

        inicio = jugador.get("atrincherando_inicio")
        if inicio:
            if isinstance(inicio, str):
                inicio = datetime.fromisoformat(inicio)
            if inicio.tzinfo is None:
                inicio = inicio.replace(tzinfo=timezone.utc)
            elapsed_min = int((datetime.now(timezone.utc) - inicio).total_seconds() / 60)
            ticks = elapsed_min // TICK_ATRINCH_MIN
            horas = elapsed_min // 60
            minutos = elapsed_min % 60
        else:
            ticks = 0
            horas = 0
            minutos = 0

        zona_id = jugador.get("atrincherando_zona", jugador["zona"])
        zona = ZONAS.get(zona_id, {})

        await self._finalizar_atrincheramiento(jugador, motivo="comando")

        embed = discord.Embed(
            title="🏁 Atrincheramiento terminado",
            description=(
                f"**{jugador['nombre']}** se retira de **{zona.get('nombre', zona_id)}**.\n\n"
                f"⏱️ Tiempo: **{horas}h {minutos}min**\n"
                f"⚔️ Combates aproximados: **~{ticks}**\n\n"
                f"Los recursos ganados ya están en tu inventario.\n"
                f"Usa `!inventario` y `!saldo` para ver lo que conseguiste."
            ),
            color=0x27ae60
        )
        await ctx.send(embed=embed)

    # ─────────────────────────────────────────────────────────────────────────
    # COMANDOS — ENTRENAR
    # ─────────────────────────────────────────────────────────────────────────

    @commands.command(name="entrenar", aliases=["ejercicio", "gym"])
    async def entrenar(self, ctx):
        """Entrena en el refugio para mejorar tus stats permanentemente."""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)

        if not jugador:
            await ctx.send("❌ Usa `!crear` para comenzar.")
            return

        if jugador["zona"] != "refugio":
            await ctx.send(
                "❌ Solo puedes entrenar en el **Refugio Central**.\n"
                "Usa `!explorar refugio` para volver."
            )
            return

        if jugador["estado"] == "muerto":
            await ctx.send("💀 No puedes entrenar estando muerto.")
            return

        if jugador.get("cansancio", 0) >= 75:
            await ctx.send(
                "😴 Estás demasiado cansado para entrenar con eficacia.\n"
                "Usa `!dormir` para recuperarte primero."
            )
            return

        if jugador.get("atrincherando", 0):
            await ctx.send("⚠️ Estás atrincherado. Usa `!retirar_atrincheramiento` primero.")
            return

        if jugador.get("entrenando", 0):
            await ctx.send(
                "🏋️ Ya estás entrenando.\n"
                "Usa `!parar_entrenamiento` para terminar y recibir el bonus."
            )
            return

        db.update_jugador(ctx.author.id,
            entrenando=1,
            entrenando_inicio=datetime.now(timezone.utc).isoformat(),
            estado="entrenando"
        )

        embed = discord.Embed(
            title="🏋️ Entrenamiento iniciado",
            description=(
                f"**{jugador['nombre']}** comienza a entrenar en el refugio.\n\n"
                f"Cada **{TICK_ENTRENA_MIN} minutos** ganarás EXP pasiva.\n"
                f"Al terminar recibirás **+1 stat permanente** aleatorio entre:\n"
                f"⚔️ Ataque | 🛡️ Defensa | 💨 Velocidad\n\n"
                f"⏱️ Duración máxima: **{MAX_HORAS_ENTRENA} horas**\n"
                f"❗ Solo puedes entrenar en el refugio.\n\n"
                f"Usa `!parar_entrenamiento` cuando quieras terminar."
            ),
            color=0x2980b9
        )
        embed.set_footer(text="Cuanto más tiempo entrenes, más EXP acumulas.")
        await ctx.send(embed=embed)

    @commands.command(name="parar_entrenamiento", aliases=["parar_entrena", "stop_gym"])
    async def parar_entrenamiento(self, ctx):
        """Para el entrenamiento y aplica el bonus de stat."""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)

        if not jugador:
            await ctx.send("❌ Usa `!crear` para comenzar.")
            return

        if not jugador.get("entrenando", 0):
            await ctx.send("❌ No estás entrenando.")
            return

        inicio = jugador.get("entrenando_inicio")
        if inicio:
            if isinstance(inicio, str):
                inicio = datetime.fromisoformat(inicio)
            if inicio.tzinfo is None:
                inicio = inicio.replace(tzinfo=timezone.utc)
            elapsed_min = int((datetime.now(timezone.utc) - inicio).total_seconds() / 60)
            horas = elapsed_min // 60
            minutos = elapsed_min % 60
        else:
            elapsed_min = 0
            horas = 0
            minutos = 0

        # Mínimo 5 minutos para recibir bonus
        if elapsed_min < 5:
            await ctx.send("⏱️ Necesitas entrenar al menos **5 minutos** para recibir el bonus.")
            return

        await self._finalizar_entrenamiento(jugador, motivo="comando")

        # Obtener jugador actualizado para ver el stat que subió
        jugador_nuevo = db.get_jugador(ctx.author.id)

        embed = discord.Embed(
            title="🏆 Entrenamiento completado",
            description=(
                f"**{jugador['nombre']}** termina su sesión de entrenamiento.\n\n"
                f"⏱️ Tiempo entrenado: **{horas}h {minutos}min**\n\n"
                f"Stats actuales:\n"
                f"⚔️ Ataque: **{jugador_nuevo['ataque']}**\n"
                f"🛡️ Defensa: **{jugador_nuevo['defensa']}**\n"
                f"💨 Velocidad: **{jugador_nuevo['velocidad']}**\n\n"
                f"*El bonus de +1 stat ya se ha aplicado.*"
            ),
            color=0x27ae60
        )
        await ctx.send(embed=embed)

    @commands.command(name="estado_afk", aliases=["afk_status"])
    async def estado_afk(self, ctx):
        """Muestra si estás atrincherado o entrenando."""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)

        if not jugador:
            await ctx.send("❌ Usa `!crear` para comenzar.")
            return

        if jugador.get("atrincherando", 0):
            inicio = jugador.get("atrincherando_inicio")
            zona_id = jugador.get("atrincherando_zona", jugador["zona"])
            zona = ZONAS.get(zona_id, {})
            if inicio:
                if isinstance(inicio, str):
                    inicio = datetime.fromisoformat(inicio)
                if inicio.tzinfo is None:
                    inicio = inicio.replace(tzinfo=timezone.utc)
                elapsed_min = int((datetime.now(timezone.utc) - inicio).total_seconds() / 60)
                restantes = max(0, MAX_HORAS_ATRINCH * 60 - elapsed_min)
                h, m = divmod(elapsed_min, 60)
                hr, mr = divmod(restantes, 60)
            else:
                h = m = hr = mr = 0

            embed = discord.Embed(
                title="🛡️ Atrincherado",
                description=(
                    f"Estás luchando en **{zona.get('nombre', zona_id)}**\n\n"
                    f"⏱️ Tiempo transcurrido: **{h}h {m}min**\n"
                    f"⏳ Tiempo restante: **{hr}h {mr}min**\n\n"
                    f"Usa `!retirar_atrincheramiento` para volver."
                ),
                color=0xe74c3c
            )
            await ctx.send(embed=embed)

        elif jugador.get("entrenando", 0):
            inicio = jugador.get("entrenando_inicio")
            if inicio:
                if isinstance(inicio, str):
                    inicio = datetime.fromisoformat(inicio)
                if inicio.tzinfo is None:
                    inicio = inicio.replace(tzinfo=timezone.utc)
                elapsed_min = int((datetime.now(timezone.utc) - inicio).total_seconds() / 60)
                restantes = max(0, MAX_HORAS_ENTRENA * 60 - elapsed_min)
                h, m = divmod(elapsed_min, 60)
                hr, mr = divmod(restantes, 60)
            else:
                h = m = hr = mr = 0

            embed = discord.Embed(
                title="🏋️ Entrenando",
                description=(
                    f"Estás entrenando en el **Refugio Central**\n\n"
                    f"⏱️ Tiempo entrenado: **{h}h {m}min**\n"
                    f"⏳ Tiempo restante: **{hr}h {mr}min**\n\n"
                    f"Usa `!parar_entrenamiento` para terminar y recibir el bonus."
                ),
                color=0x2980b9
            )
            await ctx.send(embed=embed)

        else:
            cansancio = jugador.get("cansancio", 0)
            await ctx.send(
                f"✅ No estás en ningún modo AFK.\n"
                f"😴 Cansancio: **{cansancio}%** | Usa `!dormir` si supera el 75%."
            )

    # ─────────────────────────────────────────────────────────────────────────
    # UTILIDADES
    # ─────────────────────────────────────────────────────────────────────────

    def _barra_cansancio(self, valor, longitud=10):
        lleno = int((valor / 100) * longitud)
        if valor < 50:
            emoji = "🟩"
        elif valor < 75:
            emoji = "🟨"
        else:
            emoji = "🟥"
        return emoji * lleno + "⬛" * (longitud - lleno)


async def setup(bot):
    await bot.add_cog(Supervivencia(bot))

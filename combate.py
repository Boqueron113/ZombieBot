import discord
from discord.ext import commands
import random
from game_data import ZONAS, ZOMBIES, ITEMS
from base_data import ESTRUCTURAS

class Combate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _get_combate(self, discord_id):
        if not hasattr(self.bot, "_combates"):
            self.bot._combates = {}
        return self.bot._combates.get(str(discord_id))

    def _set_combate(self, discord_id, data):
        if not hasattr(self.bot, "_combates"):
            self.bot._combates = {}
        self.bot._combates[str(discord_id)] = data

    def _clear_combate(self, discord_id):
        if hasattr(self.bot, "_combates"):
            self.bot._combates.pop(str(discord_id), None)

    @commands.command(name="atacar")
    async def atacar(self, ctx):
        """Ataca al zombie en tu zona"""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)

        if not jugador:
            await ctx.send("❌ Usa `!crear` para comenzar.")
            return

        combate = self._get_combate(ctx.author.id)

        # Si no hay combate activo, generar uno en la zona actual
        if not combate:
            zona_id = jugador["zona"]
            zona = ZONAS.get(zona_id)
            if not zona or not zona["zombies"] or zona_id == "refugio":
                await ctx.send("🕊️ No hay zombies aquí. Usa `!explorar <zona>` para encontrar uno.")
                return
            zombie_id = random.choice(zona["zombies"])
            combate = {"zombie_id": zombie_id, "zombie_vida": ZOMBIES[zombie_id]["vida"]}
            self._set_combate(ctx.author.id, combate)
            db.update_jugador(ctx.author.id, estado="en_combate")

        zombie_id = combate["zombie_id"]
        zombie_data = ZOMBIES[zombie_id]
        zombie_vida = combate["zombie_vida"]

        # Calcular ataque del jugador
        inv = jugador["inventario"]
        bonus_ataque = 0
        arma_usada = None
        for item_id, cantidad in inv.items():
            item = ITEMS.get(item_id, {})
            if item.get("tipo") == "arma" and cantidad > 0:
                if item.get("bonus_ataque", 0) > bonus_ataque:
                    bonus_ataque = item["bonus_ataque"]
                    arma_usada = item["nombre"]

        ataque_jugador = jugador["ataque"] + bonus_ataque
        variacion = random.randint(-3, 5)
        daño_jugador = max(1, ataque_jugador - zombie_data["defensa"] + variacion)

        # Crítico (10% de probabilidad)
        critico = random.random() < 0.10
        if critico:
            daño_jugador = int(daño_jugador * 1.8)

        # Ataque del zombie al jugador
        bonus_defensa = 0
        for item_id, cantidad in inv.items():
            item = ITEMS.get(item_id, {})
            if item.get("tipo") == "armadura" and cantidad > 0:
                bonus_defensa += item.get("bonus_defensa", 0)

        daño_zombie = max(0, zombie_data["ataque"] - (jugador["defensa"] + bonus_defensa) + random.randint(-2, 4))
        nueva_vida_zombie = zombie_vida - daño_jugador
        nueva_vida_jugador = jugador["vida"] - daño_zombie

        embed = discord.Embed(
            title=f"⚔️ COMBATE: {jugador['nombre']} vs {zombie_data['nombre']}",
            color=0xe74c3c
        )

        # Turno del jugador
        ataque_txt = f"{'💥 CRÍTICO! ' if critico else ''}Atacas con {'**'+arma_usada+'**' if arma_usada else 'tus manos'} y causas **{daño_jugador}** de daño."
        embed.add_field(name="🗡️ Tu turno", value=ataque_txt, inline=False)

        if nueva_vida_zombie <= 0:
            # ── ZOMBIE MUERTO ──────────────────────────────────
            self._clear_combate(ctx.author.id)
            db.update_jugador(ctx.author.id, kills=jugador["kills"] + 1, estado="vivo")

            # Recompensas
            tapas_ganadas = random.randint(*zombie_data["tapas"])
            exp_ganada = zombie_data["exp"]
            # ── Bonus EXP del laboratorio ──
            base_jugador = db.get_base(ctx.author.id)
            if base_jugador:
                nivel_lab = base_jugador['estructuras'].get('laboratorio', 0)
                if nivel_lab > 0:
                    bonus_pct = ESTRUCTURAS['laboratorio']['niveles'][nivel_lab]['bonus_exp_pct']
                    exp_ganada = int(exp_ganada * (1 + bonus_pct / 100))
            drops = []

            for item_id, prob in zombie_data["drop"].items():
                if random.random() < prob:
                    cant = random.randint(1, 2)
                    db.add_item_inventario(ctx.author.id, item_id, cant)
                    drops.append(f"{ITEMS.get(item_id, {}).get('emoji', '📦')} {ITEMS.get(item_id, {}).get('nombre', item_id)} x{cant}")

            nuevas_tapas = jugador["tapas"] + tapas_ganadas
            db.update_jugador(ctx.author.id, tapas=nuevas_tapas, vida=max(nueva_vida_jugador, 0))

            subio, nuevo_nivel = db.add_exp(ctx.author.id, exp_ganada)

            # Actualizar misiones
            completadas = db.actualizar_progreso_mision(ctx.author.id, "matar_zombies")

            recompensa_txt = (
                f"💰 **{tapas_ganadas}** tapas\n"
                f"⭐ **{exp_ganada}** EXP"
            )
            if drops:
                recompensa_txt += "\n" + "\n".join(drops)

            embed.add_field(
                name=f"💀 ¡{zombie_data['nombre']} eliminado!",
                value=recompensa_txt,
                inline=False
            )

            if daño_zombie > 0:
                embed.add_field(
                    name="🩸 Daño recibido",
                    value=f"El zombie te atacó antes de morir: **-{daño_zombie}** vida.\nVida restante: {max(nueva_vida_jugador, 0)}/{jugador['vida_max']}",
                    inline=False
                )

            if subio:
                embed.add_field(
                    name="⬆️ ¡SUBISTE DE NIVEL!",
                    value=f"**Nivel {nuevo_nivel - 1} → {nuevo_nivel}**\n+20 vida máx | +3 ataque | +2 defensa",
                    inline=False
                )

            if completadas:
                for mid in completadas:
                    m = db.get_mision(mid)
                    if m:
                        embed.add_field(name="✅ ¡Misión completada!", value=f"**{m['titulo']}** — usa `!entregar`", inline=False)

            embed.color = 0x2ecc71
        else:
            # ── ZOMBIE VIVO ────────────────────────────────────
            combate["zombie_vida"] = nueva_vida_zombie
            self._set_combate(ctx.author.id, combate)

            if nueva_vida_jugador <= 0:
                # Jugador muerto
                db.update_jugador(ctx.author.id, vida=0, estado="muerto", muertes=jugador["muertes"] + 1)
                self._clear_combate(ctx.author.id)
                embed.add_field(
                    name=f"🧟 {zombie_data['nombre']} contraataca",
                    value=f"Te causa **{daño_zombie}** de daño.",
                    inline=False
                )
                embed.add_field(
                    name="💀 HAS MUERTO",
                    value="El zombie te ha dado caza. Tu historia termina aquí... por ahora.\n\nUn médico del refugio puede reviverte. Usa `!revivir` (cuesta 100 tapas).",
                    inline=False
                )
                embed.color = 0x2c3e50
            else:
                db.update_jugador(ctx.author.id, vida=nueva_vida_jugador)
                embed.add_field(
                    name=f"🧟 {zombie_data['nombre']} contraataca",
                    value=f"Te causa **{daño_zombie}** de daño. Tu vida: **{nueva_vida_jugador}/{jugador['vida_max']}**",
                    inline=False
                )
                barra_zombie = self._barra(nueva_vida_zombie, zombie_data["vida"])
                embed.add_field(
                    name="📊 Estado del combate",
                    value=(
                        f"🧟 Vida zombie: {barra_zombie} {nueva_vida_zombie}/{zombie_data['vida']}\n"
                        f"❤️ Tu vida: {nueva_vida_jugador}/{jugador['vida_max']}"
                    ),
                    inline=False
                )
                embed.set_footer(text="Usa !atacar para seguir | !huir para escapar | !usar <item> para curarte")

        await ctx.send(embed=embed)

    @commands.command(name="huir")
    async def huir(self, ctx):
        """Intenta escapar del combate"""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)

        if not jugador:
            await ctx.send("❌ Usa `!crear` para comenzar.")
            return

        combate = self._get_combate(ctx.author.id)
        if not combate:
            await ctx.send("🕊️ No estás en combate.")
            return

        zombie_data = ZOMBIES[combate["zombie_id"]]
        exito = random.random() < (0.4 + jugador["velocidad"] * 0.02)

        if exito:
            self._clear_combate(ctx.author.id)
            db.update_jugador(ctx.author.id, zona="refugio", estado="vivo")
            embed = discord.Embed(
                title="💨 ¡Escapaste!",
                description=f"Lograste huir del **{zombie_data['nombre']}** y llegaste al refugio.\nVida restante: {jugador['vida']}/{jugador['vida_max']}",
                color=0xf39c12
            )
        else:
            # El zombie te golpea al intentar huir
            daño = max(0, zombie_data["ataque"] // 2 - jugador["defensa"] + random.randint(0, 5))
            nueva_vida = max(jugador["vida"] - daño, 0)
            db.update_jugador(ctx.author.id, vida=nueva_vida)

            embed = discord.Embed(
                title="❌ No pudiste escapar",
                description=(
                    f"El **{zombie_data['nombre']}** te atrapa cuando intentas huir y te causa **{daño}** de daño.\n"
                    f"Vida: {nueva_vida}/{jugador['vida_max']}\n\nUsa `!atacar` o intenta `!huir` de nuevo."
                ),
                color=0xe74c3c
            )

        await ctx.send(embed=embed)

    @commands.command(name="usar")
    async def usar(self, ctx, *, item: str):
        """Usa un item del inventario durante el combate"""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)

        if not jugador:
            await ctx.send("❌ Usa `!crear` para comenzar.")
            return

        item_id = item.lower().replace(" ", "_")
        item_data = ITEMS.get(item_id)

        if not item_data:
            await ctx.send(f"❌ Item `{item}` no encontrado.")
            return

        if item_data["tipo"] != "consumible":
            await ctx.send(f"❌ **{item_data['nombre']}** no se puede usar en combate de esta forma.")
            return

        if not db.remove_item_inventario(ctx.author.id, item_id):
            await ctx.send(f"❌ No tienes **{item_data['nombre']}** en tu inventario.")
            return

        curacion = item_data["valor"]
        nueva_vida = min(jugador["vida"] + curacion, jugador["vida_max"])
        db.update_jugador(ctx.author.id, vida=nueva_vida)

        embed = discord.Embed(
            title=f"💊 {item_data['nombre']} usada",
            description=f"Recuperas **{curacion}** puntos de vida.\n❤️ Vida: {jugador['vida']} → **{nueva_vida}/{jugador['vida_max']}**",
            color=0x2ecc71
        )
        await ctx.send(embed=embed)

    @commands.command(name="revivir")
    async def revivir(self, ctx):
        """Revive en el refugio (cuesta 100 tapas)"""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)

        if not jugador:
            await ctx.send("❌ Usa `!crear` para comenzar.")
            return

        if jugador["estado"] != "muerto":
            await ctx.send("✅ No estás muerto. No necesitas revivir.")
            return

        costo = 100
        if jugador["tapas"] < costo:
            await ctx.send(f"❌ Necesitas **{costo} tapas** para revivir. Tienes **{jugador['tapas']}**.")
            return

        nuevas_tapas = jugador["tapas"] - costo
        vida_inicial = jugador["vida_max"] // 2
        db.update_jugador(ctx.author.id, estado="vivo", vida=vida_inicial, tapas=nuevas_tapas, zona="refugio")

        embed = discord.Embed(
            title="💉 Has revivido",
            description=(
                f"El médico del refugio te devuelve a la vida.\n\n"
                f"❤️ Vida recuperada: **{vida_inicial}/{jugador['vida_max']}**\n"
                f"💰 Tapas restantes: **{nuevas_tapas}**\n"
                f"📍 Estás en: **Refugio Central**"
            ),
            color=0x27ae60
        )
        await ctx.send(embed=embed)

    def _barra(self, actual, maximo, longitud=8):
        lleno = int((actual / maximo) * longitud)
        return "🟥" * lleno + "⬛" * (longitud - lleno)

async def setup(bot):
    await bot.add_cog(Combate(bot))

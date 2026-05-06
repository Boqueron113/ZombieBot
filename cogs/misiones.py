import discord
from discord.ext import commands
from game_data import ITEMS

class Misiones(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="misiones")
    async def misiones(self, ctx):
        """Muestra todas las misiones disponibles"""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)

        if not jugador:
            await ctx.send("❌ Usa `!crear` para comenzar.")
            return

        todas = db.get_misiones()
        activas_jugador = {m["id"]: m for m in db.get_misiones_jugador(ctx.author.id)}

        embed = discord.Embed(
            title="📋 TABLÓN DE MISIONES",
            description="Acepta misiones para ganar tapas, EXP e items especiales.",
            color=0x8e44ad
        )

        for mision in todas:
            mid = mision["id"]
            en_progreso = mid in activas_jugador

            if en_progreso:
                progreso = activas_jugador[mid]["progreso"]
                completada = activas_jugador[mid]["completada"]
                if completada:
                    estado = "✅ ¡Lista para entregar!"
                else:
                    estado = f"🔄 En progreso: {progreso}/{mision['objetivo_cantidad']}"
            else:
                estado = f"📌 Disponible — `!mision {mid}` para aceptar"

            zona_req = f"\n📍 Zona: `{mision['zona_requerida']}`" if mision["zona_requerida"] else ""
            recompensa_item = ""
            if mision["recompensa_item"]:
                item = ITEMS.get(mision["recompensa_item"], {})
                recompensa_item = f" + {item.get('emoji','📦')} {item.get('nombre', mision['recompensa_item'])}"

            embed.add_field(
                name=f"[{mid}] {mision['titulo']}",
                value=(
                    f"*{mision['descripcion']}*\n"
                    f"🎯 Objetivo: {mision['objetivo_cantidad']} unidades{zona_req}\n"
                    f"🏆 Recompensa: 💰{mision['recompensa_tapas']} tapas | ⭐{mision['recompensa_exp']} EXP{recompensa_item}\n"
                    f"Estado: {estado}"
                ),
                inline=False
            )

        embed.set_footer(text="!mision <id> para aceptar • !entregar para entregar completadas • !misprogreso para ver tus misiones")
        await ctx.send(embed=embed)

    @commands.command(name="mision")
    async def aceptar_mision(self, ctx, mision_id: int):
        """Acepta una misión"""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)

        if not jugador:
            await ctx.send("❌ Usa `!crear` para comenzar.")
            return

        mision = db.get_mision(mision_id)
        if not mision or not mision["activa"]:
            await ctx.send(f"❌ Misión #{mision_id} no encontrada.")
            return

        # Verificar zona requerida
        if mision["zona_requerida"] and jugador["zona"] != mision["zona_requerida"]:
            await ctx.send(
                f"❌ Esta misión requiere estar en **{mision['zona_requerida']}**.\n"
                f"Estás en: **{jugador['zona']}**"
            )
            return

        if not db.aceptar_mision(ctx.author.id, mision_id):
            await ctx.send(f"❌ Ya tienes la misión **{mision['titulo']}** activa.")
            return

        recompensa_item = ""
        if mision["recompensa_item"]:
            item = ITEMS.get(mision["recompensa_item"], {})
            recompensa_item = f"\n🎁 Item: {item.get('emoji','📦')} {item.get('nombre', mision['recompensa_item'])}"

        embed = discord.Embed(
            title=f"📋 Misión aceptada: {mision['titulo']}",
            description=(
                f"*{mision['descripcion']}*\n\n"
                f"🎯 **Objetivo:** {mision['objetivo_cantidad']} unidades\n"
                f"💰 **Recompensa:** {mision['recompensa_tapas']} tapas\n"
                f"⭐ **EXP:** {mision['recompensa_exp']}{recompensa_item}"
            ),
            color=0x8e44ad
        )
        embed.set_footer(text="Completa el objetivo y usa !entregar para reclamar tu recompensa.")
        await ctx.send(embed=embed)

    @commands.command(name="misprogreso", aliases=["progreso"])
    async def misprogreso(self, ctx):
        """Muestra el progreso de tus misiones activas"""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)

        if not jugador:
            await ctx.send("❌ Usa `!crear` para comenzar.")
            return

        activas = db.get_misiones_jugador(ctx.author.id)

        if not activas:
            embed = discord.Embed(
                title="📋 Sin misiones activas",
                description="No tienes misiones activas. Usa `!misiones` para ver y aceptar misiones.",
                color=0x95a5a6
            )
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(
            title=f"📋 Tus misiones activas",
            color=0x8e44ad
        )

        for m in activas:
            barra = self._barra_progreso(m["progreso"], m["objetivo_cantidad"])
            estado = "✅ ¡Lista para entregar! — `!entregar`" if m["completada"] else f"🔄 {m['progreso']}/{m['objetivo_cantidad']}"
            embed.add_field(
                name=f"[{m['id']}] {m['titulo']}",
                value=f"{barra}\n{estado}",
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name="entregar")
    async def entregar(self, ctx, mision_id: int = None):
        """Entrega una misión completada"""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)

        if not jugador:
            await ctx.send("❌ Usa `!crear` para comenzar.")
            return

        activas = db.get_misiones_jugador(ctx.author.id)
        completadas = [m for m in activas if m["completada"]]

        if not completadas:
            await ctx.send("❌ No tienes misiones completadas para entregar.\nSigue el objetivo de tus misiones activas.")
            return

        # Si no se especifica ID, entregar la primera completada
        if mision_id is None:
            mision_objetivo = completadas[0]
            mision_id = mision_objetivo["id"]

        mision = db.entregar_mision(ctx.author.id, mision_id)
        if not mision:
            await ctx.send(f"❌ La misión #{mision_id} no está completada o no existe.")
            return

        # Dar recompensas
        nuevas_tapas = jugador["tapas"] + mision["recompensa_tapas"]
        db.update_jugador(ctx.author.id, tapas=nuevas_tapas)
        subio, nuevo_nivel = db.add_exp(ctx.author.id, mision["recompensa_exp"])

        recompensa_item_txt = ""
        if mision["recompensa_item"]:
            db.add_item_inventario(ctx.author.id, mision["recompensa_item"])
            item = ITEMS.get(mision["recompensa_item"], {})
            recompensa_item_txt = f"\n🎁 Item: {item.get('emoji','📦')} {item.get('nombre', mision['recompensa_item'])}"

        embed = discord.Embed(
            title=f"🏆 ¡Misión entregada!",
            description=(
                f"**{mision['titulo']}** completada.\n\n"
                f"💰 **+{mision['recompensa_tapas']} tapas** (Total: {nuevas_tapas})\n"
                f"⭐ **+{mision['recompensa_exp']} EXP**{recompensa_item_txt}"
            ),
            color=0xf1c40f
        )

        if subio:
            embed.add_field(
                name="⬆️ ¡SUBISTE DE NIVEL!",
                value=f"**Nivel {nuevo_nivel - 1} → {nuevo_nivel}**\n+20 vida máx | +3 ataque | +2 defensa",
                inline=False
            )

        await ctx.send(embed=embed)

    def _barra_progreso(self, actual, maximo, longitud=10):
        lleno = int((actual / maximo) * longitud) if maximo > 0 else 0
        return "🟩" * lleno + "⬛" * (longitud - lleno)

async def setup(bot):
    await bot.add_cog(Misiones(bot))

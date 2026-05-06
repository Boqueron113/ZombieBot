import discord
from discord.ext import commands
from game_data import ITEMS

class Personaje(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="crear")
    async def crear(self, ctx):
        """Crea tu personaje de superviviente"""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)

        if jugador:
            embed = discord.Embed(
                title="⚠️ Ya tienes un personaje",
                description=f"Ya existes en el mundo zombie como **{jugador['nombre']}**.\nUsa `!perfil` para ver tus stats.",
                color=0xe74c3c
            )
            await ctx.send(embed=embed)
            return

        nombre = ctx.author.display_name
        db.crear_jugador(ctx.author.id, nombre)

        embed = discord.Embed(
            title="🧟 BIENVENIDO AL APOCALIPSIS",
            description=(
                f"**{nombre}** acaba de despertar en el refugio central.\n\n"
                "El mundo se ha ido a la mierda. Los zombies están en todas partes.\n"
                "Tienes que sobrevivir como puedas.\n\n"
                "Empiezas con:\n"
                "🩹 **2 vendas** | 🥫 **3 comidas** | 🔶 **10 munición** | 💰 **50 tapas**"
            ),
            color=0x2d5a1b
        )
        embed.add_field(
            name="📋 Primeros pasos",
            value="`!ayuda` — Ver todos los comandos\n`!mapa` — Ver zonas explorables\n`!perfil` — Ver tus estadísticas",
            inline=False
        )
        embed.set_footer(text="Sobrevive. Lucha. Adapta. 🧟")
        await ctx.send(embed=embed)

    @commands.command(name="perfil")
    async def perfil(self, ctx, miembro: discord.Member = None):
        """Muestra el perfil de un jugador"""
        target = miembro or ctx.author
        db = self.bot.db
        jugador = db.get_jugador(target.id)

        if not jugador:
            nombre = "tú" if target == ctx.author else target.display_name
            embed = discord.Embed(
                title="❌ Personaje no encontrado",
                description=f"{'Tú no tienes' if target == ctx.author else f'{target.display_name} no tiene'} un personaje.\nUsa `!crear` para empezar.",
                color=0xe74c3c
            )
            await ctx.send(embed=embed)
            return

        vida_barra = self._barra_vida(jugador["vida"], jugador["vida_max"])
        exp_necesaria = jugador["nivel"] * 100
        exp_barra = self._barra_exp(jugador["exp"], exp_necesaria)

        estado_color = {
            "vivo": 0x2ecc71,
            "muerto": 0xe74c3c,
            "en_combate": 0xe67e22
        }.get(jugador["estado"], 0x95a5a6)

        embed = discord.Embed(
            title=f"👤 {jugador['nombre']}",
            color=estado_color
        )
        embed.add_field(
            name="📊 Estadísticas",
            value=(
                f"**Nivel:** {jugador['nivel']}\n"
                f"**EXP:** {jugador['exp']}/{exp_necesaria}\n"
                f"{exp_barra}\n"
                f"**Vida:** {jugador['vida']}/{jugador['vida_max']}\n"
                f"{vida_barra}"
            ),
            inline=True
        )
        embed.add_field(
            name="⚔️ Combate",
            value=(
                f"**Ataque:** ⚔️ {jugador['ataque']}\n"
                f"**Defensa:** 🛡️ {jugador['defensa']}\n"
                f"**Velocidad:** 💨 {jugador['velocidad']}\n"
                f"**Kills:** 🧟 {jugador['kills']}\n"
                f"**Muertes:** 💀 {jugador['muertes']}"
            ),
            inline=True
        )
        embed.add_field(
            name="📍 Estado",
            value=(
                f"**Zona:** {jugador['zona'].title()}\n"
                f"**Tapas:** 💰 {jugador['tapas']}\n"
                f"**Estado:** {'🟢 Vivo' if jugador['estado'] == 'vivo' else '🔴 Muerto'}"
            ),
            inline=True
        )
        embed.set_thumbnail(url=target.display_avatar.url)
        embed.set_footer(text=f"Personaje de {target.display_name}")
        await ctx.send(embed=embed)

    @commands.command(name="inventario", aliases=["inv"])
    async def inventario(self, ctx):
        """Muestra tu inventario"""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)

        if not jugador:
            await ctx.send("❌ Usa `!crear` para comenzar.")
            return

        inv = jugador["inventario"]
        if not inv:
            embed = discord.Embed(
                title="🎒 Inventario vacío",
                description="No tienes ningún item. ¡Explora zonas para conseguir recursos!",
                color=0x95a5a6
            )
            await ctx.send(embed=embed)
            return

        embed = discord.Embed(
            title=f"🎒 Inventario de {jugador['nombre']}",
            color=0x8e44ad
        )

        categorias = {
            "consumible": ("💊 Consumibles", []),
            "arma": ("⚔️ Armas", []),
            "armadura": ("🛡️ Armaduras", []),
            "material": ("🔧 Materiales", []),
            "arma_especial": ("💣 Especiales", []),
            "equipamiento": ("🗃️ Equipamiento", []),
        }

        for item_id, cantidad in inv.items():
            item_data = ITEMS.get(item_id)
            if item_data:
                tipo = item_data.get("tipo", "material")
                emoji = item_data.get("emoji", "📦")
                nombre = item_data["nombre"]
                cat = categorias.get(tipo, ("📦 Otros", []))
                cat[1].append(f"{emoji} **{nombre}** x{cantidad}")

        for cat_key, (cat_nombre, items_lista) in categorias.items():
            if items_lista:
                embed.add_field(
                    name=cat_nombre,
                    value="\n".join(items_lista),
                    inline=True
                )

        embed.set_footer(text=f"💰 Tapas: {jugador['tapas']}")
        await ctx.send(embed=embed)

    @commands.command(name="curar")
    async def curar(self, ctx, item: str = "venda"):
        """Usa un item de curación"""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)

        if not jugador:
            await ctx.send("❌ Usa `!crear` para comenzar.")
            return

        item = item.lower().replace(" ", "_")
        item_data = ITEMS.get(item)

        if not item_data or item_data.get("tipo") != "consumible":
            await ctx.send(f"❌ `{item}` no es un item de curación válido.")
            return

        if jugador["vida"] >= jugador["vida_max"]:
            await ctx.send("✅ ¡Ya tienes la vida al máximo! No necesitas curarte.")
            return

        if not db.remove_item_inventario(ctx.author.id, item):
            await ctx.send(f"❌ No tienes **{item_data['nombre']}** en tu inventario.")
            return

        curacion = item_data["valor"]
        nueva_vida = min(jugador["vida"] + curacion, jugador["vida_max"])
        db.update_jugador(ctx.author.id, vida=nueva_vida)

        embed = discord.Embed(
            title=f"💊 {item_data['nombre']} usada",
            description=f"Te curas **{curacion}** puntos de vida.\n❤️ Vida: {jugador['vida']} → **{nueva_vida}/{jugador['vida_max']}**",
            color=0x2ecc71
        )
        await ctx.send(embed=embed)

    def _barra_vida(self, actual, maximo, longitud=10):
        lleno = int((actual / maximo) * longitud)
        return "❤️" * lleno + "🖤" * (longitud - lleno)

    def _barra_exp(self, actual, maximo, longitud=10):
        lleno = int((actual / maximo) * longitud) if maximo > 0 else 0
        return "⭐" * lleno + "▪️" * (longitud - lleno)

async def setup(bot):
    await bot.add_cog(Personaje(bot))

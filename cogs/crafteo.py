import discord
from discord.ext import commands
from crafteo_data import RECETAS, get_receta, get_recetas_disponibles
from game_data import ITEMS


class Crafteo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="craftear", aliases=["fabricar", "craft"])
    async def craftear(self, ctx, *, item_id: str = None):
        """Fabrica un item usando materiales de tu inventario."""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)

        if not jugador:
            await ctx.send("❌ Usa `!crear` para comenzar.")
            return

        if not item_id:
            await ctx.send("❌ Indica qué quieres fabricar. Usa `!recetas` para ver las recetas.")
            return

        item_id = item_id.lower().replace(" ", "_")
        receta = get_receta(item_id)

        if not receta:
            await ctx.send(f"❌ No hay receta para `{item_id}`. Usa `!recetas` para ver qué puedes fabricar.")
            return

        if jugador["nivel"] < receta["nivel_min"]:
            await ctx.send(
                f"❌ Necesitas **Nivel {receta['nivel_min']}** para fabricar esto.\n"
                f"Tu nivel: **{jugador['nivel']}**"
            )
            return

        # Verificar ingredientes
        inv = jugador["inventario"]
        faltantes = []
        for mat_id, cantidad in receta["ingredientes"].items():
            tiene = inv.get(mat_id, 0)
            if tiene < cantidad:
                mat = ITEMS.get(mat_id, {})
                faltantes.append(
                    f"{mat.get('emoji','📦')} **{mat.get('nombre', mat_id)}**: tienes {tiene}/{cantidad}"
                )

        if faltantes:
            embed = discord.Embed(
                title="❌ Materiales insuficientes",
                description=f"Para fabricar **{ITEMS.get(item_id, {}).get('nombre', item_id)}** necesitas:\n\n" + "\n".join(faltantes),
                color=0xe74c3c
            )
            await ctx.send(embed=embed)
            return

        # Consumir ingredientes
        for mat_id, cantidad in receta["ingredientes"].items():
            db.remove_item_inventario(ctx.author.id, mat_id, cantidad)

        # Añadir item fabricado
        cantidad_resultado = receta["cantidad_resultado"]
        db.add_item_inventario(ctx.author.id, item_id, cantidad_resultado)

        # EXP por craftear
        exp_craft = receta["nivel_min"] * 10
        db.add_exp(ctx.author.id, exp_craft)

        item = ITEMS.get(item_id, {})
        ingredientes_str = "\n".join(
            f"  {ITEMS.get(k,{}).get('emoji','📦')} {ITEMS.get(k,{}).get('nombre',k)} ×{v}"
            for k, v in receta["ingredientes"].items()
        )

        embed = discord.Embed(
            title=f"🔧 ¡Fabricado!",
            description=(
                f"{item.get('emoji','📦')} **{item.get('nombre', item_id)} ×{cantidad_resultado}**\n\n"
                f"*{receta['descripcion']}*\n\n"
                f"**Materiales usados:**\n{ingredientes_str}\n\n"
                f"⭐ +{exp_craft} EXP"
            ),
            color=0x27ae60
        )
        await ctx.send(embed=embed)

    @commands.command(name="recetas", aliases=["crafteo", "taller"])
    async def recetas(self, ctx, categoria: str = None):
        """Muestra las recetas disponibles para tu nivel."""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)

        if not jugador:
            await ctx.send("❌ Usa `!crear` para comenzar.")
            return

        nivel = jugador["nivel"]
        inv = jugador["inventario"]
        recetas_disponibles = get_recetas_disponibles(nivel)

        # Categorías
        cats = {
            "fuego":      ("🔫 Armas de Fuego",   ["pistola_mod","francotirador","subfusil","lanzallamas","minigun"]),
            "cac":        ("⚔️ Cuerpo a Cuerpo",   ["bate_clavos","lanza","sierra_circular"]),
            "especiales": ("💣 Especiales",         ["granada","molotov","mina","explosivo"]),
            "armaduras":  ("🛡️ Armaduras",          ["armadura_cuero","escudo_improvisado"]),
            "consumibles":("💊 Consumibles",         ["botiquin","antidoto","adrenalina","racion_militar","venda"]),
            "municion":   ("🔶 Munición",            ["municion","municion_pesada"]),
            "materiales": ("⚙️ Materiales",          ["piezas_metal"]),
        }

        if categoria and categoria.lower() in cats:
            cats = {categoria.lower(): cats[categoria.lower()]}

        embed = discord.Embed(
            title=f"🔧 TALLER — Recetas disponibles (Nivel {nivel})",
            description="Usa `!craftear <id>` para fabricar. Los items marcados con ✅ tienes todos los materiales.",
            color=0x8e44ad
        )

        for cat_key, (cat_nombre, item_ids) in cats.items():
            lineas = []
            for item_id in item_ids:
                if item_id not in recetas_disponibles:
                    # Bloqueado por nivel
                    receta = RECETAS.get(item_id)
                    if receta:
                        item = ITEMS.get(item_id, {})
                        lineas.append(f"🔒 {item.get('emoji','')} ~~{item.get('nombre',item_id)}~~ *(Nivel {receta['nivel_min']})*")
                    continue

                receta = recetas_disponibles[item_id]
                item = ITEMS.get(item_id, {})

                # Comprobar si tiene todos los ingredientes
                puede = all(inv.get(mat, 0) >= cant for mat, cant in receta["ingredientes"].items())
                check = "✅" if puede else "🔧"

                mats_str = " + ".join(
                    f"{ITEMS.get(k,{}).get('emoji','📦')}{v}"
                    for k, v in receta["ingredientes"].items()
                )
                cant_res = receta["cantidad_resultado"]
                res_txt = f"×{cant_res}" if cant_res > 1 else ""
                lineas.append(
                    f"{check} {item.get('emoji','')} **{item.get('nombre',item_id)}{res_txt}** "
                    f"— `{item_id}`\n"
                    f"  ↳ {mats_str}"
                )

            if lineas:
                embed.add_field(
                    name=cat_nombre,
                    value="\n".join(lineas),
                    inline=False
                )

        cats_txt = " | ".join(f"`{k}`" for k in cats.keys())
        embed.set_footer(text=f"Categorías: {cats_txt} | !recetas <cat> para filtrar")
        await ctx.send(embed=embed)

    @commands.command(name="ingredientes", aliases=["receta"])
    async def ingredientes(self, ctx, *, item_id: str):
        """Muestra los ingredientes necesarios para fabricar un item."""
        item_id = item_id.lower().replace(" ", "_")
        receta = get_receta(item_id)

        if not receta:
            await ctx.send(f"❌ No hay receta para `{item_id}`.")
            return

        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)
        inv = jugador["inventario"] if jugador else {}

        item = ITEMS.get(item_id, {})
        embed = discord.Embed(
            title=f"📋 Receta: {item.get('emoji','')} {item.get('nombre', item_id)}",
            description=f"*{receta['descripcion']}*\n\nNivel mínimo: **{receta['nivel_min']}**",
            color=0x8e44ad
        )

        mats = []
        puede_craftear = True
        for mat_id, cantidad in receta["ingredientes"].items():
            mat = ITEMS.get(mat_id, {})
            tiene = inv.get(mat_id, 0)
            ok = tiene >= cantidad
            if not ok:
                puede_craftear = False
            estado = "✅" if ok else f"❌ (tienes {tiene})"
            mats.append(f"{mat.get('emoji','📦')} **{mat.get('nombre',mat_id)}** ×{cantidad} {estado}")

        embed.add_field(name="🔧 Ingredientes", value="\n".join(mats), inline=False)

        resultado_txt = f"×{receta['cantidad_resultado']}" if receta["cantidad_resultado"] > 1 else ""
        embed.add_field(
            name="📦 Resultado",
            value=f"{item.get('emoji','')} {item.get('nombre',item_id)} {resultado_txt}",
            inline=True
        )

        estado_final = "✅ ¡Puedes fabricarlo!" if puede_craftear else "❌ Te faltan materiales"
        embed.set_footer(text=f"{estado_final} | !craftear {item_id}")
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Crafteo(bot))

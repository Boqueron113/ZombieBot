import discord
from discord.ext import commands
from game_data import ITEMS, TIENDA_ITEMS

class Economia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="tienda")
    async def tienda(self, ctx, categoria: str = None):
        """Muestra la tienda del refugio."""
        import os
        base_url = os.getenv("RAILWAY_PUBLIC_DOMAIN", "localhost:8080")
        if not base_url.startswith("http"):
            base_url = "https://" + base_url
        url = base_url + "/tienda"

        categorias_disponibles = "consumible, arma, armadura, material"

        embed = discord.Embed(
            title="🏪 TIENDA DEL REFUGIO",
            description=(
                "La tienda completa está disponible en el navegador.\n\n"
                "[🌐 Ver tienda completa](" + url + ")\n\n"
                "**Compra rápida en Discord:**\n"
                "`!comprar <id_item>` — Comprar un item\n"
                "`!vender <id_item>` — Vender un item\n"
                "`!tienda <categoria>` — Ver categoría aquí\n\n"
                "Categorías: `" + categorias_disponibles + "`"
            ),
            color=0xf39c12
        )

        # Si pidieron una categoría, mostrarla aquí
        if categoria:
            categoria = categoria.lower()
            nombres_cat = {
                "consumible": "💊 Consumibles",
                "arma": "⚔️ Armas",
                "armadura": "🛡️ Armaduras",
                "material": "🔧 Materiales",
            }
            items_cat = []
            for item_id in TIENDA_ITEMS:
                item = ITEMS.get(item_id)
                if not item:
                    continue
                if item.get("tipo","") == categoria or item.get("subtipo","") == categoria:
                    precio = item.get("precio_compra", 0)
                    if precio > 0:
                        items_cat.append(
                            f"{item.get('emoji','📦')} **{item['nombre']}** — {precio}💰 | `{item_id}`"
                        )
            if items_cat:
                # Split into chunks to avoid Discord limit
                chunk = []
                chunk_size = 0
                for linea in items_cat:
                    if chunk_size + len(linea) > 900:
                        embed.add_field(
                            name=nombres_cat.get(categoria, categoria.title()),
                            value="\n".join(chunk),
                            inline=False
                        )
                        chunk = []
                        chunk_size = 0
                    chunk.append(linea)
                    chunk_size += len(linea)
                if chunk:
                    embed.add_field(
                        name=nombres_cat.get(categoria, categoria.title()),
                        value="\n".join(chunk),
                        inline=False
                    )
            else:
                embed.add_field(name="❌", value=f"Categoría `{categoria}` no encontrada.", inline=False)

        # Generar token para compra web
        try:
            from webapp import crear_token
            token = crear_token(ctx.author.id)
            raw_domain = os.getenv("RAILWAY_PUBLIC_DOMAIN", "localhost:8080")
            if raw_domain.startswith("http"):
                base_url = raw_domain
            else:
                base_url = "https://" + raw_domain
            url_tienda = base_url + "/tienda/" + token
            embed.add_field(
                name="🌐 Tienda web (recomendado)",
                value=f"[Abrir tienda completa con compra incluida]({url_tienda})\n*Enlace válido 15 minutos*",
                inline=False
            )
        except Exception:
            pass
        embed.set_footer(text="!comprar <id> • !vender <id> • !saldo")
        await ctx.send(embed=embed)

    @commands.command(name="comprar")
    async def comprar(self, ctx, item_id: str, cantidad: int = 1):
        """Compra un item de la tienda"""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)

        if not jugador:
            await ctx.send("❌ Usa `!crear` para comenzar.")
            return

        if jugador["zona"] != "refugio":
            await ctx.send("❌ Solo puedes comprar en el **Refugio Central**.\nUsa `!explorar refugio` o `!huir` para volver.")
            return

        item_id = item_id.lower()
        if item_id not in TIENDA_ITEMS:
            await ctx.send(f"❌ `{item_id}` no está disponible en la tienda.\nUsa `!tienda` para ver los items disponibles.")
            return

        item = ITEMS[item_id]
        precio_total = item["precio_compra"] * cantidad

        if precio_total == 0:
            await ctx.send("❌ Este item no se puede comprar.")
            return

        if jugador["tapas"] < precio_total:
            await ctx.send(
                f"❌ No tienes suficientes tapas.\n"
                f"Necesitas: **{precio_total}💰** | Tienes: **{jugador['tapas']}💰**"
            )
            return

        nuevas_tapas = jugador["tapas"] - precio_total
        db.update_jugador(ctx.author.id, tapas=nuevas_tapas)
        db.add_item_inventario(ctx.author.id, item_id, cantidad)

        embed = discord.Embed(
            title=f"✅ Compra realizada",
            description=(
                f"Compraste **{item['emoji']} {item['nombre']} x{cantidad}**\n"
                f"💰 Pagaste: **{precio_total} tapas**\n"
                f"💰 Saldo restante: **{nuevas_tapas} tapas**"
            ),
            color=0x27ae60
        )
        await ctx.send(embed=embed)

    @commands.command(name="vender")
    async def vender(self, ctx, item_id: str, cantidad: int = 1):
        """Vende un item al refugio"""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)

        if not jugador:
            await ctx.send("❌ Usa `!crear` para comenzar.")
            return

        if jugador["zona"] != "refugio":
            await ctx.send("❌ Solo puedes vender en el **Refugio Central**.")
            return

        item_id = item_id.lower()
        item = ITEMS.get(item_id)

        if not item:
            await ctx.send(f"❌ Item `{item_id}` no reconocido.")
            return

        precio_venta = item.get("precio_venta", 0)
        if precio_venta == 0:
            await ctx.send(f"❌ **{item['nombre']}** no tiene valor de venta.")
            return

        if not db.remove_item_inventario(ctx.author.id, item_id, cantidad):
            await ctx.send(f"❌ No tienes **{item['nombre']} x{cantidad}** en tu inventario.")
            return

        ganancia = precio_venta * cantidad
        nuevas_tapas = jugador["tapas"] + ganancia
        db.update_jugador(ctx.author.id, tapas=nuevas_tapas)

        # Actualizar misión de ventas
        completadas = db.actualizar_progreso_mision(ctx.author.id, "vender_items", ganancia)

        embed = discord.Embed(
            title="💸 Venta realizada",
            description=(
                f"Vendiste **{item['emoji']} {item['nombre']} x{cantidad}**\n"
                f"💰 Ganaste: **{ganancia} tapas**\n"
                f"💰 Saldo total: **{nuevas_tapas} tapas**"
            ),
            color=0x3498db
        )

        if completadas:
            for mid in completadas:
                m = db.get_mision(mid)
                if m:
                    embed.add_field(name="✅ ¡Misión completada!", value=f"**{m['titulo']}** — usa `!entregar`")

        await ctx.send(embed=embed)

    @commands.command(name="saldo", aliases=["tapas", "dinero"])
    async def saldo(self, ctx):
        """Muestra tus tapas actuales"""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)

        if not jugador:
            await ctx.send("❌ Usa `!crear` para comenzar.")
            return

        embed = discord.Embed(
            title=f"💰 Saldo de {jugador['nombre']}",
            description=f"Tienes **{jugador['tapas']} tapas**\n\n*La moneda del apocalipsis.*",
            color=0xf1c40f
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Economia(bot))

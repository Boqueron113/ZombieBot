import discord
from discord.ext import commands
import random
from game_data import (
    ITEMS, ITEMS_DEGRADABLES, ITEMS_MEJORABLES, ITEMS_EVENTO,
    ITEMS_EVENTO_IDS, ITEMS_DEGRADABLES_IDS, ITEMS_MEJORABLES_IDS, ITEMS_LEGENDARIOS_IDS
)


class ItemsManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Cache de efectos temporales activos: {discord_id: {stat: valor, combates_restantes: n}}
        self._efectos_temporales = {}

    # ─────────────────────────────────────────────────────────────────────────
    # DURABILIDAD
    # ─────────────────────────────────────────────────────────────────────────

    def get_durabilidad(self, jugador, item_id):
        """Obtiene la durabilidad actual de un item degradable."""
        inv = jugador["inventario"]
        dur_key = f"{item_id}_dur"
        if dur_key in inv:
            return inv[dur_key]
        item_data = ITEMS_DEGRADABLES.get(item_id)
        if item_data:
            return item_data["durabilidad_max"]
        return None

    def reducir_durabilidad(self, discord_id, item_id):
        """Reduce la durabilidad de un item. Devuelve True si se rompió."""
        db = self.bot.db
        jugador = db.get_jugador(discord_id)
        if not jugador:
            return False

        item_data = ITEMS_DEGRADABLES.get(item_id)
        if not item_data:
            return False

        inv = jugador["inventario"]
        dur_key = f"{item_id}_dur"
        dur_actual = inv.get(dur_key, item_data["durabilidad_max"])
        dano = item_data.get("dano_durabilidad_por_uso", 1)
        nueva_dur = max(0, dur_actual - dano)
        inv[dur_key] = nueva_dur
        db.update_jugador(discord_id, inventario=inv)

        if nueva_dur <= 0:
            # Se rompió — quitar del inventario
            db.remove_item_inventario(discord_id, item_id)
            inv2 = db.get_jugador(discord_id)["inventario"]
            if dur_key in inv2:
                del inv2[dur_key]
            db.update_jugador(discord_id, inventario=inv2)
            return True
        return False

    @commands.command(name="durabilidad", aliases=["dur", "estado_items"])
    async def ver_durabilidad(self, ctx):
        """Muestra la durabilidad de tus items degradables."""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)
        if not jugador:
            await ctx.send("❌ Usa `!crear` para comenzar.")
            return

        inv = jugador["inventario"]
        items_deg = [(item_id, ITEMS_DEGRADABLES[item_id])
                     for item_id in ITEMS_DEGRADABLES
                     if inv.get(item_id, 0) > 0]

        if not items_deg:
            await ctx.send("📦 No tienes ningún item degradable. Estos items se deterioran con el uso.")
            return

        embed = discord.Embed(
            title="🔧 Estado de tus items",
            description="Items que se degradan con el uso:",
            color=0xe67e22
        )

        for item_id, item_data in items_deg:
            dur_key = f"{item_id}_dur"
            dur_actual = inv.get(dur_key, item_data["durabilidad_max"])
            dur_max = item_data["durabilidad_max"]
            pct = dur_actual / dur_max
            barra = self._barra_dur(dur_actual, dur_max)

            if pct > 0.6:
                estado = "✅ Buen estado"
            elif pct > 0.3:
                estado = "⚠️ Desgastado"
            elif pct > 0:
                estado = "🔴 Casi roto"
            else:
                estado = "💀 Roto"

            item = ITEMS.get(item_id, item_data)
            rep = item_data.get("reparacion", {})
            rep_txt = " + ".join(
                f"{ITEMS.get(k,{}).get('emoji','📦')}{v} {k}"
                for k, v in rep.items()
            )
            embed.add_field(
                name=f"{item.get('emoji','')} {item.get('nombre', item_id)}",
                value=(
                    f"{barra} **{dur_actual}/{dur_max}** — {estado}\n"
                    f"Reparar: `!reparar_item {item_id}` ({rep_txt})"
                ),
                inline=False
            )
        await ctx.send(embed=embed)

    @commands.command(name="reparar_item")
    async def reparar_item(self, ctx, item_id: str):
        """Repara un item degradado usando materiales."""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)
        if not jugador:
            await ctx.send("❌ Usa `!crear` para comenzar.")
            return

        item_id = item_id.lower()
        if item_id not in ITEMS_DEGRADABLES:
            await ctx.send(f"❌ `{item_id}` no es un item reparable.")
            return

        inv = jugador["inventario"]
        if inv.get(item_id, 0) == 0:
            await ctx.send(f"❌ No tienes ese item.")
            return

        item_data = ITEMS_DEGRADABLES[item_id]
        dur_key = f"{item_id}_dur"
        dur_actual = inv.get(dur_key, item_data["durabilidad_max"])

        if dur_actual >= item_data["durabilidad_max"]:
            await ctx.send("✅ Este item ya está en perfecto estado.")
            return

        reparacion = item_data.get("reparacion", {})
        faltantes = []
        for mat_id, cant in reparacion.items():
            if inv.get(mat_id, 0) < cant:
                mat = ITEMS.get(mat_id, {})
                faltantes.append(f"{mat.get('emoji','📦')} {mat.get('nombre', mat_id)} ×{cant}")

        if faltantes:
            await ctx.send(f"❌ Faltan materiales: {', '.join(faltantes)}")
            return

        for mat_id, cant in reparacion.items():
            db.remove_item_inventario(ctx.author.id, mat_id, cant)

        inv2 = db.get_jugador(ctx.author.id)["inventario"]
        inv2[dur_key] = item_data["durabilidad_max"]
        db.update_jugador(ctx.author.id, inventario=inv2)

        item = ITEMS.get(item_id, item_data)
        embed = discord.Embed(
            title="🔧 Item reparado",
            description=(
                f"{item.get('emoji','')} **{item.get('nombre', item_id)}** restaurado.\n"
                f"🔧 Durabilidad: **{dur_actual} → {item_data['durabilidad_max']}/{item_data['durabilidad_max']}**"
            ),
            color=0x27ae60
        )
        await ctx.send(embed=embed)

    # ─────────────────────────────────────────────────────────────────────────
    # MEJORAS DE ITEMS
    # ─────────────────────────────────────────────────────────────────────────

    @commands.command(name="mejorar_item", aliases=["upgrade"])
    async def mejorar_item(self, ctx, item_id: str):
        """Mejora un item usando materiales."""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)
        if not jugador:
            await ctx.send("❌ Usa `!crear` para comenzar.")
            return

        item_id = item_id.lower()

        # Buscar si este item tiene una mejora disponible
        mejora_id = None
        mejora_data = None
        for mid, mdata in ITEMS_MEJORABLES.items():
            if mdata.get("mejora_de") == item_id:
                mejora_id = mid
                mejora_data = mdata
                break

        if not mejora_id:
            await ctx.send(f"❌ `{item_id}` no tiene mejora disponible. Usa `!mejorables` para ver qué se puede mejorar.")
            return

        inv = jugador["inventario"]
        if inv.get(item_id, 0) == 0:
            await ctx.send(f"❌ No tienes **{ITEMS.get(item_id, {}).get('nombre', item_id)}**.")
            return

        if jugador["nivel"] < mejora_data.get("nivel_min", 1):
            await ctx.send(f"❌ Necesitas **Nivel {mejora_data['nivel_min']}** para esta mejora.")
            return

        coste = mejora_data.get("coste_mejora", {})
        faltantes = []
        for mat_id, cant in coste.items():
            if inv.get(mat_id, 0) < cant:
                mat = ITEMS.get(mat_id, {})
                faltantes.append(f"{mat.get('emoji','📦')} {mat.get('nombre',mat_id)} ×{cant} (tienes {inv.get(mat_id,0)})")

        if faltantes:
            embed = discord.Embed(
                title="❌ Materiales insuficientes",
                description="Para mejorar necesitas:\n" + "\n".join(faltantes),
                color=0xe74c3c
            )
            await ctx.send(embed=embed)
            return

        # Consumir item base y materiales
        db.remove_item_inventario(ctx.author.id, item_id)
        for mat_id, cant in coste.items():
            db.remove_item_inventario(ctx.author.id, mat_id, cant)

        db.add_item_inventario(ctx.author.id, mejora_id)

        item_base = ITEMS.get(item_id, {})
        item_nuevo = ITEMS.get(mejora_id, mejora_data)
        embed = discord.Embed(
            title="⬆️ ¡Item mejorado!",
            description=(
                f"{item_base.get('emoji','')} **{item_base.get('nombre',item_id)}** → "
                f"{item_nuevo.get('emoji','')} **{item_nuevo.get('nombre',mejora_id)}**\n\n"
                f"*{mejora_data.get('descripcion','')}*"
            ),
            color=0x9b59b6
        )
        await ctx.send(embed=embed)

    @commands.command(name="mejorables")
    async def ver_mejorables(self, ctx):
        """Muestra los items que se pueden mejorar."""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)
        if not jugador:
            await ctx.send("❌ Usa `!crear` para comenzar.")
            return

        inv = jugador["inventario"]
        embed = discord.Embed(
            title="⬆️ Items mejorables",
            description="Mejora tus items para obtener versiones más poderosas.",
            color=0x9b59b6
        )

        cadenas = {}
        for mid, mdata in ITEMS_MEJORABLES.items():
            base = mdata.get("mejora_de")
            if base not in cadenas:
                cadenas[base] = []
            cadenas[base].append((mid, mdata))

        for base_id, mejoras in cadenas.items():
            item_base = ITEMS.get(base_id, {})
            tiene_base = inv.get(base_id, 0) > 0
            check = "✅" if tiene_base else "❌"
            linea = f"{check} {item_base.get('emoji','')} **{item_base.get('nombre',base_id)}**"
            for mid, mdata in mejoras:
                item_m = ITEMS.get(mid, mdata)
                coste_txt = " + ".join(
                    f"{ITEMS.get(k,{}).get('emoji','📦')}{v}"
                    for k, v in mdata.get("coste_mejora",{}).items()
                )
                linea += f"\n  → {item_m.get('emoji','')} **{item_m.get('nombre',mid)}** | {coste_txt} | `!mejorar_item {base_id}`"
            embed.add_field(name="\u200b", value=linea, inline=False)

        await ctx.send(embed=embed)

    # ─────────────────────────────────────────────────────────────────────────
    # DROGAS / EFECTOS TEMPORALES
    # ─────────────────────────────────────────────────────────────────────────

    def get_efecto_temporal(self, discord_id):
        return self._efectos_temporales.get(str(discord_id))

    def reducir_combate_efecto(self, discord_id):
        """Reduce en 1 el contador de combates del efecto temporal."""
        did = str(discord_id)
        if did not in self._efectos_temporales:
            return
        self._efectos_temporales[did]["combates_restantes"] -= 1
        if self._efectos_temporales[did]["combates_restantes"] <= 0:
            del self._efectos_temporales[did]

    @commands.command(name="usar_droga", aliases=["estimular", "tomar"])
    async def usar_droga(self, ctx, *, item_id: str):
        """Usa una droga o estimulante para efectos temporales en combate."""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)
        if not jugador:
            await ctx.send("❌ Usa `!crear` para comenzar.")
            return

        item_id = item_id.lower().replace(" ", "_")
        from game_data import ITEMS_DROGAS
        droga = ITEMS_DROGAS.get(item_id)
        if not droga:
            await ctx.send(f"❌ `{item_id}` no es una droga o estimulante válido.")
            return

        if jugador["inventario"].get(item_id, 0) == 0:
            await ctx.send(f"❌ No tienes **{droga['nombre']}**.")
            return

        # Aplicar efecto
        efecto = droga.get("efecto_temporal", {})

        # Efecto especial de cansancio
        if "cansancio_reduce" in efecto:
            cansancio_actual = jugador.get("cansancio", 0)
            nuevo_cansancio = max(0, cansancio_actual - efecto["cansancio_reduce"])
            db.update_jugador(ctx.author.id, cansancio=nuevo_cansancio)
            db.remove_item_inventario(ctx.author.id, item_id)
            embed = discord.Embed(
                title=f"💊 {droga['nombre']}",
                description=(
                    f"😴 Cansancio: **{cansancio_actual}% → {nuevo_cansancio}%**\n"
                    f"*{droga['descripcion']}*"
                ),
                color=0x9b59b6
            )
            await ctx.send(embed=embed)
            return

        duracion = efecto.get("duracion_combates", 0)
        if duracion == 0:
            await ctx.send(f"❌ Esta droga no tiene efecto de combate. Usa `!curar` para consumibles normales.")
            return

        # Guardar en cache
        did = str(ctx.author.id)
        self._efectos_temporales[did] = {
            **{k: v for k, v in efecto.items() if k != "duracion_combates"},
            "combates_restantes": duracion,
            "nombre": droga["nombre"],
            "emoji": droga["emoji"],
        }

        db.remove_item_inventario(ctx.author.id, item_id)

        stats_txt = "\n".join(
            f"{'⚔️' if k=='ataque' else '🛡️' if k=='defensa' else '💨' if k=='velocidad' else '🎯'} "
            f"**{k.title()}**: {'+'if v>0 else ''}{v}"
            for k, v in efecto.items()
            if k not in ("duracion_combates", "cansancio_reduce", "critico_bonus", "reduccion_dano")
        )
        embed = discord.Embed(
            title=f"{droga['emoji']} {droga['nombre']} activado",
            description=(
                f"*{droga['descripcion']}*\n\n"
                f"{stats_txt}\n"
                f"⏱️ Duración: **{duracion} combates**\n\n"
                f"*El efecto desaparece automáticamente después.*"
            ),
            color=0x9b59b6
        )
        await ctx.send(embed=embed)

    @commands.command(name="efectos_activos", aliases=["buffs"])
    async def efectos_activos(self, ctx):
        """Muestra los efectos temporales activos."""
        efecto = self.get_efecto_temporal(ctx.author.id)
        if not efecto:
            await ctx.send("✅ No tienes ningún efecto temporal activo.")
            return

        embed = discord.Embed(
            title=f"{efecto.get('emoji','💊')} Efecto activo: {efecto.get('nombre','')}",
            description=f"⏱️ **{efecto['combates_restantes']} combates** restantes",
            color=0x9b59b6
        )
        for k, v in efecto.items():
            if k not in ("combates_restantes", "nombre", "emoji"):
                embed.add_field(name=k.title(), value=f"{'+'if v>0 else ''}{v}", inline=True)
        await ctx.send(embed=embed)

    # ─────────────────────────────────────────────────────────────────────────
    # EVENTOS ESPECIALES
    # ─────────────────────────────────────────────────────────────────────────

    @commands.command(name="evento")
    @commands.has_permissions(administrator=True)
    async def activar_evento(self, ctx, tipo_evento: str):
        """[ADMIN] Activa un evento especial y distribuye items a todos."""
        from game_data import ITEMS_EVENTO
        items_del_evento = [
            (iid, idata) for iid, idata in ITEMS_EVENTO.items()
            if idata.get("evento") == tipo_evento.lower()
        ]

        if not items_del_evento:
            eventos_disponibles = set(i.get("evento") for i in ITEMS_EVENTO.values())
            await ctx.send(f"❌ Evento no encontrado. Disponibles: {', '.join(eventos_disponibles)}")
            return

        db = self.bot.db
        c = db._cur()
        c.execute("SELECT discord_id FROM jugadores WHERE estado != 'muerto'")
        jugadores = c.fetchall()

        item_id, item_data = random.choice(items_del_evento)
        count = 0
        for j in jugadores:
            db.add_item_inventario(j["discord_id"], item_id)
            count += 1

        item = ITEMS.get(item_id, item_data)
        embed = discord.Embed(
            title=f"🎉 EVENTO: {tipo_evento.upper()}",
            description=(
                f"¡Todos los supervivientes reciben:\n\n"
                f"{item.get('emoji','')} **{item.get('nombre', item_id)}**\n"
                f"*{item.get('descripcion','')}*\n\n"
                f"✅ Distribuido a **{count} supervivientes**."
            ),
            color=0xf1c40f
        )
        await ctx.send(embed=embed)

    @commands.command(name="abrir_caja")
    async def abrir_caja(self, ctx):
        """Abre una Caja de Evento para obtener un item aleatorio."""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)
        if not jugador:
            await ctx.send("❌ Usa `!crear` para comenzar.")
            return

        if jugador["inventario"].get("caja_navidad_zombie", 0) == 0 and \
           jugador["inventario"].get("huevo_zombie", 0) == 0:
            await ctx.send("❌ No tienes ninguna caja de evento para abrir.")
            return

        # Determinar qué caja usar
        caja_id = "caja_navidad_zombie" if jugador["inventario"].get("caja_navidad_zombie", 0) > 0 else "huevo_zombie"
        db.remove_item_inventario(ctx.author.id, caja_id)

        # Tabla de recompensas de la caja
        recompensas = [
            ("morfina", 3, 0.20),
            ("municion", 15, 0.20),
            ("venda", 5, 0.15),
            ("escopeta", 1, 0.10),
            ("adrenalina", 2, 0.10),
            ("estimulante", 2, 0.08),
            ("kevlar_v2", 1, 0.05),
            ("francotirador", 1, 0.05),
            ("serum_berserker", 1, 0.04),
            ("armadura_titan", 1, 0.02),
            ("corona_paciente_cero", 1, 0.01),
        ]

        rand = random.random()
        acum = 0
        item_ganado, cant_ganada = "morfina", 2
        for item_id, cant, prob in recompensas:
            acum += prob
            if rand <= acum:
                item_ganado, cant_ganada = item_id, cant
                break

        db.add_item_inventario(ctx.author.id, item_ganado, cant_ganada)
        item = ITEMS.get(item_ganado, {})

        rareza = "🌟 ¡LEGENDARIO!" if item_ganado in ITEMS_LEGENDARIOS_IDS else \
                 "💜 ¡Raro!" if cant_ganada == 1 and item.get("precio_venta", 0) > 100 else "📦 Normal"

        embed = discord.Embed(
            title=f"🎁 ¡Caja abierta!",
            description=(
                f"{rareza}\n\n"
                f"{item.get('emoji','📦')} **{item.get('nombre', item_ganado)} ×{cant_ganada}**\n"
                f"*{item.get('descripcion','')}*"
            ),
            color=0xf1c40f if item_ganado in ITEMS_LEGENDARIOS_IDS else 0x3498db
        )
        await ctx.send(embed=embed)

    # ─────────────────────────────────────────────────────────────────────────
    # ITEMS LEGENDARIOS
    # ─────────────────────────────────────────────────────────────────────────

    @commands.command(name="usar_legendario")
    async def usar_legendario(self, ctx, *, item_id: str):
        """Usa el efecto especial de un item legendario."""
        db = self.bot.db
        jugador = db.get_jugador(ctx.author.id)
        if not jugador:
            await ctx.send("❌ Usa `!crear` para comenzar.")
            return

        item_id = item_id.lower().replace(" ", "_")
        if item_id not in ITEMS_LEGENDARIOS_IDS:
            await ctx.send(f"❌ `{item_id}` no es un item legendario.")
            return
        if jugador["inventario"].get(item_id, 0) == 0:
            await ctx.send(f"❌ No tienes ese item.")
            return

        from game_data import ITEMS_LEGENDARIOS
        leg = ITEMS_LEGENDARIOS[item_id]
        efecto = leg.get("efecto", "")
        embed = discord.Embed(color=0xf1c40f)

        if efecto == "vida_completa_y_stats":
            bonus = leg.get("bonus_permanente", {})
            db.update_jugador(ctx.author.id,
                vida=jugador["vida_max"],
                ataque=jugador["ataque"] + bonus.get("ataque", 0),
                defensa=jugador["defensa"] + bonus.get("defensa", 0),
                velocidad=jugador["velocidad"] + bonus.get("velocidad", 0),
            )
            db.remove_item_inventario(ctx.author.id, item_id)
            embed.title = f"🧬 {leg['nombre']} consumido"
            embed.description = (
                f"❤️ Vida: **{jugador['vida_max']}/{jugador['vida_max']}** *(completa)*\n"
                f"⚔️ Ataque permanente: **+{bonus.get('ataque',0)}**\n"
                f"🛡️ Defensa permanente: **+{bonus.get('defensa',0)}**\n"
                f"💨 Velocidad permanente: **+{bonus.get('velocidad',0)}**"
            )

        elif efecto == "desbloquea_todo":
            for mapa_id in ["mapa_bunker", "mapa_militar", "mapa_laboratorio", "mapa_aeropuerto"]:
                if jugador["inventario"].get(mapa_id, 0) == 0:
                    db.add_item_inventario(ctx.author.id, mapa_id)
            db.remove_item_inventario(ctx.author.id, item_id)
            embed.title = f"📖 {leg['nombre']} leído"
            embed.description = "Has obtenido todos los mapas secretos:\n📜 Búnker | 🗂️ Militar | 🧪 Laboratorio | ✈️ Aeropuerto"

        elif efecto == "cooldown_reduccion_50pct":
            embed.title = f"⌚ {leg['nombre']}"
            embed.description = "Efecto pasivo activado. Tus cooldowns se reducen a la mitad mientras lo tengas equipado.\n*(Guárdalo en el inventario para mantener el efecto)*"

        else:
            embed.title = f"⭐ {leg['nombre']}"
            embed.description = f"*{leg.get('descripcion','')}*\nEste item otorga sus bonus automáticamente al tenerlo en el inventario."

        await ctx.send(embed=embed)

    # ─────────────────────────────────────────────────────────────────────────
    # UTILIDADES
    # ─────────────────────────────────────────────────────────────────────────

    def _barra_dur(self, actual, maximo, longitud=8):
        lleno = int((actual / maximo) * longitud) if maximo > 0 else 0
        pct = actual / maximo if maximo > 0 else 0
        color = "🟩" if pct > 0.6 else ("🟨" if pct > 0.3 else "🟥")
        return color * lleno + "⬛" * (longitud - lleno)


async def setup(bot):
    await bot.add_cog(ItemsManager(bot))

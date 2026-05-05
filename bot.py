import discord
from discord.ext import commands
import asyncio
import os
from database import Database

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)
bot.db = Database()

COGS = [
    "cogs.personaje",
    "cogs.mapa",
    "cogs.combate",
    "cogs.economia",
    "cogs.misiones",
    "cogs.bases",
    "cogs.supervivencia",
    "cogs.npcs",           # ← NUEVO
]

@bot.event
async def on_ready():
    print(f"✅ Bot conectado como {bot.user}")
    print(f"📡 Servidores: {len(bot.guilds)}")
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="🧟 El apocalipsis zombie"
        )
    )

@bot.command(name="ayuda")
async def ayuda(ctx):
    embed = discord.Embed(
        title="🧟 GUÍA DE SUPERVIVENCIA ZOMBIE",
        description="Comandos disponibles para sobrevivir al apocalipsis",
        color=0x2d5a1b
    )
    embed.add_field(name="👤 PERSONAJE", value=(
        "`!crear` — Crea tu personaje\n"
        "`!perfil` — Ver tus stats\n"
        "`!inventario` — Ver tu mochila\n"
        "`!curar` — Usar vendas para curarte"
    ), inline=False)
    embed.add_field(name="🗺️ MAPA", value=(
        "`!mapa` — Ver zonas disponibles\n"
        "`!explorar <zona>` — Explorar una zona\n"
        "`!ubicacion` — Ver dónde estás"
    ), inline=False)
    embed.add_field(name="⚔️ COMBATE", value=(
        "`!atacar` — Atacar zombie en tu zona\n"
        "`!huir` — Intentar escapar del combate\n"
        "`!usar <item>` — Usar item en combate"
    ), inline=False)
    embed.add_field(name="💰 ECONOMÍA", value=(
        "`!tienda` — Ver tienda del refugio\n"
        "`!comprar <item>` — Comprar un item\n"
        "`!vender <item>` — Vender un item\n"
        "`!saldo` — Ver tus tapas (moneda)"
    ), inline=False)
    embed.add_field(name="📋 MISIONES", value=(
        "`!misiones` — Ver misiones activas\n"
        "`!mision <id>` — Aceptar una misión\n"
        "`!entregar` — Entregar misión completada"
    ), inline=False)
    embed.add_field(name="😴 SUPERVIVENCIA", value=(
        "`!dormir` — Descansar y recuperar energía\n"
        "`!cansancio` — Ver nivel de cansancio\n"
        "`!atrincherarse [zona]` — Farm AFK en una zona\n"
        "`!retirar_atrincheramiento` — Salir del modo AFK\n"
        "`!entrenar` — Entrenar en el refugio (+stats)\n"
        "`!parar_entrenamiento` — Terminar entrenamiento\n"
        "`!estado_afk` — Ver si estás en modo AFK"
    ), inline=False)
    embed.add_field(name="👥 NPCs Y TRABAJOS", value=(
        "`!refugio` — Ver NPCs del refugio\n"
        "`!hablar <npc>` — Hablar con un NPC\n"
        "`!trabajar` — Ver ofertas de trabajo\n"
        "`!aceptar_trabajo <1/2/3>` — Aceptar trabajo\n"
        "`!curarse_medico` — Curación completa (50 tapas)\n"
        "`!mejorar_vida` — +20 vida máx permanente\n"
        "`!pistas` — Pistas de zonas secretas\n"
        "`!comprar_mapa <zona>` — Comprar mapa al informante\n"
        "`!hablar_npc` — Hablar con NPC encontrado\n"
        "`!aceptar_npc` / `!rechazar_npc` — Misión de NPC\n"
        "`!entregar_npc` — Entregar misión NPC"
    ), inline=False)
    embed.add_field(name="🏠 BASES", value=(
        "`!fundarbase <nombre>` — Crear tu base\n"
        "`!base` — Ver estado de tu base\n"
        "`!base canal` — Recibir alertas aquí\n"
        "`!estructuras` — Ver qué puedes construir\n"
        "`!construir <id>` — Construir/mejorar estructura\n"
        "`!reparar` — Reparar el muro\n"
        "`!almacenar <item> <cant>` — Guardar en almacén\n"
        "`!retirar <item> <cant>` — Sacar del almacén\n"
        "`!historialbase` — Ver ataques recibidos"
    ), inline=False)
    embed.set_footer(text="🧟 Sobrevive. Construye. Resiste.")
    await ctx.send(embed=embed)

async def main():
    async with bot:
        for cog in COGS:
            try:
                await bot.load_extension(cog)
                print(f"✅ Cog cargado: {cog}")
            except Exception as e:
                print(f"❌ Error cargando {cog}: {e}")

        token = os.getenv("DISCORD_TOKEN", "TU_TOKEN_AQUI")
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())

import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import sys
import asyncio

# Adicionar o diretório raiz ao sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from my_bot.commands.farm import farm
from my_bot.commands.buscar_membro import buscar_membro
from my_bot.commands.consultar import consultar
from my_bot.commands.ajuda import ajuda
from my_bot.commands.pagar_membro import pagar_membro

# Configurar as intents
intents = discord.Intents.default()
intents.message_content = True  # Permite que o bot leia o conteúdo das mensagens
intents.members = True  # Necessário para buscar informações dos membros

# Início da configuração do bot
bot = commands.Bot(command_prefix='!', intents=intents)

# Inicialização do bot
@bot.event
async def on_ready():
    print(f'Bot {bot.user} ready')

# Comando para registrar membro e adicionar farm
@bot.command(name='farm')
async def farm_command(ctx):
    msg = await farm(ctx, bot)
    await asyncio.sleep(30)
    await msg.delete()

# Comando para buscar membro por passaporte ou mostrar dropdown de membros registrados
@bot.command(name='buscar_membro')
async def buscar_membro_command(ctx, passaporte: int = None):
    farm_channel_id = int(os.getenv('FARM_CHANNEL_ID'))
    if ctx.channel.id != farm_channel_id:
        msg = await ctx.send(f"🚫 Este comando só pode ser usado no canal de farm.")
        await asyncio.sleep(30)
        await msg.delete()
        return
    
    else:
        msg = await buscar_membro(ctx, bot, passaporte)
        await asyncio.sleep(30)
        await msg.delete()

# Comando para consultar registros de farm do usuário
@bot.command(name='consultar')
async def consultar_command(ctx):
    msg = await consultar(ctx, bot)
    await asyncio.sleep(30)
    await msg.delete()

# Comando para exibir a lista de comandos e suas descrições
@bot.command(name='ajuda')
async def ajuda_command(ctx):
    msg = await ajuda(ctx)
    await asyncio.sleep(30)
    await msg.delete()

# Comando para pagar membro
@bot.command(name='pagar_membro')
async def pagar_membro_command(ctx):
    msg = await pagar_membro(ctx, bot)
    await asyncio.sleep(30)
    await msg.delete()

# Iniciar o bot
load_dotenv()
token = os.getenv('DISCORD_BOT_TOKEN')
farm_channel_id = os.getenv('FARM_CHANNEL_ID')

try:
    bot.run(token)
except KeyboardInterrupt:
    print("Bot desligado manualmente.")

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

# Carregar variáveis de ambiente
load_dotenv()
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
MONGO_URI = os.getenv('MONGO_URI')
FARM_CHANNEL_ID = os.getenv('FARM_CHANNEL_ID')

# Verificar se a variável FARM_CHANNEL_ID está definida
if FARM_CHANNEL_ID is None:
    print("Error: FARM_CHANNEL_ID is not set in the environment variables.")
    exit(1)
else:
    FARM_CHANNEL_ID = int(FARM_CHANNEL_ID)

# Inicialização do bot
@bot.event
async def on_ready():
    print(f'Bot {bot.user} ready')

# Comando para registrar membro e adicionar farm
@bot.command(name='farm')
async def farm_command(ctx):
    await farm(ctx, bot)

# Comando para buscar membro por passaporte ou mostrar dropdown de membros registrados
@bot.command(name='buscar_membro')
async def buscar_membro_command(ctx, passaporte: int = None):
    # Verifica se o comando está sendo usado no canal correto
    if ctx.channel.id != FARM_CHANNEL_ID:
        msg = await ctx.send(f"🚫 Este comando só pode ser usado no canal de farm.")
        await asyncio.sleep(30)
        await msg.delete()
        return
    
    await buscar_membro(ctx, bot, passaporte)

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
try:
    bot.run(DISCORD_BOT_TOKEN)
except KeyboardInterrupt:
    print("Bot desligado manualmente.")

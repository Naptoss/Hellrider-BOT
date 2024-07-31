import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os

# Configurar as intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Carregar variáveis de ambiente
load_dotenv()
token = os.getenv('DISCORD_BOT_TOKEN')
GUILD_ID = os.getenv('GUILD_ID')

if not token or not GUILD_ID:
    raise ValueError("Certifique-se de que DISCORD_BOT_TOKEN e GUILD_ID estão definidos no arquivo .env")

class MyBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        guild = discord.Object(id=int(GUILD_ID))
        await self.tree.sync(guild=guild)
        await self.tree.sync(guild=None)
        print("Todos os comandos globais e específicos do servidor foram removidos.")

bot = MyBot()

@bot.event
async def on_ready():
    print(f'Bot {bot.user} está pronto e todos os comandos foram removidos.')
    await bot.close()

bot.run(token)

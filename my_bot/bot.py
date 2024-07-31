import os
import asyncio
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord import app_commands

from my_bot.commands.farm import farm_command
from my_bot.commands.buscar_membro import buscar_membro_command
from my_bot.commands.consultar import consultar_command
from my_bot.commands.ajuda import ajuda_command

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix='/', intents=intents)
        self.synced = False

    async def setup_hook(self):
        await self.tree.sync(guild=discord.Object(id=GUILD_ID))
        self.synced = True

bot = MyBot()

GUILD_ID = os.getenv('GUILD_ID')

@bot.event
async def on_ready():
    print(f'{bot.user} is ready and slash commands are synced.')

@bot.command(name='sync')
@commands.is_owner()
async def sync_commands(ctx):
    await ctx.bot.tree.sync()
    await ctx.send('Commands synced.')

farm_command(bot)
buscar_membro_command(bot)
consultar_command(bot)
ajuda_command(bot)

load_dotenv()
token = os.getenv('DISCORD_BOT_TOKEN')

bot.run(token)

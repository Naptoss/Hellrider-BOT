import discord
from discord.ext import commands
import sqlite3
from dotenv import load_dotenv
import os
from discord import SelectOption
from discord.ui import Select, View
from collections import defaultdict

# Configurar as intents
intents = discord.Intents.default()
intents.message_content = True  # Permite que o bot leia o conteúdo das mensagens
intents.members = True  # Necessário para buscar informações dos membros

# Início da configuração do bot
bot = commands.Bot(command_prefix='/', intents=intents)

def add_farm_log(user_id, passport, farm_type, quantity):
    conn = sqlite3.connect('database/database.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO farm_logs (user_id, passport, farm_type, quantity)
    VALUES (?, ?, ?, ?)
    ''', (user_id, passport, farm_type, quantity))
    conn.commit()
    conn.close()

# Inicialização do bot
@bot.event
async def on_ready():
    print(f'Bot {bot.user} ready') 
    
# Comando para adicionar farm
@bot.command(name='farm')
async def farm(ctx):
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    user_id = ctx.author.id  # Obtém o ID do usuário que invocou o comando

    await ctx.send('Passaporte: ')
    passport = await bot.wait_for('message', check=check)
    
    # Menu dropdown para Tipo de farm
    options = [
        SelectOption(label="Pólvora", value="Polvora"),
        SelectOption(label="Projétil", value="Projetil"),
        SelectOption(label="Cápsula", value="Capsula")
    ]
    select = Select(placeholder="Escolha o tipo de farm...", options=options)
    
    async def select_callback(interaction):
        farm_type = select.values[0]
        await interaction.response.send_message(f'Tipo de farm selecionado: {farm_type}', ephemeral=True)
        await ctx.send('Quantidade: ')
        quantity = await bot.wait_for('message', check=check)

        # Adicionando informações ao banco de dados
        add_farm_log(user_id, passport.content, farm_type, int(quantity.content))
        await ctx.send(f'Farm adicionado com sucesso ao membro {ctx.author.name}')

    select.callback = select_callback
    view = View()
    view.add_item(select)
    await ctx.send("Escolha o tipo de farm:", view=view)

# Comando para consultar registros de farm
@bot.command(name='consultar_farm')
async def consultar_farm(ctx):
    conn = sqlite3.connect('database/database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, passport, farm_type, SUM(quantity) FROM farm_logs GROUP BY user_id, passport, farm_type')
    rows = cursor.fetchall()
    conn.close()

    farm_data = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    for row in rows:
        user_id, passport, farm_type, quantity = row
        farm_data[user_id][passport][farm_type] += quantity

    for user_id, passports in farm_data.items():
        user = await bot.fetch_user(user_id)
        for passport, farms in passports.items():
            farms_summary = ', '.join([f'{ft} - {qt}' for ft, qt in farms.items()])
            await ctx.send(f"-Membro: {user.name}, Passaporte: {passport}, Farms: {farms_summary}")

# Iniciar o bot
load_dotenv()
token = os.getenv('DISCORD_BOT_TOKEN')
bot.run(token)

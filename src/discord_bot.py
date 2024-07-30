import discord
from discord.ext import commands
import sqlite3
from dotenv import load_dotenv
import os
from discord import SelectOption
from discord.ui import Select, View

# Configurar as intents
intents = discord.Intents.default()
intents.message_content = True  # Permite que o bot leia o conteúdo das mensagens

# Início da configuração do bot
bot = commands.Bot(command_prefix='/', intents=intents)

def add_farm_log(member_name, rank, passport, farm_type, quantity):
    conn = sqlite3.connect('database/database.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO farm_logs (member_name, rank, passport, farm_type, quantity)
    VALUES (?, ?, ?, ?, ?)
    ''', (member_name, rank, passport, farm_type, quantity))
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
    
    await ctx.send('Nome do membro: ')
    member_name = await bot.wait_for('message', check=check)
    await ctx.send('Cargo: ')
    rank = await bot.wait_for('message', check=check)
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
        add_farm_log(member_name.content, rank.content, passport.content, farm_type, int(quantity.content))
        await ctx.send(f'Farm adicionado com sucesso ao membro {member_name.content}')

    select.callback = select_callback
    view = View()
    view.add_item(select)
    await ctx.send("Escolha o tipo de farm:", view=view)

# Comando para consultar registros de farm
@bot.command(name='consultar_farm')
async def consultar_farm(ctx):
    conn = sqlite3.connect('database/database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT member_name, rank, passport, farm_type, quantity, timestamp FROM farm_logs')
    rows = cursor.fetchall()
    conn.close()

    if rows:
        for row in rows:
            await ctx.send(f"Nome: {row[0]}, Cargo: {row[1]}, Passaporte: {row[2]}, Tipo de Farm: {row[3]}, Quantidade: {row[4]}, Data: {row[5]}")
    else:
        await ctx.send("Nenhum registro de farm encontrado.")

# Iniciar o bot
load_dotenv()
token = os.getenv('DISCORD_BOT_TOKEN')
bot.run(token)

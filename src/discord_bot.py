import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
import asyncio
from discord import SelectOption
from discord.ui import Select, View
from pymongo import MongoClient
from datetime import datetime
from collections import defaultdict

# Configurar as intents
intents = discord.Intents.default()
intents.message_content = True  # Permite que o bot leia o conteúdo das mensagens
intents.members = True  # Necessário para buscar informações dos membros

# Início da configuração do bot
bot = commands.Bot(command_prefix='/', intents=intents)

# Conectar ao MongoDB
load_dotenv()
mongo_uri = os.getenv('MONGO_URI')
client = MongoClient(mongo_uri)
db = client['hellriders_bot']
members_collection = db['members']
farm_logs_collection = db['farm_logs']

active_farm_commands = {}  # Rastrear comandos /farm ativos por canal

def add_member(user_id, user_name, passaporte):
    members_collection.update_one(
        {'user_id': user_id},
        {'$set': {'user_id': user_id, 'user_name': user_name, 'passaporte': passaporte}},
        upsert=True
    )

def add_farm_log(user_id, passaporte, farm_type, quantity):
    farm_logs_collection.insert_one({
        'user_id': user_id,
        'passaporte': passaporte,
        'farm_type': farm_type,
        'quantity': quantity,
        'timestamp': datetime.utcnow()
    })

def get_member_by_passport(passaporte):
    return list(farm_logs_collection.find({'passaporte': passaporte}))

def is_passport_registered(passaporte):
    member = members_collection.find_one({'passaporte': passaporte})
    return member

# Inicialização do bot
@bot.event
async def on_ready():
    print(f'Bot {bot.user} ready')

async def get_valid_passport(user):
    def check(m):
        return m.author == user and isinstance(m.channel, discord.DMChannel)
    
    while True:
        await user.send('Por favor, forneça o passaporte (apenas números inteiros):')
        passport_msg = await bot.wait_for('message', check=check)
        passaporte = passport_msg.content

        if passaporte.isdigit():
            return int(passaporte)
        else:
            await user.send("🚫 Passaporte inválido. Deve conter apenas números inteiros.")

# Comando para registrar membro e adicionar farm
@bot.command(name='farm')
async def farm(ctx):
    user = ctx.author  # Usuário que invocou o comando
    user_id = user.id
    user_name = user.name
    channel_id = ctx.channel.id

    if channel_id in active_farm_commands:
        await ctx.send(f"🚫 Outro usuário já está utilizando o comando /farm neste canal. Por favor, aguarde.")
        return

    active_farm_commands[channel_id] = user_id

    try:
        await ctx.send(f"{user.mention}, por favor, verifique suas mensagens diretas para continuar o registro do farm.")
        dm_channel = await user.create_dm()

        passaporte = await get_valid_passport(user)

        # Verificar se o passaporte já está registrado por outro usuário
        registered_member = is_passport_registered(passaporte)
        if registered_member and registered_member['user_id'] != user_id:
            await dm_channel.send(f"🚫 O passaporte {passaporte} já está registrado por outro usuário.")
            return

        # Registrar membro no banco de dados
        add_member(user_id, user_name, passaporte)
        
        # Menu dropdown para Tipo de farm
        options = [
            SelectOption(label="Pólvora", value="Polvora"),
            SelectOption(label="Projétil", value="Projetil"),
            SelectOption(label="Cápsula", value="Capsula")
        ]
        select = Select(placeholder="Escolha o tipo de farm...", options=options)

        async def select_callback(interaction):
            if interaction.user.id != user_id:
                await interaction.response.send_message("🚫 Você não tem permissão para interagir com este menu.", ephemeral=True)
                return

            farm_type = select.values[0]
            await interaction.response.send_message(f'Tipo de farm selecionado: {farm_type}', ephemeral=True)
            await dm_channel.send('Quantidade: ')
            quantity_msg = await bot.wait_for('message', check=lambda m: m.author == user and isinstance(m.channel, discord.DMChannel))
            quantity = int(quantity_msg.content)

            # Adicionando informações ao banco de dados
            add_farm_log(user_id, passaporte, farm_type, quantity)
            await ctx.send(f"Farm adicionado com sucesso ao membro {user.mention}")

        select.callback = select_callback
        view = View()
        view.add_item(select)
        await dm_channel.send("Escolha o tipo de farm:", view=view)

    finally:
        del active_farm_commands[channel_id]

# Comando para buscar todos os membros e seus passaportes
@bot.command(name='buscar_registros')
async def buscar_registros(ctx):
    members = members_collection.find()
    if members:
        for member in members:
            await ctx.send(f"**Membro**: <@{member['user_id']}> - {member['passaporte']}")
    else:
        await ctx.send("Nenhum membro registrado encontrado.")

# Comando para buscar membro por passaporte
@bot.command(name='buscar_membro')
async def buscar_membro(ctx, passaporte: int = None):
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    if passaporte is None:
        await ctx.send('Por favor, forneça o passaporte:')
        passport_msg = await bot.wait_for('message', check=check)
        passaporte = passport_msg.content

        if not passaporte.isdigit():
            await ctx.send("🚫 Passaporte inválido. Deve conter apenas números inteiros.")
            return
        passaporte = int(passaporte)

    rows = get_member_by_passport(passaporte)
    if rows:
        member_data = defaultdict(lambda: defaultdict(int))
        user_id = rows[0]['user_id']
        for row in rows:
            farm_type = row['farm_type']
            quantity = row['quantity']
            date = row['timestamp'].strftime('%d/%m/%Y')
            member_data[date][farm_type] += quantity

        member = await ctx.guild.fetch_member(user_id)
        farms_summary = ''
        for date, farms in member_data.items():
            farms_summary += f"**Data: {date}**\n"
            farms_summary += '\n'.join([f'--> {ft} - {qt}' for ft, qt in farms.items()])
            farms_summary += '\n'
        await ctx.send(f"**Membro** {member.display_name}:\n{farms_summary}")
    else:
        await ctx.send(f"Nenhum registro encontrado para o passaporte {passaporte}")

# Comando para exibir a lista de comandos e suas descrições
@bot.command(name='ajuda')
async def ajuda(ctx):
    help_message = """
    **Comandos Disponíveis:**
    - `/farm`: Registrar uma atividade de farm. O bot irá solicitar o passaporte, tipo de farm e quantidade.
    - `/buscar_registros`: Buscar todos os membros registrados e seus passaportes.
    - `/buscar_membro [passaporte]`: Buscar um membro específico pelo passaporte e exibir suas atividades de farm separadas por data. Se o passaporte não for fornecido, o bot solicitará o passaporte.
    - `/ajuda`: Exibir a lista de comandos disponíveis e suas descrições.
    """
    await ctx.send(help_message)

# Iniciar o bot
load_dotenv()
token = os.getenv('DISCORD_BOT_TOKEN')

try:
    bot.run(token)
except KeyboardInterrupt:
    print("Bot desligado manualmente.")

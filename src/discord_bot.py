import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
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

# Comando para registrar membro e adicionar farm
@bot.command(name='farm')
async def farm(ctx):
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    user_id = ctx.author.id  # Obtém o ID do usuário que invocou o comando
    user_name = ctx.author.name

    await ctx.send('Passaporte: ')
    passport_msg = await bot.wait_for('message', check=check)
    passaporte = passport_msg.content

    # Verificar se o passaporte já está registrado por outro usuário
    registered_member = is_passport_registered(passaporte)
    if registered_member and registered_member['user_id'] != user_id:
        await ctx.send(f"🚫 O passaporte {passaporte} já está registrado por outro usuário.")
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
        farm_type = select.values[0]
        await interaction.response.send_message(f'Tipo de farm selecionado: {farm_type}', ephemeral=True)
        await ctx.send('Quantidade: ')
        quantity_msg = await bot.wait_for('message', check=check)
        quantity = int(quantity_msg.content)

        # Adicionando informações ao banco de dados
        add_farm_log(user_id, passaporte, farm_type, quantity)
        await ctx.send(f"Farm adicionado com sucesso ao membro {ctx.author.mention}")

    select.callback = select_callback
    view = View()
    view.add_item(select)
    await ctx.send("Escolha o tipo de farm:", view=view)

# Comando para buscar todos os membros e seus passaportes
@bot.command(name='buscar_registros')
async def buscar_registros(ctx):
    members = members_collection.find()
    if members:
        for member in members:
            await ctx.send(f"Membro: {member['user_name']}, Passaporte: {member['passaporte']}")
    else:
        await ctx.send("Nenhum membro registrado encontrado.")

# Comando para buscar membro por passaporte
@bot.command(name='buscar_membro')
async def buscar_membro(ctx, passaporte: str = None):
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel
    
    if passaporte is None:
        await ctx.send('Por favor, forneça o passaporte:')
        passport_msg = await bot.wait_for('message', check=check)
        passaporte = passport_msg.content

    rows = get_member_by_passport(passaporte)
    if rows:
        member_data = defaultdict(int)
        user_id = None
        for row in rows:
            user_id = row['user_id']
            farm_type = row['farm_type']
            quantity = row['quantity']
            member_data[farm_type] += quantity

        if user_id:
            user = await bot.fetch_user(user_id)
            farms_summary = ', '.join([f'{ft} - {qt}' for ft, qt in member_data.items()])
            await ctx.send(f"-Membro: {user.name}, Passaporte: {passaporte}, Farms: {farms_summary}")
    else:
        await ctx.send(f"Nenhum registro encontrado para o passaporte {passaporte}")

# Comando para exibir a lista de comandos e suas descrições
@bot.command(name='ajuda')
async def ajuda(ctx):
    help_message = """
    **Comandos Disponíveis:**
    - `/farm`: Registrar uma atividade de farm. O bot irá solicitar o passaporte, tipo de farm e quantidade.
    - `/buscar_registros`: Buscar todos os membros registrados e seus passaportes.
    - `/buscar_membro [passaporte]`: Buscar um membro específico pelo passaporte e exibir suas atividades de farm. Se o passaporte não for fornecido, o bot solicitará o passaporte.
    - `/ajuda`: Exibir a lista de comandos disponíveis e suas descrições.
    """
    await ctx.send(help_message)

# Iniciar o bot
load_dotenv()
token = os.getenv('DISCORD_BOT_TOKEN')
bot.run(token)

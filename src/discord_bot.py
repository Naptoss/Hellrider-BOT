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
import uuid

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

def add_farm_log(user_id, passaporte, farm_type, quantity, img_antes, img_depois):
    id_farm = str(uuid.uuid4())
    farm_logs_collection.insert_one({
        'id_farm': id_farm,
        'user_id': user_id,
        'passaporte': passaporte,
        'farm_type': farm_type,
        'quantity': quantity,
        'img_antes': img_antes,
        'img_depois': img_depois,
        'timestamp': datetime.utcnow()
    })

def get_member_by_passport(passaporte):
    return list(farm_logs_collection.find({'passaporte': passaporte}))

def get_farm_by_id(id_farm):
    return farm_logs_collection.find_one({'id_farm': id_farm})

def is_passport_registered(passaporte):
    member = members_collection.find_one({'passaporte': passaporte})
    return member

def get_all_members():
    return list(members_collection.find())

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

async def get_image(user, prompt):
    def check(m):
        return m.author == user and isinstance(m.channel, discord.DMChannel)
    
    while True:
        await user.send(prompt)
        message = await bot.wait_for('message', check=check)
        if message.attachments:
            return message.attachments[0].url
        else:
            await user.send("🚫 Envie uma imagem válida.")

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

            while True:
                quantity_msg = await bot.wait_for('message', check=lambda m: m.author == user and isinstance(m.channel, discord.DMChannel))
                if quantity_msg.content.isdigit():
                    quantity = int(quantity_msg.content)
                    break
                else:
                    await dm_channel.send("🚫 Quantidade inválida. Deve conter apenas números inteiros.")

            img_antes = await get_image(user, 'Por favor, envie a imagem de antes de colocar o farm no baú.')
            img_depois = await get_image(user, 'Por favor, envie a imagem de depois de colocar o farm no baú.')

            # Adicionando informações ao banco de dados
            add_farm_log(user_id, passaporte, farm_type, quantity, img_antes, img_depois)
            await ctx.send(f"Farm adicionado com sucesso ao membro {user.mention}")

        select.callback = select_callback
        view = View()
        view.add_item(select)
        await dm_channel.send("Escolha o tipo de farm:", view=view)

    finally:
        del active_farm_commands[channel_id]

# Comando para buscar membro por passaporte ou mostrar dropdown de membros registrados
@bot.command(name='buscar_membro')
async def buscar_membro(ctx, passaporte: int = None):
    if passaporte is None:
        members = get_all_members()
        if not members:
            await ctx.send("Nenhum membro registrado encontrado.")
            return

        options = []
        for member in members:
            discord_member = await ctx.guild.fetch_member(member['user_id'])
            display_name = discord_member.display_name if discord_member else member['user_name']
            options.append(SelectOption(label=f"{display_name} ({member['passaporte']})", value=str(member['passaporte'])))
        
        select = Select(placeholder="Escolha um membro para buscar...", options=options)

        async def select_callback(interaction):
            selected_passaporte = int(select.values[0])
            await interaction.response.send_message(f"Buscando informações para o passaporte {selected_passaporte}...", ephemeral=True)
            await fetch_member_data(ctx, selected_passaporte)

        select.callback = select_callback
        view = View()
        view.add_item(select)
        await ctx.send("Escolha um membro para buscar:", view=view)
    else:
        await fetch_member_data(ctx, passaporte)

async def fetch_member_data(ctx, passaporte):
    rows = get_member_by_passport(passaporte)
    if rows:
        member_data = defaultdict(list)
        user_id = rows[0]['user_id']
        for row in rows:
            farm_type = row['farm_type']
            quantity = row['quantity']
            date = row['timestamp'].strftime('%d/%m/%Y')
            time = row['timestamp'].strftime('%H:%M')
            member_data[date].append({
                'farm_type': farm_type,
                'quantity': quantity,
                'id_farm': row['id_farm'],
                'time': time
            })

        member = await ctx.guild.fetch_member(user_id)
        farms_summary = ''
        for date, farms in member_data.items():
            farms_summary += f"**Data: {date}**\n"
            farms_summary += '\n'.join([f'--> {farm["farm_type"]} - {farm["quantity"]}' for farm in farms])
            farms_summary += '\n'

        await ctx.send(f"Farms registrados por **{member.display_name}** \n{farms_summary}")

        options = [SelectOption(label="Não desejo checar nenhum farm", value="no")]
        options += [
            SelectOption(
                label=f"{farm['farm_type']} - {farm['quantity']} - {farm['time']} {date}",
                value=farm['id_farm']
            ) for date, farms in member_data.items() for farm in farms
        ]

        select = Select(placeholder="Selecione o farm que deseja checar.", options=options)

        async def select_callback(interaction):
            selected_id = select.values[0]
            if selected_id == "no":
                await interaction.response.send_message("Checagem encerrada.", ephemeral=True)
            else:
                await interaction.response.send_message(f"Buscando imagens para o farm {selected_id}...", ephemeral=True)
                await fetch_farm_images(ctx, selected_id)

        select.callback = select_callback
        view = View()
        view.add_item(select)
        await ctx.send("Se desejar, selecione um farm para ver as imagens:", view=view)
    else:
        await ctx.send(f"Nenhum registro encontrado para o passaporte {passaporte}")

async def fetch_farm_images(ctx, id_farm):
    farm = get_farm_by_id(id_farm)
    if farm:
        await ctx.send(f"Imagens para o farm ID: {id_farm}\nAntes:\n{farm['img_antes']}\nDepois:\n{farm['img_depois']}")
    else:
        await ctx.send(f"Nenhum registro encontrado para o ID do farm {id_farm}")

# Comando para exibir a lista de comandos e suas descrições
@bot.command(name='ajuda')
async def ajuda(ctx):
    help_message = (
        "**Comandos Disponíveis:**\n"
        "- `/farm`: Use este comando para registrar uma atividade de farm. O bot irá pedir seu passaporte, tipo de farm, quantidade e duas imagens (uma antes e uma depois de colocar o farm no baú).\n"
        "- `/buscar_membro [passaporte]`: Use este comando para buscar as atividades de farm de um membro específico pelo passaporte. Se você não fornecer um passaporte, o bot mostrará uma lista de todos os membros registrados para você escolher.\n"
        "- `/consultar`: Use este comando para ver todos os registros de farm associados ao seu passaporte. O bot enviará as informações diretamente para suas mensagens diretas.\n"
        "- `/ajuda`: Exibe esta lista de comandos e explica como usar cada um deles."
    )
    await ctx.send(help_message)




@bot.command(name='consultar')
async def consultar(ctx):
    user = ctx.author  # Usuário que invocou o comando
    user_id = user.id

    # Verificar o passaporte vinculado ao usuário
    member = members_collection.find_one({'user_id': user_id})
    if not member:
        await ctx.send(f"{user.mention}, você não possui nenhum passaporte registrado.")
        return

    passaporte = member['passaporte']

    # Buscar os registros de farm vinculados ao passaporte
    rows = get_member_by_passport(passaporte)
    if rows:
        member_data = defaultdict(list)
        for row in rows:
            farm_type = row['farm_type']
            quantity = row['quantity']
            date = row['timestamp'].strftime('%d/%m/%Y')
            time = row['timestamp'].strftime('%H:%M')
            member_data[date].append({
                'farm_type': farm_type,
                'quantity': quantity,
                'id_farm': row['id_farm'],
                'time': time
            })

        farms_summary = ''
        for date, farms in member_data.items():
            farms_summary += f"**Data: {date}**\n"
            farms_summary += '\n'.join([f'--> {farm["farm_type"]} - {farm["quantity"]}' for farm in farms])
            farms_summary += '\n'

        dm_channel = await user.create_dm()
        await dm_channel.send(f"**Membro** {user.name}:\n{farms_summary}")
        await ctx.send(f"{user.mention}, por favor, verifique suas mensagens diretas para ver seus registros de farm.")
    else:
        await ctx.send(f"{user.mention}, nenhum registro de farm encontrado para o passaporte {passaporte}.")


# Iniciar o bot
load_dotenv()
token = os.getenv('DISCORD_BOT_TOKEN')

try:
    bot.run(token)
except KeyboardInterrupt:
    print("Bot desligado manualmente.")
import os
import discord
from discord import SelectOption
from discord.ui import Select, View
from collections import defaultdict
from dotenv import load_dotenv
import asyncio
from my_bot.db import get_member_by_passport, get_all_members, get_farm_by_id

load_dotenv()
FARM_CHANNEL_ID = int(os.getenv('FARM_CHANNEL_ID'))

async def buscar_membro(ctx, bot, passaporte: int = None):
    if ctx.channel.id != FARM_CHANNEL_ID:
        msg = await ctx.send("🚫 Este comando não pode ser usado neste canal. Se deseja ver seu farm utilize o comando '!consultar' e siga as instruções.")
        await asyncio.sleep(30)
        await msg.delete()
        return
    
    else:
        if passaporte is None:
            members = get_all_members()
            if not members:
                msg = await ctx.send("Nenhum membro registrado encontrado.")
                await asyncio.sleep(30)
                await msg.delete()
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
                await fetch_member_data(ctx, bot, selected_passaporte)  # Passar bot aqui também
                select.disabled = True  # Desabilitar o dropdown após a seleção
                await interaction.message.edit(view=view)

            select.callback = select_callback
            view = View()
            view.add_item(select)
            msg = await ctx.send("Escolha um membro para buscar:", view=view)
            await asyncio.sleep(30)
            await msg.delete()
        else:
            await fetch_member_data(ctx, bot, passaporte)  # Passar bot aqui também


async def fetch_member_data(ctx, bot, passaporte):  # Receber bot como parâmetro
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

        await ctx.send(f"**Membro** {member.display_name}:\n{farms_summary}")

        # Criar menu dropdown para verificar as imagens
        options = [SelectOption(label="Não", value="no")]
        for date, farms in member_data.items():
            for farm in farms:
                label = f"{farm['farm_type']} - {farm['quantity']} - {farm['time']} {date}"
                options.append(SelectOption(label=label, value=farm['id_farm']))

        select = Select(placeholder="Deseja ver as imagens de algum farm?", options=options)

        async def select_callback(interaction):
            selected_id = select.values[0]
            if selected_id == "no":
                await interaction.response.send_message("Operação encerrada.", ephemeral=True)
            else:
                await interaction.response.send_message(f"Buscando imagens para o farm {selected_id}...", ephemeral=True)
                await fetch_farm_images(ctx, selected_id)

        select.callback = select_callback
        view = View()
        view.add_item(select)
        await ctx.send("Escolha um farm para ver as imagens:", view=view)
    else:
        await ctx.send(f"Nenhum registro encontrado para o passaporte {passaporte}")

async def fetch_farm_images(ctx, id_farm):
    farm = get_farm_by_id(id_farm)
    if farm:
        await ctx.send(f"Imagens para o farm ID: {id_farm}\nAntes:\n{farm['img_antes']}\nDepois:\n{farm['img_depois']}")
    else:
        await ctx.send(f"Nenhum registro encontrado para o ID do farm {id_farm}")

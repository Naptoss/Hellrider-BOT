import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Select, View
from my_bot.db.db_operations import get_all_members, get_member_by_passport, get_farm_by_id
import asyncio

class MemberSelect(Select):
    def __init__(self, members):
        options = [
            discord.SelectOption(
                label=f"{member['user_name']} ({member['passaporte']})",
                value=str(member['passaporte'])
            ) for member in members
        ]
        super().__init__(placeholder='Escolha um membro para buscar...', options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        selected_passaporte = int(self.values[0])
        await interaction.response.send_message(f"Buscando informações para o passaporte {selected_passaporte}...", ephemeral=True)
        await fetch_member_data(interaction, selected_passaporte)

async def fetch_member_data(interaction, passaporte):
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

        member = interaction.guild.get_member(user_id)
        farms_summary = ''
        for date, farms in member_data.items():
            farms_summary += f"**Data: {date}**\n"
            farms_summary += '\n'.join([f'--> {farm["farm_type"]} - {farm["quantity"]}' for farm in farms])
            farms_summary += '\n'

        await interaction.followup.send(f"**Membro** {member.display_name}:\n{farms_summary}")

        options = [discord.SelectOption(label="Não", value="no")] + [
            discord.SelectOption(
                label=f"{farm['farm_type']} - {farm['quantity']} - {farm['time']} {date}",
                value=farm['id_farm']
            ) for date, farms in member_data.items() for farm in farms
        ]

        select = Select(placeholder="Escolha um farm para ver as imagens...", options=options)

        async def select_callback(interaction):
            selected_id = select.values[0]
            if selected_id == "no":
                await interaction.response.send_message("Operação encerrada.", ephemeral=True)
            else:
                await interaction.response.send_message(f"Buscando imagens para o farm {selected_id}...", ephemeral=True)
                await fetch_farm_images(interaction, selected_id)

        select.callback = select_callback
        view = View()
        view.add_item(select)
        await interaction.followup.send("Deseja ver as imagens de algum farm? (Sim/Não)", view=view)

    else:
        await interaction.followup.send(f"Nenhum registro encontrado para o passaporte {passaporte}")

async def fetch_farm_images(interaction, id_farm):
    farm = get_farm_by_id(id_farm)
    if farm:
        await interaction.followup.send(f"Imagens para o farm ID: {id_farm}\nAntes:\n{farm['img_antes']}\nDepois:\n{farm['img_depois']}")
    else:
        await interaction.followup.send(f"Nenhum registro encontrado para o ID do farm {id_farm}")

@app_commands.command(name="buscar_membro", description="Buscar atividades de farm de um membro específico pelo passaporte")
async def buscar_membro_command(interaction: discord.Interaction, passaporte: int = None):
    await buscar_membro(interaction, passaporte)

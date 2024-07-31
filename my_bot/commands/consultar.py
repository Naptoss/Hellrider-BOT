import discord
from my_bot.db.db_operations import get_member_by_passport

async def consultar(interaction: discord.Interaction, bot):
    user = interaction.user
    user_id = user.id

    member_data = get_member_by_passport(user_id)
    if not member_data:
        await interaction.response.send_message("Nenhum registro de farm encontrado para seu passaporte.", ephemeral=True)
        return

    dm_channel = await user.create_dm()
    farms_summary = ''
    for record in member_data:
        farms_summary += f"**Data: {record['timestamp'].strftime('%d/%m/%Y')}**\n"
        farms_summary += f"--> {record['farm_type']} - {record['quantity']}\n"
    
    await dm_channel.send(f"Seus registros de farm:\n{farms_summary}")
    await interaction.response.send_message(f"{user.mention}, verifique suas mensagens diretas para ver seus registros de farm.", ephemeral=True)

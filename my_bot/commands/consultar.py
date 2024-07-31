import discord
from my_bot.db import get_member_by_passport

async def consultar(ctx, bot):
    user = ctx.author
    user_id = user.id

    member_data = get_member_by_passport(user_id)
    if not member_data:
        await ctx.send("Nenhum registro de farm encontrado para seu passaporte.")
        return

    dm_channel = await user.create_dm()
    farms_summary = ''
    for record in member_data:
        farms_summary += f"**Data: {record['timestamp'].strftime('%d/%m/%Y')}**\n"
        farms_summary += f"--> {record['farm_type']} - {record['quantity']}\n"
    
    await dm_channel.send(f"Seus registros de farm:\n{farms_summary}")
    await ctx.send(f"{user.mention}, verifique suas mensagens diretas para ver seus registros de farm.")

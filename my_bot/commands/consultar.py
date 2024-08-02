import discord
from my_bot.db import get_member_by_passport, get_farm_by_id, is_passport_registered

async def consultar(ctx, bot):
    user = ctx.author
    user_id = user.id

    # Verificar se o passaporte do usuário está registrado
    member = is_passport_registered(user_id)
    if not member:
        await ctx.send("Nenhum passaporte registrado para seu usuário.")
        return

    passaporte = member['passaporte']
    member_data = get_member_by_passport(passaporte)
    if not member_data:
        await ctx.send("Nenhum registro de farm encontrado para seu passaporte.")
        return

    dm_channel = await user.create_dm()
    farms_summary = ''
    options = []
    for record in member_data:
        farm_id = record['id_farm']
        farm_type = record['farm_type']
        quantity = record['quantity']
        date = record['timestamp'].strftime('%d/%m/%Y')
        time = record['timestamp'].strftime('%H:%M')
        farms_summary += f"**Data: {date}**\n--> {farm_type} - {quantity}\n"

        options.append(discord.SelectOption(label=f"{farm_type} - {quantity} - {time} {date}", value=farm_id))

    await dm_channel.send(f"Seus registros de farm:\n{farms_summary}")

    select = discord.ui.Select(placeholder="Escolha um registro para ver as imagens", options=options)

    async def select_callback(interaction):
        selected_id = select.values[0]
        await interaction.response.send_message(f"Buscando imagens para o farm {selected_id}...", ephemeral=True)
        await fetch_farm_images(ctx, selected_id)

    select.callback = select_callback
    view = discord.ui.View()
    view.add_item(select)
    await dm_channel.send("Escolha um registro para ver as imagens:", view=view)
    await ctx.send(f"{user.mention}, verifique suas mensagens diretas para ver seus registros de farm.")

async def fetch_farm_images(ctx, id_farm):
    farm = get_farm_by_id(id_farm)
    if farm:
        await ctx.send(f"Imagens para o farm ID: {id_farm}\nAntes:\n{farm['img_antes']}\nDepois:\n{farm['img_depois']}")
    else:
        await ctx.send(f"Nenhum registro encontrado para o ID do farm {id_farm}")

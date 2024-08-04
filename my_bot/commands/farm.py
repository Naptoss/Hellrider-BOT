import discord
from discord import SelectOption
from discord.ui import Select, View
import asyncio
from my_bot.db import add_member, add_farm_log, is_passport_registered
from my_bot.utils import get_valid_passport, get_image

active_farm_commands = {}

async def farm(ctx, bot):
    user = ctx.author
    user_id = user.id
    user_name = user.name
    channel_id = ctx.channel.id

    if channel_id in active_farm_commands:
        msg = await ctx.send(f"🚫 Outro usuário já está utilizando o comando /farm neste canal. Por favor, aguarde.")
        await asyncio.sleep(30)
        await msg.delete()
        return

    active_farm_commands[channel_id] = user_id

    try:
        msg = await ctx.send(f"{user.mention}, por favor, verifique suas mensagens diretas para continuar o registro do farm.")
        await asyncio.sleep(30)
        await msg.delete()
        dm_channel = await user.create_dm()

        passaporte = await get_valid_passport(bot, user)

        registered_member = is_passport_registered(passaporte)
        if registered_member and registered_member['user_id'] != user_id:
            msg = await dm_channel.send(f"🚫 O passaporte {passaporte} já está registrado por outro usuário.")
            await asyncio.sleep(30)
            await msg.delete()
            return

        add_member(user_id, user_name, passaporte)

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

            # Desabilitar o dropdown após a seleção
            select.disabled = True
            await interaction.message.edit(view=view)

            msg = await dm_channel.send('Quantidade: ')
            while True:
                quantity_msg = await bot.wait_for('message', check=lambda m: m.author == user and isinstance(m.channel, discord.DMChannel))
                if quantity_msg.content.isdigit():
                    quantity = int(quantity_msg.content)
                    await msg.delete()
                    break
                else:
                    msg = await dm_channel.send("🚫 Quantidade inválida. Deve conter apenas números inteiros.")
                    await asyncio.sleep(30)
                    await msg.delete()

            img_antes = await get_image(bot, user, 'Por favor, envie uma imagem de antes de colocar o farm no baú.')
            img_depois = await get_image(bot, user, 'Por favor, envie uma imagem de depois de colocar o farm no baú.')

            add_farm_log(user_id, passaporte, farm_type, quantity, img_antes, img_depois)
            success_msg = await ctx.send(f"Farm adicionado com sucesso ao membro {user.mention}")
            await asyncio.sleep(30)
            await success_msg.delete()

        select.callback = select_callback
        view = View()
        view.add_item(select)
        msg = await dm_channel.send("Escolha o tipo de farm:", view=view)
        await asyncio.sleep(30)
        await msg.delete()

    finally:
        del active_farm_commands[channel_id]

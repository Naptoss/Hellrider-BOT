import discord

async def get_valid_passport(bot, user):
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

async def get_image(bot, user, prompt):
    def check(m):
        return m.author == user and isinstance(m.channel, discord.DMChannel)
    
    while True:
        await user.send(prompt)
        message = await bot.wait_for('message', check=check)
        if message.attachments:
            return message.attachments[0].url
        else:
            await user.send("🚫 Envie uma imagem válida.")

import discord
from my_bot.db import get_member_by_passport, add_payment_log, clear_member_farms

async def pagar_membro(ctx, bot):
    def check(m):
        return m.author == ctx.author and isinstance(m.channel, discord.DMChannel)
    
    await ctx.send(f"{ctx.author.mention}, por favor, verifique suas mensagens diretas para continuar.")
    dm_channel = await ctx.author.create_dm()

    await dm_channel.send("Qual é o passaporte do membro que será pago?")
    passaporte_msg = await bot.wait_for('message', check=check)
    passaporte = int(passaporte_msg.content)

    farms = get_member_by_passport(passaporte)
    if not farms:
        await dm_channel.send("Nenhum registro de farm encontrado para este passaporte.")
        return

    farms_summary = ''
    total_quantity = 0
    for farm in farms:
        farms_summary += f"{farm['farm_type']} - {farm['quantity']}\n"
        total_quantity += farm['quantity']
    
    await dm_channel.send(f"Registros de farm para o passaporte {passaporte}:\n{farms_summary}")

    await dm_channel.send("Qual é o valor total a ser pago?")
    valor_msg = await bot.wait_for('message', check=check)
    valor = valor_msg.content

    await dm_channel.send(f"Confirma o pagamento de {valor} para o passaporte {passaporte}? (sim/não)")
    confirm_msg = await bot.wait_for('message', check=check)
    if confirm_msg.content.lower() == 'sim':
        add_payment_log(passaporte, valor)
        clear_member_farms(passaporte)
        await dm_channel.send("Pagamento confirmado e registros de farm apagados.")
    else:
        await dm_channel.send("Operação cancelada.")

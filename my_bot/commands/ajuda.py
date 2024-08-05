import discord

async def ajuda(ctx):
    help_message = (
        "**Comandos Disponíveis:**\n"
        "- `!farm`: Use este comando para registrar uma atividade de farm. O bot irá pedir seu passaporte, tipo de farm, quantidade e duas imagens (uma antes e uma depois de colocar o farm no baú).\n"
        "- `!buscar_membro [passaporte]`: Use este comando para buscar as atividades de farm de um membro específico pelo passaporte. Se você não fornecer um passaporte, o bot mostrará uma lista de todos os membros registrados para você escolher.\n"
        "- `!consultar`: Use este comando para ver todos os registros de farm associados ao seu passaporte. O bot enviará as informações diretamente para suas mensagens diretas.\n"
        "- `!ajuda`: Exibe esta lista de comandos e explica como usar cada um deles."
        "Teste"
    )
    await ctx.send(help_message)

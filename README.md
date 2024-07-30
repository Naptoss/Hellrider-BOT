# Hellrider BOT

O Hellrider BOT é um bot desenvolvido para gerenciar e registrar as atividades dos membros de um moto clube virtual, incluindo a captura de informações sobre suas atividades de farm. O bot interage com os usuários no Discord, permitindo o registro e a consulta de dados de maneira fácil e eficiente.

## Funcionalidades

- **Registrar Atividades de Farm**: Os membros podem registrar suas atividades de farm, incluindo tipo de farm, quantidade e passaporte.
- **Consultar Atividades**: Os administradores podem consultar as atividades registradas de um membro específico ou obter um resumo das atividades de todos os membros.
- **Interações com Menu Dropdown**: Utiliza menus dropdown para uma experiência de usuário mais intuitiva ao selecionar tipos de farm.
- **Busca por Passaporte**: Permite buscar informações de um membro específico através do passaporte.

## Tecnologias Utilizadas

- **Python**: Linguagem de programação principal.
- **discord.py**: Biblioteca para interações com a API do Discord.
- **sqlite3**: Banco de dados leve para armazenamento de dados.
- **dotenv**: Gerenciamento de variáveis de ambiente.

## Pré-requisitos

- **Python 3.6+**: Certifique-se de ter o Python instalado.
- **Bibliotecas Python**: Instale as bibliotecas necessárias utilizando o `pip`.

## Comandos Disponíveis
/farm

Inicia o processo de registro de uma nova atividade de farm. O bot solicitará as seguintes informações:

    Passaporte: Identificação do membro.
    Tipo de Farm: Escolha entre "Pólvora", "Projétil" ou "Cápsula".
    Quantidade: Número de itens farmeados.

/consultar_farm

Consulta e exibe um resumo das atividades de farm de todos os membros registrados.
/consultar_membro

    Solicita o passaporte do membro e exibe as atividades de farm registradas para esse passaporte específico.

## Estruta do Projeto
        hellrider-bot/
          ├── database/
          │   └── database.db         # Banco de dados SQLite
          ├── src/
          │   └── discord_bot.py      # Script principal do bot
          ├── .env                    # Arquivo de variáveis de ambiente (não incluído no repositório)
          ├── README.md               # Este arquivo
          └── requirements.txt        # Dependências do projeto


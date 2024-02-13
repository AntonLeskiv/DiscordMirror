import discord
from discord.ext import commands, tasks
from colorama import Fore
import requests
import json
import threading

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
def load_config(): 
    with open("config.json", 'r') as file:
        data = json.load(file)
    
    return data["filter_file"], data["server_a"], data["server_b"], data["discord_token"]

FILTER_FILE, ID_SERVER_A, ID_SERVER_B, DISCORD_TOKEN = load_config()

def cargar_categorias_permitidas():
    try:
        with open(FILTER_FILE, "r") as file:
            return [int(line.strip()) for line in file.readlines()]
    except FileNotFoundError:
        print(f"{Fore.RED}Error: The file {FILTER_FILE} was not found{Fore.WHITE}")
        return []
    
categorias_permitidas = cargar_categorias_permitidas()
print(categorias_permitidas)

@bot.event  
async def on_ready():
    global SERVER_A, SERVER_B
    SERVER_A = bot.get_guild(ID_SERVER_A)
    print(SERVER_A.name)
    SERVER_B = bot.get_guild(ID_SERVER_B)
    print(SERVER_B.name)
    print(f'{Fore.GREEN}Logged in as {bot.user.name}#{bot.user.discriminator} -> ID {bot.user.id}{Fore.WHITE}')
    
    sync_channels_and_categories.start(SERVER_A, SERVER_B) 

@tasks.loop(seconds=60)
async def sync_channels_and_categories(SERVER_A, SERVER_B):
    for category_a in SERVER_A.categories:
        if category_a.id in categorias_permitidas:
            category_b = discord.utils.get(SERVER_B.categories, name=category_a.name)
            if not category_b:
                category_b = await SERVER_B.create_category(category_a.name)
                print(f"Creada nueva categoría: {category_b.name}")

            for channel_a in category_a.text_channels:
                normalized_channel_name = channel_a.name.lower().replace(' ', '-')
                channel_b = discord.utils.get(category_b.text_channels, name=normalized_channel_name)

                if not channel_b:
                    await category_b.create_text_channel(normalized_channel_name)
                    print(f"Creado nuevo canal: {normalized_channel_name}")
                    
    for category_b in SERVER_B.categories:
        if category_b.name in categorias_permitidas:
            category_a = discord.utils.get(SERVER_A.categories, name=category_b.name)
            if not category_a:
                await category_b.delete()
            else:
                for channel_b in category_b.text_channels:
                    channel_a = discord.utils.get(category_a.text_channels, name=channel_b.name)
                    if not channel_a:
                        await channel_b.delete()
 
 
async def get_or_create_webhook(channel):
    webhooks = await channel.webhooks()
    if webhooks:
        return webhooks[0].url
    else:
        webhook = await channel.create_webhook(name="Nuevo Webhook")
        return webhook.url
 
@bot.event
async def on_message(message):
    try:
        if message.guild.id == ID_SERVER_A and message.channel.category.id in categorias_permitidas:
            category_name = message.channel.category.name
            category_b = discord.utils.get(SERVER_B.categories, name=category_name)
            if category_b:
                channel_b = discord.utils.get(category_b.text_channels, name=message.channel.name)

            if channel_b:
                webhook_url = await get_or_create_webhook(channel_b)
                threading.Thread(target=process_message, args=(message, webhook_url)).start()
    except Exception as e:
        print(f"Error: {e}")

def process_message(message, webhook_url):
    try:
        data = {
            "content": message.content,
            "username": message.author.display_name,
            "avatar_url": str(message.author.avatar_url)
        }

        if message.embeds:
            data["embeds"] = [embed.to_dict() for embed in message.embeds]

        result = requests.post(webhook_url, json=data)

        if result.status_code not in (200, 201, 202, 203, 204, 205):
            print(f"Error al enviar mensaje: {result.status_code}")
    except Exception as e:
        print(f"Error: {e}")

bot.run(DISCORD_TOKEN, bot=False)



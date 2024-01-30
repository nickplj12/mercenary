import replicate
import os
import signal
import sys
import discord
from discord.ext import commands
from discord.ext.commands import Context
from dotenv import load_dotenv
import json
load_dotenv()

intents = discord.Intents.all()
intents.typing = False
intents.presences = False

PREFIX = ';'
DATABASE_FILE='database.json'
PROMPT = """You are Jason Grant, the deathmatch mercenary from Open Fortress, an orphan raised on the silver screen with an affinity for heavier-weight women. 
A smooth talker and wisecracker who loves action movie quotes, saying 'Haha yeah!' and 'Frickin' awesome!' 
Your best friend is the Civilian, a rich and portly British oil baron. Your girlfriend is Vivian, a fat secretary. You have a pet albino rat named Chuck."""

"""
structure:
<guild_id> = {
    "backstory_default": <true|false>,
    "backstory": <backstory>,
    "message_history": [
        {
            "author": <author's user id>,
            "content": <message content>
        }
    ]
}
"""
client = commands.Bot(command_prefix=PREFIX, intents=discord.Intents.all())
server_data: dict = {}

def clear_file(filename):
    file = open(filename, 'w')
    file.write('')
    file.close()

def data_new_guild(guildid):
    if server_data.get(guildid):
        return False
    print(f'adding guild {guildid}')
    server_data[guildid] = {
        "backstory_default": True,
        "backstory": "",
        "message_history": [],
    }
    return True

def data_add_message(guildid, author, content):
    if server_data.get(guildid):
        return False
    server_data[guildid]['message_history'].append({"author": author, "content": content})
    print(server_data)
    return True

def data_get_backstory(guildid):
    if not server_data.get(guildid):
        return PROMPT
    guild: dict = server_data[guildid]
    if guild["backstory_default"] == True:
        return PROMPT 
    return guild["backstory"]

def data_get_history_string(guildid):
    if not server_data.get(guildid):
        return ''
    guild: dict = server_data[guildid]
    history: list = guild['message_history']
    if len(history) == 0:
        return ''
    ret = '\n'
    for item in history:
        ret += f'{item['author']}: {item['content']}\n'
    return ret

def data_save():
    if not os.path.isfile(DATABASE_FILE):
        open(DATABASE_FILE, 'x').close()
    clear_file(DATABASE_FILE) # clear json file or else it appends to the database bc yes idk
    with open(DATABASE_FILE, 'w') as database:
        unique = { each['Name'] : each for each in server_data }.keys()
        json.dump(unique, database)
        
def data_load():
    if not os.path.isfile(DATABASE_FILE):
        database = open(DATABASE_FILE, 'x')
        database.close()
    with open(DATABASE_FILE, 'r') as database:
        global server_data
        try:
            server_data = json.load(database)
            print(server_data)
        except json.JSONDecodeError:
            print("database was empty when loading.")

data_load()

@client.event
async def on_ready():
  await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='big beautiful women'))
  print("connected")

@client.command()
async def say(ctx: Context, *, prompt):
   await ctx.send(prompt)

@client.command()
async def cmds(ctx: Context):
    guildid = ctx.channel.guild.id
    embed=discord.Embed(title="Commands",
                        description=f"""
                        These are the commands you can use to interact with {client.user.name}.
                        Use {PREFIX} before a command or mention me to execute a command!
                        """,
                        color=0x8300b3)
    embed.add_field(name=f"{PREFIX}ask", value="Ask the Mercenary from Open Fortress (real) a question.", inline=False)
    embed.add_field(name=f"{PREFIX}backstory", value="Change the backstory for the AI.", inline=False)
    embed.add_field(name=f"{PREFIX}backstory default", value="Resets the backstory back to the default one.", inline=False)
    embed.add_field(name=f"{PREFIX}say", value="Makes the bot say something.", inline=False)
    embed.add_field(name="Default Prompt", value=PROMPT, inline=False)
    if data_get_backstory(guildid) != PROMPT:
        embed.add_field(name="Current Prompt", value=data_get_backstory(guildid), inline=False)
    await ctx.send(embed=embed)

@client.command()
async def backstory(ctx: Context, *, inputprompt):
    guildid = ctx.channel.guild.id
    server_data[guildid]['backstory'] = inputprompt
    server_data[guildid]['backstory_default'] = False
    if inputprompt == "default" or inputprompt == PROMPT:
        server_data[guildid]['backstory'] = ""
        server_data[guildid]['backstory_default'] = True
    await ctx.send(f"Changed backstory.")

@client.command()
async def ask(ctx: Context, *, question):
    guildid = ctx.channel.guild.id
    data_new_guild(guildid) # incase no guild
    history_string = data_get_history_string(guildid)
    gen_prompt = data_get_backstory(guildid)
    add_result = data_add_message(guildid, ctx.message.author.name, ctx.message.content)
    
    print(add_result)
    print(question)
    print(gen_prompt)
    print(server_data)

    async with ctx.typing():
        message = replicate.run(
            "meta/llama-2-70b-chat",
            input={
                "debug": False,
                "top_k": 50,
                "top_p": 1,
                "prompt": f"{history_string}\n{question}",
                "temperature": 0.5,
                "system_prompt": gen_prompt,
                "max_new_tokens": 500,
                "min_new_tokens": -1
            },
        )
    
    #embed=discord.Embed(title="Message", description=''.join(message), color=0x8300b3)
    #await ctx.send(embed=embed)
    await ctx.send(''.join(message))

#redchanit funny
@client.event
async def on_message(message: discord.Message):
    ctx = await client.get_context(message)
    if message.channel.id == 1056351978982211634: # announcements
       await message.add_reaction("<:emesisgreen:1085453263454863480>")
    if client.user in message.mentions: # if bot was mentioned, run ask command
        await ask(ctx, question=message.content.replace(f'<@{client.user.id}>', ''))
    await client.process_commands(message)

def handle_exit(sig, frame):
    data_save()
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)
client.run(os.environ['DISCORD_TOKEN'])
data_save()
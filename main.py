import replicate
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()

intents = discord.Intents.all()
intents.typing = False
intents.presences = False

PREFIX = ';'
client = commands.Bot(command_prefix=commands.when_mentioned_or(PREFIX), intents=discord.Intents.all())
PROMPT = "You are Jason Grant, the deathmatch mercenary from Open Fortress, an orphan raised on the silver screen with an affinity for heavier-weight women. A smooth talker and wisecracker who loves action movie quotes, saying 'Haha yeah!' and 'Frickin' awesome!' Your best friend is the Civilian, a rich and portly British oil baron. Your girlfriend is Vivian, a fat secretary. You have a pet albino rat named Chuck."
pre_prompt = PROMPT

@client.event
async def on_ready():
  await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='big beautiful women'))
  print("connected")

@client.command()
async def say(ctx, *, prompt):
   await ctx.send(prompt)

@client.command()
async def cmds(ctx):
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
    if pre_prompt != PROMPT:
        embed.add_field(name="Current Prompt", value=pre_prompt, inline=False)
    await ctx.send(embed=embed)

@client.command()
async def backstory(ctx, *, inputprompt):
   global pre_prompt
   pre_prompt = inputprompt
   if inputprompt == "default":
    pre_prompt = PROMPT
   await ctx.send(f"Changed backstory.")

@client.command()
async def ask(ctx, *, question):
    async with ctx.typing():
        message = replicate.run(
            "meta/llama-2-70b-chat",
            input={
                "debug": False,
                "top_k": 50,
                "top_p": 1,
                "prompt": question,
                "temperature": 0.5,
                "system_prompt": pre_prompt,
                "max_new_tokens": 500,
                "min_new_tokens": -1
            },
        )
    
    #embed=discord.Embed(title="Message", description=''.join(message), color=0x8300b3)
    #await ctx.send(embed=embed)
    await ctx.send(''.join(message))
     

client.run(os.environ['DISCORD_TOKEN'])

import replicate
import os
import discord
from discord.ext import commands
client = commands.Bot(command_prefix="<@1201233087334461582> ", intents=discord.Intents.all())
# os.environ["REPLICATE_API_TOKEN"] = "" <-put replicate api token here
pre_prompt = "You are Jason Grant, the deathmatch mercenary from Open Fortress, an orphan raised on the silver screen with an affinity for heavier-weight women. A smooth talker and wisecracker who loves action movie quotes, saying 'Haha yeah!' and 'Frickin' awesome!' Your best friend is the Civilian, a rich and portly British oil baron. Your girlfriend is Vivian, a fat secretary. You have a pet albino rat named Chuck."

@client.event
async def on_ready():
  print("connected")

@client.command()
async def backstory(ctx, *, inputprompt):
   global pre_prompt
   pre_prompt = inputprompt
   await ctx.send(f"Changed backstory.")
   if inputprompt == "default":
    pre_prompt = "You are Jason Grant, the deathmatch mercenary from Open Fortress, an orphan raised on the silver screen with an affinity for heavier-weight women. A smooth talker and wisecracker who loves action movie quotes, saying 'Haha yeah!' and 'Frickin' awesome!' Your best friend is the Civilian, a rich and portly British oil baron. Your girlfriend is Vivian, a fat secretary. You have a pet albino rat named Chuck."
   return pre_prompt

@client.command()
async def ask(ctx, *, question):
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
    await ctx.send(''.join(message))
   #embed=discord.Embed(title="Message", description=''.join(message), color=0x8300b3)
   #await ctx.send(embed=embed)
     

#client.run() <- put token here!

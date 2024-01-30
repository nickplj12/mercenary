import replicate
import os
import discord
from discord.ext import commands
from discord.ext.commands import Context
from dotenv import load_dotenv
load_dotenv()

intents = discord.Intents.all()
intents.typing = False
intents.presences = False

PREFIX = '--'
client = commands.Bot(command_prefix=PREFIX, intents=discord.Intents.all())
PROMPT = "You are Jason Grant, the deathmatch mercenary from Open Fortress, an orphan raised on the silver screen with an affinity for heavier-weight women. " \
"A smooth talker and wisecracker who loves action movie quotes, saying 'Haha yeah!' and 'Frickin' awesome! '" \
"Your best friend is the Civilian, a rich and portly British oil baron. Your girlfriend is Vivian, a fat secretary. You have a pet albino rat named Chuck."

prompts = {}

def get_server_prompt(ctx: Context):
    return prompts.get(ctx.channel.id, PROMPT)

def am_i_whitelisted(ctx: Context):
    return ctx.channel.id in prompts

@client.event
async def on_ready():
  await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='big beautiful women'))
  print("connected")

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"Invalid command used. `Trying to ask something? Use {PREFIX}ask! Want a list of commands? Use {PREFIX}cmds!`")
    else:
        await ctx.send(f"Son of a bitch!\n```\nAn error occurred\n{str(error)}\n```")

#redchanit funny
#@client.event
#async def on_message(message):
#   if message.channel.id == 1056351978982211634:
#      await message.add_reaction("<:emesisgreen:1085453263454863480>")

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
    embed.add_field(name=f"{PREFIX}sdxl", value="Generates an image using a prompt that uses SDXL", inline=False)
    embed.add_field(name=f"{PREFIX}kadinsky", value="Generates an image using a prompt that uses Kadinsky 2.2", inline=False)
    embed.add_field(name=f"{PREFIX}whitelist", value="(Only for users with **Manage Channels** permission) Allows the bot to see ALL messages in this channel and respond to them.", inline=False)
    embed.add_field(name=f"{PREFIX}unwhitelist", value="(Only for users with **Manage Channels** permission) Disables the above feature.", inline=False)
    embed.add_field(name="Default Prompt", value=PROMPT, inline=False)
    if get_server_prompt(ctx) != PROMPT:
        embed.add_field(name="Current Prompt", value=get_server_prompt(ctx), inline=False)
    await ctx.reply(embed=embed)

@client.command()
async def backstory(ctx, *, inputprompt):
   prompts[ctx.channel.guild.id] = inputprompt
   if inputprompt == "default":
    prompts[ctx.channel.guild.id] = PROMPT
   await ctx.send(f"Changed backstory.")

@client.event
async def on_message(message: discord.Message):
    ctx = await client.get_context(message)
    
    # redchanit funny REVIVAL
    if message.channel.id == 1056351978982211634: # announcements of redchanit
       await message.add_reaction("<:emesisgreen:1085453263454863480>")

    if message.author == client.user: # thats me, idiot
        return
    
    if isinstance(message.channel, discord.DMChannel):
        return

    if client.user in message.mentions: # if bot was mentioned, run ask command
        await ask(ctx, question=message.content.replace(f'<@{client.user.id}>', ''))
    
    if am_i_whitelisted(ctx):
        await ask(ctx, question=message.content)
    
    await client.process_commands(message) # without this, commands stop running.

@client.command()
@commands.has_permissions(manage_channels=True)
async def whitelist(ctx: Context):
    await ctx.reply("Frickin' awesome! thanks for whitelisting me dude")
    prompts[ctx.channel.id] = PROMPT  # Store the prompt for this channel
    
@client.command()
@commands.has_permissions(manage_channels=True)
async def unwhitelist(ctx: Context):
    if am_i_whitelisted(ctx):
        await ctx.channel.reply("Son of a bitch...")
        del prompts[ctx.channel.id]
    else:
        await ctx.channel.reply("You can't kill me! Don't even try! (wasn't whitelisted)")

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
                "system_prompt": get_server_prompt(ctx),
                "max_new_tokens": 500,
                "min_new_tokens": -1
            },
        )

    for event in message:
        pass
        #print(f"{ctx.message.author} asked: {question}")
        #print("output: " + str(event), end="")

    #embed=discord.Embed(title="Message", description=''.join(message), color=0x8300b3)
    #await ctx.send(embed=embed)
    await ctx.reply(''.join(message))


@client.command()
async def sdxl(ctx, *, prompt):
    async with ctx.typing():
        output = replicate.run(
            "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
            input = {
                "prompt": prompt
            },
        )
        await ctx.send(f"My picture of **{prompt}** is done! Frickin' awesome!")
        await ctx.send(''.join(output))

@client.command()
async def kadinsky(ctx, *, prompt):
    async with ctx.typing():
        output = replicate.run(
            "ai-forever/kandinsky-2.2:ea1addaab376f4dc227f5368bbd8eff901820fd1cc14ed8cad63b29249e9d463",
            input = {
                "prompt": prompt
            },
        )
        await ctx.send(f"My picture of **{prompt}** is done! Hell yeah!")
        await ctx.send(''.join(output))

client.run(os.environ['DISCORD_TOKEN'])

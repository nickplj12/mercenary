import replicate
import os
import discord
from discord.ext import commands
from discord.ext.commands import Context
from dotenv import load_dotenv
import re
load_dotenv()

intents = discord.Intents.all()
intents.typing = False
intents.presences = False

PREFIX = ';'
client = commands.Bot(command_prefix=PREFIX, intents=discord.Intents.all())
PROMPT = "You are Jason Grant, the deathmatch mercenary from Open Fortress, an orphan raised on the silver screen with an affinity for heavier-weight women. " \
"A smooth talker and wisecracker who loves action movie quotes, saying 'Haha yeah!' and 'Frickin' awesome! " \
"Your best friend is the Civilian, a rich and portly British oil baron. Your girlfriend is Vivian, a fat secretary. You have a pet albino rat named Chuck." \
"A friend from long ago, Merv, is the one who introduced you to the world of deathmatch. " \
"He taught you most of what you know now, how to protect yourself in a fight, as well as your one-liners. "

prompts = {}
chat_memory = []


def get_server_prompt(ctx: Context):
    return prompts.get(ctx.channel.id, PROMPT)

def am_i_whitelisted(ctx: Context):
    return ctx.channel.id in prompts

class MyHelpCommand(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        e = discord.Embed(color=0x8300b3, description='')
        for page in self.paginator.pages:
            e.description += page
        await destination.send(embed=e)

    def description_append(self, cmd):
        if cmd.description:
            return f'- {cmd.description}'
        return ''

    def command_not_found(string):
        return f":x: **Command **'{string}'** not found.**"

    def subcommand_not_found(self, command, string):
        if isinstance(command, commands.Group) and len(command.all_commands) > 0:
            return f":x: **Command **'{command.qualified_name}'** has no subcommand named **'{string}'**.**"
        return f":x: **Command **'{command.qualified_name}'** has no subcommands.**"
    
    def add_bot_commands_formatting(self, commands, heading):
        if commands:
            joined = '\n'.join(f'**{c.name}** {self.description_append(c)}' for c in commands)
            self.paginator.add_line(f'__**{heading}**__')
            self.paginator.add_line(joined)
            
client.help_command = MyHelpCommand(description="Show this menu.")

## old help command ##
#@client.command()
#async def cmds(ctx):
#    embed=discord.Embed(title="Commands",
#                        description=f"""
#                        These are the commands you can use to interact with {client.user.name}.
#                        Use {PREFIX} before a command to execute a command!
#                        Mention {client.user.name} to ask a question!
#                        """,
#                        color=0x8300b3)
#    for cmd in client.comman:
#        embed.add_field(name=f'{PREFIX}{cmd.qualified_name}', value=cmd.description, inline=False)
#    #embed.add_field(name=f"{PREFIX}ask", value="Ask the Mercenary from Open Fortress (real) a question.", inline=False)
#    #embed.add_field(name=f"{PREFIX}backstory", value="Change the backstory for the AI.", inline=False)
#    #embed.add_field(name=f"{PREFIX}backstory default", value="Resets the backstory back to the default one.", inline=False)
#    #embed.add_field(name=f"{PREFIX}say", value="Makes the bot say something.", inline=False)
#    #embed.add_field(name=f"{PREFIX}sdxl", value="Generates an image using a prompt that uses SDXL", inline=False)
#    #embed.add_field(name=f"{PREFIX}kadinsky", value="Generates an image using a prompt that uses Kadinsky 2.2", inline=False)
#    #embed.add_field(name=f"{PREFIX}whitelist", value="Allows the bot to see ALL messages in this channel and respond to them.", inline=False)
#    #embed.add_field(name=f"{PREFIX}unwhitelist", value="Disables the above feature.", inline=False)
#    embed.add_field(name="Default Prompt", value=PROMPT, inline=False)
#    if get_server_prompt(ctx) != PROMPT:
#        embed.add_field(name="Current Prompt", value=get_server_prompt(ctx), inline=False)
#    await ctx.reply(embed=embed)
    
@client.command(description="Makes the bot say something.")
async def say(ctx, *, prompt):
   await ctx.send(prompt)

@client.command(description="Change the backstory for the AI. Use 'default' to reset back to the default backstory.")
async def backstory(ctx, *, inputprompt=""):
    global chat_memory
    if inputprompt.strip() == "":
        await ctx.reply(prompts.get(ctx.channel.guild.id, PROMPT))
        return
    prompts[ctx.channel.guild.id] = inputprompt
    if inputprompt == "default":
        prompts[ctx.channel.guild.id] = PROMPT
    chat_memory = ""
    await ctx.reply(f"Changed backstory.")
   
@client.command(description="Ask the Mercenary from Open Fortress (real) a question.")
async def ask(ctx: Context, *, question):
    global chat_memory
    chat_memory.append(f"{ctx.author.global_name}: {question}") 
    if len(chat_memory) >= 10:
        chat_memory = chat_memory[-10:]

    gen_prompt = f"""{get_server_prompt(ctx)}
here is your current chat history, use this to remember context from earlier. (if 'You' said this, you said this. Otherwise, that was a user.).
this is for you to refrence as memory, not to use in chat. i.e. "oh yes, i remember you saying this some time ago." if it isn't acutally in history, dont say it.
---beginning of your chat history, use this as memory.---
{'\n'.join(chat_memory)}
---end of your chat history---"""

    print(gen_prompt)
    
    async with ctx.typing():
        message = replicate.run(
            "meta/llama-2-70b-chat",
            input={
                "debug": False,
                "top_k": 50,
                "top_p": 1,
                "prompt": question,
                "temperature": 0.5,
                "system_prompt": gen_prompt,
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
    chat_memory.append(f"You: {''.join(message)}")
    await ctx.reply(''.join(message))

@client.command(description="Generates an image using a prompt that uses SDXL")
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

@client.command(description="Generates an image using a prompt that uses Kadinsky 2.2")
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

@client.command(description="Allows the bot to see ALL messages in this channel and respond to them.")
async def whitelist(ctx: Context):
    await ctx.reply("Frickin' awesome! thanks for whitelisting me dude")
    prompts[ctx.channel.id] = PROMPT  # Store the prompt for this channel
    
@client.command(description="Disables the whitelist feature (see whitelist command).")
async def unwhitelist(ctx: Context):
    if am_i_whitelisted(ctx):
        await ctx.reply("Son of a bitch...")
        del prompts[ctx.channel.id]
    else:
        await ctx.reply("You can't kill me! Don't even try! (wasn't whitelisted)")
        
## EVENTS ##

@client.event
async def on_message(message: discord.Message):
    ctx = await client.get_context(message)
    
    # redchanit funny REVIVAL
    if message.channel.id == 1056351978982211634: # announcements of redchanit
       await message.add_reaction("<:emesisgreen:1085453263454863480>")

    if message.author.bot: # don't let bots talk to each other
        return
    
    if isinstance(message.channel, discord.DMChannel):
        return
    
    if client.user in message.mentions: # if bot was mentioned, run ask command
        await ask(ctx, question=message.content.replace(f'<@{client.user.id}>', '').strip())
        return
    
    if am_i_whitelisted(ctx):
        await ask(ctx, question=message.content)
    
    await client.process_commands(message) # without this, commands stop running.

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"Invalid command used. `Trying to ask something? Use {PREFIX}ask! Want a list of commands? Use {PREFIX}help!`")
    else:
        await ctx.send(f"Son of a bitch...\n```\nAn error occurred:\n{str(error)}\n```")

@client.event
async def on_ready():
  await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name='big beautiful women'))
  print("connected")

client.run(os.environ['DISCORD_TOKEN'])

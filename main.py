import discord
from discord.ext import commands
import os
import asyncio

# 1. SETUP INTENTS (Crucial: This lets the bot actually read your messages)
intents = discord.Intents.default()
intents.message_content = True 

bot = commands.Bot(command_prefix=",", self_bot=True, help_command=None, intents=intents)

# Database for the snipe command
deleted_messages = {}
STREAM_URL = "https://www.twitch.tv/twitch"

@bot.event
async def on_ready():
    print(f"--- SBO ONLINE: {bot.user.name} ---")
    print("Commands should now be responsive.")

@bot.event
async def on_message(message):
    # This is the FIX: It allows commands to work alongside on_message
    await bot.process_commands(message)

@bot.event
async def on_message_delete(message):
    if message.author.bot:
        return
    deleted_messages[message.channel.id] = {
        'content': message.content,
        'author': str(message.author),
        'mention': message.author.mention
    }

# --- HELP COMMAND ---

@bot.command()
async def help(ctx):
    help_text = (
        "**SBO SELF-BOT COMMANDS**\n\n"
        "**RPC Status:**\n"
        "`,playing <text>`\n"
        "`,streaming <text>`\n"
        "`,listen <text>`\n"
        "`,watching <text>`\n\n"
        "**Utilities:**\n"
        "`,snipe` - Get last deleted msg\n"
        "`,snipe <mode> <@user>` - DM Modes (1=All, 2=Open, 3=Target)"
    )
    await ctx.message.edit(content=help_text)

# --- RPC COMMANDS ---

@bot.command()
async def listen(ctx, *, text=None):
    if not text:
        return await ctx.message.edit(content="⚠️ **Correction:** Use `,listen <song>`", delete_after=5)
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=text))
    await ctx.message.edit(content=f"🎧 Listening to: **{text}**", delete_after=2)

@bot.command()
async def streaming(ctx, *, text=None):
    if not text:
        return await ctx.message.edit(content="⚠️ **Correction:** Use `,streaming <title>`", delete_after=5)
    await bot.change_presence(activity=discord.Streaming(name=text, url=STREAM_URL))
    await ctx.message.edit(content=f"💜 Streaming: **{text}**", delete_after=2)

# --- SNIPE COMMAND ---

@bot.command()
async def snipe(ctx, mode: int = None, user: discord.User = None):
    # Correction for missing user in DM modes
    if mode is not None and user is None:
        return await ctx.message.edit(content="⚠️ **Correction:** Use `,snipe <mode> {@user}`", delete_after=5)

    if mode and user:
        await ctx.message.edit(content=f"✅ Mode {mode} triggered for {user.name}", delete_after=2)
        await user.send(f"Targeted via Mode {mode}")
    else:
        msg = deleted_messages.get(ctx.channel.id)
        if msg:
            await ctx.message.edit(content=f"**{msg['author']}** said: {msg['content']}")
        else:
            await ctx.message.edit(content="❌ Nothing to snipe.", delete_after=2)

# RUN LOGIC
token = os.getenv("DISCORD_TOKEN")
if token:
    bot.run(token)
else:
    print("Error: DISCORD_TOKEN not found in environment.")

import discord
from discord.ext import commands
import os
import asyncio

# Setup bot with prefix ',' and self_bot enabled
bot = commands.Bot(command_prefix=",", self_bot=True, help_command=None)

# Store for the ,snipe command
deleted_messages = {}

# Generic link to satisfy Discord's RPC requirement for the purple icon
STREAM_URL = "https://www.twitch.tv/twitch"

@bot.event
async def on_ready():
    print(f"--- SBO ONLINE: {bot.user.name} ---")
    print("Using Token Variable: DISCORD_TOKEN")

@bot.event
async def on_message_delete(message):
    # Log the last deleted message per channel
    if message.author.bot:
        return
    deleted_messages[message.channel.id] = {
        'content': message.content,
        'author': str(message.author),
        'mention': message.author.mention
    }

# --- RPC COMMANDS ---

@bot.command()
async def listen(ctx, *, text):
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=text))
    await ctx.message.edit(content=f"🎧 Listening to: **{text}**", delete_after=2)

@bot.command()
async def playing(ctx, *, text):
    await bot.change_presence(activity=discord.Game(name=text))
    await ctx.message.edit(content=f"🎮 Playing: **{text}**", delete_after=2)

@bot.command()
async def streaming(ctx, *, text):
    await bot.change_presence(activity=discord.Streaming(name=text, url=STREAM_URL))
    await ctx.message.edit(content=f"💜 Streaming: **{text}**", delete_after=2)

@bot.command()
async def watching(ctx, *, text):
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=text))
    await ctx.message.edit(content=f"👀 Watching: **{text}**", delete_after=2)

# --- SNIPE & DM MODES ---

@bot.command()
async def snipe(ctx, mode: int = None, user: discord.User = None):
    # Logic: ,snipe <1, 2, 3> {user.mention}
    if mode is not None and user is not None:
        # Mode 1: All | Mode 2: Open DMs | Mode 3: Specific
        if mode == 1:
            await ctx.message.edit(content=f"🚀 Sending All-Mode DM to {user.mention}...")
            await user.send("Mass DM Mode 1 triggered.")
        elif mode == 2:
            await ctx.message.edit(content=f"📂 Sending Open-DM Mode to {user.mention}...")
            await user.send("Mode 2 DM.")
        elif mode == 3:
            await ctx.message.edit(content=f"🎯 Target Snipe: {user.mention}")
            await user.send("Mode 3 DM.")
    
    # Standard Snipe: ,snipe (shows last deleted message in channel)
    else:
        msg = deleted_messages.get(ctx.channel.id)
        if msg:
            await ctx.message.edit(content=f"**{msg['author']}** said: {msg['content']}")
        else:
            await ctx.message.edit(content="❌ Nothing to snipe.", delete_after=2)

# Running the bot using the environment variable
token = os.getenv("DISCORD_TOKEN")
if token:
    bot.run(token)
else:
    print("Error: DISCORD_TOKEN variable not found in environment.")

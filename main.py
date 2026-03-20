import discord
from discord.ext import commands
import os
import asyncio

# Setup bot with prefix ',' and self_bot enabled
bot = commands.Bot(command_prefix=",", self_bot=True, help_command=None)

# Store for the ,snipe command
deleted_messages = {}
STREAM_URL = "https://www.twitch.tv/twitch"

@bot.event
async def on_ready():
    print(f"--- SBO ONLINE: {bot.user.name} ---")

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
        "`,playing <text>` - Set Game Status\n"
        "`,streaming <text>` - Set Streaming Status (Purple)\n"
        "`,listen <text>` - Set Listening Status\n"
        "`,watching <text>` - Set Watching Status\n\n"
        "**Utilities:**\n"
        "`,snipe` - Recover last deleted message in channel\n"
        "`,snipe <mode> <@user>` - Targeted DM Modes\n"
        "   `1` = All | `2` = Open DMs | `3` = Target Only"
    )
    await ctx.message.edit(content=help_text)

# --- RPC COMMANDS ---

@bot.command()
async def listen(ctx, *, text=None):
    if not text:
        return await ctx.message.edit(content="⚠️ **Correction:** Use `,listen <song/text>`", delete_after=5)
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=text))
    await ctx.message.edit(content=f"🎧 Listening to: **{text}**", delete_after=2)

@bot.command()
async def playing(ctx, *, text=None):
    if not text:
        return await ctx.message.edit(content="⚠️ **Correction:** Use `,playing <game>`", delete_after=5)
    await bot.change_presence(activity=discord.Game(name=text))
    await ctx.message.edit(content=f"🎮 Playing: **{text}**", delete_after=2)

@bot.command()
async def streaming(ctx, *, text=None):
    if not text:
        return await ctx.message.edit(content="⚠️ **Correction:** Use `,streaming <title>`", delete_after=5)
    await bot.change_presence(activity=discord.Streaming(name=text, url=STREAM_URL))
    await ctx.message.edit(content=f"💜 Streaming: **{text}**", delete_after=2)

@bot.command()
async def watching(ctx, *, text=None):
    if not text:
        return await ctx.message.edit(content="⚠️ **Correction:** Use `,watching <show/movie>`", delete_after=5)
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=text))
    await ctx.message.edit(content=f"👀 Watching: **{text}**", delete_after=2)

# --- SNIPE & DM MODES ---

@bot.command()
async def snipe(ctx, mode: int = None, user: discord.User = None):
    # If mode is provided but user is missing, provide correction
    if mode is not None and user is None:
        return await ctx.message.edit(content="⚠️ **Correction:** Proper usage: `,snipe <1, 2, or 3> {@user}`", delete_after=5)

    # Targeted DM Logic
    if mode is not None and user is not None:
        if mode == 1:
            await ctx.message.edit(content=f"🚀 [Mode 1] Sending to All: {user.mention}")
            await user.send("Mass DM Mode 1")
        elif mode == 2:
            await ctx.message.edit(content=f"📂 [Mode 2] Sending to Open DMs: {user.mention}")
            await user.send("Mode 2 DM")
        elif mode == 3:
            await ctx.message.edit(content=f"🎯 [Mode 3] Targeted: {user.mention}")
            await user.send("Mode 3 DM")
    
    # Standard Snipe
    else:
        msg = deleted_messages.get(ctx.channel.id)
        if msg:
            await ctx.message.edit(content=f"**{msg['author']}** said: {msg['content']}")
        else:
            await ctx.message.edit(content="❌ Nothing to snipe.", delete_after=2)

# Run logic
token = os.getenv("DISCORD_TOKEN")
if token:
    bot.run(token)
else:
    print("Error: DISCORD_TOKEN variable not found in environment.")

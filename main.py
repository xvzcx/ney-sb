import discord
import asyncio
import os
import time
import random
from discord.ext import commands
from flask import Flask
from threading import Thread

# ─── KEEPALIVE (For 24/7 Hosting) ───
app = Flask(__name__)
@app.route('/')
def home(): return "SYSTEM ONLINE"
def run_flask(): app.run(host='0.0.0.0', port=8080)

# ─── BOT SETUP ───
# Removed Intents to fix the 'severity: error' crash
bot = commands.Bot(command_prefix=",", self_bot=True, help_command=None)

# Global Registries
bot.deleted_messages = {}
bot.current_rpc = None
STREAM_URL = "https://www.twitch.tv/twitch"

# ─── NEAT UI ENGINE ───
def ui_box(title, body, color="36"):
    # colors: 31=Red, 32=Green, 33=Yellow, 34=Blue, 35=Magenta, 36=Cyan, 37=White
    width = 32
    res = f"```ansi\n"
    res += f"[1;{color}m┎{'─'*(width-2)}┒[0m\n"
    res += f"[1;{color}m┃[0m [1;37m{title.center(width-4)}[0m [1;{color}m┃[0m\n"
    res += f"[1;{color}m┠{'─'*(width-2)}┨[0m\n"
    for line in body.split("\n"):
        res += f"[1;{color}m┃[0m {line.ljust(width-4)} [1;{color}m┃[0m\n"
    res += f"[1;{color}m┖{'─'*(width-2)}⚚[0m\n" # Custom bottom corner
    res += "```"
    return res

@bot.event
async def on_ready():
    print(f"─── {bot.user} v1.0 | SBO ENGINE ONLINE ───")
    print("Using Token: DISCORD_TOKEN")

@bot.event
async def on_message(message):
    # This allows commands to function
    await bot.process_commands(message)

@bot.event
async def on_message_delete(message):
    if message.author.bot: return
    # Store the last deleted message for ,snipe
    bot.deleted_messages[message.channel.id] = {
        'content': message.content,
        'author': str(message.author)
    }

# ─── RPC COMMANDS ───

@bot.command()
async def rpc(ctx, mode=None, *, text=None):
    await ctx.message.delete()
    if not mode or not text:
        body = "[1;31mUsage:[0m\n,rpc [play|listen|watch] [txt]"
        return await ctx.send(ui_box("Correction", body, "31"), delete_after=5)
    
    m = mode.lower()
    if m == "play": act = discord.Game(name=text)
    elif m == "listen": act = discord.Activity(type=discord.ActivityType.listening, name=text)
    elif m == "watch": act = discord.Activity(type=discord.ActivityType.watching, name=text)
    else: return

    bot.current_rpc = act
    await bot.change_presence(activity=act)
    await ctx.send(ui_box("Presence", f"[1;36m{m.upper()}ING[0m\n{text}", "36"), delete_after=3)

@bot.command()
async def streaming(ctx, *, text=None):
    await ctx.message.delete()
    if not text:
        return await ctx.send(ui_box("Correction", "Use: ,streaming [txt]", "31"), delete_after=5)
    
    act = discord.Streaming(name=text, url=STREAM_URL)
    bot.current_rpc = act
    await bot.change_presence(activity=act)
    await ctx.send(ui_box("Stream", f"Live: {text}", "35"), delete_after=3)

# ─── SNIPE & MDM COMMANDS ───

@bot.command()
async def snipe(ctx, mode: int = None, user: discord.User = None):
    # Targeted DM Modes (,snipe <1,2,3> @user)
    if mode is not None:
        await ctx.message.delete()
        if not user:
            body = "[1;31mCorrection:[0m\n,snipe [1|2|3] [@user]"
            return await ctx.send(ui_box("Error", body, "31"), delete_after=5)
        
        # Mode Logic
        await user.send(f"**[SBO Mode {mode}]** Target Sniped.")
        await ctx.send(ui_box("Snipe", f"Mode {mode} -> {user.name}", "32"), delete_after=3)

    # Standard Snipe (,snipe)
    else:
        await ctx.message.delete()
        data = bot.deleted_messages.get(ctx.channel.id)
        if data:
            body = f"[1;34m{data['author']}[0m\n{data['content']}"
            await ctx.send(ui_box("Last Deleted", body, "34"))
        else:
            await ctx.send(ui_box("Snipe", "Nothing found.", "31"), delete_after=3)

@bot.command()
async def mdm(ctx, *, message: str = None):
    await ctx.message.delete()
    if not message:
        return await ctx.send(ui_box("Correction", "Use: ,mdm [message]", "31"), delete_after=5)
    
    # Gather all unique users from your guilds
    targets = [m for g in bot.guilds for m in g.members if not m.bot and m.id != bot.user.id]
    random.shuffle(targets)
    
    await ctx.send(ui_box("MDM", f"Blasting {len(targets)} users...", "33"), delete_after=5)
    
    for member in targets:
        try:
            # Replace <user> with their display name if it's in the text
            await member.send(message.replace("<user>", member.display_name))
            await asyncio.sleep(random.uniform(3.5, 5.0)) # Jitter delay to stay safe
        except: 
            continue

# ─── HELP COMMAND ───

@bot.command()
async def help(ctx):
    await ctx.message.delete()
    body = "[1;36m,rpc [mode] [text][0m\n[1;35m,streaming [text][0m\n[1;34m,snipe[0m\n[1;32m,snipe [1-3] [@user][0m\n[1;33m,mdm [text][0m"
    await ctx.send(ui_box("SBO Help", body, "37"), delete_after=20)

# ─── RUN ENGINE ───
if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN")
    if TOKEN:
        # Start keep-alive for hosting
        Thread(target=run_flask, daemon=True).start()
        try:
            bot.run(TOKEN)
        except Exception as e:
            print(f"FAILED TO START: {e}")
    else:
        print("!!! ERROR: Set 'DISCORD_TOKEN' in your environment variables !!!")

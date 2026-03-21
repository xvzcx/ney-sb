import discord
import asyncio
import os
import time
import random
from discord.ext import commands
from flask import Flask
from threading import Thread

# ─── RAILWAY KEEPALIVE ───
app = Flask(__name__)
@app.route('/')
def home(): return "SBO SYSTEM ONLINE"

def run_flask():
    # Railway provides the PORT variable automatically
    port = int(os.getenv("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# ─── BOT SETUP ───
# No intents for self-bot to prevent library crashes
bot = commands.Bot(command_prefix=",", self_bot=True, help_command=None)

bot.deleted_messages = {}
bot.current_rpc = None
STREAM_URL = "https://www.twitch.tv/twitch"

# ─── NEAT UI ENGINE ───
def ui_box(title, body, color="36"):
    width = 32
    res = f"```ansi\n"
    res += f"[1;{color}m┎{'─'*(width-2)}┒[0m\n"
    res += f"[1;{color}m┃[0m [1;37m{title.center(width-4)}[0m [1;{color}m┃[0m\n"
    res += f"[1;{color}m┠{'─'*(width-2)}┨[0m\n"
    for line in body.split("\n"):
        res += f"[1;{color}m┃[0m {line.ljust(width-4)} [1;{color}m┃[0m\n"
    res += f"[1;{color}m┖{'─'*(width-2)}┚[0m\n"
    res += "```"
    return res

@bot.event
async def on_ready():
    print(f"─── {bot.user} | RAILWAY DEPLOYMENT SUCCESS ───")

@bot.event
async def on_message(message):
    await bot.process_commands(message)

@bot.event
async def on_message_delete(message):
    if message.author.bot: return
    bot.deleted_messages[message.channel.id] = {
        'content': message.content,
        'author': str(message.author)
    }

# ─── RPC COMMANDS ───

@bot.command()
async def rpc(ctx, mode=None, *, text=None):
    await ctx.message.delete()
    if not mode or not text:
        return await ctx.send(ui_box("Error", "Usage: ,rpc [play|listen|watch] [txt]", "31"), delete_after=5)
    
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
        return await ctx.send(ui_box("Error", "Usage: ,streaming [txt]", "31"), delete_after=5)
    
    act = discord.Streaming(name=text, url=STREAM_URL)
    bot.current_rpc = act
    await bot.change_presence(activity=act)
    await ctx.send(ui_box("Stream", f"Live: {text}", "35"), delete_after=3)

# ─── SNIPE & MDM COMMANDS ───

@bot.command()
async def snipe(ctx, mode: int = None, user: discord.User = None):
    await ctx.message.delete()
    if mode is not None:
        if not user:
            return await ctx.send(ui_box("Error", "Usage: ,snipe [1|2|3] [@u]", "31"), delete_after=5)
        await user.send(f"**[SBO Mode {mode}]** Status Check.")
        await ctx.send(ui_box("Snipe", f"Mode {mode} -> {user.name}", "32"), delete_after=3)
    else:
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
        return await ctx.send(ui_box("Error", "Usage: ,mdm [txt]", "31"), delete_after=5)
    
    targets = [m for g in bot.guilds for m in g.members if not m.bot and m.id != bot.user.id]
    random.shuffle(targets)
    
    await ctx.send(ui_box("MDM", f"Blasting {len(targets)} users...", "33"), delete_after=5)
    for member in targets:
        try:
            await member.send(message.replace("<user>", member.display_name))
            await asyncio.sleep(random.uniform(3.5, 6.0))
        except: continue

@bot.command()
async def help(ctx):
    await ctx.message.delete()
    body = "[1;36m,rpc [mode] [txt][0m\n[1;35m,streaming [txt][0m\n[1;34m,snipe[0m\n[1;32m,snipe [1-3] [@u][0m\n[1;33m,mdm [txt][0m"
    await ctx.send(ui_box("SBO Help", body, "37"), delete_after=20)

# ─── EXECUTION ───
if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN")
    if TOKEN:
        # Start the Flask thread for Railway's health check
        Thread(target=run_flask, daemon=True).start()
        bot.run(TOKEN)
    else:
        print("CRITICAL: DISCORD_TOKEN not found in Railway Variables.")

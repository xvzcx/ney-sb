import discord
import asyncio
import os
import random
import time
from discord.ext import commands
from flask import Flask
from threading import Thread

# ─── RAILWAY KEEPALIVE ───
# Railway requires a web server to pass health checks and stay online.
app = Flask(__name__)

@app.route('/')
def home():
    return "SBO SYSTEM ONLINE"

def run_flask():
    # Railway automatically assigns a PORT environment variable.
    port = int(os.getenv("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# ─── BOT SETUP ───
# Using Intents.all() to ensure the bot can see message content and deletions.
intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix=",", 
    self_bot=True, 
    help_command=None, 
    intents=intents
)

# Global Storage
bot.deleted_messages = {}
STREAM_URL = "https://www.twitch.tv/twitch"

# ─── UI ENGINE ───
def ui_box(title, body, color="36"):
    # ANSI color codes: 31=Red, 32=Green, 33=Yellow, 34=Blue, 35=Magenta, 36=Cyan, 37=White
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
    print(f"─── LOGIN SUCCESS: {bot.user} ───")
    print("Railway Health Check: http://0.0.0.0:8080")

@bot.event
async def on_message(message):
    # Only listen to your own commands
    if message.author.id != bot.user.id:
        return
    
    # Process commands attached to the bot
    await bot.process_commands(message)

@bot.event
async def on_message_delete(message):
    # Log deleted messages for the ,snipe command
    if message.author.bot:
        return
    bot.deleted_messages[message.channel.id] = {
        'content': message.content,
        'author': str(message.author),
        'time': time.strftime("%H:%M:%S", time.localtime())
    }

# ─── COMMANDS ───

@bot.command()
async def ping(ctx):
    await ctx.message.delete()
    await ctx.send(ui_box("System", "[1;32mPong![0m Bot is responsive.", "32"), delete_after=3)

@bot.command()
async def help(ctx):
    await ctx.message.delete()
    body = (
        "[1;36m,rpc [mode] [txt][0m\n"
        "[1;35m,streaming [txt][0m\n"
        "[1;34m,snipe[0m\n"
        "[1;32m,snipe [1-3] [@u][0m\n"
        "[1;33m,mdm [text][0m\n"
        "[1;37m,ping[0m"
    )
    await ctx.send(ui_box("SBO Help", body, "37"), delete_after=30)

@bot.command()
async def rpc(ctx, mode=None, *, text=None):
    await ctx.message.delete()
    if not mode or not text:
        body = "[1;31mCorrection:[0m\nUse ,rpc [play|listen|watch] [txt]"
        return await ctx.send(ui_box("Error", body, "31"), delete_after=5)
    
    m = mode.lower()
    try:
        if m == "play": 
            act = discord.Game(name=text)
        elif m == "listen": 
            act = discord.Activity(type=discord.ActivityType.listening, name=text)
        elif m == "watch": 
            act = discord.Activity(type=discord.ActivityType.watching, name=text)
        else:
            return
        
        await bot.change_presence(activity=act)
        await ctx.send(ui_box("Presence", f"[1;36m{m.upper()}ING[0m\n{text}", "36"), delete_after=3)
    except Exception as e:
        await ctx.send(f"Error: {e}", delete_after=3)

@bot.command()
async def streaming(ctx, *, text=None):
    await ctx.message.delete()
    if not text:
        body = "[1;31mCorrection:[0m\nUse ,streaming [text]"
        return await ctx.send(ui_box("Error", body, "31"), delete_after=5)
    
    act = discord.Streaming(name=text, url=STREAM_URL)
    await bot.change_presence(activity=act)
    await ctx.send(ui_box("Stream", f"Live: {text}", "35"), delete_after=3)

@bot.command()
async def snipe(ctx, mode: int = None, user: discord.User = None):
    await ctx.message.delete()
    
    # Targeted Snipe DM Logic
    if mode is not None:
        if not user:
            body = "[1;31mCorrection:[0m\nUse ,snipe [1|2|3] [@user]"
            return await ctx.send(ui_box("Error", body, "31"), delete_after=5)
        
        try:
            await user.send(f"**[SBO Snipe Mode {mode}]** Target: {user.name}")
            await ctx.send(ui_box("Snipe", f"Mode {mode} -> {user.name}", "32"), delete_after=3)
        except:
            await ctx.send(ui_box("Snipe", "[1;31mFailed to DM user.[0m", "31"), delete_after=3)
            
    # Regular Snipe Logic
    else:
        data = bot.deleted_messages.get(ctx.channel.id)
        if data:
            body = f"[1;34m{data['author']}[0m [1;30m({data['time']})[0m\n{data['content']}"
            await ctx.send(ui_box("Last Deleted", body, "34"))
        else:
            await ctx.send(ui_box("Snipe", "Nothing to recover.", "31"), delete_after=3)

@bot.command()
async def mdm(ctx, *, message: str = None):
    await ctx.message.delete()
    if not message:
        body = "[1;31mCorrection:[0m\nUse ,mdm [text]"
        return await ctx.send(ui_box("Error", body, "31"), delete_after=5)
    
    # Filter unique users from all servers
    targets = [m for g in bot.guilds for m in g.members if not m.bot and m.id != bot.user.id]
    random.shuffle(targets)
    
    await ctx.send(ui_box("MDM", f"Blasting {len(targets)} users...", "33"), delete_after=5)
    
    for member in targets:
        try:
            # Customizing message with <user> tag
            final_msg = message.replace("<user>", member.display_name)
            await member.send(final_msg)
            # Randomized delay to prevent rate-limiting/detection
            await asyncio.sleep(random.uniform(3.8, 5.5))
        except:
            continue

# ─── RUN ENGINE ───
if __name__ == "__main__":
    t = os.getenv("DISCORD_TOKEN")
    if t:
        # Strip whitespace/quotes from the token to prevent login errors
        token = t.strip().strip('"').strip("'")
        
        # Start the web thread for Railway
        Thread(target=run_flask, daemon=True).start()
        
        try:
            bot.run(token)
        except Exception as e:
            print(f"CRITICAL ERROR ON LOGIN: {e}")
    else:
        print("CRITICAL: DISCORD_TOKEN is not set in Environment

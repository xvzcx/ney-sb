import discord
import asyncio
import os
from discord.ext import commands
from flask import Flask
from threading import Thread

# ─── RAILWAY KEEPALIVE ───
app = Flask(__name__)
@app.route('/')
def home(): return "SBO SYSTEM ONLINE"

def run_flask():
    port = int(os.getenv("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# ─── BOT SETUP ───
# We add ALL intents here to ensure the bot can see your messages
intents = discord.Intents.all() 

bot = commands.Bot(
    command_prefix=",", 
    self_bot=True, 
    help_command=None, 
    intents=intents,
    case_insensitive=True # Makes ,RPC and ,rpc both work
)

bot.deleted_messages = {}
STREAM_URL = "https://www.twitch.tv/twitch"

# ─── UI ENGINE ───
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
    print(f"─── {bot.user} | COMMANDS ACTIVE ───")

@bot.event
async def on_message(message):
    # CRITICAL: This allows the bot to process commands
    await bot.process_commands(message)

@bot.event
async def on_message_delete(message):
    if message.author.bot: return
    bot.deleted_messages[message.channel.id] = {
        'content': message.content,
        'author': str(message.author)
    }

# --- SNIPE COMMAND (RE-LOGGED) ---
@bot.command()
async def snipe(ctx, mode: int = None, user: discord.User = None):
    await ctx.message.delete()
    if mode is not None:
        if not user:
            return await ctx.send(ui_box("Error", "Usage: ,snipe [1|2|3] [@u]", "31"), delete_after=5)
        await user.send(f"**[SBO Mode {mode}]** Target: {user.name}")
        await ctx.send(ui_box("Snipe", f"Mode {mode} -> {user.name}", "32"), delete_after=3)
    else:
        data = bot.deleted_messages.get(ctx.channel.id)
        if data:
            body = f"[1;34m{data['author']}[0m\n{data['content']}"
            await ctx.send(ui_box("Last Deleted", body, "34"))
        else:
            await ctx.send(ui_box("Snipe", "Nothing found.", "31"), delete_after=3)

# (Other commands like rpc, mdm, help should be placed here as before)

if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN")
    if TOKEN:
        Thread(target=run_flask, daemon=True).start()
        bot.run(TOKEN)
    else:
        print("CRITICAL: DISCORD_TOKEN MISSING")

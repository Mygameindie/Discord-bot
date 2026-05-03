import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
from google import genai

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
BOT_PREFIX = os.getenv("BOT_PREFIX", "!")

if not DISCORD_TOKEN:
    raise ValueError("Missing DISCORD_TOKEN in .env")

if not GEMINI_API_KEY:
    raise ValueError("Missing GEMINI_API_KEY in .env")

gemini_client = genai.Client(api_key=GEMINI_API_KEY)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents)


def split_discord_message(text: str, limit: int = 2000):
    """Split long Gemini replies so Discord can send them."""
    if not text:
        return ["No response from Gemini."]

    chunks = []
    while len(text) > limit:
        split_at = text.rfind("\n", 0, limit)
        if split_at == -1:
            split_at = limit
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip()

    chunks.append(text)
    return chunks


async def ask_gemini(prompt: str) -> str:
    """Run the Gemini request outside the Discord event loop."""
    response = await asyncio.to_thread(
        gemini_client.models.generate_content,
        model=GEMINI_MODEL,
        contents=prompt,
    )
    return response.text or "No response from Gemini."


@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")
    print(f"Command prefix: {BOT_PREFIX}")
    print(f"Gemini model: {GEMINI_MODEL}")


@bot.command(name="ask")
async def ask(ctx: commands.Context, *, question: str):
    async with ctx.typing():
        try:
            answer = await ask_gemini(question)

            for chunk in split_discord_message(answer):
                await ctx.reply(chunk)

        except Exception as error:
            await ctx.reply(f"Error: `{error}`")


@bot.command(name="ping")
async def ping(ctx: commands.Context):
    await ctx.reply("Pong! Gemini Discord bot is working.")


bot.run(DISCORD_TOKEN)

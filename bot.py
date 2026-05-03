import os
import asyncio
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from google import genai
from keep_alive import start_keep_alive_server

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")


def get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing {name} in environment variables")
    return value


DISCORD_TOKEN = get_required_env("DISCORD_TOKEN")
GEMINI_API_KEY = get_required_env("GEMINI_API_KEY")

gemini_client = genai.Client(api_key=GEMINI_API_KEY)

# Slash commands do not need Message Content Intent.
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


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
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands")
    except Exception as error:
        print(f"Failed to sync slash commands: {error}")

    print(f"Bot is online as {bot.user}")
    print(f"Gemini model: {GEMINI_MODEL}")


@bot.tree.command(name="ping", description="Check if the bot is online")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong! Gemini Discord bot is working.")


@bot.tree.command(name="ask", description="Ask Gemini a question")
@app_commands.describe(question="Your question for Gemini")
async def ask(interaction: discord.Interaction, question: str):
    await interaction.response.defer(thinking=True)

    try:
        answer = await ask_gemini(question)
        chunks = split_discord_message(answer)

        await interaction.followup.send(chunks[0])
        for chunk in chunks[1:]:
            await interaction.channel.send(chunk)

    except Exception as error:
        await interaction.followup.send(f"Error: `{error}`")


async def main():
    await start_keep_alive_server()
    await bot.start(DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())

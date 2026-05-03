import os
import asyncio

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from groq import Groq

from keep_alive import start_keep_alive_server

load_dotenv()

GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")


def get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing {name} in environment variables")
    return value


DISCORD_TOKEN = get_required_env("DISCORD_TOKEN")
GROQ_API_KEY = get_required_env("GROQ_API_KEY")

groq_client = Groq(api_key=GROQ_API_KEY)

# Slash commands do not need Message Content Intent.
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


def split_discord_message(text: str, limit: int = 2000):
    """Split long Groq replies so Discord can send them."""
    if not text:
        return ["No response from Groq."]

    chunks = []
    while len(text) > limit:
        split_at = text.rfind("\n", 0, limit)
        if split_at == -1:
            split_at = limit
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip()

    chunks.append(text)
    return chunks


def ask_groq_sync(prompt: str) -> str:
    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful Discord bot. Keep replies concise and friendly.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.7,
        max_tokens=1000,
    )
    return response.choices[0].message.content or "No response from Groq."


async def ask_groq(prompt: str) -> str:
    """Run the Groq request outside the Discord event loop."""
    return await asyncio.to_thread(ask_groq_sync, prompt)


@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands")
    except Exception as error:
        print(f"Failed to sync slash commands: {error}")

    print(f"Bot is online as {bot.user}")
    print(f"Groq model: {GROQ_MODEL}")


@bot.tree.command(name="ping", description="Check if the bot is online")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong! Groq Discord bot is working.")


@bot.tree.command(name="ask", description="Ask Groq a question")
@app_commands.describe(question="Your question for Groq")
async def ask(interaction: discord.Interaction, question: str):
    await interaction.response.defer(thinking=True)

    try:
        answer = await ask_groq(question)
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

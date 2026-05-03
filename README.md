# Gemini Discord Bot

A simple Discord bot that uses the Gemini API.

## Features

- `!ask <question>` asks Gemini a question
- `!ping` checks if the bot is online
- Supports long Gemini responses by splitting messages for Discord
- Uses `.env` so your API keys are not uploaded to GitHub

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/Mygameindie/Discord-bot.git
cd Discord-bot
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create your `.env` file

Copy the example file:

```bash
cp .env.example .env
```

Then edit `.env`:

```env
DISCORD_TOKEN=your_discord_bot_token_here
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash
BOT_PREFIX=!
```

Do not upload your real `.env` file to GitHub.

### 4. Enable Discord Message Content Intent

In the Discord Developer Portal:

1. Open your application
2. Go to **Bot**
3. Enable **Message Content Intent**
4. Save changes

### 5. Run the bot

```bash
python bot.py
```

## Discord commands

```text
!ping
!ask explain gravity simply
```

## Notes

If `gemini-1.5-flash` does not work for your API key, change `GEMINI_MODEL` in `.env` to another Gemini model available to your account.

# Furniture Finder Telegram Bot

Telegram bot that accepts a furniture or interior photo, asks for delivery city and budget, analyzes the item with OpenAI, and returns similar eBay listings.

## Local Checks

Use a virtual environment. On this Mac, prefer `/usr/local/bin/python3` because the Anaconda Python currently crashes on `import readline`, which also crashes pytest startup.

```bash
/usr/local/bin/python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest -v
```

## Required Environment Variables

Copy `.env.example` to `.env` for local experiments. In Render, add the same values in Environment Variables.

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_WEBHOOK_SECRET`
- `PUBLIC_BASE_URL`
- `OPENAI_API_KEY`
- `EBAY_CLIENT_ID`
- `EBAY_CLIENT_SECRET`
- `EBAY_MARKETPLACE_ID`
- `DELIVERY_COUNTRY`
- `MAX_RESULTS`

## Deployment

Recommended no-card path: [Deploy On PythonAnywhere Free](PYTHONANYWHERE.md).

Render is also supported if your account accepts a payment method.

## Render Deployment

1. Push this folder to GitHub.
2. Create a Render Web Service from the repository.
3. Use Python environment.
4. Build command: `pip install -e .`
5. Start command: `uvicorn app.web:app --host 0.0.0.0 --port $PORT`
6. Add all required environment variables.
7. Set `PUBLIC_BASE_URL` to the Render service URL, for example `https://furniture-finder-bot.onrender.com`.
8. Deploy. On startup, the app registers the Telegram webhook automatically.

## How The Bot Works

1. User sends `/start`.
2. Bot asks for a furniture or interior photo.
3. Bot asks for delivery city.
4. Bot asks for budget in USD.
5. Bot analyzes the image with OpenAI and builds an English eBay search query.
6. Bot searches eBay Browse API with budget and country-level delivery filters.
7. Bot returns up to `MAX_RESULTS` matching listings.

## Security

Do not commit real tokens or secrets. If a secret was pasted into chat or logs, rotate it in the provider dashboard and update Render.

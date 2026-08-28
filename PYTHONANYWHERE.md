# Deploy On PythonAnywhere Free

This guide deploys the bot as a FastAPI ASGI app on PythonAnywhere.

PythonAnywhere free accounts use an outbound internet allowlist. As of August 28, 2026, the required domains are listed on the free allowlist:

- `api.telegram.org`
- `api.openai.com`
- `api.ebay.com`

If a provider changes domains later, request an allowlist addition from PythonAnywhere.

## 1. Create A PythonAnywhere Account

Create or open a free account at:

```text
https://www.pythonanywhere.com/
```

Your public bot URL will be:

```text
https://YOUR_PYTHONANYWHERE_USERNAME.pythonanywhere.com
```

Use your real PythonAnywhere username wherever this guide says `YOUR_PYTHONANYWHERE_USERNAME`.

## 2. Open A Bash Console

In PythonAnywhere:

1. Go to **Consoles**.
2. Start a new **Bash** console.

## 3. Clone The GitHub Repository

```bash
cd ~
git clone https://github.com/baton-v1/furniture-finder-bot.git
cd furniture-finder-bot
```

If the folder already exists and you are updating it:

```bash
cd ~/furniture-finder-bot
git pull
```

## 4. Create Virtualenv And Install Dependencies

```bash
mkvirtualenv furniture-finder-bot --python=python3.11
pip install -e .
```

If `python3.11` is not available in your account, try:

```bash
mkvirtualenv furniture-finder-bot --python=python3.12
pip install -e .
```

## 5. Create `.env`

In the Bash console:

```bash
cd ~/furniture-finder-bot
cp .env.example .env
nano .env
```

Fill in real values:

```env
TELEGRAM_BOT_TOKEN=your-telegram-token
TELEGRAM_WEBHOOK_SECRET=make-a-long-random-secret
PUBLIC_BASE_URL=https://YOUR_PYTHONANYWHERE_USERNAME.pythonanywhere.com
OPENAI_API_KEY=your-openai-key
EBAY_CLIENT_ID=your-ebay-client-id
EBAY_CLIENT_SECRET=your-ebay-client-secret
EBAY_MARKETPLACE_ID=EBAY_US
DELIVERY_COUNTRY=US
MAX_RESULTS=5
```

Save in nano:

- Press `Ctrl+O`
- Press `Enter`
- Press `Ctrl+X`

## 6. Install PythonAnywhere CLI

```bash
pip install --upgrade pythonanywhere
```

Then create an API token:

1. Open **Account** in PythonAnywhere.
2. Open **API Token**.
3. Click to create/generate a token.

After the token is created, the `pa` command can manage your website from Bash.

## 7. Create The ASGI Website

Run this command after replacing `YOUR_PYTHONANYWHERE_USERNAME`:

```bash
pa website create \
  --domain YOUR_PYTHONANYWHERE_USERNAME.pythonanywhere.com \
  --command '/home/YOUR_PYTHONANYWHERE_USERNAME/.virtualenvs/furniture-finder-bot/bin/uvicorn --app-dir /home/YOUR_PYTHONANYWHERE_USERNAME/furniture-finder-bot --uds ${DOMAIN_SOCKET} app.web:app'
```

Wait a few seconds, then open:

```text
https://YOUR_PYTHONANYWHERE_USERNAME.pythonanywhere.com/health
```

Expected response:

```json
{"status":"ok"}
```

The app registers the Telegram webhook automatically when it starts.

## 8. Test In Telegram

1. Open your bot in Telegram.
2. Send `/start`.
3. Send a furniture or interior photo.
4. Enter a delivery city.
5. Enter a budget in USD, for example `500`.

## 9. Update After Code Changes

After pushing new code to GitHub:

```bash
cd ~/furniture-finder-bot
git pull
workon furniture-finder-bot
pip install -e .
pa website reload --domain YOUR_PYTHONANYWHERE_USERNAME.pythonanywhere.com
```

## Troubleshooting

Check website details:

```bash
pa website get --domain YOUR_PYTHONANYWHERE_USERNAME.pythonanywhere.com
```

Check logs in PythonAnywhere:

```text
/var/log/YOUR_PYTHONANYWHERE_USERNAME.pythonanywhere.com.error.log
/var/log/YOUR_PYTHONANYWHERE_USERNAME.pythonanywhere.com.server.log
/var/log/YOUR_PYTHONANYWHERE_USERNAME.pythonanywhere.com.access.log
```

If Telegram works but OpenAI or eBay fails, check the error log. If the error mentions outbound access or `403`, verify the target API domain is still on the PythonAnywhere allowlist.

## Security

Never commit `.env`.

Because the eBay client secret was pasted into chat earlier, rotate it in eBay Developers after the first successful deploy and update `.env` on PythonAnywhere.

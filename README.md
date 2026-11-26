# FinancialAgent

A Python desktop application and Telegram bot that use Gemini to analyze financial documents and generate reports in Turkish. The desktop application also saves reports locally.

## Run locally

Install the dependencies with `python3 -m pip install -r requirements.txt`. Set `GEMINI_API_KEY` in your shell and run `python3 app.py` for the desktop application. For the Telegram bot, also set `TELEGRAM_BOT_TOKEN` and run `python3 telegram_bot.py`.

The source code uses environment variables for credentials. Desktop analysis history stays in `Analiz_Gecmisi/` on your machine.

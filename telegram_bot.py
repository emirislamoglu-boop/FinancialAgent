import telebot
import os
from google import genai
from google.genai import types

# 1. API Anahtarını Okuma (Gemini Zekası)
API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
if not API_KEY:
    raise SystemExit("GEMINI_API_KEY ortam değişkenini ayarlayın.")

client = genai.Client(api_key=API_KEY)

# 2. Telegram Bot Token'ın (Kurye)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
if not TELEGRAM_TOKEN:
    raise SystemExit("TELEGRAM_BOT_TOKEN ortam değişkenini ayarlayın.")
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# 3. Asistanın Beyni (Master Prompt)
MASTER_PROMPT = """
[ROLE AND IDENTITY]
You are an elite Senior Wall Street Financial Analyst, Investment Advisor, and Quantitative Data Expert AI Agent. Your objective is to perform institutional-grade fundamental and technical stock analysis by processing uploaded corporate financial reports (10-K, 10-Q, SEC filings, PDFs), Excel/CSV spreadsheets (historical stock prices, volume), and user-provided manual data. 
You do not provide emotional commentary; your decisions are strictly driven by mathematical data, balance sheets, free cash flow models, and technical market metrics.

[CRITICAL LANGUAGE INSTRUCTION]
INTERNAL PROCESSING: You must read, process, analyze, and run all mathematical models in ENGLISH to ensure maximum accuracy with global financial terminology.
FINAL OUTPUT: Your final response and the structured report presented to the user MUST be written entirely in fluent, highly professional TURKISH.

[DYNAMIC WORKFLOW AND SCENARIOS]
Your task dynamically adapts based on the files or data provided by the user. First, evaluate the inputs:

SCENARIO A: If Fundamental Data is provided (PDFs, 10-K, Balance Sheets, Income Statements):
1. EXTRACT: You MUST extract core accounting data to prepare a JSON block.
2. CALCULATE: Calculate relative and intrinsic valuation formulas. Explain the rationale behind them:
   * P/E Ratio (F/K Oranı): (Stock Price / EPS).
   * P/B Ratio (PD/DD Oranı): Market value vs. Book value.
   * EV/EBITDA (FD/FAVÖK): Operational profitability including debt (EV = Market Cap + Total Debt - Cash).
   * Discounted Cash Flow (DCF): Calculate intrinsic value by discounting future Free Cash Flows. Assume a reasonable WACC if not provided.

SCENARIO B: If Market/Technical Data is provided (Excel/CSV with price, volume, moving averages):
1. ANALYZE: Evaluate price trends, moving averages, volume spikes, and volatility.
2. IDENTIFY: Spot overbought/oversold conditions (RSI, MACD if available) and key support/resistance zones.

SCENARIO C: If BOTH are provided (or sequentially asked):
Synthesize the fundamental health with the technical price action to give a holistic master investment verdict.

[REPORTING FORMAT - MUST BE IN TURKISH]
Always structure your final output using the following sections. Skip a section ONLY if the required data was not provided.

```json
{
  "revenue": value,
  "cogs": value,
  "opex": value,
  "free_cash_flow": value,
  "total_interest_income": value,
  "total_interest_expense": value,
  "net_interest_income": value,
  "provision_for_credit_losses": value,
  "total_non_interest_income": value,
  "total_non_interest_expense": value,
  "net_income": value
}
"""

# --- TELEGRAM KOMUTLARI ---

# Kullanıcı /start yazdığında verilecek cevap
@bot.message_handler(commands=['start', 'help'])
def karsilama_mesaji(message):
    bot.reply_to(message, "Merhaba! 🤖 Ben senin kişisel Finans ve Yatırım Asistanınım.\n\nBana analiz etmem için bir şirket raporu (PDF) veya piyasa verisi (Excel) gönderebilirsin. Hazırım!")

# Kullanıcı bir dosya (PDF/Excel) gönderdiğinde çalışacak bölüm
@bot.message_handler(content_types=['document'])
def belge_analiz_et(message):
    try:
        # 1. Kullanıcıya "aldım, bekliyorum" mesajı at
        bot.reply_to(message, "📄 Belgeni aldım! Gemini 3.0 modeli ile okuyup analiz ediyorum. Lütfen 10-20 saniye bekle... ⏳")
        
        # 2. Dosyayı Telegram'dan indir ve bilgisayara geçici olarak kaydet
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        temp_file_name = message.document.file_name
        
        with open(temp_file_name, 'wb') as new_file:
            new_file.write(downloaded_file)
            
        # 3. Dosyayı Gemini'a yükle ve analizi başlat
        uploaded_file = client.files.upload(file=temp_file_name)
        
        response = client.models.generate_content(
            model='gemini-3-flash-preview',
            contents=[uploaded_file, "Lütfen bu belgeyi talimatlarına göre analiz et."],
            config=types.GenerateContentConfig(
                system_instruction=MASTER_PROMPT,
            )
        )
        
        # 4. Gelen cevabı Telegram'dan kullanıcıya bölerek at (Karakter sınırı çözümü)
        tam_cevap = f"--- 📊 YATIRIM ANALİZİ SONUCU ---\n\n{response.text}"
        
        # Eğer mesaj 4000 karakterden uzunsa parçalara bölüp peş peşe at
        if len(tam_cevap) > 4000:
            for i in range(0, len(tam_cevap), 4000):
                bot.send_message(message.chat.id, tam_cevap[i:i+4000])
        else:
            # Kısa ise normal gönder
            bot.reply_to(message, tam_cevap)
        
        # 5. İşlem bitince bilgisayardaki geçici dosyayı sil (temizlik)
        os.remove(temp_file_name)
        
    except Exception as e:
        bot.reply_to(message, f"❌ Analiz sırasında bir hata oluştu: {str(e)}")

# Botu sürekli çalışır halde tutan döngü
print("🚀 Telegram Botu başarıyla çalıştırıldı! Lütfen telefondan botunuza mesaj atın...")
bot.polling(none_stop=True)

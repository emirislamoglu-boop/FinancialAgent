import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
from google import genai
from google.genai import types
import os
import sys
from datetime import datetime

# --- UI AYARLARI ---
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

# --- API BAŞLATMA ---
API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
if not API_KEY:
    raise SystemExit("GEMINI_API_KEY ortam değişkenini ayarlayın.")

client = genai.Client(api_key=API_KEY)

# 2. Asistanın Beyni (Master Prompt)
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


def analiz_et():
    # 1. Dosya Seçimi
    dosya_yolu = filedialog.askopenfilename(
        title="Analiz edilecek raporu (PDF/Excel) seçin",
        filetypes=(("PDF Dosyaları", "*.pdf"),
                   ("Excel Dosyaları", "*.xlsx *.csv"),
                   ("Tüm Dosyalar", "*.*"))
    )

    # DÜZELTME 1: return ifadesi if bloğunun içine alındı
    if not dosya_yolu:
        return

    # DÜZELTME 2: Aşağıdaki tüm kodlar analiz_et fonksiyonunun içine (sağa) kaydırıldı
    sonuc_ekrani.configure(state="normal")
    sonuc_ekrani.delete("1.0", "end")
    sonuc_ekrani.insert("end", f"Seçilen Belge: {os.path.basename(dosya_yolu)}\n")
    sonuc_ekrani.insert("end", "🚀 Yapay Zeka belgeyi inceliyor... Lütfen bekleyin.\n\n")
    sonuc_ekrani.configure(state="disabled")
    
    # Arayüzün donmaması için harika bir ekleme
    pencere.update() 

    try:
        # Gemini API Dosya Yükleme ve Analiz (Yeni SDK yapısına uygun)
        uploaded_file = client.files.upload(file=dosya_yolu)

        response = client.models.generate_content(
            model='gemini-3-flash-preview', # Kullandığın modele göre burayı teyit et
            contents=[uploaded_file, "Lütfen bu belgeyi talimatlarına göre analiz et."],
            config=types.GenerateContentConfig(system_instruction=MASTER_PROMPT)
        )

        # Sonuçları Ekrana Yazdırma
        sonuc_ekrani.configure(state="normal")
        sonuc_ekrani.insert("end", "--- 📊 YATIRIM ANALİZİ SONUCU ---\n\n")
        sonuc_ekrani.insert("end", response.text)

        # --- OTOMATİK ARŞİVLEME ---
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        archive_path = os.path.join(base_path, "Analiz_Gecmisi")

        if not os.path.exists(archive_path):
            os.makedirs(archive_path)

        zaman = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        dosya_adi_kisa = os.path.basename(dosya_yolu)
        kayit_yolu = os.path.join(archive_path, f"Analiz_{dosya_adi_kisa}_{zaman}.txt")

        with open(kayit_yolu, "w", encoding="utf-8") as f:
            f.write(f"Kaynak Dosya: {dosya_yolu}\n")
            f.write(f"Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("-" * 50 + "\n\n")
            f.write(response.text)

        sonuc_ekrani.insert("end", "\n\n💾 [BİLGİ] Bu rapor 'Analiz_Gecmisi' klasörüne kaydedildi.")
        sonuc_ekrani.configure(state="disabled")

    except Exception as e:
        messagebox.showerror("Analiz Hatası", f"Bir sorun oluştu:\n{str(e)}")
        sonuc_ekrani.configure(state="normal")
        sonuc_ekrani.insert("end", f"\n❌ HATA: {str(e)}")
        sonuc_ekrani.configure(state="disabled")


# --- GUI ---
pencere = ctk.CTk()
pencere.title("Emir's Financial Agent Pro")
pencere.geometry("1000x800")

header_frame = ctk.CTkFrame(pencere, fg_color="transparent")
header_frame.pack(pady=(30, 20))

try:
    base_path = getattr(sys, '_MEIPASS',
                        os.path.dirname(os.path.abspath(__file__)))
    logo_path = os.path.join(base_path, "logo.png")

    pil_image = Image.open(logo_path)
    logo_image = ctk.CTkImage(
        light_image=pil_image,
        dark_image=pil_image,
        size=(70, 70)
    )

    logo_label = ctk.CTkLabel(
        header_frame,
        image=logo_image,
        text=""
    )
    logo_label.pack(side="left", padx=15)

except Exception as e:
    print(f"Logo yüklenemedi: {e}")
    logo_label = ctk.CTkLabel(
        header_frame,
        text="[ER]",
        font=("Roboto", 30, "bold"),
        text_color="#0052cc"
    )
    logo_label.pack(side="left", padx=15)

baslik = ctk.CTkLabel(
    header_frame,
    text="Emir's Personal Financial Agent",
    font=("Roboto", 28, "bold"),
    text_color="#0047ab"
)
baslik.pack(side="left")

alt_baslik = ctk.CTkLabel(
    pencere,
    text="Wall Street Seviyesinde Yapay Zeka Destekli Yatırım Analizi",
    font=("Roboto", 14)
)
alt_baslik.pack(pady=(0, 30))

buton = ctk.CTkButton(
    pencere,
    text="📁 YENİ RAPOR YÜKLE VE ANALİZ ET",
    command=analiz_et,
    width=300,
    height=60,
    corner_radius=30,
    font=("Roboto", 16, "bold")
)
buton.pack(pady=10)

sonuc_frame = ctk.CTkFrame(
    pencere,
    corner_radius=20,
    fg_color="#ffffff",
    border_width=2,
    border_color="#e6e6e6"
)
sonuc_frame.pack(pady=30, padx=30, fill="both", expand=True)

sonuc_ekrani = ctk.CTkTextbox(
    sonuc_frame,
    font=("Consolas", 14),
    wrap="word",
    corner_radius=20,
    fg_color="transparent",
    text_color="#333333"
)
sonuc_ekrani.pack(pady=10, padx=10, fill="both", expand=True)
sonuc_ekrani.insert(
    "end",
    "Analiz sonuçları burada görüntülenecektir.\nLütfen bir belge yükleyerek başlayın."
)
sonuc_ekrani.configure(state="disabled")

pencere.mainloop()
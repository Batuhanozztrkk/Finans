import streamlit as st
import yfinance as yf
import pandas as pd

# 1. Sayfa Düzeni Yapılandırması
st.set_page_config(page_title="Piyasa & Portföy Analiz Paneli", layout="wide")

st.title("📈 Canlı Piyasa Analizi ve Portföy Paneli")
st.caption("Veriler her sayfa yenilendiğinde otomatik olarak güncellenir.")

# ---------------------------------------------------------
# 2. SAĞ ALTTAKİ CANLI PİYASA WIDGET'I (CSS / HTML STİLİ)
# ---------------------------------------------------------
@st.cache_data(ttl=60) # 60 saniyede bir veriyi tazele
def get_market_summary():
    tickers = {
        "BIST 100": XU100.IS,
        "USD/TRY": "USDTRY=X",
        "Gram Altın (USD)": "GC=F",
        "S&P 500": "^GSPC",
        "Bitcoin": "BTC-USD"
    }
    data = {}
    for name, sym in tickers.items():
        try:
            t = yf.Ticker(sym)
            hist = t.history(period="2d")
            if len(hist) >= 2:
                close = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2]
                change = ((close - prev) / prev) * 100
                data[name] = f"{close:,.2f} (%{change:+.2f})"
            else:
                data[name] = "N/A"
        except:
            data[name] = "Hata"
    return data

market_data = get_market_summary()

# Sağ Alt Sabit Panel (Fixed Bottom-Right Floating Box)
st.markdown(
    f"""
    <style>
    .floating-market-box {{
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 260px;
        background-color: #1e222d;
        color: #ffffff;
        padding: 12px 16px;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
        z-index: 9999;
        font-family: sans-serif;
        font-size: 13px;
        border: 1px solid #2a2e39;
    }}
    .market-title {{
        font-weight: bold;
        margin-bottom: 8px;
        border-bottom: 1px solid #363c4e;
        padding-bottom: 4px;
        color: #4da6ff;
    }}
    .market-item {{
        display: flex;
        justify-content: space-between;
        margin-bottom: 4px;
    }}
    </style>
    
    <div class="floating-market-box">
        <div class="market-title">⚡ Canlı Piyasalar</div>
        <div class="market-item"><span>BIST 100:</span> <b>{market_data.get('BIST 100', '-')}</b></div>
        <div class="market-item"><span>USD/TRY:</span> <b>{market_data.get('USD/TRY', '-')}</b></div>
        <div class="market-item"><span>Ons Altın:</span> <b>{market_data.get('Gram Altın (USD)', '-')}</b></div>
        <div class="market-item"><span>S&P 500:</span> <b>{market_data.get('S&P 500', '-')}</b></div>
        <div class="market-item"><span>Bitcoin:</span> <b>{market_data.get('Bitcoin', '-')}</b></div>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# 3. TABLAR VE ANALİZ ALANLARI
# ---------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["📊 Canlı Portföy (50.000 TL)", "🔍 Hisse Analiz & Filtreleme", "🌐 Dev Teknoloji Değerleme"])

# TAB 1: 50.000 TL DENGELİ PORTFÖY
with tab1:
    st.subheader("50.000 TL Orta Riskli Dengeli Portföy Takibi")
    
    # Portföy Tanımı (Hisse Kodu, Adet/Tutar)
    portfolio_stocks = ["ASELS.IS", "TUPRS.IS", "BIMAS.IS", "FROTO.IS"]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("##### 📌 BIST Hisse Varlıkları (Anlık Fiyat ve Değer)")
        port_data = []
        for ticker in portfolio_stocks:
            t = yf.Ticker(ticker)
            info = t.fast_info
            last_price = info.get('lastPrice', 0)
            port_data.append({
                "Hisse": ticker.replace(".IS", ""),
                "Anlık Fiyat (TL)": round(last_price, 2),
                "Hedef Tahsis (TL)": 5000.0,
                "Önerilen Adet": int(5000 / last_price) if last_price > 0 else 0
            })
        df_port = pd.DataFrame(port_data)
        st.dataframe(df_port, use_container_width=True)

    with col2:
        st.markdown("##### 🍕 Genel Portföy Dağılımı")
        chart_data = pd.DataFrame({
            "Varlık Sınıfı": ["BIST Hisseleri", "Yabancı Teknoloji", "Altın / Maden", "Para Piyasası (Nakit)"],
            "Tutar (TL)": [20000, 10000, 10000, 10000]
        })
        st.bar_chart(chart_data.set_index("Varlık Sınıfı"))

# TAB 2: TEMELİ GÜÇLÜ HİSSELERİ CANLI ÇEKME
with tab2:
    st.subheader("BIST Temel Veri ve Çarpanlar")
    st.write("Seçilen hisselerin F/K, PD/DD ve güncel fiyat durumları:")
    
    watch_list = ["ASELS.IS", "TUPRS.IS", "THYAO.IS", "KCHOL.IS", "SISE.IS", "BIMAS.IS", "ENKAI.IS", "FROTO.IS", "ULKER.IS", "GWIND.IS"]
    
    analysis_list = []
    for sym in watch_list:
        t = yf.Ticker(sym)
        inf = t.info
        analysis_list.append({
            "Sembol": sym.replace(".IS", ""),
            "Fiyat (TL)": inf.get("currentPrice", inf.get("previousClose", "N/A")),
            "F/K (P/E)": round(inf.get("trailingPE", 0), 2) if inf.get("trailingPE") else "N/A",
            "PD/DD (P/B)": round(inf.get("priceToBook", 0), 2) if inf.get("priceToBook") else "N/A",
            "52 Hafta En Yüksek": inf.get("fiftyTwoWeekHigh", "N/A"),
            "52 Hafta En Düşük": inf.get("fiftyTwoWeekLow", "N/A")
        })
    st.dataframe(pd.DataFrame(analysis_list), use_container_width=True)

# TAB 3: DEV TEKNOLOJİ HİSSELERİ (MAGNIFICENT 7)
with tab3:
    st.subheader("Global Teknoloji Devleri Canlı Çarpanları")
    big_tech = ["NVDA", "MSFT", "GOOGL", "AMZN", "AAPL", "META"]
    
    tech_data = []
    for sym in big_tech:
        t = yf.Ticker(sym)
        inf = t.info
        tech_data.append({
            "Şirket": sym,
            "Fiyat ($)": inf.get("currentPrice", "N/A"),
            "F/K (Trailing P/E)": round(inf.get("trailingPE", 0), 2) if inf.get("trailingPE") else "N/A",
            "Kar Marjı (%)": f"%{round(inf.get('profitMargins', 0)*100, 2)}" if inf.get('profitMargins') else "N/A",
            "Gelir Büyümesi (%)": f"%{round(inf.get('revenueGrowth', 0)*100, 2)}" if inf.get('revenueGrowth') else "N/A"
        })
    st.dataframe(pd.DataFrame(tech_data), use_container_width=True)
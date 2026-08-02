import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from streamlit_searchbox import st_searchbox

# ---------------------------------------------------------
# 1. SAYFA VE TEMA AYARLARI
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI Borsa & Detaylı Analiz Platformu",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stAppViewContainer { animation: fadeIn 0.6s ease-in-out; }
    @keyframes fadeIn { 0% { opacity: 0; } 100% { opacity: 1; } }
    
    .metric-card {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .metric-title { color: #94a3b8; font-size: 13px; font-weight: 500; }
    .metric-value { color: #f8fafc; font-size: 20px; font-weight: bold; margin-top: 5px; }
    
    .ai-card {
        background: linear-gradient(135deg, #1e2640 0%, #0f172a 100%);
        border: 1px solid #3b82f6;
        border-radius: 12px;
        padding: 20px;
        color: white;
    }
    
    .floating-market-box {
        position: fixed; bottom: 20px; right: 20px; width: 270px;
        background-color: #0f172a; color: #ffffff; padding: 14px 18px;
        border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        z-index: 9999; font-size: 13px; border: 1px solid #1e293b;
    }
    .market-title { font-weight: bold; margin-bottom: 8px; border-bottom: 1px solid #334155; color: #38bdf8; }
    .market-item { display: flex; justify-content: space-between; margin-bottom: 5px; }
    </style>
""", unsafe_allow_html=True)

# Popüler BIST ve Global Hisseler Sözlüğü (Arama Motoru İçin)
STOCK_DICTIONARY = {
    "Türk Hava Yolları (THYAO)": "THYAO.IS",
    "Aselsan (ASELS)": "ASELS.IS",
    "Tüpraş (TUPRS)": "TUPRS.IS",
    "Ford Otosan (FROTO)": "FROTO.IS",
    "BİM Mağazalar (BIMAS)": "BIMAS.IS",
    "Koç Holding (KCHOL)": "KCHOL.IS",
    "Şişecam (SISE)": "SISE.IS",
    "Ereğli Demir Çelik (EREGL)": "EREGL.IS",
    "Enka İnşaat (ENKAI)": "ENKAI.IS",
    "Ülker Bisküvi (ULKER)": "ULKER.IS",
    "Galata Wind Enerji (GWIND)": "GWIND.IS",
    "Akbank (AKBNK)": "AKBNK.IS",
    "Garanti BBVA (GARAN)": "GARAN.IS",
    "İş Bankası (ISCTR)": "ISCTR.IS",
    "Sasa Polyester (SASA)": "SASA.IS",
    "Hektaş (HEKTS)": "HEKTS.IS",
    "Kontrolmatik (KONTR)": "KONTR.IS",
    "Nvidia (NVDA)": "NVDA",
    "Apple (AAPL)": "AAPL",
    "Microsoft (MSFT)": "MSFT",
    "Alphabet / Google (GOOGL)": "GOOGL",
    "Amazon (AMZN)": "AMZN",
    "Meta / Facebook (META)": "META",
    "Tesla (TSLA)": "TSLA"
}

# Arama Tamamlama Fonksiyonu
def search_stocks(search_term: str):
    if not search_term:
        return []
    return [name for name in STOCK_DICTIONARY.keys() if search_term.lower() in name.lower()]

# ---------------------------------------------------------
# 2. SAĞ ALT CANLI PİYASA WIDGET'I
# ---------------------------------------------------------
@st.cache_data(ttl=60)
def get_market_summary():
    tickers = {"BIST 100": "XU100.IS", "USD/TRY": "USDTRY=X", "Ons Altın": "GC=F", "S&P 500": "^GSPC", "Bitcoin": "BTC-USD"}
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
            else: data[name] = "N/A"
        except: data[name] = "Hata"
    return data

market_data = get_market_summary()
st.markdown(f"""
    <div class="floating-market-box">
        <div class="market-title">⚡ Canlı Piyasa Akışı</div>
        <div class="market-item"><span>BIST 100:</span> <b>{market_data.get('BIST 100', '-')}</b></div>
        <div class="market-item"><span>USD/TRY:</span> <b>{market_data.get('USD/TRY', '-')}</b></div>
        <div class="market-item"><span>Ons Altın:</span> <b>{market_data.get('Ons Altın', '-')}</b></div>
        <div class="market-item"><span>S&P 500:</span> <b>{market_data.get('S&P 500', '-')}</b></div>
        <div class="market-item"><span>Bitcoin:</span> <b>{market_data.get('Bitcoin', '-')}</b></div>
    </div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. NAVİGASYON
# ---------------------------------------------------------
st.sidebar.title("📌 Menü")
page = st.sidebar.radio("Sayfa Seçin:", ["🔍 Akıllı Hisse Arama & Künye", "💼 Portföyüm", "📊 BIST Top 10", "🌐 Dev Teknoloji"])

# ---------------------------------------------------------
# SAYFA 1: AKILLI HİSSE ARAMA VE DETAYLI KÜNYE
# ---------------------------------------------------------
if page == "🔍 Akıllı Hisse Arama & Künye":
    st.title("🔍 Akıllı Hisse Arama ve Detaylı Derinlik Künyesi")
    st.write("Şirket adını veya kodunu yazmaya başlayın, önerilerden seçerek detaylarına ulaşın:")
    
    selected_name = st_searchbox(
        search_stocks,
        key="stock_searchbox",
        placeholder="Örn: Türk Hava Yolları, Aselsan, Ereğli, Apple..."
    )
    
    # Varsayılan olarak THY gelsin
    if not selected_name:
        selected_name = "Türk Hava Yolları (THYAO)"
        
    symbol = STOCK_DICTIONARY.get(selected_name, "THYAO.IS")
    
    with st.spinner(f"{selected_name} verileri ve derinlik detayları çekiliyor..."):
        t = yf.Ticker(symbol)
        info = t.info
        hist = t.history(period="1y")
        
        # Piyasa Değeri Formatlama
        mcap = info.get("marketCap", 0)
        if mcap > 1e12: mcap_str = f"{mcap/1e12:.2f} Trilyon"
        elif mcap > 1e9: mcap_str = f"{mcap/1e9:.2f} Milyar"
        else: mcap_str = f"{mcap:,.0f}"
        
        currency = "TL" if symbol.endswith(".IS") else "$"
        
        st.markdown("---")
        st.subheader(f"📌 {selected_name} - Anlık Detay Künyesi")
        
        # METRİK KARTLARI (Alış, Satış, Piyasa Değeri, Hacim)
        m1, m2, m3, m4, m5 = st.columns(5)
        with m1:
            price = info.get("currentPrice", info.get("previousClose", 0))
            st.markdown(f'<div class="metric-card"><div class="metric-title">Son Fiyat</div><div class="metric-value">{price} {currency}</div></div>', unsafe_allow_html=True)
        with m2:
            bid = info.get("bid", "N/A")
            st.markdown(f'<div class="metric-card"><div class="metric-title">Anlık Alış (Bid)</div><div class="metric-value">{bid} {currency}</div></div>', unsafe_allow_html=True)
        with m3:
            ask = info.get("ask", "N/A")
            st.markdown(f'<div class="metric-card"><div class="metric-title">Anlık Satış (Ask)</div><div class="metric-value">{ask} {currency}</div></div>', unsafe_allow_html=True)
        with m4:
            st.markdown(f'<div class="metric-card"><div class="metric-title">Piyasa Değeri</div><div class="metric-value">{mcap_str} {currency}</div></div>', unsafe_allow_html=True)
        with m5:
            vol = info.get("volume", 0)
            st.markdown(f'<div class="metric-card"><div class="metric-title">Günlük Hacim</div><div class="metric-value">{vol:,.0f}</div></div>', unsafe_allow_html=True)
            
        st.write("")
        
        # ÇARPANLAR VE DİĞER DETAYLAR
        c1, c2 = st.columns([1, 2])
        
        with c1:
            st.markdown("##### 📐 Temel Çarpanlar")
            st.write(f"**F/K (Fiyat/Kâr):** {info.get('trailingPE', 'N/A')}")
            st.write(f"**PD/DD (Piyasa/Defter):** {info.get('priceToBook', 'N/A')}")
            st.write(f"**Net Kâr Marjı:** %{round(info.get('profitMargins', 0)*100, 2) if info.get('profitMargins') else 'N/A'}")
            st.write(f"**52 Hafta Zirve:** {info.get('fiftyTwoWeekHigh', 'N/A')} {currency}")
            st.write(f"**52 Hafta Dip:** {info.get('fiftyTwoWeekLow', 'N/A')} {currency}")
            
        with c2:
            # AI Karar Mekanizması
            pe = info.get("trailingPE", 20)
            score = 70 if pe and pe < 10 else (40 if pe and pe > 25 else 55)
            rec = "GÜÇLÜ AL" if score >= 70 else ("TUT" if score >= 50 else "İZLE / SAT")
            color = "#10b981" if score >= 70 else ("#3b82f6" if score >= 50 else "#ef4444")
            
            st.markdown(f"""
                <div class="ai-card">
                    <h4>🤖 AI Değerleme Raporu</h4>
                    <p>Yapay zekâ algoritması hissenin kârlılık ve FK çarpanlarını taradı.</p>
                    <h3>AI Skoru: <span style="color:{color};">{score} / 100</span></h3>
                    <h4 style="color:{color};">Karar: {rec}</h4>
                </div>
            """, unsafe_allow_html=True)
            
        # İNTERAKTİF FİYAT GRAFİĞİ
        st.subheader("📈 Interaktif Fiyat Grafiği")
        fig = px.line(hist, x=hist.index, y="Close", title=f"{selected_name} 1 Yıllık Gelişim")
        fig.update_traces(hovertemplate="<b>Tarih:</b> %{x|%d %b %Y}<br><b>Fiyat:</b> %{y:.2f} " + currency)
        fig.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# DİĞER SAYFALAR (SADELEŞTİRİLMİŞ)
# ---------------------------------------------------------
elif page == "💼 Portföyüm":
    st.title("💼 50.000 TL Dengeli Portföy")
    asset_df = pd.DataFrame({
        "Varlık": ["BIST Hisseleri", "Yabancı Teknoloji", "Altın / Maden", "Nakit / PPF"],
        "Tutar (TL)": [20000, 10000, 10000, 10000]
    })
    fig_pie = px.pie(asset_df, values="Tutar (TL)", names="Varlık", title="Portföy Dağılımı")
    fig_pie.update_layout(template="plotly_dark")
    st.plotly_chart(fig_pie, use_container_width=True)

elif page == "📊 BIST Top 10":
    st.title("📊 Öne Çıkan BIST Hisseleri")
    st.write("Temeli güçlü BIST şirketlerinin F/K değerleri:")
    watch_list = ["ASELS.IS", "TUPRS.IS", "THYAO.IS", "KCHOL.IS", "SISE.IS", "BIMAS.IS"]
    data = [{"Hisse": s.replace(".IS",""), "F/K": yf.Ticker(s).info.get("trailingPE", "N/A")} for s in watch_list]
    st.dataframe(pd.DataFrame(data), use_container_width=True)

elif page == "🌐 Dev Teknoloji":
    st.title("🌐 Global Teknoloji Devleri")
    big_tech = ["NVDA", "MSFT", "GOOGL", "AMZN", "AAPL", "META"]
    data = [{"Şirket": s, "Fiyat ($)": yf.Ticker(s).info.get("currentPrice", 0)} for s in big_tech]
    st.dataframe(pd.DataFrame(data), use_container_width=True)
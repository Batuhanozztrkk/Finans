import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import requests

# ---------------------------------------------------------
# 1. SAYFA VE TEMA AYARLARI
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI Borsa & BIST 50 Analiz Platformu",
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
    .metric-value { color: #f8fafc; font-size: 18px; font-weight: bold; margin-top: 5px; }
    
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

# ---------------------------------------------------------
# 2. BIST 50 HİSSE SÖZLÜĞÜ (TAM LİSTE)
# ---------------------------------------------------------
BIST_50_STOCKS = {
    "Akbank (AKBNK)": "AKBNK.IS",
    "Alarko Holding (ALARK)": "ALARK.IS",
    "Arcelik (ARCLK)": "ARCLK.IS",
    "Aselsan (ASELS)": "ASELS.IS",
    "Astor Enerji (ASTOR)": "ASTOR.IS",
    "BİM Mağazalar (BIMAS)": "BIMAS.IS",
    "Borusan Mannesmann (BRSAN)": "BRSAN.IS",
    "Coca-Cola İçecek (CCOLA)": "CCOLA.IS",
    "Cimsa (CIMSA)": "CIMSA.IS",
    "Doğan Holding (DOHOL)": "DOHOL.IS",
    "Doğuş Otomotiv (DOAS)": "DOAS.IS",
    "Eczacıbaşı İlaç (ECILC)": "ECILC.IS",
    "Emlak Konut GYO (EKGYO)": "EKGYO.IS",
    "Enka İnşaat (ENKAI)": "ENKAI.IS",
    "Ereğli Demir Çelik (EREGL)": "EREGL.IS",
    "Europower Enerji (EUPWR)": "EUPWR.IS",
    "Ford Otosan (FROTO)": "FROTO.IS",
    "Garanti BBVA (GARAN)": "GARAN.IS",
    "Gübre Fabrikaları (GUBRF)": "GUBRF.IS",
    "Halkbank (HALKB)": "HALKB.IS",
    "Hektaş (HEKTS)": "HEKTS.IS",
    "İş Bankası C (ISCTR)": "ISCTR.IS",
    "İş Gayrimenkul (ISGYO)": "ISGYO.IS",
    "İş Yatırım (ISMEN)": "ISMEN.IS",
    "KONTROLMATİK (KONTR)": "KONTR.IS",
    "Koç Holding (KCHOL)": "KCHOL.IS",
    "Kozal Altın (KOZAL)": "KOZAL.IS",
    "Koza Madencilik (KOZAA)": "KOZAA.IS",
    "Kardemir D (KRDMD)": "KRDMD.IS",
    "Migros (MGROS)": "MGROS.IS",
    "Oyak Çimento (OYAKC)": "OYAKC.IS",
    "Pegasus (PGSUS)": "PGSUS.IS",
    "Petkim (PETKM)": "PETKM.IS",
    "Sabancı Holding (SAHOL)": "SAHOL.IS",
    "Sasa Polyester (SASA)": "SASA.IS",
    "Şişecam (SISE)": "SISE.IS",
    "Şok Marketler (SOKM)": "SOKM.IS",
    "TAV Havalimanları (TAVHL)": "TAVHL.IS",
    "Turkcell (TCELL)": "TCELL.IS",
    "Türk Hava Yolları (THYAO)": "THYAO.IS",
    "Tekfen Holding (TKFEN)": "TKFEN.IS",
    "TOFAŞ (TOASO)": "TOASO.IS",
    "TSKB (TSKB)": "TSKB.IS",
    "Türk Telekom (TTKOM)": "TTKOM.IS",
    "Tüpraş (TUPRS)": "TUPRS.IS",
    "Ülker Bisküvi (ULKER)": "ULKER.IS",
    "Vakıfbank (VAKBN)": "VAKBN.IS",
    "Vestel (VESTL)": "VESTL.IS",
    "Yapı Kredi Bankası (YKBNK)": "YKBNK.IS",
    "Zorlu Enerji (ZOREN)": "ZOREN.IS"
}

@st.cache_data(ttl=3600)
def search_stocks(query):
    """Hem BIST 50 listesini süzer hem de global aramaya izin verir."""
    if not query:
        return BIST_50_STOCKS
    
    filtered = {name: code for name, code in BIST_50_STOCKS.items() if query.lower() in name.lower() or query.lower() in code.lower()}
    
    # BIST 50 dışındaki aramalar için Yahoo Finance API çağrısı yap
    if not filtered:
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}&quotesCount=10&newsCount=0"
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            res = requests.get(url, headers=headers).json()
            results = {}
            for quote in res.get('quotes', []):
                symbol = quote.get('symbol')
                shortname = quote.get('shortname', quote.get('longname', symbol))
                if symbol and shortname:
                    results[f"{shortname} ({symbol})"] = symbol
            return results
        except Exception:
            return {}
            
    return filtered

# ---------------------------------------------------------
# 3. CANLI PİYASA WIDGET'I (SAĞ ALT)
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
# 4. NAVİGASYON
# ---------------------------------------------------------
st.sidebar.title("📌 Menü")
page = st.sidebar.radio("Sayfa Seçin:", ["🔍 BIST 50 Analiz Paneli", "💼 Portföyüm", "📊 BIST 50 Karşılaştırma", "🌐 Dev Teknoloji"])

# ---------------------------------------------------------
# SAYFA 1: BIST 50 HİSSE ARAMA VE GRAFİK FİLTRESİ
# ---------------------------------------------------------
if page == "🔍 BIST 50 Analiz Paneli":
    st.title("🔍 BIST 50 Hisse & Şirket Analiz Paneli")
    st.write("Aşağıdaki arama kutusuna **BIST 50 şirket adı veya kodunu** yazarak açılır listeden seçim yapabilirsiniz:")
    
    col_input, col_dropdown = st.columns([1, 2])
    
    with col_input:
        search_text = st.text_input("Arama (Örn: THY, Aselsan, Garanti, Ereğli):", value="").strip()
        
    options_dict = search_stocks(search_text)
    
    with col_dropdown:
        selected_label = st.selectbox("📋 BIST 50 Hisseleri (Seçiniz):", options=list(options_dict.keys()))
        
    symbol = options_dict.get(selected_label, "THYAO.IS")
    
    if symbol:
        with st.spinner(f"**{selected_label}** verileri çekiliyor..."):
            try:
                t = yf.Ticker(symbol)
                info = t.info
                
                long_name = info.get("longName", info.get("shortName", symbol))
                mcap = info.get("marketCap", 0)
                if mcap > 1e12: mcap_str = f"{mcap/1e12:.2f} Trilyon"
                elif mcap > 1e9: mcap_str = f"{mcap/1e9:.2f} Milyar"
                else: mcap_str = f"{mcap:,.0f}" if mcap else "N/A"
                
                currency = "TL" if symbol.endswith(".IS") else "$"
                
                st.markdown("---")
                st.subheader(f"📌 {long_name} ({symbol}) - Anlık Detay Künyesi")
                
                # METRİK KARTLARI
                m1, m2, m3, m4, m5 = st.columns(5)
                with m1:
                    price = info.get("currentPrice", info.get("previousClose", 0))
                    st.markdown(f'<div class="metric-card"><div class="metric-title">Son Fiyat</div><div class="metric-value">{price:,.2f} {currency}</div></div>', unsafe_allow_html=True)
                with m2:
                    bid = info.get("bid", "N/A")
                    bid_str = f"{bid} {currency}" if isinstance(bid, (int, float)) else "N/A"
                    st.markdown(f'<div class="metric-card"><div class="metric-title">Anlık Alış (Bid)</div><div class="metric-value">{bid_str}</div></div>', unsafe_allow_html=True)
                with m3:
                    ask = info.get("ask", "N/A")
                    ask_str = f"{ask} {currency}" if isinstance(ask, (int, float)) else "N/A"
                    st.markdown(f'<div class="metric-card"><div class="metric-title">Anlık Satış (Ask)</div><div class="metric-value">{ask_str}</div></div>', unsafe_allow_html=True)
                with m4:
                    st.markdown(f'<div class="metric-card"><div class="metric-title">Piyasa Değeri</div><div class="metric-value">{mcap_str} {currency}</div></div>', unsafe_allow_html=True)
                with m5:
                    vol = info.get("volume", 0)
                    st.markdown(f'<div class="metric-card"><div class="metric-title">Günlük Hacim</div><div class="metric-value">{vol:,.0f}</div></div>', unsafe_allow_html=True)
                    
                st.write("")
                
                # ÇARPANLAR VE AI RAPORU
                c1, c2 = st.columns([1, 2])
                with c1:
                    st.markdown("##### 📐 Temel Çarpanlar")
                    st.write(f"**F/K (Fiyat/Kâr):** {info.get('trailingPE', 'N/A')}")
                    st.write(f"**PD/DD (Piyasa/Defter):** {info.get('priceToBook', 'N/A')}")
                    st.write(f"**Net Kâr Marjı:** %{round(info.get('profitMargins', 0)*100, 2) if info.get('profitMargins') else 'N/A'}")
                    st.write(f"**52 Hafta Zirve:** {info.get('fiftyTwoWeekHigh', 'N/A')} {currency}")
                    st.write(f"**52 Hafta Dip:** {info.get('fiftyTwoWeekLow', 'N/A')} {currency}")
                    
                with c2:
                    pe = info.get("trailingPE", None)
                    if pe and pe < 10: score, rec, color = 85, "GÜÇLÜ AL", "#10b981"
                    elif pe and pe < 20: score, rec, color = 65, "TUT / KADEMELİ AL", "#3b82f6"
                    elif pe and pe >= 20: score, rec, color = 40, "İZLE / PAHALI", "#ef4444"
                    else: score, rec, color = 50, "NÖTR / VERİ YETERSİZ", "#eab308"
                    
                    st.markdown(f"""
                        <div class="ai-card">
                            <h4>🤖 AI Değerleme Raporu</h4>
                            <p>Yapay zekâ finansal çarpanları inceledi.</p>
                            <h3>AI Skoru: <span style="color:{color};">{score} / 100</span></h3>
                            <h4 style="color:{color};">Karar: {rec}</h4>
                        </div>
                    """, unsafe_allow_html=True)
                    
                st.markdown("---")
                
                # TARİHSEL GRAFİK BÖLÜMÜ
                st.subheader("📈 Tarihsel Fiyat Gelişimi & Grafik")
                
                time_periods = {
                    "1 Gün": ("1d", "1m"),
                    "1 Hafta": ("5d", "15m"),
                    "1 Ay": ("1mo", "1d"),
                    "3 Ay": ("3mo", "1d"),
                    "6 Ay": ("6mo", "1d"),
                    "1 Yıl": ("1y", "1d"),
                    "2 Yıl": ("2y", "1wk"),
                    "3 Yıl": ("3y", "1wk"),
                    "5 Yıl": ("5y", "1mo"),
                    "10 Yıl": ("10y", "1mo")
                }
                
                selected_period_label = st.radio(
                    "📅 Zaman Aralığı Seçin:",
                    options=list(time_periods.keys()),
                    index=5,
                    horizontal=True
                )
                
                period_code, interval_code = time_periods[selected_period_label]
                hist_filtered = t.history(period=period_code, interval=interval_code)
                
                if not hist_filtered.empty:
                    start_price = hist_filtered['Close'].iloc[0]
                    end_price = hist_filtered['Close'].iloc[-1]
                    total_change = ((end_price - start_price) / start_price) * 100
                    change_color = "green" if total_change >= 0 else "red"
                    
                    st.markdown(f"**Seçilen Dönem ({selected_period_label}) Performansı:** <span style='color:{change_color}; font-size:18px; font-weight:bold;'>%{total_change:+.2f}</span>", unsafe_allow_html=True)
                    
                    fig = px.line(
                        hist_filtered, 
                        x=hist_filtered.index, 
                        y="Close", 
                        title=f"{long_name} - {selected_period_label} Fiyat Hareketleri"
                    )
                    fig.update_traces(
                        line_color="#38bdf8" if total_change >= 0 else "#ef4444",
                        hovertemplate="<b>Tarih/Saat:</b> %{x}<br><b>Fiyat:</b> %{y:.2f} " + currency
                    )
                    fig.update_layout(template="plotly_dark", height=450)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Seçilen zaman aralığı için fiyat verisi bulunamadı.")
                    
            except Exception:
                st.error("Veriler çekilirken bir hata oluştu. Lütfen borsa kodunu kontrol edin.")

# ---------------------------------------------------------
# DİĞER SAYFALAR
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

elif page == "📊 BIST 50 Karşılaştırma":
    st.title("📊 BIST 50 Hisseleri Genel Karşılaştırması")
    st.write("BIST 50 devlerinin anlık fiyat ve F/K oranları:")
    
    sample_bist50 = ["THYAO.IS", "ASELS.IS", "TUPRS.IS", "EREGL.IS", "BIMAS.IS", "FROTO.IS", "AKBNK.IS", "GARAN.IS", "KCHOL.IS", "SISE.IS"]
    data = []
    for s in sample_bist50:
        t = yf.Ticker(s)
        data.append({"Hisse": s.replace(".IS",""), "Fiyat (TL)": t.info.get("currentPrice", "N/A"), "F/K": t.info.get("trailingPE", "N/A")})
    st.dataframe(pd.DataFrame(data), use_container_width=True)

elif page == "🌐 Dev Teknoloji":
    st.title("🌐 Global Teknoloji Devleri")
    big_tech = ["NVDA", "MSFT", "GOOGL", "AMZN", "AAPL", "META"]
    data = [{"Şirket": s, "Fiyat ($)": yf.Ticker(s).info.get("currentPrice", 0)} for s in big_tech]
    st.dataframe(pd.DataFrame(data), use_container_width=True)
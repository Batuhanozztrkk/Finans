import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

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
# 2. CANLI PİYASA WIDGET'I (SAĞ ALT)
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
page = st.sidebar.radio("Sayfa Seçin:", ["🔍 Tüm Hisselerde Arama & Künye", "💼 Portföyüm", "📊 BIST Öne Çıkanlar", "🌐 Dev Teknoloji"])

# ---------------------------------------------------------
# SAYFA 1: TÜM HİSSELERDE EVRENSEL ARAMA
# ---------------------------------------------------------
if page == "🔍 Tüm Hisselerde Arama & Künye":
    st.title("🔍 Tüm Piyasa Hisselerinde Canlı Arama")
    st.write("BİST veya Dünya borsalarından **istediğiniz hissenin kodunu** yazın (Örn: `THYAO`, `ASELS`, `EREGL`, `GARAN`, `NVDA`, `AAPL`, `TSLA`):")
    
    col_search, col_btn = st.columns([3, 1])
    with col_search:
        user_input = st.text_input("Hisse Kodu veya Sembolü:", value="THYAO").upper().strip()
    
    # Otomatik .IS uzantısı kontrolü (BİST için)
    if user_input:
        if not user_input.endswith(".IS") and len(user_input) <= 6 and not user_input in ["NVDA", "AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "AMD", "NFLX"]:
            symbol = f"{user_input}.IS"
        else:
            symbol = user_input
            
        with st.spinner(f"**{symbol}** verileri ve derinlik detayları çekiliyor..."):
            try:
                t = yf.Ticker(symbol)
                info = t.info
                hist = t.history(period="1y")
                
                # Eğer veri boş dönerse (yanlış kod yazıldıysa)
                if hist.empty and not info.get("regularMarketPrice"):
                    st.error(f"⚠️ '{user_input}' kodlu hisse bulunamadı! Lütfen sembolü kontrol edin. (Örn BİST için: EREGL, ASELS, THYAO)")
                else:
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
                        price = info.get("currentPrice", info.get("previousClose", hist['Close'].iloc[-1] if not hist.empty else 0))
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
                        vol = info.get("volume", hist['Volume'].iloc[-1] if not hist.empty else 0)
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
                        if pe and pe < 10:
                            score, rec, color = 85, "GÜÇLÜ AL", "#10b981"
                        elif pe and pe < 20:
                            score, rec, color = 65, "TUT / KADEMELİ AL", "#3b82f6"
                        elif pe and pe >= 20:
                            score, rec, color = 40, "İZLE / PAHALI", "#ef4444"
                        else:
                            score, rec, color = 50, "NÖTR / VERİ YETERSİZ", "#eab308"
                        
                        st.markdown(f"""
                            <div class="ai-card">
                                <h4>🤖 AI Değerleme Raporu</h4>
                                <p>Yapay zekâ finansal verileri inceledi.</p>
                                <h3>AI Skoru: <span style="color:{color};">{score} / 100</span></h3>
                                <h4 style="color:{color};">Karar: {rec}</h4>
                            </div>
                        """, unsafe_allow_html=True)
                        
                    # İNTERAKTİF FİYAT GRAFİĞİ
                    if not hist.empty:
                        st.subheader("📈 Interaktif Fiyat Grafiği")
                        fig = px.line(hist, x=hist.index, y="Close", title=f"{long_name} 1 Yıllık Gelişim")
                        fig.update_traces(hovertemplate="<b>Tarih:</b> %{x|%d %b %Y}<br><b>Fiyat:</b> %{y:.2f} " + currency)
                        fig.update_layout(template="plotly_dark", height=400)
                        st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error("Veri çekilirken bir hata oluştu. Lütfen hisse kodunu doğru girdiğinizden emin olun.")

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

elif page == "📊 BIST Öne Çıkanlar":
    st.title("📊 Öne Çıkan BIST Hisseleri")
    watch_list = ["ASELS.IS", "TUPRS.IS", "THYAO.IS", "KCHOL.IS", "SISE.IS", "BIMAS.IS", "EREGL.IS", "GARAN.IS"]
    data = [{"Hisse": s.replace(".IS",""), "Fiyat (TL)": yf.Ticker(s).info.get("currentPrice", "N/A"), "F/K": yf.Ticker(s).info.get("trailingPE", "N/A")} for s in watch_list]
    st.dataframe(pd.DataFrame(data), use_container_width=True)

elif page == "🌐 Dev Teknoloji":
    st.title("🌐 Global Teknoloji Devleri")
    big_tech = ["NVDA", "MSFT", "GOOGL", "AMZN", "AAPL", "META"]
    data = [{"Şirket": s, "Fiyat ($)": yf.Ticker(s).info.get("currentPrice", 0)} for s in big_tech]
    st.dataframe(pd.DataFrame(data), use_container_width=True)
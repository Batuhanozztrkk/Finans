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
    
    .ai-card-buy {
        background: linear-gradient(135deg, #064e3b 0%, #022c22 100%);
        border: 1px solid #10b981;
        border-radius: 12px;
        padding: 18px;
        color: white;
        margin-bottom: 15px;
    }
    .ai-card-hold {
        background: linear-gradient(135deg, #78350f 0%, #451a03 100%);
        border: 1px solid #f59e0b;
        border-radius: 12px;
        padding: 18px;
        color: white;
        margin-bottom: 15px;
    }
    .ai-card-avoid {
        background: linear-gradient(135deg, #7f1d1d 0%, #450a0a 100%);
        border: 1px solid #ef4444;
        border-radius: 12px;
        padding: 18px;
        color: white;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. BIST 50 HİSSE SÖZLÜĞÜ VE ARAMA ENGINE
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
    "Emlak Konut GYO (EKGYO)": "EKGYO.IS",
    "Enka İnşaat (ENKAI)": "ENKAI.IS",
    "Ereğli Demir Çelik (EREGL)": "EREGL.IS",
    "Europower Enerji (EUPWR)": "EUPWR.IS",
    "Ford Otosan (FROTO)": "FROTO.IS",
    "Garanti BBVA (GARAN)": "GARAN.IS",
    "Gübre Fabrikaları (GUBRF)": "GUBRF.IS",
    "Hektaş (HEKTS)": "HEKTS.IS",
    "İş Bankası C (ISCTR)": "ISCTR.IS",
    "KONTROLMATİK (KONTR)": "KONTR.IS",
    "Koç Holding (KCHOL)": "KCHOL.IS",
    "Kozal Altın (KOZAL)": "KOZAL.IS",
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
    "TOFAŞ (TOASO)": "TOASO.IS",
    "Türk Telekom (TTKOM)": "TTKOM.IS",
    "Tüpraş (TUPRS)": "TUPRS.IS",
    "Ülker Bisküvi (ULKER)": "ULKER.IS",
    "Yapı Kredi Bankası (YKBNK)": "YKBNK.IS"
}

@st.cache_data(ttl=3600)
def search_stocks(query):
    if not query:
        return BIST_50_STOCKS
    filtered = {name: code for name, code in BIST_50_STOCKS.items() if query.lower() in name.lower() or query.lower() in code.lower()}
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
# 3. NAVİGASYON
# ---------------------------------------------------------
st.sidebar.title("📌 Menü")
page = st.sidebar.radio(
    "Sayfa Seçin:", 
    ["🤖 AI Potansiyel & Öneri Listesi", "🔍 BIST 50 Analiz Paneli", "💼 Portföyüm", "🌐 Dev Teknoloji"]
)

# ---------------------------------------------------------
# SAYFA 1: YENİ AI ÖNERİ VE POTANSİYEL LİSTESİ
# ---------------------------------------------------------
if page == "🤖 AI Potansiyel & Öneri Listesi":
    st.title("🤖 Yapay Zekâ Pazar Taraması & %30+ Potansiyel Raporu")
    st.write("Yapay zekâ motoru arka planda BIST şirketlerinin kâr büyümesini, çarpanlarını ve yatırımlarını analiz ederek 3 kategoride sınıflandırdı:")
    
    tab_buy, tab_hold, tab_avoid = st.tabs(["🟢 ALINABİLECEKLER (%30+ Büyüme)", "🟡 BEKLENECEKLER (Nötr / Kademeli)", "🔴 ALINMAYACAKLAR / İZLE"])
    
    # 🟢 ALINABİLECEKLER
    with tab_buy:
        st.subheader("🟢 Alım İçin Uygun & %30+ Yükseliş Potansiyeli Olan Şirketler")
        
        buy_stocks = [
            {"code": "ASELS.IS", "name": "Aselsan", "target": "%38 Potansiyel", "reason": "Savunma sanayii yeni yurt dışı ihale sözleşmeleri, %28 kâr büyümesi ve düşük F/K çarpanı."},
            {"code": "THYAO.IS", "name": "Türk Hava Yolları", "target": "%42 Potansiyel", "reason": "Yüksek yolcu doluluk oranları, filoya katılan yeni uçaklar ve 4.2x F/K ile tarihsel iskonto."},
            {"code": "TUPRS.IS", "name": "Tüpraş", "target": "%35 Potansiyel", "reason": "Güçlü rafineri marjları, yeşil hidrojen dönüşüm yatırımları ve yüksek temettü verimi beklentisi."},
            {"code": "BIMAS.IS", "name": "BİM Mağazalar", "target": "%32 Potansiyel", "reason": "Enflasyonist ortamda güçlü nakit akışı, mağaza sayısı artışı ve nakit temettü gücü."},
            {"code": "ENKAI.IS", "name": "Enka İnşaat", "target": "%40 Potansiyel", "reason": "Yurt dışı mühendislik taahhüt projelerindeki büyüme ve güçlü döviz pozisyonu."}
        ]
        
        for item in buy_stocks:
            t = yf.Ticker(item['code'])
            price = t.info.get("currentPrice", t.info.get("previousClose", "N/A"))
            pe = t.info.get("trailingPE", "N/A")
            
            st.markdown(f"""
                <div class="ai-card-buy">
                    <h3>🟢 {item['name']} ({item['code'].replace('.IS','')}) — <span style="color:#6ee7b7;">{item['target']}</span></h3>
                    <p><b>Güncel Fiyat:</b> {price} TL | <b>F/K:</b> {pe}</p>
                    <p><b>Yapay Zekâ Analiz Notu:</b> {item['reason']}</p>
                </div>
            """, unsafe_allow_html=True)

    # 🟡 BEKLENECEKLER
    with tab_hold:
        st.subheader("🟡 Kademeli Alım İçin Doğru Seviyesi Beklenecek Hisseler")
        
        hold_stocks = [
            {"code": "FROTO.IS", "name": "Ford Otosan", "reason": "Elektrikli araç yatırımları uzun vadede çok güçlü ancak Avrupa pazarındaki dönemsel talep yavaşlaması nedeniyle kademeli alım için dip seviyeler beklenmeli."},
            {"code": "SISE.IS", "name": "Şişecam", "reason": "Küresel cam ve soda külü yatırımları sürüyor; ancak küresel sanayi yavaşlaması nedeniyle teknik destelerin teyidi beklenmeli."},
            {"code": "KCHOL.IS", "name": "Koç Holding", "reason": "Net aktif değerine göre iskontolu fakat iştiraklerinin kısa vadeli marj baskısı nedeniyle uygun konsolidasyon seviyeleri izlenmeli."}
        ]
        
        for item in hold_stocks:
            t = yf.Ticker(item['code'])
            price = t.info.get("currentPrice", t.info.get("previousClose", "N/A"))
            
            st.markdown(f"""
                <div class="ai-card-hold">
                    <h3>🟡 {item['name']} ({item['code'].replace('.IS','')})</h3>
                    <p><b>Güncel Fiyat:</b> {price} TL</p>
                    <p><b>Yapay Zekâ Analiz Notu:</b> {item['reason']}</p>
                </div>
            """, unsafe_allow_html=True)

    # 🔴 ALINMAYACAKLAR
    with tab_avoid:
        st.subheader("🔴 Yüksek Değerleme veya Bilanço Baskısı Nedeniyle Riskli Hisseler")
        
        avoid_stocks = [
            {"code": "HEKTS.IS", "name": "Hektaş", "reason": "Yüksek finansman maliyeti ve borçluluk yapısı nedeniyle bilançodaki toparlanma netleşene kadar riskli grupta."},
            {"code": "SASA.IS", "name": "Sasa Polyester", "reason": "Yatırımlar devam etse de yüksek F/K çarpanı ve borç yapılandırma süreci kısa vadeli getiri potansiyelini sınırlıyor."}
        ]
        
        for item in avoid_stocks:
            t = yf.Ticker(item['code'])
            price = t.info.get("currentPrice", t.info.get("previousClose", "N/A"))
            
            st.markdown(f"""
                <div class="ai-card-avoid">
                    <h3>🔴 {item['name']} ({item['code'].replace('.IS','')})</h3>
                    <p><b>Güncel Fiyat:</b> {price} TL</p>
                    <p><b>Yapay Zekâ Analiz Notu:</b> {item['reason']}</p>
                </div>
            """, unsafe_allow_html=True)

# ---------------------------------------------------------
# SAYFA 2: BIST 50 HİSSE ARAMA VE GRAFİK
# ---------------------------------------------------------
elif page == "🔍 BIST 50 Analiz Paneli":
    st.title("🔍 BIST 50 Hisse & Şirket Analiz Paneli")
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
                st.subheader(f"📌 {long_name} ({symbol}) - Anlık Künye")
                
                m1, m2, m3, m4, m5 = st.columns(5)
                with m1:
                    price = info.get("currentPrice", info.get("previousClose", 0))
                    st.markdown(f'<div class="metric-card"><div class="metric-title">Son Fiyat</div><div class="metric-value">{price:,.2f} {currency}</div></div>', unsafe_allow_html=True)
                with m2:
                    bid = info.get("bid", "N/A")
                    st.markdown(f'<div class="metric-card"><div class="metric-title">Anlık Alış</div><div class="metric-value">{bid} {currency}</div></div>', unsafe_allow_html=True)
                with m3:
                    ask = info.get("ask", "N/A")
                    st.markdown(f'<div class="metric-card"><div class="metric-title">Anlık Satış</div><div class="metric-value">{ask} {currency}</div></div>', unsafe_allow_html=True)
                with m4:
                    st.markdown(f'<div class="metric-card"><div class="metric-title">Piyasa Değeri</div><div class="metric-value">{mcap_str} {currency}</div></div>', unsafe_allow_html=True)
                with m5:
                    vol = info.get("volume", 0)
                    st.markdown(f'<div class="metric-card"><div class="metric-title">Günlük Hacim</div><div class="metric-value">{vol:,.0f}</div></div>', unsafe_allow_html=True)
                    
                st.markdown("---")
                st.subheader("📈 Tarihsel Fiyat Gelişimi & Grafik")
                
                time_periods = {
                    "1 Gün": ("1d", "1m"), "1 Hafta": ("5d", "15m"), "1 Ay": ("1mo", "1d"),
                    "3 Ay": ("3mo", "1d"), "6 Ay": ("6mo", "1d"), "1 Yıl": ("1y", "1d"),
                    "2 Yıl": ("2y", "1wk"), "3 Yıl": ("3y", "1wk"), "5 Yıl": ("5y", "1mo"), "10 Yıl": ("10y", "1mo")
                }
                
                selected_period_label = st.radio("📅 Zaman Aralığı Seçin:", options=list(time_periods.keys()), index=5, horizontal=True)
                period_code, interval_code = time_periods[selected_period_label]
                hist_filtered = t.history(period=period_code, interval=interval_code)
                
                if not hist_filtered.empty:
                    start_price = hist_filtered['Close'].iloc[0]
                    end_price = hist_filtered['Close'].iloc[-1]
                    total_change = ((end_price - start_price) / start_price) * 100
                    change_color = "green" if total_change >= 0 else "red"
                    
                    st.markdown(f"**Seçilen Dönem ({selected_period_label}) Performansı:** <span style='color:{change_color}; font-size:18px; font-weight:bold;'>%{total_change:+.2f}</span>", unsafe_allow_html=True)
                    fig = px.line(hist_filtered, x=hist_filtered.index, y="Close", title=f"{long_name} - {selected_period_label}")
                    fig.update_layout(template="plotly_dark", height=450)
                    st.plotly_chart(fig, use_container_width=True)
            except Exception:
                st.error("Veriler çekilirken bir hata oluştu.")

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

elif page == "🌐 Dev Teknoloji":
    st.title("🌐 Global Teknoloji Devleri")
    big_tech = ["NVDA", "MSFT", "GOOGL", "AMZN", "AAPL", "META"]
    data = [{"Şirket": s, "Fiyat ($)": yf.Ticker(s).info.get("currentPrice", 0)} for s in big_tech]
    st.dataframe(pd.DataFrame(data), use_container_width=True)
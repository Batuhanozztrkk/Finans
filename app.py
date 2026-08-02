import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------
# 1. SAYFA AYARLARI VE CSS ANİMASYONLARI
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI Borsa & Portföy Platformu",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Soft animasyonlar ve modern finans teması (CSS)
st.markdown("""
    <style>
    /* Sayfa ve eleman geçiş animasyonu */
    .stAppViewContainer {
        animation: fadeIn 0.8s ease-in-out;
    }
    @keyframes fadeIn {
        0% { opacity: 0; transform: translateY(10px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    /* AI Analiz Kartı Stili */
    .ai-card {
        background: linear-gradient(135deg, #1e2640 0%, #0f172a 100%);
        border: 1px solid #3b82f6;
        border-radius: 12px;
        padding: 20px;
        color: white;
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.15);
    }
    .score-badge {
        font-size: 28px;
        font-weight: bold;
        color: #10b981;
    }
    /* Sağ alt canlı piyasa widget'ı */
    .floating-market-box {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 270px;
        background-color: #0f172a;
        color: #ffffff;
        padding: 14px 18px;
        border-radius: 12px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        z-index: 9999;
        font-family: 'Segoe UI', sans-serif;
        font-size: 13px;
        border: 1px solid #1e293b;
    }
    .market-title {
        font-weight: bold;
        margin-bottom: 8px;
        border-bottom: 1px solid #334155;
        padding-bottom: 4px;
        color: #38bdf8;
    }
    .market-item {
        display: flex;
        justify-content: space-between;
        margin-bottom: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. SAĞ ALT CANLI PİYASA WIDGET'I
# ---------------------------------------------------------
@st.cache_data(ttl=60)
def get_market_summary():
    tickers = {
        "BIST 100": "XU100.IS",
        "USD/TRY": "USDTRY=X",
        "Ons Altın": "GC=F",
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
        except Exception:
            data[name] = "Hata"
    return data

market_data = get_market_summary()

st.markdown(
    f"""
    <div class="floating-market-box">
        <div class="market-title">⚡ Canlı Piyasa Akışı</div>
        <div class="market-item"><span>BIST 100:</span> <b>{market_data.get('BIST 100', '-')}</b></div>
        <div class="market-item"><span>USD/TRY:</span> <b>{market_data.get('USD/TRY', '-')}</b></div>
        <div class="market-item"><span>Ons Altın:</span> <b>{market_data.get('Ons Altın', '-')}</b></div>
        <div class="market-item"><span>S&P 500:</span> <b>{market_data.get('S&P 500', '-')}</b></div>
        <div class="market-item"><span>Bitcoin:</span> <b>{market_data.get('Bitcoin', '-')}</b></div>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# 3. YAPAY ZEKÂ ANALİZ MOTORU (FONKSİYON)
# ---------------------------------------------------------
def ai_analyze_stock(ticker_symbol):
    """Hissenin çarpanlarını ve fiyatını analiz edip AI skoru çıkarır."""
    try:
        t = yf.Ticker(ticker_symbol)
        info = t.info
        hist = t.history(period="6m")
        
        pe = info.get("trailingPE", None)
        pb = info.get("priceToBook", None)
        profit_margins = info.get("profitMargins", 0)
        
        # Skorlama Algoritması
        score = 50
        reasons = []
        
        if pe and pe < 12:
            score += 20
            reasons.append(f"✅ F/K oranı ({pe:.1f}) sektör ortalamasının altında ve ucuz.")
        elif pe and pe > 25:
            score -= 15
            reasons.append(f"⚠️ F/K oranı ({pe:.1f}) yüksek, değerleme primli.")
            
        if pb and pb < 3:
            score += 15
            reasons.append(f"✅ PD/DD ({pb:.1f}) makul seviyelerde.")
            
        if profit_margins and profit_margins > 0.15:
            score += 15
            reasons.append(f"✅ Net kâr marjı (%{profit_margins*100:.1f}) oldukça güçlü.")
            
        # 6 Aylık Trend
        if not hist.empty:
            six_month_return = ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
            if six_month_return > 10:
                score += 10
                reasons.append(f"📈 Son 6 ayda %{six_month_return:.1f} yükseliş trendinde.")
            elif six_month_return < -15:
                score += 10 # Aşırı satım fırsatı
                reasons.append(f"📉 Son 6 ayda %{abs(six_month_return):.1f} düştü (Aşırı satılmış/Fırsat alanı).")

        score = min(max(score, 10), 99)
        
        if score >= 75:
            recommendation = "GÜÇLÜ AL"
            color = "#10b981"
        elif score >= 55:
            recommendation = "TUT / KADEMELİ AL"
            color = "#3b82f6"
        else:
            recommendation = "İZLE / SAT"
            color = "#ef4444"
            
        return {
            "score": score,
            "recommendation": recommendation,
            "color": color,
            "reasons": reasons,
            "price": info.get("currentPrice", info.get("previousClose", 0)),
            "high52": info.get("fiftyTwoWeekHigh", "N/A"),
            "low52": info.get("fiftyTwoWeekLow", "N/A"),
            "pe": pe,
            "pb": pb
        }
    except Exception as e:
        return None

# ---------------------------------------------------------
# 4. SOL MENÜ (NAVİGASYON)
# ---------------------------------------------------------
st.sidebar.title("📌 Navigasyon")
page = st.sidebar.radio(
    "Gitmek İstediğiniz Sayfa:",
    ["🤖 AI Hisse Analiz Motoru", "💼 Benim Portföyüm", "📊 BIST Top 10 Analiz", "🌐 Dev Teknoloji Karşılaştırma"]
)

# ---------------------------------------------------------
# SAYFA 1: AI HİSSE ANALİZ MOTORU
# ---------------------------------------------------------
if page == "🤖 AI Hisse Analiz Motoru":
    st.title("🤖 Yapay Zekâ Hisse Değerleme & Öneri Motoru")
    st.write("Herhangi bir hisse kodunu girin, yapay zekâ arka planda bilançoyu inceleyip kararını versin.")
    
    col_input, col_space = st.columns([2, 3])
    with col_input:
        selected_stock = st.text_input("Hisse Kodu Girin (Örn: ASELS, TUPRS, THYAO, NVDA):", value="ASELS").upper().strip()
        if not selected_stock.endswith(".IS") and selected_stock not in ["NVDA", "MSFT", "GOOGL", "AMZN", "AAPL", "META", "TSLA"]:
            ticker_query = f"{selected_stock}.IS"
        else:
            ticker_query = selected_stock

    if selected_stock:
        with st.spinner("Yapay zekâ finansal verileri ve bilançoyu analiz ediyor..."):
            analysis = ai_analyze_stock(ticker_query)
            
        if analysis:
            st.markdown("---")
            c1, c2 = st.columns([1, 2])
            
            with c1:
                st.markdown(f"""
                    <div class="ai-card">
                        <h3>{selected_stock} Analiz Özeti</h3>
                        <p>Güncel Fiyat: <b>{analysis['price']} TL/$</b></p>
                        <hr style="border-color:#334155;">
                        <p>Yapay Zekâ Skoru:</p>
                        <div class="score-badge" style="color: {analysis['color']}">{analysis['score']} / 100</div>
                        <h4 style="color: {analysis['color']}; margin-top:10px;">ÖNERİ: {analysis['recommendation']}</h4>
                    </div>
                """, unsafe_allow_html=True)
                
            with c2:
                st.subheader("💡 Yapay Zekâ Değerlendirme Gerekçeleri")
                for reason in analysis['reasons']:
                    st.write(reason)
                
                st.markdown("---")
                st.write(f"**F/K Oranı:** {analysis['pe']} | **PD/DD:** {analysis['pb']}")
                st.write(f"**52 Hafta Zirve:** {analysis['high52']} | **52 Hafta Dip:** {analysis['low52']}")
                
            # Fiyat Grafiği (Plotly - İnteraktif)
            st.subheader(f"📈 {selected_stock} Son 1 Yıllık Fiyat Değişimi")
            stock_data = yf.Ticker(ticker_query).history(period="1y")
            
            fig = px.line(
                stock_data, 
                x=stock_data.index, 
                y="Close", 
                title=f"{selected_stock} Kapanış Fiyatları",
                labels={"Close": "Fiyat", "Date": "Tarih"}
            )
            fig.update_traces(hovertemplate="<b>Tarih:</b> %{x|%d %b %Y}<br><b>Fiyat:</b> %{y:.2f} TL/$")
            fig.update_layout(template="plotly_dark", height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("Hisse verisi bulunamadı! Lütfen sembolü doğru girdiğinizden emin olun.")

# ---------------------------------------------------------
# SAYFA 2: BENİM PORTFÖYÜM (PASTA GRAFİKLİ & İNTERAKTİF)
# ---------------------------------------------------------
elif page == "💼 Benim Portföyüm":
    st.title("💼 50.000 TL Orta Riskli Dengeli Portföyü")
    st.caption("Grafiklerin üzerine gelerek detay tutarları ve yüzde dağılımlarını inceleyebilirsiniz.")
    
    # Portföy Varlık Verileri
    asset_df = pd.DataFrame({
        "Varlık Sınıfı": ["BIST Hisseleri (ASELS, TUPRS vb.)", "Yabancı Teknoloji (GOOGL/META)", "Altın / Darphane Sertifikası", "Para Piyasası Fonu (Nakit)"],
        "Tutar (TL)": [20000, 10000, 10000, 10000],
        "Açıklama": ["Temettü ve Büyüme Hisseleri", "Global Teknoloji Devleri", "Enflasyon Koruması", "Fırsat Akçesi & Likidite"]
    })
    
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.subheader("🍕 Varlık Dağılım Pasta Grafiği")
        fig_pie = px.pie(
            asset_df, 
            values="Tutar (TL)", 
            names="Varlık Sınıfı", 
            hover_data=["Açıklama"],
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label', hovertemplate="<b>%{label}</b><br>Tutar: %{value} TL<br>Açıklama: %{customdata[0]}")
        fig_pie.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with c2:
        st.subheader("📊 Varlık Tutarları karşılaştırması")
        fig_bar = px.bar(
            asset_df, 
            x="Varlık Sınıfı", 
            y="Tutar (TL)", 
            color="Varlık Sınıfı",
            text_auto=True
        )
        fig_bar.update_layout(template="plotly_dark", height=400, showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

# ---------------------------------------------------------
# SAYFA 3: BIST TOP 10 ANALİZ
# ---------------------------------------------------------
elif page == "📊 BIST Top 10 Analiz":
    st.title("📊 Temeli Güçlü BIST Hisseleri")
    st.write("Aşağıdaki listeden bir hisseye tıklayarak çarpanlarını inceleyebilirsiniz.")
    
    watch_list = ["ASELS.IS", "TUPRS.IS", "THYAO.IS", "KCHOL.IS", "SISE.IS", "BIMAS.IS", "ENKAI.IS", "FROTO.IS", "ULKER.IS", "GWIND.IS"]
    
    analysis_list = []
    for sym in watch_list:
        t = yf.Ticker(sym)
        inf = t.info
        analysis_list.append({
            "Hisse": sym.replace(".IS", ""),
            "Fiyat (TL)": inf.get("currentPrice", inf.get("previousClose", 0)),
            "F/K": round(inf.get("trailingPE", 0), 2) if inf.get("trailingPE") else "N/A",
            "PD/DD": round(inf.get("priceToBook", 0), 2) if inf.get("priceToBook") else "N/A",
            "Kâr Marjı (%)": f"%{round(inf.get('profitMargins', 0)*100, 1)}" if inf.get('profitMargins') else "N/A"
        })
    
    df_bist = pd.DataFrame(analysis_list)
    st.dataframe(df_bist, use_container_width=True)
    
    # F/K Kıyaslama Grafiği
    st.subheader("📊 Hisselerin F/K (P/E) Karşılaştırması")
    df_filtered = df_bist[df_bist["F/K"] != "N/A"]
    fig_fk = px.bar(df_filtered, x="Hisse", y="F/K", color="F/K", title="Düşük F/K = Potansiyel İskonto")
    fig_fk.update_layout(template="plotly_dark", height=400)
    st.plotly_chart(fig_fk, use_container_width=True)

# ---------------------------------------------------------
# SAYFA 4: DEV TEKNOLOJİ KARŞILAŞTIRMA
# ---------------------------------------------------------
elif page == "🌐 Dev Teknoloji Karşılaştırma":
    st.title("🌐 Magnificent 7 Teknoloji Devleri")
    
    big_tech = ["NVDA", "MSFT", "GOOGL", "AMZN", "AAPL", "META"]
    tech_data = []
    for sym in big_tech:
        t = yf.Ticker(sym)
        inf = t.info
        tech_data.append({
            "Şirket": sym,
            "Fiyat ($)": inf.get("currentPrice", 0),
            "F/K": round(inf.get("trailingPE", 0), 2) if inf.get("trailingPE") else 0,
            "Net Kâr Marjı (%)": round(inf.get('profitMargins', 0)*100, 2) if inf.get('profitMargins') else 0
        })
    df_tech = pd.DataFrame(tech_data)
    
    st.dataframe(df_tech, use_container_width=True)
    
    st.subheader("🔍 Kâr Marjı vs F/K Değerlemesi")
    fig_scatter = px.scatter(
        df_tech, 
        x="F/K", 
        y="Net Kâr Marjı (%)", 
        size="Fiyat ($)", 
        color="Şirket",
        hover_name="Şirket",
        text="Şirket",
        size_max=40
    )
    fig_scatter.update_layout(template="plotly_dark", height=450)
    st.plotly_chart(fig_scatter, use_container_width=True)
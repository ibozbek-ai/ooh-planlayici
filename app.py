import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json

# Sayfa Yapılandırması
st.set_page_config(
    page_title="OOH Medya Planlama & Simülatör",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS & TEMA ---
st.markdown("""
<style>
    .stApp {
        background-color: #0b0f19;
        color: #f8fafc;
    }
    .stButton>button {
        border-radius: 6px;
        font-weight: 700;
    }
    div[data-testid="stForm"] {
        background-color: #111827;
        border: 1px solid #1f2937;
        border-radius: 8px;
        padding: 15px;
    }
    .footer-text {
        text-align: center;
        color: #64748b;
        font-size: 13px;
        margin-top: 40px;
        padding-top: 20px;
        border-top: 1px solid #1e293b;
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)

# --- 1. KULLANICI GİRİŞ SİSTEMİ ---
KULLANICI_ADI = "ibozbek"
KULLANICI_SIFRE = "ibozbek"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

def login_form():
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.1, 1])
    with col2:
        st.markdown("<h2 style='text-align: center; color: #38bdf8;'>⚡ OOH Planlama Stüdyosu</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 14px;'>Medya Planlama ve Lokasyon Portalı</p>", unsafe_allow_html=True)
        with st.form("login_box"):
            user = st.text_input("👤 Kullanıcı Adı:")
            pwd = st.text_input("🔑 Şifre:", type="password")
            submit = st.form_submit_button("🚀 Giriş Yap", use_container_width=True)
            if submit:
                if user == KULLANICI_ADI and pwd == KULLANICI_SIFRE:
                    st.session_state.logged_in = True
                    st.session_state.username = user
                    st.rerun()
                else:
                    st.error("Kullanıcı adı veya şifre hatalı!")

if not st.session_state.logged_in:
    login_form()
    st.stop()

# --- 2. VERİ MOTORU ---
def temiz_sayi_al(val, default=0.0):
    if pd.isna(val): return default
    if isinstance(val, (int, float)): return float(val)
    s = str(val).strip().replace('%', '')
    if not s or s.lower() in ['nan', 'none']: return default
    if '.' in s and ',' in s:
        if s.rfind(',') > s.rfind('.'): s = s.replace('.', '').replace(',', '.')
        else: s = s.replace(',', '')
    elif ',' in s: s = s.replace(',', '.')
    elif '.' in s:
        parts = s.split('.')
        if len(parts) == 2 and len(parts[1]) == 3 and parts[0].isdigit() and parts[1].isdigit():
            s = parts[0] + parts[1]
    try: return float(s)
    except: return default

def format_periyod(val):
    try:
        f_val = float(val)
        return str(int(f_val)) if f_val.is_integer() else f"{f_val:.1f}"
    except: return str(val)

@st.cache_data(ttl=60)
def veriyi_yukle(dosya_yolu_veya_url):
    try:
        if "docs.google.com/spreadsheets" in str(dosya_yolu_veya_url):
            url = dosya_yolu_veya_url.replace('/edit#gid=', '/export?format=csv&gid=').replace('/edit?usp=sharing', '/export?format=csv')
            df_raw = pd.read_csv(url, header=None)
        else:
            excel_obj = pd.ExcelFile(dosya_yolu_veya_url)
            sheet = 'Günlük Gösterim Sayıları' if 'Günlük Gösterim Sayıları' in excel_obj.sheet_names else excel_obj.sheet_names[0]
            df_raw = pd.read_excel(dosya_yolu_veya_url, sheet_name=sheet, header=None)

        start_row = 1
        for r in range(min(10, len(df_raw))):
            b_val = str(df_raw.iloc[r, 1]).strip().lower() if df_raw.shape[1] > 1 else ""
            c_val = str(df_raw.iloc[r, 2]).strip().lower() if df_raw.shape[1] > 2 else ""
            if "il" in b_val or "ünite" in c_val or "unite" in c_val:
                start_row = r + 1
                break

        rows_data = []
        for r in range(start_row, len(df_raw)):
            il_val = str(df_raw.iloc[r, 1]).strip() if df_raw.shape[1] > 1 else ""
            unite_val = str(df_raw.iloc[r, 2]).strip() if df_raw.shape[1] > 2 else ""
            if not il_val or il_val.lower() in ['nan', 'none', ''] or not unite_val or unite_val.lower() in ['nan', 'none', '']:
                continue

            gost_val = temiz_sayi_al(df_raw.iloc[r, 3] if df_raw.shape[1] > 3 else 0, 0.0)
            frek_val = temiz_sayi_al(df_raw.iloc[r, 4] if df_raw.shape[1] > 4 else 1, 1.0)
            net_val = temiz_sayi_al(df_raw.iloc[r, 5] if df_raw.shape[1] > 5 else 100, 100.0)
            endeks_raw = temiz_sayi_al(df_raw.iloc[r, 6] if df_raw.shape[1] > 6 else 1, 1.0)
            endeks_val = endeks_raw / 100.0 if endeks_raw > 1.5 else endeks_raw

            rows_data.append({
                'İl': il_val,
                'Ünite': unite_val,
                'Günlük Gösterim': gost_val,
                'Frekans': frek_val,
                'Network Adedi': net_val,
                'Endeks': endeks_val
            })

        df_gost = pd.DataFrame(rows_data)

        nufus_dict = {
            "İstanbul": 15754053, "Ankara": 5910320, "İzmir": 4504185, 
            "Bursa": 3263011, "Antalya": 2777677, "Türkiye": 86920168
        }
        sure_dict = {
            "Durak Raket CLP": 7, "Billboard": 7, "Afiş Değiştiricili Megalight": 7,
            "Megalight": 7, "Üst Geçit Alınlık": 15, "Giantboard": 10,
            "Elektrik Direği Banner": 14, "Avm Dış Led Ekran": 7, "Dijital Raket": 7,
            "Dijital Ekran": 7, "Toplu Taşıma Ekran": 7, "Tramvay Raket CLP": 7, "Raket CLP": 7
        }

        for c in range(5, df_raw.shape[1]):
            col_txt = " ".join([str(v) for v in df_raw.iloc[:, c].dropna().values])
            if "Nüfus" in col_txt:
                for r in range(start_row - 1, len(df_raw)):
                    il_c = str(df_raw.iloc[r, c-1]).strip()
                    nuf_val = temiz_sayi_al(df_raw.iloc[r, c], None)
                    if il_c and nuf_val is not None and il_c.lower() != 'nan':
                        nufus_dict[il_c] = nuf_val

            if "Kullanım Süresi" in col_txt:
                for r in range(start_row - 1, len(df_raw)):
                    u_c = str(df_raw.iloc[r, c-2] if c>=2 else df_raw.iloc[r, c-1]).strip()
                    sure_val = temiz_sayi_al(df_raw.iloc[r, c], None)
                    if u_c and sure_val is not None and u_c.lower() != 'nan':
                        sure_dict[u_c] = sure_val

        tr_nufus = float(nufus_dict.get("Türkiye", 86920168))
        ozel_iller = [k for k in nufus_dict.keys() if k not in ["Türkiye", "Anadolu İlleri", "TR", "Genel"]]
        ozel_toplam = sum(nufus_dict[k] for k in ozel_iller)
        kalan_il = max(1, 81 - len(ozel_iller))
        anadolu_ort = round(max(0, tr_nufus - ozel_toplam) / kalan_il)
        nufus_dict["Anadolu İlleri"] = float(anadolu_ort)

        return df_gost, nufus_dict, sure_dict, tr_nufus
    except Exception as e:
        st.error(f"Veri yükleme hatası: {e}")
        return None, {}, {}, 86920168

# --- 3. SESSION STATE ---
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "simulasyon"

if "sim_rows" not in st.session_state:
    st.session_state.sim_rows = []

if "arsiv_rows" not in st.session_state:
    st.session_state.arsiv_rows = []

# --- 4. YAN PANEL (SIDEBAR) ---
st.sidebar.markdown(f"**👤 Giriş Yapan:** `{st.session_state.username}`")
if st.sidebar.button("🚪 Çıkış Yap"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Veri & Harita Ayarları")

veri_kaynagi = st.sidebar.radio("Veri Kaynağı:", ["Yerel Excel (OUTDOOR.xlsx)", "Google Sheets (Canlı)"])
if veri_kaynagi == "Google Sheets (Canlı)":
    sheet_url = st.sidebar.text_input("Google Sheets Linki:", "")
    df_gost, nufus_dict, sure_dict, TR_TOTAL_NUFUS = veriyi_yukle(sheet_url)
else:
    df_gost, nufus_dict, sure_dict, TR_TOTAL_NUFUS = veriyi_yukle("OUTDOOR.xlsx")

looker_url = st.sidebar.text_input(
    "🗺️ Looker Studio Harita Embed Linki:",
    placeholder="https://lookerstudio.google.com/embed/reporting/..."
)

# --- 5. RAPOR OLUŞTURMA YARDIMCISI ---
def generate_html_report(df_to_export, report_title, is_arsiv=False):
    if is_arsiv:
        table_headers = "<th>Yıl</th><th>Dönem</th><th>Marka</th><th>Kampanya</th><th>Mecra</th><th>Ünite</th><th>İl</th><th>Süre</th><th>Periyod</th><th>Adet</th><th>Toplam Gösterim</th><th>Frekans</th><th>Erişim</th><th>İl Nüfusu</th><th>TR Nüfusu</th><th>TR Erişim %</th><th>TR GRP</th>"
        table_rows_html = "".join([
            f"<tr><td>{r['Yıl']}</td><td>{r['Dönem (Ay)']}</td><td>{r['Marka']}</td><td>{r['Kampanya Adı']}</td><td>{r['Mecra Adı']}</td><td>{r['Ünite']}</td><td>{r['İl']}</td><td>{r['Süre (Gün)']}</td><td>{r['Periyod']}</td><td>{r['Adet']}</td><td>{r['Toplam Gösterim']:,}</td><td>{r['Frekans']}</td><td>{r['Erişim (Kişi)']:,}</td><td>{r['İl Nüfusu']:,}</td><td>{r['TR Nüfusu']:,}</td><td>%{r['TR Erişim %']:.2f}</td><td>{r['TR GRP']:.2f}</td></tr>"
            for _, r in df_to_export.iterrows()
        ])
    else:
        table_headers = "<th>Ünite</th><th>İl</th><th>Süre</th><th>Periyod</th><th>Adet</th><th>Toplam Gösterim</th><th>Frekans</th><th>Erişim</th><th>İl Nüfusu</th><th>TR Nüfusu</th><th>TR Erişim %</th><th>TR GRP</th>"
        table_rows_html = "".join([
            f"<tr><td>{r['Ünite']}</td><td>{r['İl']}</td><td>{r['Süre (Gün)']}</td><td>{r['Periyod']}</td><td>{r['Adet']}</td><td>{r['Toplam Gösterim']:,}</td><td>{r['Frekans']}</td><td>{r['Erişim (Kişi)']:,}</td><td>{r['İl Nüfusu']:,}</td><td>{r['TR Nüfusu']:,}</td><td>%{r['TR Erişim %']:.2f}</td><td>{r['TR GRP']:.2f}</td></tr>"
            for _, r in df_to_export.iterrows()
        ])

    toplam_gos = df_to_export["Toplam Gösterim"].sum()
    toplam_grp = round(df_to_export["TR GRP"].sum(), 2)
    kapsanan_il = df_to_export["İl"].nunique()
    kapsanan_nufus = sum(nufus_dict.get(il, 719000) for il in df_to_export["İl"].unique())
    maks_erisim = round((kapsanan_nufus / TR_TOTAL_NUFUS) * 100, 1)

    looker_section = ""
    if looker_url:
        looker_section = f"""
        <div style="margin-top: 30px; background: #131b2e; border: 1px solid #1f293d; border-radius: 10px; padding: 20px;">
            <h3 style="color: #38bdf8; margin-bottom: 15px;">🗺️ Kampanya Harita ve Lokasyon Paneli</h3>
            <iframe src="{looker_url}" width="100%" height="560" frameborder="0" style="border:0; border-radius: 8px;" allowfullscreen></iframe>
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>{report_title}</title>
    <style>
        body {{ background-color: #090d16; color: #e2e8f0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 30px; line-height: 1.5; }}
        .kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 25px; }}
        .kpi-card {{ background: #131b2e; border: 1px solid #1f293d; border-radius: 10px; padding: 20px; text-align: center; }}
        table {{ width: 100%; border-collapse: collapse; text-align: center; font-size: 13px; margin-top: 20px; }}
        th {{ background: #1e293b; color: #38bdf8; padding: 12px; border: 1px solid #1f293d; }}
        td {{ padding: 10px; border: 1px solid #1f293d; color: #cbd5e1; }}
        tr:nth-child(even) {{ background: rgba(255,255,255,0.02); }}
        .footer-note {{ text-align: center; color: #64748b; font-size: 13px; margin-top: 40px; padding-top: 20px; border-top: 1px solid #1e293b; }}
    </style>
</head>
<body>
    <h1 style="color: #f1f5f9;">📊 {report_title}</h1>
    <div class="kpi-grid">
        <div class="kpi-card"><div style="font-size: 12px; color: #94a3b8;">TOPLAM GÖSTERİM</div><div style="font-size: 24px; font-weight: bold; color: #4ade80;">{toplam_gos:,}</div></div>
        <div class="kpi-card"><div style="font-size: 12px; color: #94a3b8;">TOPLAM TR GRP</div><div style="font-size: 24px; font-weight: bold; color: #38bdf8;">{toplam_grp:.2f}</div></div>
        <div class="kpi-card"><div style="font-size: 12px; color: #94a3b8;">KAPSASANAN İL</div><div style="font-size: 24px; font-weight: bold; color: #c084fc;">{kapsanan_il} İl</div></div>
        <div class="kpi-card"><div style="font-size: 12px; color: #94a3b8;">MAKS. TR ERİŞİMİ</div><div style="font-size: 24px; font-weight: bold; color: #facc15;">%{maks_erisim}</div></div>
    </div>
    <table>
        <thead><tr>{table_headers}</tr></thead>
        <tbody>{table_rows_html}</tbody>
    </table>
    {looker_section}
    <div class="footer-note">📌 CAFAS verileri dikkate alınarak hesaplanmıştır.</div>
</body>
</html>"""

# --- 6. ÜST GEÇİŞ BUTONLARI ---
st.title("⚡ OOH MEDYA PLANLAMA & SİMÜLASYON MERKEZİ")

col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    btn_type1 = "primary" if st.session_state.active_tab == "simulasyon" else "secondary"
    if st.button("📊 Anlık Hesaplama & Simülatör", type=btn_type1, use_container_width=True):
        st.session_state.active_tab = "simulasyon"
        st.rerun()

with col_btn2:
    btn_type2 = "primary" if st.session_state.active_tab == "arsiv" else "secondary"
    if st.button("📁 Kampanya Yönetimi & Yıllık Arşiv", type=btn_type2, use_container_width=True):
        st.session_state.active_tab = "arsiv"
        st.rerun()

st.markdown("---")

# ==========================================
# 1. SEKME: ANLIK HESAPLAMA & SİMÜLATÖR
# ==========================================
if st.session_state.active_tab == "simulasyon":
    if df_gost is not None and not df_gost.empty:
        st.markdown("### 📝 Yeni Kampanya Simülasyon Planı Oluştur")
        
        c1, c2, c3, c4, c5 = st.columns([2, 2, 1, 1, 1])
        with c1:
            il_listesi = sorted(list(set(df_gost['İl'].tolist())))
            secilen_il = st.selectbox("📍 İl Seçin:", il_listesi, key="sim_il")
        with c2:
            uniteler = sorted(list(set(df_gost[df_gost['İl'] == secilen_il]['Ünite'].tolist())))
            secilen_unite = st.selectbox("🎯 Ünite Seçin:", uniteler, key="sim_unite")
            baz_sure = sure_dict.get(secilen_unite, 7.0)
        with c3:
            periyod_val = st.number_input("⏱️ Periyod:", min_value=0.5, max_value=20.0, value=1.0, step=0.5, key="sim_periyod")
            hesaplanan_sure = int(round(baz_sure * periyod_val))
        with c4:
            sure_val = st.number_input("📅 Süre (Gün):", min_value=1, value=hesaplanan_sure, key="sim_sure")
            if sure_val != hesaplanan_sure:
                periyod_val = round(sure_val / baz_sure, 2) if baz_sure > 0 else 1.0
        with c5:
            adet_val = st.number_input("🔢 Adet:", min_value=1, value=100, step=10, key="sim_adet")

        if st.button("➕ Simülasyon Satırını Plana Ekle", use_container_width=True):
            m_gost = df_gost[(df_gost['İl'] == secilen_il) & (df_gost['Ünite'] == secilen_unite)]
            gunluk_gost = float(m_gost['Günlük Gösterim'].values[0]) if not m_gost.empty else 0.0
            baz_frekans = float(m_gost['Frekans'].values[0]) if not m_gost.empty else 1.0
            network_adedi = float(m_gost['Network Adedi'].values[0]) if not m_gost.empty else 100.0
            endeks = float(m_gost['Endeks'].values[0]) if not m_gost.empty else 1.0

            if network_adedi > 0 and adet_val > 0 and periyod_val > 0:
                dinamik_frekans = baz_frekans * ((adet_val / network_adedi) ** 0.55) * endeks * (periyod_val ** 0.80)
            else:
                dinamik_frekans = 0.0

            il_nufus = float(nufus_dict.get(secilen_il, nufus_dict.get("Anadolu İlleri", 719000)))
            toplam_gosterim = gunluk_gost * sure_val * adet_val
            erisim_kisi = (toplam_gosterim / dinamik_frekans) if dinamik_frekans > 0 else 0
            erisim_pct_tr = (erisim_kisi / TR_TOTAL_NUFUS) * 100
            grp_tr = (toplam_gosterim / TR_TOTAL_NUFUS) * 100

            st.session_state.sim_rows.append({
                "Ünite": secilen_unite,
                "İl": secilen_il,
                "Süre (Gün)": sure_val,
                "Periyod": format_periyod(periyod_val),
                "Adet": adet_val,
                "Toplam Gösterim": int(toplam_gosterim),
                "Frekans": round(dinamik_frekans, 1),
                "Erişim (Kişi)": int(erisim_kisi),
                "İl Nüfusu": int(il_nufus),
                "TR Nüfusu": int(TR_TOTAL_NUFUS),
                "TR Erişim %": round(erisim_pct_tr, 2),
                "TR GRP": round(grp_tr, 2)
            })

        if st.session_state.sim_rows:
            df_sim = pd.DataFrame(st.session_state.sim_rows)
            st.markdown("---")
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            toplam_gos = df_sim["Toplam Gösterim"].sum()
            toplam_grp = round(df_sim["TR GRP"].sum(), 2)
            kapsanan_il = df_sim["İl"].nunique()
            kapsanan_nufus = sum(nufus_dict.get(il, 719000) for il in df_sim["İl"].unique())
            maks_erisim = round((kapsanan_nufus / TR_TOTAL_NUFUS) * 100, 1)

            kpi1.metric("📊 Toplam Gösterim", f"{toplam_gos:,}")
            kpi2.metric("🇹🇷 Toplam TR GRP", f"{toplam_grp:.2f}")
            kpi3.metric("🌐 Maks. TR Erişimi", f"%{maks_erisim}")
            kpi4.metric("📍 Kapsanan İl Sayısı", f"{kapsanan_il} İl")

            st.dataframe(df_sim.style.format({
                "Toplam Gösterim": "{:,}",
                "Erişim (Kişi)": "{:,}",
                "İl Nüfusu": "{:,}",
                "TR Nüfusu": "{:,}",
                "TR Erişim %": "%{:.2f}",
                "TR GRP": "{:.2f}",
                "Frekans": "{:.1f}"
            }), use_container_width=True)

            if looker_url:
                st.markdown("### 🗺️ Lokasyon Haritası (Looker Studio)")
                st.components.v1.html(
                    f'<iframe src="{looker_url}" width="100%" height="520" frameborder="0" style="border:0; border-radius: 8px;" allowfullscreen></iframe>',
                    height=540
                )

            col_s1, col_s2 = st.columns([1, 4])
            with col_s1:
                if st.button("🧹 Simülasyonu Temizle"):
                    st.session_state.sim_rows = []
                    st.rerun()
            with col_s2:
                sim_html = generate_html_report(df_sim, "OOH Medya Simülasyon Raporu", is_arsiv=False)
                st.download_button(
                    label="📥 Harita Entegreli HTML Raporu Al",
                    data=sim_html,
                    file_name="OOH_Simulasyon_Raporu.html",
                    mime="text/html",
                    use_container_width=True
                )

# ==========================================
# 2. SEKME: KAMPANYA YÖNETİMİ & YILLIK ARŞİV
# ==========================================
elif st.session_state.active_tab == "arsiv":
    st.markdown("### 📝 Yeni Kampanya Satırı Ekle")
    
    if df_gost is not None and not df_gost.empty:
        il_listesi = sorted(list(set(df_gost['İl'].tolist())))
        
        k1, k2, k3, k4, k5 = st.columns([1, 1.2, 1.5, 1.5, 1.2])
        with k1:
            a_yil = st.number_input("Yıl:", min_value=2020, max_value=2035, value=2026, step=1, key="ars_yil")
        with k2:
            aylar = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
            a_donem = st.selectbox("Dönem:", aylar, index=0, key="ars_donem")
        with k3:
            a_marka_in = st.text_input("Marka:", placeholder="Örn: Vodafone", key="ars_marka")
            a_marka = a_marka_in.strip() if a_marka_in.strip() else "Marka"
        with k4:
            a_kampanya_in = st.text_input("Kampanya:", placeholder="Örn: Yaz Kampanyası", key="ars_kampanya")
            a_kampanya = a_kampanya_in.strip() if a_kampanya_in.strip() else "Kampanya Adı"
        with k5:
            a_mecra_in = st.text_input("Mecra:", placeholder="Örn: Ströer", key="ars_mecra")
            a_mecra = a_mecra_in.strip() if a_mecra_in.strip() else "Ströer"

        k6, k7, k8, k9, k10, k11 = st.columns([1.5, 2, 1, 1, 1, 1.2])
        with k6:
            a_il = st.selectbox("İl:", il_listesi, key="ars_il")
        with k7:
            a_uniteler = sorted(list(set(df_gost[df_gost['İl'] == a_il]['Ünite'].tolist())))
            a_unite = st.selectbox("Ünite:", a_uniteler, key="ars_unite")
            baz_sure_a = sure_dict.get(a_unite, 7.0)
        with k8:
            a_periyod = st.number_input("Periyod:", min_value=0.5, max_value=20.0, value=1.0, step=0.5, key="ars_per")
            hesap_sure_a = int(round(baz_sure_a * a_periyod))
        with k9:
            a_sure = st.number_input("Süre:", min_value=1, value=hesap_sure_a, key="ars_sure")
            if a_sure != hesap_sure_a:
                a_periyod = round(a_sure / baz_sure_a, 2) if baz_sure_a > 0 else 1.0
        with k10:
            a_adet = st.number_input("Adet:", min_value=1, value=100, step=10, key="ars_adet")
        with k11:
            st.markdown("<br>", unsafe_allow_html=True)
            ekle_btn = st.button("➕ Ekle", use_container_width=True, type="primary")

        if ekle_btn:
            m_gost = df_gost[(df_gost['İl'] == a_il) & (df_gost['Ünite'] == a_unite)]
            gunluk_gost = float(m_gost['Günlük Gösterim'].values[0]) if not m_gost.empty else 0.0
            baz_frekans = float(m_gost['Frekans'].values[0]) if not m_gost.empty else 1.0
            network_adedi = float(m_gost['Network Adedi'].values[0]) if not m_gost.empty else 100.0
            endeks = float(m_gost['Endeks'].values[0]) if not m_gost.empty else 1.0

            if network_adedi > 0 and a_adet > 0 and a_periyod > 0:
                dinamik_frekans = baz_frekans * ((a_adet / network_adedi) ** 0.55) * endeks * (a_periyod ** 0.80)
            else:
                dinamik_frekans = 0.0

            il_nufus = float(nufus_dict.get(a_il, nufus_dict.get("Anadolu İlleri", 719000)))
            toplam_gosterim = gunluk_gost * a_sure * a_adet
            erisim_kisi = (toplam_gosterim / dinamik_frekans) if dinamik_frekans > 0 else 0
            erisim_pct_tr = (erisim_kisi / TR_TOTAL_NUFUS) * 100
            grp_tr = (toplam_gosterim / TR_TOTAL_NUFUS) * 100

            st.session_state.arsiv_rows.append({
                "Yıl": int(a_yil),
                "Dönem (Ay)": a_donem,
                "Marka": a_marka,
                "Kampanya Adı": a_kampanya,
                "Mecra Adı": a_mecra,
                "Ünite": a_unite,
                "İl": a_il,
                "Süre (Gün)": a_sure,
                "Periyod": format_periyod(a_periyod),
                "Adet": a_adet,
                "Toplam Gösterim": int(toplam_gosterim),
                "Frekans": round(dinamik_frekans, 1),
                "Erişim (Kişi)": int(erisim_kisi),
                "İl Nüfusu": int(il_nufus),
                "TR Nüfusu": int(TR_TOTAL_NUFUS),
                "TR Erişim %": round(erisim_pct_tr, 2),
                "TR GRP": round(grp_tr, 2)
            })
            st.success(f"✅ `{a_marka} - {a_kampanya}` satırı başarıyla eklendi!")

        if st.session_state.arsiv_rows:
            df_arsiv = pd.DataFrame(st.session_state.arsiv_rows)
            st.markdown("---")
            
            ak1, ak2, ak3, ak4 = st.columns(4)
            toplam_gos_a = df_arsiv["Toplam Gösterim"].sum()
            toplam_grp_a = round(df_arsiv["TR GRP"].sum(), 2)
            kapsanan_il_a = df_arsiv["İl"].nunique()
            kapsanan_nufus_a = sum(nufus_dict.get(il, 719000) for il in df_arsiv["İl"].unique())
            maks_erisim_a = round((kapsanan_nufus_a / TR_TOTAL_NUFUS) * 100, 1)

            ak1.metric("📊 Toplam Gösterim", f"{toplam_gos_a:,}")
            ak2.metric("🇹🇷 Toplam TR GRP", f"{toplam_grp:.2f}")
            ak3.metric("🌐 Maks. TR Erişimi", f"%{maks_erisim_a}")
            ak4.metric("📍 Kapsanan İl", f"{kapsanan_il_a} İl")

            st.dataframe(df_arsiv.style.format({
                "Toplam Gösterim": "{:,}",
                "Erişim (Kişi)": "{:,}",
                "İl Nüfusu": "{:,}",
                "TR Nüfusu": "{:,}",
                "TR Erişim %": "%{:.2f}",
                "TR GRP": "{:.2f}",
                "Frekans": "{:.1f}",
                "Adet": "{:,}"
            }), use_container_width=True)

            if looker_url:
                st.markdown("### 🗺️ Lokasyon Haritası (Looker Studio)")
                st.components.v1.html(
                    f'<iframe src="{looker_url}" width="100%" height="520" frameborder="0" style="border:0; border-radius: 8px;" allowfullscreen></iframe>',
                    height=540
                )

            col_a1, col_a2 = st.columns([1, 4])
            with col_a1:
                if st.button("🧹 Arşiv Listesini Temizle"):
                    st.session_state.arsiv_rows = []
                    st.rerun()
            with col_a2:
                arsiv_html = generate_html_report(df_arsiv, "OOH Kampanya Arşiv & Yönetim Raporu", is_arsiv=True)
                st.download_button(
                    label="📥 Harita Entegreli HTML Raporu Al",
                    data=arsiv_html,
                    file_name="OOH_Kampanya_Arsiv_Raporu.html",
                    mime="text/html",
                    use_container_width=True
                )

# --- 7. DİPNOT (FOOTER) ---
st.markdown("<div class='footer-text'>📌 CAFAS verileri dikkate alınarak hesaplanmıştır.</div>", unsafe_allow_html=True)

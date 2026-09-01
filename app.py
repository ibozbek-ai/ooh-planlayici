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
    .panel-card {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 700;
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

if "past_rows" not in st.session_state:
    st.session_state.past_rows = []

# --- 4. YAN PANEL (SIDEBAR) ---
st.sidebar.markdown(f"**Hoş geldin, `{st.session_state.username}`**")
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

# --- 5. ÜST GEÇİŞ BUTONLARI (EXE DÜZENİ) ---
st.title("⚡ OOH Medya Planlama & Kampanya Yönetimi")

col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    btn_type1 = "primary" if st.session_state.active_tab == "simulasyon" else "secondary"
    if st.button("📊 Yeni Kampanya Simülatörü", type=btn_type1, use_container_width=True):
        st.session_state.active_tab = "simulasyon"
        st.rerun()

with col_btn2:
    btn_type2 = "primary" if st.session_state.active_tab == "gecmis" else "secondary"
    if st.button("📁 Geçmiş Kampanya / Manuel Veri Girişi", type=btn_type2, use_container_width=True):
        st.session_state.active_tab = "gecmis"
        st.rerun()

st.markdown("---")

# ==========================================
# 1. SEKME: YENİ KAMPANYA SİMÜLATÖRÜ
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

            col_b1, col_b2 = st.columns([1, 4])
            with col_b1:
                if st.button("🧹 Simülasyonu Temizle"):
                    st.session_state.sim_rows = []
                    st.rerun()

# ==========================================
# 2. SEKME: GEÇMİŞ KAMPANYA MANUEL GİRİŞİ (EXE DÜZENİ)
# ==========================================
elif st.session_state.active_tab == "gecmis":
    st.markdown("### 📂 Geçmiş Kampanya / Manuel Veri Giriş Paneli")
    st.markdown("<p style='color: #94a3b8; font-size: 13px;'>Gerçekleşmiş veya arşivdeki kampanya metriklerini doğrudan elle girip analiz edin.</p>", unsafe_allow_html=True)
    
    g1, g2, g3 = st.columns(3)
    with g1:
        p_kampanya = st.text_input("🏷️ Kampanya / Marka Adı:", value="Örnek Kampanya", key="past_name")
        p_il = st.selectbox("📍 Kampanya İli:", sorted(list(set(df_gost['İl'].tolist()))) if df_gost is not None else ["İstanbul"], key="past_il")
    with g2:
        p_unite = st.selectbox("🎯 Kullanılan Ünite:", sorted(list(set(df_gost['Ünite'].tolist()))) if df_gost is not None else ["Durak Raket CLP"], key="past_unite")
        p_adet = st.number_input("🔢 Adet:", min_value=1, value=50, step=5, key="past_adet")
    with g3:
        p_gosterim = st.number_input("📊 Toplam Gösterim (Gerçekleşen):", min_value=0, value=5000000, step=50000, key="past_gos")
        p_grp = st.number_input("🇹🇷 Gerçekleşen GRP:", min_value=0.0, value=15.50, step=0.5, format="%.2f", key="past_grp")

    if st.button("➕ Geçmiş Kampanyayı Kaydet & Listeye Ekle", use_container_width=True):
        st.session_state.past_rows.append({
            "Kampanya Adı": p_kampanya,
            "İl": p_il,
            "Ünite": p_unite,
            "Adet": p_adet,
            "Toplam Gösterim": int(p_gosterim),
            "Gerçekleşen GRP": p_grp
        })
        st.success(f"✅ `{p_kampanya}` satırı başarıyla eklendi!")

    if st.session_state.past_rows:
        df_past = pd.DataFrame(st.session_state.past_rows)
        st.markdown("---")
        st.markdown("### 📋 Geçmiş Kampanyalar Analiz Tablosu")

        pk1, pk2, pk3 = st.columns(3)
        pk1.metric("📊 Toplam Gerçekleşen Gösterim", f"{df_past['Toplam Gösterim'].sum():,}")
        pk2.metric("🇹🇷 Kümülatif GRP", f"{df_past['Gerçekleşen GRP'].sum():.2f}")
        pk3.metric("📍 Kapsanan İl Sayısı", f"{df_past['İl'].nunique()} İl")

        st.dataframe(df_past.style.format({
            "Toplam Gösterim": "{:,}",
            "Gerçekleşen GRP": "{:.2f}",
            "Adet": "{:,}"
        }), use_container_width=True)

        if looker_url:
            st.markdown("### 🗺️ Lokasyon Haritası (Looker Studio)")
            st.components.v1.html(
                f'<iframe src="{looker_url}" width="100%" height="520" frameborder="0" style="border:0; border-radius: 8px;" allowfullscreen></iframe>',
                height=540
            )

        if st.button("🧹 Geçmiş Kampanya Listesini Temizle"):
            st.session_state.past_rows = []
            st.rerun()

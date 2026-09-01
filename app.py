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
            col_txt = " ".join(

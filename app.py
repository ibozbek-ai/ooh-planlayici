import streamlit as st
import pandas as pd
import io
import json
import urllib.request
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Sayfa Yapılandırması
st.set_page_config(
    page_title="OOH Planlama Stüdyosu | Medya Yönetim Merkezi",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CANLI & ULTRA-PREMIUM DYNAMIC CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');

    html, body, .stApp, p, label, input, select, textarea, span, div {
        font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    span[data-testid="stIconMaterial"], .material-symbols-rounded, [class*="material-symbols"] {
        font-family: 'Material Symbols Rounded', 'Material Icons' !important;
    }

    .stApp {
        background: radial-gradient(circle at 50% -10%, #1e3a8a 0%, #0f172a 50%, #030712 100%) !important;
        color: #f8fafc !important;
        font-size: 15px !important;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #172554 0%, #090d16 100%) !important;
        border-right: 1.5px solid rgba(56, 189, 248, 0.3) !important;
    }

    .app-header {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 24px;
        padding-bottom: 18px;
        border-bottom: 2px solid rgba(56, 189, 248, 0.35);
    }
    .app-header h1 {
        font-size: 32px !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
        background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }

    div[data-testid="stWidgetLabel"] p {
        font-size: 15px !important;
        font-weight: 700 !important;
        color: #38bdf8 !important;
        margin-bottom: 6px !important;
    }

    div[data-baseweb="input"], div[data-baseweb="select"] {
        border-radius: 12px !important;
        background-color: #172554 !important;
        border: 2px solid #3b82f6 !important;
        min-height: 52px !important;
        box-shadow: 0 6px 16px rgba(59, 130, 246, 0.25) !important;
    }
    div[data-baseweb="input"]:focus-within, div[data-baseweb="select"]:focus-within {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 0 4px rgba(56, 189, 248, 0.4) !important;
    }
    div[data-baseweb="input"] input {
        font-size: 16px !important;
        font-weight: 600 !important;
        color: #ffffff !important;
    }

    /* --- GİRİŞ EKRANI (LOGIN) İÇİN SABİT ORTALANMIŞ KOMPAKT KUTU --- */
    div.stForm:has(input[aria-label*="Şifre"]) {
        max-width: 440px !important;
        width: 100% !important;
        margin: 50px auto !important;
        background: linear-gradient(145deg, #131f3b 0%, #0d1529 100%) !important;
        border: 2px solid rgba(56, 189, 248, 0.4) !important;
        border-radius: 20px !important;
        padding: 35px 30px !important;
        box-shadow: 0 25px 50px rgba(0,0,0,0.7) !important;
    }

    /* --- KAMPANYA YÖNETİMİ FORMU (GENİŞ VE FERAH) --- */
    div.stForm:not(:has(input[aria-label*="Şifre"])) {
        max-width: 100% !important;
        width: 100% !important;
        margin: 20px 0 30px 0 !important;
        background: linear-gradient(145deg, #131f3b 0%, #0d1529 100%) !important;
        border: 2px solid rgba(56, 189, 248, 0.35) !important;
        border-radius: 20px !important;
        padding: 30px !important;
        box-shadow: 0 20px 45px rgba(0,0,0,0.6) !important;
    }

    div.stForm:not(:has(input[aria-label*="Şifre"])) div[data-baseweb="input"], 
    div.stForm:not(:has(input[aria-label*="Şifre"])) div[data-baseweb="select"] {
        background-color: #172554 !important;
        border: 2px solid #3b82f6 !important;
        min-height: 54px !important;
    }

    /* --- KAMPANYA FORSU BÜTÇE KUTUSU ÖZEL ZÜMRÜT YEŞİLİ --- */
    div.stForm:not(:has(input[aria-label*="Şifre"])) div:nth-last-of-type(2) div[data-baseweb="input"] {
        background: linear-gradient(145deg, #064e3b 0%, #022c22 100%) !important;
        border: 2.5px solid #34d399 !important;
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4) !important;
    }
    div.stForm:not(:has(input[aria-label*="Şifre"])) div:nth-last-of-type(2) div[data-baseweb="input"] input {
        color: #34d399 !important;
        font-weight: 800 !important;
        font-size: 18px !important;
    }

    .stButton>button, div[data-testid="stPopover"]>button {
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        height: 52px !important;
        padding: 0 24px !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        white-space: nowrap !important;
    }

    .stButton>button:hover, div[data-testid="stPopover"]>button:hover {
        transform: translateY(-3px) scale(1.02) !important;
        cursor: pointer !important;
    }

    .tab-btn-active > button {
        background: linear-gradient(135deg, #2563eb 0%, #06b6d4 100%) !important;
        color: #ffffff !important;
        border: 2px solid #38bdf8 !important;
        box-shadow: 0 8px 25px rgba(6, 182, 212, 0.5) !important;
    }

    .tab-btn-inactive > button {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%) !important;
        color: #94a3b8 !important;
        border: 2px solid #334155 !important;
    }
    .tab-btn-inactive > button:hover {
        background: linear-gradient(135deg, #334155 0%, #1e293b 100%) !important;
        color: #ffffff !important;
        border-color: #38bdf8 !important;
    }

    .brand-folder-btn > button {
        background: linear-gradient(145deg, #1e3a8a 0%, #0f172a 100%) !important;
        color: #38bdf8 !important;
        border: 2px solid rgba(56, 189, 248, 0.4) !important;
        border-radius: 16px !important;
        height: 84px !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.4) !important;
        white-space: pre-line !important;
        line-height: 1.4 !important;
    }
    .brand-folder-btn > button:hover {
        background: linear-gradient(145deg, #2563eb 0%, #172554 100%) !important;
        border-color: #38bdf8 !important;
        box-shadow: 0 12px 30px rgba(56, 189, 248, 0.5) !important;
        transform: translateY(-4px) !important;
        color: #ffffff !important;
    }

    .save-box {
        background: linear-gradient(145deg, #1e3a8a 0%, #0f172a 100%);
        border: 2px solid rgba(56, 189, 248, 0.4);
        border-radius: 18px;
        padding: 28px;
        margin-top: 30px;
        box-shadow: 0 12px 35px rgba(0,0,0,0.5);
    }

    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #1e3a8a 0%, #0f172a 100%) !important;
        border: 2px solid rgba(56, 189, 248, 0.4) !important;
        border-radius: 16px !important;
        padding: 20px 24px !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4) !important;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 14px !important;
        font-weight: 700 !important;
        color: #38bdf8 !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 32px !important;
        font-weight: 800 !important;
        color: #4ade80 !important;
    }

    .table-responsive-box {
        width: 100%;
        overflow-x: auto;
        margin: 22px 0 32px 0;
        border: 2px solid rgba(56, 189, 248, 0.3);
        border-radius: 16px;
        background-color: #0f172a;
        box-shadow: 0 12px 35px rgba(0,0,0,0.5);
    }
    .custom-ooh-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 15px;
    }
    .custom-ooh-table th {
        background: linear-gradient(180deg, #1e3a8a 0%, #172554 100%);
        color: #38bdf8;
        padding: 18px 16px;
        text-align: center !important;
        vertical-align: middle;
        font-weight: 700;
        font-size: 14.5px;
        border-bottom: 2px solid #3b82f6;
        white-space: nowrap;
    }
    .custom-ooh-table td {
        padding: 15px 16px;
        text-align: center !important;
        vertical-align: middle;
        color: #f1f5f9;
        border-bottom: 1px solid #1e3a8a;
        white-space: nowrap;
    }
    .custom-ooh-table tbody tr:hover {
        background-color: rgba(56, 189, 248, 0.12);
    }

    .corporate-footer {
        text-align: center;
        color: #94a3b8;
        font-size: 14px;
        font-weight: 600;
        margin-top: 55px;
        padding-top: 22px;
        border-top: 2px solid rgba(56, 189, 248, 0.2);
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
    st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; font-weight: 800; font-size: 34px; color: #38bdf8; margin-bottom: 6px;'>OOH Planlama Stüdyosu</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 16px; margin-bottom: 15px; font-weight: 600;'>Kurumsal Medya Planlama & Simülasyon Portalı</p>", unsafe_allow_html=True)
    
    with st.form("login_box_form"):
        user = st.text_input("Kullanıcı Adı:", placeholder="Kullanıcı adınızı giriniz")
        pwd = st.text_input("Şifre:", type="password", placeholder="••••••••")
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        submit = st.form_submit_button("Güvenli Giriş Yap", use_container_width=True, type="primary")
        if submit:
            if user == KULLANICI_ADI and pwd == KULLANICI_SIFRE:
                st.session_state.logged_in = True
                st.session_state.username = user
                st.rerun()
            else:
                st.error("Kullanıcı adı veya şifre hatalı!")
                
    st.markdown("<div class='corporate-footer'>CAFAS verileri dikkate alınarak geliştirilmiştir.</div>", unsafe_allow_html=True)

if not st.session_state.logged_in:
    login_form()
    st.stop()

# --- 2. 44 MÜŞTERİ MARKASI LİSTESİ ---
MASTER_BRANDS = [
    "BİM", "Casper", "Hayat", "Kumtel", "Muratbey", "Namet", "Maret", "Kale",
    "File Market", "Kervan", "Kastamonu Entegre", "Biota", "Daikin", "Brita", "Doğanlar Holding",
    "Paribu", "Koton", "Geberit", "Yolcu360", "Weber", "Saint-Gobain", "Pasifik Holding",
    "Turna.com", "Herbalife", "Kopaş Kozmetik", "KFC", "Makarnam", "Pidem", "HD İskender",
    "Yataş", "Burgan Bank", "Milhans", "Çizmeci Time", "Hayat Finans", "Demant", "Siemens",
    "Pozitif", "Gloria Jean's", "Karnaval", "Bosch", "De'Longhi", "Braun", "Humm", "Evolvia"
]

# --- 3. GOOGLE SHEETS ENTEGRASYONU ---
GSHEET_ID = "19XUBd2QxMj9ObOkqhJp9Ie-hjCDk-A2RarpoxdDP5y0"
GSHEET_XLSX_URL = f"https://docs.google.com/spreadsheets/d/{GSHEET_ID}/export?format=xlsx"

# --- 4. SAYI BİÇİMLENDİRME VE ÖZEL İL SAYIMI YARDIMCILARI ---
def tr_tam_sayi(val):
    try:
        n = int(round(float(val)))
        return f"{n:,}".replace(",", ".")
    except:
        return str(val)

def tr_ondalik(val, basamak=2):
    try:
        f = float(val)
        fmt = f"{f:,.{basamak}f}"
        return fmt.replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return str(val)

def format_periyod(val):
    try:
        f_val = float(val)
        if f_val.is_integer():
            return str(int(f_val))
        return tr_ondalik(f_val, 2)
    except:
        return str(val)

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

def tahmin_mecra(unite_str, il_str):
    u = str(unite_str).lower()
    i = str(il_str).lower()
    if "starbuck" in u or "starbuck" in i:
        return "Core Medya"
    elif "macfit" in u or "mac fit" in u or "macfit" in i or "mac fit" in i:
        return "Donanım Medya"
    elif "üni" in u or "uni" in u or "üniversite" in u:
        return "Üniversite Network"
    elif "istanbul" in i:
        return "İBB / Medya A.Ş."
    elif "ankara" in i or "izmir" in i:
        return "Kentvizyon"
    return "Kentvizyon"

STARBUCKS_ILLERI_SET = {
    "İstanbul", "Ankara", "İzmir", "Bursa", "Antalya", "Adana", "Eskişehir", "Kocaeli", "Gaziantep", 
    "Konya", "Mersin", "Muğla", "Aydın", "Denizli", "Samsun", "Kayseri", "Tekirdağ", "Balıkesir", 
    "Trabzon", "Sakarya", "Çanakkale", "Hatay", "Manisa", "Afyonkarahisar", "Isparta", "Edirne", 
    "Kütahya", "Sivas", "Malatya", "Kahramanmaraş", "Şanlıurfa", "Diyarbakır", "Zonguldak", "Yalova", 
    "Bolu", "Düzce", "Ordu", "Rize"
}

MACFIT_ILLERI_SET = {
    "İstanbul", "Ankara", "İzmir", "Bursa", "Antalya", "Adana", "Eskişehir", "Kocaeli", "Gaziantep", 
    "Konya", "Mersin", "Muğla", "Aydın", "Denizli", "Samsun", "Kayseri", "Tekirdağ", "Balıkesir", 
    "Sakarya", "Yalova"
}

UNI_ILLERI_SET = {
    "İstanbul", "Ankara", "İzmir", "Bursa", "Antalya", "Eskişehir", "Konya", "Trabzon", "Erzurum"
}

def get_il_nufusu(il_adi, nufus_dict):
    il_adi = str(il_adi).strip()
    if "starbuck" in il_adi.lower():
        return float(nufus_dict.get("Starbucks İlleri", 58150000))
    elif "macfit" in il_adi.lower() or "mac fit" in il_adi.lower():
        return float(nufus_dict.get("MacFit İlleri", 52274000))
    elif "üni" in il_adi.lower() or "uni" in il_adi.lower():
        return float(nufus_dict.get("Üni İlleri", 36462000))
    elif "anadolu" in il_adi.lower():
        val = float(nufus_dict.get("Anadolu İlleri", 719000))
        return val if val > 0 else 719000.0
    
    val = float(nufus_dict.get(il_adi, 0))
    if val <= 0:
        val = float(nufus_dict.get("Anadolu İlleri", 719000))
    return val if val > 0 else 719000.0

def hesapla_net_kapsama_metrikleri(df, nufus_dict, tr_total_nufus):
    if df is None or df.empty:
        return 0, 0.0

    kapsanan_tekil_iller = set()
    ozel_ag_nufuslari = []
    
    for _, r in df.iterrows():
        il_str = str(r.get('İl', '')).strip().lower()
        unite_str = str(r.get('Ünite', '')).strip().lower()

        if "starbuck" in il_str or "starbuck" in unite_str:
            kapsanan_tekil_iller.update(STARBUCKS_ILLERI_SET)
            ozel_ag_nufuslari.append(58150000)
        elif "macfit" in il_str or "mac fit" in il_str or "macfit" in unite_str or "mac fit" in unite_str:
            kapsanan_tekil_iller.update(MACFIT_ILLERI_SET)
            ozel_ag_nufuslari.append(52274000)
        elif "üni" in il_str or "uni" in il_str or "üniversite" in il_str or "üni" in unite_str or "uni" in unite_str:
            kapsanan_tekil_iller.update(UNI_ILLERI_SET)
            ozel_ag_nufuslari.append(36462000)
        elif "anadolu" in il_str:
            kapsanan_tekil_iller.add("Anadolu İlleri")
        else:
            kapsanan_tekil_iller.add(r['İl'])

    toplam_il_sayisi = min(81, len(kapsanan_tekil_iller))
    
    net_nufus = 0
    if ozel_ag_nufuslari and len(kapsanan_tekil_iller) <= 38:
        net_nufus = max(ozel_ag_nufuslari)
    else:
        for il in kapsanan_tekil_iller:
            net_nufus += get_il_nufusu(il, nufus_dict)
    
    maks_erisim_pct = min(100.0, round((net_nufus / tr_total_nufus) * 100, 1))
    return toplam_il_sayisi, maks_erisim_pct

# --- 5. EXCEL VERİ MOTORU ---
@st.cache_data
def yerel_exceli_yukle():
    try:
        excel_path = "OUTDOOR.xlsx"
        excel_obj = pd.ExcelFile(excel_path)
        sheet = 'Günlük Gösterim Sayıları' if 'Günlük Gösterim Sayıları' in excel_obj.sheet_names else excel_obj.sheet_names[0]
        df_raw = pd.read_excel(excel_path, sheet_name=sheet, header=None)

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

            if not il_val or il_val.lower() in ['nan', 'none', '', 'il', 'i̇l'] or not unite_val or unite_val.lower() in ['nan', 'none', '', 'ünite', 'unite']:
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
                'Network Adedi': int(round(net_val)),
                'Endeks': endeks_val
            })

        df_gost = pd.DataFrame(rows_data)

        nufus_dict = {
            "İstanbul": 15754053, "Ankara": 5910320, "İzmir": 4504185, 
            "Bursa": 3263011, "Antalya": 2777677, "Adana": 2274106, "Konya": 2320645,
            "Gaziantep": 2185982, "Kocaeli": 2102907, "Mersin": 1938389, "Diyarbakır": 1818133,
            "Hatay": 1544640, "Manisa": 1475716, "Kayseri": 1445495, "Samsun": 1377546,
            "Balıkesir": 1273519, "Tekirdağ": 1167059, "Aydın": 1161702, "Van": 1127612,
            "Trabzon": 824352, "Eskişehir": 915418, "Denizli": 1059082, "Sakarya": 1098115,
            "Muğla": 1066736, "Türkiye": 86920168, "Starbucks İlleri": 58150000,
            "MacFit İlleri": 52274000, "Üni İlleri": 36462000, "Anadolu İlleri": 719000
        }
        sure_dict = {
            "Durak Raket CLP": 7, "Billboard": 7, "Afiş Değiştiricili Megalight": 7,
            "Megalight": 7, "Üst Geçit Alınlık": 15, "Giantboard": 10,
            "Elektrik Direği Banner": 14, "Avm Dış Led Ekran": 7, "Dijital Raket": 7,
            "Dijital Ekran": 7, "Toplu Taşıma Ekran": 7, "Tramvay Raket CLP": 7, "Raket CLP": 7,
            "Üni Ekran": 7, "Üniversite Ekran": 7, "Starbucks Kasa Arkası Ekran": 7,
            "MacFit Ekran": 7
        }

        for c in range(5, df_raw.shape[1]):
            col_txt = " ".join([str(v) for v in df_raw.iloc[:, c].dropna().values])
            if "Nüfus" in col_txt:
                for r in range(start_row - 1, len(df_raw)):
                    il_c = str(df_raw.iloc[r, c-1] if c>=1 else "").strip()
                    nuf_val = temiz_sayi_al(df_raw.iloc[r, c], None)
                    if il_c and nuf_val is not None and il_c.lower() != 'nan' and nuf_val > 0:
                        nufus_dict[il_c] = nuf_val

            if "Kullanım Süresi" in col_txt or "Süre" in col_txt:
                for r in range(start_row - 1, len(df_raw)):
                    u_c = str(df_raw.iloc[r, c-2] if c>=2 else df_raw.iloc[r, c-1]).strip()
                    sure_val = temiz_sayi_al(df_raw.iloc[r, c], None)
                    if u_c and sure_val is not None and u_c.lower() != 'nan' and sure_val > 0:
                        sure_dict[u_c] = sure_val

        tr_nufus = float(nufus_dict.get("Türkiye", 86920168))
        if nufus_dict.get("Anadolu İlleri", 0) <= 0:
            nufus_dict["Anadolu İlleri"] = 719000.0

        return df_gost, nufus_dict, sure_dict, tr_nufus
    except Exception as e:
        st.error(f"Excel Okuma Hatası (OUTDOOR.xlsx): {e}")
        return None, {}, {}, 86920168

df_gost, nufus_dict, sure_dict, TR_TOTAL_NUFUS = yerel_exceli_yukle()

# --- 6. SESSION STATE ---
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "simulasyon"

if "sim_rows" not in st.session_state:
    st.session_state.sim_rows = []

if "arsiv_rows" not in st.session_state:
    st.session_state.arsiv_rows = []

if "selected_brand_folder" not in st.session_state:
    st.session_state.selected_brand_folder = None

if "selected_campaign_folder" not in st.session_state:
    st.session_state.selected_campaign_folder = None

if "sim_per" not in st.session_state:
    st.session_state.sim_per = 1.0
if "sim_sure" not in st.session_state:
    st.session_state.sim_sure = 7

if "ars_per" not in st.session_state:
    st.session_state.ars_per = 1.0
if "ars_sure" not in st.session_state:
    st.session_state.ars_sure = 7

# --- 7. YAN PANEL (SIDEBAR) ---
st.sidebar.markdown(f"**Giriş Yapan:** `{st.session_state.username}`")
if st.sidebar.button("Çıkış Yap"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("Sistem Ayarları")

if st.sidebar.button("Excel Verisini Yenile", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

looker_url = st.sidebar.text_input(
    "Looker Studio Harita Linki:",
    placeholder="https://lookerstudio.google.com/embed/reporting/..."
)

st.sidebar.markdown("---")
st.sidebar.caption("Geliştirici: İbrahim Özbek Arslan")

# --- 8. RAPOR OLUŞTURMA YARDIMCILARI (EXCEL & HTML) ---
def generate_excel_report(df_to_export, report_title, looker_link="", is_arsiv=False):
    output = io.BytesIO()
    df_excel = df_to_export.copy()
    
    if "TR Erişim %" in df_excel.columns:
        df_excel["TR Erişim %"] = df_excel["TR Erişim %"].apply(lambda v: temiz_sayi_al(v, 0.0) / 100.0)

    df_excel["Toplam Bütçe (TL)"] = None
    df_excel["CPR (TL)"] = None

    toplam_adet = int(df_to_export["Adet"].sum())
    toplam_gos = int(df_to_export["Toplam Gösterim"].sum())
    toplam_grp = float(round(df_to_export["TR GRP"].sum(), 2))
    kapsanan_il, maks_erisim = hesapla_net_kapsama_metrikleri(df_to_export, nufus_dict, TR_TOTAL_NUFUS)

    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        summary_df = pd.DataFrame([
            {"Metrik": "Rapor Başlığı", "Değer": str(report_title)},
            {"Metrik": "Geliştirici & Sistem", "Değer": "İbrahim Özbek Arslan | OOH Planlama Stüdyosu"},
            {"Metrik": "Toplam Adet", "Değer": toplam_adet},
            {"Metrik": "Toplam Gösterim", "Değer": toplam_gos},
            {"Metrik": "Toplam TR GRP", "Değer": toplam_grp},
            {"Metrik": "Kapsanan İl Sayısı", "Değer": f"{kapsanan_il} İl"},
            {"Metrik": "Maks. TR Erişimi", "Değer": float(round(maks_erisim / 100.0, 4))},
            {"Metrik": "Looker Studio Harita Linki", "Değer": str(looker_link) if looker_link else "Belirtilmedi"}
        ])
        
        summary_df.to_excel(writer, sheet_name='Özet KPI', index=False)
        df_excel.to_excel(writer, sheet_name='Medya Planı', index=False)
        
        wb = writer.book

        header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
        header_font = Font(name="Segoe UI", size=11, bold=True, color="38BDF8")

        total_fill = PatternFill(start_color="172554", end_color="172554", fill_type="solid")
        total_font = Font(name="Segoe UI", size=11, bold=True, color="38BDF8")

        alt_row_fill = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
        regular_font = Font(name="Segoe UI", size=10, color="0F172A")

        center_align = Alignment(horizontal="center", vertical="center")
        left_align = Alignment(horizontal="left", vertical="center")
        
        thin_border = Border(
            left=Side(style='thin', color='CBD5E1'),
            right=Side(style='thin', color='CBD5E1'),
            top=Side(style='thin', color='CBD5E1'),
            bottom=Side(style='thin', color='CBD5E1')
        )
        total_border = Border(
            top=Side(style='medium', color='38BDF8'),
            bottom=Side(style='double', color='38BDF8'),
            left=Side(style='thin', color='CBD5E1'),
            right=Side(style='thin', color='CBD5E1')
        )
        
        ws_sum = wb['Özet KPI']
        for row_idx, row in enumerate(ws_sum.iter_rows(), start=1):
            for cell in row:
                cell.border = thin_border
                cell.font = regular_font
                cell.alignment = left_align
                if row_idx > 1 and row_idx % 2 == 0:
                    cell.fill = alt_row_fill

        for cell in ws_sum[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = center_align

        for r in range(2, ws_sum.max_row + 1):
            lbl = str(ws_sum.cell(row=r, column=1).value or '').strip()
            val_cell = ws_sum.cell(row=r, column=2)
            if lbl == "Toplam Adet":
                val_cell.number_format = '#,##0'
            elif lbl == "Toplam Gösterim":
                val_cell.number_format = '#,##0'
            elif lbl == "Toplam TR GRP":
                val_cell.number_format = '#,##0.00'
            elif lbl == "Maks. TR Erişimi":
                val_cell.value = float(round(maks_erisim / 100.0, 4))
                val_cell.number_format = '0.0%'
        
        ws_plan = wb['Medya Planı']
        col_names = [cell.value for cell in ws_plan[1]]
        last_row = ws_plan.max_row

        grp_col_letter = get_column_letter(col_names.index("TR GRP") + 1)
        butce_col_letter = get_column_letter(col_names.index("Toplam Bütçe (TL)") + 1)

        for row in range(2, last_row + 1):
            is_alt = (row % 2 == 0)
            for col_idx, col_name in enumerate(col_names, start=1):
                cell = ws_plan.cell(row=row, column=col_idx)
                cell.border = thin_border
                cell.font = regular_font
                cell.alignment = center_align
                if is_alt:
                    cell.fill = alt_row_fill

                if col_name in ["Adet", "Toplam Gösterim", "Erişim (Kişi)", "İl Nüfusu", "TR Nüfusu"]:
                    cell.number_format = '#,##0'
                elif col_name in ["Frekans", "TR GRP"]:
                    cell.number_format = '#,##0.00'
                elif col_name in ["TR Erişim %"]:
                    cell.number_format = '0.00%'
                elif col_name == "Toplam Bütçe (TL)":
                    cell.number_format = '#,##0 ₺'
                elif col_name == "CPR (TL)":
                    cell.value = f'=IFERROR({butce_col_letter}{row}/{grp_col_letter}{row}, 0)'
                    cell.number_format = '#,##0.00 ₺'

        for cell in ws_plan[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = center_align

        tot_row = last_row + 1
        ws_plan.cell(row=tot_row, column=1, value="GENEL TOPLAM")
        for col_idx, col_name in enumerate(col_names, start=1):
            cell = ws_plan.cell(row=tot_row, column=col_idx)
            cell.fill = total_fill
            cell.font = total_font
            cell.border = total_border
            cell.alignment = center_align
            if col_name == "Adet":
                cell.value = toplam_adet
                cell.number_format = '#,##0'
            elif col_name == "Toplam Gösterim":
                cell.value = toplam_gos
                cell.number_format = '#,##0'
            elif col_name == "TR GRP":
                cell.value = toplam_grp
                cell.number_format = '#,##0.00'
            elif col_name == "Toplam Bütçe (TL)":
                cell.value = f'=SUM({butce_col_letter}2:{butce_col_letter}{last_row})'
                cell.number_format = '#,##0 ₺'
            elif col_name == "CPR (TL)":
                cell.value = f'=IFERROR({butce_col_letter}{tot_row}/{grp_col_letter}{tot_row}, 0)'
                cell.number_format = '#,##0.00 ₺'

        for ws in [ws_sum, ws_plan]:
            for col in ws.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                col_letter = get_column_letter(col[0].column)
                ws.column_dimensions[col_letter].width = max(max_len + 4, 13)

    return output.getvalue()

def generate_html_report(df_to_export, report_title, include_looker=False, is_arsiv=False):
    toplam_adet = df_to_export["Adet"].sum()
    toplam_gos = df_to_export["Toplam Gösterim"].sum()
    toplam_grp = round(df_to_export["TR GRP"].sum(), 2)
    kapsanan_il, maks_erisim = hesapla_net_kapsama_metrikleri(df_to_export, nufus_dict, TR_TOTAL_NUFUS)

    if is_arsiv:
        table_headers = "<th>Yıl</th><th>Dönem</th><th>Marka</th><th>Kampanya</th><th>Mecra</th><th>Ünite</th><th>İl</th><th>Süre (Gün)</th><th>Periyod</th><th>Adet</th><th>Toplam Gösterim</th><th>Frekans</th><th>Erişim (Kişi)</th><th>İl Nüfusu</th><th>TR Nüfusu</th><th>TR Erişim %</th><th>TR GRP</th>"
        rows_list = []
        for _, r in df_to_export.iterrows():
            rows_list.append(f"<tr><td>{r['Yıl']}</td><td>{r['Dönem (Ay)']}</td><td>{r['Marka']}</td><td>{r['Kampanya Adı']}</td><td>{r['Mecra Adı']}</td><td>{r['Ünite']}</td><td>{r['İl']}</td><td>{r['Süre (Gün)']}</td><td>{r['Periyod']}</td><td>{tr_tam_sayi(r['Adet'])}</td><td>{tr_tam_sayi(r['Toplam Gösterim'])}</td><td>{tr_ondalik(r['Frekans'], 1)}</td><td>{tr_tam_sayi(r['Erişim (Kişi)'])}</td><td>{tr_tam_sayi(r['İl Nüfusu'])}</td><td>{tr_tam_sayi(r['TR Nüfusu'])}</td><td>%{tr_ondalik(r['TR Erişim %'], 2)}</td><td>{tr_ondalik(r['TR GRP'], 2)}</td></tr>")
        table_rows_html = "".join(rows_list)
        footer_html = f"<tfoot><tr><td colspan='9' style='text-align:right; padding-right:15px;'>GENEL TOPLAM:</td><td>{tr_tam_sayi(toplam_adet)}</td><td>{tr_tam_sayi(toplam_gos)}</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>{tr_ondalik(toplam_grp, 2)}</td></tr></tfoot>"
    else:
        table_headers = "<th>Ünite</th><th>İl</th><th>Süre (Gün)</th><th>Periyod</th><th>Adet</th><th>Toplam Gösterim</th><th>Frekans</th><th>Erişim (Kişi)</th><th>İl Nüfusu</th><th>TR Nüfusu</th><th>TR Erişim %</th><th>TR GRP</th>"
        rows_list = []
        for _, r in df_to_export.iterrows():
            rows_list.append(f"<tr><td>{r['Ünite']}</td><td>{r['İl']}</td><td>{r['Süre (Gün)']}</td><td>{r['Periyod']}</td><td>{tr_tam_sayi(r['Adet'])}</td><td>{tr_tam_sayi(r['Toplam Gösterim'])}</td><td>{tr_ondalik(r['Frekans'], 1)}</td><td>{tr_tam_sayi(r['Erişim (Kişi)'])}</td><td>{tr_tam_sayi(r['İl Nüfusu'])}</td><td>{tr_tam_sayi(r['TR Nüfusu'])}</td><td>%{tr_ondalik(r['TR Erişim %'], 2)}</td><td>{tr_ondalik(r['TR GRP'], 2)}</td></tr>")
        table_rows_html = "".join(rows_list)
        footer_html = f"<tfoot><tr><td colspan='4' style='text-align:right; padding-right:15px;'>GENEL TOPLAM:</td><td>{tr_tam_sayi(toplam_adet)}</td><td>{tr_tam_sayi(toplam_gos)}</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>{tr_ondalik(toplam_grp, 2)}</td></tr></tfoot>"

    looker_section = ""
    if include_looker and looker_url:
        looker_section = f"""<div style="margin-top: 30px; background: #172554; border: 1.5px solid #3b82f6; border-radius: 12px; padding: 20px;"><h3 style="color: #38bdf8; margin-bottom: 15px;">Kampanya Harita ve Lokasyon Paneli</h3><iframe src="{looker_url}" width="100%" height="560" frameborder="0" style="border:0; border-radius: 8px;" allowfullscreen></iframe></div>"""

    return f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>{report_title}</title>
    <style>
        body {{ background-color: #030712; color: #e2e8f0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; padding: 30px; line-height: 1.5; }}
        .kpi-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 25px; }}
        .kpi-card {{ background: #172554; border: 1.5px solid #3b82f6; border-radius: 12px; padding: 20px; text-align: center; }}
        table {{ width: 100%; border-collapse: collapse; text-align: center; font-size: 13px; margin-top: 20px; }}
        th {{ background: #1e3a8a; color: #38bdf8; padding: 12px; border: 1px solid #3b82f6; text-align: center; }}
        td {{ padding: 10px; border: 1px solid #1e3a8a; color: #cbd5e1; text-align: center; }}
        tr:nth-child(even) {{ background: rgba(56, 189, 248, 0.03); }}
        tfoot td {{ background: #172554; color: #38bdf8; font-weight: bold; border-top: 2px solid #38bdf8; }}
        .footer-note {{ text-align: center; color: #94a3b8; font-size: 13px; margin-top: 40px; padding-top: 20px; border-top: 1px solid #1e3a8a; }}
    </style>
</head>
<body>
    <h1 style="color: #f1f5f9;">{report_title}</h1>
    <div class="kpi-grid">
        <div class="kpi-card"><div style="font-size: 12px; color: #94a3b8;">TOPLAM GÖSTERİM</div><div style="font-size: 24px; font-weight: bold; color: #4ade80;">{tr_tam_sayi(toplam_gos)}</div></div>
        <div class="kpi-card"><div style="font-size: 12px; color: #94a3b8;">TOPLAM TR GRP</div><div style="font-size: 24px; font-weight: bold; color: #38bdf8;">{tr_ondalik(toplam_grp, 2)}</div></div>
        <div class="kpi-card"><div style="font-size: 12px; color: #94a3b8;">KAPSASANAN İL</div><div style="font-size: 24px; font-weight: bold; color: #c084fc;">{kapsanan_il} İl</div></div>
        <div class="kpi-card"><div style="font-size: 12px; color: #94a3b8;">MAKS. TR ERİŞİMİ</div><div style="font-size: 24px; font-weight: bold; color: #facc15;">%{tr_ondalik(maks_erisim, 1)}</div></div>
    </div>
    <table>
        <thead><tr>{table_headers}</tr></thead>
        <tbody>{table_rows_html}</tbody>
        {footer_html}
    </table>
    {looker_section}
    <div class="footer-note">CAFAS verileri dikkate alınarak geliştirilmiştir.</div>
</body>
</html>"""

# --- 9. GOOGLE SHEETS SÜTUN TABANLI NETWORK AYRIŞTIRMA MOTORU ---
@st.cache_data(ttl=300)
def fetch_and_split_networks():
    try:
        req = urllib.request.Request(GSHEET_XLSX_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp:
            xlsx_bytes = resp.read()
            excel_file = pd.ExcelFile(io.BytesIO(xlsx_bytes))
            
            sheet_name = excel_file.sheet_names[0]
            df_full = pd.read_excel(excel_file, sheet_name=sheet_name)
            
            df_full.columns = [str(c).strip() for c in df_full.columns]
            
            target_col = None
            for col in df_full.columns:
                c_low = col.lower()
                if "network" in c_low or "mecra" in c_low or "paket" in c_low or "grup" in c_low:
                    target_col = col
                    break
            
            if not target_col:
                for col in df_full.columns:
                    if "ünite" in col.lower() or "unite" in col.lower():
                        target_col = col
                        break
            if not target_col and len(df_full.columns) > 1:
                target_col = df_full.columns[0]
                
            networks_dict = {}
            if target_col:
                unique_nets = df_full[target_col].dropna().unique()
                for net in unique_nets:
                    net_str = str(net).strip()
                    if net_str and net_str.lower() not in ['nan', 'none', '', 'toplam']:
                        sub_df = df_full[df_full[target_col] == net].copy()
                        networks_dict[net_str] = sub_df
            else:
                networks_dict["Tüm Envanter"] = df_full
                
            return networks_dict, target_col
    except Exception as e:
        return {}, None

def generate_custom_multi_network_excel(selected_networks_dict):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for net_name, df_net in selected_networks_dict.items():
            valid_sheet_title = str(net_name)[:31].replace(":", "").replace("/", "").replace("\\", "").replace("?", "").replace("*", "").replace("[", "").replace("]", "")
            if not valid_sheet_title: valid_sheet_title = "Network"
            df_net.to_excel(writer, sheet_name=valid_sheet_title, index=False)
            
            wb = writer.book
            ws = wb[valid_sheet_title]
            
            header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
            header_font = Font(name="Segoe UI", size=11, bold=True, color="38BDF8")
            thin_border = Border(
                left=Side(style='thin', color='CBD5E1'),
                right=Side(style='thin', color='CBD5E1'),
                top=Side(style='thin', color='CBD5E1'),
                bottom=Side(style='thin', color='CBD5E1')
            )
            
            for cell in ws[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center", vertical="center")
                
            for row in ws.iter_rows(min_row=2):
                for cell in row:
                    cell.border = thin_border
                    cell.alignment = Alignment(horizontal="center", vertical="center")
                    
            for col in ws.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                col_letter = get_column_letter(col[0].column)
                ws.column_dimensions[col_letter].width = max(max_len + 4, 12)
                
    return output.getvalue()

# --- 10. ÜST MENÜ & BAŞLIK ---
st.markdown("""
<div class="app-header">
    <h1>OOH PLANLAMA & SİMÜLASYON MERKEZİ</h1>
</div>
""", unsafe_allow_html=True)

col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
with col_btn1:
    btn1_class = "tab-btn-active" if st.session_state.active_tab == "simulasyon" else "tab-btn-inactive"
    st.markdown(f'<div class="{btn1_class}">', unsafe_allow_html=True)
    if st.button("Anlık Hesaplama & Simülatör", key="tab_sim_btn", use_container_width=True):
        st.session_state.active_tab = "simulasyon"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with col_btn2:
    btn2_class = "tab-btn-active" if st.session_state.active_tab == "arsiv" else "tab-btn-inactive"
    st.markdown(f'<div class="{btn2_class}">', unsafe_allow_html=True)
    if st.button("Kampanya Yönetimi & Arşiv", key="tab_ars_btn", use_container_width=True):
        st.session_state.active_tab = "arsiv"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with col_btn3:
    btn3_class = "tab-btn-active" if st.session_state.active_tab == "markalar" else "tab-btn-inactive"
    st.markdown(f'<div class="{btn3_class}">', unsafe_allow_html=True)
    if st.button("Markalarımız & Portföy", key="tab_marka_btn", use_container_width=True):
        st.session_state.active_tab = "markalar"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

with col_btn4:
    btn4_class = "tab-btn-active" if st.session_state.active_tab == "ornekler" else "tab-btn-inactive"
    st.markdown(f'<div class="{btn4_class}">', unsafe_allow_html=True)
    if st.button("Örnek Listeler", key="tab_ornek_btn", use_container_width=True):
        st.session_state.active_tab = "ornekler"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

# ==========================================
# 1. SEKME: ANLIK HESAPLAMA & SİMÜLATÖR
# ==========================================
if st.session_state.active_tab == "simulasyon":
    if df_gost is not None and not df_gost.empty:
        st.markdown("<h4 style='color: #38bdf8; font-weight: 700; font-size: 17px; margin-bottom: 14px;'>YENİ KAMPANYA SİMÜLASYONU</h4>", unsafe_allow_html=True)

        col_il, col_unite, col_per, col_sure, col_adet = st.columns([2.2, 2.2, 1.2, 1.2, 1.2])
        
        with col_il:
            il_listesi = sorted(list(set(df_gost['İl'].tolist())))
            
            def on_sim_il_change():
                sec_il = st.session_state.sim_il_select
                uniteler_yeni = sorted(list(set(df_gost[df_gost['İl'] == sec_il]['Ünite'].tolist())))
                if uniteler_yeni:
                    ilk_unite = uniteler_yeni[0]
                    b = sure_dict.get(ilk_unite, 7.0)
                    st.session_state.sim_sure = int(round(b * st.session_state.sim_per))
                    row_match = df_gost[(df_gost['İl'] == sec_il) & (df_gost['Ünite'] == ilk_unite)]
                    if not row_match.empty:
                        st.session_state.sim_adet_input = int(row_match['Network Adedi'].values[0])

            secilen_il = st.selectbox("İl Seçin:", il_listesi, key="sim_il_select", on_change=on_sim_il_change)

        with col_unite:
            uniteler = sorted(list(set(df_gost[df_gost['İl'] == secilen_il]['Ünite'].tolist())))
            
            def on_sim_unite_change():
                u = st.session_state.sim_unite_select
                b = sure_dict.get(u, 7.0)
                st.session_state.sim_sure = int(round(b * st.session_state.sim_per))
                
                row_match = df_gost[(df_gost['İl'] == st.session_state.sim_il_select) & (df_gost['Ünite'] == u)]
                if not row_match.empty:
                    st.session_state.sim_adet_input = int(row_match['Network Adedi'].values[0])

            secilen_unite = st.selectbox("Ünite Seçin:", uniteler, key="sim_unite_select", on_change=on_sim_unite_change)
            baz_sure = sure_dict.get(secilen_unite, 7.0)

            current_net_row = df_gost[(df_gost['İl'] == secilen_il) & (df_gost['Ünite'] == secilen_unite)]
            current_net_adet = int(current_net_row['Network Adedi'].values[0]) if not current_net_row.empty else 100

        def update_from_per():
            p = st.session_state.sim_per
            st.session_state.sim_sure = int(round(baz_sure * p))

        def update_from_sure():
            s = st.session_state.sim_sure
            st.session_state.sim_per = round(s / baz_sure, 2) if baz_sure > 0 else 1.0

        with col_per:
            st.number_input(
                "Periyod:",
                min_value=0.1,
                max_value=20.0,
                step=0.1,
                key="sim_per",
                on_change=update_from_per
            )

        with col_sure:
            st.number_input(
                "Süre (Gün):",
                min_value=1,
                step=1,
                key="sim_sure",
                on_change=update_from_sure
            )

        with col_adet:
            if "sim_adet_input" not in st.session_state:
                st.session_state.sim_adet_input = current_net_adet
            adet_val = st.number_input("Adet:", min_value=1, value=int(st.session_state.sim_adet_input), step=1, key="sim_adet_input")

        periyod_val = st.session_state.sim_per
        sure_val = st.session_state.sim_sure

        st.markdown('<div class="action-add-btn">', unsafe_allow_html=True)
        ekle_tiklandi = st.button("Simülasyon Satırını Plana Ekle", key="sim_add_row_btn", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if ekle_tiklandi:
            m_gost = df_gost[(df_gost['İl'] == secilen_il) & (df_gost['Ünite'] == secilen_unite)]
            gunluk_gost = float(m_gost['Günlük Gösterim'].values[0]) if not m_gost.empty else 0.0
            baz_frekans = float(m_gost['Frekans'].values[0]) if not m_gost.empty else 1.0
            network_adedi = float(m_gost['Network Adedi'].values[0]) if not m_gost.empty else 100.0
            endeks = float(m_gost['Endeks'].values[0]) if not m_gost.empty else 1.0

            if network_adedi > 0 and adet_val > 0 and periyod_val > 0:
                dinamik_frekans = baz_frekans * ((adet_val / network_adedi) ** 0.55) * endeks * (periyod_val ** 0.80)
            else:
                dinamik_frekans = 0.0

            il_nufus = get_il_nufusu(secilen_il, nufus_dict)
            toplam_gosterim = gunluk_gost * sure_val * adet_val
            erisim_kisi = (toplam_gosterim / dinamik_frekans) if dinamik_frekans > 0 else 0
            erisim_pct_tr = (erisim_kisi / TR_TOTAL_NUFUS) * 100
            grp_tr = (toplam_gosterim / TR_TOTAL_NUFUS) * 100

            st.session_state.sim_rows.append({
                "Ünite": secilen_unite,
                "İl": secilen_il,
                "Süre (Gün)": int(sure_val),
                "Periyod": format_periyod(periyod_val),
                "Adet": int(adet_val),
                "Toplam Gösterim": int(toplam_gosterim),
                "Frekans": float(round(dinamik_frekans, 1)),
                "Erişim (Kişi)": int(erisim_kisi),
                "İl Nüfusu": int(il_nufus),
                "TR Nüfusu": int(TR_TOTAL_NUFUS),
                "TR Erişim %": float(round(erisim_pct_tr, 2)),
                "TR GRP": float(round(grp_tr, 2))
            })
            st.rerun()

        if st.session_state.sim_rows:
            df_sim = pd.DataFrame(st.session_state.sim_rows)
            st.markdown("<div style='height: 18px;'></div>", unsafe_allow_html=True)
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            toplam_gos = df_sim["Toplam Gösterim"].sum()
            toplam_grp = round(df_sim["TR GRP"].sum(), 2)
            kapsanan_il, maks_erisim = hesapla_net_kapsama_metrikleri(df_sim, nufus_dict, TR_TOTAL_NUFUS)

            kpi1.metric("Toplam Gösterim", tr_tam_sayi(toplam_gos))
            kpi2.metric("Toplam TR GRP", tr_ondalik(toplam_grp, 2))
            kpi3.metric("Maks. TR Erişimi", f"%{tr_ondalik(maks_erisim, 1)}")
            kpi4.metric("Kapsanan İl Sayısı", f"{kapsanan_il} İl")

            rows_html = "".join([
                f"<tr><td>{r['Ünite']}</td><td>{r['İl']}</td><td>{r['Süre (Gün)']}</td><td>{r['Periyod']}</td><td>{tr_tam_sayi(r['Adet'])}</td><td>{tr_tam_sayi(r['Toplam Gösterim'])}</td><td>{tr_ondalik(r['Frekans'], 1)}</td><td>{tr_tam_sayi(r['Erişim (Kişi)'])}</td><td>{tr_tam_sayi(r['İl Nüfusu'])}</td><td>{tr_tam_sayi(r['TR Nüfusu'])}</td><td>%{tr_ondalik(r['TR Erişim %'], 2)}</td><td>{tr_ondalik(r['TR GRP'], 2)}</td></tr>"
                for _, r in df_sim.iterrows()
            ])
            
            table_markup = f"""<div class="table-responsive-box"><table class="custom-ooh-table"><thead><tr><th>Ünite</th><th>İl</th><th>Süre (Gün)</th><th>Periyod</th><th>Adet</th><th>Toplam Gösterim</th><th>Frekans</th><th>Erişim (Kişi)</th><th>İl Nüfusu</th><th>TR Nüfusu</th><th>TR Erişim %</th><th>TR GRP</th></tr></thead><tbody>{rows_html}</tbody></table></div>"""
            st.markdown(table_markup, unsafe_allow_html=True)

            col_s1, col_s2, col_s3, col_s4, col_s5 = st.columns([1, 1.2, 1, 1.2, 1.5])
            with col_s1:
                if st.button("Son Satırı Sil", key="sim_del_last", use_container_width=True):
                    if st.session_state.sim_rows:
                        st.session_state.sim_rows.pop()
                        st.rerun()
            with col_s2:
                with st.popover("Seçili Satırı Sil", use_container_width=True):
                    silinecek_sim_idx = st.selectbox(
                        "Silinecek Satır No:",
                        range(len(st.session_state.sim_rows)),
                        key="sim_del_select",
                        format_func=lambda i: f"Satır {i+1}: {st.session_state.sim_rows[i]['Ünite']} ({st.session_state.sim_rows[i]['İl']})"
                    )
                    if st.button("Bu Satırı Sil", key="sim_del_btn", type="primary", use_container_width=True):
                        st.session_state.sim_rows.pop(silinecek_sim_idx)
                        st.rerun()
            with col_s3:
                if st.button("Tümünü Temizle", key="sim_clear_all", use_container_width=True):
                    st.session_state.sim_rows = []
                    st.rerun()
            with col_s4:
                sim_html = generate_html_report(df_sim, "OOH Medya Simülasyon Raporu", include_looker=False, is_arsiv=False)
                st.download_button(
                    label="HTML Raporu Al",
                    data=sim_html,
                    file_name="OOH_Simulasyon_Raporu.html",
                    mime="text/html",
                    use_container_width=True
                )
            with col_s5:
                sim_excel = generate_excel_report(df_sim, "OOH Medya Simülasyon Raporu", looker_link=looker_url, is_arsiv=False)
                st.download_button(
                    label="Excel Raporu Al",
                    data=sim_excel,
                    file_name="OOH_Simulasyon_Raporu.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

            # --- SİMÜLASYON PLANINI DOĞRUDAN MARKA KLASÖRÜNE KAYDETME & BÜTÇE GİRİŞİ ---
            st.markdown("""
            <div class="save-box">
                <h3 style="color: #38bdf8; margin-top: 0; font-size: 20px; font-weight: 800;">Bu Planı ve Bütçeyi Doğrudan Marka Klasörüne Kaydet</h3>
                <p style="color: #94a3b8; font-size: 14.5px; margin-bottom: 16px;">Oluşturduğun bu kampanyaya harcanan bütçeyi girerek doğrudan ilgili markanın portföy klasörüne kaydedebilirsin:</p>
            </div>
            """, unsafe_allow_html=True)

            with st.form("sim_direct_save_form"):
                ds_col1, ds_col2, ds_col3, ds_col4, ds_col5, ds_col6 = st.columns([2, 2, 1, 1.2, 1.5, 1.5])
                with ds_col1:
                    ds_marka = st.selectbox("Marka Seç:", MASTER_BRANDS, key="ds_marka_box")
                with ds_col2:
                    ds_kampanya = st.text_input("Kampanya Adı:", placeholder="Örn: Lansman", key="ds_kampanya_box")
                with ds_col3:
                    ds_yil = st.number_input("Yıl:", min_value=2020, max_value=2035, value=2026, step=1, key="ds_yil_box")
                with ds_col4:
                    ds_donem = st.selectbox("Dönem:", aylar, index=0, key="ds_donem_box")
                with ds_col5:
                    ds_butce = st.number_input("Toplam Bütçe (₺):", min_value=0.0, value=150000.0, step=10000.0, key="ds_butce_box")
                with ds_col6:
                    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                    ds_submit = st.form_submit_button("Klasöre Kaydet", use_container_width=True, type="primary")

                if ds_submit:
                    k_adi = ds_kampanya.strip() if ds_kampanya.strip() else "Genel Kampanya"
                    satir_sayisi = len(st.session_state.sim_rows)
                    butce_payi = ds_butce / satir_sayisi if satir_sayisi > 0 else 0.0

                    for row in st.session_state.sim_rows:
                        c_adi = tahmin_mecra(row["Ünite"], row["İl"])
                        st.session_state.arsiv_rows.append({
                            "Yıl": int(ds_yil),
                            "Dönem (Ay)": ds_donem,
                            "Marka": ds_marka,
                            "Kampanya Adı": k_adi,
                            "Mecra Adı": c_adi,
                            "Ünite": row["Ünite"],
                            "İl": row["İl"],
                            "Süre (Gün)": row["Süre (Gün)"],
                            "Periyod": format_periyod(row["Periyod"]),
                            "Adet": int(row["Adet"]),
                            "Toplam Gösterim": int(row["Toplam Gösterim"]),
                            "Frekans": float(row["Frekans"]),
                            "Erişim (Kişi)": int(row["Erişim (Kişi)"]),
                            "İl Nüfusu": int(row["İl Nüfusu"]),
                            "TR Nüfusu": int(TR_TOTAL_NUFUS),
                            "TR Erişim %": float(round(row["TR Erişim %"], 2)),
                            "TR GRP": float(round(row["TR GRP"], 2)),
                            "Bütçe (TL)": float(round(butce_payi, 2))
                        })
                    st.session_state.sim_rows = []
                    st.success(f"Başarıyla '{ds_marka}' klasörüne ve bütçe arşivine kaydedildi! 'Markalarımız & Portföy' sekmesinden harcamalarını inceleyebilirsin.")
                    st.rerun()

# ==========================================
# 2. SEKME: KAMPANYA YÖNETİMİ (ZÜMRÜT YEŞİLİ BÜTÇE KUTULU)
# ==========================================
elif st.session_state.active_tab == "arsiv":
    st.markdown("<h4 style='color: #38bdf8; font-weight: 700; font-size: 18px; margin-bottom: 12px;'>YENİ KAMPANYA OLUŞTUR & ARŞİVE GÖNDER</h4>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8; font-size: 14.5px; margin-bottom: 20px;'>Aşağıdaki genişletilmiş alanları doldurarak kampanyanı bütçesiyle birlikte doğrudan ilgili marka klasörüne kaydedebilirsin:</p>", unsafe_allow_html=True)
    
    if df_gost is not None and not df_gost.empty:
        il_listesi = sorted(list(set(df_gost['İl'].tolist())))

        with st.form("arsiv_ekle_ve_gonder_form_genis_v5"):
            # 1. Satır: Yıl, Dönem, Marka, Kampanya Adı, Mecra
            ak_c1, ak_c2, ak_c3, ak_c4, ak_c5 = st.columns([1.2, 1.8, 2.5, 3, 2.5])
            with ak_c1:
                a_yil = st.number_input("Yıl:", min_value=2020, max_value=2035, value=2026, step=1, key="ars_yil")
            with ak_c2:
                aylar = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
                a_donem = st.selectbox("Dönem:", aylar, index=0, key="ars_donem")
            with ak_c3:
                a_marka = st.selectbox("Marka Seçin:", MASTER_BRANDS, key="ars_marka_select")
            with ak_c4:
                a_kampanya_in = st.text_input("Kampanya Adı:", placeholder="Örn: Kırtasiye / Lansman", key="ars_kampanya")
            with ak_c5:
                a_mecra_in = st.text_input("Mecra:", placeholder="Örn: Kentvizyon / Donanım Medya", key="ars_mecra")

            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

            # 2. Satır: İl, Ünite, Periyod, Süre, Adet, Bütçe (Zümrüt Yeşili Vurgulu Bütçe Kutusu)
            bk_c1, bk_c2, bk_c3, bk_c4, bk_c5, bk_c6 = st.columns([2.5, 3, 1.5, 1.5, 1.5, 2.2])
            with bk_c1:
                a_il = st.selectbox("İl Seçin:", il_listesi, key="ars_il_select")
            with bk_c2:
                a_uniteler = sorted(list(set(df_gost[df_gost['İl'] == a_il]['Ünite'].tolist())))
                a_unite = st.selectbox("Ünite Seçin:", a_uniteler, key="ars_unite_select")
            with bk_c3:
                a_periyod = st.number_input("Periyod:", min_value=0.1, max_value=20.0, value=1.0, step=0.1, key="ars_per")
            with bk_c4:
                a_sure = st.number_input("Süre (Gün):", min_value=1, value=7, step=1, key="ars_sure")
            with bk_c5:
                a_adet = st.number_input("Adet:", min_value=1, value=50, step=1, key="ars_adet")
            with bk_c6:
                a_butce = st.number_input("Toplam Bütçe (₺):", min_value=0.0, value=50000.0, step=5000.0, key="ars_butce")

            st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
            arsiv_gonder_btn = st.form_submit_button("🚀 Kampanyayı Arşive ve Marka Klasörüne Gönder", use_container_width=True, type="primary")

            if arsiv_gonder_btn:
                m_isim = a_marka.strip() if a_marka.strip() else "BİM"
                k_isim = a_kampanya_in.strip() if a_kampanya_in.strip() else "Genel Kampanya"
                c_isim = a_mecra_in.strip() if a_mecra_in.strip() else "Kentvizyon"

                m_gost = df_gost[(df_gost['İl'] == a_il) & (df_gost['Ünite'] == a_unite)]
                gunluk_gost = float(m_gost['Günlük Gösterim'].values[0]) if not m_gost.empty else 0.0
                baz_frekans = float(m_gost['Frekans'].values[0]) if not m_gost.empty else 1.0
                network_adedi = float(m_gost['Network Adedi'].values[0]) if not m_gost.empty else 100.0
                endeks = float(m_gost['Endeks'].values[0]) if not m_gost.empty else 1.0

                if network_adedi > 0 and a_adet > 0 and a_periyod > 0:
                    dinamik_frekans = baz_frekans * ((a_adet / network_adedi) ** 0.55) * endeks * (a_periyod ** 0.80)
                else:
                    dinamik_frekans = 0.0

                il_nufus = get_il_nufusu(a_il, nufus_dict)
                toplam_gosterim = gunluk_gost * a_sure * a_adet
                erisim_kisi = (toplam_gosterim / dinamik_frekans) if dinamik_frekans > 0 else 0
                erisim_pct_tr = (erisim_kisi / TR_TOTAL_NUFUS) * 100
                grp_tr = (toplam_gosterim / TR_TOTAL_NUFUS) * 100

                st.session_state.arsiv_rows.append({
                    "Yıl": int(a_yil),
                    "Dönem (Ay)": a_donem,
                    "Marka": m_isim,
                    "Kampanya Adı": k_isim,
                    "Mecra Adı": c_isim,
                    "Ünite": a_unite,
                    "İl": a_il,
                    "Süre (Gün)": int(a_sure),
                    "Periyod": format_periyod(a_periyod),
                    "Adet": int(a_adet),
                    "Toplam Gösterim": int(toplam_gosterim),
                    "Frekans": float(round(dinamik_frekans, 1)),
                    "Erişim (Kişi)": int(erisim_kisi),
                    "İl Nüfusu": int(il_nufus),
                    "TR Nüfusu": int(TR_TOTAL_NUFUS),
                    "TR Erişim %": float(round(erisim_pct_tr, 2)),
                    "TR GRP": float(round(grp_tr, 2)),
                    "Bütçe (TL)": float(round(a_butce, 2))
                })
                st.success(f"✅ '{m_isim}' markasının '{k_isim}' kampanyası arşive ve klasörüne başarıyla gönderildi!")
                st.rerun()

        if st.session_state.arsiv_rows:
            st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
            st.markdown("<h4 style='color: #38bdf8; font-weight: 700; font-size: 17px; margin-bottom: 12px;'>📋 Kayıtlı Arşiv Havuzu</h4>", unsafe_allow_html=True)
            
            df_arsiv = pd.DataFrame(st.session_state.arsiv_rows)
            
            ak1, ak2, ak3, ak4 = st.columns(4)
            toplam_gos_a = df_arsiv["Toplam Gösterim"].sum()
            toplam_grp_a = round(df_arsiv["TR GRP"].sum(), 2)
            kapsanan_il_a, maks_erisim_a = hesapla_net_kapsama_metrikleri(df_arsiv, nufus_dict, TR_TOTAL_NUFUS)

            ak1.metric("Toplam Gösterim", tr_tam_sayi(toplam_gos_a))
            ak2.metric("Toplam TR GRP", tr_ondalik(toplam_grp_a, 2))
            ak3.metric("Maks. TR Erişimi", f"%{tr_ondalik(maks_erisim_a, 1)}")
            ak4.metric("Kapsanan İl", f"{kapsanan_il_a} İl")

            rows_arsiv_html = "".join([
                f"<tr><td>{r['Yıl']}</td><td>{r['Dönem (Ay)']}</td><td><strong>{r['Marka']}</strong></td><td>{r['Kampanya Adı']}</td><td>{r['Mecra Adı']}</td><td>{r['Ünite']}</td><td>{r['İl']}</td><td>{r['Süre (Gün)']}</td><td>{r['Periyod']}</td><td>{tr_tam_sayi(r['Adet'])}</td><td>{tr_tam_sayi(r['Toplam Gösterim'])}</td><td>{tr_ondalik(r['Frekans'], 1)}</td><td>{tr_tam_sayi(r['Erişim (Kişi)'])}</td><td>%{tr_ondalik(r['TR Erişim %'], 2)}</td><td>{tr_ondalik(r['TR GRP'], 2)}</td><td style='color:#4ade80; font-weight:700;'>{tr_ondalik(r.get('Bütçe (TL)', 0), 2)} ₺</td></tr>"
                for _, r in df_arsiv.iterrows()
            ])
            
            table_arsiv_markup = f"""<div class="table-responsive-box"><table class="custom-ooh-table"><thead><tr><th>Yıl</th><th>Dönem</th><th>Marka</th><th>Kampanya</th><th>Mecra</th><th>Ünite</th><th>İl</th><th>Süre</th><th>Periyod</th><th>Adet</th><th>Gösterim</th><th>Frekans</th><th>Erişim</th><th>TR Erişim %</th><th>TR GRP</th><th>Bütçe</th></tr></thead><tbody>{rows_arsiv_html}</tbody></table></div>"""
            st.markdown(table_arsiv_markup, unsafe_allow_html=True)

            col_a1, col_a2, col_a3, col_a4 = st.columns([1.2, 1.2, 1.5, 1.5])
            with col_a1:
                if st.button("🧹 Tüm Arşivi Temizle", key="ars_clear_all", use_container_width=True):
                    st.session_state.arsiv_rows = []
                    st.rerun()
            with col_a2:
                with st.popover("🗑️ Seçili Satırı Sil", use_container_width=True):
                    silinecek_idx = st.selectbox(
                        "Silinecek Satır No:",
                        range(len(st.session_state.arsiv_rows)),
                        key="ars_del_select",
                        format_func=lambda i: f"Satır {i+1}: {st.session_state.arsiv_rows[i]['Marka']} - {st.session_state.arsiv_rows[i]['Kampanya Adı']} ({st.session_state.arsiv_rows[i]['Ünite']})"
                    )
                    if st.button("❌ Bu Satırı Sil", key="ars_del_btn", type="primary", use_container_width=True):
                        st.session_state.arsiv_rows.pop(silinecek_idx)
                        st.rerun()
            with col_a3:
                arsiv_html = generate_html_report(df_arsiv, "OOH Kampanya Arşiv & Yönetim Raporu", include_looker=True, is_arsiv=True)
                st.download_button(
                    label="📄 HTML Raporu Al",
                    data=arsiv_html,
                    file_name="OOH_Kampanya_Arsiv_Raporu.html",
                    mime="text/html",
                    use_container_width=True
                )
            with col_a4:
                arsiv_excel = generate_excel_report(df_arsiv, "OOH Kampanya Arşiv & Yönetim Raporu", looker_link=looker_url, is_arsiv=True)
                st.download_button(
                    label="📊 Excel Raporu Al",
                    data=arsiv_excel,
                    file_name="OOH_Kampanya_Arsiv_Raporu.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #94a3b8; font-weight: 700; font-size: 17px; margin-bottom: 12px;'>GERÇEKLEŞEN KAMPANYA LOKASYONLARI & HARİTA PANELİ</h4>", unsafe_allow_html=True)
        if looker_url:
            st.components.v1.html(
                f'<iframe src="{looker_url}" width="100%" height="540" frameborder="0" style="border:0; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.4);" allowfullscreen></iframe>',
                height=560
            )
        else:
            st.info("Arşiv haritasını görüntülemek için sol yan menüden Looker Studio Harita Linkini giriniz.")

# ==========================================
# 3. SEKME: MARKALARIMIZ & KAMPANYA KLASÖRLERİ Hiyerarşisi
# ==========================================
elif st.session_state.active_tab == "markalar":
    st.markdown("<h4 style='color: #38bdf8; font-weight: 700; font-size: 18px; margin-bottom: 16px;'>MÜŞTERİ PORTFÖYÜ & KAMPANYA KLASÖRLERİ</h4>", unsafe_allow_html=True)

    df_arsiv_all = pd.DataFrame(st.session_state.arsiv_rows) if st.session_state.arsiv_rows else pd.DataFrame()

    # DURUM 1: Ana Marka Klasörleri Listesi
    if st.session_state.selected_brand_folder is None:
        search_query = st.text_input("Müşteri / Marka Ara:", placeholder="Marka adı arayın... (örn: KFC, Pidem, BİM, Brita, Yataş)", key="brand_search_box")
        
        kayitli_arsiv_markalari = set(df_arsiv_all["Marka"].dropna().astype(str).tolist()) if not df_arsiv_all.empty else set()
        tum_markalar_listesi = sorted(list(set(MASTER_BRANDS + list(kayitli_arsiv_markalari))))

        if search_query:
            tum_markalar_listesi = [m for m in tum_markalar_listesi if search_query.lower() in m.lower()]

        st.markdown(f"<p style='color: #94a3b8; font-size: 14.5px; margin-bottom: 22px;'>Toplam <strong>{len(tum_markalar_listesi)}</strong> kurumsal müşteri listeleniyor. Kampanya klasörlerini görmek istediğiniz markaya tıklayın:</p>", unsafe_allow_html=True)

        cols = st.columns(4)
        for idx, marka in enumerate(tum_markalar_listesi):
            col = cols[idx % 4]
            kampanya_sayisi = len(df_arsiv_all[df_arsiv_all["Marka"] == marka]) if not df_arsiv_all.empty else 0
            
            with col:
                st.markdown('<div class="brand-folder-btn">', unsafe_allow_html=True)
                btn_title = f"📁 {marka}\n({kampanya_sayisi} Kayıt)"
                if st.button(btn_title, key=f"bfolder_{marka}", use_container_width=True):
                    st.session_state.selected_brand_folder = marka
                    st.session_state.selected_campaign_folder = None
                    st.rerun()
                st.markdown('</div><div style="height: 14px;"></div>', unsafe_allow_html=True)

    # DURUM 2: Marka İçine Girildiğinde -> Kampanya Adı Klasörlerini Listele
    elif st.session_state.selected_campaign_folder is None:
        secilen_marka = st.session_state.selected_brand_folder

        col_back, col_title = st.columns([1.5, 5])
        with col_back:
            if st.button("⬅️ Tüm Markalara Dön", use_container_width=True):
                st.session_state.selected_brand_folder = None
                st.rerun()
        with col_title:
            st.markdown(f"<h3 style='color: #38bdf8; margin: 4px 0 0 0; font-weight: 800;'>📁 {secilen_marka} • Kampanya Klasörleri</h3>", unsafe_allow_html=True)

        if not df_arsiv_all.empty and secilen_marka in df_arsiv_all["Marka"].values:
            df_marka = df_arsiv_all[df_arsiv_all["Marka"] == secilen_marka]
            kampanya_listesi = sorted(list(set(df_marka["Kampanya Adı"].dropna().astype(str).tolist())))

            st.markdown(f"<p style='color: #94a3b8; font-size: 15px; margin: 15px 0;'><strong>{secilen_marka}</strong> markasına ait toplam <strong>{len(kampanya_listesi)}</strong> kampanya klasörü bulundu. İncelemek istediğiniz kampanyaya tıklayın:</p>", unsafe_allow_html=True)

            camp_cols = st.columns(3)
            for idx, k_adi in enumerate(kampanya_listesi):
                ccol = camp_cols[idx % 3]
                df_camp = df_marka[df_marka["Kampanya Adı"] == k_adi]
                c_butce = df_camp["Bütçe (TL)"].sum() if "Bütçe (TL)" in df_camp.columns else 0.0
                c_gos = df_camp["Toplam Gösterim"].sum()
                
                with ccol:
                    st.markdown(f"""
                    <div style="background: linear-gradient(145deg, #172554 0%, #0f172a 100%); border: 2px solid rgba(56, 189, 248, 0.4); border-radius: 16px; padding: 22px; margin-bottom: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.4);">
                        <h4 style="color: #38bdf8; margin: 0 0 10px 0; font-size: 19px; font-weight: 700;">📂 {k_adi}</h4>
                        <p style="color: #4ade80; font-size: 14.5px; font-weight: 700; margin: 0 0 6px 0;">💰 Harcama: {tr_ondalik(c_butce, 2)} ₺</p>
                        <p style="color: #94a3b8; font-size: 13.5px; margin: 0;">📊 Gösterim: {tr_tam_sayi(c_gos)}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"Klasörü Aç: {k_adi}", key=f"open_camp_{k_adi}", use_container_width=True):
                        st.session_state.selected_campaign_folder = k_adi
                        st.rerun()
        else:
            st.warning(f"📌 {secilen_marka} markasına ait henüz arşivlenmiş bir kampanya kaydı bulunamadı. 'Kampanya Yönetimi & Arşiv' sekmesinden bu markaya kampanya ekleyebilirsiniz.")

    # DURUM 3: Seçilen Kampanya Klasörünün İçi (Detaylar & Harcama)
    else:
        secilen_marka = st.session_state.selected_brand_folder
        secilen_kampanya = st.session_state.selected_campaign_folder

        col_back2, col_title2 = st.columns([1.5, 5])
        with col_back2:
            if st.button("⬅️ Kampanyalara Dön", use_container_width=True):
                st.session_state.selected_campaign_folder = None
                st.rerun()
        with col_title2:
            st.markdown(f"<h3 style='color: #38bdf8; margin: 4px 0 0 0; font-weight: 800;'>📂 {secilen_marka} / {secilen_kampanya} Kampanya Detayı</h3>", unsafe_allow_html=True)

        df_detay = df_arsiv_all[(df_arsiv_all["Marka"] == secilen_marka) & (df_arsiv_all["Kampanya Adı"] == secilen_kampanya)]

        if not df_detay.empty:
            d_butce = df_detay["Bütçe (TL)"].sum() if "Bütçe (TL)" in df_detay.columns else 0.0
            d_gos = df_detay["Toplam Gösterim"].sum()
            d_grp = round(df_detay["TR GRP"].sum(), 2)
            d_il, d_erisim = hesapla_net_kapsama_metrikleri(df_detay, nufus_dict, TR_TOTAL_NUFUS)

            dkpi1, dkpi2, dkpi3, dkpi4 = st.columns(4)
            dkpi1.metric("Kampanya Harcaması", f"{tr_ondalik(d_butce, 2)} ₺")
            dkpi2.metric("Toplam Gösterim", tr_tam_sayi(d_gos))
            dkpi3.metric("Toplam TR GRP", tr_ondalik(d_grp, 2))
            dkpi4.metric("Kapsanan İl", f"{d_il} İl")

            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            st.markdown("<h5 style='color: #38bdf8; font-weight: 700; margin-bottom: 10px;'>📍 Bu Kampanyaya Ait Medya Planı Satırları</h5>", unsafe_allow_html=True)

            rows_detay_html = "".join([
                f"<tr><td>{r['Yıl']}</td><td>{r['Dönem (Ay)']}</td><td>{r['Mecra Adı']}</td><td>{r['Ünite']}</td><td>{r['İl']}</td><td>{r['Süre (Gün)']}</td><td>{r['Periyod']}</td><td>{tr_tam_sayi(r['Adet'])}</td><td>{tr_tam_sayi(r['Toplam Gösterim'])}</td><td>{tr_ondalik(r['Frekans'], 1)}</td><td>{tr_tam_sayi(r['Erişim (Kişi)'])}</td><td>%{tr_ondalik(r['TR Erişim %'], 2)}</td><td>{tr_ondalik(r['TR GRP'], 2)}</td><td style='color:#4ade80; font-weight:700;'>{tr_ondalik(r.get('Bütçe (TL)', 0), 2)} ₺</td></tr>"
                for _, r in df_detay.iterrows()
            ])

            table_detay_markup = f"""<div class="table-responsive-box"><table class="custom-ooh-table"><thead><tr><th>Yıl</th><th>Dönem</th><th>Mecra</th><th>Ünite</th><th>İl</th><th>Süre</th><th>Periyod</th><th>Adet</th><th>Gösterim</th><th>Frekans</th><th>Erişim</th><th>TR Erişim %</th><th>TR GRP</th><th>Bütçe</th></tr></thead><tbody>{rows_detay_html}</tbody></table></div>"""
            st.markdown(table_detay_markup, unsafe_allow_html=True)

            d_col1, d_col2 = st.columns([1.5, 1.5])
            with d_col1:
                detay_html = generate_html_report(df_detay, f"{secilen_marka} - {secilen_kampanya} Kampanya Raporu", include_looker=False, is_arsiv=True)
                st.download_button(
                    label="📄 Kampanya HTML Raporu Al",
                    data=detay_html,
                    file_name=f"{secilen_marka}_{secilen_kampanya}_Rapor.html",
                    mime="text/html",
                    use_container_width=True
                )
            with d_col2:
                detay_excel = generate_excel_report(df_detay, f"{secilen_marka} - {secilen_kampanya} Kampanya Raporu", looker_link=looker_url, is_arsiv=True)
                st.download_button(
                    label="📊 Kampanya Excel Raporu Al",
                    data=detay_excel,
                    file_name=f"{secilen_marka}_{secilen_kampanya}_Rapor.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        else:
            st.warning("Bu kampanyaya ait detay bulunamadı.")

# --- 11. KURUMSAL DİPNOT (FOOTER) ---
st.markdown("<div class='corporate-footer'>CAFAS verileri dikkate alınarak geliştirilmiştir.</div>", unsafe_allow_html=True)

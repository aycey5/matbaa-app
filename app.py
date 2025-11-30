import streamlit as st

# ==========================================
# ⚙️ AYARLAR VE KURLAR (SIDEBAR)
# ==========================================
st.set_page_config(page_title="Matbaa Maliyet Hesaplayıcı", layout="wide", page_icon="🖨️")

with st.sidebar:
    st.header("⚙️ Döviz Kurları")
    # S3 Hücresi
    dolar_kur = st.number_input("Dolar Kuru ($) - S3", value=34.50, step=0.01, format="%.2f")
    # S4 Hücresi (Q4'ü de bu kabul ettik)
    euro_kur = st.number_input("Euro Kuru (€) - S4", value=37.20, step=0.01, format="%.2f")
    
    st.divider()
    st.info("Formüllerdeki S3 (Dolar) ve S4 (Euro) değerleri buradan çekilir.")

st.title("🖨️ Matbaa Üretim & Maliyet Hesabı")
st.markdown("---")

# ==========================================
# 📝 İŞ BİLGİLERİ (A1, A2)
# ==========================================
col_info1, col_info2 = st.columns(2)
with col_info1:
    musteri_adi = st.text_input("Müşteri Adı (B1)", "Örnek Müşteri A.Ş.")
with col_info2:
    isin_adi = st.text_input("İşin Adı (B2)", "Özel Kutu Basımı")

st.markdown("---")

# ==========================================
# 📦 1. BÖLÜM: KAĞIT HESABI (A5-A14)
# ==========================================
st.header("📦 1. Kağıt Hesabı")
k1, k2, k3, k4 = st.columns(4)

with k1:
    kagit_en = st.number_input("Kağıt En (B5/H5)", value=70.0) # B5 ve H5 aynı
    kagit_boy = st.number_input("Kağıt Boy (C5/I5)", value=100.0) # C5 ve I5 aynı
    gramaj = st.number_input("Kağıt Gramaj (B7)", value=350) 

with k2:
    kagit_brut = st.number_input("Kağıt Brüt Tabaka (B8)", value=1000, step=100) 
    baski_brut = st.number_input("Baskı Brüt Tabaka (B9/H10)", value=1000, step=100) # Selefonda H10 olacak
    verimlilik = st.number_input("Baskı Verimlilik (B10)", value=100) 

with k3:
    siparis_adedi = st.number_input("Sipariş Ürün Adedi (B11)", value=5000) 
    kur_secimi = st.selectbox("Kağıt Kur (B12)", ["DOLAR", "EURO", "TL"]) 
    kagit_birim_fiyat = st.number_input("Kağıt Fiyatı (B13)", value=800.0) 

# --- KAĞIT HESAPLAMALARI ---
toplam_kilo = (kagit_en * kagit_boy * gramaj * kagit_brut) / 10000000

secilen_kur_degeri = 1.0
if kur_secimi == "DOLAR": secilen_kur_degeri = dolar_kur
elif kur_secimi == "EURO": secilen_kur_degeri = euro_kur

kagit_toplam_tutar = (kagit_birim_fiyat / 1000) * toplam_kilo * secilen_kur_degeri

with k4:
    st.metric("Toplam Kilo (B14)", f"{toplam_kilo:.2f} kg")
    st.metric("Kağıt Tutarı", f"{kagit_toplam_tutar:,.2f} ₺")

st.markdown("---")

# ==========================================
# 🎨 2. BÖLÜM: BASKI HESABI (D5-F30)
# ==========================================
st.header("🎨 2. Baskı Hesabı")

col_baski_ebat1, col_baski_ebat2 = st.columns(2)
with col_baski_ebat1:
    baski_en = st.number_input("Baskı Ebadı En (E5)", value=70.0)
with col_baski_ebat2:
    baski_boy = st.number_input("Baskı Ebadı Boy (F5)", value=100.0)

col_karton, col_metalize = st.columns(2)

# --- YARDIMCI FONKSİYONLAR ---
def hesapla_baski_sayisi(evet_hayir, brut_tabaka):
    return brut_tabaka if evet_hayir == "EVET" else 0

def hesapla_setup(evet_hayir, kalip_sayisi, tip="KARTON"):
    if evet_hayir == "HAYIR": return 0
    if tip == "KARTON":
        return 6000 if 6 <= kalip_sayisi < 10 else 3000
    else:
        return 12000 if 6 <= kalip_sayisi < 10 else 6000

def hesapla_tiraj(baski_sayisi, kalip_sayisi, tip="KARTON"):
    if baski_sayisi <= 1000: return 0
    fark = baski_sayisi - 1000
    carpan = 2 if 6 <= kalip_sayisi < 10 else 1
    birim = 0.8 if tip == "KARTON" else 1.3
    return fark * birim * carpan

# --- KARTON BASKI ---
with col_karton:
    st.subheader("🟫 Karton Baskı (E)")
    e_on_baski = st.selectbox("Ön Baskı (E7)", ["EVET", "HAYIR"], index=0)
    e_arka_baski = st.selectbox("Arka Baskı (E8)", ["EVET", "HAYIR"], index=1)
    e_boya_turu = st.selectbox("Boya Türü (E9)", ["CMYK", "PANTONE"])
    e_on_kalip = st.number_input("Ön Kalıp (D10)", value=4)
    e_arka_kalip = st.number_input("Arka Kalıp (E11)", value=0)
    e_vernik = st.selectbox("Vernik (E12)", ["EVET", "HAYIR"], index=1)
    e_uv = st.selectbox("UV Lak (E13)", ["EVET", "HAYIR"], index=1)
    e_disp = st.selectbox("Dispersiyon (E14)", ["EVET", "HAYIR"], index=1)
    e_kaucuk = st.selectbox("Kauçuk (E15)", ["EVET", "HAYIR"], index=1)

    # Hesaplamalar
    e_on_sayi = hesapla_baski_sayisi(e_on_baski, baski_brut)
    e_on_setup = hesapla_setup(e_on_baski, e_on_kalip, "KARTON")
    e_on_tiraj = hesapla_tiraj(e_on_sayi, e_on_kalip, "KARTON")
    
    e_arka_sayi = hesapla_baski_sayisi(e_arka_baski, baski_brut)
    e_arka_setup = hesapla_setup(e_arka_baski, e_arka_kalip, "KARTON")
    e_arka_tiraj = hesapla_tiraj(e_arka_sayi, e_arka_kalip, "KARTON")

    e_boya_mik = (baski_en * baski_boy * 0.2 * e_on_sayi) / 1000000
    e_murekkep_fiyat = (e_boya_mik * 17 * euro_kur) if e_boya_turu == "CMYK" else (e_boya_mik * 28 * euro_kur)
    
    e_vernik_mik = (baski_en * baski_boy * 0.25 * e_on_sayi) / 1000000 if e_vernik == "EVET" else 0
    e_vernik_gecis = (600 + (e_vernik_mik * 30 * dolar_kur) * 1.2) if e_vernik == "EVET" else 0
    
    e_uv_mik = (baski_en * baski_boy * 0.7 * e_on_sayi) / 1000000 if e_uv == "EVET" else 0
    e_uv_fiyat = (e_uv_mik * 8 * euro_kur + 3000) if e_uv == "EVET" else 0
    
    e_disp_fiyat = (1500 + (kagit_en * kagit_boy * baski_brut * 4 / 10000000 * 3 * euro_kur * 3)) if e_disp == "EVET" else 0
    e_kaucuk_fiyat = 3000 if e_kaucuk == "EVET" else 0

    e_toplam = e_on_setup + e_arka_setup + e_on_tiraj + e_arka_tiraj + e_vernik_gecis + e_disp_fiyat + e_kaucuk_fiyat + e_murekkep_fiyat + e_uv_fiyat
    st.info(f"Karton Toplam: {e_toplam:,.2f} ₺")

# --- METALİZE BASKI ---
with col_metalize:
    st.subheader("⬜ Metalize Baskı (F)")
    f_on_baski = st.selectbox("Ön Baskı (F7)", ["EVET", "HAYIR"], index=1)
    f_arka_baski = st.selectbox("Arka Baskı (F8)", ["EVET", "HAYIR"], index=1)
    f_boya_turu = st.selectbox("Boya Türü (F9)", ["CMYK", "PANTONE"])
    f_on_kalip = st.number_input("Ön Kalıp (F10)", value=0)
    f_arka_kalip = st.number_input("Arka Kalıp (F11)", value=0)
    f_vernik = st.selectbox("Vernik (F12)", ["EVET", "HAYIR"], index=1)
    f_uv = st.selectbox("UV Lak (F13)", ["EVET", "HAYIR"], index=1)
    f_disp = st.selectbox("Dispersiyon (F14)", ["EVET", "HAYIR"], index=1)
    f_kaucuk = st.selectbox("Kauçuk (F15)", ["EVET", "HAYIR"], index=1)

    # Hesaplamalar
    f_on_sayi = hesapla_baski_sayisi(f_on_baski, baski_brut)
    f_on_setup = hesapla_setup(f_on_baski, f_on_kalip, "METALIZE")
    f_on_tiraj = hesapla_tiraj(f_on_sayi, f_on_kalip, "METALIZE")

    f_arka_sayi = hesapla_baski_sayisi(f_arka_baski, baski_brut)
    f_arka_setup = hesapla_setup(f_arka_baski, f_arka_kalip, "METALIZE")
    f_arka_tiraj = hesapla_tiraj(f_arka_sayi, f_arka_kalip, "METALIZE")
    
    f_boya_mik = (baski_en * baski_boy * 0.2 * f_on_sayi) / 1000000
    f_murekkep_fiyat = (f_boya_mik * 17 * euro_kur) if f_boya_turu == "CMYK" else (f_boya_mik * 28 * euro_kur)
    
    f_vernik_mik = (baski_en * baski_boy * 0.25 * f_on_sayi) / 1000000 if f_vernik == "EVET" else 0
    f_vernik_gecis = (600 + (f_vernik_mik * 30 * dolar_kur) * 1.2) if f_vernik == "EVET" else 0
    
    f_uv_mik = (baski_en * baski_boy * 0.7 * f_on_sayi) / 1000000 if f_uv == "EVET" else 0
    f_uv_fiyat = (f_uv_mik * 8 * euro_kur + 3000) if f_uv == "EVET" else 0
    
    f_disp_fiyat = (1500 + (kagit_en * kagit_boy * kagit_brut * 4 / 10000000 * 3 * euro_kur * 3)) if f_disp == "EVET" else 0
    f_kaucuk_fiyat = 3000 if f_kaucuk == "EVET" else 0
    
    f_toplam = f_on_setup + f_arka_setup + f_on_tiraj + f_arka_tiraj + f_vernik_gecis + f_disp_fiyat + f_kaucuk_fiyat + f_murekkep_fiyat + f_uv_fiyat
    st.info(f"Metalize Toplam: {f_toplam:,.2f} ₺")

st.markdown("---")

# ==========================================
# ✨ 3. BÖLÜM: SELEFON HESABI (YENİ EKLENEN)
# ==========================================
st.header("✨ 3. Selefon Hesabı (G5-I11)")
col_sel1, col_sel2, col_sel3 = st.columns(3)

with col_sel1:
    # H6: Tedarikçi Firma
    sel_tedarikci = st.selectbox("Tedarikçi (H6)", ["SÜPER", "TEKNİK"])
    # H7: Selefon Türü
    sel_tur = st.selectbox("Selefon Türü (H7)", ["PARLAK", "MAT", "METALİZE", "ÇİZİLMEZ"])

with col_sel2:
    # H9: Selefon Yönü
    sel_yon = st.selectbox("Selefon Yönü (H9)", ["TEK YÜZ", "ÇİFT YÜZ"])
    # G10/H10: Adet (Otomatik B9'dan geliyor)
    st.info(f"Adet (H10): {baski_brut}")

# H8: Metrekare Fiyatı Hesaplama (Sözlük Yapısı ile)
# Excel'deki VE(H6=...; H7=...) mantığının Python hali
fiyat_listesi = {
    ("SÜPER", "PARLAK"): 0.10,
    ("SÜPER", "MAT"): 0.11,
    ("SÜPER", "METALİZE"): 0.18,
    ("SÜPER", "ÇİZİLMEZ"): 0.42,
    ("TEKNİK", "PARLAK"): 0.13,
    ("TEKNİK", "MAT"): 0.14,
    ("TEKNİK", "METALİZE"): 0.20,
    ("TEKNİK", "ÇİZİLMEZ"): 0.60
}

# Seçilen kombinasyona göre fiyatı çek, yoksa 0 döndür
sel_m2_fiyat = fiyat_listesi.get((sel_tedarikci, sel_tur), 0.0)

with col_sel3:
    st.metric("m² Fiyatı ($) (H8)", f"{sel_m2_fiyat} $")

# H11: TOPLAM FİYAT HESAPLAMA
# Formül: (H5/100) * (I5/100) * H8 * H10 * S3
# Eğer Çift Yüz ise * 2
sel_alan_hesabi = (kagit_en / 100) * (kagit_boy / 100) * sel_m2_fiyat * baski_brut * dolar_kur

if sel_yon == "ÇİFT YÜZ":
    sel_toplam_tutar = sel_alan_hesabi * 2
else:
    sel_toplam_tutar = sel_alan_hesabi

st.success(f"Selefon Toplam Fiyat (H11): {sel_toplam_tutar:,.2f} ₺")

st.markdown("---")

# ==========================================
# 💰 GENEL SONUÇ
# ==========================================
st.header("💰 Genel Toplam")
genel_toplam = kagit_toplam_tutar + e_toplam + f_toplam + sel_toplam_tutar

col_res1, col_res2 = st.columns(2)
with col_res1:
    st.write(f"Kağıt Maliyeti: {kagit_toplam_tutar:,.2f} ₺")
    st.write(f"Karton Baskı Maliyeti: {e_toplam:,.2f} ₺")
    st.write(f"Metalize Baskı Maliyeti: {f_toplam:,.2f} ₺")
    st.write(f"Selefon Maliyeti: {sel_toplam_tutar:,.2f} ₺")
with col_res2:
    st.metric("TOPLAM MALİYET", f"{genel_toplam:,.2f} ₺")
    st.metric("BİRİM MALİYET", f"{genel_toplam/siparis_adedi:,.2f} ₺")

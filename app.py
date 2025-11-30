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
    st.info("Formüllerdeki S3 (Dolar) ve S4/Q4 (Euro) değerleri buradan çekilir.")

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
    kagit_en = st.number_input("Kağıt En (B5)", value=70.0) # B5
    kagit_boy = st.number_input("Kağıt Boy (C5)", value=100.0) # C5
    gramaj = st.number_input("Kağıt Gramaj (B7)", value=350) # B7

with k2:
    kagit_brut = st.number_input("Kağıt Brüt Tabaka (B8)", value=1000, step=100) # B8
    baski_brut = st.number_input("Baskı Brüt Tabaka (B9)", value=1000, step=100) # B9
    verimlilik = st.number_input("Baskı Verimlilik (B10)", value=100) # B10

with k3:
    siparis_adedi = st.number_input("Sipariş Ürün Adedi (B11)", value=5000) # B11
    kur_secimi = st.selectbox("Kağıt Kur (B12)", ["DOLAR", "EURO", "TL"]) # B12
    kagit_birim_fiyat = st.number_input("Kağıt Fiyatı (B13)", value=800.0) # B13

# --- KAĞIT HESAPLAMALARI ---
# B14: Toplam Kilo Formülü: =B5*C5*B7*B8/10000000
toplam_kilo = (kagit_en * kagit_boy * gramaj * kagit_brut) / 10000000

# Kağıt Toplam Maliyeti (Excel'de formülünü yazmamıştın ama genelde şöyledir: Kilo * Fiyat * Kur)
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
st.header("🎨 2. Baskı Hesabı (Karton & Metalize)")

# Ortak Girdiler
col_baski_ebat1, col_baski_ebat2 = st.columns(2)
with col_baski_ebat1:
    baski_en = st.number_input("Baskı Ebadı En (E5)", value=70.0) # E5
with col_baski_ebat2:
    baski_boy = st.number_input("Baskı Ebadı Boy (F5)", value=100.0) # F5

# Ekranı İkiye Bölüyoruz: KARTON (E Sütunu) vs METALİZE (F Sütunu)
col_karton, col_metalize = st.columns(2)

# --- FONKSİYONLAR (Excel Formüllerinin Python Hali) ---
def hesapla_baski_sayisi(evet_hayir, brut_tabaka):
    return brut_tabaka if evet_hayir == "EVET" else 0

def hesapla_setup(evet_hayir, kalip_sayisi, tip="KARTON"):
    if evet_hayir == "HAYIR":
        return 0
    # Karton Mantığı
    if tip == "KARTON":
        if 6 <= kalip_sayisi < 10: return 6000
        else: return 3000
    # Metalize Mantığı
    else:
        if 6 <= kalip_sayisi < 10: return 12000
        else: return 6000

def hesapla_tiraj(baski_sayisi, kalip_sayisi, tip="KARTON"):
    if baski_sayisi <= 1000:
        return 0
    fark = baski_sayisi - 1000
    if tip == "KARTON":
        if 6 <= kalip_sayisi < 10: return fark * 0.8 * 2
        else: return fark * 0.8
    else: # Metalize
        if 6 <= kalip_sayisi < 10: return fark * 1.3 * 2
        else: return fark * 1.3

# ==========================================
# 🟫 KARTON BASKI (E SÜTUNU)
# ==========================================
with col_karton:
    st.subheader("🟫 Karton Baskı (E)")
    
    # Girdiler
    e_on_baski = st.selectbox("Ön Baskı (E7)", ["EVET", "HAYIR"], index=0)
    e_arka_baski = st.selectbox("Arka Baskı (E8)", ["EVET", "HAYIR"], index=1)
    e_boya_turu = st.selectbox("Boya Türü (E9)", ["CMYK", "PANTONE"])
    e_on_kalip = st.number_input("Ön Kalıp Adedi (D10)", value=4)
    e_arka_kalip = st.number_input("Arka Kalıp Adedi (E11)", value=0)
    
    e_vernik = st.selectbox("Vernik (E12)", ["EVET", "HAYIR"], index=1)
    e_uv = st.selectbox("UV Lak (E13)", ["EVET", "HAYIR"], index=1)
    e_disp = st.selectbox("Dispersiyon (E14)", ["EVET", "HAYIR"], index=1)
    e_kaucuk = st.selectbox("Kauçuk (E15)", ["EVET", "HAYIR"], index=1)

    # --- HESAPLAMALAR (Sırayla) ---
    
    # 1. Baskı Sayıları (E16, E17)
    e_on_sayi = hesapla_baski_sayisi(e_on_baski, baski_brut)
    e_arka_sayi = hesapla_baski_sayisi(e_arka_baski, baski_brut)
    
    # 2. Setup (E18, E19)
    e_on_setup = hesapla_setup(e_on_baski, e_on_kalip, "KARTON")
    e_arka_setup = hesapla_setup(e_arka_baski, e_arka_kalip, "KARTON")
    
    # 3. Tiraj (E20, E21)
    e_on_tiraj = hesapla_tiraj(e_on_sayi, e_on_kalip, "KARTON")
    e_arka_tiraj = hesapla_tiraj(e_arka_sayi, e_arka_kalip, "KARTON")
    
    # 4. Miktarlar (E25, E26, E27)
    # E27 Boya Miktarı: E5*F5*0,2*E16/1000000
    e_boya_mik = (baski_en * baski_boy * 0.2 * e_on_sayi) / 1000000
    # E26 Vernik Miktarı: E5*F5*0,25*E16/1000000 (Eğer EVET ise)
    e_vernik_mik = (baski_en * baski_boy * 0.25 * e_on_sayi) / 1000000 if e_vernik == "EVET" else 0
    # E25 UV Lak Miktarı: E5*F5*0,7*E16/1000000 (Eğer EVET ise)
    e_uv_mik = (baski_en * baski_boy * 0.7 * e_on_sayi) / 1000000 if e_uv == "EVET" else 0
    
    # 5. Fiyatlar (Maliyetler)
    # E28 Tüketilen Mürekkep: CMYK ise *17*S4, değilse *28*S4
    e_murekkep_fiyat = (e_boya_mik * 17 * euro_kur) if e_boya_turu == "CMYK" else (e_boya_mik * 28 * euro_kur)
    
    # E22 Vernik Geçiş: 600+(E26*30*S3)*1,2
    e_vernik_gecis = (600 + (e_vernik_mik * 30 * dolar_kur) * 1.2) if e_vernik == "EVET" else 0
    
    # E29 UV Lak Fiyatı: E25*8*S4+3000
    e_uv_fiyat = (e_uv_mik * 8 * euro_kur + 3000) if e_uv == "EVET" else 0
    
    # E23 Dispersiyon: 1500 + KağıtAlan * KağıtAdet * 4 / 10m * 3 * S4 * 3
    # Not: Formül B5*C5*B9 kullanıyor.
    e_disp_fiyat = (1500 + (kagit_en * kagit_boy * baski_brut * 4 / 10000000 * 3 * euro_kur * 3)) if e_disp == "EVET" else 0
    
    # E24 Kauçuk: 3000
    e_kaucuk_fiyat = 3000 if e_kaucuk == "EVET" else 0

    # 6. TOPLAM (E30)
    e_toplam = e_on_setup + e_arka_setup + e_on_tiraj + e_arka_tiraj + e_vernik_gecis + e_disp_fiyat + e_kaucuk_fiyat + e_murekkep_fiyat + e_uv_fiyat

    st.info(f"Karton Toplam (E30): {e_toplam:,.2f} ₺")
    with st.expander("Detaylar"):
        st.write(f"Ön Setup: {e_on_setup}")
        st.write(f"Ön Tiraj: {e_on_tiraj:.2f}")
        st.write(f"Mürekkep: {e_murekkep_fiyat:.2f}")
        st.write(f"UV Fiyat: {e_uv_fiyat:.2f}")

# ==========================================
# ⬜ METALİZE BASKI (F SÜTUNU)
# ==========================================
with col_metalize:
    st.subheader("⬜ Metalize Baskı (F)")
    
    # Girdiler
    f_on_baski = st.selectbox("Ön Baskı (F7)", ["EVET", "HAYIR"], index=1)
    f_arka_baski = st.selectbox("Arka Baskı (F8)", ["EVET", "HAYIR"], index=1)
    f_boya_turu = st.selectbox("Boya Türü (F9)", ["CMYK", "PANTONE"])
    f_on_kalip = st.number_input("Ön Kalıp Adedi (F10)", value=0)
    f_arka_kalip = st.number_input("Arka Kalıp Adedi (F11)", value=0)
    
    f_vernik = st.selectbox("Vernik (F12)", ["EVET", "HAYIR"], index=1)
    f_uv = st.selectbox("UV Lak (F13)", ["EVET", "HAYIR"], index=1)
    f_disp = st.selectbox("Dispersiyon (F14)", ["EVET", "HAYIR"], index=1)
    f_kaucuk = st.selectbox("Kauçuk (F15)", ["EVET", "HAYIR"], index=1)

    # --- HESAPLAMALAR ---
    
    # 1. Baskı Sayıları
    f_on_sayi = hesapla_baski_sayisi(f_on_baski, baski_brut)
    f_arka_sayi = hesapla_baski_sayisi(f_arka_baski, baski_brut)
    
    # 2. Setup
    f_on_setup = hesapla_setup(f_on_baski, f_on_kalip, "METALIZE")
    f_arka_setup = hesapla_setup(f_arka_baski, f_arka_kalip, "METALIZE")
    
    # 3. Tiraj
    f_on_tiraj = hesapla_tiraj(f_on_sayi, f_on_kalip, "METALIZE")
    f_arka_tiraj = hesapla_tiraj(f_arka_sayi, f_arka_kalip, "METALIZE")
    
    # 4. Miktarlar
    f_boya_mik = (baski_en * baski_boy * 0.2 * f_on_sayi) / 1000000
    f_vernik_mik = (baski_en * baski_boy * 0.25 * f_on_sayi) / 1000000 if f_vernik == "EVET" else 0
    f_uv_mik = (baski_en * baski_boy * 0.7 * f_on_sayi) / 1000000 if f_uv == "EVET" else 0
    
    # 5. Fiyatlar
    # Not: Q4 yerine Euro kuru (S4) kullandık.
    f_murekkep_fiyat = (f_boya_mik * 17 * euro_kur) if f_boya_turu == "CMYK" else (f_boya_mik * 28 * euro_kur)
    
    f_vernik_gecis = (600 + (f_vernik_mik * 30 * dolar_kur) * 1.2) if f_vernik == "EVET" else 0
    f_uv_fiyat = (f_uv_mik * 8 * euro_kur + 3000) if f_uv == "EVET" else 0
    
    # Dispersiyon Metalize: 1500+C5*D5*C8*4/10000000*3*Q4*3
    # Formülde C5, D5, C8 kullanılmış. Bu muhtemelen kağıt ebat ve brüt kağıt.
    # Bizim değişkenlerimizde: kagit_en, kagit_boy, kagit_brut.
    f_disp_fiyat = (1500 + (kagit_en * kagit_boy * kagit_brut * 4 / 10000000 * 3 * euro_kur * 3)) if f_disp == "EVET" else 0
    
    f_kaucuk_fiyat = 3000 if f_kaucuk == "EVET" else 0

    # 6. TOPLAM (F30)
    f_toplam = f_on_setup + f_arka_setup + f_on_tiraj + f_arka_tiraj + f_vernik_gecis + f_disp_fiyat + f_kaucuk_fiyat + f_murekkep_fiyat + f_uv_fiyat

    st.info(f"Metalize Toplam (F30): {f_toplam:,.2f} ₺")
    with st.expander("Detaylar"):
        st.write(f"Ön Setup: {f_on_setup}")
        st.write(f"Ön Tiraj: {f_on_tiraj:.2f}")
        st.write(f"Mürekkep: {f_murekkep_fiyat:.2f}")

st.markdown("---")

# ==========================================
# 💰 GENEL SONUÇ
# ==========================================
st.header("💰 Genel Toplam")
genel_toplam = kagit_toplam_tutar + e_toplam + f_toplam

col_res1, col_res2 = st.columns(2)
with col_res1:
    st.write(f"Kağıt Maliyeti: {kagit_toplam_tutar:,.2f} ₺")
    st.write(f"Karton Baskı Maliyeti: {e_toplam:,.2f} ₺")
    st.write(f"Metalize Baskı Maliyeti: {f_toplam:,.2f} ₺")
with col_res2:
    st.metric("TOPLAM MALİYET", f"{genel_toplam:,.2f} ₺")
    st.metric("BİRİM MALİYET", f"{genel_toplam/siparis_adedi:,.2f} ₺")

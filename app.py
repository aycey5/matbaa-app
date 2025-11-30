import streamlit as st

# ==========================================
# ⚙️ AYARLAR VE KURLAR (SIDEBAR)
# ==========================================
st.set_page_config(page_title="Matbaa Maliyet Hesaplayıcı", layout="wide", page_icon="🖨️")

with st.sidebar:
    st.header("⚙️ Döviz Kurları")
    dolar_kur = st.number_input("Dolar Kuru ($) - S3", value=34.50, step=0.01, format="%.2f")
    euro_kur = st.number_input("Euro Kuru (€) - S4", value=37.20, step=0.01, format="%.2f")
    sterlin_kur = st.number_input("Sterlin Kuru (£)", value=43.50, step=0.01, format="%.2f")
    
    st.divider()
    
    st.header("📈 Kâr Ayarı")
    kar_orani = st.number_input("Kâr Oranı (%) - N17", value=30, step=1)
    
    st.divider()
    teklif_para_birimi = st.selectbox("Satış Para Birimi (N23)", ["TL", "DOLAR", "EURO", "STERLIN"])
    
    st.info("Formüllerdeki S3, S4 değerleri ve Kâr buradan çekilir.")

st.title("🖨️ Matbaa Üretim & Maliyet Hesabı (PRO)")
st.markdown("---")

# ==========================================
# 📝 İŞ BİLGİLERİ
# ==========================================
col_info1, col_info2 = st.columns(2)
with col_info1:
    musteri_adi = st.text_input("Müşteri Adı (B1)", "Örnek Müşteri A.Ş.")
with col_info2:
    isin_adi = st.text_input("İşin Adı (B2)", "Özel Kutu Basımı")

st.markdown("---")

# ==========================================
# 📦 1. BÖLÜM: KAĞIT HESABI
# ==========================================
st.header("📦 1. Kağıt Hesabı")
k1, k2, k3, k4 = st.columns(4)

with k1:
    kagit_en = st.number_input("Kağıt En (cm) (B5)", value=70.0) 
    kagit_boy = st.number_input("Kağıt Boy (cm) (C5)", value=100.0) 
    gramaj = st.number_input("Kağıt Gramaj (B7)", value=350) 

with k2:
    kagit_brut = st.number_input("Kağıt Brüt Tabaka (B8)", value=1000, step=100) 
    baski_brut = st.number_input("Baskı Brüt Tabaka (B9)", value=1000, step=100) 
    verimlilik = st.number_input("Baskı Verimlilik (B10)", value=100) 

with k3:
    siparis_adedi = st.number_input("Sipariş Ürün Adedi (B11)", value=5000) 
    kur_secimi = st.selectbox("Kağıt Kur (B12)", ["DOLAR", "EURO", "TL"]) 
    kagit_birim_fiyat = st.number_input("Kağıt Fiyatı (B13)", value=800.0) 

# Hesaplamalar
toplam_kilo = (kagit_en * kagit_boy * gramaj * kagit_brut) / 10000000
secilen_kur_degeri = 1.0
if kur_secimi == "DOLAR": secilen_kur_degeri = dolar_kur
elif kur_secimi == "EURO": secilen_kur_degeri = euro_kur
kagit_toplam_tutar = (kagit_birim_fiyat / 1000) * toplam_kilo * secilen_kur_degeri

with k4:
    st.metric("Toplam Kilo (B14)", f"{toplam_kilo:.2f} kg")
    st.metric("Kağıt Tutarı (N3)", f"{kagit_toplam_tutar:,.2f} ₺")

st.markdown("---")

# ==========================================
# 🎨 2. BÖLÜM: BASKI HESABI
# ==========================================
st.header("🎨 2. Baskı Hesabı")

col_baski_ebat1, col_baski_ebat2 = st.columns(2)
with col_baski_ebat1:
    baski_en = st.number_input("Baskı Ebadı En (B6/E5)", value=70.0)
with col_baski_ebat2:
    baski_boy = st.number_input("Baskı Ebadı Boy (C6/F5)", value=100.0)

col_karton, col_metalize = st.columns(2)

# Fonksiyonlar
def hesapla_baski_sayisi(evet_hayir, brut_tabaka):
    return brut_tabaka if evet_hayir == "EVET" else 0

def hesapla_setup(evet_hayir, kalip_sayisi, tip="KARTON"):
    if evet_hayir == "HAYIR": return 0
    if tip == "KARTON": return 6000 if 6 <= kalip_sayisi < 10 else 3000
    else: return 12000 if 6 <= kalip_sayisi < 10 else 6000

def hesapla_tiraj(baski_sayisi, kalip_sayisi, tip="KARTON"):
    if baski_sayisi <= 1000: return 0
    fark = baski_sayisi - 1000
    carpan = 2 if 6 <= kalip_sayisi < 10 else 1
    birim = 0.8 if tip == "KARTON" else 1.3
    return fark * birim * carpan

# Karton Baskı
with col_karton:
    st.subheader("🟫 Karton Baskı")
    e_on_baski = st.selectbox("Ön Baskı", ["EVET", "HAYIR"], index=0, key="e_on")
    e_arka_baski = st.selectbox("Arka Baskı", ["EVET", "HAYIR"], index=1, key="e_arka")
    e_boya_turu = st.selectbox("Boya Türü", ["CMYK", "PANTONE"], key="e_boya")
    e_on_kalip = st.number_input("Ön Kalıp", value=4, key="e_on_k")
    e_arka_kalip = st.number_input("Arka Kalıp", value=0, key="e_arka_k")
    
    # Ekstralar
    e_vernik = st.selectbox("Vernik", ["EVET", "HAYIR"], index=1, key="e_ver")
    e_uv = st.selectbox("UV Lak", ["EVET", "HAYIR"], index=1, key="e_uv")
    e_disp = st.selectbox("Dispersiyon", ["EVET", "HAYIR"], index=1, key="e_disp")
    e_kaucuk = st.selectbox("Kauçuk", ["EVET", "HAYIR"], index=1, key="e_kau")

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
    st.info(f"Karton Toplam (E30): {e_toplam:,.2f} ₺")

# Metalize Baskı
with col_metalize:
    st.subheader("⬜ Metalize Baskı")
    f_on_baski = st.selectbox("Ön Baskı", ["EVET", "HAYIR"], index=1, key="f_on")
    f_arka_baski = st.selectbox("Arka Baskı", ["EVET", "HAYIR"], index=1, key="f_arka")
    f_boya_turu = st.selectbox("Boya Türü", ["CMYK", "PANTONE"], key="f_boya")
    f_on_kalip = st.number_input("Ön Kalıp", value=0, key="f_on_k")
    f_arka_kalip = st.number_input("Arka Kalıp", value=0, key="f_arka_k")
    f_vernik = st.selectbox("Vernik", ["EVET", "HAYIR"], index=1, key="f_ver")
    f_uv = st.selectbox("UV Lak", ["EVET", "HAYIR"], index=1, key="f_uv")
    f_disp = st.selectbox("Dispersiyon", ["EVET", "HAYIR"], index=1, key="f_disp")
    f_kaucuk = st.selectbox("Kauçuk", ["EVET", "HAYIR"], index=1, key="f_kau")

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
    st.info(f"Metalize Toplam (F30): {f_toplam:,.2f} ₺")

st.markdown("---")

# ==========================================
# ✨ 3. BÖLÜM: DIŞ İŞLEMLER (SOFT TOUCH DAHİL)
# ==========================================
st.header("✨ 3. Dış İşlemler & Ekstralar")

tab1, tab2, tab3, tab4 = st.tabs(["Selefon & Soft Touch", "Sıvama & Ondüle", "Yaldız & Serigraf", "Manuel Ekstralar"])

with tab1:
    col_sel, col_soft = st.columns(2)
    
    # --- SELEFON (N6) ---
    with col_sel:
        st.subheader("🔹 Selefon")
        sel_tedarikci = st.selectbox("Tedarikçi", ["SÜPER", "TEKNİK"])
        sel_tur = st.selectbox("Selefon Türü", ["PARLAK", "MAT", "METALİZE", "ÇİZİLMEZ"])
        sel_yon = st.selectbox("Selefon Yönü", ["TEK YÜZ", "ÇİFT YÜZ"])
        
        fiyat_listesi_sel = {
            ("SÜPER", "PARLAK"): 0.10, ("SÜPER", "MAT"): 0.11,
            ("SÜPER", "METALİZE"): 0.18, ("SÜPER", "ÇİZİLMEZ"): 0.42,
            ("TEKNİK", "PARLAK"): 0.13, ("TEKNİK", "MAT"): 0.14,
            ("TEKNİK", "METALİZE"): 0.20, ("TEKNİK", "ÇİZİLMEZ"): 0.60
        }
        sel_m2_fiyat = fiyat_listesi_sel.get((sel_tedarikci, sel_tur), 0.0)
        sel_alan = (kagit_en / 100) * (kagit_boy / 100) * sel_m2_fiyat * baski_brut * dolar_kur
        sel_toplam_tutar = sel_alan * 2 if sel_yon == "ÇİFT YÜZ" else sel_alan
        st.success(f"Selefon Tutarı (N6): {sel_toplam_tutar:,.2f} ₺")

    # --- SOFT TOUCH LAK (N7, N8) ---
    with col_soft:
        st.subheader("🔹 Soft Touch Lak")
        soft_touch = st.selectbox("Soft Touch Uygula (N7)", ["HAYIR", "EVET"])
        
        soft_touch_fiyat = 0
        if soft_touch == "EVET":
            # N8 Formülü: 1500 + B6 * C6 * B9 * 4 / 10.000.000 * 15 * S4 * 3
            # Not: B6=BaskıEn, C6=BaskıBoy, B9=BaskıBrüt, S4=Euro
            soft_touch_fiyat = 1500 + (baski_en * baski_boy * baski_brut * 4 / 10000000 * 15 * euro_kur * 3)
            
        st.success(f"Soft Touch Geçişi (N8): {soft_touch_fiyat:,.2f} ₺")

with tab2:
    col_siv, col_ondu = st.columns(2)
    # --- SIVAMA (N4) ---
    with col_siv:
        st.subheader("🔹 Sıvama")
        sivama_sekli = st.selectbox("Sıvama Şekli", ["YOK", "TEK YÜZ ONDÜLE", "ÇİFT YÜZ ONDÜLE", "KARTON+KARTON"])
        sivama_fiyat = 0
        if sivama_sekli == "TEK YÜZ ONDÜLE": sivama_fiyat = (kagit_en/100)*(kagit_boy/100)*baski_brut*3.3
        elif sivama_sekli == "ÇİFT YÜZ ONDÜLE": sivama_fiyat = (kagit_en/100)*(kagit_boy/100)*baski_brut*6.6
        elif sivama_sekli == "KARTON+KARTON": sivama_fiyat = (kagit_en/100)*(kagit_boy/100)*baski_brut*4.4
        st.success(f"Sıvama (N4): {sivama_fiyat:,.2f} ₺")

    # --- ONDÜLE (N12 - Manuel) ---
    with col_ondu:
        st.subheader("🔹 Ondüle Manuel")
        ondule_manuel = st.number_input("Ondüle Toplam Fiyat (N12)", value=0.0)
        st.success(f"Ondüle (N12): {ondule_manuel:,.2f} ₺")

with tab3:
    col_seri, col_yaldiz, col_gofre = st.columns(3)
    # --- SERİGRAF (N9) ---
    with col_seri:
        st.subheader("Serigraf (N9)")
        lak_turu = st.selectbox("Lak Türü", ["YOK", "KISMİ LAK", "EMBOS LAK"])
        serigraf_fiyat = 0
        if lak_turu == "KISMİ LAK": serigraf_fiyat = 1000 + (baski_brut * 0.6)
        elif lak_turu == "EMBOS LAK": serigraf_fiyat = 1000 + (baski_brut * 1.5)
        st.write(f"Tutar: {serigraf_fiyat:,.2f} ₺")

    # --- YALDIZ (N10) ---
    with col_yaldiz:
        st.subheader("Yaldız (N10)")
        if st.checkbox("Yaldız Ekle"):
            y_en = st.number_input("En", value=10.0)
            y_boy = st.number_input("Boy", value=5.0)
            y_k_adet = st.number_input("Klişe Adet", value=1)
            y_b_adet = st.number_input("Baskı Adet", value=baski_brut)
            
            y_gecis = 2000 if y_b_adet <= 1000 else (y_b_adet - 1000) * 0.8 + 2000
            y_sarf = (y_en/100)*(y_boy/100)*y_b_adet*y_k_adet*0.185*dolar_kur
            y_klise = y_en*y_boy*5.5*y_k_adet
            yaldiz_toplam = y_gecis + y_sarf + y_klise
            st.write(f"Tutar: {yaldiz_toplam:,.2f} ₺")
        else: yaldiz_toplam = 0

    # --- GOFRE (N11) ---
    with col_gofre:
        st.subheader("Gofre (N11)")
        if st.checkbox("Gofre Ekle"):
            g_en = st.number_input("G. En", value=10.0)
            g_boy = st.number_input("G. Boy", value=5.0)
            g_adet = st.number_input("G. Adet", value=1)
            g_tur = st.selectbox("Tür", ["NORMAL", "BRAILLE"])
            carpan = 11 if g_tur=="NORMAL" else 4
            gofre_fiyat = g_en*g_boy*carpan*g_adet
            st.write(f"Tutar: {gofre_fiyat:,.2f} ₺")
        else: gofre_fiyat = 0

with tab4:
    col_man1, col_man2 = st.columns(2)
    # --- MANUEL GİDERLER (N12, N13) ---
    with col_man1:
        st.subheader("🔹 Manuel Giderler")
        bicak_manuel = st.number_input("Bıçak Maliyeti (N12)", value=0.0)
        
        st.caption("Asetat Pencere (N13)")
        asetat_birim = st.number_input("Asetat Birim Fiyat", value=0.0)
        asetat_toplam = asetat_birim * siparis_adedi
        st.write(f"Asetat Toplam: {asetat_toplam:,.2f} ₺")
    
    with col_man2:
        pass

st.markdown("---")

# ==========================================
# ✂️ 4. BÖLÜM: KESİM VE YAPIŞTIRMA (İÇ MALİYET)
# ==========================================
st.header("✂️ 4. Kesim ve Yapıştırma (İç Maliyet)")
col_kesim, col_yap = st.columns(2)

# KESİM (P6)
with col_kesim:
    kesim_sekli = st.selectbox("Kesim Şekli", ["BOBST KESİM", "GOFRELİ KESİM", "SIVAMALI KESİM", "AYIKLAMALI KESİM"])
    kesim_adet = baski_brut
    k_data = {"BOBST KESİM": [2500, 0.75], "GOFRELİ KESİM": [3000, 0.80], 
              "SIVAMALI KESİM": [3000, 1.50], "AYIKLAMALI KESİM": [4500, 0.85]}
    k_taban, k_carpan = k_data.get(kesim_sekli, [0, 0])
    kesim_fiyat = k_taban if kesim_adet <= 2000 else k_taban + (kesim_adet - 2000) * k_carpan
    st.success(f"Kesim (P6): {kesim_fiyat:,.2f} ₺")

# YAPIŞTIRMA (P7)
with col_yap:
    yap_sekli = st.selectbox("Yapıştırma Şekli", ["YAN YAPIŞTIRMA", "YAN DİP YAPIŞTIRMA", "KONİK DİP YAPIŞTIRMA", 
                                                  "ÜST SÜRME YAPIŞTIRMA", "4 NOKTA YAPIŞTIRMA", "6 NOKTA YAPIŞTIRMA"])
    yap_adet = siparis_adedi
    y_data = {"YAN YAPIŞTIRMA": [1500, 0.15], "YAN DİP YAPIŞTIRMA": [3000, 0.25], 
              "KONİK DİP YAPIŞTIRMA": [5500, 0.55], "ÜST SÜRME YAPIŞTIRMA": [3000, 0.35],
              "4 NOKTA YAPIŞTIRMA": [7500, 0.75], "6 NOKTA YAPIŞTIRMA": [10000, 0.90]}
    y_taban, y_carpan = y_data.get(yap_sekli, [0, 0])
    yapistirma_fiyat = y_taban if yap_adet <= 5000 else y_taban + (yap_adet - 5000) * y_carpan
    st.success(f"Yapıştırma (P7): {yapistirma_fiyat:,.2f} ₺")

st.markdown("---")

# ==========================================
# 🚛 5. BÖLÜM: LOJİSTİK VE GÜMRÜK (N14-N16)
# ==========================================
st.header("🚛 5. Lojistik ve Gümrük")
col_loj1, col_loj2, col_loj3 = st.columns(3)

with col_loj1:
    st.subheader("Koli & Palet (N14)")
    koli_adedi = st.number_input("Koli Sayısı", value=0)
    palet_adedi = st.number_input("Palet Sayısı", value=0)
    # Formül: Koli*50 + Palet*600
    koli_palet_maliyet = (koli_adedi * 50) + (palet_adedi * 600)
    st.write(f"Tutar: {koli_palet_maliyet:,.2f} ₺")

with col_loj2:
    st.subheader("Gümrük & Navlun")
    gumruk_maliyet = st.number_input("Gümrük (N15)", value=4000.0)
    navlun_maliyet = st.number_input("Navlun (N16)", value=0.0)

with col_loj3:
    st.subheader("Navlun Sigortası (P8)")
    # Formül: Navlun * 0.01
    navlun_sigorta = navlun_maliyet * 0.01
    st.write(f"Tutar: {navlun_sigorta:,.2f} ₺")

st.markdown("---")

# ==========================================
# 💰 FİNAL HESAPLAMA (ÖZET TABLO)
# ==========================================
st.header("📊 FİNAL MALİYET VE SATIŞ RAPORU")

# 1. DIŞ MALİYETLER (N20)
# N20 = Topla(N2:N18)
# Kalemler: Kağıt(N3) + Sıvama(N4) + Metalize(Yok) + Selefon(N6) + SoftTouch(N8) + 
#           Serigraf(N9) + Yaldız(N10) + Gofre(N11) + Ondüle(N12) + Bıçak(N12) + 
#           Asetat(N13) + KoliPalet(N14) + Gümrük(N15) + Navlun(N16)
dis_maliyet_toplam = (kagit_toplam_tutar + sivama_fiyat + sel_toplam_tutar + soft_touch_fiyat +
                      serigraf_fiyat + yaldiz_toplam + gofre_fiyat + ondule_manuel + bicak_manuel +
                      asetat_toplam + koli_palet_maliyet + gumruk_maliyet + navlun_maliyet)

# 2. İÇ MALİYETLER (P20)
# P20 = Topla(P3:P7 + P8)
# Kalemler: KartonBaskı(P4) + MetalizeBaskı(P5) + Kesim(P6) + Yapıştırma(P7) + Sigorta(P8)
ic_maliyet_toplam = (e_toplam + f_toplam + kesim_fiyat + yapistirma_fiyat + navlun_sigorta)

# 3. GENEL TOPLAM (N21)
genel_toplam_tl = dis_maliyet_toplam + ic_maliyet_toplam

# 4. SATIŞ HESABI (N22)
# N22 = N21 + N21 * (Kar / 100)
toplam_satis_tl = genel_toplam_tl + (genel_toplam_tl * (kar_orani / 100))

# 5. BİRİM FİYATLAR (P21, P22)
birim_maliyet_tl = genel_toplam_tl / siparis_adedi
birim_satis_tl = toplam_satis_tl / siparis_adedi

# 6. DÖVİZ ÇEVRİM (N24, N25)
# Seçilen kura göre (N23)
satis_doviz_toplam = 0
satis_doviz_birim = 0
simge = "₺"

if teklif_para_birimi == "DOLAR":
    satis_doviz_toplam = toplam_satis_tl / dolar_kur
    satis_doviz_birim = birim_satis_tl / dolar_kur
    simge = "$"
elif teklif_para_birimi == "EURO":
    satis_doviz_toplam = toplam_satis_tl / euro_kur
    satis_doviz_birim = birim_satis_tl / euro_kur
    simge = "€"
elif teklif_para_birimi == "STERLIN":
    satis_doviz_toplam = toplam_satis_tl / sterlin_kur
    satis_doviz_birim = birim_satis_tl / sterlin_kur
    simge = "£"
else:
    satis_doviz_toplam = toplam_satis_tl
    satis_doviz_birim = birim_satis_tl
    simge = "₺"

# --- GÖRSELLEŞTİRME ---
c_final1, c_final2 = st.columns(2)

with c_final1:
    st.warning("📉 MALİYET DÖKÜMÜ")
    st.write(f"**DIŞ MALİYET (N20):** {dis_maliyet_toplam:,.2f} ₺")
    with st.expander("Dış Maliyet Detayları"):
        st.write(f"Kağıt: {kagit_toplam_tutar:,.2f}")
        st.write(f"Sıvama: {sivama_fiyat:,.2f}")
        st.write(f"Selefon + Soft Touch: {(sel_toplam_tutar+soft_touch_fiyat):,.2f}")
        st.write(f"Serigraf + Yaldız + Gofre: {(serigraf_fiyat+yaldiz_toplam+gofre_fiyat):,.2f}")
        st.write(f"Ondüle + Bıçak + Asetat: {(ondule_manuel+bicak_manuel+asetat_toplam):,.2f}")
        st.write(f"Lojistik (Koli/Gümrük/Navlun): {(koli_palet_maliyet+gumruk_maliyet+navlun_maliyet):,.2f}")

    st.write(f"**İÇ MALİYET (P20):** {ic_maliyet_toplam:,.2f} ₺")
    with st.expander("İç Maliyet Detayları"):
        st.write(f"Baskı (Karton+Metalize): {(e_toplam+f_toplam):,.2f}")
        st.write(f"Kesim: {kesim_fiyat:,.2f}")
        st.write(f"Yapıştırma: {yapistirma_fiyat:,.2f}")
        st.write(f"Sigorta: {navlun_sigorta:,.2f}")

    st.divider()
    st.error(f"**TOPLAM MALİYET (N21): {genel_toplam_tl:,.2f} ₺**")
    st.write(f"Birim Maliyet (P21): {birim_maliyet_tl:,.2f} ₺")

with c_final2:
    st.success(f"📈 SATIŞ VE TEKLİF ({teklif_para_birimi})")
    st.write(f"Kâr Oranı (N17): %{kar_orani}")
    st.write(f"Toplam Satış TL (N22): {toplam_satis_tl:,.2f} ₺")
    
    st.divider()
    st.metric("SATIŞ DÖVİZ TOPLAM (N24)", f"{satis_doviz_toplam:,.2f} {simge}")
    st.metric("SATIŞ BİRİM FİYAT (N25)", f"{satis_doviz_birim:,.3f} {simge}")

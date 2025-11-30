import streamlit as st

# ==========================================
# ⚙️ 0. AYARLAR VE SAYFA YAPISI
# ==========================================
st.set_page_config(page_title="Matbaa Maliyet Hesaplayıcı", layout="wide", page_icon="🖨️")

# --- KENAR ÇUBUĞU (KURLAR VE KÂR) ---
with st.sidebar:
    st.header("⚙️ Parametreler")
    st.write("Döviz Kurları (Güncelleyin)")
    
    # S3 ve S4 Hücreleri
    dolar_kur = st.number_input("Dolar Kuru ($) - S3", value=34.50, step=0.01, format="%.2f")
    euro_kur = st.number_input("Euro Kuru (€) - S4", value=37.20, step=0.01, format="%.2f")
    
    st.divider()
    
    # N19 Hücresi (Kâr Oranı)
    kar_orani = st.number_input("Kâr Oranı (%) - N19", value=20, step=1)
    
    # N23 Hücresi (Teklif Para Birimi)
    teklif_para_birimi = st.radio("Teklif Para Birimi (N23)", ["TL", "DOLAR", "EURO"])
    
    st.info("Hesaplamalar anlık olarak bu kurlara göre yapılır.")

st.title("🖨️ Matbaa Maliyet & Teklif Sistemi")
st.markdown("---")

# ==========================================
# 📦 1. BÖLÜM: KAĞIT (N3, B14 HESAPLARI)
# ==========================================
st.header("📦 1. Kağıt Özellikleri")
c_kagit1, c_kagit2, c_kagit3, c_kagit4 = st.columns(4)

with c_kagit1:
    kagit_en = st.number_input("Kağıt En (cm) - B5", value=70.0)
    kagit_boy = st.number_input("Kağıt Boy (cm) - C5", value=100.0)

with c_kagit2:
    gramaj = st.number_input("Gramaj (gr) - B7", value=350)
    # B11 Hücresi
    tabaka_sayisi = st.number_input("Tabaka Sayısı (B11)", value=1000, step=100)

with c_kagit3:
    # B12 Hücresi
    kagit_kur_tipi = st.selectbox("Kağıt Alış Kuru", ["TL", "DOLAR", "EURO"])
    # B13 Hücresi
    ton_fiyati = st.number_input("Kağıt Ton Fiyatı", value=800.0)

# --- KAĞIT FORMÜLLERİ ---
# B14: Toplam Kilo = En * Boy * Gramaj * Adet / 10.000.000
toplam_kilo = (kagit_en * kagit_boy * gramaj * tabaka_sayisi) / 10000000

# Kur Seçimi
secilen_kagit_kuru = 1.0
if kagit_kur_tipi == "DOLAR": secilen_kagit_kuru = dolar_kur
elif kagit_kur_tipi == "EURO": secilen_kagit_kuru = euro_kur

# N3: Kağıt Maliyeti = (TonFiyat / 1000) * Kilo * Kur
kagit_maliyeti = (ton_fiyati / 1000) * toplam_kilo * secilen_kagit_kuru

with c_kagit4:
    st.metric("Toplam Kağıt (kg)", f"{toplam_kilo:.2f} kg")
    st.metric("Kağıt Maliyeti", f"{kagit_maliyeti:,.2f} ₺")

st.markdown("---")

# ==========================================
# 🎨 2. BÖLÜM: BASKI (İÇ MALİYETLER)
# ==========================================
st.header("🎨 2. Baskı Maliyetleri")

# Baskı Hesaplama Fonksiyonu (Setup + Tiraj + Boya)
def baski_hesapla(tur, kalip_sayisi, adet):
    if kalip_sayisi == 0: return 0
    
    # 1. Setup Bedeli (E18, E19)
    # Kalıp < 6 ise 500 TL/kalıp, değilse 400 TL/kalıp (Örnek mantık, revize edilebilir)
    setup = 500 * kalip_sayisi if kalip_sayisi < 6 else 400 * kalip_sayisi
    
    # 2. Tiraj Bedeli (E20, E21 - İlk 1000 Ücretsiz)
    tiraj = 0
    if adet > 1000:
        tiraj = (adet - 1000) * 0.8 # Formüldeki 0.8 çarpanı
    
    # 3. Boya Bedeli (E27, E28)
    # Boya Miktarı = En * Boy * 0.2 * Adet / 1.000.000
    boya_miktari = (kagit_en * kagit_boy * 0.2 * adet) / 1000000
    
    # Boya Fiyatı (CMYK: 17 Euro, Special: 28 Euro)
    birim_boya_fiyat = 17 * euro_kur if tur == "CMYK" else 28 * euro_kur
    boya_tutari = boya_miktari * birim_boya_fiyat
    
    return setup + tiraj + boya_tutari

c_baski1, c_baski2, c_baski3 = st.columns(3)

# Ön Baskı
with c_baski1:
    st.subheader("Ön Baskı")
    if st.checkbox("Ön Baskı Var mı?", value=True):
        on_kalip = st.number_input("Ön Kalıp Sayısı", 0, 10, 4)
        on_tur = st.selectbox("Ön Boya Türü", ["CMYK", "Special"])
        on_maliyet = baski_hesapla(on_tur, on_kalip, tabaka_sayisi)
    else: on_maliyet = 0

# Arka Baskı
with c_baski2:
    st.subheader("Arka Baskı")
    if st.checkbox("Arka Baskı Var mı?"):
        arka_kalip = st.number_input("Arka Kalıp Sayısı", 0, 10, 0)
        arka_tur = st.selectbox("Arka Boya Türü", ["CMYK", "Special"])
        arka_maliyet = baski_hesapla(arka_tur, arka_kalip, tabaka_sayisi)
    else: arka_maliyet = 0

# Ekstra (Lak/Vernik)
with c_baski3:
    st.subheader("Ekstralar")
    ekstra_maliyet = 0
    
    # U.V Lak (E25, E29 Mantığı)
    if st.checkbox("U.V. Lak"):
        # Alan * 0.7 * 8 Euro + 3000 Sabit
        lak_miktar = (kagit_en * kagit_boy * 0.7 * tabaka_sayisi) / 1000000
        ekstra_maliyet += (lak_miktar * 8 * euro_kur) + 3000
        
    # Vernik (E26, E22 Mantığı)
    if st.checkbox("Vernik"):
        # Alan * 0.25 * 30 Dolar * 1.2 + 600 Sabit
        vernik_miktar = (kagit_en * kagit_boy * 0.25 * tabaka_sayisi) / 1000000
        ekstra_maliyet += 600 + (vernik_miktar * 30 * dolar_kur * 1.2)

baski_toplam = on_maliyet + arka_maliyet + ekstra_maliyet
st.info(f"Baskı Toplam (P4): **{baski_toplam:,.2f} ₺**")

st.markdown("---")

# ==========================================
# ✨ 3. BÖLÜM: SELEFON, YALDIZ, SIVAMA (DIŞ MALİYET)
# ==========================================
st.header("✨ 3. Dış İşlemler")
c_dis1, c_dis2, c_dis3 = st.columns(3)

# --- SELEFON (H8 Hücresi) ---
with c_dis1:
    st.subheader("Selefon")
    sel_tip = st.selectbox("Selefon Tipi", ["YOK", "SÜPER PARLAK", "SÜPER MAT", "SÜPER METALİZE", "TEKNİK MAT", "ÇİZİLMEZ"])
    
    sel_fiyat = 0
    if sel_tip != "YOK":
        # Kombinasyon Fiyatları (Dolar bazlı kabul edildi)
        fiyatlar = {
            "SÜPER PARLAK": 0.10, "SÜPER MAT": 0.11, "SÜPER METALİZE": 0.18,
            "TEKNİK MAT": 0.14, "ÇİZİLMEZ": 0.42
        }
        birim_m2 = fiyatlar.get(sel_tip, 0.10)
        # Formül: (En * Boy / 10000) * Adet * Birim * Dolar
        sel_fiyat = (kagit_en * kagit_boy / 10000) * tabaka_sayisi * birim_m2 * dolar_kur
    
    st.write(f"Tutar: {sel_fiyat:,.2f} ₺")

# --- YALDIZ (K13, K14, K15) ---
with c_dis2:
    st.subheader("Yaldız")
    yaldiz_fiyat = 0
    if st.checkbox("Yaldız Ekle"):
        y_en = st.number_input("Yaldız En (cm)", 10.0)
        y_boy = st.number_input("Yaldız Boy (cm)", 5.0)
        y_adet = st.number_input("Vuruş Adedi", value=tabaka_sayisi)
        
        # 1. Setup (Geçiş Bedeli)
        y_setup = 2000 if y_adet <= 1000 else 2000 + (y_adet - 1000) * 0.8
        # 2. Sarfiyat (Adet * Alan * 0.185 * S3)
        y_sarfiyat = (y_en/100) * (y_boy/100) * y_adet * 0.185 * dolar_kur
        # 3. Klişe (En * Boy * 5.5)
        y_klise = y_en * y_boy * 5.5
        
        yaldiz_fiyat = y_setup + y_sarfiyat + y_klise
        
    st.write(f"Tutar: {yaldiz_fiyat:,.2f} ₺")

# --- SIVAMA / ONDÜLE (H26) ---
with c_dis3:
    st.subheader("Sıvama / Ondüle")
    ond_tip = st.selectbox("Ondüle Tipi", ["YOK", "TEK YÜZ ONDÜLE", "LWC+ONDÜLE", "ÇİFT YÜZ ONDÜLE"])
    
    sivama_fiyat = 0
    if ond_tip != "YOK":
        # Çarpanlar
        carpan = 0
        if ond_tip == "TEK YÜZ ONDÜLE": carpan = 3.3
        elif ond_tip == "LWC+ONDÜLE": carpan = 3.8
        elif ond_tip == "ÇİFT YÜZ ONDÜLE": carpan = 5.0 # Tahmini
        
        # Formül: (En/100) * (Boy/100) * Adet * Çarpan
        sivama_fiyat = (kagit_en / 100) * (kagit_boy / 100) * tabaka_sayisi * carpan
        
    st.write(f"Tutar: {sivama_fiyat:,.2f} ₺")

st.markdown("---")

# ==========================================
# ✂️ 4. BÖLÜM: KESİM VE YAPIŞTIRMA (ÖZEL FORMÜLLER)
# ==========================================
st.header("✂️ 4. Kesim ve Yapıştırma")
c_son1, c_son2 = st.columns(2)

# --- KESİM (H16) ---
# Kural: 2000 adet altı sabit, üstü çarpanlı
with c_son1:
    kesim_tip = st.selectbox("Kesim Şekli", ["YOK", "BOBST", "GOFRELİ", "SIVAMALI", "AYIKLAMALI"])
    kesim_fiyat = 0
    
    if kesim_tip != "YOK":
        # Fiyat Sözlüğü: [Taban Fiyat, Ek Adet Başı Fiyat]
        k_param = {
            "BOBST":      [2500, 0.75],
            "GOFRELİ":    [3000, 0.80],
            "SIVAMALI":   [3000, 1.50],
            "AYIKLAMALI": [4500, 0.85]
        }
        taban, ek = k_param.get(kesim_tip, [0, 0])
        
        if tabaka_sayisi <= 2000:
            kesim_fiyat = taban
        else:
            kesim_fiyat = taban + (tabaka_sayisi - 2000) * ek
            
    st.success(f"Kesim Maliyeti: {kesim_fiyat:,.2f} ₺")

# --- YAPIŞTIRMA (H21) ---
# Kural: 5000 adet altı sabit, üstü çarpanlı
with c_son2:
    yap_tip = st.selectbox("Yapıştırma Türü", ["YOK", "YAN", "ALT-YAN", "4 NOKTA", "6 NOKTA"])
    yap_fiyat = 0
    
    if yap_tip != "YOK":
        # Fiyat Sözlüğü: [Taban Fiyat, Ek Adet Başı Fiyat]
        y_param = {
            "YAN":     [600,  0.03],
            "ALT-YAN": [700,  0.04],
            "4 NOKTA": [900,  0.07],
            "6 NOKTA": [1100, 0.09]
        }
        ytaban, yek = y_param.get(yap_tip, [0, 0])
        
        if tabaka_sayisi <= 5000:
            yap_fiyat = ytaban
        else:
            yap_fiyat = ytaban + (tabaka_sayisi - 5000) * yek
            
    st.success(f"Yapıştırma Maliyeti: {yap_fiyat:,.2f} ₺")

st.markdown("---")

# ==========================================
# 📊 FİNAL BÖLÜM: TOPLAMLAR VE TEKLİF (N21, N22...)
# ==========================================
st.header("📊 FİNAL TEKLİF EKRANI")

# 1. Maliyet Toplamları
# Dış Maliyet (N) = Kağıt + Selefon + Yaldız + Sıvama
dis_maliyet_toplam = kagit_maliyeti + sel_fiyat + yaldiz_fiyat + sivama_fiyat

# İç Maliyet (P) = Baskı + Kesim + Yapıştırma
ic_maliyet_toplam = baski_toplam + kesim_fiyat + yap_fiyat

# Genel Toplam (N21)
genel_toplam_maliyet = dis_maliyet_toplam + ic_maliyet_toplam

# 2. Satış Hesapları
# N22 = Maliyet + (Maliyet * Kâr / 100)
toplam_satis_tl = genel_toplam_maliyet * (1 + kar_orani / 100)
birim_satis_tl = toplam_satis_tl / tabaka_sayisi

# 3. Döviz Çevirimi (N23 Seçimine Göre)
final_toplam = 0
final_birim = 0
simge = "₺"

if teklif_para_birimi == "DOLAR":
    final_toplam = toplam_satis_tl / dolar_kur
    final_birim = birim_satis_tl / dolar_kur
    simge = "$"
elif teklif_para_birimi == "EURO":
    final_toplam = toplam_satis_tl / euro_kur
    final_birim = birim_satis_tl / euro_kur
    simge = "€"
else:
    final_toplam = toplam_satis_tl
    final_birim = birim_satis_tl
    simge = "₺"

# GÖSTERİM
col_f1, col_f2 = st.columns(2)

with col_f1:
    st.warning("📉 MALİYET KIRILIMI (TL)")
    st.write(f"Dış Maliyetler: {dis_maliyet_toplam:,.2f} ₺")
    st.write(f"İç Maliyetler: {ic_maliyet_toplam:,.2f} ₺")
    st.divider()
    st.write(f"**TOPLAM MALİYET (N21): {genel_toplam_maliyet:,.2f} ₺**")

with col_f2:
    st.success(f"📈 MÜŞTERİ TEKLİFİ ({teklif_para_birimi})")
    st.write(f"Kâr Marjı: %{kar_orani}")
    st.divider()
    st.metric("TOPLAM FİYAT", f"{final_toplam:,.2f} {simge}")
    st.metric("ADET BAŞI FİYAT", f"{final_birim:,.3f} {simge}")

import streamlit as st
import math

# ==========================================
# ⚙️ 0. AYARLAR VE SAYFA YAPISI
# ==========================================
st.set_page_config(page_title="Matbaa Maliyet Hesaplayıcı", layout="wide", page_icon="🖨️")

# --- KENAR ÇUBUĞU (KURLAR VE KÂR) ---
with st.sidebar:
    st.header("⚙️ Parametreler")
    st.write("Döviz Kurları (Güncelleyin)")
    
    dolar_kur = st.number_input("Dolar Kuru ($) - S3", value=34.50, step=0.01, format="%.2f")
    euro_kur = st.number_input("Euro Kuru (€) - S4", value=37.20, step=0.01, format="%.2f")
    
    st.divider()
    
    kar_orani = st.number_input("Kâr Oranı (%) - N19", value=20, step=1)
    teklif_para_birimi = st.radio("Teklif Para Birimi (N23)", ["TL", "DOLAR", "EURO"])
    
    st.info("Hesaplamalar anlık olarak bu kurlara göre yapılır.")

st.title("🖨️ Matbaa Maliyet & Teklif Sistemi")
st.markdown("---")

# ==========================================
# 🚀 YENİ BÖLÜM: SİPARİŞ VE VERİM (MONTAJ)
# ==========================================
st.header("🚀 Sipariş ve Verim Hesabı")
col_sip1, col_sip2, col_sip3, col_sip4 = st.columns(4)

with col_sip1:
    siparis_adedi = st.number_input("Sipariş Adedi", value=10000, step=1000)

with col_sip2:
    verim = st.number_input("Tabakadan Çıkan Adet (Verim)", value=4, min_value=1)

with col_sip3:
    fire_yuzdesi = st.number_input("Fire Oranı (%)", value=3, step=1)

# HESAPLAMA: (Sipariş / Verim) + Fire
net_tabaka = math.ceil(siparis_adedi / verim)
fire_tabaka = math.ceil(net_tabaka * (fire_yuzdesi / 100))
tabaka_sayisi = net_tabaka + fire_tabaka  # Bu değişken aşağıda kullanılacak (B11)

with col_sip4:
    st.warning(f"Baskı Tirajı (Net): {net_tabaka}")
    st.error(f"Fire Dahil Tabaka (B11): {tabaka_sayisi}")

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
    # Burada artık tabaka sayısını sormuyoruz, yukarıdan hesaplananı gösteriyoruz
    st.info(f"Kullanılacak Tabaka: {tabaka_sayisi}")

with c_kagit3:
    kagit_kur_tipi = st.selectbox("Kağıt Alış Kuru", ["TL", "DOLAR", "EURO"])
    ton_fiyati = st.number_input("Kağıt Ton Fiyatı", value=800.0)

# KAĞIT HESABI
toplam_kilo = (kagit_en * kagit_boy * gramaj * tabaka_sayisi) / 10000000
secilen_kagit_kuru = 1.0
if kagit_kur_tipi == "DOLAR": secilen_kagit_kuru = dolar_kur
elif kagit_kur_tipi == "EURO": secilen_kagit_kuru = euro_kur
kagit_maliyeti = (ton_fiyati / 1000) * toplam_kilo * secilen_kagit_kuru

with c_kagit4:
    st.metric("Toplam Kağıt (kg)", f"{toplam_kilo:.2f} kg")
    st.metric("Kağıt Maliyeti", f"{kagit_maliyeti:,.2f} ₺")

st.markdown("---")

# ==========================================
# 🎨 2. BÖLÜM: BASKI (İÇ MALİYETLER)
# ==========================================
st.header("🎨 2. Baskı Maliyetleri")

def baski_hesapla(tur, kalip_sayisi, adet):
    if kalip_sayisi == 0: return 0
    setup = 500 * kalip_sayisi if kalip_sayisi < 6 else 400 * kalip_sayisi
    tiraj = 0
    if adet > 1000:
        tiraj = (adet - 1000) * 0.8 
    boya_miktari = (kagit_en * kagit_boy * 0.2 * adet) / 1000000
    birim_boya_fiyat = 17 * euro_kur if tur == "CMYK" else 28 * euro_kur
    boya_tutari = boya_miktari * birim_boya_fiyat
    return setup + tiraj + boya_tutari

c_baski1, c_baski2, c_baski3 = st.columns(3)

with c_baski1:
    st.subheader("Ön Baskı")
    if st.checkbox("Ön Baskı Var mı?", value=True):
        on_kalip = st.number_input("Ön Kalıp Sayısı", 0, 10, 4)
        on_tur = st.selectbox("Ön Boya Türü", ["CMYK", "Special"])
        on_maliyet = baski_hesapla(on_tur, on_kalip, tabaka_sayisi)
    else: on_maliyet = 0

with c_baski2:
    st.subheader("Arka Baskı")
    if st.checkbox("Arka Baskı Var mı?"):
        arka_kalip = st.number_input("Arka Kalıp Sayısı", 0, 10, 0)
        arka_tur = st.selectbox("Arka Boya Türü", ["CMYK", "Special"])
        arka_maliyet = baski_hesapla(arka_tur, arka_kalip, tabaka_sayisi)
    else: arka_maliyet = 0

with c_baski3:
    st.subheader("Ekstralar")
    ekstra_maliyet = 0
    if st.checkbox("U.V. Lak"):
        lak_miktar = (kagit_en * kagit_boy * 0.7 * tabaka_sayisi) / 1000000
        ekstra_maliyet += (lak_miktar * 8 * euro_kur) + 3000
    if st.checkbox("Vernik"):
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

with c_dis1:
    st.subheader("Selefon")
    sel_tip = st.selectbox("Selefon Tipi", ["YOK", "SÜPER PARLAK", "SÜPER MAT", "SÜPER METALİZE", "TEKNİK MAT", "ÇİZİLMEZ"])
    sel_fiyat = 0
    if sel_tip != "YOK":
        fiyatlar = {"Süper Parlak": 0.10, "Süper Mat": 0.11, "Süper Metalize": 0.18, "Teknik Mat": 0.14, "Çizilmez": 0.42}
        sel_fiyat = (kagit_en * kagit_boy / 10000) * tabaka_sayisi * fiyatlar.get(sel_tip, 0.10) * dolar_kur
    st.write(f"Tutar: {sel_fiyat:,.2f} ₺")

with c_dis2:
    st.subheader("Yaldız")
    yaldiz_fiyat = 0
    if st.checkbox("Yaldız Ekle"):
        y_en = st.number_input("Yaldız En (cm)", 10.0)
        y_boy = st.number_input("Yaldız Boy (cm)", 5.0)
        # Yaldız adedi genellikle sipariş adedidir ama tabaka sayısı kadar da basılabilir. Burada tabaka aldık.
        y_adet = st.number_input("Vuruş Adedi", value=tabaka_sayisi)
        y_setup = 2000 if y_adet <= 1000 else 2000 + (y_adet - 1000) * 0.8
        y_sarfiyat = (y_en/100) * (y_boy/100) * y_adet * 0.185 * dolar_kur
        y_klise = y_en * y_boy * 5.5
        yaldiz_fiyat = y_setup + y_sarfiyat + y_klise
    st.write(f"Tutar: {yaldiz_fiyat:,.2f} ₺")

with

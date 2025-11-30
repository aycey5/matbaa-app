import streamlit as st
import math

# ==========================================
# ⚙️ 0. AYARLAR VE SAYFA YAPISI
# ==========================================
st.set_page_config(page_title="Matbaa Hesaplayıcı", layout="wide", page_icon="🖨️")

with st.sidebar:
    st.header("⚙️ Parametreler")
    dolar_kur = st.number_input("Dolar Kuru ($)", value=34.50, step=0.01, format="%.2f")
    euro_kur = st.number_input("Euro Kuru (€)", value=37.20, step=0.01, format="%.2f")
    st.divider()
    kar_orani = st.number_input("Kâr Oranı (%)", value=20, step=1)
    teklif_para_birimi = st.radio("Teklif Para Birimi", ["TL", "DOLAR", "EURO"])
    st.info("Hesaplamalar bu kurlara göre yapılır.")

st.title("🖨️ Matbaa Maliyet & Teklif Sistemi")
st.markdown("---")

# ==========================================
# 🚀 SİPARİŞ VE VERİM
# ==========================================
st.header("🚀 Sipariş ve Verim")
c1, c2, c3, c4 = st.columns(4)

with c1:
    siparis_adedi = st.number_input("Sipariş Adedi", value=10000, step=1000)
with c2:
    verim = st.number_input("Tabakadan Çıkan (Verim)", value=4, min_value=1)
with c3:
    fire_yuzdesi = st.number_input("Fire Oranı (%)", value=3, step=1)

net_tabaka = math.ceil(siparis_adedi / verim)
fire_tabaka = math.ceil(net_tabaka * (fire_yuzdesi / 100))
tabaka_sayisi = net_tabaka + fire_tabaka

with c4:
    st.warning(f"Baskı Tirajı: {net_tabaka}")
    st.error(f"Toplam Tabaka: {tabaka_sayisi}")

st.markdown("---")

# ==========================================
# 📦 KAĞIT
# ==========================================
st.header("📦 1. Kağıt Özellikleri")
k1, k2, k3, k4 = st.columns(4)

with k1:
    kagit_en = st.number_input("Kağıt En (cm)", value=70.0)
    kagit_boy = st.number_input("Kağıt Boy (cm)", value=100.0)
with k2:
    gramaj = st.number_input("Gramaj (gr)", value=350)
    st.info(f"Tabaka: {tabaka_sayisi}")
with k3:
    kagit_kur = st.selectbox("Kağıt Kuru", ["TL", "DOLAR", "EURO"])
    ton_fiyat = st.number_input("Ton Fiyatı", value=800.0)

toplam_kilo = (kagit_en * kagit_boy * gramaj * tabaka_sayisi) / 10000000
secilen_kur = 1.0
if kagit_kur == "DOLAR": secilen_kur = dolar_kur
elif kagit_kur == "EURO": secilen_kur = euro_kur
kagit_maliyeti = (ton_fiyat / 1000) * toplam_kilo * secilen_kur

with k4:
    st.metric("Toplam Kilo", f"{toplam_kilo:.2f} kg")
    st.metric("Kağıt Maliyeti", f"{kagit_maliyeti:,.2f} ₺")

st.markdown("---")

# ==========================================
# 🎨 BASKI
# ==========================================
st.header("🎨 2. Baskı Maliyetleri")

def baski_hesapla(tur, kalip, adet):
    if kalip == 0: return 0
    setup = 500 * kalip if kalip < 6 else 400 * kalip
    tiraj = 0
    if adet > 1000: tiraj = (adet - 1000) * 0.8
    boya_miktari = (kagit_en * kagit_boy * 0.2 * adet) / 1000000
    boya_fiyat = 17 * euro_kur if tur == "CMYK" else 28 * euro_kur
    return setup + tiraj + (boya_miktari * boya_fiyat)

b1, b2, b3 = st.columns(3)

with b1:
    st.subheader("Ön Baskı")
    if st.checkbox("Ön Baskı Var", value=True):
        on_kalip = st.number_input("Ön Kalıp", 0, 10, 4)
        on_tur = st.selectbox("Ön Tür", ["CMYK", "Special"])
        on_maliyet = baski_hesapla(on_tur, on_kalip, tabaka_sayisi)
    else: on_maliyet = 0

with b2:
    st.subheader("Arka Baskı")
    if st.checkbox("Arka Baskı Var"):
        arka_kalip = st.number_input("Arka Kalıp", 0, 10, 0)
        arka_tur = st.selectbox("Arka Tür", ["CMYK", "Special"])
        arka_maliyet = baski_hesapla(arka_tur, arka_kalip, tabaka_sayisi)
    else: arka_maliyet = 0

with b3:
    st.subheader("Ekstralar")
    ekstra_maliyet = 0
    if st.checkbox("U.V. Lak"):
        lak_miktar = (kagit_en * kagit_boy * 0.7 * tabaka_sayisi) / 1000000
        ekstra_maliyet += (lak_miktar * 8 * euro_kur) + 3000
    if st.checkbox("Vernik"):
        ver_miktar = (kagit_en * kagit_boy * 0.25 * tabaka_sayisi) / 1000000
        ekstra_maliyet += 600 + (ver_miktar * 30 * dolar_kur * 1.2)

baski_toplam = on_maliyet + arka_maliyet + ekstra_maliyet
st.info(f"Baskı Toplam: **{baski_toplam:,.2f} ₺**")

st.markdown("---")

# ==========================================
# ✨ DIŞ İŞLEMLER
# ==========================================
st.header("✨ 3. Dış İşlemler")
d1, d2, d3 = st.columns(3)

with d1:
    st.subheader("Selefon")
    sel_tip = st.selectbox("Selefon Türü", ["YOK", "SÜPER PARLAK", "SÜPER MAT", "SÜPER METALİZE", "TEKNİK MAT", "ÇİZİLMEZ"])
    sel_fiyat = 0
    if sel_tip != "YOK":
        fiyatlar = {"Süper Parlak": 0.10, "Süper Mat": 0.11, "Süper Metalize": 0.18, "Teknik Mat": 0.14, "Çizilmez": 0.42}
        sel_fiyat = (kagit_en * kagit_boy / 10000) * tabaka_sayisi * fiyatlar.get(sel_tip, 0.1) * dolar_kur
    st.write(f"Tutar: {sel_fiyat:,.2f} ₺")

with d2:
    st.subheader("Yaldız")
    yaldiz_fiyat = 0
    if st.checkbox("Yaldız Ekle"):
        y_en = st.number_input("Yaldız En", 10.0)
        y_boy = st.number_input("Yaldız Boy", 5.0)
        y_adet = st.number_input("Vuruş Adedi", value=tabaka_sayisi)
        y_setup = 2000 if y_adet <= 1000 else 2000 + (y_adet - 1000) * 0.8
        y_sarf = (y_en/100)*(y_boy/100)*y_adet*0.185*dolar_kur
        y_klise = y_en*y_boy*5.5
        yaldiz_fiyat = y_setup + y_sarf + y_klise
    st.write(f"Tutar: {yaldiz_fiyat:,.2f} ₺")

with d3:
    st.subheader("Sıvama")
    ond_tip = st.selectbox("Sıvama Türü", ["YOK", "TEK YÜZ ONDÜLE", "LWC+ONDÜLE", "ÇİFT YÜZ ONDÜLE"])
    sivama_fiyat = 0
    if ond_tip != "YOK":
        carpan = {"TEK YÜZ ONDÜLE": 3.3, "LWC+ONDÜLE": 3.8, "ÇİFT YÜZ ONDÜLE": 5.0}.get(ond_tip, 0)
        sivama_fiyat = (kagit_en/100)*(kagit_boy/100)*tabaka_sayisi*carpan
    st.write(f"Tutar: {sivama_fiyat:,.2f} ₺")

st.markdown("---")

# ==========================================
# ✂️ KESİM VE YAPIŞTIRMA
# ==========================================
st.header("✂️ 4. Kesim ve Yapıştırma")
s1, s2 = st.columns(2)

with s1:
    kesim_tip = st.selectbox("Kesim", ["YOK", "BOBST", "GOFRELİ", "SIVAMALI", "AYIKLAMALI"])
    kesim_fiyat = 0
    if kesim_tip != "YOK":
        taban = {"BOBST": 2500, "GOFRELİ": 3000, "SIVAMALI": 3000, "AYIKLAMALI": 4500}.get(kesim_tip, 0)
        ek = {"BOBST": 0.75, "GOFRELİ": 0.80, "SIVAMALI": 1.50, "AYIKLAMALI": 0.85}.get(kesim_tip, 0)
        kesim_fiyat = taban if tabaka_sayisi <= 2000 else taban + (tabaka_sayisi - 2000) * ek
    st.success(f"Kesim: {kesim_fiyat:,.2f} ₺")

with s2:
    yap_tip = st.selectbox("Yapıştırma", ["YOK", "YAN", "ALT-YAN", "4 NOKTA", "6 NOKTA"])
    yap_fiyat = 0
    if yap_tip != "YOK":
        ytaban = {"YAN": 600, "ALT-YAN": 700, "4 NOKTA": 900, "6 NOKTA": 1100}.get(yap_tip, 0)
        yek = {"YAN": 0.03, "ALT-YAN": 0.04, "4 NOKTA": 0.07, "6 NOKTA": 0.09}.get(yap_tip, 0)
        yap_fiyat = ytaban if tabaka_sayisi <= 5000 else ytaban + (tabaka_sayisi - 5000) * yek
    st.success(f"Yapıştırma: {yap_fiyat:,.2f} ₺")

st.markdown("---")

# ==========================================
# 📊 FİNAL
# ==========================================
st.header("📊 TEKLİF")
dis_toplam = kagit_maliyeti + sel_fiyat + yaldiz_fiyat + sivama_fiyat
ic_toplam = baski_toplam + kesim_fiyat + yap_fiyat
genel_toplam = dis_toplam + ic_toplam

satis_toplam = genel_toplam * (1 + kar_orani / 100)
birim_satis = satis_toplam / siparis_adedi

final_toplam = 0
final_birim = 0
simge = "₺"

if teklif_para_birimi == "DOLAR":
    final_toplam = satis_toplam / dolar_kur
    final_birim = birim_satis / dolar_kur
    simge = "$"
elif teklif_para_birimi == "EURO":
    final_toplam = satis_toplam / euro_kur
    final_birim = birim_satis / euro_kur
    simge = "€"
else:
    final_toplam = satis_toplam
    final_birim = birim_satis
    simge = "₺"

f1, f2 = st.columns(2)
with f1:
    st.write(f"Dış Maliyet: {dis_toplam:,.2f} ₺")
    st.write(f"İç Maliyet: {ic_toplam:,.2f} ₺")
    st.write(f"**TOPLAM MALİYET: {genel_toplam:,.2f} ₺**")
with f2:
    st.metric("TOPLAM FİYAT", f"{final_toplam:,.2f} {simge}")
    st.metric("ADET BAŞI", f"{final_birim:,.3f} {simge}")

import streamlit as st
import requests
import xml.etree.ElementTree as ET
import math

# ==========================================
# 🌐 OTOMATİK KUR (TCMB)
# ==========================================
def kur_getir():
    usd, eur, gbp = 34.50, 37.20, 43.50
    try:
        url = "https://www.tcmb.gov.tr/kurlar/today.xml"
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            for currency in root.findall('Currency'):
                kod = currency.get('Kod')
                try:
                    satis = currency.find('BanknoteSelling').text
                    if not satis: satis = currency.find('ForexSelling').text
                except: continue
                if kod == "USD": usd = float(satis)
                elif kod == "EUR": eur = float(satis)
                elif kod == "GBP": gbp = float(satis)
        return usd, eur, gbp
    except:
        return 34.50, 37.20, 43.50

st.set_page_config(page_title="Matbaa Hesaplayıcı", layout="wide", page_icon="🖨️")
oto_usd, oto_eur, oto_gbp = kur_getir()

# ==========================================
# ⚙️ YAN MENÜ
# ==========================================
with st.sidebar:
    st.header("💱 Döviz Kurları")
    dolar_kur = st.number_input("Dolar ($)", value=oto_usd, step=0.01)
    euro_kur = st.number_input("Euro (€)", value=oto_eur, step=0.01)
    sterlin_kur = st.number_input("Sterlin (£)", value=oto_gbp, step=0.01)

st.title("🖨️ Matbaa Maliyet & Lojistik (V14)")
st.markdown("---")

# ==========================================
# 📝 İŞ BİLGİLERİ
# ==========================================
c1, c2 = st.columns(2)
with c1: musteri_adi = st.text_input("Müşteri Adı", "")
with c2: isin_adi = st.text_input("İşin Adı", "")

st.markdown("---")

# ==========================================
# 🚀 ÜRETİM PLANLAMA
# ==========================================
st.header("🚀 Üretim Planlama")
p1, p2, p3, p4 = st.columns(4)
with p1: siparis_adedi = st.number_input("Sipariş Adedi", value=50000, step=1000)
with p2: verimlilik = st.number_input("Verimlilik (Tabakadan Çıkan)", value=2, min_value=1)
with p3: fire_yuzde = st.number_input("Fire Oranı (%)", value=3.0, step=0.5)

net_tabaka = math.ceil(siparis_adedi / verimlilik)
fire_miktari = math.ceil(net_tabaka * (fire_yuzde / 100))
baski_brut = net_tabaka + fire_miktari

with p4:
    st.error(f"BRÜT TABAKA: {baski_brut}")

st.markdown("---")

# ==========================================
# 📦 1. KAĞIT
# ==========================================
st.header("1. Kağıt Hesabı")
k1, k2, k3, k4 = st.columns(4)
with k1:
    kagit_en = st.number_input("Kağıt En", value=70.0)
    kagit_boy = st.number_input("Kağıt Boy", value=100.0)
    gramaj = st.number_input("Gramaj", value=350)
with k2:
    kagit_brut = st.number_input("Kağıt Brüt (Tedarik)", value=baski_brut)
with k3:
    kur_sec = st.selectbox("Kağıt Kuru", ["DOLAR", "EURO", "TL"])
    kag_fiyat = st.number_input("Kağıt Birim Fiyat", value=800.0)

toplam_kilo = (kagit_en * kagit_boy * gramaj * kagit_brut) / 10000000
kur_val = 1.0
if kur_sec == "DOLAR": kur_val = dolar_kur
elif kur_sec == "EURO": kur_val = euro_kur
kagit_tutar = (kag_fiyat / 1000) * toplam_kilo * kur_val

with k4:
    st.metric("Toplam Kilo", f"{toplam_kilo:.2f} kg")
    st.metric("Kağıt Tutarı", f"{kagit_tutar:,.2f} ₺")

st.markdown("---")

# ==========================================
# 🎨 2. BASKI
# ==========================================
st.header("2. Baskı Hesabı")
col_grafik, col_ebat1, col_ebat2 = st.columns([1, 1, 1])
with col_grafik: grafik_sayisi = st.number_input("Grafik Çeşit Sayısı", value=1, min_value=1)
with col_ebat1: b_en = st.number_input("Baskı Ebadı En", value=70.0)
with col_ebat2: b_boy = st.number_input("Baskı Ebadı Boy", value=100.0)

def setup_hesap(var, kalip, tip):
    if var == "HAYIR": return 0
    if tip == "KARTON": return 6000 if 6 <= kalip < 10 else 3000
    else: return 12000 if 6 <= kalip < 10 else 6000

def tiraj_hesap(adet, kalip, tip):
    if adet <= 1000: return 0
    fark = adet - 1000
    carpan = 2 if 6 <= kalip < 10 else 1
    birim = 0.8 if tip == "KARTON" else 1.3
    return fark * birim * carpan

col_k, col_m = st.columns(2)

# KARTON
with col_k:
    st.subheader("🟫 Karton Baskı")
    e_on = st.selectbox("Ön Baskı", ["HAYIR", "EVET"], index=1)
    e_arka = st.selectbox("Arka Baskı", ["HAYIR", "EVET"], index=0)
    e_boya = st.selectbox("Boya Türü", ["CMYK", "PANTONE"])
    e_kalip_on = st.number_input("Ön Kalıp Adet", value=4)
    e_kalip_arka = st.number_input("Arka Kalıp Adet", value=0)
    e_ver = st.selectbox("Vernik", ["HAYIR", "EVET"], key="ev")
    e_uv = st.selectbox("UV Lak", ["HAYIR", "EVET"], key="euv")
    e_disp = st.selectbox("Dispersiyon", ["HAYIR", "EVET"], key="ed")
    e_kau = st.selectbox("Kauçuk", ["HAYIR", "EVET"], key="ek")
    
    e_on_ad = baski_brut if e_on=="EVET" else 0
    e_ark_ad = baski_brut if e_arka=="EVET" else 0
    e_set = (setup_hesap(e_on, e_kalip_on, "KARTON") + setup_hesap(e_arka, e_kalip_arka, "KARTON")) * grafik_sayisi
    e_tir = (tiraj_hesap(e_on_ad, e_kalip_on, "KARTON") + tiraj_hesap(e_ark_ad, e_kalip_arka, "KARTON")) * grafik_sayisi
    e_boya_tut = ((b_en*b_boy*0.2*e_on_ad)/1000000) * (17*euro_kur if e_boya=="CMYK" else 28*euro_kur)
    e_ver_tut = (600 + ((b_en*b_boy*0.25*e_on_ad)/1000000 * 30 * dolar_kur * 1.2)) if e_ver=="EVET" else 0
    e_uv_tut = (3000 + ((b_en*b_boy*0.7*e_on_ad)/1000000 * 8 * euro_kur)) if e_uv=="EVET" else 0
    e_disp_tut = (1500 + (kagit_en*kagit_boy*baski_brut*4/10000000*3*euro_kur*3)) if e_disp=="EVET" else 0
    e_kau_tut = 3000 if e_kau=="EVET" else 0
    e_toplam = e_set + e_tir + e_boya_tut + e_ver_tut + e_uv_tut + e_disp_tut + e_kau_tut
    st.info(f"Toplam: {e_toplam:,.2f} ₺")

# METALİZE
with col_m:
    st.subheader("⬜ Metalize Baskı")
    f_on = st.selectbox("Ön Baskı", ["HAYIR", "EVET"], key="fo")
    f_arka = st.selectbox("Arka Baskı", ["HAYIR", "EVET"], key="fa")
    f_boya = st.selectbox("Boya Türü", ["CMYK", "PANTONE"], key="fb")
    f_kalip_on = st.number_input("Ön Kalıp Adet", value=0, key="fko")
    f_kalip_arka = st.number_input("Arka Kalıp Adet", value=0, key="fka")
    f_ver = st.selectbox("Vernik", ["HAYIR", "EVET"], key="fv")
    f_uv = st.selectbox("UV Lak", ["HAYIR", "EVET"], key="fuv")
    f_disp = st.selectbox("Dispersiyon", ["HAYIR", "EVET"], key="fd")
    f_kau = st.selectbox("Kauçuk", ["HAYIR", "EVET"], key="fk")
    
    f_on_ad = baski_brut if f_on=="EVET" else 0
    f_ark_ad = baski_brut if f_arka=="EVET" else 0
    f_set = (setup_hesap(f_on, f_kalip_on, "MET") + setup_hesap(f_arka, f_kalip_arka, "MET")) * grafik_sayisi
    f_tir = (tiraj_hesap(f_on_ad, f_kalip_on, "MET") + tiraj_hesap(f_ark_ad, f_kalip_arka, "MET")) * grafik_sayisi
    f_boya_tut = ((b_en*b_boy*0.2*f_on_ad)/1000000) * (17*euro_kur if f_boya=="CMYK" else 28*euro_kur)
    f_ver_tut = (600 + ((b_en*b_boy*0.25*f_on_ad)/1000000 * 30 * dolar_kur * 1.2)) if f_ver=="EVET" else 0
    f_uv_tut = (3000 + ((b_en*b_boy*0.7*f_on_ad)/1000000 * 8 * euro_kur)) if f_uv=="EVET" else 0
    f_disp_tut = (1500 + (kagit_en*kagit_boy*baski_brut*4/10000000*3*euro_kur*3)) if f_disp=="EVET" else 0
    f_kau_tut = 3000 if f_kau=="EVET" else 0
    f_toplam = f_set + f_tir + f_boya_tut + f_ver_tut + f_uv_tut + f_disp_tut + f_kau_tut
    st.info(f"Toplam: {f_toplam:,.2f} ₺")

st.markdown("---")

# ==========================================
# ✨ 3. DIŞ İŞLEMLER
# ==========================================
st.header("3. Dış İşlemler")
t1, t2, t3 = st.tabs(["Selefon & Soft", "Sıvama & Serigraf", "Kesim & Yapıştırma"])

with t1:
    cs1, cs2 = st.columns(2)
    with cs1:
        st.caption("Selefon")
        s_tur = st.selectbox("Selefon Türü", ["YOK", "PARLAK", "MAT", "METALİZE", "ÇİZİLMEZ"])
        sel_tutar = 0
        if s_tur != "YOK":
            s_ted = st.selectbox("Tedarikçi", ["SÜPER", "TEKNİK"])
            s_yon = st.selectbox("Yön", ["TEK YÜZ", "ÇİFT YÜZ"])
            sfiyats = {("SÜPER","PARLAK"):0.10, ("SÜPER","MAT"):0.11, ("SÜPER","METALİZE"):0.18, ("SÜPER","ÇİZİLMEZ"):0.42,
                       ("TEKNİK","PARLAK"):0.13, ("TEKNİK","MAT"):0.14, ("TEKNİK","METALİZE"):0.20, ("TEKNİK","ÇİZİLMEZ"):0.60}
            sm2 = sfiyats.get((s_ted, s_tur), 0.0)
            sel_tutar = (kagit_en/100)*(kagit_boy/100)*sm2*baski_brut*dolar_kur
            if s_yon=="ÇİFT YÜZ": sel_tutar *= 2
        st.write(f"Tutar: {sel_tutar:,.2f} ₺")
    with cs2:
        st.caption("Soft Touch Lak")
        soft = st.selectbox("Uygula", ["HAYIR", "EVET"])
        soft_tutar = 0
        if soft=="EVET":
            soft_tutar = 1500 + (b_en*b_boy*baski_brut*4/10000000*15*euro_kur*3)
        st.write(f"Tutar: {soft_tutar:,.2f} ₺")

with t2:
    co1, co2, co3 = st.columns(3)
    with co1:
        st.caption("Sıvama")
        siv_tur = st.selectbox("Sıvama", ["YOK", "TEK YÜZ ONDÜLE", "ÇİFT YÜZ ONDÜLE", "KARTON+KARTON"])
        siv_tutar = 0
        if siv_tur=="TEK YÜZ ONDÜLE": siv_tutar=(kagit_en/100)*(kagit_boy/100)*baski_brut*3.3
        elif siv_tur=="ÇİFT YÜZ ONDÜLE": siv_tutar=(kagit_en/100)*(kagit_boy/100)*baski_brut*6.6
        elif siv_tur=="KARTON+KARTON": siv_tutar=(kagit_en/100)*(kagit_boy/100)*baski_brut*4.4
        st.write(f"Tutar: {siv_tutar:,.2f} ₺")
    with co2:
        st.caption("Serigraf / Yaldız")
        seri = st.selectbox("Serigraf", ["YOK", "KISMİ LAK", "EMBOS LAK"])
        seri_tutar = 0
        if seri=="KISMİ LAK": seri_tutar = 1000 + baski_brut*0.6
        elif seri=="EMBOS LAK": seri_tutar = 1000 + baski_brut*1.5
        
        yaldiz_var = st.selectbox("Yaldız Var mı?", ["HAYIR", "EVET"])
        yal_tutar = 0
        if yaldiz_var == "EVET":
            y_adet = st.number_input("Yaldız Adet", value=baski_brut)
            y_gecis = 2000 if y_adet<=1000 else (y_adet-1000)*0.8+2000
            y_sarf_klise = st.number_input("Yaldız Sarf+Klişe (Manuel)", value=0.0)
            yal_tutar = y_gecis + y_sarf_klise
        st.write(f"Toplam: {(seri_tutar+yal_tutar):,.2f} ₺")
    with co3:
        st.caption("Gofre")
        gof_tutar = st.number_input("Gofre Toplam (Yoksa 0)", value=0.0)

with t3:
    ck1, ck2 = st.columns(2)
    with ck1:
        st.caption("Kesim")
        ks = st.selectbox("Kesim", ["YOK", "BOBST KESİM", "GOFRELİ KESİM", "SIVAMALI KESİM", "AYIKLAMALI KESİM"])
        kesim_tutar = 0
        if ks != "YOK":
            ktab = {"BOBST KESİM":2500, "GOFRELİ KESİM":3000, "SIVAMALI KESİM":3000, "AYIKLAMALI KESİM":4500}.get(ks,0)
            kek = {"BOBST KESİM":0.75, "GOFRELİ KESİM":0.80, "SIVAMALI KESİM":1.50, "AYIKLAMALI KESİM":0.85}.get(ks,0)
            kesim_tutar = ktab if baski_brut<=2000 else ktab + (baski_brut-2000)*kek
        st.success(f"{kesim_tutar:,.2f} ₺")
    with ck2:
        st.caption("Yapıştırma")
        ys = st.selectbox("Yapıştırma", ["YOK", "YAN YAPIŞTIRMA", "YAN DİP YAPIŞTIRMA", "KONİK DİP YAPIŞTIRMA", "ÜST SÜRME", "4 NOKTA", "6 NOKTA"])
        yap_tutar = 0
        if ys != "YOK":
            ytab = {"YAN YAPIŞTIRMA":1500, "YAN DİP YAPIŞTIRMA":3000, "KONİK DİP YAPIŞTIRMA":5500, "ÜST SÜRME":3000, "4 NOKTA":7500, "6 NOKTA":10000}.get(ys,0)
            yek = {"YAN YAPIŞTIRMA":0.15, "YAN DİP YAPIŞTIRMA":0.25, "KONİK DİP YAPIŞTIRMA":0.55, "ÜST SÜRME":0.35, "4 NOKTA":0.75, "6 NOKTA":0.90}.get(ys,0)
            yap_tutar = ytab if siparis_adedi<=5000 else ytab + (siparis_adedi-5000)*yek
        st.success(f"{yap_tutar:,.2f} ₺")

st.markdown("---")

# ==========================================
# 📦 KOLİ VE PALET SİHİRBAZI (YENİ MODÜL)
# ==========================================
st.header("📦 Koli & Palet Sihirbazı")
st.info("Karton kalınlığı ve ürün ölçülerine göre otomatik koli ebadı hesaplar.")

kp1, kp2 = st.columns(2)

with kp1:
    st.subheader("Ürün Özellikleri")
    urun_en = st.number_input("Ürün Eni (cm)", value=10.0, step=0.1)
    urun_boy = st.number_input("Ürün Boyu (cm)", value=15.0, step=0.1)
    urun_yukseklik = st.number_input("Ürün Derinlik/Körük (cm)", value=5.0, step=0.1)
    karton_mikron = st.number_input("Karton Kalınlığı (mm)", value=0.40, step=0.01, format="%.2f")
    yapistirma_tipi = st.radio("Yapıştırma Tipi", ["Yan Yapıştırma (3 Kat)", "Dip Yapıştırma (5 Kat)"], horizontal=True)

with kp2:
    st.subheader("Koli Özellikleri")
    dizim_yonu = st.radio("Koli İçi Dizim", ["Dik Dizim (Kutu)", "Yatık Dizim (Çanta)"])
    koli_ici_adet = st.number_input("Koli İçi Adet", value=100, step=10)
    koli_tolerans = st.number_input("Koli Payı (cm)", value=0.5)

# --- KOLİ HESAPLAMA MOTORU ---
# 1. Tek Ürün Kalınlık Hesabı
kat_sayisi = 3 if "Yan" in yapistirma_tipi else 5
tek_urun_kalinlik_cm = (karton_mikron * kat_sayisi) / 10 # mm to cm

# 2. İstif Kalınlığı (Toplam Şişme)
istif_kalinligi = tek_urun_kalinlik_cm * koli_ici_adet

# 3. Koli Ebatları
koli_en = 0
koli_boy = 0
koli_yukseklik = 0

if dizim_yonu == "Dik Dizim (Kutu)":
    # Kutu dik duruyor (Yan yana)
    koli_en = urun_en + koli_tolerans
    koli_boy = urun_boy + koli_tolerans
    koli_yukseklik = istif_kalinligi + koli_tolerans # Derinlik yükseklik olur
else:
    # Çanta yatık duruyor (Üst üste)
    koli_en = urun_en + koli_tolerans
    koli_boy = urun_yukseklik + koli_tolerans # Çanta körüğü boy olur
    koli_yukseklik = istif_kalinligi + koli_tolerans # Üst üste binen kalınlık

st.warning(f"📏 HESAPLANAN KOLİ EBADI: {koli_en:.1f} x {koli_boy:.1f} x {koli_yukseklik:.1f} cm")

# --- PALET HESABI (80x120) ---
st.subheader("Euro Palet (80x120) Yerleşimi")

# Algoritma: İki türlü de dener, en çok sığanı seçer
# Senaryo 1: En -> 80, Boy -> 120
s1_en = math.floor(80 / koli_en)
s1_boy = math.floor(120 / koli_boy)
toplam1 = s1_en * s1_boy

# Senaryo 2: Boy -> 80, En -> 120 (Döndürerek)
s2_en = math.floor(80 / koli_boy)
s2_boy = math.floor(120 / koli_en)
toplam2 = s2_en * s2_boy

if toplam1 >= toplam2:
    palet_taban_adet = toplam1
    dizilim_text = f"80'lik tarafa {s1_en}, 120'lik tarafa {s1_boy} adet."
else:
    palet_taban_adet = toplam2
    dizilim_text = f"80'lik tarafa {s2_en} (döndürülmüş), 120'lik tarafa {s2_boy} adet."

st.success(f"Bir Sıraya Sığan Koli: **{palet_taban_adet} Adet** ({dizilim_text})")

# Toplam Koli İhtiyacı
toplam_koli_ihtiyaci = math.ceil(siparis_adedi / koli_ici_adet)
palet_kat_sayisi = math.ceil(toplam_koli_ihtiyaci / palet_taban_adet)

kp_col1, kp_col2 = st.columns(2)
with kp_col1:
    st.write(f"Toplam Koli İhtiyacı: **{toplam_koli_ihtiyaci}**")
with kp_col2:
    st.write(f"Tahmini Palet Yüksekliği: **{palet_kat_sayisi * koli_yukseklik + 15:.1f} cm** (Palet dahil)")

# Otomatik Veri Aktarımı
auto_koli = st.checkbox("Koli ve Palet Sayısını Lojistik Kısmına Aktar")

st.markdown("---")

# ==========================================
# 🚛 4. MANUEL GİDERLER & LOJİSTİK
# ==========================================
st.header("🚛 4. Manuel Giderler & Lojistik")
ml1, ml2, ml3, ml4 = st.columns(4)

with ml1:
    m_bicak = st.number_input("Bıçak", value=0.0)
    m_asetat = st.number_input("Asetat", value=0.0)
    m_ondule = st.number_input("Ondüle", value=0.0)
with ml2:
    # Otomatik aktarım varsa buraya yaz, yoksa manuel
    val_koli = toplam_koli_ihtiyaci if auto_koli else 0
    val_palet = 1 if auto_koli else 0 # Basitçe 1 palet varsaydık, detaylandırılabilir
    
    koli_ad = st.number_input("Koli Adet", value=val_koli)
    palet_ad = st.number_input("Palet Adet", value=val_palet)
    m_koli_palet = (koli_ad * 50) + (palet_ad * 600)
    st.write(f"Koli+Palet: {m_koli_palet} ₺")
with ml3:
    m_gumruk = st.number_input("Gümrük", value=0.0)
    m_navlun = st.number_input("NAVLUN (Yoksa 0)", value=0.0)
    m_sigorta = m_navlun * 0.01
with ml4:
    lojistik_toplam = m_bicak + m_asetat + m_ondule + m_koli_palet + m_gumruk + m_navlun + m_sigorta
    st.error(f"Lojistik Toplam: {lojistik_toplam:,.2f} ₺")

st.markdown("---")

# ==========================================
# 📊 5. FİYATLANDIRMA
# ==========================================
st.header("📊 5. Fiyatlandırma & Kâr")

dis_maliyet = (kagit_tutar + sel_tutar + soft_tutar + siv_tutar + 
               seri_tutar + yal_tutar + gof_tutar + m_bicak + m_asetat + m_ondule + 
               m_koli_palet + m_gumruk + m_navlun)
ic_maliyet = (e_toplam + f_toplam + kesim_tutar + yap_tutar + m_sigorta)
ham_maliyet = dis_maliyet + ic_maliyet

c_son1, c_son2 = st.columns(2)
with c_son1:
    st.write(f"Dış Maliyet: {dis_maliyet:,.2f} ₺")
    st.write(f"İç Maliyet: {ic_maliyet:,.2f} ₺")
    st.error(f"**HAM MALİYET: {ham_maliyet:,.2f} ₺**")
    if m_navlun > 0: st.success(f"Navlun dahildir.")

with c_son2:
    kar_yuzde = st.number_input("Kâr Oranı (%)", value=0, step=5)
    satis_tl = ham_maliyet * (1 + kar_yuzde/100)
    para_birimi = st.radio("Para Birimi", ["TL", "DOLAR", "EURO", "STERLIN"], horizontal=True)
    
    final_fiyat = 0
    simge = "₺"
    if para_birimi == "DOLAR": final_fiyat = satis_tl / dolar_kur; simge = "$"
    elif para_birimi == "EURO": final_fiyat = satis_tl / euro_kur; simge = "€"
    elif para_birimi == "STERLIN": final_fiyat = satis_tl / sterlin_kur; simge = "£"
    else: final_fiyat = satis_tl; simge = "₺"
        
    st.divider()
    st.metric("TOPLAM SATIŞ", f"{final_fiyat:,.2f} {simge}")
    st.metric("ADET BAŞI", f"{(final_fiyat/siparis_adedi):,.3f} {simge}")

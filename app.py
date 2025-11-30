import streamlit as st
import requests
import xml.etree.ElementTree as ET

# ==========================================
# 🌐 OTOMATİK KUR ÇEKME FONKSİYONU (TCMB)
# ==========================================
def kur_getir():
    # Varsayılan değerler (Eğer internet yoksa bunlar gelir)
    usd, eur, gbp = 34.50, 37.20, 43.50
    
    try:
        url = "https://www.tcmb.gov.tr/kurlar/today.xml"
        response = requests.get(url)
        
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            
            # XML içinden kurları bul
            for currency in root.findall('Currency'):
                kod = currency.get('Kod')
                # Banknot Satış (Efektif Satış) en güvenlisidir, yoksa ForexSelling alırız
                try:
                    satis = currency.find('BanknoteSelling').text
                    if not satis: # Bazen boş olabilir
                        satis = currency.find('ForexSelling').text
                except:
                    continue

                if kod == "USD":
                    usd = float(satis)
                elif kod == "EUR":
                    eur = float(satis)
                elif kod == "GBP":
                    gbp = float(satis)
                    
        return usd, eur, gbp
        
    except Exception as e:
        # Hata olursa varsayılanları döndür
        return 34.50, 37.20, 43.50

# Sayfa Ayarları
st.set_page_config(page_title="Matbaa Maliyet Hesaplayıcı", layout="wide", page_icon="🖨️")

# Kurları Çek
oto_usd, oto_eur, oto_gbp = kur_getir()

# ==========================================
# ⚙️ AYARLAR (SIDEBAR)
# ==========================================
with st.sidebar:
    st.header("💱 Döviz Kurları")
    
    # Otomatik çekilen değerleri 'value' olarak atadık
    dolar_kur = st.number_input("Dolar ($)", value=oto_usd, step=0.01, format="%.4f")
    euro_kur = st.number_input("Euro (€)", value=oto_eur, step=0.01, format="%.4f")
    sterlin_kur = st.number_input("Sterlin (£)", value=oto_gbp, step=0.01, format="%.4f")
    
    st.success(f"✅ Kurlar TCMB'den çekildi.\nGüncelleme: Otomatik")
    st.info("Kurlar otomatik gelir ama isterseniz manuel değiştirebilirsiniz.")

st.title("🖨️ Matbaa Maliyet Hesabı (Canlı Kur)")
st.markdown("---")

# ==========================================
# 📝 İŞ BİLGİLERİ
# ==========================================
c1, c2 = st.columns(2)
with c1: musteri_adi = st.text_input("Müşteri Adı", "")
with c2: isin_adi = st.text_input("İşin Adı", "")

st.markdown("---")

# ==========================================
# 📦 1. KAĞIT
# ==========================================
st.header("1. Kağıt")
k1, k2, k3, k4 = st.columns(4)
with k1:
    kagit_en = st.number_input("Kağıt En", value=70.0)
    kagit_boy = st.number_input("Kağıt Boy", value=100.0)
    gramaj = st.number_input("Gramaj", value=350)
with k2:
    kagit_brut = st.number_input("Kağıt Brüt Tabaka", value=1000, step=100)
    baski_brut = st.number_input("Baskı Brüt Tabaka", value=1000, step=100)
    verim = st.number_input("Verimlilik", value=100)
with k3:
    siparis_adedi = st.number_input("Sipariş Adedi", value=5000)
    kur_sec = st.selectbox("Kağıt Kuru", ["DOLAR", "EURO", "TL"])
    kag_fiyat = st.number_input("Kağıt Birim Fiyat", value=800.0)

# Hesap
toplam_kilo = (kagit_en * kagit_boy * gramaj * kagit_brut) / 10000000
kur_val = 1.0
if kur_sec == "DOLAR": kur_val = dolar_kur
elif kur_sec == "EURO": kur_val = euro_kur
kagit_tutar = (kag_fiyat / 1000) * toplam_kilo * kur_val

with k4:
    st.metric("Kağıt Tutarı", f"{kagit_tutar:,.2f} ₺")

st.markdown("---")

# ==========================================
# 🎨 2. BASKI
# ==========================================
st.header("2. Baskı")
be1, be2 = st.columns(2)
with be1: b_en = st.number_input("Baskı En", value=70.0)
with be2: b_boy = st.number_input("Baskı Boy", value=100.0)

ck, cm = st.columns(2)

# Baskı Fonksiyonları
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

# Karton
with ck:
    st.subheader("Karton Baskı")
    e_on = st.selectbox("Ön Baskı", ["HAYIR", "EVET"], index=1)
    e_arka = st.selectbox("Arka Baskı", ["HAYIR", "EVET"], index=0)
    e_boya = st.selectbox("Boya", ["CMYK", "PANTONE"])
    e_kalip_on = st.number_input("Ön Kalıp", value=4)
    e_kalip_arka = st.number_input("Arka Kalıp", value=0)
    
    e_ver = st.selectbox("Vernik", ["HAYIR", "EVET"], key="ev")
    e_uv = st.selectbox("UV Lak", ["HAYIR", "EVET"], key="euv")
    e_disp = st.selectbox("Dispersiyon", ["HAYIR", "EVET"], key="ed")
    e_kau = st.selectbox("Kauçuk", ["HAYIR", "EVET"], key="ek")
    
    e_on_ad = baski_brut if e_on=="EVET" else 0
    e_ark_ad = baski_brut if e_arka=="EVET" else 0
    
    e_set = setup_hesap(e_on, e_kalip_on, "KARTON") + setup_hesap(e_arka, e_kalip_arka, "KARTON")
    e_tir = tiraj_hesap(e_on_ad, e_kalip_on, "KARTON") + tiraj_hesap(e_ark_ad, e_kalip_arka, "KARTON")
    
    e_boya_tut = ((b_en*b_boy*0.2*e_on_ad)/1000000) * (17*euro_kur if e_boya=="CMYK" else 28*euro_kur)
    
    e_ekstra = 0
    if e_ver=="EVET": e_ekstra += 600 + ((b_en*b_boy*0.25*e_on_ad)/1000000 * 30 * dolar_kur * 1.2)
    if e_uv=="EVET": e_ekstra += 3000 + ((b_en*b_boy*0.7*e_on_ad)/1000000 * 8 * euro_kur)
    if e_disp=="EVET": e_ekstra += 1500 + (kagit_en*kagit_boy*baski_brut*4/10000000*3*euro_kur*3)
    if e_kau=="EVET": e_ekstra += 3000
    
    e_toplam = e_set + e_tir + e_boya_tut + e_ekstra
    st.info(f"Tutar: {e_toplam:,.2f} ₺")

# Metalize
with cm:
    st.subheader("Metalize Baskı")
    f_on = st.selectbox("Ön Baskı", ["HAYIR", "EVET"], key="fo")
    f_arka = st.selectbox("Arka Baskı", ["HAYIR", "EVET"], key="fa")
    f_boya = st.selectbox("Boya", ["CMYK", "PANTONE"], key="fb")
    f_kalip_on = st.number_input("Ön Kalıp", value=0, key="fko")
    f_kalip_arka = st.number_input("Arka Kalıp", value=0, key="fka")
    
    f_ver = st.selectbox("Vernik", ["HAYIR", "EVET"], key="fv")
    f_uv = st.selectbox("UV Lak", ["HAYIR", "EVET"], key="fuv")
    f_disp = st.selectbox("Dispersiyon", ["HAYIR", "EVET"], key="fd")
    f_kau = st.selectbox("Kauçuk", ["HAYIR", "EVET"], key="fk")
    
    f_on_ad = baski_brut if f_on=="EVET" else 0
    f_ark_ad = baski_brut if f_arka=="EVET" else 0
    
    f_set = setup_hesap(f_on, f_kalip_on, "MET") + setup_hesap(f_arka, f_kalip_arka, "MET")
    f_tir = tiraj_hesap(f_on_ad, f_kalip_on, "MET") + tiraj_hesap(f_ark_ad, f_kalip_arka, "MET")
    
    f_boya_tut = ((b_en*b_boy*0.2*f_on_ad)/1000000) * (17*euro_kur if f_boya=="CMYK" else 28*euro_kur)
    
    f_ekstra = 0
    if f_ver=="EVET": f_ekstra += 600 + ((b_en*b_boy*0.25*f_on_ad)/1000000 * 30 * dolar_kur * 1.2)
    if f_uv=="EVET": f_ekstra += 3000 + ((b_en*b_boy*0.7*f_on_ad)/1000000 * 8 * euro_kur)
    if f_disp=="EVET": f_ekstra += 1500 + (kagit_en*kagit_boy*baski_brut*4/10000000*3*euro_kur*3)
    if f_kau=="EVET": f_ekstra += 3000
    
    f_toplam = f_set + f_tir + f_boya_tut + f_ekstra
    st.info(f"Tutar: {f_toplam:,.2f} ₺")

st.markdown("---")

# ==========================================
# ✨ 3. İŞLEMLER
# ==========================================
st.header("3. Dış İşlemler")
t1, t2, t3 = st.tabs(["Selefon & Soft", "Sıvama & Serigraf", "Kesim & Yapıştırma"])

with t1:
    cs1, cs2 = st.columns(2)
    with cs1:
        st.caption("Selefon")
        s_ted = st.selectbox("Tedarikçi", ["SÜPER", "TEKNİK"])
        s_tur = st.selectbox("Tür", ["PARLAK", "MAT", "METALİZE", "ÇİZİLMEZ"])
        s_yon = st.selectbox("Yön", ["TEK YÜZ", "ÇİFT YÜZ"])
        
        sfiyats = {("SÜPER","PARLAK"):0.10, ("SÜPER","MAT"):0.11, ("SÜPER","METALİZE"):0.18, ("SÜPER","ÇİZİLMEZ"):0.42,
                   ("TEKNİK","PARLAK"):0.13, ("TEKNİK","MAT"):0.14, ("TEKNİK","METALİZE"):0.20, ("TEKNİK","ÇİZİLMEZ"):0.60}
        sm2 = sfiyats.get((s_ted, s_tur), 0.0)
        sel_tutar = (kagit_en/100)*(kagit_boy/100)*sm2*baski_brut*dolar_kur
        if s_yon=="ÇİFT YÜZ": sel_tutar *= 2
        st.write(f"Selefon: {sel_tutar:,.2f} ₺")
        
    with cs2:
        st.caption("Soft Touch Lak")
        soft = st.selectbox("Uygula", ["HAYIR", "EVET"])
        soft_tutar = 0
        if soft=="EVET":
            soft_tutar = 1500 + (b_en*b_boy*baski_brut*4/10000000*15*euro_kur*3)
        st.write(f"Soft Touch: {soft_tutar:,.2f} ₺")

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
        
        yal_tutar = 0
        if st.checkbox("Yaldız"):
            y_adet = st.number_input("Yaldız Baskı Adet", value=baski_brut)
            y_gecis = 2000 if y_adet<=1000 else (y_adet-1000)*0.8+2000
            y_sarf_klise = st.number_input("Yaldız Sarfiyat + Klişe Toplamı", value=0.0)
            yal_tutar = y_gecis + y_sarf_klise
        st.write(f"Toplam: {(seri_tutar+yal_tutar):,.2f} ₺")

    with co3:
        st.caption("Gofre")
        gof_tutar = st.number_input("Gofre Toplam Fiyat (Manuel)", value=0.0)

with t3:
    ck1, ck2 = st.columns(2)
    with ck1:
        st.caption("Kesim")
        ks = st.selectbox("Kesim", ["BOBST KESİM", "GOFRELİ KESİM", "SIVAMALI KESİM", "AYIKLAMALI KESİM"])
        ktab = {"BOBST KESİM":2500, "GOFRELİ KESİM":3000, "SIVAMALI KESİM":3000, "AYIKLAMALI KESİM":4500}.get(ks,0)
        kek = {"BOBST KESİM":0.75, "GOFRELİ KESİM":0.80, "SIVAMALI KESİM":1.50, "AYIKLAMALI KESİM":0.85}.get(ks,0)
        kesim_tutar = ktab if baski_brut<=2000 else ktab + (baski_brut-2000)*kek
        st.success(f"{kesim_tutar:,.2f} ₺")
        
    with ck2:
        st.caption("Yapıştırma")
        ys = st.selectbox("Yapıştırma", ["YAN YAPIŞTIRMA", "YAN DİP YAPIŞTIRMA", "KONİK DİP YAPIŞTIRMA", "ÜST SÜRME", "4 NOKTA", "6 NOKTA"])
        ytab = {"YAN YAPIŞTIRMA":1500, "YAN DİP YAPIŞTIRMA":3000, "KONİK DİP YAPIŞTIRMA":5500, "ÜST SÜRME":3000, "4 NOKTA":7500, "6 NOKTA":10000}.get(ys,0)
        yek = {"YAN YAPIŞTIRMA":0.15, "YAN DİP YAPIŞTIRMA":0.25, "KONİK DİP YAPIŞTIRMA":0.55, "ÜST SÜRME":0.35, "4 NOKTA":0.75, "6 NOKTA":0.90}.get(ys,0)
        yap_tutar = ytab if siparis_adedi<=5000 else ytab + (siparis_adedi-5000)*yek
        st.success(f"{yap_tutar:,.2f} ₺")

st.markdown("---")

# ==========================================
# 🚛 4. MANUEL GİDERLER & LOJİSTİK
# ==========================================
st.header("🚛 4. Manuel Giderler & Lojistik")
st.warning("⚠️ Lojistik kalemlerini manuel giriniz.")

ml1, ml2, ml3, ml4 = st.columns(4)

with ml1:
    m_bicak = st.number_input("Bıçak Maliyeti (N12)", value=0.0, step=100.0)
    m_asetat = st.number_input("Asetat / Pencere", value=0.0, step=100.0)
    m_ondule = st.number_input("Ondüle Ekstra", value=0.0, step=100.0)

with ml2:
    koli_ad = st.number_input("Koli Adedi", value=0, step=1)
    palet_ad = st.number_input("Palet Adedi", value=0, step=1)
    m_koli_palet = (koli_ad * 50) + (palet_ad * 600)
    st.write(f"Koli+Palet: **{m_koli_palet:,.2f} ₺**")

with ml3:
    m_gumruk = st.number_input("Gümrük (N15)", value=0.0, step=100.0)
    m_navlun = st.number_input("NAVLUN BEDELİ (N16)", value=0.0, step=100.0)
    m_sigorta = m_navlun * 0.01
    st.write(f"Sigorta (%1): **{m_sigorta:,.2f} ₺**")

with ml4:
    lojistik_toplam = m_bicak + m_asetat + m_ondule + m_koli_palet + m_gumruk + m_navlun + m_sigorta
    st.error(f"Lojistik Toplam:\n\n{lojistik_toplam:,.2f} ₺")

st.markdown("---")

# ==========================================
# 💰 5. FİNAL HESAP
# ==========================================
st.header("📊 5. Fiyatlandırma & Kâr")

dis_maliyet = (kagit_tutar + sel_tutar + soft_tutar + siv_tutar + 
               seri_tutar + yal_tutar + gof_tutar + m_bicak + m_asetat + m_ondule + 
               m_koli_palet + m_gumruk + m_navlun)

ic_maliyet = (e_toplam + f_toplam + kesim_tutar + yap_tutar + m_sigorta)

ham_maliyet = dis_maliyet + ic_maliyet

c_son1, c_son2 = st.columns(2)

with c_son1:
    st.write(f"Dış Maliyetler: {dis_maliyet:,.2f} ₺")
    st.write(f"İç Maliyetler: {ic_maliyet:,.2f} ₺")
    st.error(f"**TOPLAM HAM MALİYET: {ham_maliyet:,.2f} ₺**")
    if m_navlun > 0: st.success(f"Navlun ({m_navlun} ₺) dahildir.")
    else: st.warning("Navlun 0 ₺ girildi.")

with c_son2:
    st.subheader("Satış Fiyatını Belirle")
    kar_yuzde = st.number_input("Kâr Oranı (%) Giriniz", value=0, step=5)
    
    satis_tl = ham_maliyet * (1 + kar_yuzde/100)
    
    para_birimi = st.radio("Teklif Para Birimi", ["TL", "DOLAR", "EURO", "STERLIN"], horizontal=True)
    
    final_fiyat = 0
    simge = "₺"
    
    if para_birimi == "DOLAR":
        final_fiyat = satis_tl / dolar_kur
        simge = "$"
    elif para_birimi == "EURO":
        final_fiyat = satis_tl / euro_kur
        simge = "€"
    elif para_birimi == "STERLIN":
        final_fiyat = satis_tl / sterlin_kur
        simge = "£"
    else:
        final_fiyat = satis_tl
        simge = "₺"
        
    st.divider()
    st.metric("TOPLAM SATIŞ FİYATI", f"{final_fiyat:,.2f} {simge}")
    st.metric("ADET BAŞI FİYAT", f"{(final_fiyat/siparis_adedi):,.3f} {simge}")

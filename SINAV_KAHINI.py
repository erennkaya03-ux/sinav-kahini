import streamlit as st
import google.generativeai as genai
from datetime import datetime
from pypdf import PdfReader
import io
from streamlit_autorefresh import st_autorefresh

# Sayfa Ayarları ve Mobil Görünüm Optimizasyonu
st.set_page_config(page_title="Sınav Kahini", page_icon="🔮", layout="centered")

# --- MOBİL ARAYÜZ STİL AYARLARI (CSS) ---
st.markdown("""
<style>
    .stButton>button {
        width: 100% !important;
        border-radius: 12px !important;
        height: 45px !important;
        font-weight: bold !important;
    }
    .stTextArea textarea {
        border-radius: 10px !important;
    }
    button[data-baseweb="tab"] {
        font-size: 14px !important;
        padding: 10px 5px !important;
    }
    .ders-baslik {
        font-weight: bold;
        color: #1E88E5;
        margin-top: 10px;
        margin-bottom: 5px;
        border-bottom: 1px solid #ddd;
        padding-bottom: 2px;
    }
</style>
""", unsafe_allow_html=True)

# --- SANAL HAFIZA KURULUMU ---
if "ders_notlari" not in st.session_state:
    st.session_state["ders_notlari"] = {}

if "api_key_kayitli" not in st.session_state:
    st.session_state["api_key_kayitli"] = ""

# --- MÜFREDAT VERİTABANI (SINIFLARA GÖRE AYRILMIŞ HAVUZ) ---
MÜFREDAT_HAVUZU = {
    "1. SINIF DERSLERİ": [
        "İktisada Giriş I", "Genel Hukuk", "Bilgisayar Kullanımı ve Ofis Uygulamaları", 
        "Genel İşletme", "Finansal Muhasebe I", "İktisada Giriş II", 
        "Yönetim ve Organizasyon", "Ticari Belgeler", "Ticari ve Mali Matematik", 
        "Finansal Muhasebe II", "Ticaret Hukuku"
    ],
    "2. SINIF DERSLERİ": [
        "Finansal Okuryazarlık", "Finans Matematiği", "Muhasebe Paket Programları I", 
        "Şirketler Muhasebesi", "Stratejik Yönetim", "Halkla İlişkiler", 
        "İş ve Sosyal Güvenlik Hukuku", "Muhasebe Meslek Mevzuatı ve Etiği", "E-Ticaret", 
        "Muhasebe Paket Programları II", "Para ve Sermaye Piyasası Kurumları", 
        "Finansal Tablolar Analizi", "İhtisas Muhasebesi", "Kıymetli Evrak Hukuku", 
        "Girişimcilik", "İletişim ve Etkili Sunum Teknikleri", "Davranışsal İktisat", 
        "Dış Ticaret İşlemleri", "Pazarlama Yönetimi"
    ],
    "3. SINIF DERSLERİ": [
        "Vergi Hukuku", "Yatırım Analizi ve Portföy Yönetimi", "Finansal Yönetim I", 
        "Maliyet Muhasebesi I", "Sermaye Piyasası Mevzuatı", "Türkiye Ekonomisi", 
        "Borsa İşlemleri", "Muhasebede Seçilmiş Konular ve Örnek Olaylar", "İstatistik", 
        "Enflasyon Muhasebesi", "Finansal Sistem ve Uygulamaları I", "Finansal Yönetim II", 
        "Maliyet Muhasebesi II", "Türk Vergi Sistemi ve Uygulamaları", "Muhasebe Denetimi", 
        "Yatırım Kuruluşları ve Araçları", "Yönlendirilmiş Çalışmalar", "Davranış Bilimleri", 
        "Dış Ticaret İşlemleri Muhasebesi", "Sosyoloji"
    ],
    "4. SINIF DERSLERİ": [
        "Muhasebe Standartları", "Finansal Sistem ve Uygulamaları II", "Maliyet Yönetimi", 
        "Davranışsal Finans", "Yönetim Muhasebesi", "Bilimsel Araştırma Yöntemleri", 
        "Türev Piyasalar ve Risk Yönetimi", "Muhasebe Bilgi Sistemleri", "Kobi Finansmanı", 
        "İş Sağlığı ve Güvenliği", "İnsan Kaynakları Yönetimi", "İşletmede Mesleki Eğitim"
    ]
}

# Başlangıç varsayılan dersleri
if "secilen_dersler" not in st.session_state:
    st.session_state["secilen_dersler"] = ["Finansal Muhasebe I", "Finansal Muhasebe II", "Ticaret Hukuku"]

# --- TEK DÜZEN HESAP PLANI VERİTABANI ---
HESAP_PLANI = {"100": "KASA", "101": "ALINAN ÇEKLER", "102": "BANKALAR", "103": "VERİLEN ÇEKLER (-)", "120": "ALICILAR", "121": "ALACAK SENETLERİ", "153": "TİCARİ MALLAR", "191": "İNDİRİLECEK KDV", "254": "TAŞITLAR", "255": "DEMİRBAŞLAR", "257": "BİRİKMİŞ AMORTİSMANLAR (-)", "320": "SATICILAR", "321": "BORÇ SENETLERİ", "391": "HESAPLANAN KDV", "500": "SERMAYE", "600": "YURTİÇİ SATIŞLAR", "621": "STMM (-)", "770": "GENEL YÖNETİM GİDERLERİ"}

# --- GİRİŞ KONTROLÜ ---
if not st.session_state["api_key_kayitli"]:
    st.title("🔮 Sınav Kahini Giriş")
    st.subheader("Hoş geldiniz")
    girilen_key = st.text_input("🔑 Gemini API Key Girin:", type="password", help="Google AI Studio'dan aldığınız ücretsiz anahtarı buraya yapıştırın.")
    
    if st.button("Sisteme Giriş Yap 🚀", use_container_width=True):
        if girilen_key:
            st.session_state["api_key_kayitli"] = girilen_key
            st.success("Giriş başarılı! Uygulama açılıyor...")
            st.rerun()
        else:
            st.error("Lütfen geçerli bir anahtar girin.")
else:
    genai.configure(api_key=st.session_state["api_key_kayitli"])
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    st.title("🔮 Sınav Kahini")
    
    if st.button("🔒 Oturumu Kapat / Key Değiştir", use_container_width=True):
        st.session_state["api_key_kayitli"] = ""
        st.rerun()

    st.markdown("---")

    # --- MOBİL ÜST SEKME SİSTEMİ ---
    sekme1, sekme2, sekme3, sekme4, sekme5 = st.tabs(["📁 Arşiv", "📢 Not/PDF Yükle", "📝 Soru Odası", "📊 Hesapla", "💬 Sohbet"])

    # SEKME 1: DERS ARŞİVİ
    with sekme1:
        st.subheader("📌 Ders Kütüphanesi")
        if st.session_state["ders_notlari"]:
            aktif_arsiv_var_mi = False
            for ders, haftalar in st.session_state["ders_notlari"].items():
                if ders in st.session_state["secilen_dersler"]:
                    aktif_arsiv_var_mi = True
                    with st.expander(f"📁 {ders}", expanded=True):
                        for hafta, veri_listesi in sorted(haftalar.items()):
                            st.markdown(f"**🗓️ {hafta}. Hafta**")
                            for idx, eleman in enumerate(veri_listesi):
                                if eleman["tip"] == "metin":
                                    st.info(eleman['icerik'])
                                elif eleman["tip"] == "fotograf":
                                    st.image(eleman["icerik"], use_container_width=True)
                            if st.button(f"🗑️ {hafta}. Haftayı Temizle", key=f"del_{ders}_{hafta}", use_container_width=True):
                                del st.session_state["ders_notlari"][ders][hafta]
                                st.rerun()
            if not aktif_arsiv_var_mi:
                st.caption("Seçili aktif derslerinize ait yüklenmiş not bulunmamaktadır.")
        else:
            st.caption("Henüz yüklenmiş bir ders notu bulunmamaktadır.")

    # SEKME 2: NOT VE PDF YÜKLEME
    with sekme2:
        st.subheader("📢 Ders Notu & PDF & Fotoğraf Yükle")
        
        # Ders Yönetim Paneli
        with st.popover("➕ Dönem Derslerini Düzenle (Ekle/Çıkar)"):
            st.markdown("### 📚 Müfredat Listesi")
            st.caption("Bu dönem aldığınız dersleri işaretleyin:")
            gecici_secimler = []
            for sinif_adi, ders_listesi in MÜFREDAT_HAVUZU.items():
                st.markdown(f"<div class='ders-baslik'>{sinif_adi}</div>", unsafe_allow_html=True)
                for ders in ders_listesi:
                    durum = ders in st.session_state["secilen_dersler"]
                    if st.checkbox(ders, value=durum, key=f"pop_{ders}"):
                        gecici_secimler.append(ders)
            
            st.markdown("---")
            if st.button("Listeyi Güncelle", type="primary", use_container_width=True):
                if gecici_secimler:
                    st.session_state["secilen_dersler"] = gecici_secimler
                    st.rerun()
                else:
                    st.error("En az bir ders seçilmelidir.")
                    
        st.markdown("---")
        
        ders_adi = st.selectbox("İşlem Yapılacak Ders:", options=st.session_state["secilen_dersler"], key="mob_ders")
        secilen_hafta = st.number_input("Hafta:", min_value=1, max_value=14, value=1, key="mob_hafta")
        
        st.markdown("### 1. Yazılı Not veya Tahta Fotoğrafı")
        ham_not = st.text_area("📝 Not ekleyin veya yapıştırın:", placeholder="Önemli notlar...", height=80)
        yuklenen_foto = st.file_uploader("📸 Tahta Fotoğrafı Yükle:", type=["png", "jpg", "jpeg"])
        
        st.markdown("---")
        st.markdown("### 2. PDF Kitap/Slayt Özetleme")
        yuklenen_pdf = st.file_uploader("📄 Slayt veya Kitap PDF'i Yükle:", type=["pdf"])
        
        if st.button("🚀 Verileri Havuza ve Yapay Zekaya Gönder", use_container_width=True):
            if ders_adi not in st.session_state["ders_notlari"]:
                st.session_state["ders_notlari"][ders_adi] = {}
            if secilen_hafta not in st.session_state["ders_notlari"][ders_adi]:
                st.session_state["ders_notlari"][ders_adi][secilen_hafta] = []
            
            if ham_not:
                st.session_state["ders_notlari"][ders_adi][secilen_hafta].append({"tip": "metin", "icerik": ham_not})
            if yuklenen_foto:
                st.session_state["ders_notlari"][ders_adi][secilen_hafta].append({"tip": "fotograf", "icerik": yuklenen_foto.read()})
            if yuklenen_pdf:
                with st.spinner("📄 PDF okunuyor..."):
                    try:
                        reader = PdfReader(io.BytesIO(yuklenen_pdf.read()))
                        pdf_metni = ""
                        for sayfa in reader.pages[:10]:
                            pdf_metni += sayfa.extract_text() + "\n"
                        komut = f"Aşağıdaki ders notu PDF metnini özetle:\n\n{pdf_metni}"
                        yanit = model.generate_content(komut)
                        st.session_state["ders_notlari"][ders_adi][secilen_hafta].append({"tip": "metin", "icerik": f"📄 **PDF ÖZETİ:**\n\n{yanit.text}"})
                    except Exception as e:
                        st.error(f"Hata: {e}")
            st.success("Başarıyla arşive işlendi! 📁")
            st.rerun()

    # SEKME 3: YAPAY ZEKA SORU ODASI
    with sekme3:
        st.subheader("📝 Yapay Zeka Soru Odası")
        ders_kontrol = st.selectbox("Ders Seçin:", options=st.session_state["secilen_dersler"], key="kahin_mob_ders")
        zorluk = st.select_slider("Zorluk Seviyesi:", options=["Kolay", "Orta", "Zor", "Hocanın Saplama Modu"], key="mob_zorluk")
        
        st.markdown("---")
        ornek_soru = st.text_area("✍️ Örnek Soru Yazınız (Opsiyonel):", placeholder="Kendi sorunuzu yazın veya boş bırakın...", height=100)
        
        if st.button("🔮 Soru Hazırla / Çözdür", use_container_width=True):
            if ornek_soru:
                komut = f"Sen üniversitede {ders_kontrol} dersi veren bir hocasın. Soruyu detaylıca çöz:\n\n{ornek_soru}"
            else:
                komut = f"Sen üniversitede {ders_kontrol} dersi veren bir hocasın. {zorluk} seviyesinde orijinal bir soru ve çözümü üret."
            
            with st.spinner("🔮 Sorunuz hazırlanıyor..."):
                try:
                    response = model.generate_content(komut)
                    st.session_state["mob_soru"] = response.text
                except Exception as e:
                    st.error(f"Hata: {e}")
                    
        if "mob_soru" in st.session_state:
            st.markdown(st.session_state["mob_soru"])

    # SEKME 4: HARF NOTU VE FİNAL SİMÜLATÖRÜ
    with sekme4:
        st.subheader("📊 Harf Notu & Geçme Simülatörü")
        
        st.error("🚨 **!!DİKKAT:** Bu hesaplama matematiksel bir tahmindir. Kesin harf notu sonucu için lütfen OBS sistemine giriniz.")
        st.warning("⚠️ **NOT:** Vize ve final ortalaması 40 ve altındaysa veya final notu 45'in altındaysa sistem otomatik olarak FF verir.")
        st.markdown("---")
        
        vize_notu = st.slider("Vize Notu?", min_value=0, max_value=100, value=40, key="mob_vize")
        sinif_ort = st.slider("Sınıf Ortalaması?", min_value=20, max_value=80, value=45, key="mob_ort")
        muhtemel_final = st.slider("🔮 Muhtemelen Final Notu Kaç Olur?", min_value=0, max_value=100, value=50, key="mob_muhtemel_final")
        
        st.markdown("---")
        
        vize_katki = vize_notu * 0.4
        final_katki = muhtemel_final * 0.6
        donem_notu = vize_katki + final_katki
        fark = donem_notu - sinif_ort
        
        if muhtemel_final < 45:
            harf_notu = "FF (Final Barajı Altı)"
            durum = "Kaldınız ❌"
            renk = st.error
        elif donem_notu <= 40:
            harf_notu = "FF"
            durum = "Kaldınız ❌"
            renk = st.error
        elif fark >= 20:
            harf_notu = "AA"
            durum = "Başarıyla geçtiniz! 🚀"
            renk = st.success
        elif fark >= 12:
            harf_notu = "BA"
            durum = "Rahatlıkla geçtiniz! 😎"
            renk = st.success
        elif fark >= 5:
            harf_notu = "BB"
            durum = "İyi bir notla geçtiniz! 🙌"
            renk = st.success
        elif fark >= -2:
            harf_notu = "CB"
            durum = "Geçtiniz! 👍"
            renk = st.success
        elif fark >= -8:
            harf_notu = "CC"
            durum = "Sınırda geçtiniz! 🎯"
            renk = st.success
        elif fark >= -15:
            harf_notu = "DC"
            durum = "Koşullu Geçtiniz (Ortalama 2.00 üzeriyse)."
            renk = st.warning
        elif fark >= -20:
            harf_notu = "DD"
            durum = "Koşullu Geçtiniz (Ortalama 2.00 üzeriyse)."
            renk = st.warning
        else:
            harf_notu = "FF"
            durum = "Kaldınız ❌"
            renk = st.error

        st.metric(label="📊 Hesaplanan Dönem Sonu Notu:", value=f"{round(donem_notu, 1)}")
        renk(f"Tahmini Harf Notu: **{harf_notu}** — {durum}")
        # --- YENİ EKLENEN CHAT BÖLÜMÜ ---
with sekme5:
    st.subheader("💬 Canlı Bölüm Sohbeti")
    
    # 1. İsmi kaydet
    if "kullanici_ismi" not in st.session_state:
        isim = st.text_input("Sohbete girmek için isminiz:")
        if st.button("Sohbete Katıl"):
            st.session_state["kullanici_ismi"] = isim
            st.rerun()
    else:
        # 1 saniyede bir sayfayı yeniler
        st_autorefresh(interval=1000, key="chat_refresh")
        
        st.write(f"Kullanıcı: **{st.session_state['kullanici_ismi']}**")
        
        # 2. Mesajları Google Sheets'ten çek
        try:
            url = "https://script.google.com/macros/s/AKfycbzgEnk0Bu94xOPFF7w-jBlYhiy6PzAOST0W_6VBjIIgdJhlvImjtSWt4qv4E1jENLyxLQ/exec"
            cevap = requests.get(url).json()
            
            # Mesaj kutusu alanı
            for m in cevap:
                st.markdown(f"**{m['isim']}**: {m['mesaj']}")
        except:
            st.warning("Sohbet yükleniyor...")
            
        # 3. Mesaj gönder
        with st.form("chat_form", clear_on_submit=True):
            yeni_mesaj = st.text_input("Mesaj yaz:")
            if st.form_submit_button("Gönder"):
                requests.post(url, json={"isim": st.session_state["kullanici_ismi"], "mesaj": yeni_mesaj})
                st.rerun()

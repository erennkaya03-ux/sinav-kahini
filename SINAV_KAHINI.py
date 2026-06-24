import streamlit as st
import google.generativeai as genai
from datetime import datetime
from pypdf import PdfReader
import io

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
</style>
""", unsafe_allow_html=True)

# --- SANAL HAFIZA KURULUMU ---
if "ders_notlari" not in st.session_state:
    st.session_state["ders_notlari"] = {}

if "api_key_kayitli" not in st.session_state:
    st.session_state["api_key_kayitli"] = ""

# --- TEK DÜZEN HESAP PLANI VERİTABANI ---
HESAP_PLANI = {"100": "KASA", "101": "ALINAN ÇEKLER", "102": "BANKALAR", "103": "VERİLEN ÇEKLER (-)", "120": "ALICILAR", "121": "ALACAK SENETLERİ", "153": "TİCARİ MALLAR", "191": "İNDİRİLECEK KDV", "254": "TAŞITLAR", "255": "DEMİRBAŞLAR", "257": "BİRİKMİŞ AMORTİSMANLAR (-)", "320": "SATICILAR", "321": "BORÇ SENETLERİ", "391": "HESAPLANAN KDV", "500": "SERMAYE", "600": "YURTİÇİ SATIŞLAR", "621": "STMM (-)", "770": "GENEL YÖNETİM GİDERLERİ"}

# --- GİRİŞ KONTROLÜ (KEY YOKSA SADECE BU EKRAN GÖRÜNÜR) ---
if not st.session_state["api_key_kayitli"]:
    st.title("🔮 Sınav Kahini Giriş")
    st.subheader("Hoş geldin kanka!")
    girilen_key = st.text_input("🔑 Gemini API Key Girin:", type="password", help="Google AI Studio'dan aldığın ücretsiz anahtarı buraya yapıştır kanka.")
    
    if st.button("Sisteme Giriş Yap 🚀", use_container_width=True):
        if girilen_key:
            st.session_state["api_key_kayitli"] = girilen_key
            st.success("Giriş başarılı! Uygulama açılıyor...")
            st.rerun()
        else:
            st.error("Lütfen geçerli bir anahtar gir kanka!")
            
    st.info("💡 **Nasıl Ücretsiz Şifre Alırım?**\n1. [Google AI Studio](https://aistudio.google.com/) sitesine git.\n2. Giriş yapıp **'Get API Key'** butonuna bas.\n3. Kodu kopyala ve yukarıdaki kutuya yapıştır!")

# --- UYGULAMA ANA EKRANI ---
else:
    genai.configure(api_key=st.session_state["api_key_kayitli"])
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    st.title("🔮 Sınav Kahini Mobil")
    
    if st.button("🔒 Oturumu Kapat / Key Değiştir", use_container_width=True):
        st.session_state["api_key_kayitli"] = ""
        st.rerun()

    st.markdown("---")

    # --- MOBİL ÜST SEKME SİSTEMİ ---
    sekme1, sekme2, sekme3, sekme4 = st.tabs(["📁 Arşiv", "📢 Not/PDF Yükle", "📝 Soru Odası", "📊 Hesapla"])

    # SEKME 1: DERS ARŞİVİ
    with sekme1:
        st.subheader("📌 Ders Kütüphanen")
        if st.session_state["ders_notlari"]:
            for ders, haftalar in st.session_state["ders_notlari"].items():
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
        else:
            st.caption("Henüz yüklenmiş bir ders notu yok kanka.")

    # SEKME 2: NOT VE PDF YÜKLEME
    with sekme2:
        st.subheader("📢 Ders Notu & PDF & Fotoğraf Yükle")
        ders_adi = st.selectbox("Ders:", ["Finansal Muhasebe", "Ticaret Hukuku", "Makro İktisat"], key="mob_ders")
        secilen_hafta = st.number_input("Hafta:", min_value=1, max_value=14, value=1, key="mob_hafta")
        
        st.markdown("### 1. Yazılı Not veya Tahta Fotoğrafı")
        ham_not = st.text_area("📝 Hocanın lafını karala veya yapıştır:", placeholder="Hoca buraya yıldız koydu...", height=80)
        
        yuklenen_foto = st.file_uploader("📸 Tahta Fotoğrafı Yükle (Galeri/Dosya):", type=["png", "jpg", "jpeg"])
        
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
                with st.spinner("📄 PDF okunuyor ve yapay zeka tarafından özetleniyor..."):
                    try:
                        reader = PdfReader(io.BytesIO(yuklenen_pdf.read()))
                        pdf_metni = ""
                        for sayfa in reader.pages[:10]:
                            pdf_metni += sayfa.extract_text() + "\n"
                        
                        komut = f"Aşağıdaki ders notu PDF metnini, bir üniversite öğrencisinin sınavda en çok işine yarayacak şekilde, önemli kavramları, formülleri ve muhasebe kodlarını vurgulayarak özetle kanka:\n\n{pdf_metni}"
                        yanit = model.generate_content(komut)
                        
                        st.session_state["ders_notlari"][ders_adi][secilen_hafta].append({"tip": "metin", "icerik": f"📄 **PDF ÖZETİ:**\n\n{yanit.text}"})
                    except Exception as e:
                        st.error(f"PDF Özetleme Hatası: {e}")
            
            st.success("Tüm yüklemeler başarıyla arşive işlendi! 📁")
            st.rerun()

    # SEKME 3: YAPAY ZEKA SORU ODASI
    with sekme3:
        st.subheader("📝 Yapay Zeka Soru Odası")
        ders_kontrol = st.selectbox("Ders Seçin:", ["Finansal Muhasebe", "Ticaret Hukuku", "Makro İktisat"], key="kahin_mob_ders")
        zorluk = st.select_slider("Zorluk Seviyesi:", options=["Kolay", "Orta", "Zor", "Hocanın Saplama Modu"], key="mob_zorluk")
        
        st.markdown("---")
        ornek_soru = st.text_area("✍️ Örnek Soru Yazınız (Opsiyonel):", placeholder="Kendi sorunu buraya yazarsan yapay zeka bunu çözer. Boş bırakırsan kendisi sıfırdan soru üretir kanka...", height=100)
        
        if st.button("🔮 Soru Hazırla / Çözdür", use_container_width=True):
            if ornek_soru:
                komut = f"Sen üniversitede {ders_kontrol} dersi veren bir hocasın. Öğrencinin sana gönderdiği şu soruyu adım adım, üniversite sınav formatına uygun şekilde çok detaylıca çöz ve anlat kanka. Varsa yevmiye kayıtlarını ve muhasebe mantığını tek tek göster:\n\n{ornek_soru}"
            else:
                komut = f"Sen üniversitede {ders_kontrol} dersi veren bir hocasın. {zorluk} seviyesinde üniversite sınavına uygun orijinal bir soru üret ve hemen altına '---' koyarak adım adım çok detaylı çözümünü yaz kanka."
            
            with st.spinner("🔮 Sihirli küre soruyu inceliyor..."):
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
        vize_notu = st.slider("Vize Notun?", min_value=0, max_value=100, value=40, key="mob_vize")
        sinif_ort = st.slider("Sınıf Ortalaması?", min_value=20, max_value=80, value=45, key="mob_ort")
        muhtemel_final = st.slider("🔮 Muhtemelen Final Notun Kaç Olur?", min_value=0, max_value=100, value=50, key="mob_muhtemel_final")
        
        st.markdown("---")
        
        vize_katki = vize_notu * 0.4
        final_katki = muhtemel_final * 0.6
        donem_notu = vize_katki + final_katki
        fark = donem_notu - sinif_ort
        
        # Harf Notu Karar Mantığı
        if muhtemel_final < 45:
            harf_notu = "FF (Final Barajı Altı)"
            durum = "Kaldın kanka ❌"
            renk = st.error
        elif donem_notu <=

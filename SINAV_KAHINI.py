import streamlit as st
import google.generativeai as genai
from datetime import datetime
from pypdf import PdfReader
import io

# Sayfa Ayarları ve Mobil Görünüm Optimizasyonu
st.set_page_config(page_title="Sınav Kahini", page_icon="🔮", layout="wide")

# --- SANAL HAFIZA KURULUMU ---
if "ders_notlari" not in st.session_state:
    st.session_state["ders_notlari"] = {}

if "baslangic_tarihi" not in st.session_state:
    st.session_state["baslangic_tarihi"] = datetime.now()

if "gecici_pdf_ozeti" not in st.session_state:
    st.session_state["gecici_pdf_ozeti"] = None

# --- TEK DÜZEN HESAP PLANI VERİTABANI ---
HESAP_PLANI = {"100": "KASA", "101": "ALINAN ÇEKLER", "102": "BANKALAR", "103": "VERİLEN ÇEKLER VE ÖDEME EMİRLERİ (-)", "108": "DİĞER HAZIR DEĞERLER", "110": "HİSSE SENETLERI", "120": "ALICILAR", "121": "ALACAK SENETLERİ", "122": "ALACAK SENETLERİ REESKONTU (-)", "126": "VERİLEN DEPOZİTO VE TEMİNATLAR", "131": "ORTAKLARDAN ALACAKLAR", "150": "İLK MADDE VE MALZEME", "151": "YARI MAMULLER - ÜRETİM", "152": "MAMULLER", "153": "TİCARİ MALLAR", "157": "DİĞER STOKLAR", "158": "STOK DEĞER DÜŞÜKLÜĞÜ KARŞILIĞI (-)", "159": "VERİLEN SİPARİŞ AVANSLARI", "180": "GELECEK AYLARA AİT GİDERLER", "181": "GELİR TAHAKKUKLARI", "190": "DEVREDEN KDV", "191": "İNDİRİLECEK KDV", "193": "PEŞİN ÖDENEN VERGİLER VE FONLAR", "197": "SAYIM VE TESELLÜM NOKSANLARI", "242": "İŞTİRAKLER", "250": "ARZİ VE ARAZİLER", "252": "BİNALAR", "253": "TESİS, MAKİNE VE CİHAZLAR", "254": "TAŞITLAR", "255": "DEMİRBAŞLAR", "256": "DİĞER MADDİ DURAN VARLIKLAR", "257": "BİRİKMİŞ AMORTİSMANLAR (-)", "258": "YAPILMAKTA OLAN YATIRIMLAR", "259": "VERİLEN AVANSLAR", "260": "HAKLAR", "268": "BİRİKMİŞ AMORTİSMANLAR (-)", "280": "GELECEK YILLARA AİT GİDERLER", "300": "BANKA KREDİLERİ", "304": "TAHVİL ANAPARA BORÇ TAKSİT VE FAİZLERİ", "320": "SATICILAR", "321": "BORÇ SENETLERİ", "322": "BORÇ SENETLERİ REESKONTU (-)", "331": "ORTAKLARA BORÇLAR", "335": "PERSONELE BORÇLAR", "360": "ÖDENECEK VERGİ VE FONLAR", "361": "ÖDENECEK SOSYAL GÜVENLİK KESİNTİLERİ", "380": "GELECEK AYLARA AİT GELİRLER", "381": "GİDER TAHAKKUKLARI", "391": "HESAPLANAN KDV", "397": "SAYIM VE TESELLÜM FAZLALARI", "400": "BANKA KREDİLERİ", "420": "SATICILAR", "500": "SERMAYE", "501": "ÖDENMEMİŞ SERMAYE (-)", "540": "YASAL YEDEKLER", "542": "OLAĞANÜSTÜ YEDEKLER", "570": "GEÇMİŞ YILLAR KARLARI", "580": "GEÇMİŞ YILLAR ZARARLARI (-)", "590": "DÖNEM NET KARI", "591": "DÖNEM NET ZARARI (-)", "600": "YURTİÇİ SATIŞLAR", "610": "SATIŞTAN İADELER (-)", "611": "SATIŞ İNDİRİMLERİ (-)", "620": "SATILAN MAMULLER MALİYETİ (-)", "621": "SATILAN TİCARİ MALLAR MALİYETİ (-)", "630": "ARAŞTIRMA VE GELİŞTİRME GİDERLERİ (-)", "631": "PAZARLAMA SATIŞ VE DAĞITIM GİDERLERİ (-)", "632": "GENEL YÖNETİM GİDERLERİ (-)", "642": "FAİZ GELİRLERİ", "643": "KOMİSYON GELİRLERİ", "644": "KONUSU KALMAYAN KARŞILIKLAR", "645": "MENKUL KIYMET SATIŞ KARLARI", "646": "KAMBİYO KARLARI", "647": "REESKONT FAİZ GELİRLERİ", "653": "KOMİSYON GİDERLERİ (-)", "654": "KARŞILIK GİDERLERİ (-)", "655": "MENKUL KIYMET SATIŞ ZARARLARI (-)", "656": "KAMBİYO ZARARLARI (-)", "657": "REESKONT FAİZ GİDERLERİ (-)", "671": "ÖNCEKİ DÖNEM GELİR VE KARLARI", "680": "ÇALIŞMAYAN KISIM GİDER VE ZARARLARI (-)", "681": "ÖNCEKİ DÖNEM GİDER VE ZARARLARI (-)", "689": "DİĞER OLAĞANDIŞI GİDER VE ZARARLAR (-)", "690": "DÖNEM KARI VEYA ZARARI", "760": "PAZARLAMA SATIŞ VE DAĞITIM GİDERLERİ", "770": "GENEL YÖNETİM GİDERLERİ", "780": "FİNANSMAN GİDERLERİ"}

# --- SOL MENÜ (SIDEBAR) AYARLARI ---
st.sidebar.title("🔮 Sınav Kahini v1.5")
st.sidebar.write("---")

# Mobil Güvenlik Girişi
user_api_key = st.sidebar.text_input("🔑 Gemini API Key Girin:", type="password", help="Uygulamayı kullanabilmek için Google AI Studio'dan aldığınız ücretsiz anahtarı buraya yapıştırın kanka.")

if user_api_key:
    genai.configure(api_key=user_api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
else:
    st.sidebar.warning("⚠️ Sistemi tetiklemek için bir API anahtarı girmelisiniz kanka.")

sayfa = st.sidebar.radio(
    "Gitmek İstediğiniz Sayfa:",
    [
        "🔐 Giriş & Ders Arşivi", 
        "📢 Hocanın Ağzından (Kritik Notlar)", 
        "📝 Sınav Kahini (Soru Pratik Odası)", 
        "📊 Harf Notu Garantör"
    ]
)

# KORUMA KALKANI: Şifre girilmediyse sayfaları gösterme
if not user_api_key:
    st.title("🔮 Sınav Kahini Mobil Dünyasına Hoş Geldin!")
    st.info("Kanka, bu uygulamayı arkadaşınla ortak kullanabilmen için güvenli hale getirdik. Sol menüdeki **'Gemini API Key Girin'** kutucuğuna kendi şifreni yapıştırdığın an tüm sistem açılacak!")
    st.markdown("""
    ### 🔑 Nasıl Ücretsiz Şifre Alırım?
    1. **[Google AI Studio](https://aistudio.google.com/)** sitesine git.
    2. Google hesabınla giriş yapıp **"Get API Key"** butonuna bas.
    3. Kodunu kopyala ve sol taraftaki kutuya yapıştır. Arkadaşın da kendi telefonu için aynısını yapabilir!
    """)
else:
    # SAYFA 1: GİRİŞ & DERS ARŞİVİ
    if sayfa == "🔐 Giriş & Ders Arşivi":
        st.title("🔐 Giriş & Ders Kütüphanesi")
        st.write("Doğrudan havuza attığın ders notlarını, PDF özetlerini ve mini galeri şeklindeki tahta fotoğraflarını buradan inceleyebilirsin.")
        
        if st.session_state["ders_notlari"]:
            st.subheader("📌 Güncel Sınav Tüyoları Arşivi")
            
            for ders, haftalar in st.session_state["ders_notlari"].items():
                with st.expander(f"📁 {ders} ({len(haftalar)} Hafta İçeriği Kayıtlı)"):
                    for hafta, veri_listesi in sorted(haftalar.items()):
                        st.markdown(f"### 🗓️ {hafta}. Hafta İçeriği")
                        st.markdown("📝 **Yazılı Notlar & PDF Özetleri:**")
                        metin_var_mi = False
                        for idx, eleman in enumerate(veri_listesi):
                            if eleman["tip"] == "metin":
                                metin_var_mi = True
                                benzersiz_key = f"{ders}_{hafta}_{idx}"
                                st.info(f"**İçerik {idx+1}:** {eleman['icerik']}")
                                
                                btn_col1, btn_col2, _ = st.columns([2, 2, 6])
                                with btn_col1:
                                    if st.button("✏️ Düzenle", key=f"edit_btn_{benzersiz_key}"):
                                        st.session_state[f"duzenleme_aktif_{benzersiz_key}"] = True
                                with btn_col2:
                                    if st.button("🗑️ Notu Sil", key=f"del_btn_{benzersiz_key}"):
                                        st.session_state["ders_notlari"][ders][hafta].pop(idx)
                                        if not st.session_state["ders_notlari"][ders][hafta]:
                                            del st.session_state["ders_notlari"][ders][hafta]
                                        if not st.session_state["ders_notlari"][ders]:
                                            del st.session_state["ders_notlari"][ders]
                                        st.toast("İçerik silindi! 🗑️")
                                        st.rerun()
                                
                                if st.session_state.get(f"duzenleme_aktif_{benzersiz_key}", False):
                                    yeni_not_metni = st.text_area("İçeriği Güncelle:", value=eleman['icerik'], key=f"text_area_{benzersiz_key}")
                                    if st.button("💾 Kaydet", key=f"save_btn_{benzersiz_key}"):
                                        st.session_state["ders_notlari"][ders][hafta][idx]["icerik"] = yeni_not_metni
                                        st.session_state[f"duzenleme_aktif_{benzersiz_key}"] = False
                                        st.toast("İçerik güncellendi! 💾")
                                        st.rerun()
                        
                        if not metin_var_mi:
                            st.caption("Bu hafta için yazılı veya özet metin bulunmuyor.")
                            
                        st.write("") 
                        st.markdown("📸 **Tahta / Slayt Galerisi:**")
                        fotograflar = [el for el in veri_listesi if el["tip"] == "fotograf"]
                        
                        if fotograflar:
                            foto_sutunlari = st.columns(2)  # Mobil için 2 sütun daha iyi
                            for f_idx, foto_eleman in enumerate(fotograflar):
                                aktif_sutun = f_idx % 2
                                with foto_sutunlari[aktif_sutun]:
                                    with st.container(border=True):
                                        st.image(foto_eleman["icerik"], use_container_width=True)
                                        gercek_idx = veri_listesi.index(foto_eleman)
                                        if st.button("🗑️ Resmi Sil", key=f"del_foto_{ders}_{hafta}_{f_idx}"):
                                            st.session_state["ders_notlari"][ders][hafta].pop(gercek_idx)
                                            if not st.session_state["ders_notlari"][ders][hafta]:
                                                del st.session_state["ders_notlari"][ders][hafta]
                                            if not st.session_state["ders_notlari"][ders]:
                                                del st.session_state["ders_notlari"][ders]
                                            st.toast("Fotoğraf galeriden silindi! 🗑️")
                                            st.rerun()
                        else:
                            st.caption("Bu hafta için yüklenmiş fotoğraf bulunmuyor.")
                        st.write("---")
        else:
            st.info("Henüz kaydedilmiş bir ders veya fotoğraf bulunamadı.")

    # SAYFA 2: HOCANIN AĞZINDAN
    elif sayfa == "📢 Hocanın Ağzından (Kritik Notlar)":
        st.title("📢 Hocanın Ağzından (Doğrudan Havuza Aktarım)")
        st.write("Derste hocanın lafını yazın, tahtanın fotoğrafını çekin ya da hocanın slayt PDF'ini yükleyip anında özetletin!")
        
        with st.container(border=True):
            st.subheader("✍️ Anlık Veri, Fotoğraf veya PDF Girişi")
            ders_adi = st.selectbox("Ders Seçin:", ["Finansal Muhasebe", "Ticaret Hukuku", "Makro İktisat"])
            gun_farki = (datetime.now() - st.session_state["baslangic_tarihi"]).days
            tahmini_hafta = max(1, min(14, (gun_farki // 7) + 1))
            secilen_hafta = st.number_input("Ders Haftası:", min_value=1, max_value=14, value=tahmini_hafta)
            
            st.write("---")
            
            st.markdown("📝 **Seçenek A: Yazılı Not Gir**")
            ham_not = st.text_area("Hocanın lafını buraya karala:", placeholder="Örn: Bu tanımdan kesin soru var dedi...", height=100)
            
            st.markdown("📸 **Seçenek B: Tahta Fotoğrafı Yükle**")
            yuklenen_foto = st.file_uploader("Fotoğrafı seç:", type=["png", "jpg", "jpeg"])
                
            st.markdown("📄 **Seçenek C: Ders Slaytı / PDF Özetle**")
            yuklenen_pdf = st.file_uploader("Slayt PDF dosyasını buraya bırak:", type=["pdf"])
            ozetle_butonu = st.button("⚡ PDF'i Oku ve Özetle")

            if ozetle_butonu and yuklenen_pdf is not None:
                with st.spinner("📄 PDF okunuyor ve yapay zeka sınav özetini çıkartıyor..."):
                    try:
                        pdf_okuyucu = PdfReader(io.BytesIO(yuklenen_pdf.read()))
                        ham_pdf_metni = ""
                        for sayfa_obj in pdf_okuyucu.pages:
                            sayfa_metni = sayfa_obj.extract_text()
                            if sayfa_metni:
                                ham_pdf_metni += sayfa_metni + "\n"
                        
                        if len(ham_pdf_metni.strip()) < 10:
                            st.error("Kanka bu PDF'in içi boş veya tarama resimlerden oluşuyor, metin okunamadı.")
                        else:
                            komut = f"Sen üniversitede {ders_adi} dersi veren bir profesörsün. Sınavda çıkabilecek kritik yerleri, önemli tanımları içerecek şekilde maddeler halinde harika bir sınav özeti çıkart kanka.\n\nDERS DÖKÜMANI:\n{ham_pdf_metni[:15000]}"
                            response = model.generate_content(komut)
                            st.session_state["gecici_pdf_ozeti"] = response.text
                    except Exception as e:
                        st.error(f"PDF işlenirken bir hata oluştu: {e}")

            if st.session_state["gecici_pdf_ozeti"]:
                st.write("---")
                st.subheader("📋 Çıkarılan Akıllı Sınav Özeti")
                st.markdown(st.session_state["gecici_pdf_ozeti"])
                
                st.write("---")
                st.warning(f"💡 **Sistem Soruyor:** Bu özeti **{ders_adi}** dersinin **{secilen_hafta}. Hafta** kütüphanesine aktarayım mı kanka?")
                
                aktar_col1, aktar_col2 = st.columns(2)
                with aktar_col1:
                    if st.button("✅ Evet, Kütüphaneye Aktar"):
                        if ders_adi not in st.session_state["ders_notlari"]:
                            st.session_state["ders_notlari"][ders_adi] = {}
                        if secilen_hafta not in st.session_state["ders_notlari"][ders_adi]:
                            st.session_state["ders_notlari"][ders_adi][secilen_hafta] = []
                        
                        st.session_state["ders_notlari"][ders_adi][secilen_hafta].append({
                            "tip": "metin", 
                            "icerik": f"📋 [PDF ÖZETİ] -\n{st.session_state['gecici_pdf_ozeti']}"
                        })
                        st.success("Harika! Özet arşive fırlatıldı.")
                        st.session_state["gecici_pdf_ozeti"] = None
                        st.balloons()
                        st.rerun()
                with aktar_col2:
                    if st.button("❌ Hayır, Özet İptal"):
                        st.session_state["gecici_pdf_ozeti"] = None
                        st.toast("Özet arşive eklenmeden silindi kanka.")
                        st.rerun()
            
            st.write("---")
            if st.button("🚀 Seçenek A veya B'yi Havuza Gönder"):
                if ham_not or yuklenen_foto:
                    if ders_adi not in st.session_state["ders_notlari"]:
                        st.session_state["ders_notlari"][ders_adi] = {}
                    if secilen_hafta not in st.session_state["ders_notlari"][ders_adi]:
                        st.session_state["ders_notlari"][ders_adi][secilen_hafta] = []
                    
                    if ham_not:
                        st.session_state["ders_notlari"][ders_adi][secilen_hafta].append({"tip": "metin", "icerik": ham_not})
                    if yuklenen_foto:
                        st.session_state["ders_notlari"][ders_adi][secilen_hafta].append({"tip": "fotograf", "icerik": yuklenen_foto.read()})
                    
                    st.success("Başarılı! Havuza gönderildi.")
                    st.balloons()
                    st.rerun()

    # SAYFA 3: SINAV KAHİNİ
    elif sayfa == "📝 Sınav Kahini (Soru Pratik Odası)":
        st.title("📝 Sınav Kahini - Soru Pratik Odası 🧠")
        ders_kontrol = st.selectbox("Ders Seçin:", ["Finansal Muhasebe", "Ticaret Hukuku", "Makro İktisat"], key="kahin_ders_ust")
        
        with st.container(border=True):
            st.subheader("⚙️ Soru Kriterleri")
            hafta_secim = st.number_input("Ders Haftası:", min_value=1, max_value=14, value=1, key="kahin_hafta")
            zorluk = st.select_slider("Zorluk:", options=["Kolay", "Orta", "Zor", "Hocanın Saplama Modu"])
            s_tipi = st.radio("Soru Biçimi:", ["Klasik (Açıklamalı/Hesaplamalı)", "Çoktan Seçmeli (Test)"])
            ornek_soru = st.text_area("Varsa Örnek Soru Yapıştır (İsteğe Bağlı):", placeholder="Örn: X işletmesi satmıştır...", height=100)
            uret_butonu = st.button("🔮 Özel Soru Üret")

        if uret_butonu:
            ilgili_hafta_notlari = []
            if ders_kontrol in st.session_state["ders_notlari"] and hafta_secim in st.session_state["ders_notlari"][ders_kontrol]:
                for el in st.session_state["ders_notlari"][ders_kontrol][hafta_secim]:
                    if el["tip"] == "metin":
                        ilgili_hafta_notlari.append(el["icerik"])
            
            havuz_bilgisi = "\n".join(ilgili_hafta_notlari) if ilgili_hafta_notlari else f"Genel üniversite {ders_kontrol} müfredatı."
            komut = f"Sen bir üniversite {ders_kontrol} profesörüsün. Soru üret. Zorluk: {zorluk}, Biçim: {s_tipi}, Havuz Notu: {havuz_bilgisi}\nÖrnek: {ornek_soru}\nFormat:\n### ❓ Üretilen Sınav Sorusu\n... metin ...\n---\n### 🔑 Detaylı Adım Adım Çözüm\n... çözüm ..."
            
            with st.spinner("🔮 Kahin soruyu tasarlıyor..."):
                try:
                    response = model.generate_content(komut)
                    ham_cevap = response.text
                    if "---" in ham_cevap:
                        parcalar = ham_cevap.split("---")
                        st.session_state["guncel_soru_metni"] = parcalar[0].strip()
                        st.session_state["guncel_cozum_metni"] = parcalar[1].strip()
                    else:
                        st.session_state["guncel_soru_metni"] = ham_cevap
                        st.session_state["guncel_cozum_metni"] = "Çözüm ayrıştırılamadı."
                except Exception as e:
                    st.error(f"Yapay zeka hatası: {e}")
        
        if "guncel_soru_metni" in st.session_state:
            with st.container(border=True):
                st.markdown(st.session_state["guncel_soru_metni"])
                st.write("---")
                with st.expander("🔑 Doğru Çözümü Göster"):
                    st.markdown(st.session_state["guncel_cozum_metni"])

        if ders_kontrol == "Finansal Muhasebe":
            with st.container(border=True):
                st.subheader("📋 TDHP Kopya Duvarı")
                arama_terimi = st.text_input("🔍 Hesap Kodu veya Adı Ara:", placeholder="Örn: 100...").upper()
                
                with st.container(height=300, border=False):
                    for kod, ad in HESAP_PLANI.items():
                        if arama_terimi == "" or arama_terimi in kod or arama_terimi in ad:
                            vurgu = "🔹" if "(-)" in ad else "▪️"
                            st.markdown(f"**{kod}** | {vurgu} {ad}")

    # SAYFA 4: HARF NOTU GARANTÖR
    elif sayfa == "📊 Harf Notu Garantör":
        st.title("📊 Harf Notu Garantör")
        st.warning("🚨 Finalden **45** altı alan veya Ortalama **40** altı olan doğrudan kalır (**FF**).")
        
        with st.container(border=True):
            st.subheader("📝 Sınav Verileri")
            vize_notu = st.slider("Vize Notun Kaç?", min_value=0, max_value=100, value=50)
            vize_oran = st.number_input("Vize Etki Oranı (%)", min_value=10, max_value=90, value=40)
            final_oran = 100 - vize_oran
            sinif_ortalamasi = st.slider("Sınıf Ortalaması Kaç?", min_value=20, max_value=85, value=45)

        with st.container(border=True):
            st.subheader("🎯 Hedef Analiz Merkezi")
            hedef_harf = st.select_slider("Hedeflediğin Harf Notu:", options=["DD", "DC", "CC", "CB", "BB", "BA", "AA"], value="CC")
            
            if hedef_harf == "AA": gereken_ortalama = sinif_ortalamasi + 25
            elif hedef_harf == "BA": gereken_ortalama = sinif_ortalamasi + 18
            elif hedef_harf == "BB": gereken_ortalama = sinif_ortalamasi + 12
            elif hedef_harf == "CB": gereken_ortalama = sinif_ortalamasi + 6
            elif hedef_harf == "CC": gereken_ortalama = float(sinif_ortalamasi)
            elif hedef_harf == "DC": gereken_ortalama = sinif_ortalamasi - 5
            else: gereken_ortalama = sinif_ortalamasi - 10
            
            grid_ortalama = max(40.0, gereken_ortalama)
            vize_katkisi = vize_notu * (vize_oran / 100)
            gereken_final = (grid_ortalama - vize_katkisi) / (final_oran / 100)
            gereken_final = max(45.0, gereken_final)
            
            if gereken_final > 100:
                st.error(f"🚨 Finalden 100 alsan bile **{hedef_harf}** gelmiyor kanka.")
            else:
                st.metric(label=f"🎯 Gerekli Minimum Final Notu:", value=f"{round(gereken_final, 1)}")
            
            st.write("---")
            tahmini_final = st.slider("🔮 Peki sen finalden tahminen kaç alırsın?", min_value=0, max_value=100, value=50)
            toplam_basari_notu = (vize_notu * (vize_oran / 100)) + (tahmini_final * (final_oran / 100))
            
            if tahmini_final < 45 or toplam_basari_notu < 40:
                st.error("💀 Baraj altında kaldığın için doğrudan **FF** düşüyor kanka.")
            else:
                if toplam_basari_notu >= sinif_ortalamasi + 25: gelen_harf = "AA"
                elif toplam_basari_notu >= sinif_ortalamasi + 18: gelen_harf = "BA"
                elif toplam_basari_notu >= sinif_ortalamasi + 12: gelen_harf = "BB"
                elif toplam_basari_notu >= sinif_ortalamasi + 6: gelen_harf = "CB"
                elif toplam_basari_notu >= sinif_ortalamasi: gelen_harf = "CC"
                elif toplam_basari_notu >= sinif_ortalamasi - 5: gelen_harf = "DC"
                else: gelen_harf = "DD"
                
                if gelen_harf in ["DD", "DC"]:
                    st.warning(f"⚠️ Yıl sonu notun: **{round(toplam_basari_notu, 1)}** | Harf Notun: **{gelen_harf}**.")
                else:
                    st.success(f"🔥 Yıl sonu notun: **{round(toplam_basari_notu, 1)}** | Harf Notun: **{gelen_harf}**. Helal!")
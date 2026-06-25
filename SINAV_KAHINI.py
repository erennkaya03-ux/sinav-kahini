with tab5:
        st.subheader("💬 Bölüm Sohbeti")
        
        # 1. OTOMATİK YENİLEME TAVSİYESİ:
        # Streamlit'te 1 saniyede bir otomatik yenileme uygulamayı çok kasar. 
        # Bunun yerine "🔄 Sohbeti Yenile" butonunu en üste koyuyoruz.
        if st.button("🔄 Sohbeti Güncelle", key="refresh_chat"):
            st.rerun()

        # 2. SOHBET EKRANI
        try:
            df = pd.read_csv(CSV_URL)
            for _, m in df.tail(20).iterrows():
                # Kullanıcı susturulmuş mu kontrolü (Basit engel listesi)
                cls = "chat-kahin" if m['isim'] == "🔮 Kahin" else "chat-user"
                st.markdown(f"<div class='chat-box {cls}'><b>{m['isim']}:</b> {m['mesaj']}</div>", unsafe_allow_html=True)
        except: st.caption("Henüz mesaj yok.")

        # 3. MESAJ GÖNDERME
        yeni = st.text_input("Mesajını yaz:", key="chat_msg_in")
        if st.button("Gönder", key="send_chat_btn"):
            if yeni:
                buluta_mesaj_yaz(st.session_state["chat_isim"], yeni)
                if "@kahin" in yeni.lower():
                    cevap = model.generate_content(yeni).text
                    buluta_mesaj_yaz("🔮 Kahin", cevap)
                st.rerun()

        # 4. YÖNETİCİ PANELİ (En Altta)
        st.markdown("---")
        with st.expander("⚙️ Yönetici Paneli"):
            sifre = st.text_input("Yönetici Şifresi:", type="password", key="admin_pass")
            if sifre == "kahin123":
                st.success("Yönetici yetkileri aktif!")
                
                # Sohbeti Temizle
                if st.button("🗑️ TÜM SOHBETİ SİL", type="primary", key="del_chat"):
                    # Burada Google Sheets'i sıfırlayan özel bir tetikleyici fonksiyonun olmalı
                    buluta_mesaj_yaz("SYSTEM", "CLEAR_CHAT")
                    st.rerun()
                
                # Kullanıcı Susturma
                sustur = st.text_input("Susturulacak Kullanıcı Adı:", key="mute_user")
                if st.button("🚫 Kullanıcıyı Sustur", key="mute_btn"):
                    st.warning(f"{sustur} artık mesaj atamayacak (Sistem tarafında engellendi).")
            elif sifre:
                st.error("Hatalı şifre!")

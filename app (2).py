import streamlit as st
from bot import build_agent
from langchain_core.messages import AIMessage

# -----------------------------------------------------
# 1. KONFIGURASI & ASET GAMBAR
# -----------------------------------------------------
st.set_page_config(
    page_title="Tingang AI - Katingan",
    page_icon="🦅",
    layout="centered"
)

# URL Logo Kabupaten Katingan (Link Baru yang Bapak Berikan)
LOGO_KATINGAN_URL = "https://upload.wikimedia.org/wikipedia/commons/4/4b/Lambang_Kabupaten_Katingan.png"
LOGO_TINGANG_URL = "https://upload.wikimedia.org/wikipedia/commons/9/99/Penelopides_manillae.jpg"
LOGO_TINGANG2_URL = "https://imgur.com/RQRYhKQ"
# Avatar Pengguna (Kita pakai emoji standar agar rapi)
USER_AVATAR = "🧑‍💻" 

# -----------------------------------------------------
# 2. CUSTOM CSS (Desain Tampilan)
# -----------------------------------------------------
st.markdown("""
    <style>
    /* Background Gradasi Hijau - Putih */
    .stApp {
        background: linear-gradient(to bottom, #f0f7f0, #ffffff);
    }
    
    /* Mengatur ukuran Logo di dalam Chat agar pas */
    .stChatMessage .avatar {
        width: 50px !important;
        height: 50px !important;
        border-radius: 5px !important; /* Sedikit melengkung */
        object-fit: contain !important; /* Agar logo tidak terpotong */
        background-color: transparent !important;
    }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------
# 3. SIDEBAR & HEADER
# -----------------------------------------------------
with st.sidebar:
    # Menampilkan logo di sidebar
    st.image(LOGO_KATINGAN_URL, width=120)
   # Ikon Hutan
    st.title("Tentang Tingang")
    st.info(
        """
        **Tingang** adalah Asisten AI untuk pendidikan di Kalimantan.
        
        **Fitur:**
        - 🧮 Tutor Matematika & Sains
        - 📰 Berita Pendidikan Terkini
        - 🌲 Analogi Lokal Dayak
        """
    )
    if st.button("🗑️ Hapus Riwayat Chat"):
        st.session_state.messages = []
        st.session_state.agent = build_agent()
        st.rerun()


# Judul Utama dengan Logo di sebelahnya
col1, col2 = st.columns([1, 5])
with col1:
    st.image(LOGO_TINGANG_URL, width=100)
with col2:
    st.title("TINGANG AI")
    st.caption("Pemandu Ilmu & Pusat Informasi Pendidikan")

st.markdown("---")

# -----------------------------------------------------
# 4. LOGIKA AGENT
# -----------------------------------------------------

if "agent" not in st.session_state:
    st.session_state.agent = build_agent()
    
agent_executor = st.session_state.agent

# Pesan Sambutan (Greeting)
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": """
            **Tabe Salamat!** 🙏
            
            Saya **TINGANG**, Asisten Cerdas.
            
            Saya siap membantu:
            1. 📚 Menjelaskan pelajaran sekolah.
            2. 📰 Memberikan info pendidikan terkini.
            
            Apa yang ingin ditanyakan hari ini?
            """
        }
    ]

# -----------------------------------------------------
# 5. TAMPILAN CHAT
# -----------------------------------------------------

for message in st.session_state.messages:
    # Logika Pemilihan Avatar
    if message["role"] == "assistant":
        icon_avatar = LOGO_TINGANG_URL # Pakai Logo Katingan
    else:
        icon_avatar = USER_AVATAR # Pakai Emoji User
        
    with st.chat_message(message["role"], avatar=icon_avatar):
        st.markdown(message["content"], unsafe_allow_html=True)

# -----------------------------------------------------
# 6. INPUT USER & RESPON
# -----------------------------------------------------

if prompt := st.chat_input("Ketik pertanyaan Anda di sini..."):
    # Tampilkan Pesan User
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)

    # Proses Jawaban
    with st.spinner("Sedang mencari informasi..."):
        full_response = ""
        # Pastikan Logo Katingan muncul saat sedang mengetik
        with st.chat_message("assistant", avatar=LOGO_KATINGAN_URL):
            st_callback = st.empty()
            
            try:
                for step in agent_executor.stream({"input": prompt}):
                    # Menampilkan indikator alat (tool)
                    if "actions" in step:
                        for action in step["actions"]:
                            st.caption(f"⚙️ *Mengakses data: {action.tool}...*")
                                                
                    # Menampilkan teks jawaban
                    if "output" in step:
                        full_response += step["output"]
                        st_callback.markdown(full_response, unsafe_allow_html=True)
                    elif isinstance(step, AIMessage):
                        full_response += step.content
                        st_callback.markdown(full_response, unsafe_allow_html=True)
                        
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")

        # Simpan ke riwayat
        st.session_state.messages.append({"role": "assistant", "content": full_response})

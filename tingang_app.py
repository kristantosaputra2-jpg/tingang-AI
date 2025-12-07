%%writefile app.py

# Import semuanya dulu
import streamlit as st
from bot import build_agent
# ... (imports lainnya)

# Konfigurasi Halaman (Ikon dan Judul Tab Browser)
st.set_page_config(page_title="🦅 TINGANG | Asisten Belajar Pedalaman", page_icon="🦅") 

# Judul Utama di Halaman
st.title("🦅 TINGANG: Pemandu Ilmu dari Pedalaman") # <-- Judul sudah diubah

# Caption/Deskripsi
st.caption("Tutor AI yang fokus pada bimbingan bertahap dan konteks lokal.") 


# -----------------------------------------------------------------
# B. INISIALISASI AGENT DAN SESSION STATE
# -----------------------------------------------------------------

# Session state untuk Agent TINGANG
if "agent" not in st.session_state:
    # Panggil fungsi build_agent dari bot.py untuk membuat Agent
    st.session_state.agent = build_agent()

# Session state untuk riwayat pesan
if "messages" not in st.session_state:
    # Pesan sambutan awal dari TINGANG
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Selamat datang! Saya Tingang, siap memandumu belajar hari ini. Mau eksplorasi konsep matematika, atau tahu fakta seru Kalimantan?"
    }]

agent = st.session_state.agent

# Tombol reset chat
reset_chat_button = st.button("Reset Chat (Mulai Baru)")
if reset_chat_button:
    st.session_state.messages = []
    # Buat ulang agent untuk membersihkan memori internal LangChain
    st.session_state.agent = build_agent()
    # Muat ulang halaman agar pesan sambutan muncul
    st.rerun()


# -----------------------------------------------------------------
# C. LOGIKA TAMPILAN DAN CHAT INPUT
# -----------------------------------------------------------------

# Tampilkan semua pesan sebelumnya
for m in st.session_state.messages:
    # Menggunakan role 'assistant' untuk output tool agar terlihat berbeda
    role_display = "assistant" if m["role"] in ["assistant", "🛠️"] else "user"
    with st.chat_message(role_display):
        st.markdown(m["content"], unsafe_allow_html=True)


user_input = st.chat_input("Tanyakan sesuatu...")


if user_input:
    # 1. Tambahkan input pengguna ke riwayat dan tampilkan
    st.session_state.messages.append({
        "role": "user",
        "content": user_input,
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    # 2. Panggil Agent TINGANG
    with st.spinner("Tingang sedang memproses..."):
        full_response = ""

        # Area untuk menampilkan streaming output dan tool call
        with st.chat_message("assistant"):
            st_callback = st.empty() # Placeholder untuk streaming teks

            for step in agent.stream({"input": user_input}):
                # Aksi (Tool Call)
                if "actions" in step.keys():
                    for action in step["actions"]:
                        tool_name = action.tool
                        tool_input = action.tool_input

                        # Desain khusus untuk menampilkan Tool Call
                        tool_message = f"""
                        <div style="border-left: 5px solid #4CAF50; padding:6px 10px; background-color: #f0fff0; border-radius:4px; font-size:14px; margin-top: 10px;">
                          ⚙️ <b>TINGANG Memanggil Tool: {tool_name}</b> <br>
                          Input: <code>{tool_input}</code>
                        </div>
                        """

                        # Simpan tool call ke riwayat
                        st.session_state.messages.append({
                            "role": "🛠️",
                            "content": tool_message,
                        })

                        # Tampilkan tool call
                        st.markdown(tool_message, unsafe_allow_html=True)

                # Output (Respons Teks)
                if "output" in step.keys():
                    ai_output_part = step["output"]
                    full_response += ai_output_part
                    st_callback.markdown(full_response, unsafe_allow_html=True)

                # Output Final LangChain Agent
                if isinstance(step, AIMessage):
                    ai_output = step.content
                    full_response += ai_output
                    st_callback.markdown(full_response, unsafe_allow_html=True)


    # 3. Simpan Respons Akhir ke Session State
    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response,
    })

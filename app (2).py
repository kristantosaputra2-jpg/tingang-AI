%%writefile app.py (2)
# Import semuanya dulu
import streamlit as st
from bot import build_agent

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="Tingang AI", page_icon="🦅")
st.title("🦅 Tingang AI: Asisten Guru Kalteng")

# --- 2. SETUP API KEY (PENTING!) ---
# Masukkan API Key Replicate Bapak di sini (atau di st.secrets untuk keamanan)
if "REPLICATE_API_TOKEN" not in os.environ:
    # GANTI TULISAN DI BAWAH INI DENGAN API KEY BAPAK YANG PANJANG (r8_...)
    os.environ["REPLICATE_API_TOKEN"] = "api_token"

# --- 3. INISIALISASI OTAK AI (Hanya jalan sekali di awal) ---
if "agent_executor" not in st.session_state:
    with st.spinner("Tingang sedang bersiap terbang..."):
        try:
            # A. Siapkan LLM (Otak)
            # Menggunakan Llama-3-8b atau 70b dari Replicate
            llm = Replicate(
                model="meta/meta-llama-3-8b-instruct",
                model_kwargs={"temperature": 0.7, "max_length": 500}
            )

            # B. Siapkan Tools (Kemampuan)
            # Kita pakai 'llm-math' dulu untuk tes berhitung
            tools = load_tools(["llm-math"], llm=llm)

            # C. Siapkan Prompt (Instruksi)
            # Menggunakan prompt standar ReAct
            prompt = hub.pull("hwchase17/react")

            # D. Rakit Agen
            agent = create_react_agent(llm, tools, prompt)
            
            # E. SIMPAN KE MEMORI (Solusi Error 'Not Defined')
            st.session_state.agent_executor = AgentExecutor(
                agent=agent, 
                tools=tools, 
                verbose=True,
                handle_parsing_errors=True # Supaya tidak error kalau AI bingung format
            )
            
        except Exception as e:
            st.error(f"Gagal menyiapkan Tingang: {e}")
            st.stop()

# --- 4. ANTARMUKA CHAT ---

# Tampilkan riwayat chat jika ada
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input dari User
if prompt := st.chat_input("Apa yang ingin Bapak tanyakan?"):
    # 1. Tampilkan pesan user
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Proses jawaban AI
    with st.chat_message("assistant"):
        try:
            # Panggil agen yang sudah disimpan di session_state
            response = st.session_state.agent_executor.invoke({"input": prompt})
            
            # Ambil hasil jawaban
            output_text = response["output"]
            
            st.markdown(output_text)
            st.session_state.messages.append({"role": "assistant", "content": output_text})
            
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")

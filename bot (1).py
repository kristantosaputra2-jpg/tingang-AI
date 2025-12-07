
from langchain.agents import agent_types, initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain_community.llms import Replicate
from langchain_core.tools import tool
from langchain_community.utilities import SerpAPIWrapper
from langchain.tools import Tool
from dotenv import load_dotenv
import os

# --- TOOLS ---

def parse_input(input_str):
    parts = input_str.split(";")
    return dict(part.split("=") for part in parts)

@tool
def kalkulator_persen(input: str) -> str:
    """Menghitung persentase. Format: 'persen=20;angka=50000'."""
    try:
        data = parse_input(input)
        return str((float(data['persen']) / 100) * float(data['angka']))
    except:
        return "Error format."

@tool
def kamus_kontekstual(input: str) -> str:
    """Menjelaskan istilah sulit dengan analogi lokal Kalimantan."""
    return f"Jelaskan istilah '{input}' menggunakan analogi sungai/hutan Kalimantan."

# Tool Pencarian Berita (Penting untuk persona baru)
search = SerpAPIWrapper()
tool_berita_pendidikan = Tool(
    name="cari_info_terkini",
    func=search.run,
    description="WAJIB digunakan untuk mencari BERITA TERBARU, KEBIJAKAN PENDIDIKAN, DATA REAL-TIME, atau HARGA."
)

# --- BUILD AGENT ---

def build_agent():
    load_dotenv()
    llm = Replicate(model="anthropic/claude-3.5-haiku")

    # SYSTEM PROMPT: Menanamkan Persona Ganda
    system_message = """
    Kamu adalah **TINGANG**, AI Agent Pendidikan dari Kalimantan.
    
    **TUGAS UTAMA:**
    1. **Tutor:** Bimbing siswa belajar dengan sabar. Gunakan analogi lokal untuk konsep sulit.
    2. **Reporter Pendidikan:** Berikan informasi TERKINI mengenai kebijakan pendidikan (Kurikulum, BOS, PPG, Beasiswa) dan berita umum.

    **PROSEDUR:**
    * Jika user bertanya **"Apa kabar terbaru..."** atau **"Kebijakan baru..."**, kamu WAJIB menggunakan tool `cari_info_terkini`. Jangan jawab pakai hafalan!
    * Jika user bertanya pelajaran, bimbing step-by-step.
    """

    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    
    tools = [kalkulator_persen, kamus_kontekstual, tool_berita_pendidikan]

    return initialize_agent(
        llm=llm,
        tools=tools,
        agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
        memory=memory,
        agent_kwargs={"system_message": system_message},
        handle_parsing_errors=True
    )

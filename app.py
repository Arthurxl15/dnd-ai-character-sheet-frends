import streamlit as st
import json
import math

# Configuração da Página
st.set_page_config(
    page_title="D&D 5e Character Builder",
    page_icon="🎲",
    layout="wide"
)

# Função para carregar o Banco de Dados
@st.cache_data
def load_db():
    try:
        with open('database.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

db = load_db()

# Título Principal
st.title("🧙‍♂️ Gerador de Personagem: Multiverso D&D")
st.markdown("Fontes: *Player's Handbook, Xanathar, Tasha & Mordenkainen*")
st.divider()

if not db:
    st.error("Erro: Arquivo 'database.json' não encontrado no repositório!")
    st.stop()

# --- 1. IDENTIDADE ---
st.header("1. Definições Iniciais")
col_r, col_c, col_s = st.columns(3)

with col_r:
    raca_sel = st.selectbox("Raça", list(db['racas'].keys()))
    
with col_c:
    classe_sel = st.selectbox("Classe", list(db['classes'].keys()))

with col_s:
    subclasses = db['classes'][classe_sel]['subclasses']
    sub_sel = st.selectbox("Subclasse", subclasses if subclasses else ["Classe Única"])

st.divider()

# --- 2. ATRIBUTOS (REGRAS OFICIAIS) ---
st.header("2. Atributos Base")
st.info("Regra Point Buy: Selecione entre 8 e 15. Os bônus de raça são somados automaticamente.")

bonus_raca = db['racas'][raca_sel]['bonus']
finais = {}

atr_cols = st.columns(6)
for i, status in enumerate(["FOR", "DES", "CON", "INT", "SAB", "CAR"]):
    with atr_cols[i]:
        # Input base limitado pelas regras do LDJ
        base = st.number_input(status, 8, 15, 10, key=f"base_{status}")
        
        # Soma bônus da raça
        adicional = bonus_raca.get(status, 0)
        total = base + adicional
        
        # Cálculo do Modificador: (Valor - 10) / 2 arredondado para baixo
        mod = math.floor((total - 10) / 2)
        finais[status] = {"total": total, "mod": mod}
        
        st.metric(label="Total", value=total, delta=f"Mod: {mod}")

st.divider()

# --- 3. MAGIAS, TRUQUES E TALENTOS ---
st.header("3. Especializações")
col_t, col_m, col_f = st.columns(3)

with col_t:
    truques_list = db['classes'][classe_sel]['truques']
    if truques_list:
        truques_sel = st.multiselect("Escolha seus Truques", truques_list)
    else:
        st.write("Esta classe não possui truques.")
        truques_sel = []

with col_m:
    magias_list = db['classes'][classe_sel]['magias_n1']
    if magias_list:
        magias_sel = st.multiselect("Escolha Magias Nível 1", magias_list)
    else:
        st.write("Esta classe não possui magias de Nível 1.")
        magias_sel = []

with col_f:
    talento_sel = st.selectbox("Talento (Se disponível)", ["Nenhum"] + db['talentos'])

st.divider()

# --- 4. GERAÇÃO E VALIDAÇÃO ---
if st.button("🔥 AUTORIZAR E GERAR FICHA"):
    st.balloons()
    
    st.header(f"📜 Ficha: {raca_sel} {classe_sel}")
    st.subheader(f"Subclasse: {sub_sel}")
    
    res_col1, res_col2 = st.columns(2)
    
    with res_col1:
        st.write("### 📊 Atributos Finais")
        for k, v in finais.items():
            mod_str = f"+{v['mod']}" if v['mod'] >= 0 else str(v['mod'])
            st.write(f"**{k}:** {v['total']} (Modificador: `{mod_str}`)")
            
    with res_col2:
        st.write("### ✨ Habilidades e Magias")
        st.write("**Habilidades de Raça:**")
        for hab in db['racas'][raca_sel]['habilidades']:
            st.write(f"- {hab}")
        
        if talento_sel != "Nenhum":
            st.write(f"**Talento Selecionado:** {talento_sel}")
            
        if truques_sel:
            st.write(f"**Truques:** {', '.join(truques_sel)}")
            
        if magias_sel:
            st.write(f"**Magias Nível 1:** {', '.join(magias_sel)}")

    # Botão para download do texto da ficha
    txt_ficha = f"FICHA DE D&D 5E\n\nRaça: {raca_sel}\nClasse: {classe_sel}\nSubclasse: {sub_sel}\n\nATRIBUTOS:\n"
    for k, v in finais.items():
        txt_ficha += f"{k}: {v['total']} ({v['mod']})\n"
    
    st.download_button("📥 Baixar Ficha em TXT", txt_ficha, file_name="ficha_dnd.txt")

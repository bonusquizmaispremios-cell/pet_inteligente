import streamlit as st
from groq import Groq
from datetime import datetime
import json

st.set_page_config(page_title="Pet Inteligente", page_icon="🐾", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    .stApp { background-color:#F0FDF4; font-family:'Inter',sans-serif; }
    [data-testid="stSidebar"] { display:none; }
    .stTextInput>div>div>input, .stTextArea>div>textarea,
    .stSelectbox>div>div>div, .stNumberInput>div>div>input {
        background-color:#FFFFFF !important; color:#1A1A2E !important;
        border:1px solid #CED4DA !important; font-family:'Inter',sans-serif !important;
    }
    .stButton>button {
        width:100%; border-radius:10px; height:3.2em;
        background:linear-gradient(135deg,#065F46,#059669) !important; color:white !important;
        font-weight:600; border:none; box-shadow:2px 2px 8px rgba(0,0,0,0.1);
        font-family:'Inter',sans-serif !important; transition:all 0.2s ease;
    }
    .stButton>button:hover { background:linear-gradient(135deg,#059669,#065F46) !important; transform:translateY(-1px); }
    .stApp .stButton>button, .stApp .stButton>button p,
    .stApp .stButton>button span, .stApp .stButton>button div { color:white !important; }
    .stApp h1, .stApp h2, .stApp h3 { color:#065F46 !important; font-family:'Inter',sans-serif !important; font-weight:700 !important; }
    .card { background:linear-gradient(135deg,#F0FDF4,#DCFCE7); padding:20px; border-radius:14px; border:1px solid #86EFAC; margin-bottom:14px; white-space:normal; word-wrap:break-word; }
    .stApp .card, .stApp .card p, .stApp .card span, .stApp .card div, .stApp .card strong { color:#065F46 !important; }
    .card-red { background:linear-gradient(135deg,#FFF5F5,#FEE2E2); padding:20px; border-radius:14px; border:1px solid #FECACA; margin-bottom:14px; }
    .stApp .card-red, .stApp .card-red p, .stApp .card-red div { color:#7F1D1D !important; }
    .card-yellow { background:linear-gradient(135deg,#FFFBEB,#FEF3C7); padding:18px; border-radius:12px; border:1px solid #FCD34D; margin-bottom:12px; }
    .stApp .card-yellow, .stApp .card-yellow p, .stApp .card-yellow div { color:#78350F !important; }
    .card-blue { background:linear-gradient(135deg,#EFF6FF,#DBEAFE); padding:20px; border-radius:14px; border:1px solid #93C5FD; margin-bottom:14px; }
    .stApp .card-blue, .stApp .card-blue p, .stApp .card-blue div { color:#1E3A8A !important; }
    .badge { background:#065F46; color:white !important; padding:4px 12px; border-radius:20px; font-size:0.78em; font-weight:600; display:inline-block; margin:2px; }
    .badge-red { background:#DC2626; color:white !important; padding:4px 12px; border-radius:20px; font-size:0.78em; font-weight:600; display:inline-block; margin:2px; }
    .badge-yellow { background:#B45309; color:white !important; padding:4px 12px; border-radius:20px; font-size:0.78em; font-weight:600; display:inline-block; margin:2px; }
    .divider { border:none; height:1px; background:linear-gradient(to right,transparent,#86EFAC,transparent); margin:18px 0; }
    .hist-item { background:#FFFFFF; border-radius:10px; padding:12px 16px; margin-bottom:8px; border-left:4px solid #86EFAC; }
    .stApp .hist-item, .stApp .hist-item p, .stApp .hist-item div { color:#065F46 !important; }
    .stat-box { background:#FFFFFF; border-radius:12px; padding:16px; text-align:center; border:1px solid #86EFAC; }
    .stApp .stat-box div, .stApp .stat-box span { color:#065F46 !important; }
    .pet-card { background:#FFFFFF; border-radius:14px; padding:16px; border:2px solid #86EFAC; margin-bottom:12px; }
    .stApp .pet-card, .stApp .pet-card p, .stApp .pet-card div, .stApp .pet-card span { color:#065F46 !important; }
    .chat-user { background:#FFFFFF; border:1px solid #86EFAC; border-radius:12px 12px 4px 12px; padding:12px 16px; margin:8px 0; }
    .stApp .chat-user, .stApp .chat-user p, .stApp .chat-user div { color:#065F46 !important; }
    .chat-ia { background:#DCFCE7; border:1px solid #86EFAC; border-radius:4px 12px 12px 12px; padding:12px 16px; margin:8px 0; }
    .stApp .chat-ia, .stApp .chat-ia p, .stApp .chat-ia div { color:#065F46 !important; }
    .urgente { background:#FEE2E2; border:2px solid #EF4444; border-radius:12px; padding:16px; margin-bottom:12px; }
    .stApp .urgente, .stApp .urgente p, .stApp .urgente div { color:#7F1D1D !important; }
    </style>
""", unsafe_allow_html=True)

SYSTEM_BASE = """Você é o Pet Inteligente — assistente pessoal especializado em cuidados com animais de estimação.
REGRA FUNDAMENTAL: SEMPRE adapte suas respostas à espécie do animal. Um cachorro, gato, coelho, ave e peixe têm necessidades COMPLETAMENTE diferentes.
Antes de responder qualquer pergunta, considere a espécie, idade, peso e características do animal.
NUNCA substitua avaliação veterinária presencial. Para situações de saúde, sempre recomende consulta profissional.
Português do Brasil. Seja prático, empático e claro."""

ESPECIES = ["🐶 Cachorro","🐱 Gato","🐰 Coelho","🐹 Hamster","🐦 Ave doméstica",
            "🐢 Tartaruga","🦎 Réptil","🐠 Peixe","🐴 Cavalo","🐔 Animal de criação","🐾 Outro"]

def ia(prompt, sistema_extra="", historico_msgs=None):
    try:
        client = Groq(api_key=st.session_state.api_key)
        msgs = [{"role":"system","content": SYSTEM_BASE + "\n" + sistema_extra}]
        if historico_msgs:
            msgs.extend(historico_msgs[-10:])
        msgs.append({"role":"user","content": prompt})
        r = client.chat.completions.create(model="openai/gpt-oss-120b", messages=msgs, max_tokens=2048)
        return r.choices[0].message.content
    except Exception as e:
        return f"Erro na IA: {e}"

def perfil_pet_txt():
    pets = st.session_state.get('pets', [])
    idx = st.session_state.get('pet_ativo', 0)
    if not pets: return "Nenhum pet cadastrado."
    pet = pets[idx] if idx < len(pets) else pets[0]
    return (f"Pet: {pet.get('nome','?')} | Espécie: {pet.get('especie','?')} | "
            f"Raça: {pet.get('raca','?')} | Idade: {pet.get('idade','?')} | "
            f"Peso: {pet.get('peso','?')}kg | Sexo: {pet.get('sexo','?')} | "
            f"Castrado: {pet.get('castrado','?')} | Saúde: {pet.get('saude','?')} | "
            f"Alimentação: {pet.get('alimentacao','?')}")

def get_pet_ativo():
    pets = st.session_state.get('pets', [])
    idx = st.session_state.get('pet_ativo', 0)
    if not pets: return None
    return pets[idx] if idx < len(pets) else pets[0]

def carregar_json_sessao(dados):
    # Chaves que NÃO devem ser restauradas
    bloqueadas = {'api_key','etapa','pet_cadastrado_ok','pet_cadastrado_nome'}
    # Prefixos de widgets dinâmicos (chaves geradas com f-string)
    prefixos_widget = (
        'cad_','btn_','sel_','ul_','dl_','_sub','_sm','_tab','_bsc',
        'ativo_','rem_','sel_pet_','ev_','prof_','hig_','prev_',
        'vac_','sint_','comp_','trad_','subs_','amb_','viag_','chat_',
        'duvida_','emerg_','peso_','data_','obs_','tipo_','vet_','desc_',
        'local_','prox_','alim','sit_emerg_','_sm_','_pr',
    )
    # Também bloqueia qualquer chave que termine com número (widget dinâmico)
    import re as _re
    for k, v in dados.items():
        if k in bloqueadas: continue
        if any(k.startswith(p) for p in prefixos_widget): continue
        if _re.match(r'.+_\d+$', k): continue  # ex: ativo_0, rem_1, sel_pet_2
        st.session_state[k] = v

# ── DEFAULTS ──
defaults = {
    "etapa": "Login", "usuario": "", "api_key": "",
    "pets": [], "pet_ativo": 0,
    "hist_saude": [], "hist_vacinas": [], "hist_prevencao": [],
    "hist_peso": [], "hist_higiene": [], "hist_agenda": [],
    "hist_chat": [], "diario_pet": [], "profissionais": [],
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── LOGIN ──
if st.session_state.etapa == "Login":
    st.markdown("# 🐾 Pet Inteligente")
    st.markdown("*Seu assistente pessoal para cuidar de qualquer animal de estimação.*")
    st.markdown("<div class='card'><b>🔒 ACESSO RESTRITO A CLIENTES DO QUIZ COM PRÊMIOS</b><br>🔗 <a href='https://quizcompremios.com.br' target='_blank' style='color:#4F46E5;font-weight:700;text-decoration:underline;'>quizcompremios.com.br</a></div>", unsafe_allow_html=True)
    st.info("💻 **Dica:** Pela complexidade dos agentes, no computador a experiência é mais agradável.")
    with st.container():
        nome  = st.text_input("Seu Nome:", key="nome_login")
        chave = st.text_input("🔑 Sua Chave API da Groq:", type="password", key="chave_login")
        arq_j = st.file_uploader("📂 Carregar dados salvos (.json):", type=["json"], key="upload_login")
        dados_login = json.load(arq_j) if arq_j else None
        if st.button("✨ ENTRAR", key="btn_entrar_login"):
            if len(nome.strip()) < 2:
                st.warning("Digite um nome com pelo menos 2 caracteres.")
            elif chave.strip():
                st.session_state.usuario = nome.strip()
                st.session_state.api_key = chave
                if dados_login: carregar_json_sessao(dados_login)
                st.session_state.etapa = "App"
                st.rerun()
            else:
                st.warning("Preencha nome e chave API.")

elif st.session_state.etapa == "App":

    # TABS
    
    (_tab_home, _tab_pets, _tab_saude, _tab_alimentacao, _tab_comportamento, _tab_emergencia, _tab_agenda, _tab_peso, _tab_chat, _tab_higiene, _tab_Mais) = st.tabs(['🏠 Home', '🐾 Meus Pets', '🩺 Saúde', '🍖 Alimentação', '🧠 Comportamento', '🚨 Emergência', '📅 Agenda', '⚖️ Peso', '🤖 Converse com IA', '🧼 Higiene', '➕ Mais'])

    # ── BARRA SALVAR — visível em todas as abas ──
    with st.expander("💾 Salvar / Carregar meus dados", expanded=False):
        _bsc1, _bsc2 = st.columns(2)
        with _bsc1:
            _dsv = {k: st.session_state.get(k) for k in list(st.session_state.keys()) if not k.startswith('_') and k != 'api_key'}
            st.download_button("💾 Baixar meus dados (.json)",
                data=json.dumps(_dsv, ensure_ascii=False, indent=2, default=str),
                file_name=f"pet_inteligente_{st.session_state.get('usuario','user')}.json",
                mime="application/json", key="dl_barra_sv_pet")
        with _bsc2:
            _fupsv = st.file_uploader("📂 Carregar dados salvos:", type=["json"], key="ul_barra_sv_pet", label_visibility="collapsed")
            if _fupsv:
                try:
                    _dados_car = json.loads(_fupsv.read().decode())
                    carregar_json_sessao(_dados_car)
                    st.success("✅ Dados restaurados!"); st.rerun()
                except: st.error("Arquivo inválido.")


    with _tab_home:
        st.title(f"🐾 Olá, {st.session_state.usuario}!")
        st.markdown("*Seu assistente pessoal para cuidar de qualquer animal de estimação.*")
        st.markdown("<hr class='divider'>", unsafe_allow_html=True)

        pets = st.session_state.get('pets', [])
        if pets:
            st.markdown(f"### Você tem **{len(pets)}** pet(s) cadastrado(s):")
            for i, pet in enumerate(pets):
                col_p1, col_p2 = st.columns([4,1])
                with col_p1:
                    st.markdown(f"<div class='pet-card'><b>{pet.get('especie','🐾')} {pet.get('nome','?')}</b><br><small>{pet.get('raca','')} | {pet.get('idade','')} | {pet.get('peso','')}kg</small></div>", unsafe_allow_html=True)
                with col_p2:
                    if st.button("Selecionar", key=f"sel_pet_{i}"):
                        st.session_state.pet_ativo = i
                        st.success(f"Pet ativo: {pet.get('nome','?')}")
                        st.rerun()
            pet_atual = get_pet_ativo()
            if pet_atual:
                st.markdown(f"<div class='card'>🎯 <b>Pet ativo:</b> {pet_atual.get('especie','')} {pet_atual.get('nome','?')}</div>", unsafe_allow_html=True)
        else:
            st.info("Você ainda não cadastrou nenhum pet. Vá para a aba **🐾 Meus Pets** para começar!")

        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        st.markdown("### 🗺️ O que cada aba faz")
        guia = [
            ("🐾","Meus Pets","Cadastre e gerencie todos os seus animais"),
            ("🩺","Saúde","Diário de saúde, análise de sintomas e histórico"),
            ("💉","Vacinas","Calendário, registros e lembretes de vacinação"),
            ("🪱","Prevenção","Vermifugação, pulgas, carrapatos e parasitas"),
            ("🍖","Alimentação","Nutrição, alimentos seguros e rotina alimentar"),
            ("🐾","Comportamento","Interpretação e orientação comportamental"),
            ("🏃","Atividades","Exercícios e enriquecimento por espécie"),
            ("🧼","Higiene","Banho, unhas, pelos e cuidados ambientais"),
            ("⚖️","Peso","Controle de peso e desenvolvimento"),
            ("📅","Agenda","Calendário de consultas, vacinas e cuidados"),
            ("🚨","Emergência","Primeiros cuidados em situações urgentes"),
            ("🏡","Ambiente Seguro","Checklist de segurança para seu pet"),
            ("🧳","Viagens","Planejamento de viagens com animais"),
            ("🤖","Converse com a IA","Chat personalizado com perfil do seu pet"),
            ("🏥","Profissionais","Cadastro de vets, pet shops e especialistas"),
        ]
        for ic, nm, desc in guia:
            st.markdown(f"**{ic} {nm}** — {desc}")

        # ══════════════════════════════════════════════
        # 🐾 MEUS PETS
        # ══════════════════════════════════════════════

    with _tab_pets:
        st.header("🐾 Meus Pets")
        pets = st.session_state.get('pets', [])

        _sub_lista, _sub_cadastro = st.tabs(["📋 Meus Animais", "➕ Cadastrar Novo"])

        with _sub_lista:
            if not pets:
                st.info("Nenhum pet cadastrado ainda. Use a aba **➕ Cadastrar Novo** para adicionar.")
            else:
                for i, pet in enumerate(pets):
                    with st.expander(f"{pet.get('especie','🐾')} {pet.get('nome','?')} — {pet.get('raca','')} | {pet.get('idade','')}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**Espécie:** {pet.get('especie','?')}")
                            st.markdown(f"**Raça/Variedade:** {pet.get('raca','?')}")
                            st.markdown(f"**Idade:** {pet.get('idade','?')}")
                            st.markdown(f"**Peso:** {pet.get('peso','?')} kg")
                            st.markdown(f"**Sexo:** {pet.get('sexo','?')}")
                        with col2:
                            st.markdown(f"**Castrado:** {pet.get('castrado','?')}")
                            st.markdown(f"**Saúde:** {pet.get('saude','Não informado')}")
                            st.markdown(f"**Alergias:** {pet.get('alergias','Nenhuma')}")
                            st.markdown(f"**Alimentação:** {pet.get('alimentacao','?')}")
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button(f"✅ Tornar ativo", key=f"ativo_{i}"):
                                st.session_state.pet_ativo = i
                                st.success(f"{pet.get('nome')} é agora o pet ativo!"); st.rerun()
                        with col_b:
                            if st.button(f"🗑️ Remover", key=f"rem_{i}"):
                                st.session_state.pets.pop(i); st.rerun()

        with _sub_cadastro:
            # Tela de sucesso após cadastro
            if st.session_state.get('pet_cadastrado_ok'):
                pet_nome_ok = st.session_state.get('pet_cadastrado_nome','')
                st.markdown(f"""
                <div style='text-align:center;padding:40px 20px;'>
                    <div style='font-size:4em;'>🐾</div>
                    <h2 style='color:#065F46;'>Cadastro realizado!</h2>
                    <p style='font-size:1.1em;color:#065F46;'><b>{pet_nome_ok}</b> foi cadastrado com sucesso.</p>
                    <p style='color:#6B7280;'>Agora você pode usar todas as funcionalidades personalizadas para o seu pet.</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button("➕ Cadastrar outro pet", key="btn_cad_outro", use_container_width=True):
                    st.session_state['pet_cadastrado_ok'] = False
                    st.rerun()
            else:
                st.markdown("### ➕ Cadastrar Novo Animal")
                st.markdown("*Preencha os dados do seu pet. Quanto mais informações, mais personalizada será a IA.*")

                # CSS para labels importantes
                st.markdown("""
                <style>
                .label-imp { color:#DC2626; font-size:0.75em; font-weight:600; margin-top:-8px; margin-bottom:4px; }
                .label-aviso { color:#B45309; font-size:0.75em; font-weight:600; margin-top:-8px; margin-bottom:4px; }
                </style>
                """, unsafe_allow_html=True)

                c1, c2 = st.columns(2)
                with c1:
                    nome_pet = st.text_input("🏷️ Nome do pet:", key="cad_nome", placeholder="Ex: Thor, Mimi, Lola...")
                    especie_pet = st.selectbox("🐾 Espécie:", ESPECIES, key="cad_especie")
                    raca_pet = st.text_input("🔬 Raça/Variedade:", key="cad_raca", placeholder="Ex: Golden Retriever, SRD, Anão Holandês...")
                    sexo_pet = st.selectbox("⚥ Sexo:", ["Macho","Fêmea","Não identificado"], key="cad_sexo")
                    idade_pet = st.text_input("📅 Idade:", key="cad_idade", placeholder="Ex: 2 anos, 6 meses, filhote...")
                with c2:
                    peso_pet = st.text_input("⚖️ Peso (kg):", key="cad_peso", placeholder="Ex: 5.2")
                    castrado_pet = st.selectbox("✂️ Castrado(a):", ["Sim","Não","Não aplicável","Não sei"], key="cad_castrado")
                    cor_pet = st.text_input("🎨 Cor/Pelagem:", key="cad_cor", placeholder="Ex: Caramelo, preto e branco...")
                    identificacao_pet = st.text_input("🔖 Identificação:", key="cad_id", placeholder="Ex: Microchip, coleira, tatuagem...")

                st.markdown("<div class='label-imp'>⚠️ Campo importante — preencha com atenção:</div>", unsafe_allow_html=True)
                alergias_pet = st.text_area("⚠️ Alergias:", key="cad_alergias", height=60, placeholder="Ex: Alergia a frango, sem alergias conhecidas... (impacta todas as recomendações da IA)")

                st.markdown("<div class='label-imp'>⚠️ Campo importante — preencha com atenção:</div>", unsafe_allow_html=True)
                saude_pet = st.text_area("🩺 Condições de saúde conhecidas:", key="cad_saude", height=80, placeholder="Ex: Displasia quadril, diabetes, saudável... (a IA adapta orientações conforme este campo)")

                st.markdown("<div class='label-imp'>⚠️ Campo importante — preencha com atenção:</div>", unsafe_allow_html=True)
                medicamentos_pet = st.text_input("💊 Medicamentos prescritos:", key="cad_meds", placeholder="Ex: Nenhum, Thyrozol 5mg/dia... (essencial para recomendações seguras)")

                st.markdown("<div class='label-aviso'>💡 Recomendado — ajuda a IA a personalizar melhor:</div>", unsafe_allow_html=True)
                alimentacao_pet = st.text_area("🍖 Alimentação atual:", key="cad_alim", height=60, placeholder="Ex: Ração premium adulto, ração + vegetais frescos...")

                st.markdown("<div class='label-aviso'>💡 Recomendado — ajuda a IA a personalizar melhor:</div>", unsafe_allow_html=True)
                comportamento_pet = st.text_area("🧠 Características comportamentais:", key="cad_comp", height=60, placeholder="Ex: Dócil, ansioso, sociável com outros animais...")

                obs_pet = st.text_area("📝 Observações adicionais:", key="cad_obs", height=60, placeholder="Outras informações importantes...")

                if st.button("✅ CADASTRAR PET", key="btn_cadastrar_pet", use_container_width=True):
                    if nome_pet.strip():
                        with st.spinner(f"Cadastrando {nome_pet.strip()}..."):
                            import time as _t
                            _t.sleep(0.8)
                            novo_pet = {
                                "nome": nome_pet.strip(), "especie": especie_pet,
                                "raca": raca_pet, "sexo": sexo_pet, "idade": idade_pet,
                                "peso": peso_pet, "castrado": castrado_pet, "cor": cor_pet,
                                "identificacao": identificacao_pet, "saude": saude_pet,
                                "alergias": alergias_pet, "alimentacao": alimentacao_pet,
                                "medicamentos": medicamentos_pet, "comportamento": comportamento_pet,
                                "obs": obs_pet, "cadastrado_em": datetime.now().strftime("%d/%m/%Y")
                            }
                            if 'pets' not in st.session_state: st.session_state.pets = []
                            st.session_state.pets.append(novo_pet)
                            st.session_state.pet_ativo = len(st.session_state.pets) - 1
                            st.session_state['pet_cadastrado_ok'] = True
                            st.session_state['pet_cadastrado_nome'] = nome_pet.strip()
                        st.rerun()
                    else:
                        st.warning("Digite o nome do pet.")

        # ══════════════════════════════════════════════
        # 🩺 SAÚDE
        # ══════════════════════════════════════════════

    with _tab_saude:
        st.header("🩺 Central de Saúde Animal")
        pet = get_pet_ativo()
        if not pet:
            st.warning("Cadastre e selecione um pet primeiro na aba 🐾 Meus Pets.")
        else:
            st.markdown(f"<div class='badge'>{pet.get('especie','')} {pet.get('nome','?')}</div>", unsafe_allow_html=True)
            st.markdown("")

            _s1, _s2, _s3 = st.tabs(["🔍 Analisar Sintomas","📓 Diário de Saúde","📋 Histórico"])

            with _s1:
                st.markdown("### 🔍 Analisador de Sintomas")
                st.markdown("Descreva o que está observando — a IA considera a espécie do seu pet antes de responder.")
                sint = st.text_area("O que você está observando?", height=120, key="sint_input",
                    placeholder=f"Ex: Meu {pet.get('nome','pet')} parou de comer hoje, está letárgico e com a barriga inchada...")
                if st.button("🔍 ANALISAR SINTOMAS", key="btn_sint", use_container_width=True):
                    if sint.strip():
                        with st.spinner("Analisando com base na espécie do seu pet..."):
                            resp = ia(f"SINTOMAS RELATADOS: {sint}",
                                     f"PERFIL DO PET: {perfil_pet_txt()}\n\nAnalise os sintomas considerando ESPECIFICAMENTE a espécie {pet.get('especie','')}. Apresente: 1) Possíveis causas 2) Perguntas importantes a observar 3) Sinais de alerta 4) Classificação: 🟢 Acompanhar / 🟡 Avaliação recomendada / 🔴 Urgente. Sempre recomende veterinário quando necessário.")
                        st.markdown(f"<div class='card'>{resp}</div>", unsafe_allow_html=True)
                        st.session_state.hist_saude.append({"data": datetime.now().strftime("%d/%m %H:%M"), "pet": pet.get('nome'), "tipo": "Sintomas", "desc": sint[:100], "resp": resp})
                    else:
                        st.warning("Descreva os sintomas.")

            with _s2:
                st.markdown("### 📓 Registrar no Diário de Saúde")
                c1, c2 = st.columns(2)
                with c1:
                    tipo_reg = st.selectbox("Tipo de registro:", ["Consulta veterinária","Exame","Diagnóstico","Medicamento","Peso","Sintoma observado","Cirurgia","Outro"], key="tipo_saude_reg")
                    data_reg = st.text_input("Data:", value=datetime.now().strftime("%d/%m/%Y"), key="data_saude_reg")
                with c2:
                    veterinario_reg = st.text_input("Veterinário/Clínica (opcional):", key="vet_saude_reg")
                desc_reg = st.text_area("Descrição:", height=100, key="desc_saude_reg", placeholder="Descreva o registro...")
                if st.button("💾 SALVAR REGISTRO", key="btn_saude_reg", use_container_width=True):
                    if desc_reg.strip():
                        st.session_state.hist_saude.append({"data": data_reg, "pet": pet.get('nome'), "tipo": tipo_reg, "desc": desc_reg, "vet": veterinario_reg, "resp": ""})
                        st.success("✅ Registro salvo!"); st.rerun()
                    else:
                        st.warning("Preencha a descrição.")

            with _s3:
                st.markdown("### 📋 Histórico de Saúde")
                registros = [r for r in st.session_state.hist_saude if r.get('pet') == pet.get('nome')]
                if registros:
                    for r in reversed(registros[-15:]):
                        with st.expander(f"📋 {r.get('data','')} — {r.get('tipo','')}"):
                            st.markdown(f"**Descrição:** {r.get('desc','')}")
                            if r.get('vet'): st.markdown(f"**Veterinário:** {r.get('vet','')}")
                            if r.get('resp'): st.markdown(f"**Análise da IA:** {r.get('resp','')}")
                else:
                    st.info("Nenhum registro de saúde ainda.")

        # ══════════════════════════════════════════════
        # 💉 VACINAS
        # ══════════════════════════════════════════════

    with _tab_alimentacao:
        st.header("🍖 Alimentação Inteligente")
        pet = get_pet_ativo()
        if not pet:
            st.warning("Cadastre e selecione um pet primeiro.")
        else:
            st.markdown(f"<div class='badge'>{pet.get('especie','')} {pet.get('nome','?')}</div>", unsafe_allow_html=True)
            st.markdown("")
            _a1, _a2, _a3 = st.tabs(["🥗 Orientação Nutricional","🔍 Posso dar esse alimento?","☠️ Alimentos Perigosos"])

            with _a1:
                duvida_alim = st.text_area("Sua dúvida sobre alimentação:", height=100, key="duvida_alim",
                    placeholder="Ex: Quantas vezes devo alimentar por dia? Posso misturar ração com comida natural?")
                if st.button("🥗 CONSULTAR IA", key="btn_ia_alim", use_container_width=True):
                    if duvida_alim.strip():
                        with st.spinner("Consultando..."):
                            resp = ia(duvida_alim, f"PERFIL DO PET: {perfil_pet_txt()}\n\nOriente sobre alimentação ESPECIFICAMENTE para {pet.get('especie','')}. A dieta varia muito entre espécies — adapte completamente.")
                            if resp: st.session_state['res_a1_petint1'] = str(resp)
                        st.markdown(f"<div class='card'>{resp}</div>", unsafe_allow_html=True)
                    else:
                        st.warning("Digite sua dúvida.")

            with _a2:
                st.markdown("### 🔍 Posso oferecer esse alimento?")
                st.markdown(f"*A IA verifica se o alimento é seguro para **{pet.get('especie','')}***")
                alimento = st.text_input("Digite o alimento:", key="alimento_check", placeholder="Ex: Cenoura, Chocolate, Abacate, Frango cru...")
                if st.button("🔍 VERIFICAR", key="btn_check_alim", use_container_width=True):
                    if alimento.strip():
                        with st.spinner("Verificando..."):
                            resp = ia(f"O alimento '{alimento}' é seguro para meu animal?",
                                     f"PERFIL DO PET: {perfil_pet_txt()}\n\nAvalie se '{alimento}' é SEGURO para {pet.get('especie','')}. Considere: 1) É seguro? 2) Em que quantidade? 3) Como preparar? 4) Riscos específicos para esta espécie. Seja muito claro sobre perigos.")
                        cor_card = 'card-red' if any(p in resp.lower() for p in ['perigoso','tóxico','evitar','não deve','nunca']) else 'card'
                        st.markdown(f"<div class='{cor_card}'>{resp}</div>", unsafe_allow_html=True)
                    else:
                        st.warning("Digite o alimento.")

            with _a3:
                st.markdown("### ☠️ Banco de Alimentos e Substâncias Perigosas")
                subs = st.text_input("Buscar substância:", key="subs_perig", placeholder="Ex: Chocolate, Uva, Cebola, Xilitol...")
                if st.button("☠️ VERIFICAR PERIGO", key="btn_perigo", use_container_width=True):
                    if subs.strip():
                        with st.spinner("Verificando..."):
                            resp = ia(f"A substância '{subs}' é perigosa para animais?",
                                     f"PERFIL DO PET: {perfil_pet_txt()}\n\nExplique os riscos de '{subs}' para {pet.get('especie','')}. Se for perigoso: sintomas de intoxicação, o que fazer, quando ir ao veterinário. Se for seguro: confirme e dê orientações de uso.")
                        st.markdown(f"<div class='card-red'>{resp}</div>", unsafe_allow_html=True)
                    else:
                        st.warning("Digite a substância.")

        # ══════════════════════════════════════════════
        # 🐾 COMPORTAMENTO
        # ══════════════════════════════════════════════

    with _tab_comportamento:
        st.header("🐾 Comportamento Animal")
        pet = get_pet_ativo()
        if not pet:
            st.warning("Cadastre e selecione um pet primeiro.")
        else:
            st.markdown(f"<div class='badge'>{pet.get('especie','')} {pet.get('nome','?')}</div>", unsafe_allow_html=True)
            st.markdown("")
            _c1, _c2 = st.tabs(["🧠 Analisar Comportamento","🔍 Tradutor de Comportamento"])

            with _c1:
                comp_desc = st.text_area("Descreva o comportamento:", height=120, key="comp_desc",
                    placeholder="Ex: Está se escondendo mais que o normal, parou de brincar, está roendo objetos...")
                c1, c2 = st.columns(2)
                with c1: comp_duracao = st.text_input("Há quanto tempo?", key="comp_dur", placeholder="Ex: 2 dias, 1 semana...")
                with c2: comp_gatilho = st.text_input("Alguma mudança recente?", key="comp_gat", placeholder="Ex: Mudança, novo pet, obra...")
                if st.button("🧠 ANALISAR COMPORTAMENTO", key="btn_comp", use_container_width=True):
                    if comp_desc.strip():
                        with st.spinner("Analisando..."):
                            resp = ia(f"Comportamento observado: {comp_desc}. Duração: {comp_duracao}. Mudanças recentes: {comp_gatilho}",
                                     f"PERFIL DO PET: {perfil_pet_txt()}\n\nInterprete o comportamento considerando ESPECIFICAMENTE {pet.get('especie','')}. Apresente: possíveis causas, se é normal para a espécie, o que fazer, quando procurar especialista.")
                        st.markdown(f"<div class='card'>{resp}</div>", unsafe_allow_html=True)
                    else:
                        st.warning("Descreva o comportamento.")

            with _c2:
                st.markdown("### 🔍 Tradutor de Comportamento")
                st.markdown("Pergunte sobre qualquer comportamento específico:")
                trad_pergunta = st.text_area("Sua pergunta:", height=100, key="trad_perg",
                    placeholder="Ex: Por que meu gato inclina a cabeça? Por que meu coelho bate com as patas?")
                if st.button("🔍 TRADUZIR", key="btn_trad", use_container_width=True):
                    if trad_pergunta.strip():
                        with st.spinner("Traduzindo..."):
                            resp = ia(trad_pergunta, f"PERFIL DO PET: {perfil_pet_txt()}\n\nExplique este comportamento de {pet.get('especie','')} de forma clara e detalhada. Considere causas naturais, instintivas e possíveis problemas.")
                            if resp: st.session_state['res_c2_petint2'] = str(resp)
                        st.markdown(f"<div class='card'>{resp}</div>", unsafe_allow_html=True)
                    else:
                        st.warning("Digite sua pergunta.")

        # ══════════════════════════════════════════════
        # 🏃 ATIVIDADES
        # ══════════════════════════════════════════════

    with _tab_emergencia:
        st.markdown("<div class='urgente'><h2>🚨 MEU ANIMAL ESTÁ EM PERIGO?</h2><p>Use esta área para situações urgentes. A IA fornece orientação inicial — mas em casos graves, procure atendimento veterinário IMEDIATAMENTE.</p></div>", unsafe_allow_html=True)

        pet = get_pet_ativo()
        especie_emerg = pet.get('especie', ESPECIES[0]) if pet else st.selectbox("Espécie:", ESPECIES, key="esp_emerg")

        emerg_desc = st.text_area("🚨 Descreva a emergência:", height=120, key="emerg_desc",
            placeholder="Ex: Meu pet ingeriu chocolate, está convulsionando, caiu de altura, está engasgado...")

        col_e1, col_e2 = st.columns(2)
        with col_e1:
            emerg_sintomas = st.text_input("Sintomas visíveis:", key="emerg_sint", placeholder="Ex: Vômito, tremores, sangramento...")
        with col_e2:
            emerg_tempo = st.text_input("Há quanto tempo?", key="emerg_tempo", placeholder="Ex: 30 minutos, acabou de acontecer...")

        if st.button("🚨 ORIENTAÇÃO DE EMERGÊNCIA", key="btn_emerg", use_container_width=True):
            if emerg_desc.strip():
                with st.spinner("Avaliando urgência..."):
                    perf = perfil_pet_txt() if pet else f"Espécie: {especie_emerg}"
                    resp = ia(f"EMERGÊNCIA: {emerg_desc}. Sintomas: {emerg_sintomas}. Tempo: {emerg_tempo}",
                             f"PERFIL DO PET: {perf}\n\nResponda com urgência. Avalie: 1) Nível de urgência (CRÍTICO/GRAVE/MODERADO) 2) Primeiros cuidados imediatos SEGUROS para esta espécie 3) Sinais que indicam necessidade de atendimento IMEDIATO 4) O que NÃO fazer. SEMPRE recomende atendimento veterinário em casos graves.")
                if any(p in resp.lower() for p in ['crítico','grave','imediato','urgente','veterinário agora']):
                    st.markdown(f"<div class='urgente'>{resp}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='card'>{resp}</div>", unsafe_allow_html=True)
            else:
                st.warning("Descreva a situação de emergência.")

        st.markdown("<hr class='divider'>", unsafe_allow_html=True)
        st.markdown("### ⚡ Situações comuns — clique para orientação rápida")
        situacoes = ["Intoxicação/envenenamento","Engasgo","Sangramento","Convulsão","Queda de altura","Picada de inseto","Dificuldade respiratória","Trauma/atropelamento"]
        cols = st.columns(4)
        for i, sit in enumerate(situacoes):
            with cols[i % 4]:
                if st.button(sit, key=f"sit_emerg_{i}", use_container_width=True):
                    with st.spinner(f"Carregando orientação para {sit}..."):
                        perf = perfil_pet_txt() if pet else f"Espécie: {especie_emerg}"
                        resp = ia(f"Como agir em caso de {sit} no meu animal?",
                                 f"PERFIL DO PET: {perf}\n\nOriente sobre {sit} de forma prática e segura para esta espécie. Primeiros cuidados, o que não fazer e quando ir ao veterinário.")
                    st.markdown(f"<div class='card'>{resp}</div>", unsafe_allow_html=True)

        # ══════════════════════════════════════════════
        # 🏡 AMBIENTE SEGURO
        # ══════════════════════════════════════════════

    with _tab_agenda:
        st.header("📅 Agenda Inteligente")
        pet = get_pet_ativo()

        _ag1, _ag2 = st.tabs(["📋 Minha Agenda","➕ Adicionar Evento"])

        with _ag1:
            agenda = st.session_state.get('hist_agenda', [])
            if agenda:
                st.markdown("### 📅 Próximos compromissos")
                for ev in agenda:
                    emoji_ev = {"Vacina":"💉","Consulta":"🏥","Exame":"🧪","Higiene":"🧼","Medicamento":"💊","Higiene":"🧼","Pesagem":"⚖️","Limpeza":"🧹","Aniversário":"🎂"}.get(ev.get('tipo',''),"📅")
                    st.markdown(f"<div class='hist-item'>{emoji_ev} <b>{ev.get('data','?')}</b> — {ev.get('tipo','?')}: {ev.get('desc','?')} <span class='badge'>{ev.get('pet','?')}</span></div>", unsafe_allow_html=True)
            else:
                st.info("Nenhum evento na agenda. Adicione na aba ➕ Adicionar Evento.")

        with _ag2:
            st.markdown("### ➕ Adicionar Evento")
            pets_nomes = [p.get('nome','?') for p in st.session_state.get('pets',[])]
            c1, c2 = st.columns(2)
            with c1:
                ev_pet = st.selectbox("Pet:", pets_nomes if pets_nomes else ["Sem pets"], key="ev_pet")
                ev_tipo = st.selectbox("Tipo:", ["Consulta","Vacina","Exame","Higiene","Medicamento","Pesagem","Limpeza","Aniversário","Outro"], key="ev_tipo")
            with c2:
                ev_data = st.text_input("Data:", key="ev_data", placeholder="Ex: 15/02/2026")
                ev_hora = st.text_input("Hora (opcional):", key="ev_hora", placeholder="Ex: 14:00")
            ev_desc = st.text_input("Descrição:", key="ev_desc", placeholder="Ex: Consulta de rotina com Dra. Ana")
            if st.button("📅 ADICIONAR À AGENDA", key="btn_agenda_add", use_container_width=True):
                if ev_data.strip() and ev_desc.strip():
                    st.session_state.hist_agenda.append({"pet": ev_pet, "tipo": ev_tipo, "data": ev_data, "hora": ev_hora, "desc": ev_desc})
                    st.success("✅ Evento adicionado!"); st.rerun()
                else:
                    st.warning("Preencha data e descrição.")

        # ══════════════════════════════════════════════
        # 🚨 EMERGÊNCIA
        # ══════════════════════════════════════════════

    with _tab_peso:
        st.header("⚖️ Controle de Peso e Desenvolvimento")
        pet = get_pet_ativo()
        if not pet:
            st.warning("Cadastre e selecione um pet primeiro.")
        else:
            st.markdown(f"<div class='badge'>{pet.get('especie','')} {pet.get('nome','?')}</div>", unsafe_allow_html=True)
            st.markdown("")
            c1, c2, c3 = st.columns(3)
            with c1: peso_novo = st.text_input("Peso atual (kg):", key="peso_novo", placeholder="Ex: 5.2")
            with c2: data_peso = st.text_input("Data:", value=datetime.now().strftime("%d/%m/%Y"), key="data_peso")
            with c3: obs_peso = st.text_input("Observação:", key="obs_peso", placeholder="Ex: Pós-castração")
            if st.button("💾 REGISTRAR PESO", key="btn_peso_reg", use_container_width=True):
                if peso_novo.strip():
                    st.session_state.hist_peso.append({"pet": pet.get('nome'), "peso": peso_novo, "data": data_peso, "obs": obs_peso})
                    # Atualizar peso no cadastro
                    idx = st.session_state.get('pet_ativo', 0)
                    if idx < len(st.session_state.pets):
                        st.session_state.pets[idx]['peso'] = peso_novo
                    st.success("✅ Peso registrado!"); st.rerun()

            pesos_pet = [p for p in st.session_state.hist_peso if p.get('pet') == pet.get('nome')]
            if pesos_pet:
                st.markdown("### 📊 Evolução de Peso")
                for p in reversed(pesos_pet[-10:]):
                    st.markdown(f"<div class='hist-item'>📅 {p.get('data','?')} — <b>{p.get('peso','?')} kg</b> {' — '+p.get('obs','') if p.get('obs') else ''}</div>", unsafe_allow_html=True)

                st.markdown("<hr class='divider'>", unsafe_allow_html=True)
                duvida_peso = st.text_area("Dúvida sobre peso ou desenvolvimento:", height=80, key="duvida_peso",
                    placeholder="Ex: Meu pet está no peso ideal? Está crescendo adequadamente?")
                if st.button("🤖 CONSULTAR IA", key="btn_ia_peso", use_container_width=True):
                    if duvida_peso.strip():
                        hist_str = " | ".join(f"{p['data']}: {p['peso']}kg" for p in pesos_pet[-5:])
                        with st.spinner("Analisando..."):
                            resp = ia(f"{duvida_peso}. Histórico de peso: {hist_str}",
                                     f"PERFIL DO PET: {perfil_pet_txt()}\n\nAnalise o desenvolvimento e peso considerando {pet.get('especie','')}. Padrões de peso variam enormemente entre espécies.")
                        st.markdown(f"<div class='card'>{resp}</div>", unsafe_allow_html=True)
                    else:
                        st.warning("Digite sua dúvida.")

        # ══════════════════════════════════════════════
        # 📅 AGENDA
        # ══════════════════════════════════════════════

    with _tab_chat:
        st.header("🤖 Converse com o Pet Inteligente")
        pet = get_pet_ativo()
        if pet:
            st.markdown(f"<div class='badge'>{pet.get('especie','')} {pet.get('nome','?')}</div> A IA conhece o perfil do seu pet!", unsafe_allow_html=True)
        else:
            st.info("Cadastre um pet para respostas mais personalizadas.")
        st.markdown("")

        hist_chat = st.session_state.get('hist_chat', [])
        for msg in hist_chat[-20:]:
            css = "chat-user" if msg['role'] == 'user' else "chat-ia"
            autor = f"👤 {st.session_state.usuario}" if msg['role'] == 'user' else "🤖 Pet Inteligente"
            st.markdown(f"<div class='{css}'><b>{autor}:</b> {msg['content']}</div>", unsafe_allow_html=True)

        msg_input = st.text_input("💬 Sua mensagem:", key="chat_msg_pet", placeholder="Pergunte qualquer coisa sobre seu pet...")
        col_c1, col_c2 = st.columns([4,1])
        with col_c1:
            if st.button("📤 ENVIAR", key="btn_chat_pet", use_container_width=True):
                if msg_input.strip():
                    hist_chat.append({"role":"user","content": msg_input})
                    with st.spinner("Respondendo..."):
                        perf = perfil_pet_txt() if pet else "Nenhum pet cadastrado."
                        resp = ia(msg_input, f"PERFIL DO PET ATIVO: {perf}", historico_msgs=hist_chat[:-1])
                        if resp: st.session_state['res_chat_petint3'] = str(resp)
                    hist_chat.append({"role":"assistant","content": resp})
                    st.session_state.hist_chat = hist_chat
                    st.rerun()
                else:
                    st.warning("Digite uma mensagem.")
        with col_c2:
            if st.button("🗑️ Limpar", key="btn_chat_clear_pet"):
                st.session_state.hist_chat = []; st.rerun()

        # ══════════════════════════════════════════════
        # 🏥 PROFISSIONAIS
        # ══════════════════════════════════════════════

    with _tab_higiene:
        st.header("🧼 Higiene e Cuidados")
        pet = get_pet_ativo()
        if not pet:
            st.warning("Cadastre e selecione um pet primeiro.")
        else:
            st.markdown(f"<div class='badge'>{pet.get('especie','')} {pet.get('nome','?')}</div>", unsafe_allow_html=True)
            st.markdown("")
            _h1, _h2 = st.tabs(["📋 Registrar Cuidado","🤖 Orientação IA"])

            with _h1:
                c1, c2 = st.columns(2)
                with c1:
                    hig_tipo = st.selectbox("Tipo de cuidado:", ["Banho","Escovação","Corte de unhas","Higiene bucal","Limpeza de orelhas","Cuidados com pelos","Limpeza de gaiola/aquário","Higienização do ambiente","Outro"], key="hig_tipo")
                    hig_data = st.text_input("Data:", value=datetime.now().strftime("%d/%m/%Y"), key="hig_data")
                with c2:
                    hig_prox = st.text_input("Próximo cuidado:", key="hig_prox", placeholder="Ex: Em 15 dias, 30/01/2026...")
                    hig_local = st.text_input("Local (pet shop, em casa):", key="hig_local")
                hig_obs = st.text_area("Observações:", height=60, key="hig_obs")
                if st.button("💾 REGISTRAR", key="btn_hig_reg", use_container_width=True):
                    st.session_state.hist_higiene.append({"pet": pet.get('nome'), "tipo": hig_tipo, "data": hig_data, "proxima": hig_prox, "local": hig_local, "obs": hig_obs})
                    st.success("✅ Registrado!"); st.rerun()

                registros_hig = [h for h in st.session_state.hist_higiene if h.get('pet') == pet.get('nome')]
                if registros_hig:
                    st.markdown("### 📋 Últimos registros")
                    for h in reversed(registros_hig[-8:]):
                        st.markdown(f"<div class='hist-item'><b>🧼 {h.get('tipo','?')}</b> — {h.get('data','?')}<br><small>Próximo: {h.get('proxima','?')} | {h.get('local','')}</small></div>", unsafe_allow_html=True)

            with _h2:
                duvida_hig = st.text_area("Sua dúvida sobre higiene:", height=100, key="duvida_hig",
                    placeholder="Ex: Com que frequência devo dar banho? Como limpar os dentes do meu gato?")
                if st.button("🤖 CONSULTAR IA", key="btn_ia_hig", use_container_width=True):
                    if duvida_hig.strip():
                        with st.spinner("Consultando..."):
                            resp = ia(duvida_hig, f"PERFIL DO PET: {perfil_pet_txt()}\n\nOriente sobre higiene ESPECIFICAMENTE para {pet.get('especie','')}. As rotinas de higiene variam muito entre espécies.")
                            if resp: st.session_state['res_h2_petint4'] = str(resp)
                        st.markdown(f"<div class='card'>{resp}</div>", unsafe_allow_html=True)
                    else:
                        st.warning("Digite sua dúvida.")

        # ══════════════════════════════════════════════
        # ⚖️ PESO E DESENVOLVIMENTO
        # ══════════════════════════════════════════════

    with _tab_Mais:
        (_sm_vacinas, _sm_prevencao, _sm_atividades, _sm_ambiente, _sm_viagem, _sm_profissionais) = st.tabs(['💉 Vacinas', '🪱 Prevenção', '🏃 Atividades', '🏡 Ambiente', '🧳 Viagens', '🏥 Profissionais'])

        with _sm_vacinas:
            st.header("💉 Vacinas e Prevenção")
            pet = get_pet_ativo()
            if not pet:
                st.warning("Cadastre e selecione um pet primeiro.")
            else:
                st.markdown(f"<div class='badge'>{pet.get('especie','')} {pet.get('nome','?')}</div>", unsafe_allow_html=True)
                st.markdown("")
                _v1, _v2, _v3 = st.tabs(["📅 Calendário","💉 Registrar Vacina","🤖 Orientação IA"])

                with _v1:
                    st.markdown("### 📅 Calendário de Vacinação")
                    vacinas = [v for v in st.session_state.hist_vacinas if v.get('pet') == pet.get('nome')]
                    if vacinas:
                        for v in reversed(vacinas):
                            st.markdown(f"<div class='hist-item'><b>💉 {v.get('vacina','?')}</b> — {v.get('data','?')}<br><small>Próxima: {v.get('proxima','?')} | Vet: {v.get('vet','?')}</small></div>", unsafe_allow_html=True)
                    else:
                        st.info("Nenhuma vacina registrada ainda.")

                with _v2:
                    st.markdown("### 💉 Registrar Nova Vacina")
                    c1, c2 = st.columns(2)
                    with c1:
                        vac_nome = st.text_input("Nome da vacina:", key="vac_nome", placeholder="Ex: V10, Antirrábica, Gripe felina...")
                        vac_data = st.text_input("Data de aplicação:", value=datetime.now().strftime("%d/%m/%Y"), key="vac_data")
                    with c2:
                        vac_prox = st.text_input("Próxima dose (data):", key="vac_prox", placeholder="Ex: 10/01/2026")
                        vac_vet = st.text_input("Veterinário/Clínica:", key="vac_vet")
                    vac_obs = st.text_input("Observações:", key="vac_obs", placeholder="Ex: Sem reações adversas")
                    if st.button("💾 REGISTRAR VACINA", key="btn_reg_vac", use_container_width=True):
                        if vac_nome.strip():
                            st.session_state.hist_vacinas.append({"pet": pet.get('nome'), "vacina": vac_nome, "data": vac_data, "proxima": vac_prox, "vet": vac_vet, "obs": vac_obs})
                            st.success("✅ Vacina registrada!"); st.rerun()
                        else:
                            st.warning("Informe o nome da vacina.")

                with _v3:
                    st.markdown("### 🤖 Orientação sobre Vacinação")
                    duvida_vac = st.text_area("Sua dúvida sobre vacinação:", height=100, key="duvida_vac",
                        placeholder="Ex: Quais vacinas são necessárias para meu pet? Já está atrasada?")
                    if st.button("🤖 CONSULTAR IA", key="btn_ia_vac", use_container_width=True):
                        if duvida_vac.strip():
                            with st.spinner("Consultando..."):
                                resp = ia(duvida_vac, f"PERFIL DO PET: {perfil_pet_txt()}\n\nOriente sobre vacinação para esta espécie específica. Lembre que protocolos variam conforme espécie, local e estilo de vida. Sempre recomende orientação veterinária.")
                                if resp: st.session_state['res_v3_petint5'] = str(resp)
                            st.markdown(f"<div class='card'>{resp}</div>", unsafe_allow_html=True)
                        else:
                            st.warning("Digite sua dúvida.")

            # ══════════════════════════════════════════════
            # 🪱 PREVENÇÃO
            # ══════════════════════════════════════════════

        with _sm_prevencao:
            st.header("🪱 Parasitas e Controle Preventivo")
            pet = get_pet_ativo()
            if not pet:
                st.warning("Cadastre e selecione um pet primeiro.")
            else:
                st.markdown(f"<div class='badge'>{pet.get('especie','')} {pet.get('nome','?')}</div>", unsafe_allow_html=True)
                st.markdown("")
                _p1, _p2 = st.tabs(["📋 Registros","🤖 Orientação IA"])

                with _p1:
                    c1, c2 = st.columns(2)
                    with c1:
                        prev_tipo = st.selectbox("Tipo:", ["Vermifugação","Antipulgas","Anticarrapatos","Parasita interno","Parasita externo","Cuidado ambiental","Outro"], key="prev_tipo")
                        prev_data = st.text_input("Data:", value=datetime.now().strftime("%d/%m/%Y"), key="prev_data")
                    with c2:
                        prev_prod = st.text_input("Produto utilizado:", key="prev_prod", placeholder="Ex: Bravecto, Milbemax...")
                        prev_prox = st.text_input("Próxima aplicação:", key="prev_prox")
                    prev_obs = st.text_input("Observações:", key="prev_obs")
                    if st.button("💾 REGISTRAR", key="btn_prev_reg", use_container_width=True):
                        if prev_prod.strip():
                            st.session_state.hist_prevencao.append({"pet": pet.get('nome'), "tipo": prev_tipo, "data": prev_data, "produto": prev_prod, "proxima": prev_prox, "obs": prev_obs})
                            st.success("✅ Registrado!"); st.rerun()
                    prev_list = [p for p in st.session_state.hist_prevencao if p.get('pet') == pet.get('nome')]
                    if prev_list:
                        st.markdown("### 📋 Histórico")
                        for p in reversed(prev_list[-10:]):
                            st.markdown(f"<div class='hist-item'><b>🪱 {p.get('tipo','?')}</b> — {p.get('data','?')}<br><small>{p.get('produto','?')} | Próxima: {p.get('proxima','?')}</small></div>", unsafe_allow_html=True)

                with _p2:
                    duvida_prev = st.text_area("Sua dúvida sobre prevenção:", height=100, key="duvida_prev",
                        placeholder="Ex: Com que frequência devo vermifugar? Qual produto usar para pulgas?")
                    if st.button("🤖 CONSULTAR IA", key="btn_ia_prev", use_container_width=True):
                        if duvida_prev.strip():
                            with st.spinner("Consultando..."):
                                resp = ia(duvida_prev, f"PERFIL DO PET: {perfil_pet_txt()}\n\nOriente sobre controle preventivo de parasitas para esta espécie. Adapte as recomendações conforme o tipo de animal.")
                                if resp: st.session_state['res_p2_petint6'] = str(resp)
                            st.markdown(f"<div class='card'>{resp}</div>", unsafe_allow_html=True)
                        else:
                            st.warning("Digite sua dúvida.")

            # ══════════════════════════════════════════════
            # 🍖 ALIMENTAÇÃO
            # ══════════════════════════════════════════════

        with _sm_atividades:
            st.header("🏃 Atividades e Enriquecimento")
            pet = get_pet_ativo()
            if not pet:
                st.warning("Cadastre e selecione um pet primeiro.")
            else:
                st.markdown(f"<div class='badge'>{pet.get('especie','')} {pet.get('nome','?')}</div>", unsafe_allow_html=True)
                st.markdown("")
                ativ_ctx = st.text_area("Contexto atual (opcional):", height=80, key="ativ_ctx",
                    placeholder="Ex: Vive em apartamento, fica sozinho 8h por dia, tem quintal...")
                ativ_objetivo = st.selectbox("Objetivo:", ["Sugestão de atividades diárias","Enriquecimento ambiental","Reduzir ansiedade","Estimular inteligência","Socialização","Atividade física","Outro"], key="ativ_obj")
                if st.button("🏃 GERAR SUGESTÕES", key="btn_ativ", use_container_width=True):
                    with st.spinner("Gerando sugestões..."):
                        resp = ia(f"Objetivo: {ativ_objetivo}. Contexto: {ativ_ctx}",
                                 f"PERFIL DO PET: {perfil_pet_txt()}\n\nSugira atividades e enriquecimento ambiental ESPECÍFICOS para {pet.get('especie','')}. Não sugira caminhada para peixe ou gaiola para cachorro — adapte completamente à espécie. Seja prático e detalhado.")
                    st.markdown(f"<div class='card'>{resp}</div>", unsafe_allow_html=True)

            # ══════════════════════════════════════════════
            # 🧼 HIGIENE
            # ══════════════════════════════════════════════

        with _sm_ambiente:
            st.header("🏡 Ambiente Seguro")
            pet = get_pet_ativo()
            if not pet:
                st.warning("Cadastre e selecione um pet primeiro.")
            else:
                st.markdown(f"<div class='badge'>{pet.get('especie','')} {pet.get('nome','?')}</div>", unsafe_allow_html=True)
                st.markdown("")
                amb_ctx = st.text_area("Descreva seu ambiente:", height=80, key="amb_ctx",
                    placeholder="Ex: Apartamento no 5º andar, varanda sem grade, plantas em casa, quintal aberto...")
                if st.button("🏡 GERAR CHECKLIST DE SEGURANÇA", key="btn_amb", use_container_width=True):
                    if amb_ctx.strip():
                        with st.spinner("Gerando checklist..."):
                            resp = ia(f"Ambiente: {amb_ctx}",
                                     f"PERFIL DO PET: {perfil_pet_txt()}\n\nCrie um checklist de segurança ambiental ESPECÍFICO para {pet.get('especie','')} neste ambiente. Inclua riscos, plantas tóxicas para esta espécie, objetos perigosos e adaptações recomendadas.")
                        st.markdown(f"<div class='card'>{resp}</div>", unsafe_allow_html=True)
                    else:
                        st.warning("Descreva seu ambiente.")

            # ══════════════════════════════════════════════
            # 🧳 VIAGENS
            # ══════════════════════════════════════════════

        with _sm_viagem:
            st.header("🧳 Viagens com Animais")
            pet = get_pet_ativo()
            if not pet:
                st.warning("Cadastre e selecione um pet primeiro.")
            else:
                st.markdown(f"<div class='badge'>{pet.get('especie','')} {pet.get('nome','?')}</div>", unsafe_allow_html=True)
                st.markdown("")
                c1, c2 = st.columns(2)
                with c1:
                    viag_tipo = st.selectbox("Tipo de viagem:", ["Carro","Avião","Ônibus","Navio","Camping","Hotel","Curta (até 2h)","Longa (mais de 2h)"], key="viag_tipo")
                    viag_destino = st.text_input("Destino:", key="viag_dest", placeholder="Ex: Praia, interior, exterior...")
                with c2:
                    viag_duracao = st.text_input("Duração:", key="viag_dur", placeholder="Ex: 3 dias, 1 semana...")
                    viag_ctx = st.text_input("Contexto adicional:", key="viag_ctx", placeholder="Ex: Primeiro voo, pet ansioso...")
                if st.button("🧳 GERAR GUIA DE VIAGEM", key="btn_viag", use_container_width=True):
                    with st.spinner("Preparando guia..."):
                        resp = ia(f"Viagem de {viag_tipo} para {viag_destino}, duração {viag_duracao}. {viag_ctx}",
                                 f"PERFIL DO PET: {perfil_pet_txt()}\n\nCrie um guia completo de viagem para {pet.get('especie','')}. Inclua: checklist, transporte, documentação, alimentação, saúde, segurança e dicas específicas para esta espécie.")
                    st.markdown(f"<div class='card'>{resp}</div>", unsafe_allow_html=True)

            # ══════════════════════════════════════════════
            # 🤖 CHAT COM IA
            # ══════════════════════════════════════════════

        with _sm_profissionais:
            st.header("🏥 Cadastro de Profissionais")
            _pr1, _pr2 = st.tabs(["📋 Meus Profissionais","➕ Cadastrar"])

            with _pr1:
                profs = st.session_state.get('profissionais', [])
                if profs:
                    for p in profs:
                        emoji_p = {"Veterinário":"🩺","Clínica":"🏥","Especialista":"👨‍⚕️","Adestrador":"🎓","Pet Shop":"🛍️","Banho e Tosa":"🧼","Hotel para animais":"🏨"}.get(p.get('tipo',''),"📋")
                        st.markdown(f"<div class='pet-card'>{emoji_p} <b>{p.get('nome','?')}</b> <span class='badge'>{p.get('tipo','?')}</span><br><small>📞 {p.get('telefone','?')} | 📍 {p.get('endereco','?')}</small><br><small>🐾 Especialidade: {p.get('especialidade','?')}</small></div>", unsafe_allow_html=True)
                else:
                    st.info("Nenhum profissional cadastrado ainda.")

            with _pr2:
                st.markdown("### ➕ Cadastrar Profissional")
                c1, c2 = st.columns(2)
                with c1:
                    prof_nome = st.text_input("Nome:", key="prof_nome", placeholder="Ex: Dr. Carlos Silva")
                    prof_tipo = st.selectbox("Tipo:", ["Veterinário","Clínica","Especialista","Adestrador","Pet Shop","Banho e Tosa","Hotel para animais","Outro"], key="prof_tipo")
                    prof_tel = st.text_input("Telefone:", key="prof_tel", placeholder="Ex: (11) 99999-9999")
                with c2:
                    prof_end = st.text_input("Endereço:", key="prof_end")
                    prof_esp = st.text_input("Especialidade:", key="prof_esp", placeholder="Ex: Dermatologia felina, Animais exóticos...")
                    prof_obs = st.text_input("Observações:", key="prof_obs")
                if st.button("💾 CADASTRAR PROFISSIONAL", key="btn_prof_cad", use_container_width=True):
                    if prof_nome.strip():
                        st.session_state.profissionais.append({"nome": prof_nome, "tipo": prof_tipo, "telefone": prof_tel, "endereco": prof_end, "especialidade": prof_esp, "obs": prof_obs})
                        st.success("✅ Profissional cadastrado!"); st.rerun()
                    else:
                        st.warning("Informe o nome.")

            # ── RODAPÉ ──
            st.markdown("<hr class='divider'>", unsafe_allow_html=True)
            st.markdown("<div style='text-align:center;font-size:0.75em;color:#94A3B8;'>© 2026 Pet Inteligente · Quiz Com Prêmios · <a href='https://quizcompremios.com.br' target='_blank' style='color:#4F46E5;'>quizcompremios.com.br</a></div>", unsafe_allow_html=True)

# ── RODAPÉ ──
st.markdown("<hr class='divider'>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center;font-size:0.75em;color:#94A3B8;'>© 2026 Pet Inteligente · Quiz Com Prêmios · <a href='https://quizcompremios.com.br' target='_blank' style='color:#4F46E5;'>quizcompremios.com.br</a></div>", unsafe_allow_html=True)

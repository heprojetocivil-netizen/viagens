import streamlit as st
from groq import Groq
from datetime import datetime
import json

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="GUIA DE VIAGENS IA", layout="wide")

# --- ESTILO CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@400;500;600&display=swap');

    .stApp { background-color: #FFFFFF; color: #000000; font-family: 'DM Sans', sans-serif; }
    [data-testid="stSidebar"] { display: none; }

    .stTextInput>div>div>input,
    .stTextArea>div>textarea,
    .stSelectbox>div>div>div {
        background-color: #F0F9FF !important;
        color: #000000 !important;
        border: 1px solid #7DD3FC !important;
        font-family: 'DM Sans', sans-serif !important;
    }

    .stButton>button {
        width: 100%; border-radius: 12px; height: 3.5em;
        background: linear-gradient(135deg, #0369A1, #0EA5E9) !important;
        color: white !important; font-weight: 600; border: none;
        box-shadow: 2px 2px 8px rgba(3,105,161,0.25);
        font-family: 'DM Sans', sans-serif !important;
        transition: all 0.2s ease;
    }
    .stButton>button:hover { background: linear-gradient(135deg, #075985, #0369A1) !important; transform: translateY(-1px); }

    h1, h2, h3 { font-family: 'Playfair Display', serif !important; color: #1A1A2E !important; }
    p, span, label, div { color: #1A1A2E !important; font-family: 'DM Sans', sans-serif; }

    .card {
        background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%);
        padding: 22px; border-radius: 16px;
        border: 1px solid #7DD3FC; margin-bottom: 15px;
        color: #1A1A2E; box-shadow: 0 2px 12px rgba(3,105,161,0.08);
        white-space: pre-wrap;
    }
    .card-dark {
        background: linear-gradient(135deg, #0C1A2E 0%, #0F2847 100%);
        padding: 22px; border-radius: 16px;
        border: 1px solid #0369A1; margin-bottom: 15px;
        white-space: pre-wrap;
    }
    .card-dark, .card-dark * { color: #BAE6FD !important; }

    .card-green {
        background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%);
        padding: 22px; border-radius: 16px;
        border: 1px solid #86EFAC; margin-bottom: 15px;
        white-space: pre-wrap;
    }
    .card-orange {
        background: linear-gradient(135deg, #FFF7ED 0%, #FFEDD5 100%);
        padding: 22px; border-radius: 16px;
        border: 1px solid #FDBA74; margin-bottom: 15px;
        white-space: pre-wrap;
    }
    .card-purple {
        background: linear-gradient(135deg, #F5F3FF 0%, #EDE9FE 100%);
        padding: 22px; border-radius: 16px;
        border: 1px solid #C4B5FD; margin-bottom: 15px;
        white-space: pre-wrap;
    }
    .card-yellow {
        background: linear-gradient(135deg, #FEFCE8 0%, #FEF9C3 100%);
        padding: 22px; border-radius: 16px;
        border: 1px solid #FDE047; margin-bottom: 15px;
        white-space: pre-wrap;
    }

    .badge         { background: #0369A1; color: white !important; padding: 4px 14px; border-radius: 20px; font-size: 0.78em; font-weight: 600; display: inline-block; margin: 2px; }
    .badge-verde   { background: #059669; color: white !important; padding: 4px 14px; border-radius: 20px; font-size: 0.78em; font-weight: 600; display: inline-block; margin: 2px; }
    .badge-laranja { background: #EA580C; color: white !important; padding: 4px 14px; border-radius: 20px; font-size: 0.78em; font-weight: 600; display: inline-block; margin: 2px; }
    .badge-roxo    { background: #7C3AED; color: white !important; padding: 4px 14px; border-radius: 20px; font-size: 0.78em; font-weight: 600; display: inline-block; margin: 2px; }
    .badge-yellow  { background: #CA8A04; color: white !important; padding: 4px 14px; border-radius: 20px; font-size: 0.78em; font-weight: 600; display: inline-block; margin: 2px; }

    .stat-box { background: #F0F9FF; border-radius: 12px; padding: 18px; text-align: center; border: 1px solid #7DD3FC; }
    .stat-numero { font-size: 2em; font-weight: 700; color: #0369A1 !important; font-family: 'Playfair Display', serif; }

    .hist-item { background: #F0F9FF; border-radius: 10px; padding: 12px 16px; margin-bottom: 8px; border-left: 4px solid #0EA5E9; }

    .perfil-btn>button {
        background: linear-gradient(135deg, #0369A1, #0EA5E9) !important;
        color: white !important; font-weight: 700 !important;
        border-radius: 12px !important; height: 3em !important;
    }

    .divider { border: none; height: 1px; background: linear-gradient(to right, transparent, #7DD3FC, transparent); margin: 20px 0; }
    </style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CACHE
# ─────────────────────────────────────────────
@st.cache_resource
def get_cache_viagens():
    return {"perfis": {}}

_cache = get_cache_viagens()

# ─────────────────────────────────────────────
# PERSISTÊNCIA LOCAL (JSON)
# ─────────────────────────────────────────────
CHAVES_SALVAR = [
    'usuario', 'historico_roteiros', 'viagens_salvas',
    'cidade_origem', 'perfil_viagem', 'orcamento_padrao',
    'viagens_realizadas',
]

def gerar_json_sessao() -> str:
    dados = {k: st.session_state.get(k) for k in CHAVES_SALVAR}
    dados['salvo_em'] = datetime.now().strftime('%d/%m/%Y %H:%M')
    return json.dumps(dados, ensure_ascii=False, indent=2, default=str)

def carregar_json_sessao(dados: dict):
    for k in CHAVES_SALVAR:
        if k in dados:
            st.session_state[k] = dados[k]

def salvar_perfil_cache(usuario: str):
    _cache["perfis"][usuario] = {k: st.session_state.get(k) for k in CHAVES_SALVAR}

def perfis_salvos() -> list:
    return list(_cache["perfis"].keys())

def carregar_perfil_cache(usuario: str) -> dict | None:
    return _cache["perfis"].get(usuario)

def salvar_roteiro(tipo: str, destino: str, conteudo: str):
    st.session_state.historico_roteiros.append({
        'data':     datetime.now().strftime('%d/%m %H:%M'),
        'tipo':     tipo,
        'destino':  destino,
        'conteudo': conteudo,
    })

# --- INICIALIZAÇÃO DE ESTADO ---
defaults = {
    'etapa':               "Login",
    'usuario':             "",
    'api_key':             "",
    'pagina':              "Home",
    'historico_roteiros':  [],
    'viagens_salvas':      [],
    'cidade_origem':       "",
    'perfil_viagem':       "Cultural e histórico",
    'orcamento_padrao':    3000,
    'viagens_realizadas':  0,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# --- MOTOR DE IA ---
def viagem_ia(prompt: str, system_extra: str = "") -> str:
    try:
        client = Groq(api_key=st.session_state.api_key)
        system = f"""Você é um especialista em turismo e planejamento de viagens no Brasil e no mundo.
Usuário: {st.session_state.usuario}.
Cidade de origem: {st.session_state.cidade_origem or 'Brasil'}.
Perfil de viagem: {st.session_state.perfil_viagem}.
{system_extra}
REGRAS:
- Seja específico com nomes de lugares, restaurantes, hotéis e atrações reais
- Sempre informe estimativas de custo em reais (R$)
- Indique horários de funcionamento quando relevante
- Dê dicas práticas que guias normais não dão
- Escreva em português brasileiro natural e animado"""
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": prompt},
            ],
            model="llama-3.3-70b-versatile",
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Erro na API: {e}"

# --- BARRA DE SALVAR ---
def barra_salvar():
    salvar_perfil_cache(st.session_state.usuario)
    nome_usuario = st.session_state.usuario.lower().replace(' ', '_') or 'minha_sessao'
    total  = len(st.session_state.historico_roteiros)
    salvos = len(st.session_state.viagens_salvas)

    col_info, col_btn = st.columns([4, 2])
    with col_info:
        st.markdown(
            f"<div style='background:#F0F9FF;border:1px solid #7DD3FC;border-radius:10px;"
            f"padding:10px 14px;font-size:0.84em;color:#1A1A2E;line-height:1.6;'>"
            f"💾 <strong>Antes de sair, salve seus dados no computador.</strong><br>"
            f"<span style='color:#888;font-size:0.88em;'>{total} roteiros gerados · {salvos} viagens salvas</span>"
            f"</div>",
            unsafe_allow_html=True
        )
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        st.download_button(
            label="💾 SALVAR MEUS DADOS (.json)",
            data=gerar_json_sessao(),
            file_name=f"guia_viagens_{nome_usuario}.json",
            mime="application/json",
            use_container_width=True,
        )
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ============================================================
# TELA: LOGIN
# ============================================================
if st.session_state.etapa == "Login":
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.title("✈️ GUIA DE VIAGENS IA")
        st.markdown("**Roteiros personalizados, estimativas de custo e dicas exclusivas com Inteligência Artificial**")

        st.markdown("""<div style="background:#F0F9FF;border:1px solid #7DD3FC;border-radius:10px;
        padding:10px 16px;margin:10px 0 16px 0;font-size:0.88em;color:#1A1A2E;line-height:1.6;">
        🔒 <strong>ACESSO RESTRITO A CLIENTES DO QUIZ COM PRÊMIOS</strong><br>
        🔗 <a href="https://quizcompremios.com.br/" target="_blank"
        style="color:#0369A1;font-weight:600;text-decoration:none;">quizcompremios.com.br</a>
        </div>""", unsafe_allow_html=True)

        st.markdown("<hr class='divider'>", unsafe_allow_html=True)

        # ── PERFIS SALVOS NO SERVIDOR ─────────────────────────
        perfis = perfis_salvos()
        if perfis:
            st.markdown("#### ✈️ Guia de Viagens — clique para acessar seus dados")
            st.caption("Seus roteiros estão no servidor. Um clique e você entra.")
            chave_rapida = st.text_input("🔑 Sua Chave API da Groq:", type="password", key="chave_rapida")
            for nome_p in perfis:
                dados_p  = carregar_perfil_cache(nome_p)
                total_p  = len(dados_p.get('historico_roteiros', [])) if dados_p else 0
                origem_p = dados_p.get('cidade_origem', '') if dados_p else ''
                st.markdown('<div class="perfil-btn">', unsafe_allow_html=True)
                if st.button(
                    f"✈️ {nome_p}  —  {total_p} roteiros gerados  {('· saindo de ' + origem_p) if origem_p else ''}",
                    key=f"perfil_{nome_p}",
                    use_container_width=True
                ):
                    if not chave_rapida.strip():
                        st.warning("Cole sua chave API acima antes de entrar.")
                    else:
                        st.session_state.usuario = nome_p
                        st.session_state.api_key = chave_rapida
                        carregar_json_sessao(dados_p)
                        st.session_state.etapa = "App"
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("<hr class='divider'>", unsafe_allow_html=True)
            st.markdown("**Ou entre com outro nome:**")

        nome = st.text_input("Seu Nome:", key="input_nome_login")
        chave = st.text_input("Sua Chave API da Groq:", type="password", key="chave_nova")

        if not perfis:
            st.markdown("""<div style="background:#F0F9FF;border:1px solid #7DD3FC;border-radius:10px;
            padding:12px 16px;font-size:0.86em;color:#1A1A2E;line-height:1.7;margin:10px 0;">
            📥 <strong>Seus dados sumiram?</strong> Isso acontece quando o servidor reinicia.<br>
            Selecione abaixo o arquivo <strong>.json</strong> que você salvou antes — seus roteiros voltam completos.
            </div>""", unsafe_allow_html=True)
            arq_login = st.file_uploader("Carregar meus dados salvos (.json):", type=["json"], key="upload_login")
        else:
            arq_login = None

        dados_login = None
        if arq_login is not None:
            try:
                dados_login = json.load(arq_login)
                nome_login  = dados_login.get('usuario', '')
                st.success(f"✅ Dados de **{nome_login}** reconhecidos! Clique em Entrar.")
            except Exception:
                st.error("Arquivo inválido.")
                dados_login = None

        if st.button("✨ ENTRAR E PLANEJAR MINHA VIAGEM"):
            if nome and chave:
                st.session_state.usuario = nome
                st.session_state.api_key = chave
                if dados_login:
                    carregar_json_sessao(dados_login)
                st.session_state.etapa = "App"
                st.rerun()
            else:
                st.warning("Preencha nome e chave API.")

        st.markdown("🔑 Não tem chave Groq? Crie grátis em <a href='https://console.groq.com/keys' target='_blank' style='color:#0369A1;font-weight:600;'>console.groq.com/keys</a>", unsafe_allow_html=True)

# ============================================================
# TELA: APP
# ============================================================
elif st.session_state.etapa == "App":

    barra_salvar()

    # NAVBAR
    cols = st.columns(8)
    paginas_nav = [
        ("🏠", "Home"),
        ("🗺️", "Roteiro"),
        ("🇧🇷", "Brasil"),
        ("💰", "Orcamento"),
        ("🗣️", "Frases"),
        ("🧳", "Checklist"),
        ("👥", "Grupo"),
        ("❤️", "Salvos"),
    ]
    nomes_nav = {
        "Home":      "Painel Principal",
        "Roteiro":   "Roteiro Completo",
        "Brasil":    "Fim de Semana no Brasil",
        "Orcamento": "Estimativa de Custos",
        "Frases":    "Frases Essenciais no Idioma",
        "Checklist": "Checklist de Viagem",
        "Grupo":     "Viagem em Grupo",
        "Salvos":    "Viagens Salvas",
    }
    for i, (icone, pagina) in enumerate(paginas_nav):
        if cols[i].button(icone, key=f"nav_{pagina}", help=nomes_nav[pagina]):
            st.session_state.pagina = pagina
            st.rerun()

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ========================
    # HOME
    # ========================
    if st.session_state.pagina == "Home":
        col_u, col_r = st.columns([3, 1])
        with col_u:
            st.title(f"Bora viajar, {st.session_state.usuario}! ✈️")
            st.markdown("<span class='badge'>Explorador</span>", unsafe_allow_html=True)
        with col_r:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚪 Sair"):
                for k in list(st.session_state.keys()):
                    del st.session_state[k]
                st.rerun()

        # AVISO SE DADOS SUMIRAM
        if len(st.session_state.historico_roteiros) == 0 and len(st.session_state.viagens_salvas) == 0:
            st.markdown("""<div style="background:#FEF3C7;border:2px solid #F59E0B;border-radius:12px;
            padding:12px 18px;margin-bottom:4px;color:#000;font-size:0.9em;font-weight:600;">
            ⚠️ Seus dados não estão mais no servidor.
            </div>""", unsafe_allow_html=True)
            arq_home = st.file_uploader("Carregar meus dados salvos (.json):", type=["json"], key="upload_home")
            if arq_home is not None:
                try:
                    dados_home = json.load(arq_home)
                    carregar_json_sessao(dados_home)
                    salvar_perfil_cache(st.session_state.usuario)
                    st.success("✅ Dados recuperados!")
                    st.rerun()
                except Exception:
                    st.error("Arquivo inválido.")
            st.markdown("<br>", unsafe_allow_html=True)

        # PERFIL DO VIAJANTE
        st.markdown("#### ⚙️ Seu perfil de viajante")
        col_a, col_b = st.columns(2)
        with col_a:
            st.session_state.cidade_origem  = st.text_input(
                "De qual cidade você sai:", value=st.session_state.cidade_origem,
                placeholder="ex: São Paulo, Fortaleza, Belo Horizonte...")
            st.session_state.perfil_viagem  = st.selectbox(
                "Seu estilo de viagem:", [
                    "Cultural e histórico","Aventura e natureza","Praia e relaxamento",
                    "Gastronomia e vinhos","Família com crianças","Casal romântico",
                    "Mochilão econômico","Luxo e conforto","Religioso e espiritual",
                ],
                index=["Cultural e histórico","Aventura e natureza","Praia e relaxamento",
                    "Gastronomia e vinhos","Família com crianças","Casal romântico",
                    "Mochilão econômico","Luxo e conforto","Religioso e espiritual",
                ].index(st.session_state.perfil_viagem) if st.session_state.perfil_viagem in
                ["Cultural e histórico","Aventura e natureza","Praia e relaxamento",
                    "Gastronomia e vinhos","Família com crianças","Casal romântico",
                    "Mochilão econômico","Luxo e conforto","Religioso e espiritual"] else 0)
        with col_b:
            st.session_state.orcamento_padrao = st.number_input(
                "Orçamento médio por viagem (R$):", min_value=500, max_value=100000,
                value=st.session_state.orcamento_padrao, step=500)

        st.markdown("<br>", unsafe_allow_html=True)

        # MÉTRICAS
        total  = len(st.session_state.historico_roteiros)
        salvos = len(st.session_state.viagens_salvas)
        tipos  = {}
        for r in st.session_state.historico_roteiros:
            tipos[r['tipo']] = tipos.get(r['tipo'], 0) + 1

        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f"<div class='stat-box'><div class='stat-numero'>{total}</div><div>Roteiros gerados</div></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='stat-box'><div class='stat-numero'>{salvos}</div><div>Viagens salvas</div></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='stat-box'><div class='stat-numero'>{tipos.get('Roteiro Completo',0)}</div><div>Roteiros completos</div></div>", unsafe_allow_html=True)
        c4.markdown(f"<div class='stat-box'><div class='stat-numero'>{tipos.get('Fim de Semana',0)}</div><div>FDS planejados</div></div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<div class='card'>💡 <em>'O mundo é um livro e quem não viaja lê apenas uma página.'</em> — Santo Agostinho</div>", unsafe_allow_html=True)

        st.markdown("### 🗺️ O que cada aba faz")
        guia = {
            "🗺️ Roteiro Completo":      "Roteiro dia a dia completo para qualquer destino do mundo — com horários, custos e dicas",
            "🇧🇷 Fim de Semana no Brasil": "Destinos incríveis perto de você para viajar sem gastar muito",
            "💰 Estimativa de Custos":   "Planejamento financeiro da viagem — passagem, hotel, alimentação, passeios",
            "🗣️ Frases Essenciais":      "As frases mais importantes no idioma local para se virar em qualquer situação",
            "🧳 Checklist de Viagem":    "Lista completa do que levar, documentos, apps e o que não esquecer",
            "👥 Viagem em Grupo":        "Plano completo para viagem em grupo — divisão de custos e o que combinar antes",
            "❤️ Viagens Salvas":         "Seus roteiros favoritos organizados e prontos para consultar",
        }
        for aba, desc in guia.items():
            st.markdown(f"**{aba}** — {desc}")

        if st.session_state.historico_roteiros:
            st.markdown("### 🕐 Últimos Roteiros")
            for item in reversed(st.session_state.historico_roteiros[-4:]):
                st.markdown(
                    f"<div class='hist-item'>"
                    f"<span class='badge'>{item['tipo']}</span> "
                    f"<span class='badge-laranja'>✈️ {item['destino']}</span> "
                    f"<small style='color:#888'>{item['data']}</small></div>",
                    unsafe_allow_html=True
                )

    # ========================
    # ROTEIRO COMPLETO
    # ========================
    elif st.session_state.pagina == "Roteiro":
        st.header("🗺️ Roteiro Completo de Viagem")
        st.markdown("Roteiro dia a dia detalhado — do café da manhã ao jantar, com custos e dicas exclusivas.")

        col1, col2 = st.columns(2)
        with col1:
            destino   = st.text_input("✈️ Destino:", placeholder="ex: Lisboa, Cancún, Nordeste Brasileiro, Roma, Tokyo...")
            dias      = st.slider("📅 Quantos dias:", 2, 21, 7)
            origem    = st.text_input("🏠 Saindo de:", value=st.session_state.cidade_origem, placeholder="ex: São Paulo, Recife...")
        with col2:
            orcamento = st.number_input("💰 Orçamento total (R$):", min_value=500, max_value=200000,
                value=st.session_state.orcamento_padrao, step=500)
            perfil    = st.selectbox("🎭 Estilo da viagem:", [
                "Cultural e histórico","Aventura e natureza","Praia e relaxamento",
                "Gastronomia","Família com crianças","Casal romântico",
                "Mochilão econômico","Luxo e conforto",
            ], index=["Cultural e histórico","Aventura e natureza","Praia e relaxamento",
                "Gastronomia","Família com crianças","Casal romântico",
                "Mochilão econômico","Luxo e conforto"].index(
                st.session_state.perfil_viagem) if st.session_state.perfil_viagem in
                ["Cultural e histórico","Aventura e natureza","Praia e relaxamento",
                "Gastronomia","Família com crianças","Casal romântico",
                "Mochilão econômico","Luxo e conforto"] else 0)
            pessoas   = st.selectbox("👥 Quantas pessoas:", ["1 pessoa","2 pessoas","3-4 pessoas","5+ pessoas"])
            epoca     = st.text_input("📅 Período da viagem:", placeholder="ex: janeiro, carnaval, julho, qualquer época...")

        if st.button("🗺️ GERAR ROTEIRO COMPLETO"):
            if destino.strip():
                with st.spinner(f"Montando seu roteiro para {destino}..."):
                    prompt = (
                        f"Crie um roteiro completo de {dias} dias para {destino}.\n"
                        f"Saindo de: {origem or 'Brasil'}. Orçamento: R${orcamento}. "
                        f"Estilo: {perfil}. Pessoas: {pessoas}. Época: {epoca or 'qualquer'}.\n\n"
                        f"ESTRUTURA:\n\n"
                        f"✈️ ROTEIRO: {destino.upper()} — {dias} DIAS\n"
                        f"Estilo: {perfil} | {pessoas} | R${orcamento} total\n\n"
                        f"📋 INFORMAÇÕES ESSENCIAIS:\n"
                        f"• Melhor época para ir\n"
                        f"• Como chegar (passagem estimada de {origem or 'Brasil'})\n"
                        f"• Documentos necessários\n"
                        f"• Moeda e câmbio atual estimado\n"
                        f"• Fuso horário\n\n"
                        f"Para CADA dia use este formato:\n\n"
                        f"━━━━━━━━━━━━━━━━━━━━━\n"
                        f"📅 DIA [N] — [TEMA DO DIA]\n"
                        f"━━━━━━━━━━━━━━━━━━━━━\n"
                        f"☕ Manhã ([horário]):\n"
                        f"• [atividade/local] — [dica exclusiva] — aprox. R$[X]\n\n"
                        f"🍽️ Almoço ([horário]):\n"
                        f"• [restaurante específico] — [prato recomendado] — R$[X] p/pessoa\n\n"
                        f"🌅 Tarde ([horário]):\n"
                        f"• [atividade/local] — [dica exclusiva] — R$[X]\n\n"
                        f"🌙 Noite ([horário]):\n"
                        f"• [jantar + programa noturno] — R$[X]\n\n"
                        f"💰 Gasto estimado do dia: R$[X] p/pessoa\n\n"
                        f"[Repita para todos os {dias} dias]\n\n"
                        f"🏨 HOSPEDAGEM SUGERIDA:\n"
                        f"[3 opções por perfil: econômico, intermediário e confortável — com bairro e preço/noite]\n\n"
                        f"🚗 COMO SE LOCOMOVER:\n"
                        f"[Transporte local — app, metrô, carro, táxi — com custos]\n\n"
                        f"📊 RESUMO FINANCEIRO:\n"
                        f"Passagem: R$[X]\n"
                        f"Hospedagem {dias} noites: R$[X]\n"
                        f"Alimentação: R$[X]\n"
                        f"Passeios: R$[X]\n"
                        f"Transporte local: R$[X]\n"
                        f"Total estimado: R$[X] p/pessoa\n\n"
                        f"💡 DICAS DE OURO:\n"
                        f"[5 dicas que só quem conhece {destino} de verdade sabe]"
                    )
                    res = viagem_ia(prompt)
                    salvar_roteiro("Roteiro Completo", destino, res)
                    st.session_state['roteiro_temp'] = res
                    st.markdown(f"<div class='card'>{res}</div>", unsafe_allow_html=True)
            else:
                st.warning("Informe o destino da viagem.")

        if st.session_state.get('roteiro_temp'):
            col_dl, col_sv, col_novo = st.columns(3)
            with col_dl:
                st.download_button("📋 Baixar roteiro (.txt)",
                    data=st.session_state['roteiro_temp'],
                    file_name=f"roteiro_{destino.replace(' ','_') if 'destino' in dir() else 'viagem'}.txt",
                    mime="text/plain", use_container_width=True)
            with col_sv:
                if st.button("❤️ Salvar viagem", use_container_width=True):
                    st.session_state.viagens_salvas.append({
                        'tipo': 'Roteiro Completo',
                        'destino': destino if 'destino' in dir() else '',
                        'conteudo': st.session_state['roteiro_temp'],
                        'data': datetime.now().strftime('%d/%m %H:%M'),
                    })
                    st.success("❤️ Salvo!")
            with col_novo:
                if st.button("🔄 Gerar outro roteiro", use_container_width=True):
                    st.session_state.pop('roteiro_temp', None)
                    st.rerun()

    # ========================
    # FIM DE SEMANA NO BRASIL
    # ========================
    elif st.session_state.pagina == "Brasil":
        st.header("🇧🇷 Fim de Semana no Brasil")
        st.markdown("Descubra destinos incríveis perto de você — para viajar sem gastar muito.")

        col1, col2 = st.columns(2)
        with col1:
            origem_br  = st.text_input("🏠 Sua cidade:", value=st.session_state.cidade_origem,
                placeholder="ex: São Paulo, Recife, Belo Horizonte...")
            distancia  = st.selectbox("📍 Distância máxima:", [
                "Até 3 horas de carro","Até 5 horas de carro","Até 2 horas de avião","Qualquer lugar do Brasil",
            ])
            orcamento_br= st.number_input("💰 Orçamento do fim de semana (R$):",
                min_value=200, max_value=10000, value=1500, step=200)
        with col2:
            perfil_br  = st.selectbox("🎭 O que você quer:", [
                "Praia e mar","Serra e natureza","Cidade histórica","Parque e ecoturismo",
                "Gastronomia regional","Aventura e esportes","Sossego e descanso",
            ])
            pessoas_br = st.selectbox("👥 Viajantes:", ["Só eu","Casal","Família com crianças","Grupo de amigos"])
            carro      = st.checkbox("🚗 Tenho carro", value=True)

        if st.button("🇧🇷 ENCONTRAR DESTINOS PERFEITOS"):
            if origem_br.strip():
                with st.spinner("Procurando os melhores destinos..."):
                    prompt = (
                        f"Sugira 3 destinos para fim de semana saindo de {origem_br}.\n"
                        f"Distância: {distancia}. Orçamento: R${orcamento_br}. "
                        f"Perfil: {perfil_br}. Viajantes: {pessoas_br}. "
                        f"{'Tem carro.' if carro else 'Sem carro — vai de ônibus ou avião.'}\n\n"
                        f"Para CADA destino:\n\n"
                        f"🏖️ DESTINO [N]: [NOME DA CIDADE/LUGAR]\n"
                        f"📍 Estado: [X] | Distância de {origem_br}: [X] horas\n"
                        f"⭐ Por que ir: [3 motivos específicos]\n\n"
                        f"📅 ROTEIRO DO FIM DE SEMANA:\n\n"
                        f"SÁBADO:\n"
                        f"• Manhã: [o que fazer] — R$[X]\n"
                        f"• Almoço: [onde comer — restaurante específico] — R$[X]\n"
                        f"• Tarde: [o que fazer] — R$[X]\n"
                        f"• Jantar: [onde comer] — R$[X]\n\n"
                        f"DOMINGO:\n"
                        f"• Manhã: [o que fazer] — R$[X]\n"
                        f"• Almoço: [onde comer] — R$[X]\n"
                        f"• Retorno: [horário sugerido]\n\n"
                        f"💰 CUSTO TOTAL ESTIMADO:\n"
                        f"• Transporte (ida e volta): R$[X]\n"
                        f"• Hospedagem (1 noite): R$[X]\n"
                        f"• Alimentação: R$[X]\n"
                        f"• Passeios: R$[X]\n"
                        f"• TOTAL: R$[X] p/pessoa\n\n"
                        f"🏨 Onde ficar: [2 sugestões com preço/noite]\n"
                        f"💡 Dica especial: [algo que poucos turistas sabem]\n\n"
                        f"---\n\n"
                        f"[Repita para os 3 destinos]\n\n"
                        f"🏆 NOSSA RECOMENDAÇÃO:\n"
                        f"[Qual dos 3 é melhor para esse perfil e por quê]"
                    )
                    res = viagem_ia(prompt)
                    salvar_roteiro("Fim de Semana", f"FDS saindo de {origem_br}", res)
                    st.session_state['brasil_temp'] = res
                    st.markdown(f"<div class='card-green'>{res}</div>", unsafe_allow_html=True)
            else:
                st.warning("Informe sua cidade de origem.")

        if st.session_state.get('brasil_temp'):
            col_dl, col_sv = st.columns(2)
            with col_dl:
                st.download_button("📋 Baixar roteiro (.txt)", data=st.session_state['brasil_temp'],
                    file_name="fim_de_semana_brasil.txt", mime="text/plain", use_container_width=True)
            with col_sv:
                if st.button("❤️ Salvar", key="sv_br", use_container_width=True):
                    st.session_state.viagens_salvas.append({
                        'tipo': 'Fim de Semana', 'destino': f"FDS de {origem_br if 'origem_br' in dir() else ''}",
                        'conteudo': st.session_state['brasil_temp'],
                        'data': datetime.now().strftime('%d/%m %H:%M'),
                    })
                    st.success("❤️ Salvo!")

    # ========================
    # ESTIMATIVA DE CUSTOS
    # ========================
    elif st.session_state.pagina == "Orcamento":
        st.header("💰 Estimativa de Custos da Viagem")
        st.markdown("Planejamento financeiro completo — para não ter surpresas na viagem.")

        col1, col2 = st.columns(2)
        with col1:
            destino_o  = st.text_input("✈️ Destino:", placeholder="ex: Europa, Maldivas, Bahia...")
            dias_o     = st.number_input("📅 Dias de viagem:", min_value=2, max_value=60, value=10)
            pessoas_o  = st.number_input("👥 Número de pessoas:", min_value=1, max_value=20, value=2)
        with col2:
            padrao_o   = st.selectbox("⭐ Padrão de viagem:", [
                "Econômico (mochileiro)","Intermediário (confortável)","Superior (confortável+)","Luxo",
            ])
            origem_o   = st.text_input("🏠 Cidade de origem:", value=st.session_state.cidade_origem)
            tipo_o     = st.radio("Tipo:", ["Internacional","Nacional"], horizontal=True)

        if st.button("💰 GERAR ESTIMATIVA COMPLETA"):
            if destino_o.strip():
                with st.spinner("Calculando custos..."):
                    prompt = (
                        f"Crie uma estimativa detalhada de custos para viagem.\n"
                        f"Destino: {destino_o}. Dias: {dias_o}. Pessoas: {pessoas_o}.\n"
                        f"Padrão: {padrao_o}. Saindo de: {origem_o or 'Brasil'}. Tipo: {tipo_o}.\n\n"
                        f"FORMATO:\n\n"
                        f"💰 ESTIMATIVA DE CUSTOS — {destino_o.upper()}\n"
                        f"{dias_o} dias · {pessoas_o} pessoa(s) · Padrão {padrao_o}\n\n"
                        f"✈️ PASSAGENS (ida e volta por pessoa):\n"
                        f"• Preço médio: R$[X]\n"
                        f"• Melhor época para comprar: [X meses antes]\n"
                        f"• Sites recomendados: [lista]\n"
                        f"• Dica para economizar: [estratégia específica]\n\n"
                        f"🏨 HOSPEDAGEM (por noite — {dias_o-1} noites):\n"
                        f"• Econômico: R$[X]/noite — exemplo: [tipo de local]\n"
                        f"• Recomendado: R$[X]/noite — exemplo: [tipo de local]\n"
                        f"• Confortável: R$[X]/noite — exemplo: [tipo de local]\n"
                        f"• Total ({padrao_o}): R$[X]\n\n"
                        f"🍽️ ALIMENTAÇÃO (por dia por pessoa):\n"
                        f"• Café da manhã: R$[X]\n"
                        f"• Almoço: R$[X]\n"
                        f"• Jantar: R$[X]\n"
                        f"• Lanches/bebidas: R$[X]\n"
                        f"• Total por dia: R$[X] | Total {dias_o} dias: R$[X]\n\n"
                        f"🎡 PASSEIOS E ATRAÇÕES:\n"
                        f"• [Atração 1]: R$[X]\n"
                        f"• [Atração 2]: R$[X]\n"
                        f"• [Atração 3]: R$[X]\n"
                        f"• Estimativa total passeios: R$[X]\n\n"
                        f"🚗 TRANSPORTE LOCAL:\n"
                        f"• [modalidade]: R$[X]/dia\n"
                        f"• Total: R$[X]\n\n"
                        f"🛍️ COMPRAS E SOUVENIRS: R$[X] (estimativa)\n\n"
                        f"🏥 SEGURO VIAGEM: R$[X] (recomendado)\n\n"
                        f"━━━━━━━━━━━━━━━━━━━━━\n"
                        f"📊 RESUMO TOTAL:\n"
                        f"• Por pessoa: R$[X]\n"
                        f"• Total do grupo ({pessoas_o} pessoas): R$[X]\n"
                        f"• Reserve mais 15% para imprevistos: R$[X]\n"
                        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"💡 3 FORMAS DE ECONOMIZAR NESSA VIAGEM:\n"
                        f"[Dicas específicas para {destino_o} no padrão {padrao_o}]\n\n"
                        f"📅 MELHOR ÉPOCA PARA IR (relação custo-benefício):\n"
                        f"[Meses ideais e por que]"
                    )
                    res = viagem_ia(prompt)
                    salvar_roteiro("Estimativa de Custos", destino_o, res)
                    st.session_state['orcamento_temp'] = res
                    st.markdown(f"<div class='card-orange'>{res}</div>", unsafe_allow_html=True)
            else:
                st.warning("Informe o destino.")

        if st.session_state.get('orcamento_temp'):
            col_dl, col_sv = st.columns(2)
            with col_dl:
                st.download_button("📋 Baixar estimativa (.txt)", data=st.session_state['orcamento_temp'],
                    file_name=f"custos_{destino_o.replace(' ','_') if 'destino_o' in dir() else 'viagem'}.txt",
                    mime="text/plain", use_container_width=True)
            with col_sv:
                if st.button("❤️ Salvar", key="sv_orc", use_container_width=True):
                    st.session_state.viagens_salvas.append({
                        'tipo': 'Estimativa de Custos', 'destino': destino_o if 'destino_o' in dir() else '',
                        'conteudo': st.session_state['orcamento_temp'],
                        'data': datetime.now().strftime('%d/%m %H:%M'),
                    })
                    st.success("❤️ Salvo!")

    # ========================
    # FRASES ESSENCIAIS
    # ========================
    elif st.session_state.pagina == "Frases":
        st.header("🗣️ Frases Essenciais no Idioma Local")
        st.markdown("As frases que você PRECISA saber para se virar em qualquer país.")

        col1, col2 = st.columns(2)
        with col1:
            pais_f   = st.text_input("🌍 País ou idioma:", placeholder="ex: França, Japão, Espanha, Italiano...")
            contexto_f = st.multiselect("📋 Situações:", [
                "Hotel e acomodação","Restaurante e comida","Transporte e direções",
                "Compras e mercado","Emergências e saúde","Turismo e passeios",
                "Aeroporto e fronteira","Social e apresentações","Números e dinheiro",
            ], default=["Restaurante e comida","Transporte e direções","Emergências e saúde"])
        with col2:
            nivel_f  = st.radio("Nível:", ["Turista básico (sobrevivência)","Intermediário (conforto)","Avançado (fluência básica)"], horizontal=True)
            fonetica = st.checkbox("Incluir pronúncia fonética", value=True)

        if st.button("🗣️ GERAR FRASES ESSENCIAIS"):
            if pais_f.strip():
                with st.spinner(f"Preparando frases em {pais_f}..."):
                    contexts = ", ".join(contexto_f) if contexto_f else "situações gerais"
                    prompt = (
                        f"Crie um guia de frases essenciais para {pais_f}.\n"
                        f"Situações: {contexts}. Nível: {nivel_f}.\n"
                        f"{'Inclua pronúncia fonética entre colchetes.' if fonetica else ''}\n\n"
                        f"FORMATO para cada situação:\n\n"
                        f"[EMOJI] [SITUAÇÃO]\n\n"
                        f"| Português | {pais_f} | {'Pronúncia' if fonetica else ''} |\n"
                        f"|-----------|---------|{'---------' if fonetica else ''}|\n"
                        f"| [frase PT] | [frase no idioma] | {'[como pronunciar]' if fonetica else ''} |\n\n"
                        f"[Mínimo 6 frases por situação]\n\n"
                        f"[Repita para todas as situações solicitadas]\n\n"
                        f"🆘 FRASES DE EMERGÊNCIA (memorize antes de viajar):\n"
                        f"[As 10 frases mais importantes em qualquer situação de risco]\n\n"
                        f"📱 APPS DE TRADUÇÃO RECOMENDADOS:\n"
                        f"[Os melhores apps para {pais_f} — com ou sem internet]\n\n"
                        f"💡 DICA CULTURAL:\n"
                        f"[Como os locais reagem quando estrangeiros tentam falar o idioma deles]"
                    )
                    res = viagem_ia(prompt)
                    salvar_roteiro("Frases Essenciais", pais_f, res)
                    st.session_state['frases_temp'] = res
                    st.markdown(f"<div class='card-purple'>{res}</div>", unsafe_allow_html=True)
            else:
                st.warning("Informe o país ou idioma.")

        if st.session_state.get('frases_temp'):
            col_dl, col_sv = st.columns(2)
            with col_dl:
                st.download_button("📋 Baixar frases (.txt)", data=st.session_state['frases_temp'],
                    file_name=f"frases_{pais_f.replace(' ','_') if 'pais_f' in dir() else 'idioma'}.txt",
                    mime="text/plain", use_container_width=True)
            with col_sv:
                if st.button("❤️ Salvar", key="sv_fr", use_container_width=True):
                    st.session_state.viagens_salvas.append({
                        'tipo': 'Frases Essenciais', 'destino': pais_f if 'pais_f' in dir() else '',
                        'conteudo': st.session_state['frases_temp'],
                        'data': datetime.now().strftime('%d/%m %H:%M'),
                    })
                    st.success("❤️ Salvo!")

    # ========================
    # CHECKLIST DE VIAGEM
    # ========================
    elif st.session_state.pagina == "Checklist":
        st.header("🧳 Checklist de Viagem")
        st.markdown("Lista completa e personalizada do que levar — para não esquecer nada importante.")

        col1, col2 = st.columns(2)
        with col1:
            destino_c  = st.text_input("✈️ Destino:", placeholder="ex: Europa no inverno, praia no Nordeste, Tokyo...")
            dias_c     = st.number_input("📅 Dias de viagem:", min_value=1, max_value=60, value=10)
            clima_c    = st.selectbox("🌡️ Clima esperado:", [
                "Quente e úmido (tropical)","Quente e seco","Frio (abaixo de 15°C)","Muito frio (neve/geada)",
                "Temperado (ameno)","Variado (várias estações)",
            ])
        with col2:
            tipo_c     = st.selectbox("✈️ Tipo de viagem:", [
                "Internacional","Nacional — avião","Nacional — carro","Cruzeiro","Camping/Aventura",
            ])
            atividades = st.multiselect("🎯 Atividades planejadas:", [
                "Praia e mar","Trilhas e montanha","Cidade e museus","Festas e baladas",
                "Negócios","Mergulho","Esqui","Safari","Spa e relaxamento",
            ])
            mala_c     = st.radio("🧳 Tipo de mala:", ["Mala de despacho","Mochila carry-on","Ambas"], horizontal=True)

        if st.button("🧳 GERAR MEU CHECKLIST PERSONALIZADO"):
            if destino_c.strip():
                with st.spinner("Montando seu checklist..."):
                    ativ = ", ".join(atividades) if atividades else "turismo geral"
                    prompt = (
                        f"Crie um checklist completo e personalizado de viagem.\n"
                        f"Destino: {destino_c}. Dias: {dias_c}. Clima: {clima_c}.\n"
                        f"Tipo: {tipo_c}. Atividades: {ativ}. Mala: {mala_c}.\n\n"
                        f"FORMATO:\n\n"
                        f"🧳 CHECKLIST — {destino_c.upper()}\n"
                        f"{dias_c} dias · {clima_c} · {mala_c}\n\n"
                        f"📄 DOCUMENTOS E DINHEIRO:\n"
                        f"[ ] [item — com observação específica]\n\n"
                        f"👔 ROUPAS E ACESSÓRIOS:\n"
                        f"[ ] [item — quantidade sugerida para {dias_c} dias]\n\n"
                        f"🧴 HIGIENE E SAÚDE:\n"
                        f"[ ] [item]\n\n"
                        f"💊 MEDICAMENTOS E PRIMEIROS SOCORROS:\n"
                        f"[ ] [item — com para que serve]\n\n"
                        f"📱 TECNOLOGIA E ELETRÔNICOS:\n"
                        f"[ ] [item — com observação]\n\n"
                        f"🎒 ITENS ESPECÍFICOS PARA {ativ.upper()}:\n"
                        f"[ ] [item específico para as atividades planejadas]\n\n"
                        f"🔑 ANTES DE SAIR DE CASA:\n"
                        f"[ ] [checklist do apartamento/casa]\n\n"
                        f"📱 APPS ESSENCIAIS PARA INSTALAR:\n"
                        f"[ ] [app — para que serve]\n\n"
                        f"⚠️ NÃO LEVE NA MALA DE MÃO:\n"
                        f"[Lista do que é proibido — específico para {tipo_c}]\n\n"
                        f"💡 DICA DE MALA:\n"
                        f"[Como organizar a mala para {dias_c} dias em {mala_c}]"
                    )
                    res = viagem_ia(prompt)
                    salvar_roteiro("Checklist", destino_c, res)
                    st.session_state['check_temp'] = res
                    st.markdown(f"<div class='card-yellow'>{res}</div>", unsafe_allow_html=True)
            else:
                st.warning("Informe o destino.")

        if st.session_state.get('check_temp'):
            col_dl, col_sv = st.columns(2)
            with col_dl:
                st.download_button("📋 Baixar checklist (.txt)", data=st.session_state['check_temp'],
                    file_name=f"checklist_{destino_c.replace(' ','_') if 'destino_c' in dir() else 'viagem'}.txt",
                    mime="text/plain", use_container_width=True)
            with col_sv:
                if st.button("❤️ Salvar", key="sv_ck", use_container_width=True):
                    st.session_state.viagens_salvas.append({
                        'tipo': 'Checklist', 'destino': destino_c if 'destino_c' in dir() else '',
                        'conteudo': st.session_state['check_temp'],
                        'data': datetime.now().strftime('%d/%m %H:%M'),
                    })
                    st.success("❤️ Salvo!")

    # ========================
    # VIAGEM EM GRUPO
    # ========================
    elif st.session_state.pagina == "Grupo":
        st.header("👥 Plano de Viagem em Grupo")
        st.markdown("Organize tudo antes de sair — divisão de custos, o que combinar e como evitar conflitos.")

        col1, col2 = st.columns(2)
        with col1:
            destino_g  = st.text_input("✈️ Destino:", placeholder="ex: Cartagena, Chapada Diamantina, Buenos Aires...")
            pessoas_g  = st.number_input("👥 Número de pessoas no grupo:", min_value=3, max_value=30, value=6)
            dias_g     = st.number_input("📅 Dias de viagem:", min_value=2, max_value=21, value=5)
        with col2:
            perfil_g   = st.selectbox("🎭 Perfil do grupo:", [
                "Amigos da faculdade","Família grande","Colegas de trabalho",
                "Casal + amigos","Grupo misto (famílias e solteiros)","Turma da empresa",
            ])
            orcamento_g= st.number_input("💰 Orçamento por pessoa (R$):", min_value=200, max_value=20000, value=2000, step=200)
            diferencias= st.text_area("⚠️ Restrições ou diferenças no grupo:", height=60,
                placeholder="ex: 2 vegetarianos, 1 com mobilidade reduzida, crianças pequenas...")

        if st.button("👥 GERAR PLANO COMPLETO PARA GRUPO"):
            if destino_g.strip():
                with st.spinner("Organizando a viagem em grupo..."):
                    prompt = (
                        f"Crie um plano completo de viagem em grupo.\n"
                        f"Destino: {destino_g}. Pessoas: {pessoas_g}. Dias: {dias_g}.\n"
                        f"Perfil: {perfil_g}. Orçamento por pessoa: R${orcamento_g}.\n"
                        f"Particularidades: {diferencias or 'nenhuma'}.\n\n"
                        f"ESTRUTURA:\n\n"
                        f"👥 PLANO DE GRUPO — {destino_g.upper()}\n"
                        f"{pessoas_g} pessoas · {dias_g} dias · R${orcamento_g}/pessoa\n\n"
                        f"📋 CHECKLIST PRÉ-VIAGEM (1 mês antes):\n"
                        f"[O que combinar antes de sair — decisões que precisam ser tomadas em grupo]\n\n"
                        f"💰 DIVISÃO DE CUSTOS:\n"
                        f"• Total estimado do grupo: R${orcamento_g * pessoas_g:,}\n"
                        f"• Como dividir passagens: [estratégia]\n"
                        f"• Como dividir hospedagem: [estratégia]\n"
                        f"• Como dividir refeições: [estratégia — cada um paga o seu ou divide?]\n"
                        f"• App recomendado para dividir contas: [nome + como usar]\n\n"
                        f"🏨 HOSPEDAGEM PARA GRUPO:\n"
                        f"[Opções ideais para {pessoas_g} pessoas — casa alugada, hostels, hotéis]\n"
                        f"[Estimativa de custo por pessoa por noite]\n\n"
                        f"🗓️ ROTEIRO DO GRUPO (resumido):\n"
                        f"[Dia a dia — atividades que funcionam bem para grupos de {pessoas_g}]\n\n"
                        f"⚠️ REGRAS DO GRUPO (combine antes):\n"
                        f"[As conversas difíceis que precisam acontecer antes — horários, gastos, preferências]\n\n"
                        f"🚗 TRANSPORTE DO GRUPO:\n"
                        f"[Como se locomover com {pessoas_g} pessoas — van, carros, apps]\n\n"
                        f"😤 COMO EVITAR CONFLITOS:\n"
                        f"[As 5 principais causas de conflito em viagens em grupo e como prevenir]\n\n"
                        f"👨‍💼 QUEM ORGANIZA O QUÊ:\n"
                        f"[Sugestão de divisão de tarefas — passagens, hotel, restaurantes, passeios]\n\n"
                        f"💡 DICA ESPECIAL PARA {perfil_g.upper()}:\n"
                        f"[Conselho específico para esse tipo de grupo]"
                    )
                    res = viagem_ia(prompt)
                    salvar_roteiro("Viagem em Grupo", destino_g, res)
                    st.session_state['grupo_temp'] = res
                    st.markdown(f"<div class='card-dark'>{res}</div>", unsafe_allow_html=True)
            else:
                st.warning("Informe o destino.")

        if st.session_state.get('grupo_temp'):
            col_dl, col_sv = st.columns(2)
            with col_dl:
                st.download_button("📋 Baixar plano (.txt)", data=st.session_state['grupo_temp'],
                    file_name=f"grupo_{destino_g.replace(' ','_') if 'destino_g' in dir() else 'viagem'}.txt",
                    mime="text/plain", use_container_width=True)
            with col_sv:
                if st.button("❤️ Salvar", key="sv_gr", use_container_width=True):
                    st.session_state.viagens_salvas.append({
                        'tipo': 'Viagem em Grupo', 'destino': destino_g if 'destino_g' in dir() else '',
                        'conteudo': st.session_state['grupo_temp'],
                        'data': datetime.now().strftime('%d/%m %H:%M'),
                    })
                    st.success("❤️ Salvo!")

    # ========================
    # VIAGENS SALVAS
    # ========================
    elif st.session_state.pagina == "Salvos":
        st.header("❤️ Viagens Salvas e Histórico")

        total  = len(st.session_state.historico_roteiros)
        salvos = len(st.session_state.viagens_salvas)
        tipos  = {}
        for r in st.session_state.historico_roteiros:
            tipos[r['tipo']] = tipos.get(r['tipo'], 0) + 1

        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f"<div class='stat-box'><div class='stat-numero'>{total}</div><div>Roteiros gerados</div></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='stat-box'><div class='stat-numero'>{salvos}</div><div>Viagens salvas</div></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='stat-box'><div class='stat-numero'>{tipos.get('Roteiro Completo',0)}</div><div>Roteiros completos</div></div>", unsafe_allow_html=True)
        c4.markdown(f"<div class='stat-box'><div class='stat-numero'>{tipos.get('Fim de Semana',0)}</div><div>FDS planejados</div></div>", unsafe_allow_html=True)

        if st.session_state.viagens_salvas:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### ❤️ Suas Viagens Favoritas")
            tipos_s = list(set(v['tipo'] for v in st.session_state.viagens_salvas))
            filtro  = st.selectbox("Filtrar:", ["Todos"] + tipos_s)

            viagens_f = [
                v for v in st.session_state.viagens_salvas
                if filtro == "Todos" or v['tipo'] == filtro
            ]

            for i, item in enumerate(reversed(viagens_f)):
                idx_real = len(st.session_state.viagens_salvas) - 1 - i
                with st.expander(f"❤️ [{item['tipo']}] ✈️ {item['destino']} — {item['data']}"):
                    st.markdown(f"<div class='card'>{item['conteudo']}</div>", unsafe_allow_html=True)
                    col_dl, col_del = st.columns([3, 1])
                    with col_dl:
                        st.download_button("📋 Baixar", data=item['conteudo'],
                            file_name=f"{item['tipo'].lower().replace(' ','_')}_{item['destino'].replace(' ','_')}.txt",
                            mime="text/plain", key=f"dl_salvo_{i}")
                    with col_del:
                        if st.button("🗑️", key=f"del_salvo_{i}"):
                            st.session_state.viagens_salvas.pop(idx_real)
                            st.rerun()
        else:
            st.info("Nenhuma viagem salva ainda. Gere roteiros e salve os favoritos!")

        if st.session_state.historico_roteiros:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### 📊 Histórico Completo")
            col_f, col_ex = st.columns([3, 1])
            with col_f:
                filtro_h = st.selectbox("Filtrar histórico:", ["Todos"] + list(tipos.keys()), key="filtro_hist")
            with col_ex:
                st.markdown("<br>", unsafe_allow_html=True)
                hist_txt = "\n\n".join(
                    f"[{r['data']}] {r['tipo']} — {r['destino']}\n{r['conteudo']}\n{'─'*40}"
                    for r in st.session_state.historico_roteiros
                )
                st.download_button("⬇️ Exportar TXT", data=hist_txt,
                    file_name="historico_viagens.txt", mime="text/plain")

            for i, item in enumerate(reversed(st.session_state.historico_roteiros)):
                if filtro_h != "Todos" and item['tipo'] != filtro_h:
                    continue
                idx_real = len(st.session_state.historico_roteiros) - 1 - i
                with st.expander(f"[{item['tipo']}] ✈️ {item['destino']} — {item['data']}"):
                    st.markdown(f"<div class='card'>{item['conteudo']}</div>", unsafe_allow_html=True)
                    col_sv, col_del = st.columns([3, 1])
                    with col_sv:
                        if st.button("❤️ Salvar", key=f"sv_hist_{i}"):
                            st.session_state.viagens_salvas.append(item.copy())
                            st.success("Salvo!")
                    with col_del:
                        if st.button("🗑️", key=f"del_hist_{i}"):
                            st.session_state.historico_roteiros.pop(idx_real)
                            st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️ Limpar Todo o Histórico"):
                st.session_state.historico_roteiros = []
                st.rerun()

# --- RODAPÉ ---
st.markdown(
    "<div style='text-align:center;color:#999;font-size:0.8em;margin-top:60px;'>"
    "© 2026 Guia de Viagens IA — Roteiros Personalizados com IA · Quiz Com Prêmios"
    "</div>", unsafe_allow_html=True
)

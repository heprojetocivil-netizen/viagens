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

# --- NORMALIZA TABELAS DE FRASES (converte tabs em pipes, garante separador) ---
def normalizar_tabelas_frases(texto: str) -> str:
    """
    Garante que todas as tabelas de frases usem formato pipe markdown.
    Converte linhas com tabs em linhas com pipes.
    Injeta linha separadora |---|---| quando ausente (só após cabeçalho).
    """
    linhas = texto.split('\n')
    resultado = []
    aguardando_separador = False
    i = 0
    while i < len(linhas):
        linha = linhas[i]

        # Linha com tabs (formato errado): converte para pipes
        if '\t' in linha and not linha.strip().startswith('|'):
            partes = [p.strip() for p in linha.split('\t') if p.strip()]
            if len(partes) >= 2:
                linha = '| ' + ' | '.join(partes) + ' |'

        eh_linha_tabela = linha.strip().startswith('|') and linha.strip().endswith('|')
        eh_separador = '---' in linha and linha.strip().startswith('|')

        if eh_linha_tabela and not eh_separador:
            if aguardando_separador:
                # Esta é uma linha de dados após o cabeçalho — ok, já inserimos o separador
                resultado.append(linha)
            else:
                # Este é o cabeçalho — verifica se próxima linha tem separador
                resultado.append(linha)
                prox = linhas[i+1].strip() if i+1 < len(linhas) else ''
                # Converte próxima linha se for tab
                if '\t' in prox:
                    partes_prox = [p.strip() for p in prox.split('\t') if p.strip()]
                    prox = '| ' + ' | '.join(partes_prox) + ' |' if len(partes_prox) >= 2 else prox
                if not (prox.startswith('|---') or prox.startswith('| ---') or '---' in prox):
                    colunas = len([c for c in linha.split('|') if c.strip()])
                    resultado.append('|' + '|'.join(['---'] * colunas) + '|')
                aguardando_separador = True
        elif eh_separador:
            resultado.append(linha)
            aguardando_separador = True
        else:
            aguardando_separador = False
            resultado.append(linha)
        i += 1

    return '\n'.join(resultado)

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

    # NAVBAR — linha 1
    cols1 = st.columns(8)
    paginas_nav1 = [
        ("🏠","Home"),("🗺️","Roteiro"),("🇧🇷","Brasil"),("💰","Orcamento"),
        ("🗣️","Frases"),("🧳","Checklist"),("👥","Grupo"),("❤️","Salvos"),
    ]
    nomes_nav1 = {
        "Home":"Painel Principal","Roteiro":"Roteiro Completo","Brasil":"Fim de Semana no Brasil",
        "Orcamento":"Estimativa de Custos","Frases":"Frases Essenciais","Checklist":"Checklist de Viagem",
        "Grupo":"Viagem em Grupo","Salvos":"Viagens Salvas",
    }
    for i,(icone,pagina) in enumerate(paginas_nav1):
        if cols1[i].button(icone, key=f"nav1_{pagina}", help=nomes_nav1[pagina]):
            st.session_state.pagina = pagina; st.rerun()

    # NAVBAR — linha 2 (novos módulos)
    cols2 = st.columns(10)
    paginas_nav2 = [
        ("🌍","Destino"),("🗺","Mapa"),("💱","Moeda"),("🌤️","Clima"),
        ("🛡️","Seguranca"),("🏛️","Historia"),("📄","PDF"),("💸","Economizar"),
        ("🚫","Armadilha"),("🤝","Pessoas"),
    ]
    nomes_nav2 = {
        "Destino":"Guia Completo do Destino","Mapa":"Mapa dos Passeios",
        "Moeda":"Moeda e Câmbio","Clima":"Clima no Período",
        "Seguranca":"Segurança e Saúde","Historia":"Conheça o Destino",
        "PDF":"Gerar PDF da Viagem","Economizar":"Economizar Mais",
        "Armadilha":"Palavras Armadilha — Evite Micos",
        "Pessoas":"Como São as Pessoas — Guia de Relacionamento",
    }
    for i,(icone,pagina) in enumerate(paginas_nav2):
        if cols2[i].button(icone, key=f"nav2_{pagina}", help=nomes_nav2[pagina]):
            st.session_state.pagina = pagina; st.rerun()

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
        st.markdown("**Linha 1 — Planejamento principal:**")
        guia1 = {
            "🗺️ Roteiro Completo":       "Roteiro dia a dia completo para qualquer destino — horários, custos, restaurantes com nota, tempo de deslocamento e análise de orçamento",
            "🇧🇷 Fim de Semana no Brasil": "Destinos incríveis perto de você para viajar sem gastar muito",
            "💰 Estimativa de Custos":    "Planejamento financeiro da viagem — passagem, hotel, alimentação, passeios",
            "🗣️ Frases Essenciais":       "As frases mais importantes no idioma local — com pronúncia e dica cultural",
            "🧳 Checklist de Viagem":     "Lista completa do que levar de acordo com o destino e a estação do ano",
            "👥 Viagem em Grupo":         "Plano completo para viagem em grupo — divisão de custos e o que combinar antes",
            "❤️ Viagens Salvas":          "Seus roteiros favoritos organizados e prontos para consultar",
        }
        for aba, desc in guia1.items():
            st.markdown(f"**{aba}** — {desc}")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Linha 2 — Módulos avançados:**")
        guia2 = {
            "🌍 Guia do Destino":         "Tudo em um só lugar — clima, segurança, moeda, transporte, saúde, costumes, pratos típicos, festivais e apps",
            "🗺 Mapa dos Passeios":        "Organiza os pontos turísticos por bairro e proximidade com tempo de deslocamento entre cada um",
            "💱 Moeda e Câmbio":          "Câmbio estimado, quanto seu orçamento vale na moeda local e estratégia de pagamento (Wise, C6, espécie)",
            "🌤️ Clima no Período":         "Temperatura, chance de chuva e lista específica de roupas para aquele mês naquele destino",
            "🛡️ Segurança e Saúde":       "Nível de segurança, regiões tranquilas, vacinas, hospitais de referência e seguro viagem",
            "🏛️ Conheça o Destino":       "História, monumentos, filmes gravados, curiosidades, lendas e apps indispensáveis",
            "📄 PDF da Viagem":           "Reformata qualquer roteiro em versão compacta para imprimir ou salvar no celular",
            "💸 Economizar Mais":         "Refaz o roteiro inteiro focando em reduzir custos — atrações gratuitas, hospedagem custo-benefício e análise de orçamento",
            "🚫 Palavras Armadilha":      "Palavras normais em português que são ofensivas ou obscenas no destino — e o inverso também",
            "🤝 Como São as Pessoas":     "Cumprimentos, presentes que ofendem, o que falar e evitar, etiqueta à mesa, dinâmica social e o que os locais adoram (e não gostam) no jeito brasileiro",
        }
        for aba, desc in guia2.items():
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
                    # Detecta se é destino internacional com euro
                    paises_euro = ["portugal","lisboa","porto","espanha","madrid","barcelona","frança","paris","itália","roma","milão","alemanha","berlim","grécia","atenas","holanda","amsterdam","bélgica","bruxelas","áustria","viena","irlanda","dublin"]
                    usa_euro = any(p in destino.lower() for p in paises_euro)
                    moeda_info = "O destino usa Euro (€). Mostre os preços em € e também a conversão estimada em R$ (considere câmbio de aproximadamente R$6 por €1). " if usa_euro else ""

                    prompt = (
                        f"Crie um roteiro completo de {dias} dias para {destino}.\n"
                        f"Saindo de: {origem or 'Brasil'}. Orçamento: R${orcamento}. "
                        f"Estilo: {perfil}. Pessoas: {pessoas}. Época: {epoca or 'qualquer'}.\n"
                        f"{moeda_info}\n\n"
                        f"INSTRUÇÕES IMPORTANTES:\n"
                        f"- Todos os preços são ESTIMATIVAS e podem variar — informe isso sempre\n"
                        f"- Inclua links para sites oficiais ou de compra de ingressos sempre que possível\n"
                        f"- Sugira restaurantes com nota média (ex: ⭐4.5) e faixa de preço (€/R$ por pessoa)\n"
                        f"- Informe o tempo de deslocamento entre pontos turísticos (ex: 15 min a pé, 20 min de metrô)\n"
                        f"- Ao final, calcule o orçamento total e avise se R${orcamento} é suficiente ou não\n"
                        f"- Inclua sugestão de restaurante por dia com nome real, prato recomendado e preço\n\n"
                        f"ESTRUTURA:\n\n"
                        f"✈️ ROTEIRO: {destino.upper()} — {dias} DIAS\n"
                        f"Estilo: {perfil} | {pessoas} | Orçamento: R${orcamento} total\n\n"
                        f"📋 INFORMAÇÕES ESSENCIAIS:\n"
                        f"• Melhor época para ir\n"
                        f"• Como chegar (passagem estimada de {origem or 'Brasil'})\n"
                        f"• Documentos necessários\n"
                        f"• Moeda e câmbio estimado\n"
                        f"• Fuso horário\n\n"
                        f"Para CADA dia use este formato:\n\n"
                        f"━━━━━━━━━━━━━━━━━━━━━\n"
                        f"📅 DIA [N] — [TEMA DO DIA]\n"
                        f"━━━━━━━━━━━━━━━━━━━━━\n"
                        f"☕ Manhã ([horário]):\n"
                        f"• [Local] — [dica exclusiva] — aprox. [preço] (⚠️ estimativa, pode variar)\n"
                        f"  🔗 Site/ingresso: [link oficial se existir]\n"
                        f"  🚶 Deslocamento até próximo ponto: [X min a pé / metrô / táxi]\n\n"
                        f"🍽️ Almoço ([horário]):\n"
                        f"• [Nome do restaurante] ⭐[nota] — [prato recomendado] — [faixa de preço] p/pessoa\n\n"
                        f"🌅 Tarde ([horário]):\n"
                        f"• [Local] — [dica] — [preço] (⚠️ estimativa)\n"
                        f"  🔗 [link se existir]\n"
                        f"  🚶 Deslocamento: [X min]\n\n"
                        f"🌙 Noite ([horário]):\n"
                        f"• [Jantar: restaurante ⭐nota] — [preço]\n"
                        f"• [Programa noturno opcional]\n\n"
                        f"💰 Gasto estimado do dia: [preço] p/pessoa (⚠️ estimativa)\n\n"
                        f"[Repita para todos os {dias} dias]\n\n"
                        f"🗺️ ORDEM SUGERIDA DOS PASSEIOS (para reduzir deslocamentos):\n"
                        f"[Liste os pontos turísticos em ordem geográfica para minimizar trajetos, com bairro de cada um]\n\n"
                        f"🍽️ TOP RESTAURANTES DO ROTEIRO:\n"
                        f"[Lista dos melhores mencionados com: nome, culinária, nota, faixa de preço, bairro]\n\n"
                        f"🏨 HOSPEDAGEM SUGERIDA:\n"
                        f"[3 opções: econômico, intermediário, confortável — com bairro e preço/noite]\n\n"
                        f"🚗 COMO SE LOCOMOVER:\n"
                        f"[Transporte local — app, metrô, carro, táxi — com custos e dicas]\n\n"
                        f"📊 RESUMO FINANCEIRO COMPLETO:\n"
                        f"Passagem: [preço]\n"
                        f"Hospedagem {dias} noites: [preço]\n"
                        f"Alimentação: [preço]\n"
                        f"Passeios e ingressos: [preço]\n"
                        f"Transporte local: [preço]\n"
                        f"Total estimado: [preço] p/pessoa\n\n"
                        f"⚠️ ANÁLISE DO ORÇAMENTO:\n"
                        f"[Calcule se R${orcamento} é suficiente para {pessoas}. Se não for, indique quanto falta e onde cortar]\n\n"
                        f"💡 DICAS DE OURO:\n"
                        f"[5 dicas que só quem conhece {destino} de verdade sabe]"
                    )
                    res = viagem_ia(prompt)
                    salvar_roteiro("Roteiro Completo", destino, res)
                    st.session_state['roteiro_temp'] = res
                    st.session_state['roteiro_destino'] = destino
                    st.session_state['roteiro_dias'] = dias
                    st.session_state['roteiro_orcamento'] = orcamento
                    st.session_state['roteiro_pessoas'] = pessoas
                    st.session_state['roteiro_epoca'] = epoca
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
                        f"REGRAS DE FORMATAÇÃO — siga rigorosamente:\n"
                        f"1. Use SEMPRE tabela markdown com pipes | para todas as seções\n"
                        f"2. NUNCA use tabulações (tab) para separar colunas\n"
                        f"3. O título da situação vai na linha imediatamente ANTES da tabela, sem linhas em branco entre eles\n"
                        f"4. Separe as seções com apenas UMA linha em branco\n\n"
                        f"FORMATO EXATO (copie esta estrutura):\n\n"
                        f"🍴 Nome da Situação\n"
                        f"| Português | {pais_f} | {'Pronúncia' if fonetica else ''} |\n"
                        f"|-----------|---------|{'---------' if fonetica else ''}|\n"
                        f"| frase em português | tradução | {'[pronúncia]' if fonetica else ''} |\n\n"
                        f"🚌 Próxima Situação\n"
                        f"| Português | {pais_f} | {'Pronúncia' if fonetica else ''} |\n"
                        f"|-----------|---------|{'---------' if fonetica else ''}|\n"
                        f"| frase | tradução | {'[pronúncia]' if fonetica else ''} |\n\n"
                        f"Mínimo 6 frases por situação. Repita para todas: {contexts}\n\n"
                        f"🆘 FRASES DE EMERGÊNCIA\n"
                        f"| Português | {pais_f} | {'Pronúncia' if fonetica else ''} |\n"
                        f"|-----------|---------|{'---------' if fonetica else ''}|\n"
                        f"[10 frases de emergência]\n\n"
                        f"📱 APPS DE TRADUÇÃO RECOMENDADOS:\n"
                        f"[Os melhores apps para {pais_f} — com ou sem internet]\n\n"
                        f"💡 DICA CULTURAL:\n"
                        f"[Como os locais reagem quando estrangeiros tentam falar o idioma]"
                    )
                    res = viagem_ia(prompt)
                    # Normaliza tabelas: converte tabs em pipes e garante cabeçalho separador
                    res = normalizar_tabelas_frases(res)
                    salvar_roteiro("Frases Essenciais", pais_f, res)
                    st.session_state['frases_temp'] = res
            else:
                st.warning("Informe o país ou idioma.")

        if st.session_state.get('frases_temp'):
            # Usa st.markdown nativo para renderizar tabelas markdown corretamente
            st.markdown("""
            <div style='background:linear-gradient(135deg,#F5F3FF,#EDE9FE);
            border:1px solid #C4B5FD;border-radius:16px;padding:20px 24px;margin-bottom:15px;'>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(st.session_state['frases_temp'])
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

    # ========================
    # GUIA COMPLETO DO DESTINO
    # ========================
    elif st.session_state.pagina == "Destino":
        st.header("🌍 Guia Completo do Destino")
        st.markdown("Tudo que você precisa saber antes de embarcar — em um só lugar.")

        destino_d = st.text_input("✈️ Destino:", placeholder="ex: Lisboa, Tóquio, Nova York, Marrocos...")
        epoca_d = st.text_input("📅 Período da viagem:", placeholder="ex: janeiro, julho, verão europeu...")

        if st.button("🌍 GERAR GUIA COMPLETO"):
            if destino_d.strip():
                with st.spinner(f"Reunindo tudo sobre {destino_d}..."):
                    prompt = (
                        f"Crie um guia completo e prático sobre {destino_d} para um viajante brasileiro.\n"
                        f"Período: {epoca_d or 'geral'}.\n\n"
                        f"FORMATO:\n\n"
                        f"🌍 GUIA COMPLETO — {destino_d.upper()}\n\n"
                        f"🌤️ CLIMA NO PERÍODO:\n"
                        f"• Temperatura média (máxima e mínima)\n"
                        f"• Chance de chuva e precipitação\n"
                        f"• Roupas recomendadas — liste peças específicas\n\n"
                        f"🛡️ SEGURANÇA:\n"
                        f"• Nível geral de segurança para turistas\n"
                        f"• Regiões mais tranquilas (onde ficar)\n"
                        f"• Áreas para evitar e por quê\n"
                        f"• Cuidados comuns (golpes frequentes, cuidados com pertences)\n\n"
                        f"💰 CUSTO DE VIDA:\n"
                        f"• Classificação: barato / médio / caro para brasileiros\n"
                        f"• Comparação com São Paulo\n"
                        f"• Onde economizar vs onde vale gastar mais\n\n"
                        f"🏛️ IDIOMA OFICIAL E FRASES ÚTEIS:\n"
                        f"• Idioma(s) falado(s)\n"
                        f"• 10 frases essenciais com pronúncia\n"
                        f"• Nível de inglês da população local\n\n"
                        f"💱 MOEDA, CÂMBIO E PAGAMENTO:\n"
                        f"• Moeda oficial e câmbio estimado em R$\n"
                        f"• Formas de pagamento aceitas\n"
                        f"• Dicas de câmbio (onde trocar, o que evitar)\n"
                        f"• Taxas de cartão no exterior\n\n"
                        f"🚖 TRANSPORTE PÚBLICO:\n"
                        f"• Meios disponíveis (metrô, ônibus, trem, ferry)\n"
                        f"• Apps de transporte locais\n"
                        f"• Custo médio por trajeto\n"
                        f"• Dicas para não errar\n\n"
                        f"⚡ TOMADAS E VOLTAGEM:\n"
                        f"• Tipo de tomada (A, B, C, F, G...)\n"
                        f"• Voltagem (110V/220V)\n"
                        f"• Precisa de adaptador? Qual modelo?\n\n"
                        f"📶 INTERNET, CHIP E ESIM:\n"
                        f"• Operadoras locais recomendadas\n"
                        f"• Preço médio de chip turista\n"
                        f"• eSIM — vale a pena? Quais apps usar\n"
                        f"• Qualidade da internet local\n\n"
                        f"🏥 SAÚDE:\n"
                        f"• Vacinas exigidas ou recomendadas para brasileiros\n"
                        f"• Seguro viagem — é obrigatório? Qual contratar?\n"
                        f"• Hospitais de referência para turistas\n"
                        f"• Farmácias e medicamentos básicos a levar\n\n"
                        f"📜 COSTUMES LOCAIS:\n"
                        f"• Etiqueta e boas maneiras locais\n"
                        f"• O que NUNCA fazer para não ofender\n"
                        f"• Horários culturais (almoço, jantar, lojas)\n"
                        f"• Gorjeta — como funciona\n\n"
                        f"🍽️ PRATOS TÍPICOS:\n"
                        f"• 5 pratos que valem a pena experimentar\n"
                        f"• Onde encontrá-los (tipo de restaurante)\n"
                        f"• Preço médio de cada prato\n\n"
                        f"🎉 EVENTOS E FESTIVAIS NO PERÍODO:\n"
                        f"• Festivais, feriados ou eventos durante {epoca_d or 'o ano'}\n"
                        f"• Impacto nos preços e disponibilidade\n\n"
                        f"📱 APLICATIVOS INDISPENSÁVEIS:\n"
                        f"• Apps de transporte, mapas, tradução, reservas e pagamento específicos para {destino_d}\n"
                        f"• Quais baixar antes de embarcar"
                    )
                    res = viagem_ia(prompt)
                    salvar_roteiro("Guia do Destino", destino_d, res)
                    st.session_state['destino_temp'] = res

        if st.session_state.get('destino_temp'):
            st.markdown(f"<div class='card'>{st.session_state['destino_temp']}</div>", unsafe_allow_html=True)
            col_dl, col_sv = st.columns(2)
            with col_dl:
                st.download_button("📋 Baixar (.txt)", data=st.session_state['destino_temp'],
                    file_name=f"guia_{destino_d.replace(' ','_') if 'destino_d' in dir() else 'destino'}.txt",
                    mime="text/plain", use_container_width=True)
            with col_sv:
                if st.button("❤️ Salvar", key="sv_destino", use_container_width=True):
                    st.session_state.viagens_salvas.append({'tipo':'Guia do Destino',
                        'destino': destino_d if 'destino_d' in dir() else '',
                        'conteudo': st.session_state['destino_temp'],
                        'data': datetime.now().strftime('%d/%m %H:%M')})
                    st.success("❤️ Salvo!")

    # ========================
    # MAPA DOS PASSEIOS
    # ========================
    elif st.session_state.pagina == "Mapa":
        st.header("🗺 Mapa dos Passeios")
        st.markdown("Ordem inteligente dos pontos turísticos para reduzir deslocamentos.")

        destino_m = st.text_input("✈️ Destino:", placeholder="ex: Lisboa, Paris, Roma...")
        pontos_m = st.text_area("📍 Liste os passeios que quer fazer:", height=120,
            placeholder="ex: Torre Eiffel, Louvre, Notre Dame, Montmartre, Palais Royal, Sacré-Cœur...")
        dias_m = st.number_input("📅 Quantos dias:", min_value=1, max_value=21, value=5)

        if st.button("🗺 ORGANIZAR MAPA DE PASSEIOS"):
            if destino_m.strip():
                with st.spinner("Organizando passeios por proximidade..."):
                    prompt = (
                        f"Organize estes passeios de {destino_m} na ordem mais eficiente para reduzir deslocamentos.\n"
                        f"Passeios: {pontos_m or 'os principais pontos turísticos'}. Dias disponíveis: {dias_m}.\n\n"
                        f"FORMATO:\n\n"
                        f"🗺 MAPA DE PASSEIOS — {destino_m.upper()}\n\n"
                        f"📍 DISTRIBUIÇÃO POR BAIRRO/REGIÃO:\n"
                        f"[Agrupe os pontos por proximidade geográfica]\n\n"
                        f"Para cada DIA, organize assim:\n\n"
                        f"📅 DIA [N] — BAIRRO/REGIÃO [NOME]\n"
                        f"• [Ponto 1] — [bairro] — [horário sugerido]\n"
                        f"  🚶 Até próximo: [X min a pé / Y min de metrô]\n"
                        f"• [Ponto 2] — [bairro]\n"
                        f"  🚶 Até próximo: [X min]\n"
                        f"[continue...]\n\n"
                        f"🚇 DICAS DE TRANSPORTE ENTRE OS DIAS:\n"
                        f"[Como ir de um bairro ao outro — metrô, ônibus, táxi]\n\n"
                        f"⏱️ TEMPO TOTAL DE DESLOCAMENTO ESTIMADO:\n"
                        f"[Quanto tempo por dia será gasto em transporte]\n\n"
                        f"💡 POR QUE ESSA ORDEM FAZ SENTIDO:\n"
                        f"[Explique a lógica geográfica]"
                    )
                    res = viagem_ia(prompt)
                    salvar_roteiro("Mapa de Passeios", destino_m, res)
                    st.session_state['mapa_temp'] = res

        if st.session_state.get('mapa_temp'):
            st.markdown(f"<div class='card-green'>{st.session_state['mapa_temp']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar (.txt)", data=st.session_state['mapa_temp'],
                file_name="mapa_passeios.txt", mime="text/plain")

    # ========================
    # MOEDA E CÂMBIO
    # ========================
    elif st.session_state.pagina == "Moeda":
        st.header("💱 Moeda e Câmbio")

        destino_mo = st.text_input("✈️ Destino:", placeholder="ex: Lisboa, Nova York, Tóquio...")
        orcamento_mo = st.number_input("💰 Orçamento em R$:", min_value=100, max_value=200000, value=5000, step=500)

        if st.button("💱 ANALISAR CÂMBIO E ESTRATÉGIA"):
            if destino_mo.strip():
                with st.spinner("Analisando..."):
                    prompt = (
                        f"Crie um guia prático de câmbio para {destino_mo} com orçamento de R${orcamento_mo}.\n\n"
                        f"💱 GUIA DE CÂMBIO — {destino_mo.upper()}\n\n"
                        f"• Moeda oficial e símbolo\n"
                        f"• Câmbio estimado atual (R$ para a moeda local)\n"
                        f"• Quanto R${orcamento_mo} equivale na moeda local\n\n"
                        f"💳 MELHORES FORMAS DE LEVAR DINHEIRO:\n"
                        f"• Cartão de crédito internacional (vantagens e taxas)\n"
                        f"• Cartão débito/pré-pago (Wise, Nomad, C6 — comparativo)\n"
                        f"• Dinheiro em espécie — quanto levar\n"
                        f"• O que NUNCA fazer (casas de câmbio no aeroporto, etc)\n\n"
                        f"💡 ESTRATÉGIA PARA R${orcamento_mo}:\n"
                        f"• Como dividir entre os meios de pagamento\n"
                        f"• Onde sacar dinheiro local sem pagar abusivo\n"
                        f"• Gorjeta — quanto e como"
                    )
                    res = viagem_ia(prompt)
                    salvar_roteiro("Moeda e Câmbio", destino_mo, res)
                    st.session_state['moeda_temp'] = res

        if st.session_state.get('moeda_temp'):
            st.markdown(f"<div class='card-yellow'>{st.session_state['moeda_temp']}</div>", unsafe_allow_html=True)

    # ========================
    # CLIMA
    # ========================
    elif st.session_state.pagina == "Clima":
        st.header("🌤️ Clima no Período da Viagem")

        col1, col2 = st.columns(2)
        with col1:
            destino_cl = st.text_input("✈️ Destino:", placeholder="ex: Lisboa, Amsterdã, Bangkok...")
        with col2:
            mes_cl = st.selectbox("📅 Mês da viagem:", ["Janeiro","Fevereiro","Março","Abril","Maio","Junho",
                "Julho","Agosto","Setembro","Outubro","Novembro","Dezembro"])

        if st.button("🌤️ VER CLIMA E ROUPAS"):
            if destino_cl.strip():
                with st.spinner("Consultando clima..."):
                    prompt = (
                        f"Informe o clima de {destino_cl} em {mes_cl} para um turista brasileiro.\n\n"
                        f"🌤️ CLIMA EM {destino_cl.upper()} — {mes_cl.upper()}\n\n"
                        f"🌡️ TEMPERATURA:\n"
                        f"• Média mínima e máxima\n"
                        f"• Temperatura da água (se litoral)\n"
                        f"• Sensação térmica (umidade)\n\n"
                        f"🌧️ CHUVA:\n"
                        f"• Chance de chuva (%)\n"
                        f"• Tipo de chuva (pancadas rápidas, chuva contínua, neve)\n"
                        f"• Impacto nos passeios\n\n"
                        f"👗 ROUPAS RECOMENDADAS — lista específica:\n"
                        f"[Liste peças de roupa concretas: ex: calça jeans, 2 camisetas, casaco impermeável...]\n\n"
                        f"👟 CALÇADOS:\n[Tipo ideal para o clima e terreno]\n\n"
                        f"🧴 ACESSÓRIOS ESSENCIAIS:\n[protetor solar, guarda-chuva, óculos, etc]\n\n"
                        f"⚠️ CUIDADOS ESPECIAIS:\n[o que o clima de {mes_cl} exige de atenção em {destino_cl}]"
                    )
                    res = viagem_ia(prompt)
                    salvar_roteiro("Clima", destino_cl, res)
                    st.session_state['clima_temp'] = res

        if st.session_state.get('clima_temp'):
            st.markdown(f"<div class='card-purple'>{st.session_state['clima_temp']}</div>", unsafe_allow_html=True)
            st.download_button("📋 Baixar (.txt)", data=st.session_state['clima_temp'],
                file_name="clima_viagem.txt", mime="text/plain")

    # ========================
    # SEGURANÇA E SAÚDE
    # ========================
    elif st.session_state.pagina == "Seguranca":
        st.header("🛡️ Segurança e Saúde")

        destino_sg = st.text_input("✈️ Destino:", placeholder="ex: Lisboa, Cairo, Medellín...")

        if st.button("🛡️ GERAR GUIA DE SEGURANÇA E SAÚDE"):
            if destino_sg.strip():
                with st.spinner("Analisando..."):
                    prompt = (
                        f"Crie um guia completo de segurança e saúde para turistas brasileiros em {destino_sg}.\n\n"
                        f"🛡️ SEGURANÇA — {destino_sg.upper()}\n\n"
                        f"📊 NÍVEL GERAL DE SEGURANÇA:\n[Classificação: seguro / atenção moderada / cuidado redobrado]\n\n"
                        f"✅ REGIÕES MAIS TRANQUILAS:\n[Bairros e áreas recomendadas para ficar e passear]\n\n"
                        f"⚠️ ÁREAS PARA EVITAR:\n[Bairros ou regiões com mais ocorrências — sem alarmismo]\n\n"
                        f"🔒 CUIDADOS COMUNS:\n"
                        f"• Golpes frequentes aplicados em turistas\n"
                        f"• Como proteger documentos e pertences\n"
                        f"• O que fazer em caso de roubo\n"
                        f"• Número de emergência local\n\n"
                        f"🏥 SAÚDE — {destino_sg.upper()}\n\n"
                        f"💉 VACINAS:\n[Exigidas, recomendadas e dispensáveis para brasileiros]\n\n"
                        f"🏥 HOSPITAIS DE REFERÊNCIA:\n[Nome e localização dos melhores para turistas]\n\n"
                        f"📋 SEGURO VIAGEM:\n[Obrigatório? Qual cobrir? Preço médio? Melhores empresas?]\n\n"
                        f"💊 MEDICAMENTOS BÁSICOS A LEVAR:\n[Lista de itens para farmácia de viagem]"
                    )
                    res = viagem_ia(prompt)
                    salvar_roteiro("Segurança e Saúde", destino_sg, res)
                    st.session_state['seg_temp'] = res

        if st.session_state.get('seg_temp'):
            st.markdown(f"<div class='card-orange'>{st.session_state['seg_temp']}</div>", unsafe_allow_html=True)
            col_dl, col_sv = st.columns(2)
            with col_dl:
                st.download_button("📋 Baixar (.txt)", data=st.session_state['seg_temp'],
                    file_name="seguranca_saude.txt", mime="text/plain", use_container_width=True)
            with col_sv:
                if st.button("❤️ Salvar", key="sv_seg", use_container_width=True):
                    st.session_state.viagens_salvas.append({'tipo':'Segurança e Saúde',
                        'destino': destino_sg if 'destino_sg' in dir() else '',
                        'conteudo': st.session_state['seg_temp'],
                        'data': datetime.now().strftime('%d/%m %H:%M')})
                    st.success("❤️ Salvo!")

    # ========================
    # HISTÓRIA DO DESTINO
    # ========================
    elif st.session_state.pagina == "Historia":
        st.header("🏛️ Conheça o Destino")
        st.markdown("Descubra a história, cultura e curiosidades antes de visitar.")

        destino_h = st.text_input("✈️ Destino:", placeholder="ex: Lisboa, Roma, Machu Picchu, Kyoto...")

        tema_h = st.multiselect("📚 O que você quer saber:", [
            "📜 Como a cidade surgiu",
            "👑 Personagens históricos importantes",
            "⚔️ Principais acontecimentos históricos",
            "🏰 Monumentos que marcaram essa história",
            "🎬 Filmes famosos gravados no local",
            "📚 Livros famosos ambientados na cidade",
            "🌟 Curiosidades que quase ninguém conhece",
            "🏆 Recordes ou títulos (Patrimônio Mundial, etc)",
            "💬 Uma lenda ou história curiosa da região",
            "📱 Aplicativos indispensáveis para esse destino",
        ], default=["📜 Como a cidade surgiu","🌟 Curiosidades que quase ninguém conhece","🏰 Monumentos que marcaram essa história"])

        if st.button("🏛️ CONHECER ESTE DESTINO"):
            if destino_h.strip():
                with st.spinner(f"Mergulhando na história de {destino_h}..."):
                    temas_txt = "\n".join(f"• {t}" for t in tema_h) if tema_h else "• História geral e curiosidades"
                    prompt = (
                        f"Crie um guia histórico e cultural envolvente sobre {destino_h}.\n"
                        f"Cubra os seguintes temas:\n{temas_txt}\n\n"
                        f"FORMATO:\n\n"
                        f"🏛️ CONHEÇA {destino_h.upper()}\n\n"
                        f"[Parágrafo de introdução vibrante — 3-4 linhas que faça a pessoa querer visitar]\n\n"
                        f"[Para cada tema selecionado, use o emoji e o título como cabeçalho, depois o conteúdo detalhado]\n\n"
                        f"💡 ANTES DE VISITAR, SAIBA:\n"
                        f"[3 fatos que vão transformar a experiência de visitar {destino_h}]"
                    )
                    res = viagem_ia(prompt)
                    salvar_roteiro("História do Destino", destino_h, res)
                    st.session_state['historia_temp'] = res

        if st.session_state.get('historia_temp'):
            st.markdown(f"<div class='card-purple'>{st.session_state['historia_temp']}</div>", unsafe_allow_html=True)
            col_dl, col_sv = st.columns(2)
            with col_dl:
                st.download_button("📋 Baixar (.txt)", data=st.session_state['historia_temp'],
                    file_name=f"historia_{destino_h.replace(' ','_') if 'destino_h' in dir() else 'destino'}.txt",
                    mime="text/plain", use_container_width=True)
            with col_sv:
                if st.button("❤️ Salvar", key="sv_historia", use_container_width=True):
                    st.session_state.viagens_salvas.append({'tipo':'História do Destino',
                        'destino': destino_h if 'destino_h' in dir() else '',
                        'conteudo': st.session_state['historia_temp'],
                        'data': datetime.now().strftime('%d/%m %H:%M')})
                    st.success("❤️ Salvo!")

    # ========================
    # GERAR PDF DA VIAGEM
    # ========================
    elif st.session_state.pagina == "PDF":
        st.header("📄 Gerar Resumo da Viagem para Levar")
        st.markdown("Gere um resumo compacto e organizado do seu roteiro — para imprimir ou salvar no celular.")

        if not st.session_state.historico_roteiros:
            st.info("Gere pelo menos um roteiro primeiro, depois volte aqui para criar o resumo.")
        else:
            roteiros_disponiveis = [f"{r['tipo']} — {r['destino']} ({r['data']})" for r in st.session_state.historico_roteiros[-10:]]
            roteiro_sel = st.selectbox("Escolha o roteiro:", roteiros_disponiveis)
            idx_sel = roteiros_disponiveis.index(roteiro_sel)
            roteiro_escolhido = st.session_state.historico_roteiros[-(len(roteiros_disponiveis) - idx_sel)]

            formato_pdf = st.radio("Formato:", ["Resumo compacto (1 página)","Versão completa para imprimir","Versão para celular (compacta e visual)"])

            if st.button("📄 GERAR RESUMO"):
                with st.spinner("Gerando versão para levar..."):
                    prompt = (
                        f"Reformate este roteiro de viagem no formato: {formato_pdf}.\n"
                        f"Destino: {roteiro_escolhido['destino']}.\n"
                        f"Roteiro original:\n{roteiro_escolhido['conteudo'][:3000]}\n\n"
                        f"INSTRUÇÕES:\n"
                        f"- Formato compacto: destaque APENAS o essencial (endereços, horários, preços, telefones)\n"
                        f"- Use emojis como marcadores visuais para facilitar a leitura rápida\n"
                        f"- Inclua uma seção 'EMERGÊNCIA' com números úteis e endereço do hotel\n"
                        f"- Organize por dia de forma clara\n"
                        f"- Adicione uma checklist rápida de itens para não esquecer no dia"
                    )
                    res = viagem_ia(prompt)
                    salvar_roteiro("Resumo PDF", roteiro_escolhido['destino'], res)
                    st.session_state['pdf_temp'] = res

        if st.session_state.get('pdf_temp'):
            st.markdown(f"<div class='card'>{st.session_state['pdf_temp']}</div>", unsafe_allow_html=True)
            col_dl, col_sv = st.columns(2)
            with col_dl:
                st.download_button("📄 Baixar resumo (.txt)", data=st.session_state['pdf_temp'],
                    file_name="resumo_viagem.txt", mime="text/plain", use_container_width=True)
            with col_sv:
                if st.button("❤️ Salvar", key="sv_pdf", use_container_width=True):
                    st.session_state.viagens_salvas.append({'tipo':'Resumo para Viagem',
                        'destino': roteiro_escolhido['destino'] if 'roteiro_escolhido' in dir() else '',
                        'conteudo': st.session_state['pdf_temp'],
                        'data': datetime.now().strftime('%d/%m %H:%M')})
                    st.success("❤️ Salvo!")

    # ========================
    # ECONOMIZAR MAIS
    # ========================
    elif st.session_state.pagina == "Economizar":
        st.header("💸 Economizar Mais")
        st.markdown("Refaz o roteiro reduzindo custos sem abrir mão da experiência.")

        col1, col2 = st.columns(2)
        with col1:
            destino_ec = st.text_input("✈️ Destino:", value=st.session_state.get('roteiro_destino',''), placeholder="ex: Lisboa, Paris...")
            dias_ec = st.number_input("📅 Dias:", min_value=2, max_value=21, value=st.session_state.get('roteiro_dias', 7))
            orcamento_ec = st.number_input("💰 Orçamento disponível (R$):", min_value=500, max_value=100000, value=st.session_state.get('roteiro_orcamento', 3000), step=500)
        with col2:
            pessoas_ec = st.selectbox("👥 Pessoas:", ["1 pessoa","2 pessoas","3-4 pessoas","5+ pessoas"],
                index=["1 pessoa","2 pessoas","3-4 pessoas","5+ pessoas"].index(st.session_state.get('roteiro_pessoas','1 pessoa')) if st.session_state.get('roteiro_pessoas') in ["1 pessoa","2 pessoas","3-4 pessoas","5+ pessoas"] else 0)
            epoca_ec = st.text_input("📅 Período:", value=st.session_state.get('roteiro_epoca',''), placeholder="ex: julho...")
            prioridade_ec = st.multiselect("🎯 O que NÃO abrir mão:", ["Hospedagem boa","Restaurantes","Passeios pagos","Transporte confortável"],
                default=["Passeios pagos"])

        if st.button("💸 GERAR ROTEIRO ECONÔMICO"):
            if destino_ec.strip():
                with st.spinner(f"Otimizando custos para {destino_ec}..."):
                    prompt = (
                        f"Crie um roteiro ECONÔMICO e otimizado para {destino_ec}.\n"
                        f"Dias: {dias_ec}. Orçamento: R${orcamento_ec}. Pessoas: {pessoas_ec}. Época: {epoca_ec or 'qualquer'}.\n"
                        f"O que não pode faltar: {', '.join(prioridade_ec) if prioridade_ec else 'flexível'}.\n\n"
                        f"FOCO: reduzir custos ao máximo sem perder qualidade de experiência.\n\n"
                        f"FORMATO:\n\n"
                        f"💸 ROTEIRO ECONÔMICO — {destino_ec.upper()}\n\n"
                        f"💡 ESTRATÉGIA DE ECONOMIA:\n"
                        f"[As 5 principais decisões que vão economizar mais dinheiro nessa viagem]\n\n"
                        f"🆓 ATRAÇÕES GRATUITAS OU QUASE:\n"
                        f"[Lista de museus gratuitos, parques, mirantes, eventos sem custo]\n\n"
                        f"Para cada dia:\n\n"
                        f"📅 DIA [N]\n"
                        f"• Manhã: [atividade gratuita ou barata] — R$[X]\n"
                        f"• Almoço: [opção econômica com nome real] — R$[X]/pessoa\n"
                        f"• Tarde: [atividade] — R$[X]\n"
                        f"• Jantar: [opção econômica] — R$[X]/pessoa\n"
                        f"💰 Total do dia: R$[X]/pessoa\n\n"
                        f"🏨 HOSPEDAGEM ECONÔMICA:\n"
                        f"[Melhores opções custo-benefício: hostels bons, apartamentos Airbnb por localização]\n\n"
                        f"🚇 TRANSPORTE ECONÔMICO:\n"
                        f"[Passes de transporte, quando vale a pena, como evitar táxi]\n\n"
                        f"📊 ORÇAMENTO FINAL ECONOMIZADO:\n"
                        f"Total estimado: R$[X] p/pessoa\n"
                        f"Economia vs roteiro padrão: aprox. R$[X]\n"
                        f"[Compare com o orçamento de R${orcamento_ec} e diga se é suficiente]\n\n"
                        f"⚠️ ONDE NÃO ECONOMIZAR:\n"
                        f"[Itens que vale gastar um pouco mais — seguro, transporte no aeroporto, etc]"
                    )
                    res = viagem_ia(prompt)
                    salvar_roteiro("Roteiro Econômico", destino_ec, res)
                    st.session_state['econom_temp'] = res

        if st.session_state.get('econom_temp'):
            st.markdown(f"<div class='card-green'>{st.session_state['econom_temp']}</div>", unsafe_allow_html=True)
            col_dl, col_sv = st.columns(2)
            with col_dl:
                st.download_button("📋 Baixar (.txt)", data=st.session_state['econom_temp'],
                    file_name="roteiro_economico.txt", mime="text/plain", use_container_width=True)
            with col_sv:
                if st.button("❤️ Salvar", key="sv_econom", use_container_width=True):
                    st.session_state.viagens_salvas.append({'tipo':'Roteiro Econômico',
                        'destino': destino_ec if 'destino_ec' in dir() else '',
                        'conteudo': st.session_state['econom_temp'],
                        'data': datetime.now().strftime('%d/%m %H:%M')})
                    st.success("❤️ Salvo!")

    # ========================
    # PALAVRAS ARMADILHA
    # ========================
    elif st.session_state.pagina == "Armadilha":
        st.header("🚫 Palavras Armadilha")
        st.markdown("Palavras ou expressões completamente normais em português — mas ofensivas, obscenas ou constrangedoras no país de destino. Saiba antes de viajar.")

        col1, col2 = st.columns(2)
        with col1:
            pais_arm = st.text_input("🌍 País de destino:", placeholder="ex: Portugal, Espanha, EUA, Japão, Argentina...")
        with col2:
            incluir_gestos = st.checkbox("Incluir gestos e linguagem corporal", value=True)
            incluir_nomes = st.checkbox("Incluir nomes próprios e marcas que soam mal", value=True)

        if st.button("🚫 DESCOBRIR AS ARMADILHAS"):
            if pais_arm.strip():
                with st.spinner(f"Pesquisando micos em {pais_arm}..."):
                    prompt = (
                        f"Crie um guia completo de palavras, expressões e comportamentos que são normais para "
                        f"brasileiros mas que podem ser ofensivos, obscenos ou constrangedores em {pais_arm}.\n\n"
                        f"SEJA ESPECÍFICO E HONESTO — este guia existe justamente para evitar micos reais.\n\n"
                        f"FORMATO:\n\n"
                        f"🚫 PALAVRAS ARMADILHA — BRASIL → {pais_arm.upper()}\n\n"
                        f"📖 INTRODUÇÃO:\n"
                        f"[1 parágrafo explicando por que isso acontece — diferenças históricas, evolução dos idiomas, colonização, etc.]\n\n"
                        f"⚠️ PALAVRAS DO PORTUGUÊS BRASILEIRO QUE CAUSAM PROBLEMA:\n\n"
                        f"Para cada palavra/expressão use este formato:\n"
                        f"🔴 **[PALAVRA EM PORTUGUÊS]**\n"
                        f"• O que significa para nós: [definição normal/inocente em pt-BR]\n"
                        f"• O que significa lá: [o que aquela palavra significa ou soa em {pais_arm}]\n"
                        f"• Nível de constrangimento: [leve 😅 / moderado 😬 / grave 😱]\n"
                        f"• Como evitar: [palavra substituta ou jeito certo de falar]\n\n"
                        f"[Inclua pelo menos 12-15 exemplos reais e conhecidos]\n\n"
                    )
                    if incluir_gestos:
                        prompt += (
                            f"👋 GESTOS E LINGUAGEM CORPORAL QUE ENGANAM:\n\n"
                            f"[Gestos comuns no Brasil que têm significado diferente ou ofensivo em {pais_arm}. "
                            f"Ex: jinha de ok, polegar, acenar, etc. Mesmo formato: gesto, o que significa aqui, o que significa lá, nível de problema.]\n\n"
                        )
                    if incluir_nomes:
                        prompt += (
                            f"😬 NOMES PRÓPRIOS E MARCAS QUE SOAM MAL:\n\n"
                            f"[Nomes comuns no Brasil — de pessoas, produtos ou lugares — que soam como algo ofensivo "
                            f"ou engraçado em {pais_arm}. Explique o porquê.]\n\n"
                        )
                    prompt += (
                        f"🔁 O INVERSO TAMBÉM VALE — PALAVRAS DELES QUE NOS SURPREENDEM:\n\n"
                        f"[Palavras comuns em {pais_arm} que soam ofensivas, engraçadas ou inadequadas para brasileiros. "
                        f"Para não se ofender à toa quando ouvir.]\n\n"
                        f"💡 DICA FINAL:\n"
                        f"[Conselho prático sobre como lidar quando escapar uma palavra errada — "
                        f"como se desculpar de forma adequada na cultura de {pais_arm}]"
                    )
                    res = viagem_ia(prompt,
                        "Seja completo e honesto. Este guia existe para ajudar brasileiros a evitar situações "
                        "constrangedoras reais. Inclua exemplos verídicos e conhecidos. Não omita por pudor — "
                        "o objetivo é exatamente informar sobre o que é delicado.")
                    salvar_roteiro("Palavras Armadilha", pais_arm, res)
                    st.session_state['armadilha_temp'] = res
            else:
                st.warning("Informe o país de destino.")

        if st.session_state.get('armadilha_temp'):
            st.markdown(f"<div class='card-orange'>{st.session_state['armadilha_temp']}</div>",
                unsafe_allow_html=True)
            col_dl, col_sv = st.columns(2)
            with col_dl:
                st.download_button("📋 Baixar (.txt)",
                    data=st.session_state['armadilha_temp'],
                    file_name=f"armadilhas_{pais_arm.replace(' ','_') if 'pais_arm' in dir() else 'destino'}.txt",
                    mime="text/plain", use_container_width=True)
            with col_sv:
                if st.button("❤️ Salvar", key="sv_armadilha", use_container_width=True):
                    st.session_state.viagens_salvas.append({
                        'tipo': 'Palavras Armadilha',
                        'destino': pais_arm if 'pais_arm' in dir() else '',
                        'conteudo': st.session_state['armadilha_temp'],
                        'data': datetime.now().strftime('%d/%m %H:%M'),
                    })
                    st.success("❤️ Salvo!")

            st.markdown("""
            <div style='background:#FFF7ED;border:1px solid #FDBA74;border-radius:10px;
            padding:12px 16px;font-size:0.82em;color:#92400E;margin-top:8px;'>
            💡 <strong>Dica:</strong> compartilhe esse guia com todo o grupo antes de viajar.
            Um mico evitado vale mais que qualquer roteiro.
            </div>
            """, unsafe_allow_html=True)

    # ========================
    # COMO SÃO AS PESSOAS
    # ========================
    elif st.session_state.pagina == "Pessoas":
        st.header("🤝 Como São as Pessoas")
        st.markdown("Guia de relacionamento social — como cumprimentar, o que ofende, o que agrada, como funciona a dinâmica com estrangeiros.")

        col1, col2 = st.columns(2)
        with col1:
            pais_pe = st.text_input("🌍 País de destino:", placeholder="ex: Japão, Portugal, Alemanha, Marrocos...")
            contexto_pe = st.multiselect("Situações que você vai viver:", [
                "Ir à casa de alguém","Jantar com locais","Ambiente de trabalho/negócios",
                "Bares e baladas","Fazer amizades na rua","Compras e mercado",
                "Transporte público","Visitar família local","Encontros românticos",
            ], default=["Ir à casa de alguém","Jantar com locais","Fazer amizades na rua"])
        with col2:
            perfil_pe = st.selectbox("Seu perfil de viajante:", [
                "Turista passando alguns dias","Vai visitar amigos ou conhecidos",
                "Viagem de negócios","Vai morar ou ficar por meses",
                "Intercâmbio ou estudo","Encontro romântico / namoro à distância",
            ])

        if st.button("🤝 GERAR GUIA DE RELACIONAMENTO"):
            if pais_pe.strip():
                with st.spinner(f"Preparando guia de relacionamento para {pais_pe}..."):
                    contextos_txt = ", ".join(contexto_pe) if contexto_pe else "situações gerais"
                    prompt = (
                        f"Crie um guia completo e honesto sobre como são as pessoas de {pais_pe} "
                        f"e como um brasileiro deve se relacionar com elas.\n"
                        f"Perfil do viajante: {perfil_pe}. Situações: {contextos_txt}.\n\n"
                        f"FORMATO:\n\n"
                        f"🤝 COMO SÃO AS PESSOAS DE {pais_pe.upper()}\n\n"
                        f"🧠 PERSONALIDADE GERAL:\n"
                        f"[Como as pessoas desse país são em geral — reservadas ou abertas, formais ou informais, "
                        f"desconfiadas ou receptivas com estrangeiros, diretas ou indiretas. "
                        f"Compare com o jeito brasileiro para facilitar o entendimento.]\n\n"
                        f"👋 CUMPRIMENTOS — COMO SE FAZ:\n"
                        f"• Entre homens: [aperto de mão, abraço, beijo, reverência, etc — e quando cada um é adequado]\n"
                        f"• Entre mulheres: [idem]\n"
                        f"• Homem cumprimentando mulher: [o que fazer e o que NUNCA fazer]\n"
                        f"• Em ambiente formal vs informal: [diferença]\n"
                        f"• Com idosos: [como tratar com respeito]\n"
                        f"• Com crianças: [pode tocar, fazer carinha, etc?]\n\n"
                        f"🏠 IR À CASA DE ALGUÉM — REGRAS DE OURO:\n"
                        f"• Deve-se levar algo? O quê? [seja específico — vinho, doce, o quê exatamente]\n"
                        f"• Flores: pode? Qual tipo? Qual cor? [algumas cores são luto em certos países]\n"
                        f"• Pontualidade: chegar no horário exato, adiantado ou atrasado?\n"
                        f"• Ao entrar: tira o sapato? Espera ser convidado a sentar?\n"
                        f"• À mesa: espera todos servirem? Elogia a comida? Recusa algo se não gostar?\n"
                        f"• Quanto tempo ficar após o jantar? Quando é hora de ir embora?\n"
                        f"• O que mandar depois: mensagem de agradecimento? É esperado?\n\n"
                        f"🎁 PRESENTES — O QUE OFENDE SEM QUERER:\n"
                        f"[Lista do que NUNCA dar de presente e por quê — flores de determinada cor, faca, relógio, "
                        f"número de itens, etc. Seja específico para {pais_pe}.]\n\n"
                        f"💬 CONVERSAS — O QUE FALAR E O QUE EVITAR:\n"
                        f"• Assuntos que quebram o gelo facilmente com locais de {pais_pe}\n"
                        f"• Assuntos TABU que devem ser evitados completamente\n"
                        f"• Perguntas que parecem inocentes mas ofendem\n"
                        f"• Como os locais reagem quando um brasileiro fala muito ou faz muitas perguntas pessoais\n\n"
                        f"😊 O QUE OS LOCAIS DE {pais_pe.upper()} ADORAM NOS BRASILEIROS:\n"
                        f"[Características do jeito brasileiro que são bem recebidas — use isso a seu favor]\n\n"
                        f"😬 O QUE OS LOCAIS NÃO GOSTAM NO JEITO BRASILEIRO:\n"
                        f"[Comportamentos comuns para nós que incomodam ou causam estranheza lá — sem julgamento, só informação]\n\n"
                        f"🍽️ À MESA — ETIQUETA LOCAL:\n"
                        f"• Quem paga quando saem juntos?\n"
                        f"• Gorjeta: obrigatória, opcional ou ofensiva?\n"
                        f"• Falar com a boca cheia, cotovelo na mesa — o que é tolerado?\n"
                        f"• Tirar foto da comida: aceitável ou estranho?\n\n"
                        f"💑 RELACIONAMENTO ENTRE HOMENS E MULHERES:\n"
                        f"[Como é a dinâmica social — olhar nos olhos, tocar no braço, piropear, "
                        f"o que é flerte e o que é assédio na cultura local]\n\n"
                        f"🕐 PONTUALIDADE E TEMPO:\n"
                        f"[A cultura é pontual ou relaxada com horários? O que é insulto e o que é normal em questão de tempo?]\n\n"
                        f"📱 COMUNICAÇÃO DIGITAL:\n"
                        f"[WhatsApp é usado? Como respondem mensagens — rápido, devagar? "
                        f"Ligar sem avisar é ok? Rede social favorita para se conectar com locais?]\n\n"
                        f"🌟 DICA FINAL DO VIAJANTE EXPERIENTE:\n"
                        f"[1 comportamento que, se o brasileiro adotar, vai criar uma impressão muito positiva "
                        f"nos locais de {pais_pe} — algo específico e prático]"
                    )
                    res = viagem_ia(prompt,
                        "Seja honesto, específico e culturalmente preciso. Evite generalizações vagas. "
                        "O objetivo é preparar um brasileiro para interações sociais reais — não um guia turístico genérico.")
                    salvar_roteiro("Como São as Pessoas", pais_pe, res)
                    st.session_state['pessoas_temp'] = res
            else:
                st.warning("Informe o país de destino.")

        if st.session_state.get('pessoas_temp'):
            st.markdown(f"<div class='card'>{st.session_state['pessoas_temp']}</div>",
                unsafe_allow_html=True)
            col_dl, col_sv = st.columns(2)
            with col_dl:
                st.download_button("📋 Baixar (.txt)",
                    data=st.session_state['pessoas_temp'],
                    file_name=f"pessoas_{pais_pe.replace(' ','_') if 'pais_pe' in dir() else 'destino'}.txt",
                    mime="text/plain", use_container_width=True)
            with col_sv:
                if st.button("❤️ Salvar", key="sv_pessoas", use_container_width=True):
                    st.session_state.viagens_salvas.append({
                        'tipo': 'Como São as Pessoas',
                        'destino': pais_pe if 'pais_pe' in dir() else '',
                        'conteudo': st.session_state['pessoas_temp'],
                        'data': datetime.now().strftime('%d/%m %H:%M'),
                    })
                    st.success("❤️ Salvo!")

# --- RODAPÉ ---
st.markdown(
    "<div style='text-align:center;color:#999;font-size:0.8em;margin-top:60px;'>"
    "© 2026 Guia de Viagens IA — Roteiros Personalizados com IA · Quiz Com Prêmios"
    "</div>", unsafe_allow_html=True
)

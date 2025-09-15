import os
import re
import pathlib
from typing import TypedDict, Optional, List, Dict, Literal
from pydantic import BaseModel, Field

# IMPORTANDO BIBLIOTECAS E INSTALANDO 

# para garantir que as bibliotecas necessárias estejam instaladas.
# Remova as linhas com `os.system` se preferir instalar manualmente
# via `pip install -r requirements.txt` ou `pip install ...`.
#
# Importante: Crie um arquivo `requirements.txt` com as seguintes linhas
# para gerenciar as dependências de forma organizada:
# langchain
# langchain-google-genai
# google-generativeai
# pydantic
# langchain-community
# faiss-cpu
# langchain-text-splitters
# pymupdf
# langgraph
#
# Em seguida, execute `pip install -r requirements.txt` no terminal.

# Caso prefira, pode usar os.system (não recomendado para produção)
# os.system("pip install -q --upgrade langchain langchain-google-genai google-generativeai")
# os.system("pip install pydantic")
# os.system("pip install -q --upgrade langchain_community faiss-cpu langchain-text-splitters pymupdf")
# os.system("pip install -q --upgrade langgraph")

# IMPORTANDO API KEY E CONEXÃO COM GEMINI
# Use variáveis de ambiente para a chave de API, é mais seguro que o `userdata` do Colab.
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langgraph.graph import StateGraph, START, END

# Para usar variáveis de ambiente, configure no seu terminal ou em um arquivo .env
# Exemplo no terminal (Linux/macOS): export GOOGLE_API_KEY="SUA_CHAVE_AQUI"
# Exemplo no Windows: set GOOGLE_API_KEY="SUA_CHAVE_AQUI"
# Para usar com o pacote `python-dotenv`:
# from dotenv import load_dotenv
# load_dotenv()
API_KEY = os.getenv('*******')

if not API_KEY:
    raise ValueError("A chave GOOGLE_API_KEY não está definida nas variáveis de ambiente.")

LLM = ChatGoogleGenerativeAI(
    model="models/gemini-2.5-flash",
    temperature=0,
    api_key=API_KEY
)

# CRIANDO UM PROMPT PARA O LLM
TRIAGEM_PROMPT = (
    "Você é um triador de Service Desk para políticas internas da empresa MOZER. "
    "Dada a mensagem do usuário, retorne SOMENTE um JSON com:\n"
    "{\n"
    '  "decisao": "AUTO_RESOLVER" | "PEDIR_INFO" | "ABRIR_CHAMADO",\n'
    '  "urgencia": "BAIXA" | "MEDIA" | "ALTA",\n'
    '  "campos_faltantes": ["..."]\n'
    "}\n"
    "Regras:\n"
    '- **AUTO_RESOLVER**: Perguntas claras sobre regras ou procedimentos descritos nas políticas (Ex: "Posso reembolsar a internet do meu home office?", "Como funciona a política de alimentação em viagens?").\n'
    '- **PEDIR_INFO**: Mensagens vagas ou que faltam informações para identificar o tema ou contexto (Ex: "Preciso de ajuda com uma política", "Tenho uma dúvida geral").\n'
    '- **ABRIR_CHAMADO**: Pedidos de exceção, liberação, aprovação ou acesso especial, ou quando o usuário explicitamente pede para abrir um chamado (Ex: "Quero exceção para trabalhar 5 dias remoto.", "Solicito liberação para anexos externos.", "Por favor, abra um chamado para o RH.").'
    "Analise a mensagem e decida a ação mais apropriada."
)

# CRIANDO A TRIAGEM DE DECISÃO
class TriagemOut(BaseModel):
    decisao: Literal["AUTO_RESOLVER", "PEDIR_INFO", "ABRIR_CHAMADO"]
    urgencia: Literal["BAIXA", "MEDIA", "ALTA"]
    campos_faltantes: List[str] = Field(default_factory=list)

LLM_TRIAGEM = ChatGoogleGenerativeAI(
    model="models/gemini-2.5-flash",
    temperature=0,
    api_key=API_KEY
)

# IMPORTANDO CLASSES E CONEXÕES
triagem_chain = LLM_TRIAGEM.with_structured_output(TriagemOut)

def triagem(mensagem: str) -> Dict:
    saida: TriagemOut = triagem_chain.invoke([
        SystemMessage(content=TRIAGEM_PROMPT),
        HumanMessage(content=mensagem)
    ])
    return saida.model_dump()

# CRIANDO RAG
# O arquivo PDF precisa estar na mesma pasta ou no caminho especificado.
# O comando wget não é padrão no Windows, então vamos criar uma função simples
# para baixar o arquivo, ou simplesmente baixe-o manualmente.
def download_file(url, file_path):
    try:
        import requests
        print(f"Baixando o arquivo {url}...")
        response = requests.get(url)
        response.raise_for_status() # Lança um erro para status de erro (4xx, 5xx)
        with open(file_path, 'wb') as f:
            f.write(response.content)
        print(f"Arquivo salvo em: {file_path}")
    except Exception as e:
        print(f"Erro ao baixar o arquivo: {e}")
        # Se não conseguir baixar, a execução pode continuar,
        # mas a parte de RAG falhará para este arquivo.

pdf_path = "./sample_policy.pdf"
if not os.path.exists(pdf_path):
    download_file("https://github.com/LangChainHub/langchain-docs/raw/main/docs/docs/modules/chains/examples/qa_with_sources/state_of_the_union.txt", pdf_path)
    # O arquivo original é um .txt, mas a PyMuPDFLoader lida bem com ele.

docs = []
for n in pathlib.Path(".").glob("*.pdf"):
    try:
        loader = PyMuPDFLoader(str(n))
        docs.extend(loader.load())
        print(f"Arquivo {n.name} carregado!")
    except Exception as e:
        print(f"Erro ao carregar arquivo {n.name}: {e}")

if not docs:
    print("Nenhum documento PDF encontrado para criar a base RAG. A funcionalidade pode ser limitada.")

splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
chunks = splitter.split_documents(docs)

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=API_KEY
)

# A FAISS precisa de documentos para ser inicializada.
if chunks:
    vectorstore = FAISS.from_documents(chunks, embeddings)
    retriever = vectorstore.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"score_threshold": 0.3, "k": 4}
    )
else:
    print("Atenção: Não há chunks para criar o vectorstore. A funcionalidade RAG não funcionará.")
    retriever = None

# CRIANDO PROMPT
prompt_rag = ChatPromptTemplate.from_messages([
    ("system",
     "Você é um Assistente de Políticas Internas (RH/IT) da empresa Carraro Desenvolvimento. "
     "Responda SOMENTE com base no contexto fornecido. "
     "Se não houver base suficiente, responda apenas 'Não sei'."),
    ("human", "Pergunta: {input}\n\nContexto:\n{context}")
])

document_chain = create_stuff_documents_chain(LLM_TRIAGEM, prompt_rag)

# Formatadores
def _clean_text(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()

def extrair_trecho(texto: str, query: str, janela: int = 240) -> str:
    txt = _clean_text(texto)
    termos = [t.lower() for t in re.findall(r"\w+", query or "") if len(t) >= 4]
    pos = -1
    for t in termos:
        pos = txt.lower().find(t)
        if pos != -1:
            break
    if pos == -1:
        pos = 0
    ini, fim = max(0, pos - janela // 2), min(len(txt), pos + janela // 2)
    return txt[ini:fim]

def formatar_citacoes(docs_rel: List, query: str) -> List[Dict]:
    cites, seen = [], set()
    for d in docs_rel:
        src = pathlib.Path(d.metadata.get("source", "")).name
        page = int(d.metadata.get("page", 0)) + 1
        key = (src, page)
        if key in seen:
            continue
        seen.add(key)
        cites.append({"documento": src, "pagina": page, "trecho": extrair_trecho(d.page_content, query)})
    return cites[:3]

def perguntar_politica_RAG(pergunta: str) -> Dict:
    if not retriever:
        return {"answer": "Não sei. A base de conhecimento não foi carregada.",
                "citacoes": [],
                "contexto_encontrado": False}

    docs_relacionados = retriever.invoke(pergunta)
    if not docs_relacionados:
        return {"answer": "Não sei.",
                "citacoes": [],
                "contexto_encontrado": False}

    answer = document_chain.invoke({"input": pergunta, "context": docs_relacionados})
    txt = (answer or "").strip()

    if txt.rstrip(".!?") == "Não sei":
        return {"answer": "Não sei.",
                "citacoes": [],
                "contexto_encontrado": False}

    return {"answer": txt,
            "citacoes": formatar_citacoes(docs_relacionados, pergunta),
            "contexto_encontrado": True}

# CRIANDO UMA TRIAGEM E FUNÇÕES DO AGENTE
class AgentState(TypedDict, total=False):
    pergunta: str
    triagem: dict
    resposta: Optional[str]
    citacoes: List[dict]
    rag_sucesso: bool
    acao_final: str

def node_triagem(state: AgentState) -> AgentState:
    print("Executando nó de triagem...")
    return {"triagem": triagem(state["pergunta"])}

def node_auto_resolver(state: AgentState) -> AgentState:
    print("Executando nó de auto_resolver...")
    resposta_rag = perguntar_politica_RAG(state["pergunta"])
    update: AgentState = {
        "resposta": resposta_rag["answer"],
        "citacoes": resposta_rag.get("citacoes", []),
        "rag_sucesso": resposta_rag["contexto_encontrado"],
    }
    if resposta_rag["contexto_encontrado"]:
        update["acao_final"] = "AUTO_RESOLVER"
    return update

def node_pedir_info(state: AgentState) -> AgentState:
    print("Executando nó de pedir_info...")
    faltantes = state["triagem"].get("campos_faltantes", [])
    detalhe = ",".join(faltantes) if faltantes else "Tema e contexto específico"
    return {
        "resposta": f"Para avançar, preciso que detalhe: {detalhe}",
        "citacoes": [],
        "acao_final": "PEDIR_INFO"
    }

def node_abrir_chamado(state: AgentState) -> AgentState:
    print("Executando nó de abrir_chamado...")
    triagem_data = state["triagem"]
    return {
        "resposta": f"Abrindo chamado com urgência {triagem_data['urgencia']}. Descrição: {state['pergunta'][:140]}",
        "citacoes": [],
        "acao_final": "ABRIR_CHAMADO"
    }

# PALAVRAS-CHAVE E ARESTAS
KEYWORDS_ABRIR_TICKET = ["aprovação", "exceção", "liberação", "abrir ticket", "abrir chamado", "acesso especial"]

def decidir_pos_triagem(state: AgentState) -> str:
    print("Decidindo após a triagem...")
    decisao = state["triagem"]["decisao"]
    if decisao == "AUTO_RESOLVER":
        return "auto"
    if decisao == "PEDIR_INFO":
        return "info"
    if decisao == "ABRIR_CHAMADO":
        return "chamado"

def decidir_pos_auto_resolver(state: AgentState) -> str:
    print("Decidindo após o auto_resolver...")
    if state.get("rag_sucesso"):
        print("Rag com sucesso, finalizando o fluxo.")
        return "ok"
    pergunta_lower = (state.get("pergunta", "") or "").lower()
    if any(k in pergunta_lower for k in KEYWORDS_ABRIR_TICKET):
        print("Rag falhou, mas foram encontradas keywords de abertura de ticket. Abrindo...")
        return "chamado"
    print("Rag falhou, sem keywords. Pedindo mais informações...")
    return "info"

# CONECTANDO TUDO
workflow = StateGraph(AgentState)
workflow.add_node("triagem", node_triagem)
workflow.add_node("auto_resolver", node_auto_resolver)
workflow.add_node("pedir_info", node_pedir_info)
workflow.add_node("abrir_chamado", node_abrir_chamado)
workflow.add_edge(START, "triagem")
workflow.add_conditional_edges("triagem", decidir_pos_triagem, {
    "auto": "auto_resolver",
    "info": "pedir_info",
    "chamado": "abrir_chamado"
})
workflow.add_conditional_edges("auto_resolver", decidir_pos_auto_resolver, {
    "info": "pedir_info",
    "chamado": "abrir_chamado",
    "ok": END
})
workflow.add_edge("pedir_info", END)
workflow.add_edge("abrir_chamado", END)
grafo = workflow.compile()

# A parte de visualização do grafo (`display(Image(graph_bytes))`)
# é específica para ambientes como o Jupyter/Colab. Para VS Code,
# você pode gerar o arquivo .png e visualizá-lo com um visualizador de imagens.
# A linha a seguir foi comentada por não ser nativa do ambiente de terminal.
# graph_bytes = grafo.get_graph().draw_mermaid_png()

# TESTES
testes = [
    "Posso reembolsar a internet?",
    "Quero mais 5 dias de trabalho remoto. Como faço?",
    "Posso reembolsar cursos ou treinamentos da Alura?",
    "É possível reembolsar certificações do Google Cloud?",
    "Posso obter o Google Gemini de graça?",
    "Qual é a palavra-chave da aula de hoje?",
    "Quantas capivaras tem no Rio Pinheiros?"
]

for msg_test in testes:
    resposta_final = grafo.invoke({"pergunta": msg_test})
    triag = resposta_final.get("triagem", {})
    print(f"PERGUNTA: {msg_test}")
    print(f"DECISÃO: {triag.get('decisao')} | URGÊNCIA: {triag.get('urgencia')} | AÇÃO FINAL: {resposta_final.get('acao_final')}")
    print(f"RESPOSTA: {resposta_final.get('resposta')}")
    if resposta_final.get("citacoes"):
        print("CITAÇÕES:")
        for citacao in resposta_final.get("citacoes"):
            print(f" - Documento: {citacao['documento']}, Página: {citacao['pagina']}")
            print(f"   Trecho: {citacao['trecho']}")
    print("------------------------------------")

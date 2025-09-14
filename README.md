# Agentes de IA com ALURA e Google GEMINI
## Nesse projeto, conclui um curso na ALURA onde criei um AI que lê os arquivos PDF da empresa e responde o usuário abrindo um chamado ou auto resolvendo com base nas informações da empresa usando PYTHON. Confira:

### Da Triagem Inteligente ao Atendimento Automatizado 
Criei um Agente de Service Desk com LangChain e LangGraph
Recentemente, mergulhei no universo das Large Language Models (LLMs) para construir um projeto prático e super interessante: um agente de Service Desk capaz de otimizar o fluxo de atendimento em uma empresa. A ideia é automatizar a triagem de requisições internas, direcionando o usuário para a solução mais eficiente.

### Imagine o seguinte cenário: um colaborador tem uma dúvida sobre uma política da empresa. Em vez de abrir um chamado genérico e esperar, ele pode interagir com um agente que, em segundos, faz a triagem e decide a melhor ação.

### Como funciona?

O projeto é dividido em três etapas principais, usando bibliotecas poderosas como LangChain e LangGraph:
Na triagem Inteligente na primeira camada utiliza um LLM para analisar a intenção da mensagem do usuário. A partir de um prompt estruturado, ele classifica a requisição em três categorias:

* AUTO_RESOLVER: Para perguntas simples, que podem ser respondidas consultando a base de conhecimento.

* PEDIR_INFO: Quando a mensagem é vaga e precisa de mais detalhes para ser processada.

* ABRIR_CHAMADO: Para solicitações complexas, como pedidos de exceção ou liberação, que requerem a intervenção de um time humano.

 RAG (Retrieval-Augmented Generation): Se a decisão for "AUTO_RESOLVER", a requisição é direcionada para um fluxo de RAG. Ele busca em uma base de documentos (políticas internas) a resposta mais precisa para a pergunta do usuário e, o melhor, inclui citações com o documento e a página de onde a informação foi extraída. Isso garante transparência e confiança na resposta.

 Fluxo Dinâmico com LangGraph: A mágica por trás da orquestração é o LangGraph. Ele permite criar um "gráfico de estado" que guia a requisição através dos diferentes nós (triagem, auto-resolução, etc.). A beleza do LangGraph é que ele toma decisões dinâmicas. Por exemplo, se o RAG falhar em encontrar uma resposta, o fluxo pode ser redirecionado automaticamente para "ABRIR_CHAMADO" ou "PEDIR_INFO" com base na análise da mensagem original.

### Esse projeto é um excelente exemplo de como podemos ir além de prompts simples e criar agentes que agem de forma autônoma e inteligente. Ele não apenas resolve o problema do usuário mais rapidamente, mas também libera os times de RH e TI para focar em tarefas mais estratégicas.



### Obrigada por conferir meus projetos!

<img width="1920" height="1080" alt="Image" src="https://github.com/user-attachments/assets/d7264fae-8a04-4113-803a-565683e3853d" />

# Agentes de IA com ALURA e Google GEMINI

## Nesse projeto, conclui um curso na ALURA onde criei um AI que recebe uma pergunta lê os arquivos PDF da empresa e responde o usuário abrindo um chamado ou auto resolvendo com base nas informações da empresa usando PYTHON. Confira:

<img width="1920" height="1080" alt="Image" src="https://github.com/user-attachments/assets/d9c0eab0-3bf4-476b-aa12-e08b3fe4dfc0" />

### Da Triagem Inteligente ao Atendimento Automatizado 
Criei um Agente de Service Desk com LangChain e LangGraph
Recentemente, mergulhei no universo das Large Language Models (LLMs) para construir um projeto prático e super interessante: um agente de Service Desk capaz de otimizar o fluxo de atendimento em uma empresa. A ideia é automatizar a triagem de requisições internas, direcionando o usuário para a solução mais eficiente.

<img width="1920" height="1080" alt="Image" src="https://github.com/user-attachments/assets/05a50493-a4c8-4d81-a5db-1b16b638ddd8" />

### Imagine o seguinte cenário: um colaborador tem uma dúvida sobre uma política da empresa. Em vez de abrir um chamado genérico e esperar, ele pode interagir com um agente que, em segundos, faz a triagem e decide a melhor ação.

<img width="1920" height="1080" alt="Image" src="https://github.com/user-attachments/assets/02c88251-252d-449e-acb1-709d8e7c90e7" />

### Como funciona?

O projeto é dividido em três etapas principais, usando bibliotecas poderosas como LangChain e LangGraph:
Na triagem Inteligente na primeira camada utiliza um LLM para analisar a intenção da mensagem do usuário. A partir de um prompt estruturado, ele classifica a requisição em três categorias:

* AUTO_RESOLVER: Para perguntas simples, que podem ser respondidas consultando a base de conhecimento.

* PEDIR_INFO: Quando a mensagem é vaga e precisa de mais detalhes para ser processada.

* ABRIR_CHAMADO: Para solicitações complexas, como pedidos de exceção ou liberação, que requerem a intervenção de um time humano.
<img width="1920" height="1080" alt="Image" src="https://github.com/user-attachments/assets/87a8ed3e-adcb-4cb9-9076-0f966e0c6e7f" />
 RAG (Retrieval-Augmented Generation): Se a decisão for "AUTO_RESOLVER", a requisição é direcionada para um fluxo de RAG. Ele busca em uma base de documentos (políticas internas) a resposta mais precisa para a pergunta do usuário e, o melhor, inclui citações com o documento e a página de onde a informação foi extraída. Isso garante transparência e confiança na resposta.

 Fluxo Dinâmico com LangGraph: A mágica por trás da orquestração é o LangGraph. Ele permite criar um "gráfico de estado" que guia a requisição através dos diferentes nós (triagem, auto-resolução, etc.). A beleza do LangGraph é que ele toma decisões dinâmicas. Por exemplo, se o RAG falhar em encontrar uma resposta, o fluxo pode ser redirecionado automaticamente para "ABRIR_CHAMADO" ou "PEDIR_INFO" com base na análise da mensagem original.

<img width="415" height="480" alt="Image" src="https://github.com/user-attachments/assets/4fed1fcb-bfce-4c52-bfa9-e860b3282bf5" />

### Esse projeto é um excelente exemplo de como podemos ir além de prompts simples e criar agentes que agem de forma autônoma e inteligente. Ele não apenas resolve o problema do usuário mais rapidamente, mas também libera os times de RH e TI para focar em tarefas mais estratégicas.


<img width="1920" height="1080" alt="Image" src="https://github.com/user-attachments/assets/d2d7a980-10de-4dce-bacc-96f3826b69fc" />

### Obrigada por conferir meus projetos!

<img width="1920" height="1080" alt="Image" src="https://github.com/user-attachments/assets/92e9a926-7f09-4bf9-9a41-190def5ae05f" />

import asyncio
import os
import pdb
import signal
from dataclasses import dataclass
from time import sleep

import browser_use
from autogen_core import (
    MessageContext,
    RoutedAgent,
    SingleThreadedAgentRuntime,
    TopicId,
    TypeSubscription,
    message_handler,
    type_subscription,
)
from autogen_core.models import ChatCompletionClient, SystemMessage, UserMessage, ModelFamily
from autogen_core.tools import FunctionTool
from autogen_ext.models.azure import AzureAIChatCompletionClient
from autogen_ext.models.openai import OpenAIChatCompletionClient
from azure.core.credentials import AzureKeyCredential

from agents.agent_browser import browseit
from tools.file import convert_json_to_mkd, open_file

browser_tool = FunctionTool(browseit, description="Task assigned to the agent" )

# browser_close_tool = FunctionTool(close_browser, description="Close the browser")


@dataclass
class Message:
    content: str

scraping_planner_topic_type = "ScrapingTopicAgent"
browser_agent_topic_type = "BrowserAgent"
plan_validator_topic_type = "PlanValidatorAgent"
code_implement_topic_type = "CodeImplementerAgent"
executor_validator_topic_type = "ExecutorValidatorAgent"


@type_subscription(topic_type=browser_agent_topic_type)
class BrowserAgent(RoutedAgent):
    def __init__(self, model_client: OpenAIChatCompletionClient) -> None:
        super().__init__("A planner agent")
        self._system_message = SystemMessage(
            content=(
                "Você é o **WebPilot**, o agente inicial e sua interface principal para a interação web.\n"
                "Sua responsabilidade é interpretar as instruções de navegação web fornecidas pelo usuário e executá-las utilizando uma ferramenta de controle de browser avançada que gera um arquivo HAR.\n"
                "Ao finalizar a navegação, será criado um arquivo browser_requests.json. Nesse arquivo terá todo o historico de requisições e respostas\n"
                "Você possui acesso a uma ferramenta: **convert_json_to_mkd**que receberá o caminho do arquivo json e convertera o arquivo json em markdown com mesmo nome."
                "**Como usar a ferramenta `browser_tool`:**\n"
                "Esta ferramenta permite que você controle um \"browser com IA\". Você deve fornecer a ela as ações que deseja que o browser realize, baseadas nas instruções do usuário. As ações podem incluir:\n"
                "* Visitar uma URL específica.\n"
                "* Clicar em um elemento (você pode precisar identificar o elemento, talvez descrevendo-o ou usando um seletor básico se a ferramenta suportar).\n"
                "* Digitar texto em um campo e submeter um formulário.\n"
                "* Rolar a página.\n"
                "* Aguardar elementos carregarem.\n"
                "O objetivo é simular a navegação que o usuário faria para chegar aos dados que ele eventualmente quer capturar. A ferramenta irá automaticamente gerar o HAR para a sessão de navegação que você orquestrar.\n"
                "**Sua Tarefa:**\n"
                "1. Leia e compreenda a instrução de navegação fornecida pelo usuário.\n"
                "2. Traduza essa instrução em uma sequência de ações ou um objetivo claro .\n"
                "3. Chame a ferramenta `convert` com as instruções de navegação.\n"
                "4. Assim que a ferramenta retornar o resultado (o conteúdo do HAR ou um relatório de falha/sucesso da navegação), apresente esse resultado.\n"
                "**Instrução do Usuário:**\n"
                "[AQUI SERÁ INSERIDA A SOLICITAÇÃO DE NAVEGAÇÃO DO USUÁRIO EM LINGUAGEM NATURAL. Ex: \"Vá para 'lojaexemplo.com', procure por 'notebook', clique no primeiro resultado e depois vá para a aba de 'especificações'.\"]\n"
                "**Sua Resposta (após usar a ferramenta):**\n"
                "[Você usará a ferramenta `browser_tool` aqui. O resultado da ferramenta (o conteúdo do HAR ou um status) será o corpo da sua resposta.]\n"
                "**Considerações Importantes:**\n"
                "* Se a instrução do usuário for ambígua ou faltarem detalhes cruciais para a navegação, peça por clarificação antes de usar a ferramenta.\n"
                "* Reporte de forma clara qualquer erro ou falha que ocorra durante a execução da ferramenta `BrowseAndGenerateHAR` (ex: site inacessível, elemento não encontrado durante a navegação).\n"
                "* Seu objetivo é obter um HAR representativo da navegação que levaria aos dados de interesse do usuário.\n"
                "Após finalizar utilize a ferramenta: **convert_json_to_mkd** para converter o arquivo json em markdown. por default o nome do arquivo é browser_requests.json\n "
                "Use a ferramenta open_file para abrir o arquivo markdown e mande o conteudo para a llm.\n"
                f"{0}\n"
            )
        )
        self._model_client = model_client

    @message_handler
    async def handle_browser(self, message: Message, ctx: MessageContext) -> None:
        prompt = f"Siga as instruções do usuário: {message.content}"

        await browseit(message.content)
        file_content = convert_json_to_mkd('browser_requests.json')

        llm_result = await self._model_client.create(
            messages=[self._system_message, UserMessage(content=file_content, source=self.id.key)],
            cancellation_token=ctx.cancellation_token,
        )

        response = llm_result.content
        assert isinstance(response, str)
        await self.publish_message(Message(file_content), topic_id=TopicId(scraping_planner_topic_type, source=self.id.key))



@type_subscription(topic_type=scraping_planner_topic_type)
class ScrapingPlannerAgent(RoutedAgent):
    def __init__(self, model_client: ChatCompletionClient) -> None:
        super().__init__("A planner agent")
        self._system_message = SystemMessage(
            content=(
                "Você é o Agente 1, responsável por analisar o tráfego web registrado em um arquivo HAR e os requisitos do usuário para criar um plano detalhado de web scraping.\n"
                "Você recebeu o conteúdo de um arquivo HAR que registra a navegação em um site. Analise este HAR para entender a estrutura do site, as requisições feitas, os dados transferidos e identificar as URLs relevantes para a tarefa de scraping.\n"
                "Você também recebeu os requisitos do usuário, que especificam quais informações devem ser extraídas do site.\n"
                "Sua tarefa é gerar um plano técnico que o Agente 3 (Implementador) poderá seguir para escrever o código do scraper. O plano deve incluir:\n"
                "1.  **URLs de Início:** As URLs principais de onde o scraping deve começar.\n"
                "2.  **Navegação (se aplicável):** Passos para navegar pelas páginas (ex: paginação, seguir links).\n"
                "3.  **Identificação dos Dados:** Para cada tipo de dado a ser capturado (ex: nome do produto, preço, descrição):\n"
                    "* URL(s) onde este dado pode ser encontrado.\n"
                    "* O(s) método(s) recomendado(s) para localizar o elemento na página (ex: CSS Selector: `.nome-classe`, XPath: `//div[@id='algum-id']`, ou mencionar padrões se for via API/JSON no HAR). Justifique a escolha se necessário.\n"
                    "* Qual atributo ou conteúdo textual deve ser extraído do elemento.\n"
                "4.  **Estrutura de Dados Esperada:** Um exemplo ou descrição do formato final dos dados (ex: lista de dicionários, colunas CSV: 'Nome Produto', 'Preço').\n"
                "5.  **Considerações Especiais (se houver):** Problemas potenciais identificados no HAR (ex: conteúdo dinâmico via JS, requisições XHR importantes, necessidade de cookies/headers específicos).\n"
                "Considere a eficiência e a robustez ao criar o plano.\n"
                "**Conteúdo do HAR:**"
                "[COLE AQUI O CONTEÚDO DO ARQUIVO HAR - PODE SER TRUNCADO SE FOR MUITO GRANDE, COM OS TRECHOS MAIS RELEVANTES]\n"
                "**Requisitos do Usuário:**\n"
                "[COLE AQUI A DESCRIÇÃO DO USUÁRIO SOBRE O QUE ELE QUER CAPTURAR]\n"
                "**Seu Plano:**\n"
                "[GENERE O PLANO AQUI]\n"
            )
        )
        self._model_client = model_client

    @message_handler
    async def handle_extraction_planner(self, message: Message, ctx: MessageContext) -> None:
        prompt = f"Elavore um Plano para a extração de acordo com as descriçoes de  requisições e respostas HTTP {message.content}"
        llm_result = await self._model_client.create(
            messages=[self._system_message, UserMessage(content=prompt, source=self.id.key)],
            cancellation_token=ctx.cancellation_token
        )
        response = llm_result.content
        print(response)
        assert isinstance(response, str)
        await self.publish_message(Message(response),
                                   topic_id=TopicId(code_implement_topic_type, source=self.id.key))

@type_subscription(topic_type=code_implement_topic_type)
class CodeImplementerAgent(RoutedAgent):
    def __init__(self, model_client: ChatCompletionClient) -> None:
        super().__init__("A implementer code agent")
        self._system_message = SystemMessage(
            content=(
                "Você é o Agente 3, o implementador do código web scraper. Sua tarefa é escrever o código Python baseado no plano de scraping validado ou corrigir o código existente com base no feedback de execução e validação recebido.\n"
                "Você DEVE usar as informações fornecidas (Plano ou Feedback) para gerar ou corrigir o código Python.\n"
                "**Situação Atual:**\n"
                "[INDICA SE É A PRIMEIRA VEZ (BASEADO NO PLANO) OU SE ESTÁ RECEBENDO FEEDBACK PARA CORRIGIR]\n"
                "**Informação de Entrada (Plano Validado ou Feedback do Agente 4):**\n"
                "[COLE AQUI O PLANO VALIDADO OU O FEEDBACK DO AGENTE 4]\n"
                "Escreva o código Python completo para o web scraper. Use bibliotecas comuns como `requests`, `BeautifulSoup`, ou outras que julgar apropriadas para seguir o plano. O código deve implementar a lógica de navegação (se houver), extrair os dados conforme especificado no plano, e formatar a saída de acordo com a estrutura esperada.\n"
                "Se estiver recebendo feedback, analise-o cuidadosamente e aplique as correções NECESSÁRIAS no código anterior.\n"
                "Após gerar/corrigir o código, você deve indicar que ele está pronto e, usando suas ferramentas disponíveis, garantir que ele seja salvo no arquivo designado.\n"
                "**Seu Código Python:**\n"
                "```python\n"
                "# Importações necessárias\n"
                "# ...\n"
                "\n"
                "# Implementação do scraper baseado no plano/feedback\n"
                "# ...\n"
                "\n"
                "# Lógica de extração e estruturação dos dados\n"
                "# ...\n"
                "\n"
                "# Exemplo de saída (opcional, para clarear a estrutura)\n"
                "# ...\n"
                "```\n"
            )
        )
        self._model_client = model_client

    @message_handler
    async def handle_code_implementer(self, message: Message, ctx: MessageContext) -> None:
        prompt = f"Cria um web scraper seguindo o plano: {message.content}"
        pdb.set_trace()
        llm_result = await self._model_client.create(
            messages=[self._system_message, UserMessage(content=prompt, source=self.id.key)],
            cancellation_token=ctx.cancellation_token
        )
        response = llm_result.content
        print(response)
        assert isinstance(response, str)



_model_client =  AzureAIChatCompletionClient(
        model="gpt-4o-mini",
        endpoint=os.getenv('AZURE_ENDPOINT_URL'),
        credential=AzureKeyCredential(os.getenv('AZURE_ENPOINT_API_KEY')),
        model_info={
            "json_output": False,
            "function_calling": True,
            "vision": False,
            "family": "unknown",
            "structured_output": True,
        },
    )
runtime = SingleThreadedAgentRuntime()

async def main():
    await BrowserAgent.register(
        runtime,
        type=browser_agent_topic_type,
        factory=lambda: BrowserAgent(model_client=_model_client),
    )

    await ScrapingPlannerAgent.register(
        runtime,
        type=scraping_planner_topic_type,
        factory=lambda: ScrapingPlannerAgent(model_client=_model_client),
    )

    await CodeImplementerAgent.register(
        runtime,
        type=code_implement_topic_type,
        factory=lambda: CodeImplementerAgent(model_client=_model_client),
    )

    runtime.start()

    await runtime.publish_message(
        Message(content="vá para o site https://example.com e capture a informação principal."),
        topic_id=TopicId(browser_agent_topic_type, source="default"),
    )

    await runtime.stop_when_idle()



if __name__ == '__main__':
    asyncio.run(main())
import os
import logging
import json
import requests
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Obtenha a chave da API da Perplexity a partir das variáveis de ambiente ou substitua diretamente
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "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")
# Atualize o endpoint abaixo com o endpoint correto da API da Perplexity
# PERPLEXITY_ENDPOINT = "https://api.perplexity.ai/seu-endpoint"
PERPLEXITY_ENDPOINT = "https://www.perplexity.ai/settings/api"

class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)
    
    def handle(self, handler_input):
        speak_output = "Bem vindo ao Perplexity Skill! Qual a sua pergunta?"
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class GptQueryIntentHandler(AbstractRequestHandler):
    # Você pode manter o nome da intent ou renomear para PerplexityQueryIntent, conforme sua configuração no modelo de interação.
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("GptQueryIntent")(handler_input)
    
    def handle(self, handler_input):
        query = handler_input.request_envelope.request.intent.slots["query"].value
        
        # Chama a função que consulta a API da Perplexity
        resposta = generate_perplexity_response(query)
        
        if not resposta:
            speak_output = "Desculpe, não consegui obter uma resposta."
        else:
            speak_output = resposta
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("Você pode fazer outra pergunta ou dizer sair.")
                .response
        )

def generate_perplexity_response(query):
    try:
        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {"query": query}
        
        response = requests.post(PERPLEXITY_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()
        
        data = response.json()
        # Supondo que a resposta da API venha no campo "resposta"
        resposta = data.get("resposta", "Não foi possível obter uma resposta.")
        return resposta
    except Exception as e:
        logger.error("Erro ao chamar a API da Perplexity: %s", e)
        return None

class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)
    
    def handle(self, handler_input):
        speak_output = "Como posso te ajudar?"
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class CancelOrStopIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input)
                or ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))
    
    def handle(self, handler_input):
        speak_output = "Até logo!"
        return handler_input.response_builder.speak(speak_output).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)
    
    def handle(self, handler_input):
        # Realize aqui qualquer limpeza necessária.
        return handler_input.response_builder.response

class CatchAllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True
    
    def handle(self, handler_input, exception):
        logger.error(exception, exc_info=True)
        speak_output = "Desculpe, não consegui processar sua solicitação."
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(GptQueryIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()

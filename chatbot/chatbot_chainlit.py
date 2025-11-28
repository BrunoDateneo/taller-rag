"""
Chatbot RAG con Chainlit - Versión mínima

Este archivo contiene el código base para construir un chatbot RAG paso a paso.
Seguí los ejercicios del Bloque 4 para ir agregando funcionalidades.
"""

import os
import boto3
from typing import Any, Dict
import chainlit as cl

# TODO Ejercicio 3: Agregar logging básico
# Importá el módulo logging y configurá un logger aquí
# Ejemplo:
# import logging
# logging.basicConfig(...)
# logger = logging.getLogger(__name__)

# Configuración AWS
AWS_REGION = os.getenv("AWS_REGION", "us-west-2")
KNOWLEDGE_BASE_ID = os.getenv("BEDROCK_KB_ID", "7DUKWTRFX3")
MODEL_ARN = os.getenv("BEDROCK_MODEL_ARN", "us.deepseek.r1-v1:0")

session = boto3.Session(
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID", "ASIAQQABDU3JEIAOW6TC"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY", "ystr/f21uyhYeRX4BxE4NYr+tbOHL9PNXiCbuCT9"),
    aws_session_token=os.getenv("AWS_SESSION_TOKEN", "IQoJb3JpZ2luX2VjEPT//////////wEaCXVzLXdlc3QtMiJHMEUCIQCT0P9lAhnYrveXj1lDJXXPB9w8FmSN3dEdpZvpbnRXjgIgIo2QqcpUKiFbQoPhOsH54hkheaR9VihuNhvVrg11OwwqmwIIvf//////////ARAAGgwwMzQzNjIwNzQ4MzQiDOczoFbio+8ae9iukirvAUeXGfW5Wznc7Wl9mFtLlIhzegE9XK/ucxsCWvtnEcMf7LqqN8OHiP8IVAOJSCzgtcLwdMknQiQQKtKztvY4Y96uLRkODQ03o2MmefVwbMQImKXm6ArJ33PIeyELE0aOK9kDgg6Zp6g82lUj608tMcSuVVRTjcU2r3f2ulJ3N+SZHO0P7NzhN2U5LbGGI3wGVXmv7N2cAwqL9BqGr1oMYSYObeWWpx6SkzSwYC1spPyLYTvJEF7kfwfINIdcszeVIheW/KSYI+YZOvWmlYcaQxpVdjf7w4PV3jb0p/C7lJvKBeJE+hg3yWNKTxfGyrlCMN7yp8kGOp0BigMjQFaEFZ51mhhgq8YRo/FpXVjekESfbrOX6vGtUpX+8K8C/bagrw0btP7z96Me25evuBglcdHSF6A03iGcAAJAlFEedlPqiKRkeftn6rj58mnnvnhFWC4Zk/3znVK1c+7PRTBJCnrUQgOPhOSSZ1OW7tj8ZI56b/dG4O712oPpOJ3/9YDbsCu6BtOeFgicoNLXgNexni4DcI4Kdg==")
)

cliente = session.client("bedrock-agent-runtime", region_name=AWS_REGION)

# Prompt template
DEFAULT_PROMPT_TEMPLATE = """Eres un asistente educativo especializado en Retrieval-Augmented Generation (RAG) y sistemas de búsqueda semántica.
Tu rol es ayudar a los estudiantes a comprender conceptos relacionados con embeddings, búsqueda vectorial, chunking, similitud coseno y arquitecturas RAG.

Responde la pregunta del usuario usando ÚNICAMENTE la información de los resultados de búsqueda proporcionados del material del taller.

IMPORTANTE:
- Usa ÚNICAMENTE información de los resultados de búsqueda del material educativo
- Si no hay información suficiente en los resultados, responde: "No encontré una respuesta exacta en el material del taller disponible"
- No inventes ni fabriques información que no esté presente en los resultados
- Explica los conceptos de manera clara y educativa, ayudando a los estudiantes a entender los fundamentos de RAG

Pregunta del usuario:

$query$

Resultados de búsqueda:

$search_results$

$output_format_instructions$"""


def generar_con_prompt(pregunta: str, prompt_template: str = None, top_k: int = 4, max_tokens: int = 600, temperature: float = 0.2) -> Dict[str, Any]:
    """Genera una respuesta usando retrieve_and_generate de Bedrock."""
    # TODO Ejercicio 3: Agregar logging básico
    # Agregá un log antes de llamar a Bedrock, por ejemplo:
    # logger.info(f"📤 Enviando pregunta a Bedrock: {pregunta[:100]}...")
    
    if prompt_template is None:
        prompt_template = DEFAULT_PROMPT_TEMPLATE

    config = {
        "type": "KNOWLEDGE_BASE",
        "knowledgeBaseConfiguration": {
            "knowledgeBaseId": KNOWLEDGE_BASE_ID,
            "modelArn": MODEL_ARN,
            "retrievalConfiguration": {
                "vectorSearchConfiguration": {"numberOfResults": top_k}
            },
            "generationConfiguration": {
                "inferenceConfig": {
                    "textInferenceConfig": {
                        "maxTokens": max_tokens,
                        "temperature": temperature
                    }
                },
                "promptTemplate": {"textPromptTemplate": prompt_template}
            }
        }
    }

    respuesta = cliente.retrieve_and_generate(
        input={"text": pregunta},
        retrieveAndGenerateConfiguration=config
    )
    
    # TODO Ejercicio 3: Agregar logging básico
    # Agregá un log después de recibir la respuesta, por ejemplo:
    # logger.info("✅ Respuesta recibida de Bedrock")
    
    return respuesta


# TODO Ejercicio 2: Extraer y mostrar citas básicas
# Creá una función llamada `extraer_citas_completas()` que procese el campo `citations` 
# de la respuesta de Bedrock y extraiga:
# - El texto citado (span) de cada cita
# - Las referencias (fuentes) que respaldan cada cita
# - Las URIs de las fuentes
#
# Pista: la respuesta de Bedrock tiene una estructura como:
# {
#   "output": {"text": "..."},
#   "citations": [
#     {
#       "generatedResponsePart": {
#         "textResponsePart": {
#           "text": "texto citado",
#           "span": {"start": 0, "end": 50}
#         }
#       },
#       "retrievedReferences": [
#         {
#           "location": {"s3Location": {"uri": "s3://..."}},
#           "content": {"text": "contenido de la referencia"}
#         }
#       ]
#     }
#   ]
# }
#
# Ejemplo de estructura de retorno:
# [
#   {
#     "citation_index": 1,
#     "texto_citado": "...",
#     "span_start": 0,
#     "span_end": 50,
#     "referencias": [
#       {"source": "s3://...", "content": "..."}
#     ]
#   }
# ]


@cl.on_chat_start
async def on_chat_start():
    # TODO Ejercicio 3: Agregar logging básico
    # Agregá un log cuando se inicia una sesión, por ejemplo:
    # logger.info("🚀 Nueva sesión de chat iniciada")
    
    await cl.Message(
        content="Hola 👋 Soy el asistente educativo especializado en RAG. Puedes hacerme preguntas sobre RAG, embeddings, búsqueda vectorial y arquitecturas RAG."
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    # TODO Ejercicio 3: Agregar logging básico
    # Agregá un log cuando se recibe una pregunta, por ejemplo:
    # logger.info(f"💬 Nueva pregunta del usuario: {message.content}")
    
    try:
        respuesta = generar_con_prompt(message.content)
        texto = respuesta.get("output", {}).get("text", "<Sin respuesta>")
        
        # Enviar la respuesta principal
        await cl.Message(content=texto, author="Asistente RAG").send()
        
        # TODO Ejercicio 2: Extraer y mostrar citas básicas
        # Después de enviar la respuesta principal, extraé las citas usando la función
        # `extraer_citas_completas()` que vas a crear y mostrá las fuentes consultadas.
        # Por ahora podés mostrarlas como texto simple o lista de URIs.
        # Ejemplo:
        # citas_completas = extraer_citas_completas(respuesta)
        # if citas_completas:
        #     fuentes = []
        #     for cita in citas_completas:
        #         for ref in cita.get("referencias", []):
        #             fuentes.append(ref.get("source", ""))
        #     await cl.Message(content=f"Fuentes consultadas: {', '.join(set(fuentes))}", author="Asistente RAG").send()
        
        # TODO Ejercicio 4: Integrar componente JSX para citas interactivas
        # Una vez que tengas `extraer_citas_completas()` funcionando, reemplazá el código
        # anterior por la integración del componente JSX:
        # citas_completas = extraer_citas_completas(respuesta)
        # if citas_completas:
        #     citations_element = cl.CustomElement(
        #         name="Citations",
        #         props={"citations": citas_completas}
        #     )
        #     await cl.Message(
        #         content="",
        #         elements=[citations_element],
        #         author="Asistente RAG"
        #     ).send()
        
    except Exception as e:
        # TODO Ejercicio 3: Agregar logging básico
        # Agregá un log cuando ocurre un error, por ejemplo:
        # logger.error(f"❌ Error al procesar la pregunta: {str(e)}", exc_info=True)
        
        await cl.Message(content=f"❌ Error: {str(e)}", author="Sistema").send()

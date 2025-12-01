"""
Chatbot RAG con Chainlit
Implementación completa del chatbot que integra RAG con Amazon Bedrock y Chainlit.
"""

import os
import json
import logging
import boto3
from typing import Any, Dict, List, Tuple
import chainlit as cl


# ============================================================================
# Configuración de Logging
# ============================================================================

# Configurar logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chatbot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ============================================================================
# Configuración de AWS Bedrock
# ============================================================================

AWS_REGION = os.getenv("AWS_REGION", "us-west-2")
KNOWLEDGE_BASE_ID = os.getenv("BEDROCK_KB_ID", "7DUKWTRFX3")
MODEL_ARN = os.getenv("BEDROCK_MODEL_ARN", "us.deepseek.r1-v1:0")

# Configuración de credenciales AWS
# Usa el mismo perfil 'taller-rag' que se configura en los scripts de iac/
# Para configurarlo ejecutá: aws configure --profile taller-rag
# Esto mantiene consistencia con los scripts de infraestructura
session = boto3.Session(profile_name='taller-rag')

cliente = session.client(
    "bedrock-agent-runtime",
    region_name=AWS_REGION
)


# ============================================================================
# Prompt Template
# ============================================================================

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


# ============================================================================
# Funciones de RAG
# ============================================================================

def generar_con_prompt(
    pregunta: str,
    prompt_template: str = None,
    top_k: int = 4,
    max_tokens: int = 600,
    temperature: float = 0.2
) -> Dict[str, Any]:
    """
    Genera una respuesta usando retrieve_and_generate de Bedrock.

    Args:
        pregunta: La pregunta del usuario
        prompt_template: Template del prompt (opcional, usa DEFAULT_PROMPT_TEMPLATE si no se proporciona)
        top_k: Número de resultados a recuperar
        max_tokens: Máximo de tokens en la respuesta
        temperature: Controla la aleatoriedad/creatividad de la generación (0.0-1.0).
                     Valores bajos (0.1-0.3) producen respuestas más deterministas y precisas,
                     ideales para tareas que requieren exactitud. Valores altos (0.7-1.0) generan
                     respuestas más creativas y variadas. Para RAG educativo, valores bajos (0.2)
                     son recomendados para mantener precisión y coherencia con el contexto recuperado.

    Returns:
        Diccionario con la respuesta de la API
    """
    # Usar template por defecto si no se proporciona uno
    if prompt_template is None:
        prompt_template = DEFAULT_PROMPT_TEMPLATE

    # Configuración de recuperación
    retrieval_config = {
        "vectorSearchConfiguration": {
            "numberOfResults": top_k
        }
    }

    # Configuración base
    config = {
        "type": "KNOWLEDGE_BASE",
        "knowledgeBaseConfiguration": {
            "knowledgeBaseId": KNOWLEDGE_BASE_ID,
            "modelArn": MODEL_ARN,
            "retrievalConfiguration": retrieval_config,
            "generationConfiguration": {
                "inferenceConfig": {
                    "textInferenceConfig": {
                        "maxTokens": max_tokens,
                        "temperature": temperature
                    }
                }
            }
        }
    }

    # Agregar prompt de generación si se proporciona
    if prompt_template:
        config["knowledgeBaseConfiguration"]["generationConfiguration"]["promptTemplate"] = {
            "textPromptTemplate": prompt_template
        }

    # Parámetros de la llamada
    params = {
        "input": {
            "text": pregunta
        },
        "retrieveAndGenerateConfiguration": config
    }

    logger.info(f"📤 Enviando pregunta a Bedrock: {pregunta[:100]}...")
    logger.info(f"📤 Configuración: top_k={top_k}, max_tokens={max_tokens}, temperature={temperature}")

    # Realizar llamada a la API
    respuesta = cliente.retrieve_and_generate(**params)
    
    logger.info(f"✅ Respuesta recibida de Bedrock")
    logger.info(f"📥 Respuesta completa (JSON): {json.dumps(respuesta, indent=2, ensure_ascii=False)}")
    
    return respuesta


def extraer_citas_completas(respuesta: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extrae las citas completas con su contenido textual y información de spans de la respuesta de la API.
    Agrupa las referencias por cita (span) para evitar duplicados y mostrar la relación entre
    el texto generado y sus fuentes.

    Args:
        respuesta: Diccionario con la respuesta de retrieve_and_generate

    Returns:
        Lista de diccionarios con información de cada cita incluyendo:
        - 'texto_citado': El texto del span que está siendo citado
        - 'span_start': Posición inicial del span
        - 'span_end': Posición final del span
        - 'referencias': Lista de referencias que respaldan este span
    """
    citas = respuesta.get("citations", [])
    citas_completas = []
    
    logger.info(f"📋 Procesando {len(citas)} citas encontradas")
    
    if citas:
        output = respuesta.get("output", {})
        texto_completo = output.get("text", "")
        
        for idx, cita in enumerate(citas, start=1):
            # Obtener información del generatedResponsePart con spans
            generated_part = cita.get("generatedResponsePart", {})
            text_part = generated_part.get("textResponsePart", {})
            texto_citado = text_part.get("text", "")
            span = text_part.get("span", {})
            start = span.get("start", 0)
            end = span.get("end", len(texto_completo))
            
            logger.info(f"\n{'='*80}")
            logger.info(f"📄 Cita #{idx} (Span {start}-{end})")
            logger.info(f"   Texto citado (posiciones {start}-{end}):")
            logger.info(f"   {texto_citado[:200]}..." if len(texto_citado) > 200 else f"   {texto_citado}")
            logger.info(f"   Span completo: start={start}, end={end}")
            
            retrieved_refs = cita.get("retrievedReferences", [])
            logger.info(f"   Referencias recuperadas: {len(retrieved_refs)}")
            
            # Procesar todas las referencias de esta cita
            referencias = []
            for ref_idx, ref in enumerate(retrieved_refs, start=1):
                # Intentar obtener la URI desde location o metadata
                location = ref.get("location", {})
                metadata = ref.get("metadata", {})
                
                # Priorizar metadata, luego location
                fuente = (
                    metadata.get("x-amz-bedrock-kb-source-uri") or
                    location.get("s3Location", {}).get("uri") or
                    "Fuente desconocida"
                )
                
                # Extraer el contenido completo
                content = ref.get("content", {})
                contenido_texto = content.get("text", "")
                
                logger.info(f"   [{ref_idx}] Fuente: {fuente}")
                logger.info(f"       Contenido preview: {contenido_texto[:150]}..." if len(contenido_texto) > 150 else f"       Contenido: {contenido_texto}")
                
                if fuente and fuente != "Fuente desconocida" and contenido_texto:
                    referencias.append({
                        "source": fuente,
                        "content": contenido_texto
                    })
            
            # Agregar la cita con todas sus referencias agrupadas
            if referencias:
                citas_completas.append({
                    "citation_index": idx,
                    "texto_citado": texto_citado,
                    "span_start": start,
                    "span_end": end,
                    "referencias": referencias
                })
    
    logger.info(f"✅ Total de citas procesadas: {len(citas_completas)}")
    return citas_completas


def mostrar_generacion_simple(respuesta: Dict[str, Any]) -> Tuple[str, List[str]]:
    """
    Extrae el texto generado y las URIs de las fuentes de la respuesta de la API.
    Versión simplificada para compatibilidad.

    Args:
        respuesta: Diccionario con la respuesta de retrieve_and_generate

    Returns:
        Tupla con (texto_generado, lista_de_uris)
    """
    output = respuesta.get("output", {})
    texto = output.get("text", "<Sin respuesta>")

    # Extraer solo las URIs para compatibilidad
    citas_completas = extraer_citas_completas(respuesta)
    # Extraer todas las URIs de todas las referencias de todas las citas
    lista_uris = []
    for cita in citas_completas:
        referencias = cita.get("referencias", [])
        for ref in referencias:
            fuente = ref.get("source", "")
            if fuente and fuente not in lista_uris:
                lista_uris.append(fuente)

    return texto, lista_uris


# ============================================================================
# Handlers de Chainlit
# ============================================================================

PROMPT_TEMPLATE = os.getenv("CHAINLIT_PROMPT_TEMPLATE", DEFAULT_PROMPT_TEMPLATE)


@cl.on_chat_start
async def on_chat_start():
    """Se ejecuta cuando el usuario abre la sesión del chatbot. 
    Esta función es asíncrona gracias a 'async', lo que permite, junto con 'await', 
    que el programa siga respondiendo a otras tareas mientras espera que se envíe el mensaje de bienvenida.
    Sin 'async' y 'await', el servidor esperaría a que se complete el envío antes de poder hacer cualquier otra cosa."""
    logger.info(f"\n{'='*80}")
    logger.info(f"🚀 Nueva sesión de chat iniciada")
    logger.info(f"   Knowledge Base ID: {KNOWLEDGE_BASE_ID}")
    logger.info(f"   Model ARN: {MODEL_ARN}")
    logger.info(f"   AWS Region: {AWS_REGION}")
    logger.info(f"{'='*80}\n")
    
    await cl.Message(
        content=(
            "Hola 👋 Soy el asistente educativo especializado en RAG.\n\n"
            "Puedes hacerme preguntas sobre Retrieval-Augmented Generation, embeddings, "
            "búsqueda vectorial, chunking, similitud coseno y arquitecturas RAG. "
            "Citaré las fuentes del material del taller cuando estén disponibles."
        )
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    """Se ejecuta por cada mensaje del usuario."""
    pregunta = message.content
    
    logger.info(f"\n{'='*80}")
    logger.info(f"💬 Nueva pregunta del usuario: {pregunta}")
    logger.info(f"{'='*80}")
    
    # Mostrar indicador de procesamiento
    msg = cl.Message(content="Procesando tu pregunta...")
    await msg.send()

    try:
        # Generar respuesta usando RAG
        respuesta = generar_con_prompt(pregunta, PROMPT_TEMPLATE)
        
        # Extraer texto y citas completas
        texto, _ = mostrar_generacion_simple(respuesta)
        logger.info(f"📝 Texto generado ({len(texto)} caracteres): {texto[:200]}..." if len(texto) > 200 else f"📝 Texto generado: {texto}")
        
        citas_completas = extraer_citas_completas(respuesta)

        # Enviar respuesta principal
        await cl.Message(
            content=texto,
            author="Asistente RAG"
        ).send()

        # Enviar citas completas en formato desplegable si existen
        if citas_completas:
            logger.info(f"📤 Enviando {len(citas_completas)} citas al componente JSX")
            
            # Crear elemento personalizado JSX con información de spans
            citations_element = cl.CustomElement(
                name="Citations",
                props={"citations": citas_completas}
            )
            
            await cl.Message(
                content="",
                elements=[citations_element],
                author="Asistente RAG"
            ).send()
        else:
            logger.warning("⚠️ No se encontraron citas para esta respuesta")
            await cl.Message(
                content="⚠️ No se encontraron citas para esta respuesta.",
                author="Asistente RAG"
            ).send()
        
        logger.info(f"✅ Procesamiento completado exitosamente\n")

    except Exception as e:
        logger.error(f"❌ Error al procesar la pregunta: {str(e)}", exc_info=True)
        await cl.Message(
            content=f"❌ Error al procesar tu pregunta: {str(e)}",
            author="Sistema"
        ).send()


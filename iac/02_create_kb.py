#!/usr/bin/env python3
"""
Script para crear Knowledge Base en Bedrock usando S3 Vectors
Como Terraform aún no soporta S3 Vectors, usamos la API directamente
"""

import boto3
import json
import time
from botocore.exceptions import ClientError

def create_knowledge_base():
    """Crea la Knowledge Base en Bedrock con S3 Vectors"""
    
    # Configuración
    region = "us-west-2"
    account_id = "111111111111" # TODO: Cambiar por el account_id de tu cuenta de AWS
    bucket_name = "taller-rag-knowledge-base-us-west-2-{account_id}}"
    
    kb_name = "taller-rag-kb"
    kb_description = "Knowledge base de bedrock con las transcripciones de clases de taller-rag"
    role_name = "taller-rag-knowledge-base-role"
    embedding_model = "amazon.titan-embed-text-v2:0"
    vector_dimension = 1024
    
    # Cliente de Bedrock
    session = boto3.session.Session(profile_name='taller-rag')
    bedrock_client = session.client('bedrock-agent', region_name=region)
    
    try:
        print("Creando Knowledge Base en Bedrock...")
        
        # Verificar que existe el vector bucket
        try:
            with open("vector_bucket_info.json", "r") as f:
                vector_info = json.load(f)
            vector_bucket_name = vector_info['vector_bucket_name']
            index_name = vector_info['vector_index_name']
            print(f"Usando Vector Bucket existente: {vector_bucket_name}")
            print(f"Usando indice existente: {index_name}")
        except FileNotFoundError:
            print("No se encontro vector_bucket_info.json")
            print("Ejecuta primero: python 01_create_vector_bucket.py")
            return None
        
        # Crear Knowledge Base
        kb_response = bedrock_client.create_knowledge_base(
            name=kb_name,
            description=kb_description,
            roleArn=f"arn:aws:iam::{account_id}:role/{role_name}",
            knowledgeBaseConfiguration={
                "vectorKnowledgeBaseConfiguration": {
                    "embeddingModelArn": f"arn:aws:bedrock:{region}::foundation-model/{embedding_model}",
                    "embeddingModelConfiguration": {
                        "bedrockEmbeddingModelConfiguration": {
                            "dimensions": vector_dimension,
                            "embeddingDataType": "FLOAT32"
                        }
                    }
                },
                "type": "VECTOR"
            },
            storageConfiguration={
                "type": "S3_VECTORS",
                "s3VectorsConfiguration": {
                    "indexArn": f"arn:aws:s3vectors:{region}:{account_id}:bucket/{vector_bucket_name}/index/{index_name}"
                }
            },
            tags={
                "Name": kb_name,
                "Environment": "production",
                "Purpose": "transcripciones-clases"
            }
        )
        
        knowledge_base_id = kb_response['knowledgeBase']['knowledgeBaseId']
        print(f"Knowledge Base creada: {knowledge_base_id}")
        
        # Mostrar información
        print("\n" + "="*60)
        print("INFORMACION DE LA KNOWLEDGE BASE")
        print("="*60)
        print(f"Knowledge Base ID: {knowledge_base_id}")
        print(f"Knowledge Base ARN: arn:aws:bedrock:{region}:{account_id}:knowledge-base/{knowledge_base_id}")
        print(f"Vector Bucket: {vector_bucket_name}")
        print(f"Indice Vectorial: {index_name}")
        print(f"Region: {region}")
        
        # Guardar información en archivo
        kb_info = {
            "knowledge_base_id": knowledge_base_id,
            "knowledge_base_arn": f"arn:aws:bedrock:{region}:{account_id}:knowledge-base/{knowledge_base_id}",
            "vector_bucket_name": vector_bucket_name,
            "vector_index_name": index_name,
            "region": region,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open("kb_info.json", "w") as f:
            json.dump(kb_info, f, indent=2)
        
        print(f"\nInformacion guardada en: kb_info.json")
        print("\nKnowledge Base creada exitosamente!")
        
        return knowledge_base_id
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ConflictException':
            print("La Knowledge Base ya existe")
            # Intentar obtener el ID existente
            try:
                response = bedrock_client.list_knowledge_bases()
                for kb in response['knowledgeBaseSummaries']:
                    if kb['name'] == kb_name:
                        print(f"Knowledge Base existente: {kb['knowledgeBaseId']}")
                        return kb['knowledgeBaseId']
            except Exception as list_error:
                print(f"Error listando Knowledge Bases: {list_error}")
        else:
            print(f"Error creando Knowledge Base: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado: {e}")
        return None

if __name__ == "__main__":
    create_knowledge_base()

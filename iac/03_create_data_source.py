#!/usr/bin/env python3
"""
Script para crear Data Source en la Knowledge Base de Bedrock
"""

import boto3
import json
import time
from botocore.exceptions import ClientError

def load_kb_info():
    """Carga la información de la Knowledge Base desde kb_info.json"""
    try:
        with open("kb_info.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("No se encontro kb_info.json. Ejecuta primero 02_create_kb.py")
        return None
    except Exception as e:
        print(f"Error cargando kb_info.json: {e}")
        return None

def create_data_source():
    """Crea el Data Source en la Knowledge Base"""
    
    # Cargar información de la KB
    kb_info = load_kb_info()
    if not kb_info:
        return None
    
    knowledge_base_id = kb_info['knowledge_base_id']
    bucket_name = "taller-rag-knowledge-base-us-west-2-{account_id}}"
    account_id = "111111111111" # TODO: Cambiar por el account_id de tu cuenta de AWS
    region = kb_info['region']
    data_source_name = "transcripciones-taller-rag"
    data_source_description = "Fuente de datos para transcripciones de clases de taller-rag"
    inclusion_prefixes = ["transcripciones/"]
    max_tokens = 2200
    overlap_percentage = 12
    
    # Cliente de Bedrock
    session = boto3.session.Session(profile_name='taller-rag')
    bedrock_client = session.client('bedrock-agent', region_name=region)
    
    try:
        print("Creando Data Source...")
        
        # Crear Data Source
        ds_response = bedrock_client.create_data_source(
            knowledgeBaseId=knowledge_base_id,
            name=data_source_name,
            description=data_source_description,
            dataSourceConfiguration={
                "type": "S3",
                "s3Configuration": {
                    "bucketArn": f"arn:aws:s3:::{bucket_name}",
                    "inclusionPrefixes": inclusion_prefixes
                }
            },
            vectorIngestionConfiguration={
                "chunkingConfiguration": {
                    "chunkingStrategy": "FIXED_SIZE",
                    "fixedSizeChunkingConfiguration": {
                        "maxTokens": max_tokens,
                        "overlapPercentage": overlap_percentage
                    }
                }
            },
            dataDeletionPolicy="DELETE"
        )
        
        data_source_id = ds_response['dataSource']['dataSourceId']
        print(f"Data Source creada: {data_source_id}")
        
        # Mostrar información
        print("\n" + "="*60)
        print("INFORMACION DEL DATA SOURCE")
        print("="*60)
        print(f"Data Source ID: {data_source_id}")
        print(f"Knowledge Base ID: {knowledge_base_id}")
        print(f"Bucket S3: {bucket_name}")
        print(f"Prefijo: transcripciones/")
        print(f"Chunking: FIXED_SIZE ({max_tokens} tokens, {overlap_percentage}% overlap)")
        print(f"Region: {region}")
        
        # Actualizar kb_info.json con el data source
        kb_info['data_source_id'] = data_source_id
        kb_info['data_source_created_at'] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        with open("kb_info.json", "w") as f:
            json.dump(kb_info, f, indent=2)
        
        print(f"\nInformacion actualizada en: kb_info.json")
        print("\nData Source creado exitosamente!")
        
        return data_source_id
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ConflictException':
            print("El Data Source ya existe")
            # Intentar obtener el ID existente
            try:
                response = bedrock_client.list_data_sources(knowledgeBaseId=knowledge_base_id)
                for ds in response['dataSourceSummaries']:
                    if ds['name'] == data_source_name:
                        print(f"Data Source existente: {ds['dataSourceId']}")
                        return ds['dataSourceId']
            except Exception as list_error:
                print(f"Error listando Data Sources: {list_error}")
        else:
            print(f"Error creando Data Source: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado: {e}")
        return None

if __name__ == "__main__":
    create_data_source()

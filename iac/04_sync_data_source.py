#!/usr/bin/env python3
"""
Script para sincronizar Data Source en la Knowledge Base de Bedrock
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
        print("No se encontro kb_info.json. Ejecuta primero 02_create_kb.py y 03_create_data_source.py")
        return None
    except Exception as e:
        print(f"Error cargando kb_info.json: {e}")
        return None

def check_ingestion_status(bedrock_client, knowledge_base_id, data_source_id, ingestion_job_id):
    """Verifica el estado del job de ingesta"""
    try:
        response = bedrock_client.get_ingestion_job(
            knowledgeBaseId=knowledge_base_id,
            dataSourceId=data_source_id,
            ingestionJobId=ingestion_job_id
        )
        
        status = response['ingestionJob']['status']
        return status
    except Exception as e:
        print(f"Error verificando estado: {e}")
        return "UNKNOWN"

def sync_data_source():
    """Inicia la sincronización del Data Source"""
    
    # Cargar información de la KB
    kb_info = load_kb_info()
    if not kb_info:
        return None
    
    knowledge_base_id = kb_info['knowledge_base_id']
    data_source_id = kb_info.get('data_source_id')
    region = kb_info['region']
    job_description = "Sincronizacion de transcripciones"
    monitor_interval = 10
    
    if not data_source_id:
        print("No se encontro data_source_id. Ejecuta primero 03_create_data_source.py")
        return None
    
    # Cliente de Bedrock
    session = boto3.session.Session(profile_name='taller-rag')
    bedrock_client = session.client('bedrock-agent', region_name=region)
    
    try:
        print("Iniciando sincronizacion...")
        
        # Iniciar job de sincronización
        sync_response = bedrock_client.start_ingestion_job(
            knowledgeBaseId=knowledge_base_id,
            dataSourceId=data_source_id,
            description=job_description
        )
        
        ingestion_job_id = sync_response['ingestionJob']['ingestionJobId']
        print(f"Job de sincronizacion iniciado: {ingestion_job_id}")
        
        # Mostrar información
        print("\n" + "="*60)
        print("INFORMACION DE LA SINCRONIZACION")
        print("="*60)
        print(f"Ingestion Job ID: {ingestion_job_id}")
        print(f"Knowledge Base ID: {knowledge_base_id}")
        print(f"Data Source ID: {data_source_id}")
        print(f"Region: {region}")
        
        # Actualizar kb_info.json con el job
        kb_info['last_ingestion_job_id'] = ingestion_job_id
        kb_info['last_sync_at'] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        with open("kb_info.json", "w") as f:
            json.dump(kb_info, f, indent=2)
        
        print(f"\nInformacion actualizada en: kb_info.json")
        
        # Opción para monitorear el progreso
        print("\n" + "="*60)
        print("MONITOREO DEL PROGRESO")
        print("="*60)
        print("Quieres monitorear el progreso de la sincronizacion? (s/n): ", end="")
        
        try:
            monitor = input().lower().strip()
            if monitor in ['s', 'si', 'sí', 'y', 'yes']:
                print("\nMonitoreando progreso... (Ctrl+C para salir)")
                
                while True:
                    status = check_ingestion_status(bedrock_client, knowledge_base_id, data_source_id, ingestion_job_id)
                    print(f"Estado actual: {status}")
                    
                    if status in ['COMPLETE', 'FAILED', 'CANCELLED']:
                        if status == 'COMPLETE':
                            print("Sincronizacion completada exitosamente!")
                        else:
                            print(f"Sincronizacion termino con estado: {status}")
                        break
                    
                    time.sleep(monitor_interval)
                    
        except KeyboardInterrupt:
            print("\n\nMonitoreo interrumpido por el usuario")
        
        print("\nJob de sincronizacion iniciado exitosamente!")
        
        return ingestion_job_id
        
    except ClientError as e:
        print(f"Error iniciando sincronizacion: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado: {e}")
        return None

if __name__ == "__main__":
    sync_data_source()

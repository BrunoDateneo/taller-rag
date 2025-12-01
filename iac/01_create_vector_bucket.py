#!/usr/bin/env python3
"""
Script para crear Vector Bucket en S3 Vectors
"""

import boto3
import json
import time
from botocore.exceptions import ClientError

def create_vector_bucket():
    """Crea el Vector Bucket en S3 Vectors"""
    
    # Configuración
    region = "us-west-2"
    vector_bucket_name = "taller-rag-vector-bucket"
    index_name = "taller-rag-vector-index"
    account_id = "111111111111" # TODO: Cambiar por el account_id de tu cuenta de AWS
    dimension = 1024
    distance_metric = "euclidean"
    data_type = "float32"
    
    # Cliente de S3 Vectors
    session = boto3.session.Session(profile_name='taller-rag')
    s3vectors_client = session.client('s3vectors', region_name=region)
    
    try:
        print("Creando Vector Bucket en S3 Vectors...")
        
        # Crear Vector Bucket
        bucket_response = s3vectors_client.create_vector_bucket(
            vectorBucketName=vector_bucket_name,
            encryptionConfiguration={
                "sseType": "AES256"
            }
        )
        
        print(f"Vector Bucket creado: {vector_bucket_name}")
        
        # Crear índice vectorial
        print("Creando índice vectorial...")
        
        index_response = s3vectors_client.create_index(
            vectorBucketName=vector_bucket_name,
            indexName=index_name,
            dataType=data_type,
            dimension=dimension,
            distanceMetric=distance_metric,
            metadataConfiguration={
                "nonFilterableMetadataKeys": ["AMAZON_BEDROCK_TEXT", "AMAZON_BEDROCK_METADATA"]
            }
        )
        
        print(f"Indice vectorial creado: {index_name}")
        
        # Mostrar información
        print("\n" + "="*60)
        print("INFORMACION DEL VECTOR BUCKET")
        print("="*60)
        print(f"Vector Bucket Name: {vector_bucket_name}")
        print(f"Vector Bucket ARN: arn:aws:s3vectors:{region}:{account_id}:bucket/{vector_bucket_name}")
        print(f"Indice Vectorial: {index_name}")
        print(f"Region: {region}")
        print(f"Dimension: {dimension}")
        print(f"Metrica de Distancia: {distance_metric}")
        
        # Guardar información en archivo
        vector_info = {
            "vector_bucket_name": vector_bucket_name,
            "vector_bucket_arn": f"arn:aws:s3vectors:{region}:{account_id}:bucket/{vector_bucket_name}",
            "vector_index_name": index_name,
            "dimension": dimension,
            "distance_metric": distance_metric,
            "region": region,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open("vector_bucket_info.json", "w") as f:
            json.dump(vector_info, f, indent=2)
        
        print(f"\nInformacion guardada en: vector_bucket_info.json")
        print("\nVector Bucket creado exitosamente!")
        
        return vector_bucket_name
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ConflictException':
            print("El Vector Bucket ya existe")
            # Intentar crear solo el índice
            try:
                print("Creando indice vectorial...")
                s3vectors_client.create_index(
                    vectorBucketName=vector_bucket_name,
                    indexName=index_name,
                    dataType=data_type,
                    dimension=dimension,
                    distanceMetric=distance_metric,
                    metadataConfiguration={
                        "nonFilterableMetadataKeys": ["AMAZON_BEDROCK_TEXT", "AMAZON_BEDROCK_METADATA"]
                    }
                )
                print(f"Indice vectorial creado: {index_name}")
                return vector_bucket_name
            except ClientError as index_error:
                if index_error.response['Error']['Code'] == 'ConflictException':
                    print("El indice vectorial ya existe")
                    return vector_bucket_name
                else:
                    print(f"Error creando indice vectorial: {index_error}")
                    return None
        else:
            print(f"Error creando Vector Bucket: {e}")
            return None
    except Exception as e:
        print(f"Error inesperado: {e}")
        return None

if __name__ == "__main__":
    create_vector_bucket()

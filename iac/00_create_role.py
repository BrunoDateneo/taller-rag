#!/usr/bin/env python3
"""
Script para crear el rol IAM necesario para la Knowledge Base de Bedrock
Este rol permite que Bedrock acceda a S3 y S3 Vectors
"""

import boto3
import json
import time
from botocore.exceptions import ClientError

def create_knowledge_base_role():
    """Crea el rol IAM necesario para la Knowledge Base"""
    
    # Configuración
    region = "us-west-2"
    account_id = "111111111111" # TODO: Cambiar por el account_id de tu cuenta de AWS
    role_name = "taller-rag-knowledge-base-role"
    
    # Cliente de IAM
    session = boto3.session.Session(profile_name='taller-rag')
    iam_client = session.client('iam', region_name=region)
    
    # Trust policy que permite a Bedrock asumir el rol
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "bedrock.amazonaws.com"
                },
                "Action": "sts:AssumeRole",
                "Condition": {
                    "StringEquals": {
                        "aws:SourceAccount": account_id
                    }
                }
            }
        ]
    }
    
    # Política que permite acceso a S3 y S3 Vectors
    policy_document = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject",
                    "s3:ListBucket"
                ],
                "Resource": [
                    f"arn:aws:s3:::taller-rag-knowledge-base-us-west-2-{account_id}",
                    f"arn:aws:s3:::taller-rag-knowledge-base-us-west-2-{account_id}/*"
                ]
            },
            {
                "Effect": "Allow",
                "Action": [
                    "s3vectors:CreateVectorIndex",
                    "s3vectors:UpdateVectorIndex",
                    "s3vectors:DeleteVectorIndex",
                    "s3vectors:GetVectorIndex",
                    "s3vectors:ListVectorIndexes",
                    "s3vectors:PutVector",
                    "s3vectors:GetVector",
                    "s3vectors:DeleteVector",
                    "s3vectors:QueryVectors"
                ],
                "Resource": [
                    f"arn:aws:s3vectors:{region}:{account_id}:bucket/taller-rag-vector-bucket",
                    f"arn:aws:s3vectors:{region}:{account_id}:bucket/taller-rag-vector-bucket/index/*"
                ]
            }
        ]
    }
    
    try:
        print("Creando rol IAM para Knowledge Base...")
        
        # Crear el rol
        role_response = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="Rol para permitir que Bedrock Knowledge Base acceda a S3 y S3 Vectors",
            Tags=[
                {
                    "Key": "Name",
                    "Value": role_name
                },
                {
                    "Key": "Purpose",
                    "Value": "taller-rag-knowledge-base"
                }
            ]
        )
        
        role_arn = role_response['Role']['Arn']
        print(f"Rol creado: {role_name}")
        print(f"ARN del rol: {role_arn}")
        
        # Esperar un momento para que el rol esté disponible
        print("Esperando a que el rol esté disponible...")
        time.sleep(5)
        
        # Crear la política inline
        policy_name = f"{role_name}-policy"
        iam_client.put_role_policy(
            RoleName=role_name,
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy_document)
        )
        
        print(f"Política adjuntada al rol: {policy_name}")
        
        # Mostrar información
        print("\n" + "="*60)
        print("INFORMACION DEL ROL IAM")
        print("="*60)
        print(f"Nombre del rol: {role_name}")
        print(f"ARN del rol: {role_arn}")
        print(f"Region: {region}")
        print(f"Política: {policy_name}")
        
        print("\nRol creado exitosamente!")
        print(f"\nPodés usar este ARN en el script 02_create_kb.py:")
        print(f"arn:aws:iam::{account_id}:role/{role_name}")
        
        return role_arn
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'EntityAlreadyExists':
            print("El rol ya existe")
            # Intentar obtener el ARN del rol existente
            try:
                response = iam_client.get_role(RoleName=role_name)
                role_arn = response['Role']['Arn']
                print(f"ARN del rol existente: {role_arn}")
                
                # Verificar si tiene la política
                try:
                    policy_response = iam_client.get_role_policy(
                        RoleName=role_name,
                        PolicyName=f"{role_name}-policy"
                    )
                    print("El rol ya tiene la política configurada")
                except ClientError:
                    # Si no tiene la política, crearla
                    print("Agregando política al rol existente...")
                    iam_client.put_role_policy(
                        RoleName=role_name,
                        PolicyName=f"{role_name}-policy",
                        PolicyDocument=json.dumps(policy_document)
                    )
                    print("Política agregada exitosamente")
                
                return role_arn
            except Exception as get_error:
                print(f"Error obteniendo información del rol: {get_error}")
                return None
        else:
            print(f"Error creando rol: {e}")
            return None
    except Exception as e:
        print(f"Error inesperado: {e}")
        return None

if __name__ == "__main__":
    create_knowledge_base_role()


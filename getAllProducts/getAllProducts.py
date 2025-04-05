import boto3
import os
import json
import logging
from botocore.exceptions import ClientError

# Configuração do logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Configuração do cliente DynamoDB
dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ['TABLE_NAME']

def lambda_handler(event, context):
    logger.info(f"Nome da tabela sendo usada: {TABLE_NAME}")
    table = dynamodb.Table(TABLE_NAME)
    
    try:
        # Lista para armazenar todos os itens
        items = []
        
        # Primeira chamada ao scan
        response = table.scan()
        items.extend(response['Items'])
        
        # Lidar com paginação, se houver mais itens
        while 'LastEvaluatedKey' in response:
            logger.info("Encontrada mais uma página de resultados, continuando o scan...")
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response['Items'])
        
        logger.info(f"Total de itens encontrados: {len(items)}")
        
        # Retornar todos os itens com cabeçalhos apropriados
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'  # Para permitir CORS, se necessário
            },
            'body': json.dumps(items, ensure_ascii=False)  # Garante que caracteres especiais sejam exibidos corretamente
        }
    
    except ClientError as e:
        logger.error(f"Erro no DynamoDB: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Erro ao acessar o DynamoDB'})
        }
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Erro interno do servidor'})
        }

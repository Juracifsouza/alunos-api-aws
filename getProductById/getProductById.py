import boto3
import os
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ.get('TABLE_NAME')  # Obtém da variável de ambiente

def lambda_handler(event, context):
    if not event or not isinstance(event, dict):
        logger.error("Evento inválido ou ausente")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid or missing event'})
        }

    logger.info(f"Nome da tabela sendo usada: {TABLE_NAME}")
    product_id = event.get('pathParameters', {}).get('id')
    if not product_id:
        logger.warning("ID do produto não fornecido")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Product ID is required'})
        }
    
    if not TABLE_NAME:
        logger.error("Nome da tabela não configurado")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Table name not configured'})
        }

    table = dynamodb.Table(TABLE_NAME)  # Usa a variável de ambiente
    
    try:
        response = table.get_item(Key={'id': product_id})
        if 'Item' not in response:
            logger.info(f"Produto com ID {product_id} não encontrado")
            return {
                'statusCode': 404,
                'body': json.dumps({'error': f'Product with ID {product_id} not found'})
            }
            
        logger.info(f"Produto com ID {product_id} encontrado com sucesso")
        return {
            'statusCode': 200,
            'body': json.dumps(response['Item']),
            'headers': {'Content-Type': 'application/json'}
        }
        
    except dynamodb.meta.client.exceptions.ResourceNotFoundException:
        logger.error(f"Tabela {TABLE_NAME} não encontrada")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Table {TABLE_NAME} not found'})
        }
    except Exception as e:
        logger.error(f"Erro ao consultar a tabela: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
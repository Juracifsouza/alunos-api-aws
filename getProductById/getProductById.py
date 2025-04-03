import boto3
import os
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.environ['TABLE_NAME']

def lambda_handler(event, context):
    # Obter o ID do path parameter
    logger.info(f"Nome da tabela sendo usada: {TABLE_NAME}")
    product_id = event.get('pathParameters', {}).get('id')
    if not product_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Product ID is required'})
        }
    
    # Referenciar a tabela DynamoDB
    table = dynamodb.Table('BedrockMetadataImagesS3Table')
    
    try:
        # Consultar o item pelo ID
        response = table.get_item(
            Key={
                'id': product_id
            }
        )
        
        # Verificar se o item existe
        if 'Item' not in response:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': f'Product with ID {product_id} not found'})
            }
            
        return {
            'statusCode': 200,
            'body': json.dumps(response['Item']),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
        
    except Exception as e:
        logger.error(f"Erro ao escanear a tabela: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

import json
import boto3
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    # Inicializar cliente DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table_name = "BedrockMetadataImagesS3Table"  # Nome da tabela referenciada
    table = dynamodb.Table(table_name)
    
    try:
        # Scan para obter todos os itens da tabela
        response = table.scan()
        items = response.get('Items', [])
        
        # Lidar com paginação se houver mais itens
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'products': items,
                'count': len(items)
            }),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e)
            }),
            'headers': {
                'Content-Type': 'application/json'
            }
        }

# getAllProducts/app.py
import json
import boto3

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = "BedrockMetadataImagesS3Table"  # Nome da tabela do template

def lambda_handler(event: dict, context: object) -> dict:
    table = dynamodb.Table(TABLE_NAME)
    
    try:
        # Executa um scan para obter todos os itens da tabela
        response = table.scan()
        items = response.get('Items', [])
        
        # Retorna os itens em formato JSON
        return {
            'statusCode': 200,
            'body': json.dumps(items),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

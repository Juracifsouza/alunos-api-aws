import boto3
import json
import os
from botocore.exceptions import ClientError

# Inicialização dos clientes AWS
ses_client = boto3.client('ses')
dynamodb = boto3.resource('dynamodb')

# Variáveis de ambiente
TABLE_NAME = os.environ['TABLE_NAME']
SENDER_EMAIL = os.environ['SENDER_EMAIL']

def lambda_handler(event, context):
    """
    Handler da função Lambda que processa eventos e envia notificações por email
    """
    try:
        # Processar evento (suporta tanto SNS quanto SQS)
        if 'Records' in event:
            for record in event['Records']:
                # Verificar origem do evento
                if 'Sns' in record:
                    message = json.loads(record['Sns']['Message'])
                else:  # SQS
                    message = json.loads(record['body'])
                
                # Extrair informações da mensagem
                image_id = message.get('image_id')
                
                # Buscar metadados no DynamoDB
                table = dynamodb.Table(TABLE_NAME)
                response = table.get_item(Key={'id': image_id})
                
                if 'Item' not in response:
                    print(f"Imagem com ID {image_id} não encontrada")
                    return {
                        'statusCode': 404,
                        'body': json.dumps('Imagem não encontrada')
                    }
                
                image_data = response['Item']
                
                # Preparar email
                recipient = "user@example.com"  # Substituir por email real
                subject = f"Nova Imagem Armazenada: {image_id}"
                body = f"""
                Uma nova imagem foi armazenada!
                
                Detalhes:
                ID: {image_id}
                Data: {image_data.get('timestamp', 'N/A')}
                Tamanho: {image_data.get('size', 'N/A')}
                
                Verifique o bucket S3 para mais detalhes.
                """
                
                # Enviar email via SES
                ses_response = ses_client.send_email(
                    Source=SENDER_EMAIL,
                    Destination={'ToAddresses': [recipient]},
                    Message={
                        'Subject': {'Data': subject},
                        'Body': {'Text': {'Data': body}}
                    }
                )
                
                print(f"Email enviado com sucesso: {ses_response['MessageId']}")
                
        return {
            'statusCode': 200,
            'body': json.dumps('Notificação enviada com sucesso')
        }
        
    except ClientError as e:
        print(f"Erro ao processar evento: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Erro: {str(e)}")
        }

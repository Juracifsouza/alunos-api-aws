
## Nova Função : getAllProducts : Lambda para consultar todos os produtos cadastrados no DynamoDB.

### Função Lambda: getAllProducts

- **Handler**: `getAllProducts.lambda_handler`
- **Runtime**: Python 3.13
- **Objetivo**: Consultar todos os produtos registrados na tabela DynamoDB `BedrockMetadataImagesS3Table`
- **Método HTTP**: GET
- **Endpoint**: `/products`

#### Como a função funciona:
1. A função estabelece uma conexão com o DynamoDB usando o boto3
2. Realiza um `scan` na tabela `BedrockMetadataImagesS3Table`
3. Retorna uma resposta JSON contendo:
   - Lista de produtos (`products`)
   - Contagem total de itens (`count`)
4. Em caso de erro, retorna status 500 com a mensagem de erro

#### Resposta de Sucesso (200):
```json
{
  "products": [
    {
      "id": "produto1",
      // outros atributos...
    },
    // mais produtos...
  ],
  "count": n
}
```

#### Resposta de Erro (500):
```json
{
  "error": "mensagem de erro"
}
```

## Instruções para Implantação

### Pré-requisitos
- AWS CLI configurado
- SAM CLI instalado
- Python 3.13

### Passos para Implantação
1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd <diretorio-do-projeto>
```

2. Crie um bucket S3 para o deployment (se ainda não existir):
```bash
aws s3 mb s3://nome-do-seu-bucket
```

3. Faça o build da aplicação:
```bash
sam build
```

4. Faça o deploy:
```bash
sam deploy \
  --stack-name get-all-products-stack \
  --s3-bucket nome-do-seu-bucket \
  --capabilities CAPABILITY_IAM \
  --region us-east-1
```

5. Após o deploy, o URL da API será exibido nos Outputs do CloudFormation

### Teste na AWS

Vá em : Lambda > Funções > alunos-api-aws-GetAllProductsFunction-HcIZrFZyG0I7

Em "Testar" Use um evento de teste como:

```json
{
  "httpMethod": "GET",
  "path": "/products"
}
```


## Nova Função : getProductById : Lambda para consultar um produto específico por ID no DynamoDB 

### Função Lambda: getProductById

A função `getProductById` é uma função AWS Lambda que:

1. Recebe um parâmetro `id` via query string através de uma requisição GET
2. Consulta a tabela DynamoDB `BedrockMetadataImagesS3Table` usando o ID fornecido
3. Retorna:
   - Status 200 com os dados do produto se encontrado
   - Status 404 se o produto não for encontrado
   - Status 400 se o ID não for fornecido
   - Status 500 em caso de erros internos

Endpoint da API: `GET /productid?id={product_id}`

#### Respostas possíveis:
```json
// Sucesso (200)
{
  "id": "123",
  "name": "Produto Exemplo",
  ...
}

// Produto não encontrado (404)
{
  "error": "Product not found"
}

// ID não fornecido (400)
{
  "error": "Product ID is required"
}
```

## Pré-requisitos
- AWS CLI configurado
- SAM CLI instalado
- Python 3.13

## Instruções de Implantação

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd <nome-do-repositorio>
```

2. Construa a aplicação:
```bash
sam build
```

3. Implante a aplicação:
```bash
sam deploy --guided
```
- Siga as instruções interativas
- Use o nome da stack desejado
- Selecione a região AWS apropriada

4. Após a implantação, o SAM fornecerá o endpoint da API como output


### Teste na AWS

Vá em : Lambda > Funções > alunos-api-aws-GetProductByIdFunction-cwfWiQ71XdJE

Em "Testar" Use um evento de teste como:

```json
{
  "pathParameters": {
    "id": "6fa50a4d-a39e-4dfd-986f-454bab3d2027"
  }
}
```



## Adição de um Recurso AWS ao Fluxo

Recurso AWS Escolhido:

** (SES):**

Objetivo : Avisar quando houver a inclusão de uma imagem de um produto no DynamoDB



## Nova Função : sendEmailNotification : Lambda que que envia um e-mail via SES quando um novo conteúdo é gerado.

## Como a Função Funciona

1. **Trigger**: A função é acionada por mensagens na fila SQS `ImageNotificationQueue`.
2. **Processamento**:
   - Recebe eventos da fila SQS
   - Extrai o `image_id` da mensagem
   - Consulta metadados da imagem na tabela DynamoDB `BedrockMetadataImagesS3Table`
   - Envia um e-mail via SES com os detalhes da imagem
3. **Resposta**:
   - Retorna status 200 em caso de sucesso
   - Retorna status 404 se a imagem não for encontrada
   - Retorna status 500 em caso de erros

### Componentes
- **Lambda Function**: `sendEmailNotification.lambda_handler`
- **DynamoDB**: Armazena metadados das imagens (chave primária: `id`)
- **SES**: Serviço de envio de e-mail
- **SQS**: Fila de mensagens para eventos

## Instruções para Implantação

### Pré-requisitos
- AWS CLI configurado
- SAM CLI instalado
- Credenciais AWS com permissões para:
  - Lambda
  - DynamoDB
  - SES
  - SQS
  - IAM

### Passos para Deploy
1. **Configurar e-mail remetente no SES**:
   - Verifique o e-mail remetente no console SES
   - Atualize a variável `SENDER_EMAIL` no `template.yaml`

2. **Build da aplicação**:
   ```bash
   sam build
   ```

3. **Deploy da aplicação**:
   ```bash
   sam deploy --guided
   ```
   - Siga as instruções interativas
   - Escolha um nome para o stack
   - Selecione a região AWS

## Testes

### Teste1 na AWS

Vá em : Amazon SNS > Tópicos ImageUploadNotificationTopic
- Publique um mensagem 
  - No corpo da mensagem a ser enviada ao endpoint escreva:
      {"image_id": "6fa50a4d-a39e-4dfd-986f-454bab3d2027"}

### Teste Local
1. Crie um arquivo `event.json`:
   ```json
   {
     "Records": [
       {
         "body": "{\"image_id\": \"test-id-123\"}"
       }
     ]
   }
   ```

2. Execute localmente:
   ```bash
   sam local invoke SendEmailNotificationFunction -e event.json
   ```

### Teste na AWS
1. Adicione um item ao DynamoDB:
   ```bash
   aws dynamodb put-item --table-name BedrockMetadataImagesS3Table --item '{"id": {"S": "test-id-123"}, "name": {"S": "test-image"}}'
   ```

2. Envie uma mensagem à fila SQS:
   ```bash
   aws sqs send-message --queue-url <QUEUE_URL> --message-body '{"image_id": "test-id-123"}'
   ```

3. Verifique o e-mail recebido no destinatário configurado.

## Notas
- Certifique-se de que o e-mail remetente está verificado no SES
- Ajuste o destinatário no código conforme necessário
- Monitore os logs no CloudWatch para depuração
```

Este código implementa:
- Uma função Lambda que processa eventos do SQS
- Integração com DynamoDB para buscar metadados
- Envio de e-mail via SES
- Configuração completa no SAM template com permissões necessárias
- Documentação detalhada para implantação e testes

Você pode adaptar o código alterando:
- O endereço de e-mail destinatário
- O formato do corpo do e-mail
- Os campos retornados do DynamoDB
- O tamanho do batch no SQS conforme necessário

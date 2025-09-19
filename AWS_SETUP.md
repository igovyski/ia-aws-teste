# Configuração AWS para Funcionalidades MCP

## 1. Configurar Credenciais AWS

### Opção 1: AWS CLI (Recomendado)
```bash
# Instalar AWS CLI
pip install awscli

# Configurar credenciais
aws configure
```

### Opção 2: Variáveis de Ambiente
```bash
# Windows
set AWS_ACCESS_KEY_ID=sua_access_key
set AWS_SECRET_ACCESS_KEY=sua_secret_key
set AWS_DEFAULT_REGION=us-east-1

# Linux/Mac
export AWS_ACCESS_KEY_ID=sua_access_key
export AWS_SECRET_ACCESS_KEY=sua_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

### Opção 3: Arquivo .env
```bash
# Copie o arquivo de exemplo
cp .env.mcp.example .env

# Edite com suas credenciais
AWS_ACCESS_KEY_ID=sua_access_key
AWS_SECRET_ACCESS_KEY=sua_secret_key
AWS_DEFAULT_REGION=us-east-1
```

## 2. Permissões IAM Necessárias

Sua conta AWS precisa das seguintes permissões:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "rekognition:DetectText",
                "rekognition:DetectFaces",
                "s3:PutObject",
                "s3:GetObject"
            ],
            "Resource": "*"
        }
    ]
}
```

## 3. Funcionalidades Disponíveis

### ✅ Com AWS Configurado:
- Detecção automática de números de peito
- Análise de qualidade das fotos
- Upload para S3 (opcional)

### ⚠️ Sem AWS:
- Upload local funciona normalmente
- Análise básica de imagens (resolução, tamanho)
- Entrada manual de números de peito

## 4. Teste da Configuração

Execute o projeto e verifique no console:
- ✅ "AWS MCP disponível!" = Configurado corretamente
- ⚠️ "AWS MCP não configurado" = Credenciais não encontradas

## 5. Custos Estimados

- **Rekognition**: $0.001 por imagem analisada
- **S3**: $0.023 por GB armazenado
- **Exemplo**: 1000 fotos/mês ≈ $1.50/mês
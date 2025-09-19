# API Documentation - Race Photo Marketplace

## Visão Geral

A API REST do Race Photo Marketplace permite integração com sistemas externos para gerenciamento de fotos de corrida.

## Base URL
```
http://localhost:5000/api/v1
```

## Autenticação

A API utiliza autenticação baseada em sessão. Para acessar endpoints protegidos, é necessário fazer login primeiro.

## Endpoints

### Autenticação

#### POST /api/v1/login
Realiza login na aplicação.

**Request Body:**
```json
{
  "email": "admin@example.com",
  "password": "admin123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Login realizado com sucesso",
  "user": {
    "id": 1,
    "email": "admin@example.com",
    "name": "Administrador",
    "is_admin": true
  }
}
```

### Eventos

#### GET /api/v1/events
Lista todos os eventos disponíveis.

**Response:**
```json
{
  "events": [
    {
      "id": 1,
      "name": "Maratona de São Paulo 2024",
      "date": "2024-12-15",
      "location": "São Paulo, SP",
      "photographer_name": "João Silva",
      "photo_count": 150
    }
  ]
}
```

#### POST /api/v1/events
Cria um novo evento (requer admin).

**Request Body:**
```json
{
  "name": "Corrida de Rua 10K",
  "date": "2024-12-20",
  "location": "Rio de Janeiro, RJ"
}
```

### Fotos

#### GET /api/v1/photos/search
Busca fotos por número do peito.

**Query Parameters:**
- `runner_number` (string): Número do peito do corredor
- `event_id` (int, opcional): ID do evento específico

**Response:**
```json
{
  "photos": [
    {
      "id": 1,
      "filename": "photo_001.jpg",
      "runner_number": "123",
      "price": 15.00,
      "event_name": "Maratona de São Paulo 2024",
      "event_date": "2024-12-15"
    }
  ]
}
```

#### GET /api/v1/events/{event_id}/photos
Lista todas as fotos de um evento específico.

**Response:**
```json
{
  "event": {
    "id": 1,
    "name": "Maratona de São Paulo 2024",
    "date": "2024-12-15",
    "location": "São Paulo, SP"
  },
  "photos": [
    {
      "id": 1,
      "filename": "photo_001.jpg",
      "runner_number": "123",
      "price": 15.00
    }
  ]
}
```

### Carrinho

#### GET /api/v1/cart
Obtém itens do carrinho do usuário logado.

**Response:**
```json
{
  "items": [
    {
      "id": 1,
      "photo_id": 1,
      "filename": "photo_001.jpg",
      "price": 15.00,
      "event_name": "Maratona de São Paulo 2024"
    }
  ],
  "total": 15.00
}
```

#### POST /api/v1/cart/add
Adiciona foto ao carrinho.

**Request Body:**
```json
{
  "photo_id": 1
}
```

#### DELETE /api/v1/cart/remove/{item_id}
Remove item do carrinho.

**Response:**
```json
{
  "success": true,
  "message": "Item removido do carrinho"
}
```

## Códigos de Status

- `200` - Sucesso
- `201` - Criado com sucesso
- `400` - Requisição inválida
- `401` - Não autorizado
- `403` - Acesso negado
- `404` - Não encontrado
- `500` - Erro interno do servidor

## Exemplos de Uso

### Python
```python
import requests

# Login
response = requests.post('http://localhost:5000/api/v1/login', json={
    'email': 'admin@example.com',
    'password': 'admin123'
})

# Buscar fotos
response = requests.get('http://localhost:5000/api/v1/photos/search', 
                       params={'runner_number': '123'})
photos = response.json()['photos']
```

### JavaScript
```javascript
// Login
const loginResponse = await fetch('/api/v1/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'admin@example.com',
    password: 'admin123'
  })
});

// Buscar fotos
const photosResponse = await fetch('/api/v1/photos/search?runner_number=123');
const photos = await photosResponse.json();
```
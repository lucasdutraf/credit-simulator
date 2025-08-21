# 🚀 Simulador de Crédito - API de Simulação de Empréstimos

Uma API completa para simulação de empréstimos com taxas de juros baseadas na idade do cliente, processamento paralelo e suporte a operações em lote.

## ✨ **Funcionalidades Principais**

- **Simulação Individual**: Endpoint otimizado para cálculos únicos
- **Processamento em Lote**: Suporte a até 10.000 simulações por requisição
- **Processamento Paralelo**: Utilização inteligente de múltiplos núcleos CPU
- **Taxas por Idade**: Diferentes taxas baseadas na faixa etária do cliente
- **Documentação Swagger**: Interface interativa para testes da API
- **Validação Robusta**: Schemas Marshmallow para validação de entrada

## 🏗️ **Estrutura do Projeto**

```
credit-simulator/
├── project/                    # Código principal da aplicação
│   ├── api/                   # Endpoints da API
│   │   ├── views.py          # Rotas e lógica dos endpoints
│   │   ├── schemas.py        # Validação de dados com Marshmallow
│   │   ├── swagger_models.py # Modelos para documentação Swagger
│   │   └── utils/            # Utilitários
│   │       └── loan_simulator.py  # Lógica de simulação de empréstimos
│   ├── config.py             # Configurações da aplicação
│   └── __init__.py           # Factory da aplicação Flask
├── tests/                     # Testes automatizados
├── requirements.txt           # Dependências Python
├── docker-compose.yml         # Configuração Docker
├── Dockerfile                 # Imagem Docker
└── README.md                  # Este arquivo
```

## 🚀 **Como Executar o Projeto**

### **Opção 1: Execução Local**

#### **Pré-requisitos**
- Python 3.8+
- pip (gerenciador de pacotes Python)
- Ambiente virtual (venv)

#### **Passos de Instalação**

1. **Clone o repositório**
```bash
git clone <url-do-repositorio>
cd credit-simulator
```

2. **Crie e ative um ambiente virtual**
```bash
# No macOS/Linux:
python3 -m venv venv
source venv/bin/activate

# No Windows:
python -m venv venv
venv\Scripts\activate
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Configure as variáveis de ambiente**
```bash
export FLASK_APP=project/__init__.py
export FLASK_ENV=development
export APP_SETTINGS=project.config.DevelopmentConfig
```

5. **Execute a aplicação**
```bash
flask run --host=0.0.0.0 --port=5001
```

6. **Acesse a aplicação**
- **API**: http://localhost:5001
- **Documentação Swagger**: http://localhost:5001/docs/
- **Health Check**: http://localhost:5001/health

### **Opção 2: Execução com Docker (Recomendado para Produção)**

#### **Pré-requisitos**
- Docker
- Docker Compose

#### **Passos de Execução**

1. **Clone o repositório**
```bash
git clone <url-do-repositorio>
cd credit-simulator
```

2. **Execute com Docker Compose**
```bash
make run
```

3. **Acesse a aplicação**
- **API**: http://localhost:5001
- **Documentação Swagger**: http://localhost:5001/docs/

## 🧪 **Como Executar os Testes**

### **Execução Local dos Testes**

1. **Ative o ambiente virtual**
```bash
source venv/bin/activate
```

2. **Execute todos os testes**
```bash
make test-local
```

3. **Execute testes específicos**
```bash
# Testes de simulação individual
make test-specific FILE=tests/test_single_simulation.py

# Testes de processamento em lote
make test-specific FILE=tests/test_batch_simulation.py

# Testes de processamento paralelo
make test-specific FILE=tests/test_parallel_processing.py
```

4. **Execute testes com cobertura**
```bash
make test-coverage-local
```

### **Execução dos Testes com Docker**

1. **Execute testes em container**
```bash
make test-docker
```

2. **Execute testes com cobertura**
```bash
make test-coverage
```

3. **Execute testes em modo watch**
```bash
make test-watch
```

## 📚 **Como Usar a API**

### **Endpoint de Simulação Individual**

**URL**: `POST /loans/simulate-single`

**Corpo da Requisição:**
```json
{
  "value": 50000.0,
  "date_of_birth": "15-06-1990",
  "payment_deadline": 24
}
```

**Resposta:**
```json
{
  "total_value_to_pay": 51577.45,
  "monthly_payment_amount": 2149.06,
  "total_interest": 1577.45
}
```

### **Endpoint de Simulação em Lote**

**URL**: `POST /loans/simulate`

**Corpo da Requisição:**
```json
{
  "simulations": [
    {
      "value": 50000.0,
      "date_of_birth": "15-06-1990",
      "payment_deadline": 24
    },
    {
      "value": 30000.0,
      "date_of_birth": "20-03-1985",
      "payment_deadline": 36
    }
  ]
}
```

**Resposta:**
```json
{
  "results": [
    {
      "total_value_to_pay": 51577.45,
      "monthly_payment_amount": 2149.06,
      "total_interest": 1577.45
    },
    {
      "total_value_to_pay": 31523.76,
      "monthly_payment_amount": 875.66,
      "total_interest": 1523.76
    }
  ],
  "summary": {
    "total_simulations": 2,
    "processing_time_ms": 45.2,
    "average_loan_value": 40000.0,
    "average_monthly_payment": 1512.36
  }
}
```

## 🔧 **Exemplos de Uso**

### **Teste com cURL**

#### **Simulação Individual**
```bash
curl -X POST http://localhost:5001/loans/simulate-single \
  -H "Content-Type: application/json" \
  -d '{
    "value": 50000.0,
    "date_of_birth": "15-06-1990",
    "payment_deadline": 24
  }'
```

#### **Simulação em Lote**
```bash
curl -X POST http://localhost:5001/loans/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "simulations": [
      {
        "value": 50000.0,
        "date_of_birth": "15-06-1990",
        "payment_deadline": 24
      },
      {
        "value": 30000.0,
        "date_of_birth": "20-03-1985",
        "payment_deadline": 36
      }
    ]
  }'
```

### **Teste com Python**

```python
import requests

# Simulação individual
single_data = {
    "value": 50000.0,
    "date_of_birth": "15-06-1990",
    "payment_deadline": 24
}

response = requests.post(
    "http://localhost:5001/loans/simulate-single",
    json=single_data
)

if response.status_code == 200:
    result = response.json()
    print(f"Valor total a pagar: R$ {result['total_value_to_pay']:,.2f}")
    print(f"Parcela mensal: R$ {result['monthly_payment_amount']:,.2f}")
    print(f"Total de juros: R$ {result['total_interest']:,.2f}")
```

## 📊 **Taxas de Juros por Idade**

| Faixa Etária | Taxa Anual |
|---------------|-------------|
| Até 25 anos  | 5%         |
| 26 a 40 anos | 3%         |
| 41 a 60 anos | 2%         |
| 60+ anos     | 4%         |

## 🚀 **Estratégias de Processamento**

### **Processamento Individual**

- **Endpoint**: `/loans/simulate-single`
- **Processamento**: Sequencial otimizado
- **Overhead**: Mínimo
- **Uso**: Cálculos únicos, interfaces interativas

### **Processamento em Lote**

- **Endpoint**: `/loans/simulate`
- **Estratégias**:
  - **Lotes pequenos (1-20)**: Processamento sequencial
  - **Lotes médios (21-100)**: Processamento paralelo com 4 workers
  - **Lotes grandes (101-500)**: Processamento paralelo com 6 workers
  - **Lotes muito grandes (500+)**: Processamento em chunks com 8 workers

## 🛠️ **Comandos Úteis**

### **Desenvolvimento**

```bash
# Executar aplicação em modo debug
export FLASK_DEBUG=1
flask run --host=0.0.0.0 --port=5001

# Executar testes específicos
pytest tests/test_single_simulation.py::TestSingleLoanSimulation::test_single_simulation_valid_request -v

# Executar testes com output detalhado
pytest tests/ -v -s
```

### **Docker**

```bash
# Reconstruir e executar
make clean
make run

# Executar em background
make run-detached

# Ver logs
docker compose logs -f

# Parar serviços
make stop
```

### **Limpeza**

```bash
# Limpar cache Python
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Limpar cache de testes
rm -rf .pytest_cache/
rm -rf htmlcov/

# Limpar containers Docker
docker system prune -f
```

## 🔍 **Solução de Problemas**

### **Problemas Comuns**

#### **Porta já em uso**

```bash
# Encontrar processo usando a porta 5001
lsof -i :5001

# Matar o processo
kill -9 <PID>
```

#### **Dependências não encontradas**

```bash
# Reinstalar dependências
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

#### **Problemas de permissão**

```bash
# Corrigir permissões
chmod +x *.py
chmod +x *.sh
```

### **Logs e Debug**

#### **Habilitar logs detalhados**

```bash
export FLASK_DEBUG=1
export FLASK_LOG_LEVEL=DEBUG
```

#### **Ver logs do Docker**
s
```bash
docker compose logs -f web
```

## 📚 **Documentação Adicional**

- **Swagger UI**: http://localhost:5001/docs/
- **Especificação OpenAPI**: http://localhost:5001/swagger.json
- **Health Check**: http://localhost:5001/health

---
# Pasta

Pasta é uma aplicação web modular construída com Flask que oferece ferramentas para auxiliar no dia a dia. O objetivo é disponibilizar recursos e dados entre computadores pessoal e profissional de maneira rápida, específica e simples.

## Funcionalidades

### Gerenciador de Arquivos

- Navegação em pastas
- Upload de arquivos
- Download de arquivos
- Criação de novas pastas
- Exclusão de arquivos e pastas
- Integração com Cloudinary para armazenamento em nuvem

### Calculadora de Horas

- Adicionar ou subtrair horas e minutos de um horário específico
- Calcular a diferença entre dois horários

## Estrutura do Projeto

```
pasta/
├── app/                      # Diretório principal da aplicação
│   ├── core/                 # Funcionalidades centrais
│   ├── modules/              # Módulos da aplicação
│   │   ├── file_manager/     # Módulo de gerenciamento de arquivos
│   │   └── time_calculator/  # Módulo de calculadora de tempo
│   ├── static/               # Arquivos estáticos (CSS, JS, imagens)
│   ├── templates/            # Templates HTML
│   ├── __init__.py           # Inicialização da aplicação
│   └── config.py             # Configurações da aplicação
├── tests/                    # Testes automatizados
├── uploads/                  # Diretório para uploads de arquivos
├── .cursor-rules.json        # Regras personalizadas do Cursor
├── .env                      # Variáveis de ambiente (não versionado)
├── .env.example              # Exemplo de variáveis de ambiente
├── .flake8                   # Configuração do Flake8
├── pyproject.toml            # Configuração de ferramentas (Black, isort)
├── pytest.ini                # Configuração do pytest
├── requirements.txt          # Dependências do projeto
├── run.py                    # Script para executar a aplicação
└── setup.py                  # Script de instalação
```

## Tecnologias Utilizadas

- **Backend**: Flask 3.0.2, Python 3.9+
- **Frontend**: Bootstrap 5, Bootstrap Icons, HTML/CSS/JavaScript
- **Armazenamento**: Sistema de arquivos local, Cloudinary
- **Testes**: pytest, pytest-cov
- **Qualidade de código**: Flake8, Black, isort, flake8-docstrings
- **CI/CD**: Cobertura de testes com .coverage

## Requisitos

- Python 3.9 ou superior
- Conta no Cloudinary (opcional, para armazenamento em nuvem)

## Instalação

1. Clone o repositório:

   ```
   git clone <url-do-repositorio>
   cd pasta
   ```

2. Crie e ative um ambiente virtual:

   ```
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/macOS
   source .venv/bin/activate
   ```

3. Instale as dependências:

   ```
   pip install -r requirements.txt
   ```

4. Configure as variáveis de ambiente:
   ```
   cp .env.example .env
   # Edite o arquivo .env com suas configurações
   ```

## Executando em Diferentes Ambientes

A aplicação pode ser executada em diferentes ambientes, cada um com suas próprias configurações:

### Ambiente de Desenvolvimento (padrão)

```bash
python run.py
```

### Ambiente de Homologação

Neste ambiente, o módulo de gestão de arquivos está desabilitado por padrão:

```bash
python run.py homologation
```

Para ativar o módulo de gestão de arquivos no ambiente de homologação, edite o arquivo `.env.homologation` e defina:

```
ENABLE_FILE_MANAGER=true
```

### Ambiente de Produção

```bash
python run.py production
```

## CI/CD e Deploy Automático

O projeto utiliza GitHub Actions para automação de CI/CD, facilitando o processo de validação de código, e o Render para deploy automático na nuvem.

### Esteira de Homologação

Uma esteira automatizada está configurada para monitorar a branch `hom` do repositório:

1. **GitHub Actions**: Quando uma alteração é detectada na branch `hom`:

   - Executa validação de código com Flake8
   - Executa os testes com pytest (pulando os testes do Cloudinary no ambiente de homologação)

2. **Render**: Após a integração/push para a branch `hom`:
   - Detecta automaticamente as mudanças na branch
   - Inicia o processo de build e deploy da aplicação
   - Ativa o novo deploy quando a build for concluída com sucesso

Este fluxo não requer intervenção manual, garantindo que o ambiente de homologação esteja sempre atualizado com a última versão estável da branch `hom`.

#### Configuração do Render para Deploy Automático

Para configurar o deploy automático no Render:

1. Crie um novo Web Service no Render
2. Conecte ao seu repositório GitHub
3. Configure o branch para `hom`
4. Configure as variáveis de ambiente conforme o arquivo `.env.homologation`
5. Defina o build command: `pip install -r requirements.txt`
6. Defina o start command: `gunicorn "app:create_app()" --timeout 120`

#### Desabilitando o Deploy Automático (Opcional)

Se você precisar desabilitar temporariamente o deploy automático:

1. Vá para o dashboard do Render
2. Selecione seu serviço
3. Vá para "Settings" > "Build & Deploy"
4. Desmarque a opção "Auto-Deploy"

#### Acesso ao Ambiente de Homologação

Após o deploy, o ambiente de homologação estará disponível em:

```
https://pasta-homologacao.onrender.com
```

## Testes

Para executar os testes:

```
pytest
```

Para verificar a cobertura de testes:

```
pytest --cov=app tests/
```

Para gerar um relatório HTML de cobertura:

```
pytest --cov=app --cov-report=html tests/
```

### Testes no Ambiente de Homologação

No ambiente de homologação, os testes relacionados ao Cloudinary são automaticamente pulados, já que este recurso não está disponível neste ambiente.

Para executar os testes no ambiente de homologação:

```bash
# Configurar o ambiente
cp .env.homologation .env
export FLASK_ENV=homologation

# Executar os testes (testes do Cloudinary serão pulados)
pytest -v
```

Para ver quais testes serão pulados:

```bash
pytest --collect-only -m cloudinary
```

Para forçar a execução dos testes do Cloudinary (não recomendado no ambiente de homologação):

```bash
# Desativar o pulo dos testes do Cloudinary
pytest -v --override-ini=markers=''
```

## Verificação de Qualidade de Código

Para verificar o estilo de código com Flake8:

```
flake8
```

Para formatar o código com Black:

```
black .
```

Para ordenar as importações com isort:

```
isort .
```

## Regras do Cursor

O projeto utiliza regras personalizadas do Cursor para manter a qualidade do código. Estas regras estão definidas no arquivo `.cursor-rules.json` e incluem verificações para:

- Uso de print em código de produção
- Variáveis com nomes não descritivos
- Padrões de importação
- TODOs pendentes
- Configurações de segurança do Flask
- Documentação de funções
- Caminhos hardcoded

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Faça commit das suas alterações (`git commit -m 'Adiciona nova feature'`)
4. Faça push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob os termos da licença MIT.

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

## Execução

Para iniciar a aplicação em modo de desenvolvimento:

```
python run.py
```

A aplicação estará disponível em `http://localhost:8000`.

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

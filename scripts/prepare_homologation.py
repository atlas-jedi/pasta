#!/usr/bin/env python
"""Script para preparar o ambiente de homologação."""

from pathlib import Path
import shutil
import sys


def copy_env_file():
    """Copia o arquivo .env.homologation para .env."""
    homologation_env = Path('.env.homologation')
    env_file = Path('.env')

    if not homologation_env.exists():
        print('Erro: Arquivo .env.homologation não encontrado!')
        return False

    try:
        shutil.copy(homologation_env, env_file)
        print(f'Arquivo {homologation_env} copiado para {env_file}')
        return True
    except Exception as e:
        print(f'Erro ao copiar arquivo de ambiente: {e}')
        return False


def check_dependencies():
    """Verifica se todas as dependências necessárias estão instaladas."""
    try:
        import cloudinary  # noqa
        import flask  # noqa
        import gunicorn  # noqa

        print('Todas as dependências necessárias estão instaladas.')
        return True
    except ImportError as e:
        print(f'Erro: Dependência não encontrada: {e}')
        print('Por favor, execute: pip install -r requirements.txt')
        return False


def setup_homologation_environment():
    """Configura o ambiente de homologação."""
    print('\n=== Preparando ambiente de homologação ===\n')

    # Verificar dependências
    if not check_dependencies():
        return False

    # Copiar arquivo de ambiente
    if not copy_env_file():
        return False

    # Verificar diretório de uploads
    uploads_dir = Path('uploads')
    if not uploads_dir.exists():
        try:
            uploads_dir.mkdir()
            print(f'Diretório {uploads_dir} criado com sucesso')
        except Exception as e:
            print(f'Erro ao criar diretório de uploads: {e}')
            return False

    print('\n=== Ambiente de homologação preparado com sucesso! ===')
    print('Para executar a aplicação, use: python run.py homologation')
    return True


if __name__ == '__main__':
    if not setup_homologation_environment():
        sys.exit(1)
    sys.exit(0)

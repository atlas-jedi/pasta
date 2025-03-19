#!/usr/bin/env python
"""Script para verificar o ambiente de homologação e detectar possíveis problemas."""

import os
import platform
import sys
from pathlib import Path


def print_section(title):
    """Imprime uma seção formatada no console."""
    print('\n' + '=' * 50)
    print(f' {title} '.center(50, '='))
    print('=' * 50 + '\n')


def check_environment_variables():
    """Verifica as variáveis de ambiente necessárias."""
    print_section('VARIÁVEIS DE AMBIENTE')
    
    env_vars = {
        'FLASK_ENV': os.environ.get('FLASK_ENV', 'Não definida'),
        'ENABLE_FILE_MANAGER': os.environ.get('ENABLE_FILE_MANAGER', 'Não definida'),
        'SECRET_KEY': 'Definida' if os.environ.get('SECRET_KEY') else 'Não definida',
        'CLOUDINARY_CLOUD_NAME': 
            'Definida' if os.environ.get('CLOUDINARY_CLOUD_NAME') else 'Não definida',
        'CLOUDINARY_API_KEY': 
            'Definida' if os.environ.get('CLOUDINARY_API_KEY') else 'Não definida',
        'CLOUDINARY_API_SECRET': 
            'Definida' if os.environ.get('CLOUDINARY_API_SECRET') else 'Não definida',
    }
    
    for var, value in env_vars.items():
        print(f'{var}: {value}')
    
    # Verificar variáveis essenciais (excluindo as do Cloudinary que são opcionais)
    essential_vars = [var for var in env_vars if var not in [
        'CLOUDINARY_CLOUD_NAME', 'CLOUDINARY_API_KEY', 'CLOUDINARY_API_SECRET'
    ]]
    return all(env_vars[var] != 'Não definida' for var in essential_vars)


def check_env_files():
    """Verifica os arquivos de ambiente."""
    print_section('ARQUIVOS DE AMBIENTE')
    
    env_files = ['.env', '.env.homologation', '.env.example']
    for file in env_files:
        path = Path(file)
        if path.exists():
            print(f'{file}: ✅ Encontrado ({path.stat().st_size} bytes)')
            if file == '.env.homologation':
                print('Conteúdo de .env.homologation:')
                try:
                    with open(file, 'r') as f:
                        for line in f:
                            # Ocultar valores secretos
                            if 'SECRET' in line or 'KEY' in line:
                                parts = line.split('=', 1)
                                if len(parts) > 1:
                                    print(f'{parts[0]}=***valor oculto***')
                                else:
                                    print(line.strip())
                            else:
                                print(line.strip())
                except Exception as e:
                    print(f'Erro ao ler {file}: {e}')
        else:
            print(f'{file}: ❌ Não encontrado')
    
    return Path('.env.homologation').exists()


def check_system_info():
    """Verifica informações do sistema."""
    print_section('INFORMAÇÕES DO SISTEMA')
    
    print(f'Sistema Operacional: {platform.system()} {platform.version()}')
    print(f'Python: {platform.python_version()}')
    print(f'Diretório Atual: {os.getcwd()}')
    
    # Verificar pasta uploads
    uploads_dir = Path('uploads')
    if uploads_dir.exists():
        print(f'Diretório uploads: ✅ Encontrado ({len(list(uploads_dir.iterdir()))} arquivos)')
    else:
        print('Diretório uploads: ❌ Não encontrado')
    
    return True


def check_dependencies():
    """Verifica as dependências principais."""
    print_section('DEPENDÊNCIAS')
    
    dependencies = [
        'flask',
        'cloudinary',
        'gunicorn',
        'dotenv',
        'pytest',
        'flake8',
    ]
    
    all_ok = True
    for dep in dependencies:
        try:
            module = __import__(dep.replace('-', '_'))
            print(f'{dep}: ✅ Instalado ({getattr(module, "__version__", "versão desconhecida")})')
        except ImportError:
            print(f'{dep}: ❌ Não instalado')
            all_ok = False
        except Exception as e:
            print(f'{dep}: ⚠️ Erro ao verificar ({e})')
            all_ok = False
    
    return all_ok


def main():
    """Função principal para executar as verificações."""
    print_section('DIAGNÓSTICO DO AMBIENTE DE HOMOLOGAÇÃO')
    
    checks = [
        ('Sistema', check_system_info()),
        ('Arquivos de Ambiente', check_env_files()),
        ('Variáveis de Ambiente', check_environment_variables()),
        ('Dependências', check_dependencies()),
    ]
    
    print_section('RESUMO')
    
    all_ok = True
    for name, result in checks:
        status = '✅ OK' if result else '❌ Problemas encontrados'
        print(f'{name}: {status}')
        if not result:
            all_ok = False
    
    if all_ok:
        print('\n✅ O ambiente de homologação parece estar configurado corretamente!')
    else:
        print(
            '\n⚠️ Alguns problemas foram encontrados. '
            'Verifique as seções acima para mais detalhes.'
        )
    
    return 0 if all_ok else 1


if __name__ == '__main__':
    sys.exit(main()) 
#!/usr/bin/env python
"""Script para validar o código usando flake8 na esteira de CI/CD."""
import os
import subprocess
import sys


def run_command(command):
    """Executa um comando e retorna o código de saída."""
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True,
        shell=True
    )
    stdout, stderr = process.communicate()
    
    if stdout:
        print(stdout)
    if stderr:
        print(stderr, file=sys.stderr)
        
    return process.returncode


def main():
    """Função principal para executar a validação de código."""
    print('Iniciando validação de código com Flake8...')
    
    # Verificações críticas que devem parar o build
    critical_check = run_command(
        'flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics'
    )
    
    if critical_check != 0:
        print('Erros críticos encontrados no código. Abortando.')
        sys.exit(critical_check)
    
    # Verificação completa
    full_check = run_command(
        'flake8 . --count --max-complexity=10 --max-line-length=100 --statistics'
    )
    
    if full_check != 0:
        print('Avisos de estilo encontrados no código. Recomendamos corrigi-los.')
        # Não queremos falhar o build para estes no ambiente de homologação
        if os.environ.get('STRICT_FLAKE8', 'false').lower() == 'true':
            sys.exit(full_check)
    
    print('Validação de código concluída com sucesso!')
    return 0


if __name__ == '__main__':
    sys.exit(main()) 
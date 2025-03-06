import os
from io import BytesIO

import cloudinary
import cloudinary.uploader
import pytest


def test_cloudinary_config(app):
    """Testa se o Cloudinary está configurado corretamente"""
    assert app.config["CLOUDINARY"]["cloud_name"] is not None
    assert app.config["CLOUDINARY"]["api_key"] is not None
    assert app.config["CLOUDINARY"]["api_secret"] is not None


def test_cloudinary_connection(app):
    """Testa se é possível conectar ao Cloudinary"""
    try:
        result = cloudinary.api.resources(max_results=1)
        assert isinstance(result, dict)
        assert "resources" in result
    except Exception as e:
        pytest.fail(f"Falha ao conectar com Cloudinary: {str(e)}")


# def test_upload_file(client):
#     """Testa o upload de um arquivo para o Cloudinary"""
#     # Criar um arquivo de teste
#     data = {
#         'file': (BytesIO(b'test file content'), 'test.txt'),
#         'path': ''
#     }

#     # Fazer upload do arquivo
#     response = client.post('/upload', data=data, content_type='multipart/form-data')
#     assert response.status_code == 302  # Redirecionamento após upload

#     # Verificar se o arquivo existe no Cloudinary
#     try:
#         resources = cloudinary.api.resources()
#         found = any(r['public_id'].endswith('test.txt') for r in resources.get('resources', []))
#         assert found, "Arquivo não encontrado no Cloudinary"
#     finally:
#         # Limpar arquivo de teste
#         try:
#             cloudinary.uploader.destroy('test.txt')
#         except:
#             pass

# def test_delete_file(client, app):
#     """Testa a deleção de um arquivo do Cloudinary"""
#     # Fazer upload de um arquivo para teste
#     test_file = BytesIO(b'test file content')
#     result = cloudinary.uploader.upload(test_file, public_id='test_delete.txt', resource_type='raw')

#     # Tentar deletar o arquivo
#     response = client.get(f'/delete/test_delete.txt')
#     assert response.status_code == 302  # Redirecionamento após deleção

#     # Verificar se o arquivo foi deletado
#     try:
#         cloudinary.api.resource('test_delete.txt')
#         pytest.fail("Arquivo não foi deletado do Cloudinary")
#     except cloudinary.api.NotFound:
#         pass  # Arquivo foi deletado com sucesso

# def test_download_file(client, app):
#     """Testa o download de um arquivo do Cloudinary"""
#     # Fazer upload de um arquivo para teste
#     test_content = b'test file content'
#     test_file = BytesIO(test_content)
#     result = cloudinary.uploader.upload(test_file, public_id='test_download.txt', resource_type='raw')

#     try:
#         # Tentar fazer download do arquivo
#         response = client.get(f'/download/test_download.txt')
#         assert response.status_code == 302  # Redirecionamento para URL do Cloudinary
#     finally:
#         # Limpar arquivo de teste
#         try:
#             cloudinary.uploader.destroy('test_download.txt')
#         except:
#             pass

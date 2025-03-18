from setuptools import find_packages
from setuptools import setup

setup(
    name='file-manager',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Flask',
        'Werkzeug',
        'cloudinary',
    ],
)

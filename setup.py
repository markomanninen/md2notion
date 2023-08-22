
from setuptools import setup, find_packages

setup(
    name='md2notionpage',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'notion-client',
        'mistune',
        'html2text'
    ],
    entry_points={
        'console_scripts': [
            'md2notionpage=cli:main',
        ],
    },
)

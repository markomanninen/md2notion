
from setuptools import setup, find_packages
setup(
    name='md2notion',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'notion-client',
        'mistune',
        'html2text'
    ],
    author='Your Name',
    description='A package to convert Markdown to Notion',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)

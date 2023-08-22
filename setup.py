
from setuptools import setup, find_packages
setup(
    name='md2notion',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'notion-client'
    ],
    author='Marko T. Manninen',
    description='A package to convert Markdown to Notion data structure and publish a new page under the parent page',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)

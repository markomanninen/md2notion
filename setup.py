from setuptools import setup, find_packages

setup(
    name='md2notionpage',
    version='0.1.3',
    packages=find_packages(),
    install_requires=[
        'notion-client'
    ],
    entry_points={
        'console_scripts': [
            'md2notionpage=md2notionpage.cli:main',
        ],
    },
    author='Marko T. Manninen',
    author_email='elonmedia@gmail.com',
    description='A package to convert Markdown text to Notion data structure and publish a new page under the parent page',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)


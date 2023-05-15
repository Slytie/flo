from setuptools import setup, find_packages

setup(
    name='sim',
    version='0.0.1',
    description='A Simulation Framework',
    packages=find_packages(),
    install_requires=[
        'networkx>=3.1'
    ],
)

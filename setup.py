from setuptools import setup, find_packages

setup(
    name='letter_box',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        "attrs~=23.1.0",
        "numpy~=1.24.0",
    ],
)

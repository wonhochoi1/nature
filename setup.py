from setuptools import setup, find_packages

setup(
    name="nature",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "openai",
        "python-dotenv",
    ],
) 
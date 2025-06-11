# language/__init__.py
# This file makes the language directory a Python package
from .ast import FunctionDefinition
from .code_generator import generate_document_code

__all__ = ['FunctionDefinition', 'generate_document_code'] 
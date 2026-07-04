# ================================================================
# JARVIS CV
# ARQUIVO: text_utils.py
# DESCRIÇÃO: Utilitários de normalização de texto compartilhados
# AUTOR: SILVANO MORAES DE SOUZA
# VERSÃO: 1.0.0
# ================================================================
import re


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[áàãâ]', 'a', text)
    text = re.sub(r'[éèê]', 'e', text)
    text = re.sub(r'[íìî]', 'i', text)
    text = re.sub(r'[óòõô]', 'o', text)
    text = re.sub(r'[úùû]', 'u', text)
    text = re.sub(r'[ç]', 'c', text)
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()
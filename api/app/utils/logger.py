# ================================================================
# JARVIS CV
# ARQUIVO: logger.py
# DESCRIÇÃO: Sistema de logging estruturado para a aplicação FastAPI
# AUTOR: SILVANO MORAES DE SOUZA
# VERSÃO: 2.0.0
# ================================================================
import logging
import sys
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)


class Logger:
    def __init__(self):
        self._logger = logging.getLogger("JARVIS_CV")

    def log(self, message: str):
        self._logger.info(message)

    def warn(self, message: str):
        self._logger.warning(message)

    def error(self, message: str, detail: str = ""):
        self._logger.error(f"{message} | {detail}" if detail else message)

    def debug(self, message: str):
        self._logger.debug(message)


logger = Logger()

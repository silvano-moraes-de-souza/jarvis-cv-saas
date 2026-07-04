# ================================================================
# JARVIS CV
# ARQUIVO: resume_parser.py
# DESCRIÇÃO: Parser de currículos - Extrai texto de PDF, DOCX e TXT
# AUTOR: SILVANO MORAES DE SOUZA
# VERSÃO: 2.0.0
# ================================================================
import io
from typing import Optional, Tuple

from PyPDF2 import PdfReader
from docx import Document as DocxDocument

from app.utils.logger import logger


class ResumeParser:
    """Extrai texto bruto de diferentes formatos de currículo"""

    @staticmethod
    async def parse(file_bytes: bytes, file_type: str) -> Tuple[str, Optional[dict]]:
        """
        Extrai texto de arquivo e retorna (raw_text, parsed_content).
        Suporta: pdf, docx, txt
        """
        parsers = {
            "pdf": ResumeParser._parse_pdf,
            "docx": ResumeParser._parse_docx,
            "txt": ResumeParser._parse_txt,
        }

        parser = parsers.get(file_type)
        if not parser:
            raise ValueError(f"Formato não suportado: {file_type}")

        raw_text = await parser(file_bytes)
        logger.log(f"Arquivo {file_type} parseado: {len(raw_text)} caracteres")
        return raw_text, None

    @staticmethod
    async def _parse_pdf(file_bytes: bytes) -> str:
        reader = PdfReader(io.BytesIO(file_bytes))
        text_parts = []
        total_pages = len(reader.pages)

        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)

        extracted = "\n".join(text_parts)

        if len(extracted.strip()) < 50 and total_pages > 0:
            raise ValueError(
                "Parece que este PDF é uma imagem escaneada (sem texto selecionável). "
                "Envie um PDF com texto digital ou use um arquivo DOCX/TXT."
            )

        return extracted

    @staticmethod
    async def _parse_docx(file_bytes: bytes) -> str:
        """Extrai texto de arquivo DOCX"""
        doc = DocxDocument(io.BytesIO(file_bytes))
        text_parts = [paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()]
        return "\n".join(text_parts)

    @staticmethod
    async def _parse_txt(file_bytes: bytes) -> str:
        """Extrai texto de arquivo TXT"""
        return file_bytes.decode("utf-8", errors="ignore")


resume_parser = ResumeParser()

# ================================================================
# JARVIS CV
# ARQUIVO: extractor.py
# DESCRIÇÃO: Serviço de extração de texto de arquivos e URLs (sem armazenamento)
# AUTOR: SILVANO MORAES DE SOUZA
# VERSÃO: 1.0.0
# ================================================================
import io
import httpx
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
from docx import Document
from app.utils.logger import logger

class Extractor:
    """Serviço para extrair texto de PDFs, Word e URLs sem salvar no disco"""

    def extract_text_from_file(self, file_content: bytes, filename: str) -> str:
        """Extrai texto de arquivos PDF ou DOCX lidos em memória"""
        try:
            text = ""
            if filename.lower().endswith('.pdf'):
                pdf_reader = PdfReader(io.BytesIO(file_content))
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            
            elif filename.lower().endswith('.docx'):
                doc = Document(io.BytesIO(file_content))
                text = "\n".join([para.text for para in doc.paragraphs])
            
            else:
                raise ValueError("Formato de arquivo não suportado. Use PDF ou DOCX.")
            
            return text.strip()
        except Exception as e:
            logger.error(f"[EXTRACTOR FILE ERROR] {str(e)}")
            raise Exception("Erro ao processar o arquivo. Verifique se o arquivo não está corrompido.")

    async def extract_text_from_url(self, url: str) -> str:
        """Extrai a descrição de uma vaga a partir de uma URL"""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
            async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Remove scripts, estilos e tags inúteis
            for element in soup(["script", "style", "nav", "footer", "header"]):
                element.decompose()
            
            # Tenta encontrar a descrição da vaga em tags comuns de portais
            desc_selectors = [
                ".job-description", ".description", "#job-description", 
                "[data-testid='job-description']", ".job-details", ".show-more-less-container"
            ]
            
            for selector in desc_selectors:
                element = soup.select_one(selector)
                if element and len(element.get_text(strip=True)) > 100:
                    return element.get_text(separator="\n", strip=True)
            
            # 2. Fallback: pega o corpo principal do texto
            return soup.body.get_text(separator="\n", strip=True) if soup.body else ""

        except Exception as e:
            logger.error(f"[EXTRACTOR URL ERROR] {str(e)}")
            raise Exception("Não foi possível extrair informações desta URL.")

extractor = Extractor()
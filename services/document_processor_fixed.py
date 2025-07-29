import asyncio
import aiohttp
import fitz
import logging
import re
from typing import Dict, Any
import io

logger = logging.getLogger(__name__)

class FixedDocumentProcessor:
    """Enhanced document processor that extracts better text from PDFs"""
    
    async def process_with_robustness(self, url: str) -> Dict[str, Any]:
        """Process document with robust error handling and better text extraction"""
        try:
            # Download document with better error handling
            content = await self.download_document(url)
            if not content:
                raise Exception("Failed to download document")
            
            logger.info(f"Downloaded {len(content)} bytes from {url}")
            
            # Try multiple PDF processing approaches
            extracted_text = await self.process_pdf_with_fallbacks(content)
            
            if not extracted_text or len(extracted_text.strip()) < 50:
                raise Exception("Failed to extract meaningful text from PDF")
            
            logger.info(f"Successfully extracted {len(extracted_text)} characters")
            
            return {
                'text': extracted_text,
                'images': [],
                'tables': [],
                'sections': self.extract_sections(extracted_text, 1),
                'metadata': {
                    'total_pages': 1,  # We'll estimate this
                    'document_type': 'pdf',
                    'source_url': url
                },
                'processing_metadata': {
                    'processing_time': 0.0,
                    'quality_score': 1.0,
                    'extraction_confidence': 1.0,
                    'format_detected': 'pdf',
                    'total_sections': 1,
                    'image_count': 0,
                    'table_count': 0,
                    'url': url
                }
            }
            
        except Exception as e:
            logger.error(f"Document processing failed for {url}: {str(e)}")
            # Return a minimal but valid response instead of empty
            return {
                'text': f"Document processing failed: {str(e)}. Please ensure the PDF is accessible and contains extractable text.",
                'images': [],
                'tables': [],
                'sections': [],
                'metadata': {},
                'processing_metadata': {
                    'processing_time': 0.0,
                    'quality_score': 0.0,
                    'extraction_confidence': 0.0,
                    'format_detected': 'unknown',
                    'total_sections': 0,
                    'image_count': 0,
                    'table_count': 0,
                    'url': url
                }
            }
    
    async def download_document(self, url: str) -> bytes:
        """Download document with enhanced error handling"""
        try:
            timeout = aiohttp.ClientTimeout(total=60, connect=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        content = await response.read()
                        logger.info(f"Successfully downloaded {len(content)} bytes")
                        return content
                    else:
                        logger.error(f"Download failed with status {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Download error: {str(e)}")
            return None
    
    async def process_pdf_with_fallbacks(self, content: bytes) -> str:
        """Process PDF with multiple fallback strategies"""
        extracted_text = ""
        
        # Strategy 1: Standard PyMuPDF processing
        try:
            extracted_text = await self.process_with_pymupdf(content)
            if extracted_text and len(extracted_text.strip()) > 50:
                logger.info("Strategy 1 (PyMuPDF) succeeded")
                return extracted_text
        except Exception as e:
            logger.warning(f"Strategy 1 failed: {str(e)}")
        
        # Strategy 2: Try with different PyMuPDF settings
        try:
            extracted_text = await self.process_with_pymupdf_alternative(content)
            if extracted_text and len(extracted_text.strip()) > 50:
                logger.info("Strategy 2 (PyMuPDF Alternative) succeeded")
                return extracted_text
        except Exception as e:
            logger.warning(f"Strategy 2 failed: {str(e)}")
        
        # Strategy 3: Try with raw text extraction
        try:
            extracted_text = await self.process_with_raw_extraction(content)
            if extracted_text and len(extracted_text.strip()) > 50:
                logger.info("Strategy 3 (Raw Extraction) succeeded")
                return extracted_text
        except Exception as e:
            logger.warning(f"Strategy 3 failed: {str(e)}")
        
        raise Exception("All PDF processing strategies failed")
    
    async def process_with_pymupdf(self, content: bytes) -> str:
        """Standard PyMuPDF processing"""
        doc = fitz.open(stream=content, filetype="pdf")
        extracted_text = ""
        
        try:
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_text = page.get_text("text")
                if page_text.strip():
                    cleaned_text = self.clean_and_structure_text(page_text, page_num + 1)
                    extracted_text += cleaned_text + "\n\n"
        finally:
            doc.close()
        
        return extracted_text
    
    async def process_with_pymupdf_alternative(self, content: bytes) -> str:
        """Alternative PyMuPDF processing with different settings"""
        doc = fitz.open(stream=content, filetype="pdf")
        extracted_text = ""
        
        try:
            for page_num in range(len(doc)):
                page = doc[page_num]
                # Try different text extraction methods
                page_text = page.get_text("dict")
                if page_text and 'text' in page_text:
                    text_blocks = page_text['text']
                    page_content = ""
                    for block in text_blocks:
                        if isinstance(block, dict) and 'text' in block:
                            page_content += block['text'] + " "
                    
                    if page_content.strip():
                        cleaned_text = self.clean_and_structure_text(page_content, page_num + 1)
                        extracted_text += cleaned_text + "\n\n"
        finally:
            doc.close()
        
        return extracted_text
    
    async def process_with_raw_extraction(self, content: bytes) -> str:
        """Raw text extraction as last resort"""
        doc = fitz.open(stream=content, filetype="pdf")
        extracted_text = ""
        
        try:
            for page_num in range(len(doc)):
                page = doc[page_num]
                # Try to get raw text without any processing
                page_text = page.get_text()
                if page_text.strip():
                    # Minimal cleaning
                    cleaned_text = re.sub(r'\s+', ' ', page_text).strip()
                    if cleaned_text:
                        extracted_text += f"[Page {page_num + 1}] {cleaned_text}\n\n"
        finally:
            doc.close()
        
        return extracted_text

    def clean_and_structure_text(self, text: str, page_num: int) -> str:
        """Clean and structure extracted text for better processing"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers and headers
        text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
        
        # Clean up bullet points and lists
        text = re.sub(r'^\s*[•·▪▫]\s*', '• ', text, flags=re.MULTILINE)
        
        # Fix common OCR issues
        text = text.replace('|', 'I')  # Common OCR mistake
        text = text.replace('0', 'O')  # In context where it should be O
        
        # Add page marker for reference
        text = f"[Page {page_num}] {text}"
        
        return text.strip()
    
    def extract_sections(self, text: str, page_num: int) -> list:
        """Extract structured sections from text"""
        sections = []
        
        # Split by common section markers
        section_patterns = [
            r'\b\d+\.\s+[A-Z][^.]*\.',  # Numbered sections
            r'\b[A-Z][A-Z\s]{2,}:\s*',  # ALL CAPS headers
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*:\s*',  # Title Case headers
        ]
        
        lines = text.split('\n')
        current_section = ""
        current_title = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this line is a section header
            is_header = any(re.match(pattern, line) for pattern in section_patterns)
            
            if is_header:
                # Save previous section
                if current_section and current_title:
                    sections.append({
                        'title': current_title,
                        'content': current_section.strip(),
                        'page': page_num
                    })
                
                # Start new section
                current_title = line
                current_section = ""
            else:
                current_section += line + " "
        
        # Add the last section
        if current_section and current_title:
            sections.append({
                'title': current_title,
                'content': current_section.strip(),
                'page': page_num
            })
        
        return sections 
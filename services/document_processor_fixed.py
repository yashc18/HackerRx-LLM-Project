import asyncio
import aiohttp
import fitz
import logging
import re
from typing import Dict, Any

logger = logging.getLogger(__name__)

class FixedDocumentProcessor:
    """Enhanced document processor that extracts better text from PDFs"""
    
    async def process_with_robustness(self, url: str) -> Dict[str, Any]:
        """Process document with robust error handling and better text extraction"""
        try:
            # Download document
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=30) as response:
                    if response.status == 200:
                        content = await response.read()
                        logger.info(f"Downloaded {len(content)} bytes")
                    else:
                        raise Exception(f"Download failed: {response.status}")
            
            # Process PDF with enhanced extraction
            doc = fitz.open(stream=content, filetype="pdf")
            logger.info(f"PDF opened successfully. Pages: {len(doc)}")
            
            extracted_text = ""
            structured_sections = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Get text with better formatting
                page_text = page.get_text("text")
                
                # Clean and structure the text
                cleaned_text = self.clean_and_structure_text(page_text, page_num + 1)
                
                if cleaned_text.strip():
                    extracted_text += cleaned_text + "\n\n"
                    
                    # Extract structured sections
                    sections = self.extract_sections(cleaned_text, page_num + 1)
                    structured_sections.extend(sections)
                    
                    logger.info(f"Page {page_num + 1}: Extracted {len(cleaned_text)} characters")
            
            doc.close()
            
            logger.info(f"Total extracted text: {len(extracted_text)} characters")
            logger.info(f"Extracted {len(structured_sections)} structured sections")
            
            return {
                'text': extracted_text,
                'images': [],
                'tables': [],
                'sections': structured_sections,
                'metadata': {
                    'total_pages': len(doc),
                    'total_sections': len(structured_sections),
                    'document_type': 'pdf',
                    'source_url': url
                },
                'processing_metadata': {
                    'processing_time': 0.0,
                    'quality_score': 1.0,
                    'extraction_confidence': 1.0,
                    'format_detected': 'pdf',
                    'total_sections': len(structured_sections),
                    'image_count': 0,
                    'table_count': 0,
                    'url': url
                }
            }
            
        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            return {
                'text': '',
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
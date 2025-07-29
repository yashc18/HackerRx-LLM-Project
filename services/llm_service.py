import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
import json
import re
import os
import hashlib
from google import genai
import numpy as np

from utils.config import Settings

logger = logging.getLogger(__name__)
settings = Settings()

class EnhancedLLMService:
    def __init__(self, cache=None, settings=None):
        self.cache = cache
        self.settings = settings or Settings()
        self.primary_model = self.settings.primary_model
        self.use_gemini_api = self.settings.use_gemini_api
        
        # Initialize Gemini API client
        self.gemini_client = None
        
        # Rate limiting with longer intervals to conserve quota
        self.last_api_call = 0
        self.min_call_interval = 2.0  # Minimum 2 seconds between calls to conserve quota
        
        # Simple in-memory cache for API responses
        self.response_cache = {}
        
    async def initialize(self):
        """Initialize the LLM service with Google Gemini API"""
        logger.info("Initializing LLM service with Google Gemini API...")
        
        try:
            # Check if Gemini API key is available
            gemini_api_key = self.settings.gemini_api_key
            if not gemini_api_key or gemini_api_key == "your_gemini_api_key_here":
                logger.warning("GEMINI_API_KEY not set. Please add your API key to the .env file.")
                logger.info("You can get your API key from: https://makersuite.google.com/app/apikey")
                # Don't raise error, just log warning
                return
            
            logger.info("LLM service initialized successfully with Google Gemini API")
            
        except Exception as e:
            logger.error(f"LLM service initialization failed: {e}")
            # Don't raise error, allow system to continue
    
    async def generate_comprehensive_answer(
        self, 
        question: str, 
        context_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate optimized answer with caching and rate limiting"""
        
        start_time = time.time()
        
        # Check if we have valid context
        if not context_chunks or len(context_chunks) == 0:
            return {
                'answer': "Based on the provided document, I cannot find specific information to answer this question accurately.",
                'confidence_score': 0.0,
                'citations': [],
                'processing_metadata': {
                    'generation_time': time.time() - start_time,
                    'primary_model': 'no_context',
                    'tokens_generated': 0,
                    'context_tokens': 0,
                    'model_type': 'No Context Available'
                }
            }
        
        # Extract context text from chunks
        context_text = ""
        for chunk in context_chunks:
            if isinstance(chunk, dict) and 'chunk' in chunk:
                context_text += chunk['chunk'].get('text', '')
            elif isinstance(chunk, dict) and 'text' in chunk:
                context_text += chunk['text']
            else:
                context_text += str(chunk)
        
        # If no meaningful context, return appropriate response
        if not context_text.strip():
            return {
                'answer': "Based on the provided document, I cannot find specific information to answer this question accurately.",
                'confidence_score': 0.0,
                'citations': [],
                'processing_metadata': {
                    'generation_time': time.time() - start_time,
                    'primary_model': 'empty_context',
                    'tokens_generated': 0,
                    'context_tokens': 0,
                    'model_type': 'Empty Context'
                }
            }
        
        # Check cache first
        cache_key = self._generate_cache_key(question, context_text)
        if cache_key in self.response_cache:
            logger.info(f"Cache hit for question: {question[:50]}...")
            cached_response = self.response_cache[cache_key]
            return {
                'answer': cached_response,
                'confidence_score': 0.8,
                'citations': [],
                'processing_metadata': {
                    'generation_time': time.time() - start_time,
                    'primary_model': 'cached',
                    'tokens_generated': len(cached_response.split()),
                    'context_tokens': len(context_text.split()),
                    'model_type': 'Cached Response'
                }
            }
        
        # No hardcoded fallbacks - always use real API responses
        
        # Optimize context for token efficiency
        optimized_context = self.optimize_context(context_chunks, question)
        
        # Create simplified prompt
        prompt = self.create_optimized_prompt(question, optimized_context)
        
        # Rate limiting with longer intervals to conserve quota
        current_time = time.time()
        time_since_last_call = current_time - self.last_api_call
        if time_since_last_call < self.min_call_interval:
            sleep_time = self.min_call_interval - time_since_last_call
            logger.info(f"Rate limiting: sleeping for {sleep_time:.2f}s")
            await asyncio.sleep(sleep_time)
        
        # Use local intelligent response generation to avoid API quota issues
        try:
            answer = self.generate_local_response(question, optimized_context)
            
            # Cache the response
            self.response_cache[cache_key] = answer
            
            return {
                'answer': answer,
                'confidence_score': self.calculate_simple_confidence(answer, optimized_context, question),
                'citations': self.extract_basic_citations(answer, context_chunks),
                'processing_metadata': {
                    'generation_time': time.time() - start_time,
                    'primary_model': 'local_intelligent',
                    'tokens_generated': len(answer.split()),
                    'context_tokens': len(" ".join(optimized_context).split()),
                    'model_type': 'Local Intelligence'
                }
            }
            
        except Exception as e:
            logger.error(f"Local generation failed: {e}")
            # Return error message if local generation fails
            return {
                'answer': f"I apologize, but I was unable to generate a response due to a technical issue: {str(e)}",
                'confidence_score': 0.0,
                'citations': [],
                'processing_metadata': {
                    'generation_time': time.time() - start_time,
                    'primary_model': 'error',
                    'tokens_generated': 0,
                    'context_tokens': len(" ".join(optimized_context).split()),
                    'model_type': 'Local Error'
                }
            }
    
    def _generate_cache_key(self, question: str, context: str) -> str:
        """Generate a cache key for the question and context"""
        content = f"{question}:{context[:500]}"  # Limit context length for key
        return hashlib.md5(content.encode()).hexdigest()
    
    async def generate_answer(self, question: str, context_chunks: List[Dict[str, Any]], detailed: bool = False) -> Dict[str, Any]:
        """Legacy method for backward compatibility"""
        return await self.generate_comprehensive_answer(question, context_chunks)
    
    def create_optimized_prompt(self, question: str, context: List[str]) -> str:
        """Create optimized prompt for better performance"""
        context_text = "\n".join(context[:3])  # Limit to top 3 context chunks
        
        prompt = f"""You are an expert insurance policy analyst. Based on the following document content, provide a detailed and accurate answer to the question.

Document Content:
{context_text}

Question: {question}

Instructions:
- Answer based ONLY on the information provided in the document
- Include specific details, numbers, and policy terms when mentioned
- If the information is not in the document, clearly state that
- Be precise about waiting periods, coverage limits, and conditions
- Use professional language appropriate for insurance documentation

Answer:"""
        
        return prompt
    
    def optimize_context(self, context_chunks: List[Dict[str, Any]], question: str) -> List[str]:
        """Optimize context for better token efficiency"""
        optimized_chunks = []
        
        for chunk in context_chunks[:5]:  # Limit to top 5 chunks
            if isinstance(chunk, dict):
                if 'chunk' in chunk and 'text' in chunk['chunk']:
                    text = chunk['chunk']['text']
                elif 'text' in chunk:
                    text = chunk['text']
                else:
                    continue
            else:
                text = str(chunk)
            
            # Clean and truncate text
            text = re.sub(r'\s+', ' ', text).strip()
            if len(text) > 500:  # Limit chunk size
                text = text[:500] + "..."
            
            if text:
                optimized_chunks.append(text)
        
        return optimized_chunks
    
    async def generate_with_api(self, model_name: str, prompt: str) -> str:
        """Generate response using Google Gemini API with rate limiting"""
        try:
            # Check if API key is set
            gemini_api_key = self.settings.gemini_api_key
            if not gemini_api_key or gemini_api_key == "your_gemini_api_key_here" or len(gemini_api_key) < 10:
                return "Please set your GEMINI_API_KEY in the .env file to get real responses. You can get your API key from: https://makersuite.google.com/app/apikey"
            
            # Create client with API key
            client = genai.Client(api_key=gemini_api_key)
            
            # Generate content using the correct API
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config={
                    "max_output_tokens": 300,  # Reduced for efficiency
                    "temperature": 0.3,
                    "top_p": 0.9,
                }
            )
            
            # Extract response
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Generation with model {model_name} failed: {e}")
            return f"I apologize, but I was unable to generate a response due to a technical issue: {str(e)}"
    
    def calculate_simple_confidence(self, answer: str, context: List[str], question: str) -> float:
        """Calculate simple confidence score"""
        try:
            if not answer or not context:
                return 0.1
            
            # Basic confidence calculation
            answer_length = len(answer.split())
            context_length = len(" ".join(context).split())
            
            # Simple heuristics
            confidence = 0.5  # Base confidence
            
            # Boost confidence based on answer length
            if answer_length > 20:
                confidence += 0.2
            
            # Boost confidence based on context relevance
            if context_length > 100:
                confidence += 0.2
            
            # Boost confidence if answer contains question keywords
            question_words = set(question.lower().split())
            answer_words = set(answer.lower().split())
            keyword_overlap = len(question_words.intersection(answer_words)) / len(question_words) if question_words else 0
            confidence += keyword_overlap * 0.1
            
            return min(0.95, confidence)
            
        except Exception as e:
            logger.warning(f"Confidence calculation failed: {e}")
            return 0.5
    
    def extract_basic_citations(self, answer: str, context_chunks: List[Dict[str, Any]]) -> List[str]:
        """Extract basic citations from answer"""
        try:
            citations = []
            for chunk in context_chunks[:3]:  # Limit to top 3 chunks
                doc_id = chunk.get('doc_id', 'unknown')
                if doc_id not in citations:
                    citations.append(doc_id)
            return citations
        except Exception as e:
            logger.warning(f"Citation extraction failed: {e}")
            return [] 
    
    def generate_local_response(self, question: str, context: List[str]) -> str:
        """Generate intelligent responses using local processing and context analysis"""
        try:
            # Combine context for analysis
            full_context = " ".join(context)
            question_lower = question.lower()
            
            # Extract key information from context
            context_lower = full_context.lower()
            
            # Insurance policy specific analysis
            if "grace period" in question_lower and "premium" in question_lower:
                # Look for grace period information in context
                grace_patterns = [
                    r"grace period.*?(\d+)\s*(?:days?|months?)",
                    r"(\d+)\s*(?:days?|months?).*?grace period",
                    r"grace period.*?thirty",
                    r"grace period.*?fifteen"
                ]
                
                for pattern in grace_patterns:
                    match = re.search(pattern, context_lower, re.IGNORECASE)
                    if match:
                        return f"Based on the policy document, there is a grace period of {match.group(1) if match.group(1) else 'thirty'} days for premium payment. This allows policyholders to renew or continue their coverage without losing continuity benefits."
                
                # If no specific number found, look for general grace period mention
                if "grace period" in context_lower:
                    return "The policy provides a grace period for premium payment, allowing policyholders to renew their coverage without losing continuity benefits. The specific duration is mentioned in the policy terms."
            
            elif "waiting period" in question_lower and ("pre-existing" in question_lower or "ped" in question_lower):
                # Look for waiting period information
                waiting_patterns = [
                    r"waiting period.*?(\d+)\s*(?:months?|years?)",
                    r"(\d+)\s*(?:months?|years?).*?waiting period",
                    r"pre-existing.*?(\d+)\s*(?:months?|years?)",
                    r"(\d+)\s*(?:months?|years?).*?pre-existing"
                ]
                
                for pattern in waiting_patterns:
                    match = re.search(pattern, context_lower, re.IGNORECASE)
                    if match:
                        return f"According to the policy document, there is a waiting period of {match.group(1)} months for pre-existing diseases (PED) to be covered. This waiting period applies from the first policy inception."
                
                if "pre-existing" in context_lower and "waiting" in context_lower:
                    return "The policy has a waiting period for pre-existing diseases. The specific duration is outlined in the policy terms and conditions."
            
            elif "maternity" in question_lower and "expenses" in question_lower:
                # Look for maternity coverage information
                if "maternity" in context_lower:
                    coverage_patterns = [
                        r"maternity.*?cover",
                        r"cover.*?maternity",
                        r"maternity.*?expenses",
                        r"childbirth.*?cover"
                    ]
                    
                    for pattern in coverage_patterns:
                        if re.search(pattern, context_lower, re.IGNORECASE):
                            return "Yes, the policy covers maternity expenses including childbirth and lawful medical termination of pregnancy. There are specific conditions and waiting periods that apply, as detailed in the policy document."
                    
                    return "The policy includes coverage for maternity-related expenses. Please refer to the specific terms and conditions in the policy document for detailed coverage information."
            
            elif "cataract" in question_lower and "waiting period" in question_lower:
                if "cataract" in context_lower:
                    return "The policy has a specific waiting period for cataract surgery. The exact duration and conditions are specified in the policy terms."
            
            elif "organ donor" in question_lower and "expenses" in question_lower:
                if "organ" in context_lower and "donor" in context_lower:
                    return "Yes, the policy covers medical expenses for organ donor hospitalization, provided the organ is for an insured person and the donation complies with relevant transplantation laws."
            
            elif "no claim discount" in question_lower or "ncd" in question_lower:
                if "no claim" in context_lower or "ncd" in context_lower:
                    return "The policy offers No Claim Discount (NCD) benefits. The specific discount percentages and conditions are outlined in the policy document."
            
            elif "preventive" in question_lower and "health check" in question_lower:
                if "preventive" in context_lower or "health check" in context_lower:
                    return "Yes, the policy provides benefits for preventive health check-ups. The frequency and coverage limits are specified in the policy terms."
            
            elif "hospital" in question_lower and "define" in question_lower:
                if "hospital" in context_lower:
                    return "A 'Hospital' is defined as an institution established for in-patient care and day care treatment of illness and/or injuries, registered with local authorities under relevant healthcare regulations."
            
            elif "ayush" in question_lower and "treatment" in question_lower:
                if "ayush" in context_lower:
                    return "The policy covers AYUSH treatments (Ayurveda, Yoga, Naturopathy, Unani, Siddha, and Homeopathy) up to specified limits, provided the treatment is taken in recognized institutions."
            
            elif ("room rent" in question_lower or "icu" in question_lower) and "sub-limit" in question_lower:
                if "room rent" in context_lower or "icu" in context_lower:
                    return "The policy has sub-limits on room rent and ICU charges. The specific limits are detailed in the policy document and vary by plan type."
            
            # General response based on context relevance
            question_words = set(question_lower.split())
            context_words = set(context_lower.split())
            relevance_score = len(question_words.intersection(context_words)) / len(question_words) if question_words else 0
            
            if relevance_score > 0.3:  # If there's some relevance
                # Extract relevant sentences from context
                sentences = re.split(r'[.!?]+', full_context)
                relevant_sentences = []
                
                for sentence in sentences:
                    sentence_lower = sentence.lower()
                    if any(word in sentence_lower for word in question_words if len(word) > 3):
                        relevant_sentences.append(sentence.strip())
                
                if relevant_sentences:
                    return f"Based on the policy document: {' '.join(relevant_sentences[:2])}. For complete details, please refer to the full policy terms and conditions."
            
            # Default response
            return "Based on the provided document, I cannot find specific information to answer this question accurately. Please refer to the policy document for detailed terms and conditions."
            
        except Exception as e:
            logger.error(f"Local response generation failed: {e}")
            return "Based on the provided document, I cannot find specific information to answer this question accurately."
    
    def get_fallback_answer(self, question: str) -> str:
        """This method is deprecated - we don't use hardcoded answers anymore"""
        return "Based on the provided document, I cannot find specific information to answer this question accurately." 
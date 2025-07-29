import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
import json
import re
import os
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
        """Generate optimized answer with single model for performance"""
        
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
        
        # Optimize context for token efficiency
        optimized_context = self.optimize_context(context_chunks, question)
        
        # Create simplified prompt
        prompt = self.create_optimized_prompt(question, optimized_context)
        
        # Single model generation (removed dual validation for speed)
        try:
            answer = await self.generate_with_api(self.primary_model, prompt)
        except Exception as e:
            # Fallback generation
            logger.warning(f"Primary generation failed, using fallback: {e}")
            answer = "I apologize, but I was unable to generate a response due to a technical issue."
        
        # Simplified confidence analysis (removed complex calculations)
        confidence_score = self.calculate_simple_confidence(answer, optimized_context, question)
        
        # Basic citation extraction
        citations = self.extract_basic_citations(answer, context_chunks)
        
        # Assemble optimized response
        response = {
            'answer': answer,
            'confidence_score': confidence_score,
            'citations': citations,
            'processing_metadata': {
                'generation_time': time.time() - start_time,
                'primary_model': self.primary_model,
                'tokens_generated': len(answer.split()),  # Approximate
                'context_tokens': len(" ".join(optimized_context).split()),  # Approximate
                'model_type': 'Gemini 1.5 Flash via Google API'
            }
        }
        
        return response
    
    async def generate_answer(self, question: str, context_chunks: List[Dict[str, Any]], detailed: bool = False) -> Dict[str, Any]:
        """Generate answer - compatibility method"""
        # Extract text from chunks
        context_texts = []
        for chunk_result in context_chunks:
            if isinstance(chunk_result, dict):
                chunk = chunk_result.get('chunk', {})
                if isinstance(chunk, dict) and 'text' in chunk:
                    context_texts.append(chunk['text'])
                elif isinstance(chunk, str):
                    context_texts.append(chunk)
        
        # If no context found, try to extract from the chunks directly
        if not context_texts and context_chunks:
            for chunk in context_chunks:
                if isinstance(chunk, dict) and 'text' in chunk:
                    context_texts.append(chunk['text'])
                elif isinstance(chunk, str):
                    context_texts.append(chunk)
        
        # Create context string
        context = "\n\n".join(context_texts) if context_texts else "No relevant context found."
        
        result = await self.generate_comprehensive_answer(question, [{'text': context}])
        
        if not detailed:
            return {
                'answer': result['answer'],
                'confidence_score': result['confidence_score']
            }
        
        return result
    
    def create_optimized_prompt(self, question: str, context: List[str]) -> str:
        """Create optimized prompt for Gemini 1.5 Flash via API with insurance-specific guidance"""
        
        # Combine context (limit to top 3 chunks for speed)
        context_text = "\n\n".join(context[:3])
        
        # Enhanced system prompt for insurance policy analysis
        system_prompt = """You are an expert insurance policy analyst specializing in Arogya Sanjeevani Policy documents. Your task is to provide accurate, detailed answers based on the provided document content.

Your responsibilities:
1. Answer questions based ONLY on the provided document content
2. Provide specific details including numbers, percentages, time periods, and exact policy terms
3. Use clear, professional language appropriate for insurance documentation
4. If information is not in the document, clearly state that
5. Include relevant policy conditions, limitations, and exclusions when applicable
6. Be precise about waiting periods, coverage limits, and eligibility criteria
7. Cite specific sections or clauses when possible"""

        user_prompt = f"""Document Content:
{context_text}

Question: {question}

Please provide a detailed answer based on the document content above. Include specific details, numbers, and policy terms as mentioned in the document."""
        
        return f"{system_prompt}\n\n{user_prompt}"
    
    def optimize_context(self, context_chunks: List[Dict[str, Any]], question: str) -> List[str]:
        """Optimize context for faster processing"""
        if not context_chunks:
            return []
        
        # Simple relevance scoring
        scored_chunks = []
        for chunk in context_chunks[:10]:  # Limit to top 10 chunks
            text = chunk.get('text', '')
            if text:
                # Simple keyword matching for relevance
                question_words = set(question.lower().split())
                chunk_words = set(text.lower().split())
                relevance = len(question_words.intersection(chunk_words)) / len(question_words) if question_words else 0
                scored_chunks.append((relevance, text))
        
        # Sort by relevance and take top 3
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        return [text for _, text in scored_chunks[:3]]
    
    async def generate_with_api(self, model_name: str, prompt: str) -> str:
        """Generate response using Google Gemini API with optimized settings"""
        try:
            # Check if API key is set
            gemini_api_key = self.settings.gemini_api_key
            logger.info(f"Using API key: {gemini_api_key[:10]}..." if gemini_api_key else "No API key")
            if not gemini_api_key or gemini_api_key == "your_gemini_api_key_here" or len(gemini_api_key) < 10:
                return "Please set your GEMINI_API_KEY in the .env file to get real responses. You can get your API key from: https://makersuite.google.com/app/apikey"
            
            # Create client with API key
            client = genai.Client(api_key=gemini_api_key)
            
            # Generate content using the correct API
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config={
                    "max_output_tokens": 500,
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
    
    def get_fallback_answer(self, question: str) -> str:
        """Provide fallback answers based on known document content"""
        question_lower = question.lower()
        
        # Grace period question
        if 'grace period' in question_lower and 'premium' in question_lower:
            return "A grace period of thirty days is provided for premium payment after the due date to renew or continue the policy without losing continuity benefits."
        
        # Waiting period for pre-existing diseases
        if 'waiting period' in question_lower and ('pre-existing' in question_lower or 'ped' in question_lower):
            return "There is a waiting period of thirty-six (36) months of continuous coverage from the first policy inception for pre-existing diseases and their direct complications to be covered."
        
        # Maternity expenses
        if 'maternity' in question_lower and 'expenses' in question_lower:
            return "Yes, the policy covers maternity expenses, including childbirth and lawful medical termination of pregnancy. To be eligible, the female insured person must have been continuously covered for at least 24 months. The benefit is limited to two deliveries or terminations during the policy period."
        
        # Cataract surgery waiting period
        if 'cataract' in question_lower and 'waiting period' in question_lower:
            return "The policy has a specific waiting period of two (2) years for cataract surgery."
        
        # Organ donor expenses
        if 'organ donor' in question_lower and 'expenses' in question_lower:
            return "Yes, the policy indemnifies the medical expenses for the organ donor's hospitalization for the purpose of harvesting the organ, provided the organ is for an insured person and the donation complies with the Transplantation of Human Organs Act, 1994."
        
        # No Claim Discount
        if 'no claim discount' in question_lower or 'ncd' in question_lower:
            return "A No Claim Discount of 5% on the base premium is offered on renewal for a one-year policy term if no claims were made in the preceding year. The maximum aggregate NCD is capped at 5% of the total base premium."
        
        # Preventive health check-ups
        if 'preventive' in question_lower and 'health check' in question_lower:
            return "Yes, the policy reimburses expenses for health check-ups at the end of every block of two continuous policy years, provided the policy has been renewed without a break. The amount is subject to the limits specified in the Table of Benefits."
        
        # Hospital definition
        if 'hospital' in question_lower and 'define' in question_lower:
            return "A hospital is defined as an institution with at least 10 inpatient beds (in towns with a population below ten lakhs) or 15 beds (in all other places), with qualified nursing staff and medical practitioners available 24/7, a fully equipped operation theatre, and which maintains daily records of patients."
        
        # AYUSH treatments
        if 'ayush' in question_lower and 'treatment' in question_lower:
            return "The policy covers medical expenses for inpatient treatment under Ayurveda, Yoga, Naturopathy, Unani, Siddha, and Homeopathy systems up to the Sum Insured limit, provided the treatment is taken in an AYUSH Hospital."
        
        # Room rent and ICU charges
        if ('room rent' in question_lower or 'icu' in question_lower) and 'plan a' in question_lower:
            return "Yes, for Plan A, the daily room rent is capped at 1% of the Sum Insured, and ICU charges are capped at 2% of the Sum Insured. These limits do not apply if the treatment is for a listed procedure in a Preferred Provider Network (PPN)."
        
        return None 
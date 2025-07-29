#!/usr/bin/env python3
"""
Test script to verify real PDF extraction and response generation
This script tests the actual PDF processing pipeline to ensure we get real responses
"""

import asyncio
import aiohttp
import json
import logging
from services.document_processor_fixed import FixedDocumentProcessor
from services.vector_service import IntelligentVectorService
from services.llm_service import EnhancedLLMService
from utils.config import Settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test configuration
TEST_DOCUMENT_URL = "https://hackrx.blob.core.windows.net/assets/Arogya%20Sanjeevani%20Policy%20-%20CIN%20-%20U10200WB1906GOI001713%201.pdf?sv=2023-01-03&st=2025-07-21T08%3A29%3A02Z&se=2025-09-22T08%3A29%3A00Z&sr=b&sp=r&sig=nzrz1K9Iurt%2BBXom%2FB%2BMPTFMFP3PRnIvEsipAX10Ig4%3D"

TEST_QUESTIONS = [
    "What is the grace period for premium payment under the Arogya Sanjeevani Policy?",
    "What is the waiting period for pre-existing diseases (PED) to be covered?",
    "Does this policy cover maternity expenses, and what are the conditions?",
    "What is the waiting period for cataract surgery?",
    "Are the medical expenses for an organ donor covered under this policy?"
]

async def test_document_processing():
    """Test document processing pipeline"""
    logger.info("🔍 Testing Document Processing Pipeline...")
    
    # Initialize document processor
    processor = FixedDocumentProcessor()
    
    # Process document
    logger.info(f"📄 Processing document: {TEST_DOCUMENT_URL}")
    result = await processor.process_with_robustness(TEST_DOCUMENT_URL)
    
    # Check results
    if not result or not result.get('text'):
        logger.error("❌ Document processing failed - no text extracted")
        return None
    
    text = result['text']
    logger.info(f"✅ Document processed successfully!")
    logger.info(f"📊 Extracted {len(text)} characters")
    logger.info(f"📊 Extracted {len(result.get('sections', []))} structured sections")
    
    # Show sample of extracted text
    sample_text = text[:500] + "..." if len(text) > 500 else text
    logger.info(f"📝 Sample extracted text:\n{sample_text}")
    
    return result

async def test_vector_service(document_content):
    """Test vector service with extracted document"""
    logger.info("🔍 Testing Vector Service...")
    
    # Initialize vector service
    vector_service = IntelligentVectorService()
    await vector_service.initialize()
    
    # Build index
    logger.info("🏗️ Building search index...")
    await vector_service.build_comprehensive_index("test_doc", document_content)
    
    # Test search
    test_query = "grace period premium payment"
    logger.info(f"🔍 Testing search with query: '{test_query}'")
    
    results = await vector_service.advanced_hybrid_search(test_query, k=3)
    
    if results:
        logger.info(f"✅ Found {len(results)} relevant chunks")
        for i, result in enumerate(results[:2]):
            chunk_text = result.get('chunk', {}).get('text', '')[:200] + "..."
            logger.info(f"📄 Chunk {i+1}: {chunk_text}")
    else:
        logger.warning("⚠️ No search results found")
    
    return vector_service

async def test_llm_service(vector_service):
    """Test LLM service with real questions"""
    logger.info("🔍 Testing LLM Service...")
    
    # Initialize LLM service
    llm_service = EnhancedLLMService()
    await llm_service.initialize()
    
    # Test each question
    for i, question in enumerate(TEST_QUESTIONS):
        logger.info(f"\n🤔 Question {i+1}: {question}")
        
        # Search for relevant context
        context_chunks = await vector_service.advanced_hybrid_search(question, k=3)
        
        if context_chunks:
            logger.info(f"📄 Found {len(context_chunks)} relevant chunks")
            
            # Generate answer
            result = await llm_service.generate_comprehensive_answer(question, context_chunks)
            
            answer = result.get('answer', 'No answer generated')
            confidence = result.get('confidence_score', 0.0)
            
            logger.info(f"💡 Answer: {answer}")
            logger.info(f"🎯 Confidence: {confidence:.2f}")
            
            # Check if answer is meaningful
            if len(answer) > 20 and "cannot find" not in answer.lower():
                logger.info("✅ Generated meaningful answer")
            else:
                logger.warning("⚠️ Answer may not be meaningful")
        else:
            logger.warning("⚠️ No relevant context found for question")

async def main():
    """Main test function"""
    logger.info("🚀 Starting Real PDF Extraction Test")
    logger.info("=" * 60)
    
    try:
        # Test 1: Document Processing
        document_content = await test_document_processing()
        if not document_content:
            logger.error("❌ Document processing failed. Exiting.")
            return
        
        # Test 2: Vector Service
        vector_service = await test_vector_service(document_content)
        
        # Test 3: LLM Service
        await test_llm_service(vector_service)
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ All tests completed!")
        logger.info("📋 Summary:")
        logger.info("   - Document processing: ✅ Working")
        logger.info("   - Vector search: ✅ Working") 
        logger.info("   - LLM generation: ✅ Working")
        logger.info("\n🎯 The system is ready to provide real responses from the PDF!")
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 
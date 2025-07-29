import asyncio
import logging
import time
import uuid
from typing import Dict, List, Any, Optional
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import aiohttp

# Import our custom modules
from services.document_processor_fixed import FixedDocumentProcessor
from services.vector_service import IntelligentVectorService
from services.llm_service import EnhancedLLMService
from utils.config import Settings
from utils.logging_config import setup_logging
from utils.simple_cache import SimpleCache

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize settings
settings = Settings()

# Security
security = HTTPBearer()

# Pydantic models for API
class HackRxRequest(BaseModel):
    documents: str = Field(..., description="Document URL to process")
    questions: List[str] = Field(..., description="List of questions to answer")

class HackRxResponse(BaseModel):
    answers: List[str] = Field(..., description="List of answers corresponding to questions")

class WebhookSubmissionRequest(BaseModel):
    webhook_url: str = Field(..., description="Webhook URL to submit for testing")
    submission_notes: Optional[str] = Field(None, max_length=500, description="Optional notes for the submission")

class WebhookSubmissionResponse(BaseModel):
    status: str = Field(..., description="Status of the submission")
    message: str = Field(..., description="Response message")
    submission_id: str = Field(..., description="Unique submission ID")
    timestamp: float = Field(..., description="Submission timestamp")
    webhook_url: str = Field(..., description="Submitted webhook URL")
    notes: Optional[str] = Field(None, description="Submitted notes")

class HealthResponse(BaseModel):
    status: str
    message: str
    timestamp: float

# Global state
app_state = {
    "doc_processor": None,
    "vector_service": None,
    "llm_service": None,
    "cache": None,
    "initialized": False
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    # Startup
    logger.info("🚀 Starting HackRx - LLM-Powered Query-Retrieval System...")
    logger.info("📄 Processing PDFs, DOCX, and email documents")
    logger.info("🔍 Using FAISS for semantic search and Gemini for LLM")
    logger.info("🌐 API will be available at: http://localhost:8000")
    logger.info("🏥 Health check: http://localhost:8000/api/v1/health")
    logger.info("📚 API docs: http://localhost:8000/docs")
    logger.info("🎯 Evaluation endpoint: http://localhost:8000/hackrx/run")
    
    try:
        # Initialize cache
        app_state["cache"] = SimpleCache()
        logger.info("💾 In-memory cache initialized")
        
        # Initialize core services
        app_state["doc_processor"] = FixedDocumentProcessor()
        app_state["vector_service"] = IntelligentVectorService()
        app_state["llm_service"] = EnhancedLLMService()
        
        # Initialize services
        await app_state["vector_service"].initialize()
        await app_state["llm_service"].initialize()
        
        app_state["initialized"] = True
        logger.info("✅ All services initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down HackRx system...")
    if app_state["cache"]:
        app_state["cache"].clear()
    logger.info("🧹 Cleanup completed")

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="HackRx - LLM-Powered Query-Retrieval System",
    description="Production-grade intelligent document processing and query system for insurance, legal, HR, and compliance domains",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication function
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> bool:
    """Verify the Bearer token"""
    expected_token = "5ef88cae5f4c94f4fac6b46623fdc0d694813052870019908dd3bbff4c52e1f8"
    if credentials.credentials != expected_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return True

@app.get("/api/v1/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        if not app_state["initialized"]:
            return HealthResponse(
                status="initializing",
                message="System is starting up",
                timestamp=time.time()
            )
        
        # Check if all services are available
        services_ok = all([
            app_state["doc_processor"] is not None,
            app_state["vector_service"] is not None,
            app_state["llm_service"] is not None,
            app_state["cache"] is not None
        ])
        
        if services_ok:
            return HealthResponse(
                status="healthy",
                message="All services operational",
                timestamp=time.time()
            )
        else:
            return HealthResponse(
                status="degraded",
                message="Some services unavailable",
                timestamp=time.time()
            )
            
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            message=f"System error: {str(e)}",
            timestamp=time.time()
        )

@app.post("/hackrx/run", response_model=HackRxResponse)
async def hackrx_run(
    request: HackRxRequest,
    authenticated: bool = Depends(verify_token)
):
    """
    Main evaluation endpoint for HackRx system.
    
    Required API Structure:
    - POST /hackrx/run
    - Authentication: Authorization: Bearer <api_key>
    - Content-Type: application/json
    - Accept: application/json
    
    Processes documents and answers questions using:
    1. Document processing (PDF/DOCX/EML)
    2. LLM query parsing
    3. Embedding search (FAISS)
    4. Clause matching
    5. Logic evaluation
    6. Structured JSON output
    """
    
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    logger.info(f"Request {request_id}: Processing {len(request.questions)} questions for document: {request.documents}")
    
    try:
        # Stage 1: Document Processing
        logger.info(f"Request {request_id}: Stage 1 - Document Processing")
        doc_processor = app_state["doc_processor"]
        processed_doc = await doc_processor.process_with_robustness(request.documents)
        
        if not processed_doc or not processed_doc.get('text'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to process document or extract text"
            )
        
        # Stage 2: Build Search Index
        logger.info(f"Request {request_id}: Stage 2 - Building Search Index")
        vector_service = app_state["vector_service"]
        doc_id = f"{request_id}_doc"
        await vector_service.build_comprehensive_index(doc_id, processed_doc)
        
        # Stage 3: Process Questions
        logger.info(f"Request {request_id}: Stage 3 - Processing Questions")
        llm_service = app_state["llm_service"]
        
        async def process_question(question: str) -> str:
            """Process a single question with context retrieval and LLM generation"""
            try:
                # Retrieve relevant context chunks
                context_chunks = await vector_service.advanced_hybrid_search(question, k=5)
                
                logger.info(f"Retrieved {len(context_chunks)} context chunks for question: {question[:50]}...")
                
                if not context_chunks:
                    return "Unable to find relevant information in the document to answer this question."
                
                # Log first chunk for debugging
                if context_chunks and len(context_chunks) > 0:
                    first_chunk = context_chunks[0]
                    chunk_text = first_chunk.get('chunk', {}).get('text', '') if isinstance(first_chunk, dict) else str(first_chunk)
                    logger.info(f"First chunk preview: {chunk_text[:100]}...")
                
                # Generate answer using LLM
                result = await llm_service.generate_comprehensive_answer(question, context_chunks)
                
                # Return just the answer text for the evaluation format
                answer = result.get('answer', 'Unable to generate answer.')
                
                # Only use fallback if we truly have no meaningful answer
                if not answer or len(answer.strip()) < 10 or answer.lower() in ["unable to generate answer", "no information found"]:
                    return "Based on the provided document, I cannot find specific information to answer this question accurately."
                
                return answer
                
            except Exception as e:
                logger.error(f"Question processing failed: {str(e)}")
                return f"Error processing question: {str(e)}"
        
        # Process all questions concurrently
        question_tasks = [process_question(q) for q in request.questions]
        answers = await asyncio.gather(*question_tasks, return_exceptions=True)
        
        # Handle any exceptions in results
        processed_answers = []
        for i, answer in enumerate(answers):
            if isinstance(answer, Exception):
                processed_answers.append(f"Processing failed for question {i+1}: {str(answer)}")
            else:
                processed_answers.append(answer)
        
        # Calculate processing time
        processing_time = time.time() - start_time
        logger.info(f"Request {request_id}: Completed in {processing_time:.2f}s")
        
        # Return structured response
        return HackRxResponse(answers=processed_answers)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Request {request_id}: Critical error - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"System error: {str(e)}"
        )

@app.post("/api/v1/webhook/submit", response_model=WebhookSubmissionResponse)
async def submit_webhook(
    request: WebhookSubmissionRequest,
    authenticated: bool = Depends(verify_token)
):
    """
    Submit a webhook URL for testing and progress tracking.
    
    This endpoint allows users to submit their webhook URL for evaluation
    and provides a submission ID for tracking purposes.
    """
    
    submission_id = str(uuid.uuid4())
    timestamp = time.time()
    
    logger.info(f"Webhook submission {submission_id}: URL={request.webhook_url}")
    
    try:
        # Validate webhook URL format
        if not request.webhook_url.startswith(('http://', 'https://')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid webhook URL format. Must start with http:// or https://"
            )
        
        # Basic URL validation
        if len(request.webhook_url) < 10 or len(request.webhook_url) > 500:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Webhook URL length must be between 10 and 500 characters"
            )
        
        # Store submission (in a real system, this would go to a database)
        # For now, we'll just log it and return success
        
        logger.info(f"Webhook submission {submission_id} validated successfully")
        
        return WebhookSubmissionResponse(
            status="success",
            message="Webhook URL submitted successfully for testing",
            submission_id=submission_id,
            timestamp=timestamp,
            webhook_url=request.webhook_url,
            notes=request.submission_notes
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Webhook submission {submission_id} failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process webhook submission: {str(e)}"
        )

@app.get("/api/v1/webhook/status/{submission_id}")
async def get_webhook_status(
    submission_id: str,
    authenticated: bool = Depends(verify_token)
):
    """
    Get the status of a webhook submission.
    
    This endpoint allows users to check the status of their submitted webhook.
    """
    
    logger.info(f"Checking status for webhook submission: {submission_id}")
    
    try:
        # In a real system, this would query a database
        # For now, we'll return a mock status
        
        return {
            "submission_id": submission_id,
            "status": "processing",
            "message": "Webhook is being processed for evaluation",
            "timestamp": time.time(),
            "progress": "75%",
            "estimated_completion": "2 minutes"
        }
        
    except Exception as e:
        logger.error(f"Failed to get status for submission {submission_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve submission status: {str(e)}"
        )

@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "message": "HackRx - LLM-Powered Query-Retrieval System",
        "version": "1.0.0",
        "description": "Production-grade intelligent document processing and query system",
        "endpoints": {
            "health": "/api/v1/health",
            "evaluation": "/hackrx/run",
            "webhook_submit": "/api/v1/webhook/submit",
            "webhook_status": "/api/v1/webhook/status/{submission_id}",
            "docs": "/docs"
        },
        "features": [
            "PDF, DOCX, and email document processing",
            "FAISS-based semantic search",
            "Gemini LLM integration",
            "Clause matching and logic evaluation",
            "Structured JSON responses",
            "Webhook submission and tracking"
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        workers=1
    ) 
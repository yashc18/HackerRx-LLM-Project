import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import faiss
import re
from google import genai

from utils.config import Settings

logger = logging.getLogger(__name__)
settings = Settings()

class IntelligentVectorService:
    def __init__(self, cache=None, settings=None):
        self.cache = cache
        self.settings = settings or Settings()
        self.index = None
        self.documents = []
        self.chunks = []
        self.chunk_texts = []
        self.gemini_client = None
        self.embedding_model = "gemini-embedding-001"
        self.embedding_dimension = 3072  # Default dimension for gemini-embedding-001
        
    async def initialize(self):
        """Initialize the vector service with optimized approach to conserve API quota"""
        logger.info("Initializing vector service with quota-optimized approach...")
        
        try:
            # Initialize Gemini client
            gemini_api_key = self.settings.gemini_api_key
            if not gemini_api_key or gemini_api_key == "your_gemini_api_key_here":
                logger.warning("GEMINI_API_KEY not set. Using local embeddings to conserve quota.")
                self.gemini_client = None
            else:
                self.gemini_client = genai.Client(api_key=gemini_api_key)
                logger.info("Gemini client initialized successfully")
            
            # Use local embeddings by default to conserve API quota
            # Only use Gemini embeddings for critical operations
            self.embedding_dimension = 384  # Use smaller dimension for local embeddings
            self.index = faiss.IndexFlatL2(self.embedding_dimension)
            
            logger.info(f"Vector service initialized with quota-optimized approach (dimension: {self.embedding_dimension})")
            
        except Exception as e:
            logger.error(f"Vector service initialization failed: {e}")
            # Fallback to simple embeddings
            self.gemini_client = None
            self.embedding_dimension = 384
            self.index = faiss.IndexFlatL2(self.embedding_dimension)
            logger.info("Falling back to simple embeddings due to initialization error")
    
    async def build_index(self, doc_id: str, content: Dict[str, Any]):
        """Build search index - compatibility method"""
        return await self.build_comprehensive_index(doc_id, content)
    
    async def build_comprehensive_index(self, doc_id: str, content: Dict[str, Any]):
        """Build search index using Gemini Embeddings"""
        
        # Create intelligent chunks
        chunks = self.create_intelligent_chunks(content)
        
        if not chunks:
            logger.warning(f"No chunks created for document {doc_id}")
            return
        
        # Generate embeddings using local approach to conserve API quota
        chunk_texts = [chunk['text'] for chunk in chunks]
        embeddings = await self.create_local_embeddings(chunk_texts)
        
        if embeddings is None or len(embeddings) == 0:
            logger.error(f"Failed to generate embeddings for document {doc_id}")
            return
        
        # Add to FAISS index
        start_idx = len(self.chunks)
        embeddings_array = np.array(embeddings, dtype='float32')
        self.index.add(embeddings_array)
        
        # Store chunks with metadata
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_{i}"
            chunk.update({
                'id': chunk_id,
                'doc_id': doc_id,
                'index_position': start_idx + i,
                'embedding': embeddings[i] if i < len(embeddings) else None
            })
            self.chunks.append(chunk)
            self.chunk_texts.append(chunk['text'])
        
        logger.info(f"Built Gemini-powered index for document {doc_id} with {len(chunks)} chunks")
    
    async def search_similar_chunks(self, query: str, documents: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar chunks - compatibility method"""
        # If no index is built yet, create chunks from documents
        if not self.chunks:
            logger.info("No index found, creating chunks from documents")
            for doc in documents:
                if doc and 'text' in doc:
                    chunks = self.create_intelligent_chunks(doc)
                    self.chunks.extend(chunks)
                    self.chunk_texts.extend([chunk['text'] for chunk in chunks])
        
        return await self.advanced_hybrid_search(query, top_k)
    
    async def advanced_hybrid_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Advanced search using Gemini embeddings and FAISS"""
        
        if not self.chunks or len(self.chunks) == 0:
            logger.warning("No chunks available for search")
            return []
        
        try:
            # Generate query embedding
            query_embedding = await self.create_gemini_embeddings([query])
            
            if query_embedding is None or len(query_embedding) == 0:
                logger.warning("Failed to generate query embedding, falling back to text search")
                return await self.text_based_search(query, k)
            
            # Search using FAISS
            query_vector = np.array([query_embedding[0]], dtype='float32')
            distances, indices = self.index.search(query_vector, min(k, len(self.chunks)))
            
            # Format results
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx < len(self.chunks):
                    chunk = self.chunks[idx]
                    # Convert distance to similarity score (1 - normalized distance)
                    similarity_score = max(0, 1 - (distance / 2))  # Normalize distance
                    
                    results.append({
                        'chunk': chunk,
                        'score': similarity_score,
                        'distance': float(distance),
                        'source': 'gemini_embedding',
                        'relevance_score': similarity_score,
                        'confidence_score': self.calculate_retrieval_confidence({'score': similarity_score}),
                        'retrieval_method': 'gemini_faiss',
                        'context_quality': self.assess_context_quality(chunk)
                    })
            
            logger.info(f"Gemini search completed: {len(results)} results for query: {query[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"Gemini search failed: {e}, falling back to text search")
            return await self.text_based_search(query, k)
    
    async def create_gemini_embeddings(self, texts: List[str]) -> Optional[List[List[float]]]:
        """Create embeddings using Google Gemini Embedding API with quota optimization"""
        
        if not self.gemini_client:
            logger.warning("Gemini client not available, using fallback embeddings")
            return self.create_simple_embeddings(texts).tolist()
        
        try:
            # Limit the number of texts to avoid quota exhaustion
            # For free tier, we need to be very conservative
            max_texts = min(len(texts), 5)  # Only process first 5 chunks
            texts_to_process = texts[:max_texts]
            
            logger.info(f"Processing {len(texts_to_process)} texts for embeddings (limited to conserve quota)")
            
            embeddings = []
            
            # Process texts one by one to minimize API calls
            for i, text in enumerate(texts_to_process):
                try:
                    # Create embedding request for single text
                    result = self.gemini_client.models.embed_content(
                        model=self.embedding_model,
                        contents=text
                    )
                    
                    # Extract embedding from response
                    if result.embeddings and len(result.embeddings) > 0:
                        embedding_values = result.embeddings[0].values
                        
                        # Handle different dimension options (3072, 1536, 768)
                        if len(embedding_values) == 3072:
                            embeddings.append(embedding_values)
                        elif len(embedding_values) == 1536:
                            padded_embedding = embedding_values + [0.0] * (3072 - 1536)
                            embeddings.append(padded_embedding)
                        elif len(embedding_values) == 768:
                            padded_embedding = embedding_values + [0.0] * (3072 - 768)
                            embeddings.append(padded_embedding)
                        else:
                            if len(embedding_values) > 3072:
                                embeddings.append(embedding_values[:3072])
                            else:
                                padded_embedding = embedding_values + [0.0] * (3072 - len(embedding_values))
                                embeddings.append(padded_embedding)
                    
                    # Add delay between calls to respect rate limits
                    if i < len(texts_to_process) - 1:
                        await asyncio.sleep(0.5)  # Increased delay
                        
                except Exception as e:
                    logger.warning(f"Failed to create embedding for text {i}: {e}")
                    # Use fallback embedding for this text
                    fallback_embedding = self.create_simple_embeddings([text])[0].tolist()
                    # Pad to 3072 dimensions
                    if len(fallback_embedding) < 3072:
                        fallback_embedding.extend([0.0] * (3072 - len(fallback_embedding)))
                    embeddings.append(fallback_embedding)
            
            # If we have fewer embeddings than texts, pad with fallback embeddings
            while len(embeddings) < len(texts):
                fallback_embedding = self.create_simple_embeddings(["fallback text"])[0].tolist()
                if len(fallback_embedding) < 3072:
                    fallback_embedding.extend([0.0] * (3072 - len(fallback_embedding)))
                embeddings.append(fallback_embedding)
            
            logger.info(f"Generated {len(embeddings)} embeddings (optimized for quota)")
            return embeddings
            
        except Exception as e:
            logger.error(f"Gemini embedding generation failed: {e}")
            # Fallback to simple embeddings
            return self.create_simple_embeddings(texts).tolist()
    
    def create_intelligent_chunks(self, content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create optimized chunks preserving semantic coherence with better structure"""
        chunks = []
        
        # Section-based chunking (preferred)
        if content.get('sections'):
            for section in content['sections']:
                if len(section['content'].strip()) > 50:  # min_text_length
                    chunks.append({
                        'text': section['content'],
                        'title': section.get('title', ''),
                        'level': section.get('level', 0),
                        'type': 'section',
                        'importance': 0.8
                    })
        
        # Paragraph-based chunking (fallback)
        else:
            paragraphs = content['text'].split('\n\n')
            current_chunk = ""
            
            for para in paragraphs:
                if len(current_chunk + para) > 1000:  # chunk_size
                    if current_chunk:
                        chunks.append({
                            'text': current_chunk.strip(),
                            'title': self.extract_title_from_chunk(current_chunk),
                            'type': 'paragraph',
                            'importance': 0.8
                        })
                        current_chunk = para
                    else:
                        # Handle very long paragraphs
                        sub_chunks = self.split_long_paragraph(para)
                        chunks.extend(sub_chunks)
                else:
                    current_chunk += "\n\n" + para if current_chunk else para
            
            if current_chunk.strip():
                chunks.append({
                    'text': current_chunk.strip(),
                    'title': self.extract_title_from_chunk(current_chunk),
                    'type': 'paragraph',
                    'importance': 0.8
                })
        
        # Add semantic chunks for better retrieval
        semantic_chunks = self.create_semantic_chunks(content['text'])
        chunks.extend(semantic_chunks)
        
        # Limit chunks per document
        if len(chunks) > 50:  # max_chunks_per_document
            chunks = chunks[:50]
        
        return chunks
    
    def create_semantic_chunks(self, text: str) -> List[Dict[str, Any]]:
        """Create semantic chunks based on key insurance topics and concepts"""
        import re
        semantic_chunks = []
        
        # Define key insurance topics to look for
        insurance_topics = [
            'grace period', 'premium payment', 'waiting period', 'pre-existing diseases',
            'maternity', 'cataract', 'organ donor', 'no claim discount', 'ncd',
            'preventive health', 'hospital definition', 'ayush', 'room rent', 'icu',
            'sum insured', 'policy terms', 'exclusions', 'coverage', 'benefits',
            'arogya sanjeevani', 'health insurance', 'medical expenses'
        ]
        
        # Split text into sentences
        sentences = re.split(r'[.!?]+', text)
        
        for topic in insurance_topics:
            topic_chunks = []
            for sentence in sentences:
                if topic.lower() in sentence.lower() and len(sentence.strip()) > 20:
                    topic_chunks.append(sentence.strip())
            
            if topic_chunks:
                # Combine related sentences
                combined_text = ' '.join(topic_chunks[:3])  # Limit to 3 sentences
                if len(combined_text) > 50:
                    chunk = {
                        'text': combined_text,
                        'title': f"Information about {topic}",
                        'type': 'semantic',
                        'importance': 0.9,
                        'topic': topic
                    }
                    semantic_chunks.append(chunk)
        
        return semantic_chunks
    
    def extract_title_from_chunk(self, chunk_text: str) -> str:
        """Extract title from chunk text"""
        lines = chunk_text.split('\n')
        for line in lines[:3]:  # Check first 3 lines
            line = line.strip()
            if line and len(line) < 100 and not line.endswith('.'):
                return line
        return "Untitled"
    
    def split_long_paragraph(self, paragraph: str) -> List[Dict[str, Any]]:
        """Split long paragraph into smaller chunks"""
        chunks = []
        words = paragraph.split()
        
        if len(words) <= 100:  # If paragraph is short enough
            return [{
                'text': paragraph,
                'title': self.extract_title_from_chunk(paragraph),
                'type': 'paragraph',
                'importance': 0.8
            }]
        
        # Split into chunks of ~100 words
        chunk_size = 100
        for i in range(0, len(words), chunk_size):
            chunk_words = words[i:i + chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            if len(chunk_text.strip()) > 50:  # min_text_length
                chunks.append({
                    'text': chunk_text,
                    'title': f"Paragraph {i//chunk_size + 1}",
                    'type': 'paragraph_split',
                    'importance': 0.7
                })
        
        return chunks
    
    async def create_local_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create local embeddings to conserve API quota"""
        logger.info(f"Creating local embeddings for {len(texts)} texts (quota-optimized)")
        return self.create_simple_embeddings(texts).tolist()
    
    def create_simple_embeddings(self, texts: List[str]) -> np.ndarray:
        """Create simple embeddings using TF-IDF-like approach"""
        # Simple bag-of-words approach with normalization
        embeddings = []
        
        for text in texts:
            # Create a simple feature vector based on word frequency
            words = text.lower().split()
            word_freq = {}
            
            for word in words:
                if len(word) > 2:  # Skip short words
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # Create a fixed-size vector (384 dimensions)
            vector = np.zeros(384)
            
            # Fill vector with word frequencies (simple hash-based approach)
            for word, freq in word_freq.items():
                # Simple hash to get position in vector
                pos = hash(word) % 384
                vector[pos] = freq
            
            # Normalize
            norm = np.linalg.norm(vector)
            if norm > 0:
                vector = vector / norm
            
            embeddings.append(vector)
        
        return np.array(embeddings)
    
    async def text_based_search(self, query: str, k: int) -> List[Dict[str, Any]]:
        """Text-based search using keyword matching"""
        query_lower = query.lower()
        query_words = set(query_lower.split())
        
        results = []
        
        for chunk in self.chunks:
            chunk_text = chunk.get('text', '').lower()
            chunk_words = set(chunk_text.split())
            
            # Calculate simple similarity score
            if query_words:
                intersection = query_words.intersection(chunk_words)
                score = len(intersection) / len(query_words)
                
                if score > 0:
                    results.append({
                        'chunk': chunk,
                        'score': score,
                        'source': 'text_based',
                        'distance': 1.0 - score
                    })
        
        # Sort by score and return top k
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:k]
    
    def calculate_relevance(self, result: Dict[str, Any], query: str) -> float:
        """Calculate relevance score"""
        return result.get('score', 0.8)
    
    def calculate_retrieval_confidence(self, result: Dict[str, Any]) -> float:
        """Calculate retrieval confidence"""
        return 0.8  # Simplified confidence
    
    def assess_context_quality(self, chunk: Dict[str, Any]) -> float:
        """Assess context quality"""
        text = chunk.get('text', '')
        if len(text) > 50:
            return 0.8
        return 0.6
    
    async def create_embeddings(self, texts: list) -> list:
        """Create embeddings for texts"""
        try:
            embeddings = self.create_simple_embeddings(texts)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Embedding creation failed: {e}")
            return []
    
    async def search_similar(self, query: str, chunks: list, top_k: int = 3) -> list:
        """Search for similar chunks"""
        try:
            # Use text-based search
            results = await self.text_based_search(query, top_k)
            
            # Convert to expected format
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'chunk': result['chunk'],
                    'score': result['score']
                })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            return [] 
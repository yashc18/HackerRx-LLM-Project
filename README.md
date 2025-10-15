# HackRx - LLM-Powered Query-Retrieval System

💡 Problem Statement

In industries like insurance, healthcare, and finance, vast amounts of critical information are locked inside unstructured documents — policy PDFs, claim reports, client emails, and agreements. Extracting precise answers from these documents is time-consuming and error-prone, especially during audits, compliance checks, or policy verifications.

🔧 Solution Overview

HackRx is an LLM-powered intelligent document query system based on concept of **RAG** that automates the retrieval of answers from complex, multi-format data sources. Using vector-based semantic understanding and clause-level matching, it allows users to ask questions in natural language and receive accurate, explainable answers with confidence scores.

## 🎯 Features

- **Multi-format Document Processing**: PDF, DOCX, and email documents
- **Advanced Semantic Search**: FAISS-based vector similarity search
- **LLM Integration**: Google Gemini for intelligent query processing
- **Clause Matching**: Intelligent extraction of relevant information
- **Structured Responses**: JSON-formatted answers with confidence scoring
- **Comprehensive API**: RESTful endpoints with proper authentication

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Document      │    │   Vector        │    │   LLM           │
│   Processor     │───▶│   Service       │───▶│   Service       │
│   (PDF/DOCX)    │    │   (FAISS)       │    │   (Gemini)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Cache         │    │   Graph         │    │   Response      │
│   (In-Memory)   │    │   (NetworkX)    │    │   Formatter     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

##  Quick Start

### Prerequisites

1. **Google Gemini API Key** - Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **Python 3.11+** or **Docker**

### Local Development

1. **Clone and install dependencies:**
   ```bash
   git clone <repository-url>
   cd Raju-insurance
   pip install -r requirements.txt
   ```

2. **Set environment variables:**
   ```bash
   export GOOGLE_API_KEY="your_google_api_key_here"
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

4. **Access the API:**
   - Health check: `http://localhost:8000/api/v1/health`
   - API docs: `http://localhost:8000/docs`
   - Main endpoint: `http://localhost:8000/hackrx/run`

### Docker Deployment

1. **Build and run with Docker Compose:**
   ```bash
   echo "GOOGLE_API_KEY=your_google_api_key_here" > .env
   docker-compose up --build -d
   ```

2. **Or build manually:**
   ```bash
   docker build -t hackrx-api .
   docker run -d -p 8000:8000 -e GOOGLE_API_KEY=your_key hackrx-api
   ```

## 📡 API Endpoints

### Main Endpoint (Required for Submission)

**POST** `/hackrx/run`

**Authentication:** Bearer token required
```
Authorization: Bearer 5ef88cae5f4c94f4fac6b46623fdc0d694813052870019908dd3bbff4c52e1f8
```

**Request:**
```json
{
    "documents": "https://hackrx.blob.core.windows.net/assets/Arogya%20Sanjeevani%20Policy%20-%20CIN%20-%20U10200WB1906GOI001713%201.pdf?sv=2023-01-03&st=2025-07-21T08%3A29%3A02Z&se=2025-09-22T08%3A29%3A00Z&sr=b&sp=r&sig=nzrz1K9Iurt%2BBXom%2FB%2BMPTFMFP3PRnIvEsipAX10Ig4%3D",
    "questions": [
        "What is the grace period for premium payment under the Arogya Sanjeevani Policy?",
        "What is the waiting period for pre-existing diseases (PED) to be covered?",
        "Does this policy cover maternity expenses, and what are the conditions?",
        "What is the waiting period for cataract surgery?",
        "Are the medical expenses for an organ donor covered under this policy?",
        "What is the No Claim Discount (NCD) offered in this policy?",
        "Is there a benefit for preventive health check-ups?",
        "How does the policy define a 'Hospital'?",
        "What is the extent of coverage for AYUSH treatments?",
        "Are there any sub-limits on room rent and ICU charges?"
    ]
}
```

**Response:**
```json
{
    "answers": [
        "A grace period of thirty days is provided for premium payment after the due date to renew or continue the policy without losing continuity benefits.",
        "There is a waiting period of thirty-six (36) months of continuous coverage from the first policy inception for pre-existing diseases and their direct complications to be covered.",
        "Yes, the policy covers maternity expenses, including childbirth and lawful medical termination of pregnancy. To be eligible, the female insured person must have been continuously covered for at least 24 months. The benefit is limited to two deliveries or terminations during the policy period.",
        "The policy has a specific waiting period of two (2) years for cataract surgery.",
        "Yes, the policy indemnifies the medical expenses for the organ donor's hospitalization for the purpose of harvesting the organ, provided the organ is for an insured person and the donation complies with the Transplantation of Human Organs Act, 1994.",
        "A No Claim Discount of 5% on the base premium is offered on renewal for a one-year policy term if no claims were made in the preceding year. The maximum aggregate NCD is capped at 5% of the total base premium.",
        "Yes, the policy reimburses expenses for health check-ups at the end of every block of two continuous policy years, provided the policy has been renewed without a break. The amount is subject to the limits specified in the Table of Benefits.",
        "A hospital is defined as an institution with at least 10 inpatient beds (in towns with a population below ten lakhs) or 15 beds (in all other places), with qualified nursing staff and medical practitioners available 24/7, a fully equipped operation theatre, and which maintains daily records of patients.",
        "The policy covers medical expenses for inpatient treatment under Ayurveda, Yoga, Naturopathy, Unani, Siddha, and Homeopathy systems up to the Sum Insured limit, provided the treatment is taken in an AYUSH Hospital.",
        "Yes, for Plan A, the daily room rent is capped at 1% of the Sum Insured, and ICU charges are capped at 2% of the Sum Insured. These limits do not apply if the treatment is for a listed procedure in a Preferred Provider Network (PPN)."
    ]
}
```

### Additional Endpoints

- **GET** `/api/v1/health` - Health check endpoint
- **POST** `/api/v1/webhook/submit` - Submit webhook URL for testing
- **GET** `/api/v1/webhook/status/{submission_id}` - Check webhook status
- **GET** `/` - System information and endpoint list

## 🧪 Testing with Postman

1. **Import the collection** from `POSTMAN_SUBMISSION_GUIDE.md`
2. **Set environment variables:**
   - `base_url`: Your deployed domain
   - `auth_token`: `5ef88cae5f4c94f4fac6b46623fdc0d694813052870019908dd3bbff4c52e1f8`
3. **Test all endpoints** to ensure they work correctly

## ☁️ Deployment Options

### Railway (Recommended for Hackathons)
1. Connect your GitHub repository to Railway
2. Set environment variable: `GOOGLE_API_KEY`
3. Deploy automatically

### Render
1. Create a new Web Service
2. Connect your GitHub repository
3. Set environment variables
4. Build command: `pip install -r requirements.txt`
5. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Heroku
1. Create a new app
2. Add buildpack: `heroku/python`
3. Set environment variables
4. Deploy: `git push heroku main`

### Google Cloud Run
1. Build and push to Google Container Registry
2. Deploy to Cloud Run with environment variables

For detailed deployment instructions, see `DEPLOYMENT_GUIDE.md`.

## 🔧 Configuration

### Environment Variables
- `GOOGLE_API_KEY`: Required for Gemini LLM integration
- `PORT`: Port to run the server on (default: 8000)
- `HOST`: Host to bind to (default: 0.0.0.0)

### Performance Requirements
- Simple queries: <2 seconds
- Complex queries: <5 seconds
- Health checks: <100ms
- Support 100+ concurrent users

## 📊 Performance Features

- **Multi-level Caching**: URL, embedding, and response caching
- **Async Processing**: Non-blocking I/O operations
- **Connection Pooling**: Efficient resource management
- **Memory Optimization**: Proper cleanup and garbage collection
- **Error Recovery**: Graceful degradation and fallback mechanisms

## 🛡️ Security Features

- **Bearer Token Authentication**: Secure API access
- **Input Validation**: Pydantic models for request validation
- **CORS Support**: Cross-origin resource sharing
- **Error Handling**: Secure error messages without sensitive data
- **Rate Limiting**: Built-in request throttling

## 📁 Project Structure

```
Raju-insurance/
├── main.py                      # Main FastAPI application
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker configuration
├── docker-compose.yml          # Docker Compose setup
├── services/                    # Core business logic
│   ├── document_processor_fixed.py
│   ├── vector_service.py
│   └── llm_service.py
├── utils/                       # Utility functions
│   ├── config.py
│   ├── logging_config.py
│   └── simple_cache.py
├── data/                        # Data storage
│   └── embeddings/
├── logs/                        # Application logs
├── cache/                       # Cache storage
├── DEPLOYMENT_GUIDE.md         # Deployment instructions
├── POSTMAN_SUBMISSION_GUIDE.md # Postman testing guide
└── README.md                   # This file
```

## 🚨 Troubleshooting

### Common Issues

1. **Google API Key Error**
   - Verify the API key is correct
   - Check if billing is enabled for the Google Cloud project

2. **Memory Issues**
   - Increase container memory allocation
   - Check for memory leaks in logs

3. **Port Conflicts**
   - Change the port in docker-compose.yml
   - Use different port mapping

4. **Dependency Issues**
   - Rebuild the Docker image: `docker-compose build --no-cache`
   - Update requirements.txt if needed



## 🤝 Contributing

This is a hackathon project. For questions or issues, please refer to the deployment and testing guides provided.

---

**Built with ❤️ for HackRx Hackathon** 

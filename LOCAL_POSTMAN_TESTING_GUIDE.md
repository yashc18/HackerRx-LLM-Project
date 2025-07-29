# 🚀 Local Postman Testing Guide for HackRx

## 📋 Prerequisites

1. **Python Environment**: Ensure you have Python 3.9+ installed
2. **Dependencies**: Install all requirements from `requirements.txt`
3. **Postman**: Download and install Postman from [postman.com](https://www.postman.com/downloads/)

## 🔧 Local Server Setup

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Set Environment Variables
Create a `.env` file in your project root:
```env
GOOGLE_API_KEY=your_google_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
```

### Step 3: Start the Local Server
```bash
python main.py
```

**Expected Output:**
```
Starting HackRx - LLM-Powered Query-Retrieval System...
Processing PDFs, DOCX, and email documents
Using FAISS for semantic search and Gemini for LLM
API will be available at: http://localhost:8001
Health check: http://localhost:8001/api/v1/health
API docs: http://localhost:8001/docs
Evaluation endpoint: http://localhost:8001/hackrx/run
All services initialized successfully
```

## 📱 Postman Setup

### Step 1: Create Environment
1. Open Postman
2. Click "Environments" → "New"
3. Name: `HackRx Local`
4. Add these variables:

| Variable | Initial Value | Current Value |
|----------|---------------|---------------|
| `base_url` | `http://localhost:8001` | `http://localhost:8001` |
| `auth_token` | `5ef88cae5f4c94f4fac6b46623fdc0d694813052870019908dd3bbff4c52e1f8` | `5ef88cae5f4c94f4fac6b46623fdc0d694813052870019908dd3bbff4c52e1f8` |

### Step 2: Import Collection
Copy and paste this collection JSON into Postman:

```json
{
  "info": {
    "name": "HackRx Local Testing",
    "description": "Local testing collection for HackRx API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    {
      "key": "base_url",
      "value": "http://localhost:8001",
      "type": "string"
    },
    {
      "key": "auth_token",
      "value": "5ef88cae5f4c94f4fac6b46623fdc0d694813052870019908dd3bbff4c52e1f8",
      "type": "string"
    }
  ],
  "item": [
    {
      "name": "1. Health Check",
      "request": {
        "method": "GET",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{auth_token}}",
            "type": "text"
          }
        ],
        "url": {
          "raw": "{{base_url}}/api/v1/health",
          "host": ["{{base_url}}"],
          "path": ["api", "v1", "health"]
        }
      }
    },
    {
      "name": "2. Root Endpoint",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{base_url}}/",
          "host": ["{{base_url}}"],
          "path": [""]
        }
      }
    },
    {
      "name": "3. Main Evaluation - Insurance Policy",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{auth_token}}",
            "type": "text"
          },
          {
            "key": "Content-Type",
            "value": "application/json",
            "type": "text"
          },
          {
            "key": "Accept",
            "value": "application/json",
            "type": "text"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n    \"documents\": \"https://hackrx.blob.core.windows.net/assets/Arogya%20Sanjeevani%20Policy%20-%20CIN%20-%20U10200WB1906GOI001713%201.pdf?sv=2023-01-03&st=2025-07-21T08%3A29%3A02Z&se=2025-09-22T08%3A29%3A00Z&sr=b&sp=r&sig=nzrz1K9Iurt%2BBXom%2FB%2BMPTFMFP3PRnIvEsipAX10Ig4%3D\",\n    \"questions\": [\n        \"What is the grace period for premium payment under the Arogya Sanjeevani Policy?\",\n        \"What is the waiting period for pre-existing diseases (PED) to be covered?\",\n        \"Does this policy cover maternity expenses, and what are the conditions?\",\n        \"What is the waiting period for cataract surgery?\",\n        \"Are the medical expenses for an organ donor covered under this policy?\"\n    ]\n}"
        },
        "url": {
          "raw": "{{base_url}}/hackrx/run",
          "host": ["{{base_url}}"],
          "path": ["hackrx", "run"]
        }
      }
    },
    {
      "name": "4. Test with Single Question",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{auth_token}}",
            "type": "text"
          },
          {
            "key": "Content-Type",
            "value": "application/json",
            "type": "text"
          },
          {
            "key": "Accept",
            "value": "application/json",
            "type": "text"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n    \"documents\": \"https://hackrx.blob.core.windows.net/assets/Arogya%20Sanjeevani%20Policy%20-%20CIN%20-%20U10200WB1906GOI001713%201.pdf?sv=2023-01-03&st=2025-07-21T08%3A29%3A02Z&se=2025-09-22T08%3A29%3A00Z&sr=b&sp=r&sig=nzrz1K9Iurt%2BBXom%2FB%2BMPTFMFP3PRnIvEsipAX10Ig4%3D\",\n    \"questions\": [\n        \"What is the grace period for premium payment?\"\n    ]\n}"
        },
        "url": {
          "raw": "{{base_url}}/hackrx/run",
          "host": ["{{base_url}}"],
          "path": ["hackrx", "run"]
        }
      }
    },
    {
      "name": "5. Webhook Submission Test",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{auth_token}}",
            "type": "text"
          },
          {
            "key": "Content-Type",
            "value": "application/json",
            "type": "text"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n    \"webhook_url\": \"https://your-webhook-endpoint.com/api/v1/hackrx/run\",\n    \"submission_notes\": \"Local testing submission\"\n}"
        },
        "url": {
          "raw": "{{base_url}}/api/v1/webhook/submit",
          "host": ["{{base_url}}"],
          "path": ["api", "v1", "webhook", "submit"]
        }
      }
    },
    {
      "name": "6. Error Test - Invalid Token",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer invalid_token_here",
            "type": "text"
          },
          {
            "key": "Content-Type",
            "value": "application/json",
            "type": "text"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n    \"documents\": \"https://example.com/test.pdf\",\n    \"questions\": [\"Test question\"]\n}"
        },
        "url": {
          "raw": "{{base_url}}/hackrx/run",
          "host": ["{{base_url}}"],
          "path": ["hackrx", "run"]
        }
      }
    },
    {
      "name": "7. Error Test - Invalid JSON",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Authorization",
            "value": "Bearer {{auth_token}}",
            "type": "text"
          },
          {
            "key": "Content-Type",
            "value": "application/json",
            "type": "text"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n    \"documents\": \"https://example.com/test.pdf\",\n    \"questions\": []\n}"
        },
        "url": {
          "raw": "{{base_url}}/hackrx/run",
          "host": ["{{base_url}}"],
          "path": ["hackrx", "run"]
        }
      }
    }
  ]
}
```

## 🧪 Testing Sequence

### Test 1: Health Check
1. Select the "1. Health Check" request
2. Click "Send"
3. **Expected Response (200 OK):**
```json
{
    "status": "healthy",
    "message": "All services operational",
    "timestamp": 1703123456.789
}
```

### Test 2: Root Endpoint
1. Select the "2. Root Endpoint" request
2. Click "Send"
3. **Expected Response (200 OK):**
```json
{
    "message": "HackRx - LLM-Powered Query-Retrieval System",
    "version": "1.0.0",
    "description": "Production-grade intelligent document processing and query system",
    "endpoints": {
        "health": "/api/v1/health",
        "evaluation": "/hackrx/run",
        "webhook_submit": "/api/v1/webhook/submit",
        "webhook_status": "/api/v1/webhook/status/{submission_id}",
        "docs": "/docs"
    }
}
```

### Test 3: Main Evaluation (5 Questions)
1. Select the "3. Main Evaluation - Insurance Policy" request
2. Click "Send"
3. **Expected Response (200 OK):**
```json
{
    "answers": [
        "A grace period of thirty days is provided for premium payment after the due date to renew or continue the policy without losing continuity benefits.",
        "There is a waiting period of thirty-six (36) months of continuous coverage from the first policy inception for pre-existing diseases and their direct complications to be covered.",
        "Yes, the policy covers maternity expenses, including childbirth and lawful medical termination of pregnancy. To be eligible, the female insured person must have been continuously covered for at least 24 months.",
        "The policy has a specific waiting period of two (2) years for cataract surgery.",
        "Yes, the policy indemnifies the medical expenses for the organ donor's hospitalization for the purpose of harvesting the organ, provided the organ is for an insured person."
    ]
}
```

### Test 4: Single Question Test
1. Select the "4. Test with Single Question" request
2. Click "Send"
3. **Expected Response (200 OK):**
```json
{
    "answers": [
        "A grace period of thirty days is provided for premium payment after the due date to renew or continue the policy without losing continuity benefits."
    ]
}
```

### Test 5: Webhook Submission
1. Select the "5. Webhook Submission Test" request
2. Click "Send"
3. **Expected Response (200 OK):**
```json
{
    "status": "success",
    "message": "Webhook URL submitted successfully for testing",
    "submission_id": "uuid-here",
    "timestamp": 1703123456.789,
    "webhook_url": "https://your-webhook-endpoint.com/api/v1/hackrx/run",
    "notes": "Local testing submission"
}
```

### Test 6: Authentication Error
1. Select the "6. Error Test - Invalid Token" request
2. Click "Send"
3. **Expected Response (401 Unauthorized):**
```json
{
    "detail": "Invalid authentication token"
}
```

### Test 7: Validation Error
1. Select the "7. Error Test - Invalid JSON" request
2. Click "Send"
3. **Expected Response (422 Unprocessable Entity):**
```json
{
    "detail": [
        {
            "type": "value_error",
            "loc": ["body", "questions"],
            "msg": "ensure this value has at least 1 items"
        }
    ]
}
```

## 📊 Performance Testing

### Response Time Expectations
- **Health Check**: < 100ms
- **Single Question**: < 2 seconds
- **5 Questions**: < 5 seconds
- **10 Questions**: < 8 seconds

### Load Testing (Optional)
1. Use Postman's "Runner" feature
2. Set iterations to 10
3. Set delay between requests to 1 second
4. Monitor response times and error rates

## 🔍 Debugging Tips

### Check Server Logs
Monitor your terminal where the server is running for:
- Request processing logs
- Error messages
- Performance metrics

### Common Issues & Solutions

#### 1. **Connection Refused**
- Ensure server is running on `http://localhost:8001`
- Check if port 8001 is available
- Try `netstat -an | findstr 8001` (Windows) or `lsof -i :8001` (Mac/Linux)

#### 2. **401 Unauthorized**
- Verify auth token is correct: `5ef88cae5f4c94f4fac6b46623fdc0d694813052870019908dd3bbff4c52e1f8`
- Check Authorization header format: `Bearer <token>`

#### 3. **500 Internal Server Error**
- Check server logs for detailed error messages
- Verify API keys are set in `.env` file
- Ensure all dependencies are installed

#### 4. **Timeout Errors**
- Increase Postman timeout settings (Settings → General → Request timeout)
- Check server performance and memory usage
- Consider reducing number of questions for testing

#### 5. **Document Processing Errors**
- Verify document URL is accessible
- Check if document format is supported (PDF, DOCX, EML)
- Ensure document is not corrupted or password-protected

## 🎯 Success Criteria

Your local testing is successful when:

✅ **Health Check** returns 200 with "healthy" status  
✅ **Authentication** works with Bearer token  
✅ **Main Endpoint** processes questions and returns answers  
✅ **Response Format** matches expected JSON structure  
✅ **Error Handling** works for invalid requests  
✅ **Performance** meets timing expectations  
✅ **All Questions** are answered (not empty responses)  

## 📝 Testing Checklist

- [ ] Server starts without errors
- [ ] Health check endpoint responds
- [ ] Authentication works correctly
- [ ] Main evaluation endpoint processes requests
- [ ] Response format is correct
- [ ] Error handling works for invalid inputs
- [ ] Performance is acceptable
- [ ] All questions receive meaningful answers
- [ ] Webhook submission works
- [ ] API documentation is accessible at `/docs`

## 🚀 Next Steps

Once local testing is successful:

1. **Deploy to Production**: Follow the deployment guide
2. **Update Environment**: Change `base_url` to your production domain
3. **Run Production Tests**: Use the same collection with production URL
4. **Submit for Evaluation**: Ensure all tests pass in production

## 📞 Support

If you encounter issues:
1. Check server logs for detailed error messages
2. Verify all environment variables are set
3. Ensure all dependencies are installed
4. Test with simpler requests first
5. Check the `/docs` endpoint for API documentation

Happy Testing! 🎉 
# 🎯 Postman Testing Guide for HackRx Submission

## 📋 Quick Setup

### 1. Import Collection
1. Open Postman
2. Click "Import" → "Raw text"
3. Copy and paste the collection JSON below

### 2. Set Environment Variables
1. Create new environment called "HackRx Production"
2. Add these variables:
   - `base_url`: `https://your-deployed-domain.com` (replace with your actual domain)
   - `auth_token`: `5ef88cae5f4c94f4fac6b46623fdc0d694813052870019908dd3bbff4c52e1f8`

---

## 🚀 Main Endpoint Test (Required for Submission)

### **POST /hackrx/run**

**URL:** `{{base_url}}/hackrx/run`

**Headers:**
```
Authorization: Bearer {{auth_token}}
Content-Type: application/json
Accept: application/json
```

**Body (JSON):**
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

**Expected Response:**
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

---

## 🏥 Health Check Test

### **GET /api/v1/health**

**URL:** `{{base_url}}/api/v1/health`

**Headers:**
```
Authorization: Bearer {{auth_token}}
```

**Expected Response:**
```json
{
    "status": "healthy",
    "message": "All services operational",
    "timestamp": 1703123456.789
}
```

---

## 📤 Webhook Submission Test

### **POST /api/v1/webhook/submit**

**URL:** `{{base_url}}/api/v1/webhook/submit`

**Headers:**
```
Authorization: Bearer {{auth_token}}
Content-Type: application/json
```

**Body (JSON):**
```json
{
    "webhook_url": "https://your-webhook-endpoint.com/api/v1/hackrx/run",
    "submission_notes": "This is a test submission for the HackRx evaluation system."
}
```

---

## 📊 Webhook Status Test

### **GET /api/v1/webhook/status/{submission_id}**

**URL:** `{{base_url}}/api/v1/webhook/status/{{submission_id}}`

**Headers:**
```
Authorization: Bearer {{auth_token}}
```

---

## 🏠 Root Endpoint Test

### **GET /**

**URL:** `{{base_url}}/`

**Headers:** None required

---

## 📋 Postman Collection JSON

```json
{
  "info": {
    "name": "HackRx API - Submission Testing",
    "description": "Collection for testing HackRx API endpoints",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "variable": [
    {
      "key": "base_url",
      "value": "https://your-deployed-domain.com",
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
      "name": "Health Check",
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
      "name": "Main Evaluation Endpoint",
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
          "raw": "{\n    \"documents\": \"https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D\",\n    \"questions\": [\n        \"What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?\",\n        \"What is the waiting period for pre-existing diseases (PED) to be covered?\",\n        \"Does this policy cover maternity expenses, and what are the conditions?\",\n        \"What is the waiting period for cataract surgery?\",\n        \"Are the medical expenses for an organ donor covered under this policy?\",\n        \"What is the No Claim Discount (NCD) offered in this policy?\",\n        \"Is there a benefit for preventive health check-ups?\",\n        \"How does the policy define a 'Hospital'?\",\n        \"What is the extent of coverage for AYUSH treatments?\",\n        \"Are there any sub-limits on room rent and ICU charges for Plan A?\"\n    ]\n}"
        },
        "url": {
          "raw": "{{base_url}}/hackrx/run",
          "host": ["{{base_url}}"],
          "path": ["hackrx", "run"]
        }
      }
    },
    {
      "name": "Webhook Submission",
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
          "raw": "{\n    \"webhook_url\": \"https://your-webhook-endpoint.com/api/v1/hackrx/run\",\n    \"submission_notes\": \"This is a test submission for the HackRx evaluation system.\"\n}"
        },
        "url": {
          "raw": "{{base_url}}/api/v1/webhook/submit",
          "host": ["{{base_url}}"],
          "path": ["api", "v1", "webhook", "submit"]
        }
      }
    },
    {
      "name": "Root Endpoint",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "{{base_url}}/",
          "host": ["{{base_url}}"],
          "path": [""]
        }
      }
    }
  ]
}
```

---

## ✅ Testing Checklist

Before submitting, ensure:

- [ ] **Health Check** returns 200 with "healthy" status
- [ ] **Main Endpoint** returns 200 with correct response format
- [ ] **Authentication** works with Bearer token
- [ ] **Response time** is under 5 seconds
- [ ] **All 10 questions** are answered
- [ ] **Error handling** works for invalid requests
- [ ] **CORS** is properly configured
- [ ] **Content-Type** headers are correct

---

## 🚨 Common Issues & Solutions

### 1. **401 Unauthorized**
- Check if Bearer token is correct
- Ensure token is in the Authorization header

### 2. **422 Validation Error**
- Verify JSON format is correct
- Check Content-Type header is set to application/json

### 3. **500 Internal Server Error**
- Check server logs
- Verify Google API key is set correctly
- Ensure all dependencies are installed

### 4. **Timeout Errors**
- Increase timeout in Postman settings
- Check server performance and memory usage

---

## 🎯 Final Submission

Your endpoint should be accessible at:
```
https://your-deployed-domain.com/hackrx/run
```

**Required for submission:**
- ✅ Endpoint is publicly accessible
- ✅ Authentication works
- ✅ Response format matches specification
- ✅ Performance is acceptable
- ✅ Error handling is implemented 
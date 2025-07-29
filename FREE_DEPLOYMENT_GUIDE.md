# 🆓 Free Deployment Options for HackRx

## 🎯 Best Free Deployment Platforms

Here are the **best free options** for deploying your HackRx API:

---

## 🚂 1. Railway (HIGHLY RECOMMENDED)

**Why Railway?**
- ✅ **Completely free** for hackathon projects
- ✅ **Automatic deployment** from GitHub
- ✅ **Easy setup** - just connect your repo
- ✅ **Fast deployment** - 2-3 minutes
- ✅ **Custom domain** support
- ✅ **SSL certificate** included

### **Step-by-Step Setup:**

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Go to Railway**
   - Visit [railway.app](https://railway.app)
   - Sign up with GitHub

3. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

4. **Configure Environment Variables**
   - Go to "Variables" tab
   - Add: `GOOGLE_API_KEY=your_google_api_key_here`

5. **Deploy**
   - Railway will automatically detect it's a Python app
   - It will install dependencies from `requirements.txt`
   - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

6. **Get Your URL**
   - Railway will give you a URL like: `https://your-app-name.railway.app`
   - Your endpoint will be: `https://your-app-name.railway.app/hackrx/run`

---

## 🌐 2. Render (EXCELLENT ALTERNATIVE)

**Why Render?**
- ✅ **Free tier** available
- ✅ **Easy GitHub integration**
- ✅ **Automatic deployments**
- ✅ **Custom domains**
- ✅ **SSL included**

### **Step-by-Step Setup:**

1. **Go to Render**
   - Visit [render.com](https://render.com)
   - Sign up with GitHub

2. **Create New Web Service**
   - Click "New +"
   - Select "Web Service"
   - Connect your GitHub repository

3. **Configure Service**
   - **Name**: `hackrx-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Set Environment Variables**
   - Go to "Environment" tab
   - Add: `GOOGLE_API_KEY=your_google_api_key_here`

5. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (5-10 minutes)

6. **Get Your URL**
   - Your endpoint will be: `https://your-app-name.onrender.com/hackrx/run`

---

## 🐳 3. Fly.io (GREAT FOR DOCKER)

**Why Fly.io?**
- ✅ **Free tier** with generous limits
- ✅ **Docker support**
- ✅ **Global deployment**
- ✅ **Fast performance**

### **Step-by-Step Setup:**

1. **Install Fly CLI**
   ```bash
   # macOS
   brew install flyctl
   
   # Windows
   powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
   
   # Linux
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login to Fly**
   ```bash
   fly auth login
   ```

3. **Deploy**
   ```bash
   fly launch
   # Follow the prompts
   # Set app name: hackrx-api
   # Select region: Choose closest to you
   ```

4. **Set Environment Variables**
   ```bash
   fly secrets set GOOGLE_API_KEY=your_google_api_key_here
   ```

5. **Deploy**
   ```bash
   fly deploy
   ```

6. **Get Your URL**
   - Your endpoint will be: `https://hackrx-api.fly.dev/hackrx/run`

---

## ☁️ 4. Google Cloud Run (FREE TIER)

**Why Google Cloud Run?**
- ✅ **Free tier** with generous limits
- ✅ **Serverless**
- ✅ **Auto-scaling**
- ✅ **Pay only for usage**

### **Step-by-Step Setup:**

1. **Install Google Cloud CLI**
   ```bash
   # Download from: https://cloud.google.com/sdk/docs/install
   ```

2. **Initialize Project**
   ```bash
   gcloud init
   gcloud config set project YOUR_PROJECT_ID
   ```

3. **Enable APIs**
   ```bash
   gcloud services enable run.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   ```

4. **Deploy**
   ```bash
   gcloud run deploy hackrx-api \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars GOOGLE_API_KEY=your_google_api_key_here
   ```

5. **Get Your URL**
   - Your endpoint will be: `https://hackrx-api-xxxxx-uc.a.run.app/hackrx/run`

---

## 🐙 5. Heroku (FREE TIER DISCONTINUED)

**Note**: Heroku discontinued their free tier, but if you have existing credits:

1. **Install Heroku CLI**
   ```bash
   # Download from: https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login and Deploy**
   ```bash
   heroku login
   heroku create hackrx-api
   heroku config:set GOOGLE_API_KEY=your_google_api_key_here
   git push heroku main
   ```

---

## 🎯 **RECOMMENDED CHOICE: Railway**

For hackathon submissions, I **strongly recommend Railway** because:

1. **Fastest setup** - 5 minutes total
2. **Most reliable** - rarely goes down
3. **Best free tier** - generous limits
4. **Automatic deployments** - push to GitHub, auto-deploy
5. **Great documentation** - easy to troubleshoot

---

## 🧪 Testing Your Deployment

### **1. Health Check**
```bash
curl -X GET "https://your-app.railway.app/api/v1/health" \
  -H "Authorization: Bearer 5ef88cae5f4c94f4fac6b46623fdc0d694813052870019908dd3bbff4c52e1f8"
```

### **2. Main Endpoint Test**
```bash
curl -X POST "https://your-app.railway.app/hackrx/run" \
  -H "Authorization: Bearer 5ef88cae5f4c94f4fac6b46623fdc0d694813052870019908dd3bbff4c52e1f8" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "documents": "https://hackrx.blob.core.windows.net/assets/Arogya%20Sanjeevani%20Policy%20-%20CIN%20-%20U10200WB1906GOI001713%201.pdf?sv=2023-01-03&st=2025-07-21T08%3A29%3A02Z&se=2025-09-22T08%3A29%3A00Z&sr=b&sp=r&sig=nzrz1K9Iurt%2BBXom%2FB%2BMPTFMFP3PRnIvEsipAX10Ig4%3D",
    "questions": [
      "What is the grace period for premium payment under the Arogya Sanjeevani Policy?"
    ]
  }'
```

### **3. Using Postman**
- Import the collection from `POSTMAN_SUBMISSION_GUIDE.md`
- Set `base_url` to your deployed domain
- Test all endpoints

---

## 🚨 Troubleshooting

### **Common Issues:**

1. **Build Fails**
   - Check `requirements.txt` is correct
   - Ensure all dependencies are listed
   - Check Python version compatibility

2. **Environment Variables**
   - Make sure `GOOGLE_API_KEY` is set correctly
   - Check for typos in variable names

3. **Port Issues**
   - Use `$PORT` environment variable
   - Don't hardcode port numbers

4. **Memory Issues**
   - Some platforms have memory limits
   - Optimize your application if needed

### **Debug Commands:**

```bash
# Check logs (Railway)
railway logs

# Check logs (Render)
# Use the Render dashboard

# Check logs (Fly.io)
fly logs

# Check logs (Google Cloud Run)
gcloud logs read --service=hackrx-api
```

---

## 📝 Final Steps

1. **Deploy** using Railway (recommended)
2. **Test** with Postman
3. **Verify** all endpoints work
4. **Submit** your endpoint URL

**Your submission URL will be:**
```
https://your-app-name.railway.app/hackrx/run
```

---

## 🎉 Success!

Once deployed, your API will be:
- ✅ **Publicly accessible**
- ✅ **24/7 available**
- ✅ **Automatically scaled**
- ✅ **SSL secured**
- ✅ **Ready for submission**

**Good luck with your hackathon! 🚀** 
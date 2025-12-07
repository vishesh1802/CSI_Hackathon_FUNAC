# Azure AI Foundry Verification Steps

## ✅ How to Verify Your Azure AI Agent is Working

### Method 1: Check in Azure Portal (Easiest)

1. **Go to Azure Portal**: https://portal.azure.com
2. **Find your resource**: Search for "csi-hackathon-resource"
3. **Check Deployment**:
   - Click "Model deployments"
   - Find "gpt-4o-2"
   - Status should be: **"Succeeded"** ✅

4. **Check Metrics** (after using):
   - Click on "gpt-4o-2"
   - Go to "Metrics" tab
   - You should see:
     - Request count (API calls)
     - Token usage
     - Errors (should be 0)

### Method 2: Test in Azure AI Studio

1. **Open Azure AI Studio**:
   - From your OpenAI resource, click "Azure AI Studio"
   - Or go to: https://ai.azure.com

2. **Test in Playground**:
   - Click "Chat" or "Playground"
   - Select deployment: **gpt-4o-2**
   - Type a test message
   - If you get a response = **Working!** ✅

### Method 3: Test Your Backend

1. **Start backend**:
   ```bash
   ./start_backend.sh
   ```

2. **Look for in logs**:
   - ✅ `"Azure OpenAI client initialized successfully"` = **WORKING!**
   - ❌ `"Azure OpenAI credentials not found"` = Not configured

3. **Test API**:
   ```bash
   curl http://localhost:8000/api/stats
   ```
   
   Check response for `"ai_available": true`

### Method 4: Full Integration Test

1. **Start backend**: `./start_backend.sh`
2. **Start frontend**: `./start_frontend.sh` (new terminal)
3. **Upload a file** from Hackathon_Data
4. **Select an event**
5. **Click "Score Triage"**
6. **Check for**:
   - Real AI recommendations (not mock)
   - 5-section maintenance report
   - Token usage displayed

## 📊 What to Look For in Azure Portal

### ✅ Working Correctly:
- Deployment status: **"Succeeded"** (green)
- Metrics show API requests
- No errors in logs
- Token usage increasing
- Playground responds

### ❌ Not Working:
- Deployment status: "Failed" or "Pending"
- No requests in metrics
- Errors in logs
- Playground doesn't respond
- 401/403 errors

## 🔍 Detailed Verification

### In Azure Portal → Your Resource:

1. **Overview Tab**:
   - Check resource status
   - Verify it's running

2. **Model Deployments**:
   - Deployment: **gpt-4o-2**
   - Status: **Succeeded**
   - Provisioning state: **Succeeded**

3. **Keys and Endpoint**:
   - Verify endpoint matches your .env
   - Check keys are active

4. **Metrics** (after usage):
   - **Requests**: Should show API calls
   - **Tokens**: Should show usage
   - **Errors**: Should be 0

5. **Logs**:
   - Check for errors
   - Verify API calls are being made

## 🧪 Quick Test

Run this to test connection:
```bash
# Install dependencies first
pip install -r requirements.txt

# Then test
python3 scripts/test_azure_ai.py
```

## ✅ Status Check

**Your current setup:**
- ✅ Credentials configured in `.env`
- ✅ Deployment: `gpt-4o-2`
- ✅ Endpoint: `https://csi-hackathon-resource.cognitiveservices.azure.com/`
- ✅ API Version: `2024-12-01-preview`

**To verify it's working:**
1. Start backend: `./start_backend.sh`
2. Check logs for: "Azure OpenAI client initialized successfully"
3. Test with a file upload in the UI
4. Check Azure Portal metrics for usage

## 🎯 Bottom Line

**Is it working?**
- ✅ If backend logs show "initialized successfully" = **YES**
- ✅ If Azure Portal metrics show requests = **YES**
- ✅ If playground responds = **YES**
- ❌ If you see "credentials not found" = **NO** (check .env)

Your configuration looks correct! Start the backend to verify it's actually connecting.


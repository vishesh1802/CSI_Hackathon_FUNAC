# Quick Azure AI Agent Verification

## ✅ Is It Working? Quick Check

### Method 1: Check Backend Logs
```bash
./start_backend.sh
```

**Look for:**
- ✅ `"Azure OpenAI client initialized successfully"` = **WORKING!**
- ❌ `"Azure OpenAI credentials not found"` = Not configured

### Method 2: Check .env File
```bash
cat .env | grep AZURE_OPENAI
```

Should show:
- ✅ API_KEY (long string)
- ✅ ENDPOINT (https://...)
- ✅ DEPLOYMENT_NAME (gpt-4o-2)
- ✅ API_VERSION

## 🔍 Verify in Azure AI Foundry Portal

### Step 1: Go to Azure Portal
1. Visit: https://portal.azure.com
2. Find your resource: **csi-hackathon-resource**
3. Click on it

### Step 2: Check Deployment Status
1. Click **"Model deployments"** (left menu)
2. Find: **gpt-4o-2**
3. Check status:
   - ✅ **"Succeeded"** = Working
   - ❌ **"Failed"** or **"Pending"** = Not ready

### Step 3: Check Metrics (After Using)
1. Click on **gpt-4o-2** deployment
2. Go to **"Metrics"** tab
3. Look for:
   - **Request count**: Should show API calls
   - **Token usage**: Should show tokens consumed
   - **Errors**: Should be 0

### Step 4: Test in Playground
1. Click **"Azure AI Studio"** or **"Go to Studio"**
2. Click **"Chat"** or **"Playground"**
3. Select deployment: **gpt-4o-2**
4. Type: `Test message`
5. If you get a response = **Working!**

### Step 5: Check Usage
1. In Azure Portal → Your resource
2. Click **"Usage"** or **"Metrics"**
3. You should see:
   - Total tokens used
   - API requests made
   - Cost (if any)

## 🧪 Test Your System

### Start Backend
```bash
./start_backend.sh
```

### Test API Endpoint
```bash
curl -X POST http://localhost:8000/api/triage/score \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "test-1",
    "event_type": "error_log",
    "timestamp": "2025-11-17T09:00:00",
    "description": "SRVO-160 - Collision detected"
  }'
```

**Check response for:**
- ✅ `"ai_available": true`
- ✅ `"maintenance_report"` exists
- ✅ `"token_usage"` has numbers

## ✅ Verification Checklist

- [ ] `.env` file has all credentials
- [ ] Deployment exists in Azure Portal
- [ ] Deployment status: "Succeeded"
- [ ] Backend logs show "initialized successfully"
- [ ] API calls return responses
- [ ] Metrics show usage in Azure Portal
- [ ] Playground works in Azure AI Studio

## 🎯 Quick Answer

**Is it working?** Check backend logs when you start it:
- ✅ "Azure OpenAI client initialized successfully" = **YES, WORKING!**
- ❌ "Azure OpenAI credentials not found" = **NO, check .env file**


# How to Verify Azure AI Agent in Azure AI Foundry

## ✅ Quick Test (Local)

### Option 1: Run Test Script
```bash
python3 scripts/test_azure_ai.py
```

This will:
- ✅ Check credentials
- ✅ Test API connection
- ✅ Test with sample robot event
- ✅ Verify AI agent is working

### Option 2: Start Backend
```bash
./start_backend.sh
```

Look for in logs:
- ✅ `"Azure OpenAI client initialized successfully"` = Working!
- ❌ `"Azure OpenAI credentials not found"` = Not configured

## 🔍 Verification in Azure AI Foundry Portal

### Step 1: Access Azure AI Studio
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your OpenAI resource: **csi-hackathon-resource**
3. Click **"Azure AI Studio"** or **"Go to Azure AI Studio"**

### Step 2: Check Model Deployment
1. In Azure AI Studio, click **"Deployments"** in left menu
2. Find your deployment: **gpt-4o-2**
3. Verify:
   - ✅ **Status**: "Succeeded" (green checkmark)
   - ✅ **Model**: gpt-4o-2
   - ✅ **Provisioning state**: Succeeded

### Step 3: Check Usage & Metrics
1. Click on your deployment: **gpt-4o-2**
2. Go to **"Metrics"** tab
3. You should see:
   - **Request count**: Number of API calls
   - **Token usage**: Prompt + completion tokens
   - **Latency**: Response times
   - **Errors**: Should be 0 if working

### Step 4: Test in Playground
1. In Azure AI Studio, click **"Chat"** or **"Playground"**
2. Select your deployment: **gpt-4o-2**
3. Test with a message:
   ```
   Analyze this FANUC robot event: SRVO-160 - Collision detected on J3
   ```
4. You should get a response - this confirms the model works

### Step 5: Check API Usage
1. In Azure Portal → Your OpenAI resource
2. Click **"Usage"** or **"Metrics"**
3. Look for:
   - **Total tokens used**
   - **API calls made**
   - **Cost tracking**

## 📊 What to Look For

### ✅ Signs It's Working:
- Deployment status: **Succeeded**
- Metrics show API calls being made
- No errors in metrics
- Playground responds correctly
- Your backend logs show: "Azure OpenAI client initialized successfully"

### ❌ Signs It's NOT Working:
- Deployment status: **Failed** or **Pending**
- Metrics show 0 requests
- Errors in metrics/logs
- Playground doesn't respond
- Backend logs show: "Azure OpenAI credentials not found"

## 🧪 Test Endpoints

### Test 1: Health Check
```bash
curl http://localhost:8000/
```
Should return: `{"status": "healthy"}`

### Test 2: Triage Analysis
```bash
curl -X POST http://localhost:8000/api/triage/score \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "test-1",
    "event_type": "error_log",
    "timestamp": "2025-11-17T09:00:00",
    "description": "SRVO-160 - Collision detected",
    "raw_data": {"error_code": "SRVO-160", "joint": "J3"}
  }'
```

Check response for:
- ✅ `"ai_available": true`
- ✅ `"maintenance_report"` with 5 sections
- ✅ `"token_usage"` with actual numbers

## 📈 Monitoring in Azure Portal

### Real-Time Monitoring:
1. **Azure Portal** → Your OpenAI resource
2. **Metrics** → See live usage
3. **Logs** → Check for errors
4. **Cost Management** → Track spending

### Key Metrics to Monitor:
- **Requests per minute**: Should match your usage
- **Tokens per minute**: Should show activity
- **Error rate**: Should be 0%
- **Latency**: Should be reasonable (<5 seconds)

## 🔧 Troubleshooting

### Issue: "Deployment not found"
**Solution**: 
- Check deployment name matches exactly
- Verify deployment is "Succeeded" in Azure Portal
- Wait a few minutes after creating deployment

### Issue: "401 Unauthorized"
**Solution**:
- Check API key is correct
- Verify key hasn't expired
- Try regenerating key in Azure Portal

### Issue: "429 Rate Limit"
**Solution**:
- You're making too many requests
- Check rate limits: 250,000 tokens/min, 1,500 requests/min
- Add delays between requests

### Issue: "Model not available"
**Solution**:
- Check deployment status in Azure Portal
- Verify model is deployed
- Check region availability

## ✅ Verification Checklist

- [ ] Credentials in `.env` file
- [ ] Deployment exists in Azure Portal
- [ ] Deployment status: "Succeeded"
- [ ] Backend starts without errors
- [ ] Test script passes
- [ ] API calls return responses
- [ ] Metrics show usage in Azure Portal
- [ ] Playground works in Azure AI Studio
- [ ] Token usage is tracked

## 🎯 Quick Verification Command

```bash
# Test everything at once
python3 scripts/test_azure_ai.py
```

If all tests pass, your Azure AI agent is working correctly! ✅


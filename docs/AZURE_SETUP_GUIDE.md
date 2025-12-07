# Azure AI Foundry Setup Guide

## Required Credentials

You need **3 pieces of information** from your Azure OpenAI resource:

### 1. API Key (`AZURE_OPENAI_API_KEY`)
- **What it is**: Authentication key for your Azure OpenAI resource
- **Where to find**: Azure Portal → Your OpenAI resource → Keys and Endpoint
- **Format**: Long alphanumeric string (e.g., `abc123def456...`)
- **Security**: Keep this secret! Never commit to git.

### 2. Endpoint URL (`AZURE_OPENAI_ENDPOINT`)
- **What it is**: The base URL for your Azure OpenAI resource
- **Where to find**: Azure Portal → Your OpenAI resource → Keys and Endpoint
- **Format**: `https://your-resource-name.openai.azure.com/`
- **Example**: `https://my-robot-ai.openai.azure.com/`

### 3. Deployment Name (`AZURE_OPENAI_DEPLOYMENT_NAME`)
- **What it is**: Name of your deployed model in Azure
- **Where to find**: Azure Portal → Your OpenAI resource → Model deployments
- **Format**: Usually the model name (e.g., `gpt-4`, `gpt-35-turbo`)
- **Note**: You must deploy a model first before you can use it

### 4. API Version (Optional)
- **Default**: `2024-02-15-preview` (already set)
- **What it is**: API version for Azure OpenAI
- **Usually**: Don't need to change this

## How to Get Credentials

### Step 1: Create Azure OpenAI Resource

1. Go to [Azure Portal](https://portal.azure.com)
2. Click "Create a resource"
3. Search for "Azure OpenAI"
4. Click "Create"
5. Fill in:
   - **Subscription**: Your Azure subscription
   - **Resource group**: Create new or use existing
   - **Region**: Choose closest to you (e.g., East US, West Europe)
   - **Name**: e.g., `robot-maintenance-ai`
   - **Pricing tier**: Choose based on your needs
6. Click "Review + create" → "Create"

### Step 2: Deploy a Model

1. Go to your Azure OpenAI resource
2. Click "Model deployments" in left menu
3. Click "Create"
4. Choose:
   - **Model**: See recommendations below
   - **Deployment name**: e.g., `gpt-4` or `gpt-35-turbo`
   - **Advanced options**: Use defaults
5. Click "Create" (takes a few minutes)

### Step 3: Get Your Credentials

1. In your Azure OpenAI resource, click "Keys and Endpoint"
2. Copy:
   - **KEY 1** or **KEY 2** (either works)
   - **Endpoint** (full URL)
3. Note your **Deployment name** from Step 2

### Step 4: Configure Your Project

1. Copy `config.env.example` to `.env`:
   ```bash
   cp config.env.example .env
   ```

2. Edit `.env` and fill in your credentials:
   ```bash
   AZURE_OPENAI_API_KEY=your_actual_key_here
   AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
   AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
   AZURE_OPENAI_API_VERSION=2024-02-15-preview
   ```

3. **Important**: Add `.env` to `.gitignore` (already done)

## Model Recommendations for Robot Maintenance

### 🏆 Best Choice: GPT-4
**For**: Production, critical maintenance decisions

**Pros:**
- ✅ Best reasoning and analysis
- ✅ Most accurate technical recommendations
- ✅ Better at understanding FANUC error codes
- ✅ Excellent for complex diagnostics

**Cons:**
- ❌ More expensive (~$0.03 per 1K input tokens)
- ❌ Slower response time

**Best for**: Critical events, complex diagnostics, production use

### 💰 Cost-Effective: GPT-3.5 Turbo
**For**: Development, testing, routine events

**Pros:**
- ✅ Much cheaper (~$0.0015 per 1K input tokens)
- ✅ Faster response time
- ✅ Good enough for routine maintenance
- ✅ Great for development/testing

**Cons:**
- ❌ Less sophisticated reasoning
- ❌ May miss subtle technical details

**Best for**: Development, routine events, cost-sensitive scenarios

### 🚀 Fast & Light: GPT-4 Turbo
**For**: Balance of quality and speed

**Pros:**
- ✅ Better than GPT-3.5, faster than GPT-4
- ✅ Good balance of cost and quality
- ✅ Faster than GPT-4

**Cons:**
- ❌ More expensive than GPT-3.5
- ❌ May not be available in all regions

**Best for**: When you need good quality with faster responses

### 📊 Model Comparison

| Model | Cost (per 1K tokens) | Speed | Quality | Best For |
|-------|---------------------|-------|---------|----------|
| **GPT-4** | ~$0.03 | Slow | ⭐⭐⭐⭐⭐ | Critical diagnostics |
| **GPT-4 Turbo** | ~$0.01 | Medium | ⭐⭐⭐⭐ | Balanced use |
| **GPT-3.5 Turbo** | ~$0.0015 | Fast | ⭐⭐⭐ | Routine events |

## Recommended Setup for Hackathon

### Option 1: GPT-4 (Recommended for Demo)
```bash
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
```
- **Why**: Best quality for impressive demo
- **Cost**: ~$0.50-2.00 for full demo (depending on usage)
- **Quality**: Excellent technical recommendations

### Option 2: GPT-3.5 Turbo (Budget-Friendly)
```bash
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-35-turbo
```
- **Why**: Much cheaper, still good quality
- **Cost**: ~$0.10-0.50 for full demo
- **Quality**: Good for most use cases

### Option 3: Hybrid Approach (Smart Routing)
Use different models based on event severity:
- **Critical events** → GPT-4 (best quality)
- **Routine events** → GPT-3.5 Turbo (cost-effective)

*Note: This requires code modification*

## Testing Your Setup

### 1. Check Connection
```bash
cd backend
python -c "from services.azure_ai_service import AzureAIService; ai = AzureAIService(); print('✅ Connected!' if ai.is_available() else '❌ Check credentials')"
```

### 2. Test with Sample Event
Start the backend and test the triage endpoint:
```bash
# Terminal 1: Start backend
./start_backend.sh

# Terminal 2: Test API
curl -X POST http://localhost:8000/api/triage/score \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": "test-1",
    "event_type": "error_log",
    "timestamp": "2025-11-17T09:00:00",
    "description": "SRVO-160 - Collision detected",
    "raw_data": {"error_code": "SRVO-160"}
  }'
```

### 3. Check Logs
Look for:
- ✅ `"Azure OpenAI client initialized successfully"`
- ❌ `"Azure OpenAI credentials not found. Using mock mode."`

## Troubleshooting

### Issue: "Credentials not found"
**Solution**: 
- Check `.env` file exists
- Verify variable names match exactly
- Restart backend after changing `.env`

### Issue: "Model deployment not found"
**Solution**:
- Verify deployment name matches exactly
- Check model is deployed in Azure Portal
- Wait a few minutes after deployment

### Issue: "Rate limit exceeded"
**Solution**:
- You're using the model too fast
- Add delays between requests
- Consider using GPT-3.5 for less critical events

### Issue: "Insufficient quota"
**Solution**:
- Check your Azure subscription quota
- Request quota increase in Azure Portal
- Use GPT-3.5 instead of GPT-4

## Cost Estimation

### Typical Usage (100 events analyzed)
- **GPT-4**: ~$2-5
- **GPT-3.5 Turbo**: ~$0.20-0.50
- **GPT-4 Turbo**: ~$1-2

### Free Tier
Azure OpenAI often provides:
- $200 free credit for new subscriptions
- Enough for testing and demos

## Security Best Practices

1. ✅ **Never commit `.env` to git** (already in `.gitignore`)
2. ✅ **Use environment variables** (not hardcoded)
3. ✅ **Rotate keys regularly**
4. ✅ **Use separate keys for dev/prod**
5. ✅ **Monitor usage** in Azure Portal

## Quick Start Checklist

- [ ] Create Azure OpenAI resource
- [ ] Deploy model (GPT-4 or GPT-3.5 Turbo)
- [ ] Get API key and endpoint
- [ ] Copy `config.env.example` to `.env`
- [ ] Fill in credentials in `.env`
- [ ] Test connection
- [ ] Start backend and verify Azure AI works

## Need Help?

- **Azure OpenAI Docs**: https://learn.microsoft.com/azure/ai-services/openai/
- **Azure Portal**: https://portal.azure.com
- **Pricing Calculator**: https://azure.microsoft.com/pricing/details/cognitive-services/openai-service/


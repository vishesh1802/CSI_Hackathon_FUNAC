# AI Model Recommendations for Robot Maintenance

## Available Models (Updated 2025)

### 🚀 GPT-5 / GPT-5 Pro (Latest - Check Availability)
**Status**: ⚠️ May be available in Azure OpenAI (check your region)

**Note**: GPT-5 exists, but "GPT-5 Pro" may not be the official Azure deployment name. Check your Azure Portal for exact model names.

**Best For**: 
- ✅ **Hackathon demos** (most impressive)
- ✅ Complex technical diagnostics
- ✅ FANUC robot error analysis
- ✅ Production-critical maintenance

**Pros:**
- ✅ **Best reasoning** - Expert-level intelligence
- ✅ **Most accurate** technical recommendations
- ✅ **Superior understanding** of FANUC error codes
- ✅ **Better structured output** (5-section format)
- ✅ **Multi-turn reasoning** for complex problems

**Cons:**
- ❌ **Most expensive** (~$0.05-0.10 per 1K tokens)
- ❌ **Slower** (designed for deeper reasoning)
- ❌ **May not be available** in all Azure regions yet
- ❌ **May timeout** on simple requests (use background mode)

**Cost Estimate**: ~$5-10 for 100 events analyzed

**Deployment Name**: `gpt-5-pro` or `gpt-5`

---

### 🏆 GPT-4 (Recommended for Most Cases)
**Status**: ✅ Widely available

**Best For**:
- ✅ **Hackathon demos** (excellent quality)
- ✅ Production use
- ✅ Complex diagnostics
- ✅ Balanced quality/cost

**Pros:**
- ✅ Excellent reasoning
- ✅ Great technical analysis
- ✅ Good understanding of FANUC codes
- ✅ Reliable structured output
- ✅ Widely available

**Cons:**
- ❌ More expensive than GPT-3.5
- ❌ Slower than GPT-3.5

**Cost Estimate**: ~$2-5 for 100 events

**Deployment Name**: `gpt-4`

---

### ⚡ GPT-4 Turbo
**Status**: ✅ Available

**Best For**:
- ✅ Balance of quality and speed
- ✅ Faster than GPT-4, better than GPT-3.5

**Pros:**
- ✅ Faster than GPT-4
- ✅ Better than GPT-3.5
- ✅ Good quality

**Cons:**
- ❌ More expensive than GPT-3.5
- ❌ Not as good as GPT-4/5

**Cost Estimate**: ~$1-2 for 100 events

**Deployment Name**: `gpt-4-turbo` or `gpt-4-turbo-preview`

---

### 💰 GPT-3.5 Turbo (Budget Option)
**Status**: ✅ Widely available

**Best For**:
- ✅ Development/testing
- ✅ Routine events
- ✅ Cost-sensitive scenarios

**Pros:**
- ✅ Very cheap
- ✅ Fast
- ✅ Good enough for simple cases

**Cons:**
- ❌ Less sophisticated reasoning
- ❌ May miss technical nuances

**Cost Estimate**: ~$0.20-0.50 for 100 events

**Deployment Name**: `gpt-35-turbo` or `gpt-3.5-turbo`

---

## Recommendation for Hackathon

### 🥇 First Choice: GPT-5 Pro
**If available in your Azure region**, use GPT-5 Pro:
- Most impressive for judges
- Best technical analysis
- Shows you're using cutting-edge AI

**Setup**:
```bash
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-5-pro
```

### 🥈 Second Choice: GPT-4
**If GPT-5 Pro not available**, use GPT-4:
- Excellent quality
- Widely available
- Reliable performance

**Setup**:
```bash
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
```

### 🥉 Budget Choice: GPT-3.5 Turbo
**If cost is a major concern**:
- Still good quality
- Much cheaper
- Fast responses

**Setup**:
```bash
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-35-turbo
```

## How to Check Available Models

1. Go to Azure Portal → Your OpenAI resource
2. Click "Model deployments"
3. Click "Create" to see available models
4. Look for:
   - `gpt-5-pro` (if available)
   - `gpt-4`
   - `gpt-4-turbo`
   - `gpt-35-turbo`

## Model Comparison Table

| Model | Quality | Speed | Cost (100 events) | Availability | Best For |
|-------|---------|-------|-------------------|--------------|----------|
| **GPT-5 Pro** | ⭐⭐⭐⭐⭐ | Slow | $5-10 | Limited | Impressive demos |
| **GPT-4** | ⭐⭐⭐⭐ | Medium | $2-5 | ✅ Wide | Hackathon (recommended) |
| **GPT-4 Turbo** | ⭐⭐⭐⭐ | Fast | $1-2 | ✅ Wide | Balanced |
| **GPT-3.5 Turbo** | ⭐⭐⭐ | Fast | $0.20-0.50 | ✅ Wide | Budget |

## Quick Decision Guide

**Want to impress judges?** → GPT-5 Pro (if available) or GPT-4
**Budget conscious?** → GPT-3.5 Turbo
**Need speed?** → GPT-4 Turbo or GPT-3.5 Turbo
**Best overall?** → GPT-4 (reliable, available, good quality)

## Updating Your Configuration

Edit your `.env` file:
```bash
# For GPT-5 Pro (if available)
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-5-pro

# OR for GPT-4 (recommended)
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4

# OR for GPT-3.5 Turbo (budget)
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-35-turbo
```

Then restart your backend:
```bash
./start_backend.sh
```


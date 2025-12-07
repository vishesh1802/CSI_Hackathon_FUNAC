# Azure AI Foundry Credentials Checklist

## ✅ What You Need (3 Required + 1 Optional)

### 1. API Key ⭐ REQUIRED
**Variable**: `AZURE_OPENAI_API_KEY`

**What it looks like**:
```
abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
```

**Where to find**:
1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your **Azure OpenAI resource**
3. Click **"Keys and Endpoint"** in left menu
4. Copy **KEY 1** or **KEY 2** (either works)

**Example**:
```bash
AZURE_OPENAI_API_KEY=abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
```

---

### 2. Endpoint URL ⭐ REQUIRED
**Variable**: `AZURE_OPENAI_ENDPOINT`

**What it looks like**:
```
https://your-resource-name.openai.azure.com/
```

**Where to find**:
1. Same page as above: **"Keys and Endpoint"**
2. Copy the **Endpoint** field
3. Make sure it includes `https://` and ends with `/`

**Example**:
```bash
AZURE_OPENAI_ENDPOINT=https://robot-maintenance-ai.openai.azure.com/
```

---

### 3. Deployment Name ⭐ REQUIRED
**Variable**: `AZURE_OPENAI_DEPLOYMENT_NAME`

**What it looks like**:
```
gpt-4o
```
or
```
gpt-4.1
```
or
```
gpt-5
```

**Where to find**:
1. Go to your Azure OpenAI resource
2. Click **"Model deployments"** in left menu
3. See your deployed models
4. Copy the **Deployment name** (the name you gave it when deploying)

**Note**: You must deploy a model first! If you don't see any deployments:
- Click **"Create"**
- Choose a model (recommend `gpt-4o`)
- Give it a deployment name (e.g., `gpt-4o`)
- Wait for deployment to complete

**Example**:
```bash
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
```

---

### 4. API Version (Optional - Has Default)
**Variable**: `AZURE_OPENAI_API_VERSION`

**Default**: `2024-02-15-preview` (already set in code)

**You usually don't need to change this**, but if you do:
- Check Azure OpenAI documentation for latest version
- Common values: `2024-02-15-preview`, `2024-06-01`, etc.

**Example** (usually not needed):
```bash
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

---

## 📋 Quick Setup Steps

### Step 1: Get Credentials from Azure Portal

1. **Login to Azure Portal**: https://portal.azure.com
2. **Find your OpenAI resource** (or create one if you don't have it)
3. **Get API Key**:
   - Click "Keys and Endpoint"
   - Copy KEY 1 or KEY 2
4. **Get Endpoint**:
   - Same page
   - Copy the Endpoint URL
5. **Get Deployment Name**:
   - Click "Model deployments"
   - See your deployment name (or create one if needed)

### Step 2: Create `.env` File

```bash
# In your project root
cp config.env.example .env
```

### Step 3: Fill in Your Credentials

Edit `.env` file:
```bash
AZURE_OPENAI_API_KEY=your_actual_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

### Step 4: Test

Start your backend:
```bash
./start_backend.sh
```

Look for this in logs:
- ✅ `"Azure OpenAI client initialized successfully"` = Working!
- ❌ `"Azure OpenAI credentials not found. Using mock mode."` = Check your `.env` file

---

## 🔍 Visual Guide: Where to Find Each Item

### In Azure Portal:

```
Azure OpenAI Resource
├── Keys and Endpoint
│   ├── KEY 1 → Copy this → AZURE_OPENAI_API_KEY
│   ├── KEY 2 → (Alternative, either works)
│   └── Endpoint → Copy this → AZURE_OPENAI_ENDPOINT
│
└── Model deployments
    └── [Your Deployment] → Name → AZURE_OPENAI_DEPLOYMENT_NAME
```

---

## ✅ Complete Example `.env` File

```bash
# Azure OpenAI / AI Foundry Configuration
AZURE_OPENAI_API_KEY=abc123def456ghi789jkl012mno345pqr678stu901vwx234yz
AZURE_OPENAI_ENDPOINT=https://robot-maintenance-ai.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o

# Backend Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# Frontend Configuration
FRONTEND_PORT=8501
```

---

## 🚨 Common Issues

### Issue: "Credentials not found"
**Solution**: 
- Check `.env` file exists in project root
- Verify variable names match exactly (case-sensitive)
- Make sure no extra spaces

### Issue: "Model deployment not found"
**Solution**:
- Verify deployment name matches exactly
- Check model is deployed in Azure Portal
- Wait a few minutes after creating deployment

### Issue: "Invalid endpoint"
**Solution**:
- Make sure endpoint includes `https://`
- Make sure endpoint ends with `/`
- Check for typos

---

## 📝 Summary

**You need exactly 3 things from Azure**:
1. ✅ **API Key** (from Keys and Endpoint)
2. ✅ **Endpoint URL** (from Keys and Endpoint)
3. ✅ **Deployment Name** (from Model deployments)

**Plus 1 optional**:
4. ⚪ **API Version** (has default, usually don't need)

That's it! 🎉


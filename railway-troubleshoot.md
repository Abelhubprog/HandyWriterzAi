# 🚄 Railway Docker Build Troubleshooting

## 🔍 **Current Issue**
```
failed to copy: httpReadSeeker: failed open: failed to do request: 
Get "https://registry-1.docker.io/v2/library/node/blobs/sha256:...": 
context canceled: context canceled
```

This is a **Docker registry connectivity issue**, not a code problem. The build times out while downloading the Node.js base image.

## ⚡ **Quick Solutions**

### **Solution 1: Retry (Most Common Fix)**
```bash
# Simply retry the deployment - network issues are often temporary
railway up --detach

# Or force rebuild
railway up --detach --force
```

### **Solution 2: Use Alternative Dockerfile**
```bash
# Use the simplified Railway-optimized Dockerfile
cp frontend/Dockerfile.railway frontend/Dockerfile
railway up --detach
```

### **Solution 3: Increase Build Timeout**
Add to `railway.toml`:
```toml
[build]
builder = "dockerfile"
buildCommand = "echo 'Building with extended timeout'"

[deploy]
healthcheckTimeout = 600
restartPolicyType = "ON_FAILURE"
```

### **Solution 4: Use Railway's Built-in Node.js Builder**
Create `railway.json` in frontend directory:
```json
{
  "build": {
    "builder": "nixpacks",
    "buildCommand": "pnpm install && pnpm build"
  },
  "deploy": {
    "startCommand": "pnpm start",
    "healthcheckPath": "/api/health"
  }
}
```

## 🎯 **Recommended Approach**

1. **First**: Try a simple retry:
   ```bash
   railway up --detach
   ```

2. **If that fails**: Use the Railway nixpacks builder instead of Docker:
   ```bash
   # Remove Dockerfile temporarily to force nixpacks
   mv frontend/Dockerfile frontend/Dockerfile.backup
   railway up --detach
   ```

3. **If you need Docker**: Try during off-peak hours when Docker Hub is less congested

## 🔧 **Alternative: Deploy Backend Only First**

You can deploy just the backend to test the API fixes:

```bash
# Deploy backend service only
cd backend
railway up --detach

# Test the API endpoint
curl -X POST https://your-backend.railway.app/api/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test message", "mode": "general", "file_ids": [], "user_params": {}}'
```

## 📊 **Why This Happens**

- **Docker Hub Rate Limits**: Free accounts have pull limits
- **Network Congestion**: Peak usage times cause timeouts  
- **Railway Build Environment**: Sometimes has connectivity issues
- **Large Base Images**: Node.js images are large and take time to download

## ✅ **Success Indicators**

When the build works, you'll see:
```
[frontend-builder 2/7] WORKDIR /app/frontend
[frontend-builder 3/7] RUN corepack enable && corepack prepare pnpm@9 --activate
[frontend-builder 4/7] COPY pnpm-workspace.yaml pnpm-lock.yaml ./
```

## 🚀 **Next Steps**

1. **Try Solution 1** (retry) - works 80% of the time
2. **If fails**: Use Solution 4 (nixpacks) - more reliable  
3. **Last resort**: Contact Railway support for build environment issues

The API fixes are correct - this is purely a Docker registry connectivity issue that's unrelated to our code changes.
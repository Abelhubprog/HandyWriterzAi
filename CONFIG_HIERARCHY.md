# 🏗️ Configuration Files Hierarchy in HandyWriterz

## 📁 **Configuration File Locations**

### **Root Directory (`/`)**
```
/railway.toml          # Railway deployment config
/railway.json          # Alternative Railway config  
/pnpm-workspace.yaml   # Workspace configuration
/package.json          # Root workspace package
/Dockerfile            # Multi-stage build (Backend + Frontend)
/docker-compose.yml    # Local development
```

### **Backend Directory (`/backend/`)**
```
/backend/Dockerfile           # Backend-only build
/backend/requirements.txt     # Python dependencies
/backend/alembic.ini         # Database migrations
/backend/src/config.py       # Application config
```

### **Frontend Directory (`/frontend/`)**
```
/frontend/Dockerfile         # Frontend-only build
/frontend/package.json       # Node.js dependencies  
/frontend/next.config.mjs    # Next.js configuration
/frontend/tailwind.config.ts # Styling config
/frontend/railway.json       # Frontend Railway config
```

## 🎯 **What Railway Uses During Deployment**

### **Primary Deployment Flow**
Railway reads configurations in this **order of precedence**:

1. **`/railway.toml`** (highest priority)
2. **`/railway.json`** 
3. **`/Dockerfile`** (if no railway configs)
4. **Auto-detection** (nixpacks)

### **Current Railway Deployment**
Since you have **`/railway.toml`** and **`/Dockerfile`** in root:

```bash
# Railway uses ROOT configurations:
📁 /railway.toml        ← Railway deployment settings
📁 /Dockerfile          ← Multi-stage build (Frontend + Backend)
📁 /pnpm-workspace.yaml ← Workspace dependencies
```

## 🏃‍♂️ **Deployment Process Flow**

### **Stage 1: Frontend Build**
```dockerfile
# Uses ROOT /Dockerfile
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

# Uses ROOT workspace files
COPY pnpm-workspace.yaml pnpm-lock.yaml /app/
COPY frontend/package.json ./

# Installs from FRONTEND package.json
RUN pnpm install --frozen-lockfile

# Uses FRONTEND configs
COPY frontend/ ./          # Includes next.config.mjs, tailwind.config.ts
RUN pnpm build           # Uses frontend/package.json scripts
```

### **Stage 2: Backend Build**  
```dockerfile
# Uses ROOT /Dockerfile  
FROM langchain/langgraph-api:3.11

# Copies built frontend from Stage 1
COPY --from=frontend-builder /app/frontend/.next/standalone /deps/frontend/

# Uses BACKEND files
ADD backend/ /deps/backend        # Includes requirements.txt, src/config.py
RUN uv pip install -e .          # Uses backend/requirements.txt
```

## 📋 **Configuration Usage Matrix**

| **File** | **Used By** | **Purpose** | **When Applied** |
|----------|-------------|-------------|------------------|
| `/railway.toml` | Railway Platform | Deployment settings, health checks | During deployment |
| `/Dockerfile` | Docker/Railway | Build instructions | During image build |
| `/pnpm-workspace.yaml` | pnpm | Workspace structure | During dependency install |
| `frontend/package.json` | pnpm/Node.js | Frontend dependencies | Frontend build stage |
| `frontend/next.config.mjs` | Next.js | Build & runtime config | Frontend compilation |
| `backend/requirements.txt` | pip/uv | Python dependencies | Backend build stage |
| `backend/src/config.py` | FastAPI app | Runtime configuration | Application startup |

## 🎛️ **Configuration Inheritance**

### **Frontend Configs**
```
Frontend Build Process:
1. ROOT/pnpm-workspace.yaml     → Defines workspace
2. ROOT/pnpm-lock.yaml          → Locks dependencies  
3. frontend/package.json        → Frontend dependencies
4. frontend/next.config.mjs     → Next.js build settings
5. frontend/tailwind.config.ts  → Styling compilation
```

### **Backend Configs**
```
Backend Build Process:
1. backend/requirements.txt     → Python dependencies
2. backend/alembic.ini         → Database migrations
3. backend/src/config.py       → Runtime environment
4. backend/src/main.py         → Application startup
```

## 🚀 **Railway-Specific Behavior**

### **Configuration Priority**
1. **Railway Dashboard Settings** (highest)
2. **`/railway.toml`** 
3. **`/railway.json`**
4. **Dockerfile detection**
5. **Auto-detection (nixpacks)**

### **Environment Variables**
```bash
# Set in Railway Dashboard, used by:
DATABASE_URL          → backend/src/config.py
REDIS_URL            → backend/src/config.py  
NEXT_PUBLIC_API_URL  → frontend build & runtime
DYNAMIC_ENV_ID       → frontend runtime
```

### **Build Context**
```
Railway Build Context = ROOT directory
├── Copies ROOT/Dockerfile
├── Copies ROOT/pnpm-workspace.yaml  
├── Copies ROOT/pnpm-lock.yaml
├── Copies frontend/ (entire directory)
├── Copies backend/ (entire directory)
└── Executes Docker build from ROOT
```

## 🔧 **Override Scenarios**

### **If You Want Frontend-Only Deploy**
```bash
# Remove root Dockerfile to force Railway to use frontend/
mv Dockerfile Dockerfile.backup
# Railway will then use frontend/Dockerfile or auto-detect
```

### **If You Want Backend-Only Deploy**
```bash  
# Create backend service separately
railway add backend
# Deploy from backend/ directory context
```

### **If You Want Separate Services**
Create separate Railway services:
```bash
railway new handywriterz-frontend  # Uses frontend/ configs
railway new handywriterz-backend   # Uses backend/ configs  
```

## 📊 **Current Active Configs**

Based on your setup, Railway is currently using:

```
✅ ROOT/railway.toml      → Deployment settings
✅ ROOT/Dockerfile        → Multi-stage build  
✅ ROOT/pnpm-workspace.yaml → Workspace setup
✅ frontend/package.json   → Frontend deps
✅ frontend/next.config.mjs → Next.js settings  
✅ backend/requirements.txt → Backend deps
✅ backend/src/config.py   → Runtime config
```

## 🎯 **Summary**

- **Railway uses ROOT configs** for deployment orchestration
- **Frontend configs** are used during frontend build stage  
- **Backend configs** are used during backend build stage
- **All configs work together** in the multi-stage build process
- **No conflicts** - each serves its specific purpose at the right time

The multi-stage Dockerfile ensures all configurations are properly applied at the appropriate build stages! 🚀
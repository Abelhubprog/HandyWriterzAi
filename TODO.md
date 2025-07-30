# HandyWriterzAI - Detailed Implementation TODO

## Phase 1: Critical Fixes (Day 1-2)

### 1.1 Fix Chat API Integration (CRITICAL)
- [ ] Update frontend ChatRequest interface to match backend expectations
- [ ] Fix backend `/api/chat` response format to return `trace_id`
- [ ] Add proper error handling for 500 errors
- [ ] Test with simple prompt submission

```typescript
// frontend/src/app/api/chat/route.ts
interface ChatRequest {
  prompt: string;
  mode: string;
  file_ids: string[];
  user_params: {
    citationStyle: string;
    wordCount: number;
    model: string;
    user_id: string;
  };
}
```

### 1.2 Fix Message Input Bar Design (HIGH)
- [ ] Remove separate Tools button
- [ ] Move writer type dropdown inline: `[+] [Dropdown] [Textarea] [Mic] [↑]`
- [ ] Replace file upload modal with native picker
- [ ] Show files as chips above textarea
- [ ] Enable send button when text OR files present
- [ ] Add drag-and-drop overlay
- [ ] Implement 10 file / 100MB limits

### 1.3 Implement SSE Streaming (HIGH)
- [ ] Create useStream hook for frontend
- [ ] Fix backend SSE endpoint headers
- [ ] Implement token-by-token streaming
- [ ] Add reasoning text streaming
- [ ] Show status updates ("Parsing files...", "Routing to agents...")

## Phase 2: Authentication & User Management (Day 3-4)

### 2.1 Dynamic.xyz Integration
- [ ] Get Dynamic.xyz environment ID
- [ ] Configure Dynamic provider with email/social auth
- [ ] Remove mock authentication
- [ ] Implement JWT token generation on backend
- [ ] Add auth middleware to protected routes

### 2.2 User Profile Implementation
- [ ] Create Supabase users table
- [ ] Implement user context with credits
- [ ] Build profile page with real data
- [ ] Add credits display in header
- [ ] Implement settings modal (not separate page)

### 2.3 Database Setup
- [ ] Configure Supabase connection
- [ ] Create database schema:
  - users (id, email, wallet, credits, subscription)
  - conversations (id, user_id, title, messages)
  - files (id, user_id, filename, url)
  - transactions (id, user_id, amount, type)

## Phase 3: Core Features (Day 5-6)

### 3.1 File Upload System
- [ ] Implement `/api/files/upload` endpoint
- [ ] Add progress tracking
- [ ] Store files in Cloudflare R2
- [ ] Update file references in database
- [ ] Add file preview in chat

### 3.2 Response Actions
- [ ] Add action buttons below AI messages
- [ ] Implement copy to clipboard
- [ ] Add share functionality (X, LinkedIn, Reddit)
- [ ] Create export endpoints (PDF, DOCX, MD)
- [ ] Add download progress indicator

### 3.3 Conversation Management
- [ ] Implement conversation list in sidebar
- [ ] Add search functionality
- [ ] Enable conversation switching
- [ ] Add delete conversation option
- [ ] Implement auto-save

## Phase 4: UI/UX Polish (Day 7-8)

### 4.1 Landing Page Redesign
- [ ] Create minimalist hero section
- [ ] Add gradient background
- [ ] Single CTA: "Start Writing"
- [ ] Add social proof section
- [ ] Remove unnecessary content

### 4.2 Pricing Page
- [ ] Create pricing component based on pricing.png
- [ ] Free tier: 3 docs/month
- [ ] Pro tier: $20/month for 50 docs
- [ ] Enterprise: Custom pricing
- [ ] Add Stripe integration

### 4.3 Theme System
- [ ] Implement theme context
- [ ] Add theme selector in settings
- [ ] Support light/dark/system modes
- [ ] Persist theme preference

## Phase 5: Production Readiness (Day 9-10)

### 5.1 Error Handling
- [ ] Add global error boundary
- [ ] Implement toast notifications
- [ ] Add retry mechanisms
- [ ] Log errors to monitoring service
- [ ] Create user-friendly error messages

### 5.2 Performance Optimization
- [ ] Add request caching
- [ ] Implement lazy loading
- [ ] Optimize bundle size
- [ ] Add loading skeletons
- [ ] Implement virtual scrolling for long chats

### 5.3 Testing
- [ ] Unit tests for critical functions
- [ ] Integration tests for API endpoints
- [ ] E2E tests for user journeys
- [ ] Load testing for concurrent users
- [ ] Security testing for auth flow

## Phase 6: Deployment (Day 11-12)

### 6.1 Environment Setup
- [ ] Configure production environment variables
- [ ] Set up Railway.com project
- [ ] Configure domain and SSL
- [ ] Set up monitoring (Sentry)
- [ ] Configure backup strategy

### 6.2 CI/CD Pipeline
- [ ] GitHub Actions for testing
- [ ] Automatic deployment on merge
- [ ] Database migration scripts
- [ ] Rollback procedures
- [ ] Health check endpoints

## User Journey Tests

### Test 1: New User Signup
1. Land on homepage
2. Click "Start Writing"
3. Sign up with email
4. Receive welcome credits
5. Create first document

### Test 2: Document Creation
1. Click example prompt
2. Upload 2 context files
3. Select "PhD Dissertation" type
4. Send message
5. Watch streaming response
6. Toggle reasoning view
7. Export to PDF

### Test 3: Credit Purchase
1. Check credit balance
2. Click "Buy Credits"
3. Select package
4. Complete payment
5. Verify balance updated

## Success Metrics

- **Performance**: < 3s initial response
- **Reliability**: 99.9% uptime
- **User Experience**: < 2 clicks to start
- **Quality**: 90%+ user satisfaction
- **Scale**: Handle 1000+ concurrent users

## Daily Standup Questions

1. What was completed yesterday?
2. What will be done today?
3. Are there any blockers?
4. Is the timeline on track?

## Emergency Fixes (If Time Constrained)

If running out of time, prioritize:
1. Fix chat API (without this, nothing works)
2. Basic auth (even if mock)
3. Simple file upload
4. Basic streaming
5. Deploy as-is

Remember: A working demo is better than a perfect but broken app!

# OAuth Setup Complete Guide - SaaS Factory

## Overview
This guide provides step-by-step instructions for setting up Google and GitHub OAuth applications to complete the OAuth authentication system implementation.

## Current Status
✅ **OAuth Backend Implementation**: 100% Complete  
✅ **OAuth Frontend Integration**: 100% Complete  
✅ **OAuth Database Integration**: 100% Complete  
🔄 **OAuth App Configuration**: In Progress  
🔄 **Environment Setup**: In Progress  

## Phase 1: Google OAuth Setup

### Step 1: Create Google OAuth Application
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project: `summer-nexus-463503-e1`
3. Navigate to **APIs & Services** > **Credentials**
4. Click **+ CREATE CREDENTIALS** > **OAuth client ID**
5. Configure the OAuth consent screen if prompted:
   - User Type: External
   - App name: SaaS Factory
   - User support email: your-email@domain.com
   - Developer contact information: your-email@domain.com

### Step 2: Configure OAuth Client
1. **Application type**: Web application
2. **Name**: SaaS Factory OAuth Client
3. **Authorized redirect URIs**:
   - Development: `http://localhost:8000/auth/callback/google`
   - Production: `https://api.forge95.com/auth/callback/google`
4. Click **Create**

### Step 3: Save Google OAuth Credentials
- **Client ID**: Copy the generated client ID
- **Client Secret**: Copy the generated client secret
- Store these securely for environment configuration

## Phase 2: GitHub OAuth Setup

### Step 1: Create GitHub OAuth Application
1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click **New OAuth App**
3. Fill in the application details:
   - **Application name**: SaaS Factory
   - **Homepage URL**: 
     - Development: `http://localhost:3000`
     - Production: `https://www.forge95.com`
   - **Application description**: OAuth authentication for SaaS Factory platform
   - **Authorization callback URL**:
     - Development: `http://localhost:8000/auth/callback/github`
     - Production: `https://api.forge95.com/auth/callback/github`

### Step 2: Save GitHub OAuth Credentials
- **Client ID**: Copy the generated client ID
- **Client Secret**: Click **Generate a new client secret** and copy it
- Store these securely for environment configuration

## Phase 3: Environment Configuration

### Development Environment
Update `config/environments/development.env`:

```bash
# OAuth Configuration
GOOGLE_OAUTH_ENABLED=true
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_REDIRECT_URI=/auth/callback/google

GITHUB_OAUTH_ENABLED=true
GITHUB_CLIENT_ID=your_github_client_id_here
GITHUB_CLIENT_SECRET=your_github_client_secret_here
GITHUB_REDIRECT_URI=/auth/callback/github
```

### Frontend Environment
Create `ui/.env.local`:

```bash
# OAuth Configuration
VITE_GOOGLE_CLIENT_ID=your_google_client_id_here
VITE_GITHUB_CLIENT_ID=your_github_client_id_here

# API Configuration
VITE_API_BASE_URL=http://localhost:8000
```

### Production Environment
Update `config/environments/production.env`:

```bash
# OAuth Configuration
GOOGLE_OAUTH_ENABLED=true
GOOGLE_CLIENT_ID=your_production_google_client_id
GOOGLE_CLIENT_SECRET=your_production_google_client_secret
GOOGLE_REDIRECT_URI=/auth/callback/google

GITHUB_OAUTH_ENABLED=true
GITHUB_CLIENT_ID=your_production_github_client_id
GITHUB_CLIENT_SECRET=your_production_github_client_secret
GITHUB_REDIRECT_URI=/auth/callback/github
```

## Phase 4: OAuth Flow Testing

### Test Google OAuth
1. Start the development servers:
   ```bash
   # Backend
   cd api_gateway && python -m uvicorn app:app --reload --port 8000
   
   # Frontend
   cd ui && npm run dev
   ```

2. Navigate to `http://localhost:3000/signin`
3. Click "Continue with Google"
4. Complete the OAuth flow
5. Verify user creation and authentication

### Test GitHub OAuth
1. Click "Continue with GitHub"
2. Complete the OAuth flow
3. Verify user creation and authentication

## Phase 5: Production Deployment

### Update OAuth App Settings
1. **Google OAuth**: Update redirect URIs to production URLs
2. **GitHub OAuth**: Update callback URLs to production URLs
3. **Environment Variables**: Update production environment files
4. **Deploy**: Deploy updated configuration to production

### Production URLs
- **API Gateway**: `https://api.forge95.com`
- **Frontend**: `https://www.forge95.com`
- **Google Callback**: `https://api.forge95.com/auth/callback/google`
- **GitHub Callback**: `https://api.forge95.com/auth/callback/github`

## Security Considerations

### OAuth Security Best Practices
1. **Client Secrets**: Never commit OAuth secrets to version control
2. **Redirect URIs**: Use exact match redirect URIs
3. **State Parameter**: OAuth state validation is implemented for CSRF protection
4. **HTTPS**: Use HTTPS in production for all OAuth flows
5. **Scope Limitation**: Request minimal OAuth scopes needed

### Environment Variable Security
1. **Development**: Use `.env.local` files (gitignored)
2. **Production**: Use Google Cloud Secret Manager
3. **CI/CD**: Inject OAuth credentials securely during deployment

## Troubleshooting

### Common Issues
1. **"OAuth not configured"**: Check environment variables are set correctly
2. **"Invalid redirect URI"**: Verify callback URLs match OAuth app settings
3. **"Client ID not configured"**: Ensure OAuth environment variables are loaded
4. **"OAuth error"**: Check OAuth app configuration and scopes

### Debug Steps
1. Check browser console for OAuth errors
2. Verify backend logs for OAuth flow issues
3. Confirm environment variables are loaded correctly
4. Test OAuth endpoints directly with curl/Postman

## Success Criteria

### Development Environment
- [ ] Google OAuth signup/login working
- [ ] GitHub OAuth signup/login working
- [ ] OAuth users properly created
- [ ] Tenant isolation maintained
- [ ] JWT tokens generated correctly

### Production Environment
- [ ] Production OAuth apps configured
- [ ] Production environment variables set
- [ ] OAuth flows working in production
- [ ] Security measures in place
- [ ] Monitoring and logging active

## Next Steps

1. **Complete OAuth App Setup**: Create Google and GitHub OAuth applications
2. **Configure Environment Variables**: Set OAuth credentials in environment files
3. **Test OAuth Flows**: Verify end-to-end OAuth functionality
4. **Deploy to Production**: Update production OAuth configuration
5. **Monitor Performance**: Track OAuth success rates and performance

## Support

For OAuth setup assistance:
- Check OAuth provider documentation
- Review backend logs for detailed error messages
- Verify environment variable configuration
- Test OAuth endpoints individually

---

**Status**: OAuth Implementation Ready for Configuration  
**Estimated Completion Time**: 1 hour  
**Priority**: High - Required for user authentication

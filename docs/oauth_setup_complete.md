# Complete OAuth Setup Guide - SaaS Factory

## Overview

This guide provides step-by-step instructions to complete the OAuth authentication setup for the SaaS Factory platform. The backend and frontend code is already implemented - we just need to configure the OAuth applications and environment variables.

## Prerequisites

- Access to Google Cloud Console (for Google OAuth)
- Access to GitHub Developer Settings (for GitHub OAuth)
- SaaS Factory backend and frontend running locally

## Step 1: Google OAuth Setup

### 1.1 Create Google OAuth 2.0 Credentials

1. **Go to Google Cloud Console**
   - Navigate to [Google Cloud Console](https://console.cloud.google.com/)
   - Select your project: `summer-nexus-463503-e1`

2. **Enable OAuth 2.0 API**
   - Go to **APIs & Services** > **Library**
   - Search for "Google+ API" or "OAuth 2.0"
   - Enable the API if not already enabled

3. **Create OAuth 2.0 Credentials**
   - Go to **APIs & Services** > **Credentials**
   - Click **Create Credentials** > **OAuth 2.0 Client IDs**
   - Choose **Web application** as the application type

4. **Configure OAuth Client**
   - **Name**: `SaaS Factory OAuth Client`
   - **Authorized JavaScript origins**:
     ```
     http://localhost:3000
     http://localhost:5173
     http://localhost:5175
     http://127.0.0.1:3000
     http://127.0.0.1:5173
     http://127.0.0.1:5175
     ```
   - **Authorized redirect URIs**:
     ```
     http://localhost:8000/auth/callback/google
     http://127.0.0.1:8000/auth/callback/google
     ```

5. **Save Credentials**
   - Click **Create**
   - Copy the **Client ID** and **Client Secret**
   - Keep these secure - you'll need them for configuration

### 1.2 Configure Google OAuth Environment Variables

Update your backend environment file:

```bash
# config/environments/development.env
GOOGLE_OAUTH_ENABLED=true
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_REDIRECT_URI=/auth/callback/google
```

Update your frontend environment file:

```bash
# ui/.env.local
VITE_GOOGLE_CLIENT_ID=your_google_client_id_here
```

## Step 2: GitHub OAuth Setup

### 2.1 Create GitHub OAuth App

1. **Go to GitHub Developer Settings**
   - Navigate to [GitHub Settings > Developer settings > OAuth Apps](https://github.com/settings/developers)
   - Click **New OAuth App**

2. **Configure OAuth App**
   - **Application name**: `SaaS Factory`
   - **Homepage URL**: `http://localhost:3000` (or your preferred development URL)
   - **Application description**: `OAuth authentication for SaaS Factory platform`
   - **Authorization callback URL**: `http://localhost:8000/auth/callback/github`

3. **Register Application**
   - Click **Register application**
   - Copy the **Client ID** and **Client Secret**

### 2.2 Configure GitHub OAuth Environment Variables

Update your backend environment file:

```bash
# config/environments/development.env
GITHUB_OAUTH_ENABLED=true
GITHUB_CLIENT_ID=your_github_client_id_here
GITHUB_CLIENT_SECRET=your_github_client_secret_here
GITHUB_REDIRECT_URI=/auth/callback/github
```

Update your frontend environment file:

```bash
# ui/.env.local
VITE_GITHUB_CLIENT_ID=your_github_client_id_here
```

## Step 3: Environment Configuration

### 3.1 Backend Environment Setup

Create or update `config/environments/development.env`:

```bash
# OAuth Configuration
GOOGLE_OAUTH_ENABLED=true
GOOGLE_CLIENT_ID=your_actual_google_client_id
GOOGLE_CLIENT_SECRET=your_actual_google_client_secret
GOOGLE_REDIRECT_URI=/auth/callback/google

GITHUB_OAUTH_ENABLED=true
GITHUB_CLIENT_ID=your_actual_github_client_id
GITHUB_CLIENT_SECRET=your_actual_github_client_secret
GITHUB_REDIRECT_URI=/auth/callback/github

# JWT Configuration (if not already set)
JWT_SECRET_KEY=your_secure_jwt_secret_key_here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
```

### 3.2 Frontend Environment Setup

Create `ui/.env.local`:

```bash
# OAuth Configuration
VITE_GOOGLE_CLIENT_ID=your_actual_google_client_id
VITE_GITHUB_CLIENT_ID=your_actual_github_client_id

# API Configuration
VITE_API_BASE_URL=http://localhost:8000
```

## Step 4: Testing OAuth Configuration

### 4.1 Check OAuth Status

Test the OAuth configuration endpoint:

```bash
curl http://localhost:8000/auth/status
```

Expected response:
```json
{
  "google_oauth_enabled": true,
  "github_oauth_enabled": true,
  "google_client_id_configured": true,
  "github_client_id_configured": true
}
```

### 4.2 Test OAuth Flow

1. **Start Backend**
   ```bash
   cd api_gateway
   python -m uvicorn app:app --reload --port 8000
   ```

2. **Start Frontend**
   ```bash
   cd ui
   npm run dev
   ```

3. **Test OAuth Flow**
   - Navigate to `http://localhost:3000/signin`
   - Click "Continue with Google" or "Continue with GitHub"
   - Complete the OAuth flow
   - Verify user creation and authentication

## Step 5: Production Configuration

### 5.1 Update OAuth App Settings

**Google OAuth:**
- Add production domains to authorized origins
- Add production callback URLs
- Update environment variables

**GitHub OAuth:**
- Update homepage URL to production domain
- Update callback URL to production domain
- Update environment variables

### 5.2 Production Environment Variables

```bash
# Production OAuth Configuration
GOOGLE_OAUTH_ENABLED=true
GOOGLE_CLIENT_ID=your_production_google_client_id
GOOGLE_CLIENT_SECRET=your_production_google_client_secret
GOOGLE_REDIRECT_URI=/auth/callback/google

GITHUB_OAUTH_ENABLED=true
GITHUB_CLIENT_ID=your_production_github_client_id
GITHUB_CLIENT_SECRET=your_production_github_client_secret
GITHUB_REDIRECT_URI=/auth/callback/github
```

## Troubleshooting

### Common Issues

1. **404 Error on OAuth Callback**
   - Verify redirect URIs match exactly
   - Check backend OAuth routes are included
   - Ensure environment variables are set

2. **OAuth Flow Not Starting**
   - Check client IDs are configured
   - Verify OAuth is enabled in settings
   - Check browser console for errors

3. **User Not Created**
   - Check database connection
   - Verify tenant isolation settings
   - Check backend logs for errors

### Debug Steps

1. Check OAuth status endpoint
2. Verify environment variables
3. Check backend logs
4. Test OAuth flow step by step
5. Verify database user creation

## Security Considerations

1. **Client Secrets**: Never expose client secrets in frontend code
2. **Redirect URIs**: Use exact matching for security
3. **HTTPS**: Use HTTPS in production for all OAuth flows
4. **State Parameter**: Consider implementing state parameter validation
5. **Token Storage**: Store JWT tokens securely

## Next Steps

After completing this setup:

1. Test OAuth flows thoroughly in development
2. Update production OAuth app settings
3. Deploy with production environment variables
4. Monitor OAuth performance and error rates
5. Implement additional security measures as needed

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review backend and frontend logs
3. Verify OAuth app configuration
4. Test with minimal configuration
5. Contact the development team

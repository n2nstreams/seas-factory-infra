# GitHub OAuth Setup Guide

## Overview
This guide explains how to set up GitHub OAuth authentication for the SaaS Factory platform.

## Prerequisites
- GitHub account with admin access to an organization (or personal account)
- Access to SaaS Factory environment configuration

## Step 1: Create GitHub OAuth App

### 1.1 Navigate to GitHub Developer Settings
1. Go to [GitHub Settings > Developer settings > OAuth Apps](https://github.com/settings/developers)
2. Click "New OAuth App"

### 1.2 Configure OAuth App
Fill in the following details:

**Application name:** `SaaS Factory` (or your preferred name)
**Homepage URL:** `https://yourdomain.com` (production) or `http://localhost:3000` (development)
**Application description:** `OAuth authentication for SaaS Factory platform`
**Authorization callback URL:** `https://yourdomain.com/auth/callback/github` (production) or `http://localhost:3000/auth/callback/github` (development)

### 1.3 Register Application
Click "Register application" to create the OAuth app.

### 1.4 Get Client Credentials
After registration, you'll receive:
- **Client ID:** A public identifier for your app
- **Client Secret:** A private key (keep this secure)

## Step 2: Environment Configuration

### 2.1 Backend Environment Variables
Add these to your backend `.env` file:

```bash
# GitHub OAuth Configuration
GITHUB_CLIENT_ID=your_client_id_here
GITHUB_CLIENT_SECRET=your_client_secret_here

# JWT Configuration
JWT_SECRET_KEY=your_jwt_secret_key_here
JWT_ALGORITHM=HS256

# Frontend URL for OAuth redirects
FRONTEND_URL=https://yourdomain.com
```

### 2.2 Frontend Environment Variables
Create `.env.local` in the `ui/` directory:

```bash
# OAuth Configuration
VITE_GITHUB_CLIENT_ID=your_client_id_here

# API Configuration
VITE_API_BASE_URL=https://yourdomain.com/api
```

## Step 3: OAuth Flow Implementation

### 3.1 Backend Routes
The following OAuth routes are implemented:

- `GET /auth/github` - Initiates GitHub OAuth flow
- `GET /auth/callback/github` - Handles OAuth callback

### 3.2 Frontend Integration
OAuth buttons are integrated in:
- `SignIn.tsx` - Login page
- `Signup.tsx` - Registration page

### 3.3 OAuth Success/Error Pages
- `OAuthSuccess.tsx` - Handles successful authentication
- `OAuthError.tsx` - Handles authentication errors

## Step 4: Testing OAuth Flow

### 4.1 Development Testing
1. Start backend: `cd api_gateway && python -m uvicorn app:app --reload`
2. Start frontend: `cd ui && npm run dev`
3. Navigate to `/signin` or `/signup`
4. Click "Continue with GitHub" button
5. Complete GitHub OAuth flow

### 4.2 Production Testing
1. Deploy with proper environment variables
2. Test OAuth flow in production environment
3. Verify user creation and authentication

## Step 5: Security Considerations

### 5.1 OAuth Security
- **State Parameter:** Implemented to prevent CSRF attacks
- **HTTPS Only:** Production must use HTTPS
- **Client Secret:** Keep secure and never expose in frontend

### 5.2 JWT Security
- **Secret Key:** Use strong, unique JWT secret
- **Expiration:** Tokens expire after 24 hours
- **Algorithm:** Uses HS256 for JWT signing

### 5.3 User Data Security
- **Email Verification:** GitHub provides verified email addresses
- **Tenant Isolation:** OAuth users are properly isolated
- **Access Control:** Follows existing RBAC patterns

## Step 6: Troubleshooting

### 6.1 Common Issues

**404 Error on OAuth Callback:**
- Verify callback URL matches GitHub OAuth app settings
- Check if OAuth routes are properly registered in API gateway

**Invalid Client ID:**
- Verify `GITHUB_CLIENT_ID` environment variable is set correctly
- Check if GitHub OAuth app is properly configured

**Authentication Token Errors:**
- Verify `JWT_SECRET_KEY` is set correctly
- Check JWT algorithm configuration

### 6.2 Debug Steps
1. Check backend logs for OAuth errors
2. Verify environment variables are loaded
3. Test OAuth endpoints directly
4. Check GitHub OAuth app configuration

## Step 7: Monitoring and Maintenance

### 7.1 OAuth Metrics
Monitor these key metrics:
- OAuth success/failure rates
- User creation success rates
- Authentication response times

### 7.2 Regular Maintenance
- Rotate JWT secret keys periodically
- Monitor GitHub OAuth app usage
- Update OAuth scopes if needed
- Review security logs regularly

## Additional Resources

- [GitHub OAuth Documentation](https://docs.github.com/en/developers/apps/building-oauth-apps)
- [FastAPI OAuth Tutorial](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- [JWT Security Best Practices](https://auth0.com/blog/a-look-at-the-latest-draft-for-jwt-bcp/)

## Support

For OAuth-related issues:
1. Check this documentation first
2. Review backend logs for errors
3. Verify GitHub OAuth app configuration
4. Contact the development team if issues persist

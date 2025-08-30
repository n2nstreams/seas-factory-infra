# OAuth Setup Guide for SaaS Factory

This guide explains how to configure Google and GitHub OAuth authentication for the SaaS Factory platform.

## Overview

The SaaS Factory platform supports OAuth 2.0 authentication with:
- **Google OAuth**: For Google account authentication
- **GitHub OAuth**: For GitHub account authentication

## Prerequisites

- Access to Google Cloud Console (for Google OAuth)
- Access to GitHub Developer Settings (for GitHub OAuth)
- SaaS Factory backend and frontend deployed

## Google OAuth Setup

### 1. Create Google OAuth 2.0 Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project or create a new one
3. Navigate to **APIs & Services** > **Credentials**
4. Click **Create Credentials** > **OAuth 2.0 Client IDs**
5. Choose **Web application** as the application type
6. Fill in the following details:
   - **Name**: `SaaS Factory OAuth Client`
   - **Authorized JavaScript origins**: 
     - `http://localhost:3000` (development)
     - `http://localhost:5173` (development)
     - `https://yourdomain.com` (production)
   - **Authorized redirect URIs**:
     - `http://localhost:8000/auth/callback/google` (development)
     - `https://yourdomain.com/auth/callback/google` (production)

### 2. Configure Environment Variables

Add the following to your backend environment file:

```bash
# Backend (.env or environment file)
GOOGLE_OAUTH_ENABLED=true
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_REDIRECT_URI=/auth/callback/google
```

Add the following to your frontend environment file:

```bash
# Frontend (.env.local)
VITE_GOOGLE_CLIENT_ID=your_google_client_id_here
```

## GitHub OAuth Setup

### 1. Create GitHub OAuth App

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click **New OAuth App**
3. Fill in the following details:
   - **Application name**: `SaaS Factory`
   - **Homepage URL**: `https://yourdomain.com` (or `http://localhost:3000` for development)
   - **Application description**: `SaaS Factory OAuth Application`
   - **Authorization callback URL**: 
     - `http://localhost:8000/auth/callback/github` (development)
     - `https://yourdomain.com/auth/callback/github` (production)

### 2. Configure Environment Variables

Add the following to your backend environment file:

```bash
# Backend (.env or environment file)
GITHUB_OAUTH_ENABLED=true
GITHUB_CLIENT_ID=your_github_client_id_here
GITHUB_CLIENT_SECRET=your_github_client_secret_here
GITHUB_REDIRECT_URI=/auth/callback/github
```

Add the following to your frontend environment file:

```bash
# Frontend (.env.local)
VITE_GITHUB_CLIENT_ID=your_github_client_id_here
```

## Backend Configuration

### 1. Update Settings

The OAuth configuration is automatically loaded from environment variables through the `SecurityConfig` class in `config/settings.py`.

### 2. OAuth Routes

OAuth routes are automatically included in the API gateway:
- `/auth/google` - Start Google OAuth flow
- `/auth/callback/google` - Handle Google OAuth callback
- `/auth/github` - Start GitHub OAuth flow
- `/auth/callback/github` - Handle GitHub OAuth callback
- `/auth/status` - Check OAuth configuration status

### 3. Database Integration

OAuth users are automatically created in the database with:
- Default tenant assignment
- Proper user role and status
- OAuth provider tracking

## Frontend Configuration

### 1. Environment Variables

Create a `.env.local` file in the `ui/` directory with your OAuth client IDs.

### 2. OAuth Flow

The frontend automatically handles:
- OAuth button rendering
- OAuth flow initiation
- Callback handling
- User authentication state management

### 3. OAuth Success/Error Pages

- `/auth/success` - Handles successful OAuth authentication
- `/auth/error` - Handles OAuth errors

## Testing OAuth

### 1. Development Testing

1. Start the backend and frontend
2. Navigate to `/signin` or `/signup`
3. Click the Google or GitHub OAuth button
4. Complete the OAuth flow
5. Verify user creation and authentication

### 2. OAuth Status Check

Check OAuth configuration status:
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

## Production Deployment

1. Update redirect URIs to production domains
2. Use HTTPS for all OAuth endpoints
3. Set proper CORS origins
4. Configure production environment variables
5. Test OAuth flow in production environment

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review backend and frontend logs
3. Verify OAuth app configuration
4. Test with minimal configuration
5. Contact the development team

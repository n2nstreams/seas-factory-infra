# Production OAuth Setup Guide

This guide covers the complete setup of OAuth authentication for production deployment of SaaS Factory.

## Overview

The SaaS Factory platform supports OAuth authentication with both Google and GitHub providers. This guide covers:

1. **OAuth Application Setup** - Creating OAuth apps in Google and GitHub
2. **Environment Configuration** - Setting up production environment variables
3. **Domain Configuration** - Configuring authorized redirect URIs
4. **Security Considerations** - Best practices for production OAuth
5. **Testing and Validation** - Ensuring OAuth flows work correctly

## 1. Google OAuth Setup

### 1.1 Create Google OAuth Application

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project or create a new one
3. Navigate to **APIs & Services** > **Credentials**
4. Click **Create Credentials** > **OAuth 2.0 Client IDs**
5. Configure the OAuth consent screen if prompted

### 1.2 Configure OAuth Client

- **Application type**: Web application
- **Name**: SaaS Factory Production
- **Authorized JavaScript origins**:
  - `https://www.forge95.com`
  - `https://forge95.com`
- **Authorized redirect URIs**:
  - `https://api.forge95.com/auth/callback/google`

### 1.3 Get Credentials

After creation, you'll receive:
- **Client ID**: `your-google-client-id.apps.googleusercontent.com`
- **Client Secret**: `your-google-client-secret`

## 2. GitHub OAuth Setup

### 2.1 Create GitHub OAuth Application

1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click **New OAuth App**
3. Fill in the application details

### 2.2 Configure OAuth App

- **Application name**: SaaS Factory Production
- **Homepage URL**: `https://www.forge95.com`
- **Application description**: OAuth authentication for SaaS Factory platform
- **Authorization callback URL**: `https://api.forge95.com/auth/callback/github`

### 2.3 Get Credentials

After creation, you'll receive:
- **Client ID**: `your-github-client-id`
- **Client Secret**: `your-github-client-secret`

## 3. Environment Configuration

### 3.1 Production Environment Variables

Update your production environment file (`config/environments/production.env`):

```bash
# OAuth Configuration
GOOGLE_OAUTH_ENABLED=true
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=/auth/callback/google

GITHUB_OAUTH_ENABLED=true
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
GITHUB_REDIRECT_URI=/auth/callback/github

# Service URLs
FRONTEND_URL=https://www.forge95.com
API_GATEWAY_URL=https://api.forge95.com
```

### 3.2 Secret Management

For production, store sensitive OAuth credentials in Google Secret Manager:

```bash
# Create secrets
gcloud secrets create google-oauth-client-secret --data-file=google-secret.txt
gcloud secrets create github-oauth-client-secret --data-file=github-secret.txt

# Grant access to your service account
gcloud secrets add-iam-policy-binding google-oauth-client-secret \
    --member="serviceAccount:your-service@your-project.iam.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"
```

## 4. Domain Configuration

### 4.1 Frontend Domain

Ensure your frontend is accessible at:
- `https://www.forge95.com` (main application)
- `https://forge95.com` (landing page)

### 4.2 Backend API Domain

Ensure your API gateway is accessible at:
- `https://api.forge95.com`

### 4.3 SSL/TLS Configuration

- Use valid SSL certificates (Let's Encrypt or commercial)
- Enable HTTP/2 for better performance
- Configure proper security headers

## 5. Security Considerations

### 5.1 CSRF Protection

The OAuth implementation includes state parameter validation:
- Random state tokens are generated for each OAuth flow
- State tokens are validated on callback
- Invalid state tokens result in authentication failure
- **NEW: Redis-based state storage for production scalability**

### 5.2 Rate Limiting

Configure rate limiting for OAuth endpoints:

```bash
# In production environment
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=50
RATE_LIMIT_WINDOW=60
```

**Implementation Details**:
- Per-IP rate limiting on OAuth start endpoints
- Per-IP rate limiting on OAuth callback endpoints
- Configurable limits and time windows
- Automatic cleanup of expired rate limit data

### 5.3 Input Validation and Sanitization

**Security Features**:
- Comprehensive input validation for all OAuth parameters
- Input sanitization to prevent injection attacks
- Regex-based validation for authorization codes and state parameters
- Length limits and character restrictions

### 5.4 Security Headers

**Headers Applied to All OAuth Responses**:
- `X-Content-Type-Options: nosniff` - Prevents MIME type sniffing
- `X-Frame-Options: DENY` - Prevents clickjacking
- `X-XSS-Protection: 1; mode=block` - XSS protection
- `Referrer-Policy: strict-origin-when-cross-origin` - Referrer control
- `Permissions-Policy: geolocation=(), microphone=(), camera=()` - Feature restrictions

### 5.5 Session Security

- **Production**: Redis-based state storage with TTL
- **Development**: In-memory storage with automatic fallback
- Use secure, HTTP-only cookies for session management
- Implement session timeout and rotation
- Log all OAuth events for monitoring

### 5.4 Error Handling

- Never expose sensitive information in error messages
- Log errors securely for debugging
- Provide user-friendly error messages

## 6. Testing and Validation

### 6.1 OAuth Flow Testing

Test the complete OAuth flow:

1. **Start OAuth Flow**:
   ```bash
   curl -v "https://api.saasfactory.com/auth/github"
   ```

2. **Verify Redirect**:
   - Should redirect to GitHub with proper parameters
   - State parameter should be present
   - Redirect URI should match production configuration

3. **Test Callback**:
   - Complete OAuth flow manually
   - Verify successful authentication
   - Check user creation/login

### 6.2 Error Scenarios

Test error handling:

1. **Invalid State**: Try accessing callback without proper state
2. **Missing Code**: Test callback without authorization code
3. **Invalid Credentials**: Use incorrect client secret
4. **Network Issues**: Simulate network failures

### 6.3 Monitoring

Monitor OAuth performance:

```bash
# Check OAuth metrics
curl "https://api.saasfactory.com/auth/monitoring/metrics"

# Check recent events
curl "https://api.saasfactory.com/auth/monitoring/events?limit=10"
```

## 7. Troubleshooting

### 7.1 Common Issues

**"Invalid redirect URI" error**:
- Verify redirect URI in OAuth app configuration
- Check environment variables
- Ensure exact match between configured and actual URIs

**"Invalid client" error**:
- Verify client ID and secret
- Check environment variable names
- Ensure secrets are properly loaded

**"State parameter invalid" error**:
- Check session configuration
- Verify state parameter generation
- Check for session storage issues

### 7.2 Debug Mode

Enable debug logging for OAuth:

```bash
# In production environment
LOG_LEVEL=DEBUG
DEBUG=true
```

### 7.3 Health Checks

Monitor OAuth health:

```bash
# Check OAuth status
curl "https://api.saasfactory.com/auth/status"

# Check service health
curl "https://api.saasfactory.com/health"
```

## 8. Production Deployment Checklist

- [ ] OAuth applications created in Google and GitHub
- [ ] Production domains configured in OAuth apps
- [ ] Environment variables set correctly
- [ ] SSL certificates configured
- [ ] **NEW: Redis configured for OAuth state storage**
- [ ] **NEW: Rate limiting enabled and configured**
- [ ] **NEW: Input validation and sanitization enabled**
- [ ] **NEW: Security headers configured**
- [ ] Monitoring and logging configured
- [ ] Error handling tested
- [ ] **NEW: Security testing completed (penetration testing)**
- [ ] **NEW: Load testing completed**
- [ ] Rollback plan prepared

## 9. Maintenance

### 9.1 Regular Updates

- Monitor OAuth provider changes
- Update OAuth scopes if needed
- Review and rotate client secrets
- Update documentation

### 9.2 Performance Monitoring

- Track OAuth success rates
- Monitor response times
- Alert on authentication failures
- Review usage patterns

### 9.3 Security Audits

- Regular security reviews
- Penetration testing
- Compliance checks
- Vulnerability assessments

## 10. Support and Resources

### 10.1 Documentation

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [GitHub OAuth Documentation](https://docs.github.com/en/apps/oauth-apps)
- [OAuth 2.0 Security Best Practices](https://tools.ietf.org/html/draft-ietf-oauth-security-topics)

### 10.2 Contact

For OAuth-related issues:
- **Email**: support@saasfactory.com
- **Subject**: OAuth Authentication Issue
- **Include**: Error details, steps to reproduce, environment information

---

**Last Updated**: August 23, 2025
**Version**: 1.0
**Status**: Production Ready

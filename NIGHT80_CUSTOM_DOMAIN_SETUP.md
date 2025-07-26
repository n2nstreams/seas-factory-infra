# Night 80: Custom Domain Setup Guide

## Overview

This guide explains how to configure custom domains for your AI SaaS Factory deployment after running the Terraform configuration for Night 80.

## What Was Deployed

The Terraform configuration sets up:
- **API Domain**: `api.launch84.com` → Points to API Gateway and backend services
- **Frontend Domain**: `www.launch84.com` → Points to React frontend
- **Apex Domain**: `launch84.com` → Redirects to `www.launch84.com`

## Step 1: Deploy Infrastructure

First, deploy the updated Terraform configuration:

```bash
cd infra/prod
terraform plan
terraform apply
```

## Step 2: Get Load Balancer IP Addresses

After deployment, get the IP addresses for DNS configuration:

```bash
terraform output api_lb_ip_address
terraform output frontend_lb_ip_address
```

Example output:
```
api_lb_ip_address = "34.102.136.180"
frontend_lb_ip_address = "34.102.136.181"
```

## Step 3: Configure DNS Records

In your domain registrar's DNS management console (e.g., Google Domains, Cloudflare, Route 53), create these A records:

### Required DNS Records

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | `api.launch84.com` | `<api_lb_ip_address>` | 300 |
| A | `www.launch84.com` | `<frontend_lb_ip_address>` | 300 |
| A | `launch84.com` | `<frontend_lb_ip_address>` | 300 |

### Example for Google Domains:
1. Go to [Google Domains](https://domains.google.com)
2. Select your domain (`launch84.com`)
3. Click "DNS" in the left sidebar
4. Under "Custom records", add:
   ```
   Type: A, Name: api, Data: 34.102.136.180
   Type: A, Name: www, Data: 34.102.136.181
   Type: A, Name: @, Data: 34.102.136.181
   ```

### Example for Cloudflare:
1. Log into Cloudflare Dashboard
2. Select your domain
3. Go to DNS → Records
4. Add records:
   ```
   Type: A, Name: api, IPv4: 34.102.136.180, Proxy: OFF
   Type: A, Name: www, IPv4: 34.102.136.181, Proxy: OFF
   Type: A, Name: @, IPv4: 34.102.136.181, Proxy: OFF
   ```

**Important**: If using Cloudflare, ensure proxy status is **OFF** (gray cloud) for initial setup.

## Step 4: Monitor SSL Certificate Provisioning

Google Cloud automatically provisions SSL certificates for your custom domains. Monitor the status:

```bash
terraform output api_ssl_certificate_status
terraform output frontend_ssl_certificate_status
```

Certificate states:
- `PROVISIONING` → Certificate is being created (10-20 minutes)
- `ACTIVE` → Certificate is ready and serving traffic
- `FAILED` → Check DNS configuration

## Step 5: Verify Domain Setup

Once DNS propagates (5-60 minutes), test your domains:

```bash
# Test API domain
curl -I https://api.launch84.com/health

# Test frontend domain
curl -I https://www.launch84.com

# Test apex domain redirect
curl -I https://launch84.com
```

Expected responses:
- `200 OK` for API health endpoint
- `200 OK` for frontend
- `301/302 redirect` for apex domain to www

## Step 6: Update Application Configuration

Update any hardcoded URLs in your application:

### Frontend Configuration
Update environment variables in your React app:

```typescript
// ui/src/lib/api.ts
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://api.launch84.com'
  : 'http://localhost:8080';
```

### Backend Configuration
Update CORS origins in your API Gateway:

```python
# api-gateway/app.py
CORS_ORIGINS = [
    'https://www.launch84.com',
    'https://launch84.com',
    'http://localhost:3000'  # For development
]
```

## Troubleshooting

### DNS Not Resolving
```bash
# Check DNS propagation
dig api.launch84.com
dig www.launch84.com

# Check from different locations
nslookup api.launch84.com 8.8.8.8
```

### SSL Certificate Issues
```bash
# Check certificate details
openssl s_client -connect api.launch84.com:443 -servername api.launch84.com

# Force refresh certificate status
gcloud compute ssl-certificates describe api-ssl-cert --global
```

### 502/503 Errors
1. Check Cloud Run service health:
   ```bash
   gcloud run services describe api-gateway --region=us-central1
   ```
2. Verify load balancer backend health:
   ```bash
   gcloud compute backend-services get-health api-backend-service --global
   ```

### Common Issues

1. **DNS TTL too high**: Lower TTL to 300 seconds for faster propagation
2. **Cloudflare proxy enabled**: Disable proxy (gray cloud) during initial setup
3. **Mixed content warnings**: Ensure all API calls use HTTPS
4. **Certificate not provisioning**: Verify DNS records point to correct IPs

## Monitoring

Set up monitoring for your custom domains:

```bash
# Cloud Monitoring uptime checks
gcloud alpha monitoring uptime-check-configs create \
  --display-name="Frontend Uptime Check" \
  --monitored-resource-type="uptime_url" \
  --hostname="www.launch84.com" \
  --path="/" \
  --port=443 \
  --use-ssl

gcloud alpha monitoring uptime-check-configs create \
  --display-name="API Uptime Check" \
  --monitored-resource-type="uptime_url" \
  --hostname="api.launch84.com" \
  --path="/health" \
  --port=443 \
  --use-ssl
```

## Security Considerations

1. **HSTS Headers**: Configure in your load balancer
2. **CAA Records**: Add DNS CAA records for certificate authority authorization
3. **Security Headers**: Configure CSP, X-Frame-Options, etc.

Example CAA record:
```
Type: CAA, Name: @, Value: 0 issue "letsencrypt.org"
```

## Next Steps

After custom domains are working:
1. Update all documentation and onboarding materials
2. Configure monitoring and alerting for domain health
3. Set up automated SSL certificate renewal monitoring
4. Update CI/CD pipelines to use custom domains for health checks

## Testing Checklist

- [ ] DNS records resolve correctly
- [ ] SSL certificates are ACTIVE
- [ ] HTTPS redirects work (HTTP → HTTPS)
- [ ] Apex domain redirects to www
- [ ] API endpoints respond correctly
- [ ] Frontend loads without mixed content warnings
- [ ] Search engines can crawl the site (robots.txt, sitemap)

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review Cloud Console logs for errors
3. Verify DNS propagation using online tools
4. Contact your domain registrar for DNS-specific issues

---

**Night 80 Completion Criteria:**
✅ Custom domains configured and serving traffic
✅ SSL certificates provisioned and active  
✅ DNS records properly configured
✅ Application updated to use custom domains
✅ Monitoring configured for domain health 
# SaaS Factory Scripts

This directory contains utility scripts for the SaaS Factory platform.

## OAuth Authentication Scripts

### 🚀 `setup_oauth_env.py` - OAuth Environment Setup
**Purpose**: Interactive script to configure OAuth environment variables
**Usage**: `python scripts/setup_oauth_env.py`
**What it does**:
- Prompts for Google and GitHub OAuth credentials
- Updates backend environment configuration
- Creates frontend `.env.local` file
- Provides step-by-step guidance

**When to use**: First time OAuth setup or when updating OAuth credentials

### 🔍 `test_oauth_config.py` - Comprehensive OAuth Test
**Purpose**: Full OAuth configuration validation and testing
**Usage**: `python scripts/test_oauth_config.py`
**What it does**:
- Tests OAuth status endpoint
- Checks environment variables
- Tests OAuth endpoints
- Validates database configuration
- Provides detailed configuration status

**When to use**: After OAuth setup to verify everything is working correctly

### ⚡ `quick_oauth_test.py` - Quick OAuth Endpoint Test
**Purpose**: Fast test of OAuth endpoint accessibility
**Usage**: `python scripts/quick_oauth_test.py`
**What it does**:
- Quick test of OAuth endpoints
- Basic connectivity check
- Fast feedback on OAuth status

**When to use**: Quick verification that OAuth endpoints are accessible

## Usage Examples

### Complete OAuth Setup Workflow
```bash
# 1. Set up OAuth environment variables
python scripts/setup_oauth_env.py

# 2. Test OAuth configuration
python scripts/test_oauth_config.py

# 3. Quick test OAuth endpoints
python scripts/quick_oauth_test.py
```

### Quick OAuth Status Check
```bash
# Just check if OAuth endpoints are working
python scripts/quick_oauth_test.py
```

### Troubleshooting OAuth Issues
```bash
# Comprehensive diagnostic test
python scripts/test_oauth_config.py
```

## Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)
- SaaS Factory backend running on port 8000
- OAuth applications created in Google Cloud Console and GitHub

## Script Dependencies

- `setup_oauth_env.py`: No external dependencies
- `test_oauth_config.py`: Requires `requests` library
- `quick_oauth_test.py`: Requires `requests` library

## Output Examples

### Successful OAuth Configuration
```
🚀 SaaS Factory OAuth Configuration Test
==================================================
✅ OAuth Status Check:
   Google OAuth: ✅ Enabled
   GitHub OAuth: ✅ Enabled
   Google Client ID: ✅ Configured
   GitHub Client ID: ✅ Configured

🔍 Environment Variable Check:
   GOOGLE_OAUTH_ENABLED: ✅ Set to 'true'
   GOOGLE_CLIENT_ID: ✅ Set (hidden)
   GITHUB_OAUTH_ENABLED: ✅ Set to 'true'
   GITHUB_CLIENT_ID: ✅ Set (hidden)

🎉 OAuth is fully configured and working!
```

### OAuth Configuration Issues
```
❌ OAuth needs configuration:
   1. Create Google OAuth app in Google Cloud Console
   2. Create GitHub OAuth app in GitHub Developer Settings
   3. Update environment variables with OAuth credentials
   4. Restart backend and frontend services
```

## Troubleshooting

### Common Script Issues

1. **Import Errors**: Make sure you're running from the project root directory
2. **Connection Errors**: Ensure the backend is running on port 8000
3. **Permission Errors**: Make sure scripts are executable (`chmod +x scripts/*.py`)

### Getting Help

- Check the script output for specific error messages
- Verify OAuth app configuration in Google Cloud Console and GitHub
- Review `docs/oauth_setup_complete.md` for detailed setup instructions
- Run `python scripts/test_oauth_config.py` for comprehensive diagnostics

## Next Steps

After running these scripts:
1. **If successful**: Test OAuth flows in your application
2. **If issues found**: Follow the troubleshooting guidance in the script output
3. **For production**: Update OAuth app settings and environment variables

---

**Note**: These scripts are designed to work with the existing SaaS Factory OAuth implementation. All backend and frontend code is already complete - these scripts just help with configuration and testing.

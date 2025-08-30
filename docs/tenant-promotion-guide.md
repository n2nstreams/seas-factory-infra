# Tenant Promotion Guide

## Overview

The SaaS Factory includes an automated tenant promotion system that allows you to upgrade tenants from shared infrastructure to dedicated isolated infrastructure. This process is triggered via GitHub Actions and provides complete data migration and isolation.

## When to Promote Tenants

Tenants should be promoted to isolated infrastructure when:

- **Scale Requirements**: Tenant needs dedicated resources for performance
- **Security Requirements**: Enhanced isolation for sensitive data
- **Compliance Needs**: Regulatory requirements for data separation
- **Custom Configuration**: Tenant-specific database or application settings
- **Premium Tier**: Part of premium service offering

## Promotion Methods

### Method 1: PR Label Trigger (Recommended)

1. **Create a Pull Request** with changes related to the tenant
2. **Add a label** to trigger promotion:
   - Basic: `promote-tenant` (uses default tenant or extracts from PR)
   - Specific: `promote-tenant:acme-corp` (promotes specific tenant)

3. **Wait for automation** - GitHub Actions will:
   - Extract tenant information
   - Validate tenant exists
   - Run isolation script
   - Deploy infrastructure
   - Run validation tests
   - Comment results on PR

### Method 2: Manual Script Execution

```bash
# Check tenant status
python3 scripts/tenant_isolation.py status --tenant-slug=acme-corp

# Promote tenant
python3 scripts/tenant_isolation.py promote --tenant-slug=acme-corp --confirm

# Use make command
make isolate TENANT_ID=acme-corp
```

### Method 3: PR Title/Body Specification

Include tenant information in your PR:

**PR Title Format:**
```
[TENANT: acme-corp] Add custom features for Acme Corporation
```

**PR Body Format:**
```markdown
## Changes
- Custom dashboard features
- Enhanced reporting

## Tenant Information
Tenant: acme-corp
```

## Promotion Process

### 1. Pre-Promotion Validation

- ✅ Tenant exists in database
- ✅ Tenant is currently in shared mode
- ✅ Tenant slug format is valid
- ✅ Database connectivity confirmed

### 2. Isolation Steps

1. **Create Isolated Database**
   ```sql
   CREATE DATABASE "tenant_acme_corp";
   ```

2. **Clone Schema Structure**
   - Copies all tables and relationships
   - Sets up Row Level Security policies
   - Creates application role with proper permissions

3. **Migrate Data**
   ```
   Tables migrated in order:
   - tenants
   - users  
   - projects
   - design_recommendations
   - tech_stack_recommendations
   - agent_events
   - audit_logs
   ```

4. **Update Tenant Status**
   ```json
   {
     "isolation_mode": "isolated",
     "settings": {
       "isolation": {
         "isolated_db_name": "tenant_acme_corp",
         "isolated_at": "2024-01-15T10:30:00Z",
         "migration_version": "001"
       }
     }
   }
   ```

5. **Create Routing Configuration**
   ```json
   {
     "tenant_slug": "acme-corp",
     "isolation_mode": "isolated",
     "database": {
       "name": "tenant_acme_corp",
       "host": "localhost",
       "port": 5432
     },
     "endpoints": {
       "api": "api-acme-corp.factory.local",
       "ui": "app-acme-corp.factory.local"
     }
   }
   ```

### 3. Infrastructure Deployment

- **Database**: Isolated PostgreSQL instance
- **Application**: Dedicated Cloud Run revision
- **Load Balancer**: Custom routing rules
- **DNS**: Tenant-specific subdomains
- **Monitoring**: Isolated metrics and logging

### 4. Post-Promotion Validation

- ✅ Data integrity checks
- ✅ Access control verification
- ✅ Performance baseline tests
- ✅ Security validation
- ✅ Application functionality tests

## Tenant Access After Promotion

### Database Configuration

Isolated tenants get their own database connection:

```python
# Shared tenant (before promotion)
DATABASE_URL = "postgresql://user:pass@host:5432/factorydb"

# Isolated tenant (after promotion)  
DATABASE_URL = "postgresql://user:pass@host:5432/tenant_acme_corp"
```

### API Endpoints

```bash
# Shared endpoint (before)
curl https://api.factory.local/projects

# Isolated endpoint (after)
curl https://api-acme-corp.factory.local/projects
```

### UI Access

```bash
# Shared UI (before)
https://app.factory.local

# Isolated UI (after)
https://app-acme-corp.factory.local
```

## Monitoring and Maintenance

### Health Checks

```bash
# Check tenant status
make tenant-status TENANT_ID=acme-corp

# Manual validation
python3 scripts/tenant_isolation.py status --tenant-slug=acme-corp
```

### Performance Monitoring

```sql
-- Query performance on isolated database
SELECT 
    schemaname,
    tablename,
    n_tup_ins,
    n_tup_upd,
    n_tup_del
FROM pg_stat_user_tables;
```

### Cost Tracking

Isolated tenants incur additional costs for:
- Dedicated database instance
- Separate application containers  
- Additional load balancer rules
- Enhanced monitoring/logging

## Rollback Process

If issues occur, tenants can be moved back to shared infrastructure:

```bash
# Emergency rollback (not yet implemented)
python3 scripts/tenant_isolation.py rollback --tenant-slug=acme-corp --confirm
```

**Rollback steps:**
1. Export data from isolated database
2. Import back to shared database  
3. Update tenant status to shared
4. Remove routing configuration
5. Cleanup isolated infrastructure

## Troubleshooting

### Common Issues

**Issue**: Promotion fails with "Tenant not found"
```bash
# Solution: Verify tenant exists
python3 scripts/tenant_isolation.py status --tenant-slug=acme-corp
```

**Issue**: Database connection timeout
```bash
# Solution: Check database connectivity
psql -h localhost -p 5432 -U factoryadmin -d factorydb -c "SELECT 1;"
```

**Issue**: Permission denied during migration
```bash
# Solution: Verify database permissions
psql -h localhost -p 5432 -U factoryadmin -d postgres -c "\\du"
```

### Logs and Debugging

```bash
# View GitHub Actions logs
# Go to: https://github.com/your-org/saas-factory/actions

# Local script debugging
python3 scripts/tenant_isolation.py promote --tenant-slug=test-tenant --confirm

# Database migration logs
tail -f /var/log/postgresql/postgresql.log
```

## Security Considerations

### Data Isolation

- ✅ Complete database separation
- ✅ No shared table access
- ✅ Isolated connection pools
- ✅ Separate backup strategies

### Network Isolation

- ✅ Tenant-specific subdomains
- ✅ Isolated load balancer rules
- ✅ Separate SSL certificates
- ✅ Network-level access controls

### Access Control

- ✅ Tenant-specific API keys
- ✅ Isolated authentication flows
- ✅ Separate audit trails
- ✅ Enhanced monitoring

## Best Practices

1. **Test in Staging**: Always test promotions in non-production environment
2. **Backup First**: Ensure complete backups before promotion
3. **Monitor Performance**: Track metrics before and after promotion  
4. **Validate Functionality**: Run comprehensive tests post-promotion
5. **Document Changes**: Keep detailed records of all promotions
6. **Plan Rollback**: Have rollback plan ready before starting
7. **Communicate**: Notify stakeholders of planned promotions

## Support and Escalation

For issues with tenant promotion:

1. **Check GitHub Actions logs** for detailed error messages
2. **Review database logs** for connection/permission issues  
3. **Verify infrastructure** status in cloud console
4. **Contact DevOps team** for urgent production issues
5. **Create incident ticket** for tracked resolution

---

*Last updated: January 2024*  
*Version: 1.0* 
# Module 13: Final Data Migration - Source-of-Truth Cutover

## 🎯 **Module Overview**

**Objective:** Flip per-table reads to Supabase once proven, completing the source-of-truth migration from legacy systems to the new Supabase infrastructure.

**Status:** 🔄 **IN PROGRESS** - Implementation Complete, Ready for Testing

**Priority:** **CRITICAL** - This is the final step in the data migration process

---

## 📋 **Module Requirements**

### **Key Requirements**
- ✅ Pre-cutover checklist and freeze window system
- ✅ Post-cutover monitoring and reconciliation
- ✅ Per-table read switch control with feature flags
- ✅ Comprehensive rollback procedures
- ✅ Audit logging for compliance

### **Success Criteria**
- 24–48h after switch: zero missing keys
- Referential integrity clean across all tables
- Drift < 0.05% then trending to 0
- Feature flag controls cutover process
- Zero data loss during migration

### **Rollback Plan**
- Re-enable legacy reads for affected tables
- Queue writes for replay if necessary
- Maintain data consistency during rollback
- Instant rollback capability via feature flags

---

## 🏗️ **Architecture & Implementation**

### **Core Components**

#### 1. **Final Data Migration Service** (`data-migration-final.ts`)
- **Purpose:** Orchestrates the complete cutover process
- **Features:**
  - Pre-cutover validation and preparation
  - Cutover execution with freeze windows
  - Rollback procedures and audit logging
  - Reconciliation monitoring and drift detection

#### 2. **Admin Interface** (`/app2/admin/final-data-migration`)
- **Purpose:** Comprehensive management interface for migration operations
- **Features:**
  - Migration overview and progress tracking
  - Table-by-table status management
  - Freeze window scheduling and management
  - Reconciliation monitoring dashboard

#### 3. **API Service** (`api/final-data-migration.ts`)
- **Purpose:** Server-side operations and database interactions
- **Features:**
  - CRUD operations for all migration entities
  - Cutover execution and rollback
  - Data validation and consistency checking
  - Statistics and reporting

#### 4. **Database Schema** (`migrations/013_create_final_data_migration_tables.sql`)
- **Purpose:** Persistent storage for migration state and audit trail
- **Tables:**
  - `cutover_tables` - Migration status for each table
  - `cutover_checklists` - Pre-cutover validation tracking
  - `freeze_windows` - Scheduled freeze periods
  - `reconciliation_jobs` - Data reconciliation tracking
  - `cutover_audit_log` - Complete audit trail

### **Data Flow**

```
1. Pre-Cutover Validation
   ↓
2. Freeze Window Activation
   ↓
3. Read Source Switch (Legacy → Supabase)
   ↓
4. Reconciliation Monitoring
   ↓
5. Post-Cutover Validation
   ↓
6. Status Update (Completed/Rolled Back)
```

---

## 🚀 **Implementation Details**

### **Feature Flag Integration**
```typescript
// Module 13 feature flag
data_migration_final: {
  name: 'Final Data Migration',
  description: 'Source-of-truth cutover to new systems',
  enabled: false,
  rolloutPercentage: 0,
  environment: 'development'
}
```

### **Table Migration States**
1. **`pending`** - Table not yet prepared for cutover
2. **`ready`** - All validation checks passed, ready for cutover
3. **`cutover`** - Cutover in progress, freeze window active
4. **`completed`** - Successfully migrated to Supabase
5. **`rolled_back`** - Rolled back to legacy system

### **Read Source Control**
- **`legacy`** - All reads from legacy system
- **`supabase`** - All reads from Supabase (target state)
- **`dual`** - Reads from both systems (transition state)

---

## 📊 **Pre-Cutover Checklist**

### **Data Consistency Validation**
- [ ] Drift < 0.05% between legacy and Supabase
- [ ] Record counts match within acceptable tolerance
- [ ] Golden queries return identical results
- [ ] Data integrity checks pass

### **Referential Integrity**
- [ ] Foreign key relationships validated
- [ ] No orphaned records detected
- [ ] Constraint violations resolved
- [ ] Cross-table consistency verified

### **Performance Validation**
- [ ] Response times within SLOs
- [ ] Throughput meets requirements
- [ ] Resource usage optimized
- [ ] Index performance validated

### **Security Validation**
- [ ] RLS policies tested and verified
- [ ] Tenant isolation confirmed
- [ ] Access control validated
- [ ] Audit logging operational

### **Operational Readiness**
- [ ] Backup procedures verified
- [ ] Freeze window scheduled
- [ ] Team notified and prepared
- [ ] Rollback plan ready

---

## 🕐 **Freeze Window Management**

### **Freeze Window Types**
1. **Scheduled** - Planned maintenance window
2. **Active** - Currently in freeze mode
3. **Completed** - Freeze window finished
4. **Cancelled** - Freeze window cancelled

### **Freeze Window Process**
```
1. Schedule freeze window with affected tables
2. Activate freeze window before cutover
3. Execute cutover during freeze period
4. Complete cutover and deactivate freeze
5. Monitor post-cutover stability
```

### **Freeze Window Duration**
- **Typical Duration:** 2-4 hours
- **Extended Duration:** Up to 8 hours for complex migrations
- **Emergency Freeze:** Immediate activation for critical issues

---

## 🔄 **Cutover Execution Process**

### **Step 1: Pre-Cutover Validation**
```typescript
const checklist = await finalDataMigrationService.prepareTableForCutover(tableName)
```

### **Step 2: Freeze Window Activation**
```typescript
await finalDataMigrationService.activateFreezeWindow(tableName)
```

### **Step 3: Read Source Switch**
```typescript
await finalDataMigrationService.switchReadSource(tableName, 'supabase')
```

### **Step 4: Status Update**
```typescript
await finalDataMigrationService.updateCutoverTableStatus(tableName, 'cutover')
```

### **Step 5: Reconciliation Monitoring**
```typescript
await finalDataMigrationService.startReconciliationMonitoring(tableName)
```

---

## 📈 **Post-Cutover Monitoring**

### **Reconciliation Jobs**
- **Type:** `incremental` - Continuous monitoring
- **Frequency:** Every 15 minutes
- **Scope:** All migrated tables
- **Alerting:** Drift > 0.1% triggers alerts

### **Drift Detection**
- **Threshold:** 0.05% for warning, 0.1% for critical
- **Monitoring:** Real-time drift calculation
- **Resolution:** Automatic reconciliation jobs
- **Reporting:** Daily drift reports

### **Performance Monitoring**
- **Response Times:** p95 < 2.0s maintained
- **Throughput:** No degradation from baseline
- **Error Rates:** < 1% maintained
- **Resource Usage:** Within acceptable limits

---

## 🚨 **Rollback Procedures**

### **Automatic Rollback Triggers**
- Data drift > 0.5%
- Performance degradation > 20%
- Error rate > 5%
- Security violations detected

### **Manual Rollback Process**
```typescript
await finalDataMigrationService.rollbackTableCutover(tableName, userId, reason)
```

### **Rollback Steps**
1. **Immediate:** Switch read source back to legacy
2. **Stop Monitoring:** Halt reconciliation jobs
3. **Deactivate Freeze:** End freeze window
4. **Update Status:** Mark as rolled back
5. **Audit Log:** Record rollback reason
6. **Team Notification:** Alert stakeholders

---

## 🔍 **Audit & Compliance**

### **Audit Logging**
- **All Operations:** Prepare, cutover, rollback, validation
- **User Tracking:** Who performed what operation
- **Timing:** Exact timestamps for all actions
- **Details:** Complete operation context and results

### **Compliance Requirements**
- **GDPR:** Data processing logs maintained
- **SOC2:** Change management audit trail
- **PCI:** Payment data migration tracking
- **Internal:** Business process compliance

---

## 🧪 **Testing Strategy**

### **Unit Testing**
- Service method validation
- API endpoint testing
- Database operation testing
- Error handling validation

### **Integration Testing**
- End-to-end cutover process
- Rollback procedure validation
- Freeze window management
- Reconciliation job execution

### **Performance Testing**
- Cutover execution time
- Post-cutover performance
- Reconciliation job performance
- System resource usage

### **Security Testing**
- RLS policy validation
- Access control verification
- Tenant isolation testing
- Audit log integrity

---

## 📚 **Usage Examples**

### **Prepare Table for Cutover**
```typescript
import { finalDataMigrationService } from '@/lib/data-migration-final'

// Prepare a table for cutover
const checklist = await finalDataMigrationService.prepareTableForCutover('users')
console.log('Preparation checklist:', checklist)
```

### **Execute Table Cutover**
```typescript
// Execute cutover for a table
const result = await finalDataMigrationService.executeTableCutover('users', userId)
if (result.success) {
  console.log('Cutover completed successfully')
} else {
  console.error('Cutover failed:', result.errors)
}
```

### **Rollback Table Cutover**
```typescript
// Rollback cutover if issues arise
await finalDataMigrationService.rollbackTableCutover('users', userId, 'Performance issues detected')
console.log('Rollback completed')
```

### **Monitor Migration Status**
```typescript
// Get overall migration status
const status = await finalDataMigrationService.getCutoverStatus()
console.log('Migration status:', status)

// Get specific table status
const tableStatus = await finalDataMigrationService.getTableCutoverStatus('users')
console.log('Table status:', tableStatus)
```

---

## 🚀 **Deployment Instructions**

### **Prerequisites**
1. **Module 3 Complete:** Database migration with dual-write operational
2. **Module 11 Complete:** Security and compliance system operational
3. **Module 12 Complete:** Performance monitoring system operational
4. **Feature Flags:** `data_migration_final` flag configured

### **Database Migration**
```bash
# Run the migration
psql -h your-supabase-host -U postgres -d postgres -f dev/migrations/013_create_final_data_migration_tables.sql
```

### **Feature Flag Activation**
```typescript
// Enable the final data migration feature
await featureFlagService.setFeatureFlag('data_migration_final', true)
```

### **Service Deployment**
1. Deploy the new service files
2. Restart the application
3. Verify admin interface accessibility
4. Test basic functionality

---

## 🔧 **Configuration**

### **Environment Variables**
```bash
# Database configuration
DATABASE_URL=your-supabase-connection-string

# Feature flag configuration
FEATURE_FLAG_API_URL=your-feature-flag-service-url

# Monitoring configuration
SENTRY_DSN=your-sentry-dsn
VERCEL_ANALYTICS_ID=your-vercel-analytics-id
```

### **Feature Flag Settings**
```typescript
// Development
data_migration_final: { enabled: false, rolloutPercentage: 0 }

// Staging
data_migration_final: { enabled: true, rolloutPercentage: 100 }

// Production
data_migration_final: { enabled: false, rolloutPercentage: 0 } // Enable when ready
```

---

## 📊 **Monitoring & Alerting**

### **Key Metrics**
- **Migration Progress:** Percentage of tables completed
- **Drift Detection:** Data consistency monitoring
- **Performance Impact:** Response time and throughput
- **Error Rates:** Cutover and rollback success rates

### **Alerting Rules**
- **Critical:** Data drift > 0.5%
- **Warning:** Data drift > 0.1%
- **Info:** Cutover completion milestones
- **Success:** Migration completion

### **Dashboards**
- **Migration Overview:** Overall progress and status
- **Table Status:** Individual table migration status
- **Freeze Windows:** Scheduled and active freeze periods
- **Reconciliation:** Active reconciliation jobs and drift

---

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Table Not Ready for Cutover**
- **Symptom:** Cannot execute cutover for table
- **Cause:** Validation checks failed
- **Solution:** Review checklist and resolve issues

#### **High Data Drift**
- **Symptom:** Drift percentage above threshold
- **Cause:** Data synchronization issues
- **Solution:** Investigate ETL processes and resolve

#### **Performance Degradation**
- **Symptom:** Response times increased after cutover
- **Cause:** New system performance issues
- **Solution:** Optimize queries and indexes

#### **Rollback Failures**
- **Symptom:** Cannot rollback to legacy system
- **Cause:** System state corruption
- **Solution:** Manual intervention and system restoration

### **Debug Commands**
```typescript
// Check table status
const status = await finalDataMigrationService.getTableCutoverStatus('tableName')

// Validate data consistency
const consistency = await finalDataMigrationService.validateDataConsistency('tableName')

// Check reconciliation jobs
const jobs = await finalDataMigrationService.getActiveReconciliationJobs()
```

---

## 📈 **Performance Considerations**

### **Cutover Execution**
- **Target Time:** < 30 minutes per table
- **Freeze Window:** 2-4 hours maximum
- **Rollback Time:** < 15 minutes
- **Recovery Time:** < 1 hour

### **Resource Usage**
- **Database Connections:** Monitor connection pool usage
- **Memory Usage:** Track memory consumption during cutover
- **CPU Usage:** Monitor processing overhead
- **Network I/O:** Track data transfer volumes

### **Optimization Strategies**
- **Batch Processing:** Process multiple tables in parallel
- **Incremental Validation:** Validate only changed data
- **Caching:** Cache validation results
- **Async Operations:** Non-blocking cutover execution

---

## 🔒 **Security Considerations**

### **Access Control**
- **Admin Only:** All migration operations require admin privileges
- **Audit Logging:** Complete audit trail for all operations
- **Role-Based Access:** Growth plan users can access admin features
- **Session Validation:** Verify user authentication before operations

### **Data Protection**
- **Encryption:** All data encrypted in transit and at rest
- **Tenant Isolation:** RLS policies enforce tenant boundaries
- **PII Handling:** Sensitive data handled according to privacy policies
- **Compliance:** GDPR, SOC2, and PCI compliance maintained

---

## 📋 **Checklist for Go-Live**

### **Pre-Go-Live**
- [ ] All validation checks pass
- [ ] Freeze windows scheduled
- [ ] Team notified and prepared
- [ ] Rollback procedures tested
- [ ] Monitoring and alerting configured
- [ ] Backup procedures verified

### **Go-Live Execution**
- [ ] Activate freeze window
- [ ] Execute cutover for first table
- [ ] Monitor system stability
- [ ] Validate data consistency
- [ ] Complete cutover process
- [ ] Deactivate freeze window

### **Post-Go-Live**
- [ ] Monitor reconciliation jobs
- [ ] Track performance metrics
- [ ] Validate data integrity
- [ ] Document lessons learned
- [ ] Plan next table migration
- [ ] Update migration status

---

## 🎯 **Next Steps**

### **Immediate Actions**
1. **Test Implementation:** Validate all functionality in staging
2. **Prepare First Table:** Ready one table for cutover testing
3. **Schedule Freeze Window:** Plan first cutover execution
4. **Team Training:** Ensure all stakeholders understand the process

### **Short Term (1-2 weeks)**
1. **First Cutover:** Execute cutover for one table
2. **Monitor & Validate:** Ensure stability and performance
3. **Document Process:** Refine procedures based on experience
4. **Plan Next Tables:** Identify next tables for migration

### **Medium Term (1-2 months)**
1. **Complete Core Tables:** Migrate all critical tables
2. **Performance Optimization:** Optimize based on real usage
3. **Process Refinement:** Improve procedures and automation
4. **Team Scaling:** Train additional team members

### **Long Term (3-6 months)**
1. **Full Migration:** Complete migration of all tables
2. **Legacy Decommission:** Plan Module 14 execution
3. **Process Automation:** Fully automated migration pipeline
4. **Knowledge Transfer:** Document and train team

---

## 📚 **Additional Resources**

### **Documentation**
- [Module 3: Database Migration](../templates/ts_swap_template.md#module-3-database-on-ramp---supabase-postgres--completed)
- [Module 11: Security & Compliance](../templates/ts_swap_template.md#module-11-security--compliance---rls--least-privilege--audits--completed)
- [Module 12: Performance & Cost](../templates/ts_swap_template.md#module-12-performance--cost---budgets-quotas-and-load-tests--completed)

### **Code References**
- [Final Data Migration Service](../../ui/nextjs/src/lib/data-migration-final.ts)
- [Admin Interface](../../ui/nextjs/src/app/app2/admin/final-data-migration/page.tsx)
- [API Service](../../ui/nextjs/src/lib/api/final-data-migration.ts)
- [Database Schema](../../dev/migrations/013_create_final_data_migration_tables.sql)

### **Related Modules**
- **Module 3:** Database foundation and dual-write system
- **Module 11:** Security and compliance framework
- **Module 12:** Performance monitoring and validation
- **Module 14:** Legacy system decommission (next)

---

## 🏆 **Success Metrics**

### **Technical Metrics**
- **Migration Success Rate:** 100% successful cutovers
- **Data Consistency:** Drift < 0.05% maintained
- **Performance:** No degradation from baseline
- **Security:** Zero security violations

### **Business Metrics**
- **User Experience:** No service disruption
- **Data Integrity:** Zero data loss
- **Compliance:** All audit requirements met
- **Cost Optimization:** Reduced infrastructure costs

### **Operational Metrics**
- **Cutover Time:** < 30 minutes per table
- **Rollback Time:** < 15 minutes if needed
- **Monitoring Coverage:** 100% of migrated tables
- **Alert Response:** < 5 minutes for critical issues

---

**Module Status:** 🔄 **Implementation Complete - Ready for Testing**  
**Next Phase:** Testing and Validation in Staging Environment  
**Estimated Completion:** 2-4 weeks with proper testing and validation  
**Risk Level:** **MEDIUM** - Complex operation with comprehensive rollback procedures

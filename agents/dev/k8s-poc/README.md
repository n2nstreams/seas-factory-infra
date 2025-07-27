# Night 68: DevAgent K8s POC - GKE Autopilot Deployment

This directory contains the **Night 68** Kubernetes Proof of Concept (POC) for deploying the DevAgent to **GKE Autopilot** to ensure portability beyond Cloud Run.

## 🎯 Objectives

- **Portability**: Demonstrate DevAgent can run on Kubernetes, not just Cloud Run
- **GKE Autopilot**: Leverage managed Kubernetes without node management
- **Feature Parity**: Maintain all existing functionality (database access, secrets, networking)
- **Production Ready**: Include monitoring, scaling, and security best practices
- **Comparison**: Document differences and benefits vs Cloud Run deployment

## 📋 Current vs Target Architecture

### Current (Cloud Run)
```
Internet → Cloud Load Balancer → Cloud Run → VPC Connector → Cloud SQL
                                     ↓
                              Secret Manager (API Keys)
```

### Target (GKE Autopilot)
```
Internet → Kubernetes Service → DevAgent Pod → Private Service Connect → Cloud SQL
                                     ↓
                        Kubernetes Secrets (from Secret Manager)
```

## 🏗️ Directory Structure

```
k8s-poc/
├── README.md                    # This file
├── manifests/                   # Kubernetes manifests
│   ├── namespace.yaml          # Dedicated namespace
│   ├── configmap.yaml          # Configuration settings
│   ├── secret.yaml             # Secret management
│   ├── deployment.yaml         # DevAgent deployment
│   ├── service.yaml            # Internal service
│   ├── ingress.yaml            # External access
│   └── hpa.yaml                # Horizontal Pod Autoscaler
├── scripts/                     # Deployment and management scripts
│   ├── deploy.sh               # Main deployment script
│   ├── cleanup.sh              # Cleanup script
│   ├── sync-secrets.sh         # Secret synchronization
│   └── health-check.sh         # Health monitoring
├── terraform/                   # Infrastructure as Code
│   ├── gke-cluster.tf          # GKE Autopilot cluster
│   ├── networking.tf           # VPC and connectivity
│   └── variables.tf            # Configuration variables
└── docs/                        # Additional documentation
    ├── deployment-guide.md     # Step-by-step deployment
    ├── monitoring.md           # Monitoring and logging
    └── troubleshooting.md      # Common issues and fixes
```

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Install required tools
gcloud components install gke-gcloud-auth-plugin kubectl
```

### 2. Deploy Infrastructure

```bash
# Navigate to terraform directory
cd terraform/

# Initialize and apply
terraform init
terraform apply
```

### 3. Deploy DevAgent

```bash
# Run deployment script
./scripts/deploy.sh

# Verify deployment
kubectl get pods -n devagent-poc
```

### 4. Test Connectivity

```bash
# Port forward for testing
kubectl port-forward -n devagent-poc service/devagent 8083:8083

# Test endpoint
curl http://localhost:8083/health
```

## 🔧 Key Features

### GKE Autopilot Benefits
- **Serverless Kubernetes**: No node management required
- **Auto-scaling**: Pods scale based on CPU/Memory usage
- **Cost Optimization**: Pay only for running pods
- **Security Hardening**: Built-in security best practices
- **Observability**: Integrated monitoring and logging

### Maintained Cloud Run Features
- ✅ **Database Connectivity**: Private connection to Cloud SQL
- ✅ **Secret Management**: Integration with Google Secret Manager
- ✅ **Auto-scaling**: Horizontal Pod Autoscaler (HPA)
- ✅ **Load Balancing**: Kubernetes native load balancing
- ✅ **Monitoring**: Cloud Monitoring integration
- ✅ **Logging**: Structured logging to Cloud Logging

### New Kubernetes Features
- 🆕 **Pod-level Resource Control**: Granular CPU/Memory limits
- 🆕 **Rolling Updates**: Zero-downtime deployments
- 🆕 **Health Checks**: Liveness and readiness probes
- 🆕 **Config Management**: ConfigMaps and Secrets
- 🆕 **Multi-container Pods**: Sidecar containers for enhanced functionality

## 📊 Resource Configuration

### DevAgent Pod Specifications
```yaml
resources:
  requests:
    cpu: "250m"      # 0.25 CPU cores
    memory: "512Mi"  # 512MB RAM
  limits:
    cpu: "1000m"     # 1 CPU core
    memory: "1Gi"    # 1GB RAM max
```

### Auto-scaling Configuration
```yaml
minReplicas: 1
maxReplicas: 10
targetCPUUtilizationPercentage: 70
targetMemoryUtilizationPercentage: 80
```

## 🔒 Security Considerations

### Network Security
- **Private Cluster**: Nodes have private IP addresses
- **Authorized Networks**: Restricted cluster access
- **Network Policies**: Pod-to-pod communication control
- **Private Service Connect**: Secure database connectivity

### Pod Security
- **Security Context**: Non-root user execution
- **Read-only Root Filesystem**: Immutable container filesystem
- **No Privilege Escalation**: Limited container permissions
- **Resource Quotas**: Prevent resource exhaustion

### Secret Management
- **Google Secret Manager**: External secret storage
- **Kubernetes Secrets**: In-cluster secret distribution
- **Secret Rotation**: Automated secret refresh
- **Least Privilege**: Minimal required permissions

## 📈 Monitoring and Observability

### Metrics
- **Pod Metrics**: CPU, Memory, Network usage
- **Application Metrics**: Request rates, response times
- **Business Metrics**: Code generation success rates
- **Cost Metrics**: Resource consumption tracking

### Logging
- **Structured Logging**: JSON formatted logs
- **Log Aggregation**: Cloud Logging integration
- **Log Levels**: Debug, Info, Warning, Error
- **Correlation IDs**: Request tracking across services

### Alerting
- **Pod Health**: Liveness and readiness failures
- **Resource Usage**: High CPU/Memory consumption
- **Error Rates**: Application error thresholds
- **Response Times**: Latency monitoring

## 🔄 Deployment Strategies

### Rolling Updates
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 1
    maxSurge: 1
```

### Blue-Green Deployment
- Deploy new version alongside current
- Switch traffic using service selector
- Rollback by switching selector back

### Canary Deployment
- Deploy small percentage of traffic
- Monitor metrics and errors
- Gradually increase traffic percentage

## 🔧 Operational Commands

### Deployment Management
```bash
# Deploy/Update
kubectl apply -f manifests/

# Scale manually
kubectl scale deployment devagent -n devagent-poc --replicas=3

# Check status
kubectl get all -n devagent-poc

# View logs
kubectl logs -f deployment/devagent -n devagent-poc
```

### Debugging
```bash
# Shell into pod
kubectl exec -it deployment/devagent -n devagent-poc -- /bin/bash

# Port forward
kubectl port-forward -n devagent-poc service/devagent 8083:8083

# Describe resources
kubectl describe pod -n devagent-poc
```

### Secret Management
```bash
# Sync secrets from Secret Manager
./scripts/sync-secrets.sh

# Update secret
kubectl create secret generic devagent-secrets \
  --from-literal=openai-api-key=sk-xxx \
  --dry-run=client -o yaml | kubectl apply -f -
```

## 📋 Migration Guide

### From Cloud Run to GKE

1. **Infrastructure Setup**
   - Create GKE Autopilot cluster
   - Configure VPC and networking
   - Set up Private Service Connect

2. **Application Preparation**
   - Build and push container to Artifact Registry
   - Create Kubernetes manifests
   - Configure secrets and config maps

3. **Deployment**
   - Deploy to staging namespace first
   - Test all functionality
   - Switch traffic from Cloud Run

4. **Monitoring**
   - Set up monitoring dashboards
   - Configure alerting rules
   - Monitor resource usage

### Rollback Strategy
- Keep Cloud Run deployment active
- Use DNS or load balancer to switch traffic
- Maintain data consistency during switch

## 🎯 Success Criteria

- ✅ DevAgent runs successfully on GKE Autopilot
- ✅ All API endpoints function correctly
- ✅ Database connectivity maintained
- ✅ Secret management working
- ✅ Auto-scaling responds to load
- ✅ Monitoring and logging operational
- ✅ Performance matches Cloud Run baseline

## 🔮 Future Enhancements

### Multi-Cloud Portability
- **Azure AKS**: Deploy to Azure Kubernetes Service
- **AWS EKS**: Deploy to Amazon Elastic Kubernetes Service
- **On-Premises**: Deploy to self-managed Kubernetes

### Advanced Features
- **Service Mesh**: Istio for advanced traffic management
- **GitOps**: ArgoCD for automated deployments
- **Policy Enforcement**: Open Policy Agent (OPA)
- **Multi-tenancy**: Namespace-based tenant isolation

## 📚 Additional Resources

- [GKE Autopilot Documentation](https://cloud.google.com/kubernetes-engine/docs/concepts/autopilot-overview)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [Cloud SQL Private Service Connect](https://cloud.google.com/sql/docs/postgres/private-service-connect)
- [Google Secret Manager CSI Driver](https://github.com/GoogleCloudPlatform/secrets-store-csi-driver-provider-gcp)

---

*This POC demonstrates the portability benefits of containerized applications and validates the feasibility of multi-cloud deployment strategies for the SaaS Factory platform.* 
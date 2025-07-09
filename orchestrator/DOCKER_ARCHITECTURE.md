# Docker Architecture Issue: ARM64 vs AMD64

## 🚨 **The Problem**

When developing on **Apple Silicon Macs (M1/M2)**, Docker builds container images for the **ARM64** architecture by default. However, **Google Cloud Run** requires **AMD64/Linux** architecture, causing deployment failures with this error:

```
ERROR: Cloud Run does not support image 'xxx': Container manifest type 'application/vnd.oci.image.index.v1+json' must support amd64/linux.
```

## 🔍 **Why This Happens**

1. **Apple Silicon Macs** use ARM64 architecture natively
2. **Docker builds for the host architecture by default** (ARM64 on Apple Silicon)
3. **Cloud Run only supports AMD64/Linux** containers
4. **Without explicit platform specification**, builds fail in cloud deployment

## ✅ **Solutions Implemented**

We've implemented multiple layers of protection to prevent this issue:

### 1. **Build Script** (`build.sh`)
```bash
./build.sh 0.5          # Build version 0.5
./build.sh 0.5 --push   # Build and push
```
- Always uses `--platform linux/amd64`
- Includes helpful error messages
- Provides deployment commands

### 2. **Makefile** (`Makefile`)
```bash
make build VERSION=0.5   # Build image
make deploy VERSION=0.5  # Build, push, and deploy
make help               # See all commands
```
- Standardized build commands
- Platform enforcement built-in
- Developer-friendly interface

### 3. **Docker Compose** (`docker-compose.yml`)
```bash
docker-compose build    # Build with correct platform
docker-compose up       # Run locally with AMD64
```
- Platform specified in configuration
- Consistent across team members
- Local testing with production architecture

### 4. **Docker Buildx Builder**
```bash
docker buildx use cloud-builder  # Use the AMD64 builder
```
- System-level configuration
- Consistent across all projects

## 🛠️ **Manual Commands** (If needed)

### Correct Way:
```bash
docker build --platform linux/amd64 -t myimage .
```

### Wrong Way (on Apple Silicon):
```bash
docker build -t myimage .  # ❌ Will create ARM64 image
```

## 🔧 **Best Practices**

1. **Always use the provided tools**:
   - Use `make deploy` instead of manual docker commands
   - Use `./build.sh` for scripted builds
   - Use `docker-compose` for local development

2. **Never build manually without platform flag** on Apple Silicon

3. **Test locally with the same architecture**:
   ```bash
   docker-compose up orchestrator-dev
   ```

4. **Verify image architecture before pushing**:
   ```bash
   docker inspect myimage | grep Architecture
   ```

## 🚀 **Quick Reference**

| Task | Command | Why |
|------|---------|-----|
| Build & Deploy | `make deploy VERSION=x.x` | Uses correct platform automatically |
| Local Development | `docker-compose up orchestrator-dev` | Same architecture as production |
| Dependencies | `make deps` | Updates requirements.txt properly |
| Testing | `make test-api` | Tests deployed endpoints |

## 🎯 **Future Prevention**

- **Use the provided tools** instead of raw docker commands
- **Document platform requirements** in all Dockerfiles
- **Set up CI/CD** to build on AMD64 runners (GitHub Actions, etc.)
- **Team education** about Apple Silicon vs Cloud architecture differences

## 📋 **Checklist Before Cloud Deployment**

- [ ] Used `make deploy` or `./build.sh --push`
- [ ] Verified image builds without platform warnings
- [ ] Tested locally with `docker-compose`
- [ ] Architecture matches `linux/amd64`

This multi-layered approach ensures the ARM64/AMD64 issue never occurs again! 🎉 
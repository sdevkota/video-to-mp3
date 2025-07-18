# 🚀 Deployment Guide

## Google Cloud Run (Recommended)

### Prerequisites
1. [Google Cloud CLI](https://cloud.google.com/sdk/docs/install)
2. [Docker](https://docs.docker.com/get-docker/)
3. Google Cloud Project with billing enabled

### Steps

1. **Create Google Cloud Project**
   ```bash
   gcloud projects create your-project-id
   gcloud config set project your-project-id
   ```

2. **Enable Required APIs**
   ```bash
   gcloud services enable run.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   ```

3. **Configure Authentication**
   ```bash
   gcloud auth login
   gcloud auth configure-docker
   ```

4. **Edit deploy.sh**
   ```bash
   # Edit deploy.sh and change PROJECT_ID
   PROJECT_ID="your-actual-project-id"
   ```

5. **Deploy**
   ```bash
   ./deploy.sh
   ```

### Cost Estimate
- **Free tier**: 2 million requests/month
- **After free tier**: ~$0.40 per 1M requests + compute time
- **Idle apps**: $0 (pay only when used)

---

## Alternative Hosting Options

### 1. Streamlit Cloud (Easiest)
```bash
# Push to GitHub and connect at https://share.streamlit.io/
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/username/video-to-mp3.git
git push -u origin main
```

**Pros**: Free, automatic deployment, easy setup
**Cons**: Limited resources, may not handle ffmpeg well

### 2. Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway init
railway up
```

**Pros**: Simple deployment, good for Python apps
**Cons**: Limited free tier

### 3. Heroku
```bash
# Install Heroku CLI
# Create Procfile
echo "web: streamlit run app.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile

# Create heroku app
heroku create your-app-name
heroku buildpacks:add --index 1 heroku/python
heroku buildpacks:add --index 2 https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git

# Deploy
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

### 4. DigitalOcean App Platform
```yaml
# Create .do/app.yaml
name: video-to-mp3-converter
services:
- name: web
  source_dir: /
  github:
    repo: username/video-to-mp3
    branch: main
  run_command: streamlit run app.py --server.port=8080 --server.address=0.0.0.0
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  http_port: 8080
```

---

## Firebase Hosting (Static Sites Only)

Firebase Hosting only supports static websites, not Python web apps. However, you can:

1. **Use Firebase with Cloud Functions** (Limited)
2. **Use Firebase for frontend + Cloud Run for backend**
3. **Convert to static site** (not practical for this app)

---

## Environment Variables

For production deployment, consider these environment variables:

```bash
# Streamlit configuration
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Optional: Rate limiting
STREAMLIT_SERVER_MAX_UPLOAD_SIZE=200
STREAMLIT_SERVER_MAX_MESSAGE_SIZE=200

# Optional: Caching
STREAMLIT_SERVER_ENABLE_CORS=false
STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=true
```

---

## Troubleshooting

### Common Issues

1. **FFmpeg not found**
   - Solution: Ensure ffmpeg is installed in Docker image
   - For Cloud Run: Use the provided Dockerfile

2. **Memory issues**
   - Solution: Increase memory allocation (2GB recommended)
   - For Cloud Run: Use `--memory 2Gi` flag

3. **Timeout errors**
   - Solution: Increase timeout (5 minutes recommended)
   - For Cloud Run: Use `--timeout 300` flag

4. **Permission errors**
   - Solution: Ensure proper file permissions in container
   - Use `RUN chmod +x` for executable files

### Monitoring

```bash
# Cloud Run logs
gcloud run logs tail --service=video-to-mp3-converter

# Cloud Run metrics
gcloud run services describe video-to-mp3-converter --region=us-central1
```

---

## Security Considerations

1. **Rate limiting**: Implement to prevent abuse
2. **File size limits**: Set reasonable limits for uploads
3. **CORS**: Configure properly for production
4. **Authentication**: Consider adding if needed
5. **HTTPS**: Always use HTTPS in production (automatic with Cloud Run)

---

## Scaling

### Auto-scaling Configuration (Cloud Run)
```bash
gcloud run services update video-to-mp3-converter \
    --min-instances=0 \
    --max-instances=10 \
    --concurrency=10 \
    --cpu=2 \
    --memory=2Gi
```

### Performance Tips
1. Use container caching for faster cold starts
2. Implement connection pooling if using databases
3. Use CDN for static assets
4. Monitor and optimize resource usage

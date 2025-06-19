# Railway Deployment Guide

This guide will walk you through deploying the Note Taking API on Railway with PostgreSQL and Redis.

## 🚀 Quick Deploy

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/note-api)

## 📋 Prerequisites

1. GitHub account
2. Railway account (sign up at [railway.app](https://railway.app))
3. Your repository pushed to GitHub

## 🛠️ Manual Deployment Steps

### Step 1: Create New Project on Railway

1. Log in to [Railway Dashboard](https://railway.app/dashboard)
2. Click "New Project"
3. Choose "Deploy from GitHub repo"
4. Connect your GitHub account and select your repository

### Step 2: Add PostgreSQL Database

1. In your Railway project, click "New Service"
2. Select "Database" → "Add PostgreSQL"
3. Railway automatically provides:
   - `DATABASE_URL` environment variable
   - Automatic backups
   - Connection pooling

### Step 3: Add Redis

1. Click "New Service" again
2. Select "Database" → "Add Redis"
3. Railway automatically provides:
   - `REDIS_URL` environment variable
   - Persistent storage

### Step 4: Configure Environment Variables

Click on your app service, go to "Variables" tab, and add:

```bash
# Required Variables
SECRET_KEY=<generate-using-command-below>
ENVIRONMENT=production
DEBUG=false
API_V1_STR=/api/v1

# CORS (update with your domains)
BACKEND_CORS_ORIGINS=["https://your-app.up.railway.app"]

# Optional Email (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAILS_FROM_EMAIL=noreply@your-app.com
EMAILS_FROM_NAME=NoteAPI
```

**Generate SECRET_KEY:**
```bash
openssl rand -hex 32
```

### Step 5: Configure Deployment

Railway will automatically:
- Detect the Dockerfile
- Build the production image
- Deploy with the correct PORT
- Set up HTTPS with SSL certificate
- Provide a domain: `your-app.up.railway.app`

### Step 6: Custom Domain (Optional)

1. Go to Settings → Domains
2. Add your custom domain
3. Update DNS records as instructed

## 🔧 Service Configuration

### Environment Variables from Services

Railway automatically injects these when you add services:

| Service | Variable | Example Value |
|---------|----------|---------------|
| PostgreSQL | DATABASE_URL | `postgresql://user:pass@host/db` |
| Redis | REDIS_URL | `redis://default:pass@host:6379` |
| Railway | PORT | `8080` (dynamic) |
| Railway | RAILWAY_ENVIRONMENT | `production` |

### Required Manual Configuration

| Variable | How to Get | Example |
|----------|------------|---------|
| SECRET_KEY | `openssl rand -hex 32` | `a1b2c3d4...` |
| SMTP_* | Email provider | See providers below |
| SENTRY_DSN | [sentry.io](https://sentry.io) | `https://key@sentry.io/id` |

## 📧 Email Providers

### Gmail
1. Enable 2-Factor Authentication
2. Generate App Password: [Google App Passwords](https://myaccount.google.com/apppasswords)
3. Use:
   - SMTP_HOST: `smtp.gmail.com`
   - SMTP_PORT: `587`
   - SMTP_USER: Your Gmail
   - SMTP_PASSWORD: App Password

### SendGrid (Recommended for Production)
1. Sign up at [sendgrid.com](https://sendgrid.com)
2. Create API Key
3. Use their SMTP settings

### AWS SES
1. Verify domain in AWS SES
2. Create SMTP credentials
3. Use provided settings

## 🔍 Monitoring

### View Logs
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# View logs
railway logs
```

### In Dashboard
- Click service → "Logs" tab
- Real-time log streaming
- Search and filter capabilities

## 🚨 Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check DATABASE_URL is set
   - Ensure PostgreSQL service is running
   - Check logs for connection errors

2. **Port Binding Error**
   - Use `$PORT` environment variable
   - Don't hardcode port numbers

3. **Migration Issues**
   - Check if migrations run on deploy
   - Can run manually: `railway run alembic upgrade head`

4. **Memory Issues**
   - Adjust worker count in start command
   - Monitor memory usage in Railway dashboard

## 📊 Scaling

### Horizontal Scaling
1. Go to service Settings
2. Increase "Replicas" count
3. Railway handles load balancing

### Vertical Scaling
1. Go to Settings → Resources
2. Adjust CPU and Memory limits

## 💰 Cost Optimization

### Tips to Reduce Costs:
1. Use sleep/wake schedules for dev environments
2. Optimize Docker image size
3. Set resource limits appropriately
4. Use Railway's usage-based pricing

### Free Tier Includes:
- $5 monthly credit
- 500 GB-hours of compute
- 100 GB of bandwidth

## 🔐 Security on Railway

### Automatic Security Features:
- HTTPS/SSL certificates
- DDoS protection
- Isolated containers
- Encrypted secrets

### Additional Setup:
1. Enable 2FA on Railway account
2. Use environment-specific secrets
3. Set up proper CORS origins
4. Configure rate limiting

## 🎯 Production Checklist

- [ ] SECRET_KEY is strong and unique
- [ ] DEBUG is set to false
- [ ] Database has backups enabled
- [ ] Redis has persistence enabled
- [ ] CORS origins are properly configured
- [ ] Email service is configured
- [ ] Error tracking (Sentry) is set up
- [ ] Custom domain is configured (optional)
- [ ] Health checks are passing
- [ ] Logs are being monitored

## 📚 Useful Commands

```bash
# Railway CLI commands
railway login
railway link
railway logs
railway run <command>
railway variables
railway open

# Run migrations
railway run alembic upgrade head

# Create admin user
railway run python scripts/create_admin.py

# Database backup
railway run pg_dump $DATABASE_URL > backup.sql
```

## 🔗 Additional Resources

- [Railway Documentation](https://docs.railway.app)
- [Railway Templates](https://railway.app/templates)
- [Railway Discord](https://discord.gg/railway)

## 💡 Pro Tips

1. **Use Railway Templates**: Create a template from your deployed app for easy replication
2. **Environment Cloning**: Clone environments for staging/production separation
3. **Webhooks**: Set up deployment webhooks for CI/CD
4. **Monitoring**: Integrate with external monitoring services
5. **Cron Jobs**: Use Railway's cron job feature for scheduled tasks

---

Need help? Check the logs first, then reach out on Railway Discord or create an issue in the repository. 
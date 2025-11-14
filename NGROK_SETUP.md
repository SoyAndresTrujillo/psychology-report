# 🌐 ngrok Setup Guide - Publish Your Django App to Internet

This guide shows how to expose your local Docker-based Django application to the internet using ngrok.

---

## 📋 Prerequisites

- Docker and Docker Compose installed ✅
- Your Django app running locally ✅
- ngrok account (free tier works fine)

---

## Step 1: Install ngrok

### Windows

**Option A: Using Chocolatey**
```bash
choco install ngrok
```

**Option B: Manual Installation**
1. Download from https://ngrok.com/download
2. Extract `ngrok.exe` to a folder (e.g., `C:\ngrok\`)
3. Add to PATH or use full path when running

**Verify Installation**
```bash
ngrok version
# Should output: ngrok version 3.x.x
```

---

## Step 2: Create ngrok Account & Get Auth Token

1. **Sign up** (free): https://dashboard.ngrok.com/signup
2. **Get your auth token**: https://dashboard.ngrok.com/get-started/your-authtoken
3. **Configure ngrok** with your token:

```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN_HERE
```

This saves your token to `C:\Users\YOUR_USERNAME\.ngrok2\ngrok.yml`

---

## Step 3: Start Your Django Application

```bash
# Make sure containers are stopped
dcd

# Start your Docker containers
dcu

# Verify it's running
docker-compose -f docker-compose.dev.yml ps

# Should show:
# psychologist_postgres  Up (healthy)
# psychologist_web       Up
```

Test locally first:
- Visit http://localhost:8000
- Should see your Django app

---

## Step 4: Start ngrok Tunnel

Open a **new terminal** window and run:

```bash
# Basic tunnel (HTTP only)
ngrok http 8000

# Or with custom subdomain (requires paid plan)
ngrok http 8000 --subdomain=psychology-report

# Or with specific region (us, eu, ap, au, sa, jp, in)
ngrok http 8000 --region=us
```

**Expected Output:**
```
ngrok                                                                    

Session Status                online
Account                       Your Name (Plan: Free)
Version                       3.x.x
Region                        United States (us)
Latency                       -
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://abc123.ngrok-free.app -> http://localhost:8000

Connections                   ttl     opn     rt1     rt5     p50     p90
                              0       0       0.00    0.00    0.00    0.00
```

---

## Step 5: Access Your Application

### Public URL
Your app is now live at the URL shown in ngrok output:
```
https://abc123.ngrok-free.app
```

Share this URL with anyone!

### ngrok Dashboard
Monitor traffic in real-time:
```
http://127.0.0.1:4040
```

Features:
- View all HTTP requests
- Inspect request/response details
- Replay requests
- Monitor performance

---

## 🎯 Quick Command Reference

### Start Everything
```bash
# Terminal 1: Start Django
dcu && dcl

# Terminal 2: Start ngrok
ngrok http 8000
```

### Stop Everything
```bash
# Terminal 2: Stop ngrok (Ctrl+C)

# Terminal 1: Stop Docker
dcd
```

---

## 🔒 Security Considerations

### ⚠️ Important Notes

1. **Free Tier Limitations:**
   - Random subdomain each time (e.g., `abc123.ngrok-free.app`)
   - Warning page before accessing your site
   - Limited requests per minute
   - No custom domains

2. **DO NOT USE FOR PRODUCTION:**
   - ngrok is for testing, demos, and development
   - URLs change on restart (free tier)
   - No uptime guarantees

3. **Security Best Practices:**
   - Don't share sensitive data
   - Monitor the ngrok dashboard (http://127.0.0.1:4040)
   - Close ngrok when not in use
   - Consider IP whitelisting (paid feature)

### Recommended for:
✅ Demos and presentations  
✅ Testing with remote clients  
✅ Webhook testing  
✅ Mobile device testing  
✅ Sharing work with colleagues  

### NOT recommended for:
❌ Production hosting  
❌ Long-term deployments  
❌ Sensitive/private data  
❌ High-traffic applications  

---

## 🚀 Advanced Usage

### Custom Configuration

Create `ngrok.yml` configuration:

```yaml
authtoken: YOUR_AUTH_TOKEN
version: 2
tunnels:
  django-web:
    addr: 8000
    proto: http
    bind_tls: true
  django-api:
    addr: 8000
    proto: http
    subdomain: my-api  # Requires paid plan
```

Start with config:
```bash
ngrok start django-web
```

### Basic Authentication (Paid Feature)

Add basic auth to your tunnel:
```bash
ngrok http 8000 --auth="username:password"
```

### Custom Domain (Paid Feature)

Use your own domain:
```bash
ngrok http 8000 --hostname=app.yourdomain.com
```

### Inspect API

ngrok provides an API at http://localhost:4040/api/

```bash
# Get tunnel info
curl http://localhost:4040/api/tunnels

# Replay a request
curl -X POST http://localhost:4040/api/requests/http/REQUEST_ID/replay
```

---

## 🐛 Troubleshooting

### Issue: "ngrok command not found"

**Solution:**
```bash
# Windows: Add to PATH or use full path
C:\ngrok\ngrok.exe http 8000
```

### Issue: "Failed to complete tunnel connection"

**Solution:**
1. Check firewall settings
2. Verify port 8000 is not blocked
3. Try different region: `ngrok http 8000 --region=eu`

### Issue: Django shows "Invalid HTTP_HOST header"

**Solution:**
Already fixed in `settings.py`! The following is now in your settings:
```python
if DEBUG:
    ALLOWED_HOSTS += ['.ngrok-free.app', '.ngrok.io', '.ngrok.app']
```

If still having issues, manually add your ngrok domain:
```python
ALLOWED_HOSTS = ['your-url.ngrok-free.app', 'localhost', '127.0.0.1']
```

### Issue: "This site can't be reached"

**Solution:**
1. Verify Docker containers are running: `docker-compose -f docker-compose.dev.yml ps`
2. Test localhost first: http://localhost:8000
3. Check ngrok is running and showing "Forwarding" status
4. Try the HTTPS URL (not HTTP)

### Issue: Static files not loading

**Solution:**
```bash
# Collect static files
docker exec -it psychologist_web python manage.py collectstatic --noinput
```

Or update `settings.py`:
```python
# For development with ngrok
if DEBUG:
    STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
```

---

## 📊 Monitoring & Analytics

### ngrok Dashboard Features

Access at http://127.0.0.1:4040

1. **Request Inspector:**
   - View all HTTP requests in real-time
   - Inspect headers, body, query params
   - See response status and timing

2. **Replay Requests:**
   - Re-send any request with one click
   - Useful for testing

3. **Status:**
   - Connection health
   - Bandwidth usage
   - Request counts

---

## 💡 Pro Tips

1. **Use HTTPS URLs:**
   - ngrok provides HTTPS automatically
   - Always share `https://` URLs, not `http://`

2. **Keep Terminal Open:**
   - ngrok must stay running
   - If terminal closes, tunnel dies

3. **Save ngrok URL:**
   - Copy the URL immediately (it changes on restart)
   - Save in notepad for easy sharing

4. **Test Mobile Devices:**
   - Open ngrok URL on your phone
   - Perfect for responsive design testing

5. **Webhook Testing:**
   - Use ngrok URL for webhook callbacks
   - Monitor in dashboard (http://127.0.0.1:4040)

6. **Multiple Tunnels:**
   - Run multiple ngrok instances
   - Different ports for frontend/backend

---

## 🎓 Example Workflow

### Demo Presentation

```bash
# 1. Start your app
dcu

# 2. Wait for containers to be healthy
docker-compose -f docker-compose.dev.yml ps

# 3. Test locally
# Visit http://localhost:8000

# 4. Start ngrok in new terminal
ngrok http 8000

# 5. Copy the HTTPS URL
# https://abc123.ngrok-free.app

# 6. Share with audience!

# 7. Monitor traffic in dashboard
# http://127.0.0.1:4040

# 8. After demo, stop ngrok (Ctrl+C)
# Stop containers: dcd
```

---

## 📚 Additional Resources

- **ngrok Documentation**: https://ngrok.com/docs
- **ngrok Dashboard**: https://dashboard.ngrok.com
- **Django ALLOWED_HOSTS**: https://docs.djangoproject.com/en/5.1/ref/settings/#allowed-hosts
- **ngrok Pricing**: https://ngrok.com/pricing (free tier is fine for testing)

---

## 🆓 Free Tier Limits

- ✅ 1 online ngrok process
- ✅ 4 tunnels/ngrok process
- ✅ 40 connections/minute
- ✅ HTTPS support
- ✅ HTTP/TCP tunnels
- ❌ Custom subdomains
- ❌ Reserved domains
- ❌ IP whitelisting

For production, consider:
- **Paid ngrok** ($8-10/month)
- **Heroku** (easy Django deployment)
- **DigitalOcean App Platform**
- **AWS Elastic Beanstalk**
- **Railway.app** (free tier)

---

**Ready to go live? Start ngrok and share your Django app with the world! 🚀**

# MediLab Analytics - Deployment Guide

## Overview
This guide will help you deploy the MediLab Analytics application, a stunning web-based clinical report analysis platform with user authentication, timeline tracking, and AI-powered insights.

## Features
- **Modern Animated Frontend**: Beautiful UI with particles, animations, and glass-morphism design
- **User Authentication**: Secure login/registration system
- **Report Analysis**: Upload and analyze PDF clinical reports
- **Timeline Visualization**: Track health metrics over time
- **PDF Generation**: Generate professional reports for patients and doctors
- **Responsive Design**: Works perfectly on all devices

## Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Git (for deployment)
- Modern web browser

## Local Development Setup

### 1. Clone/Download the Application
```bash
# If you have the files locally, create a project directory
mkdir medilab-analytics
cd medilab-analytics
```

### 2. Set Up Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
# Install required packages
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_secret_key_for_sessions
FLASK_ENV=development
```

### 5. Run the Application
```bash
# Start the Flask backend
python api.py

# The API will run on http://localhost:5000
```

### 6. Access the Frontend
- Open `index.html` in your web browser
- Or serve it using a local HTTP server:
```bash
# Using Python
python -m http.server 8000

# Using Node.js
npx serve .
```

## Production Deployment Options

### Option 1: PythonAnywhere (Free & Easy)

1. **Sign up** at [pythonanywhere.com](https://www.pythonanywhere.com/)

2. **Upload Files**:
   - Upload all files to your PythonAnywhere account
   - Use the "Files" tab to upload:
     - `api.py`
     - `requirements.txt`
     - All HTML, CSS, JS files

3. **Configure Web App**:
   - Go to "Web" tab
   - Click "Add a new web app"
   - Choose "Flask" framework
   - Select Python 3.8+

4. **Update WSGI Configuration**:
   - Edit the WSGI configuration file:
   ```python
   import sys
   path = "/home/yourusername/medilab-analytics"
   if path not in sys.path:
       sys.path.append(path)
   
   from api import app as application
   ```

5. **Install Dependencies**:
   - Open a Bash console
   - Run: `pip install -r requirements.txt`

6. **Reload Web App**:
   - Click the green "Reload" button

### Option 2: Heroku (Free Tier)

1. **Install Heroku CLI**:
   ```bash
   # Download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Create Required Files**:
   Create `Procfile`:
   ```
   web: python api.py
   ```

3. **Deploy**:
   ```bash
   # Login to Heroku
   heroku login

   # Create new app
   heroku create your-app-name

   # Deploy
   git add .
   git commit -m "Initial deployment"
   git push heroku main
   ```

### Option 3: Railway (Free Tier)

1. **Sign up** at [railway.app](https://railway.app/)

2. **Connect GitHub Repository**:
   - Push your code to GitHub
   - Connect repository to Railway

3. **Configure Environment**:
   - Add environment variables in Railway dashboard
   - Set Python version

4. **Deploy**:
   - Railway automatically deploys on push

### Option 4: Netlify (Frontend Only)

For static frontend deployment:

1. **Sign up** at [netlify.com](https://www.netlify.com/)

2. **Deploy Options**:
   - Drag and drop the project folder
   - Connect to GitHub repository
   - Use Netlify CLI

3. **Configure**:
   - Set build command: (none needed)
   - Set publish directory: `./`

## API Integration

### Frontend API Configuration
Update the API endpoint in `main.js`:
```javascript
// Update this line with your deployed API URL
const API_BASE_URL = 'https://your-api-domain.com/api';
```

### Backend API Endpoints
- `POST /api/analyze` - Analyze uploaded PDF reports
- `POST /api/generate-pdf` - Generate PDF reports
- `GET /api/timeline` - Get user timeline data
- `POST /api/save-timeline` - Save timeline data
- `POST /api/users/register` - User registration
- `POST /api/users/login` - User login

## Database Setup

### SQLite (Default)
The application uses SQLite for user management and data storage:

```python
# Database schema will be created automatically
# Files created:
# - users.json (user accounts)
# - timeline_data.json (health timeline)
```

### Production Database
For production, consider using:
- PostgreSQL
- MySQL
- MongoDB

## Security Considerations

1. **Environment Variables**:
   - Never commit `.env` file
   - Use strong secret keys

2. **File Uploads**:
   - Validate file types
   - Limit file sizes
   - Scan for malware

3. **User Authentication**:
   - Use HTTPS in production
   - Implement rate limiting
   - Hash passwords properly

4. **API Security**:
   - Add authentication tokens
   - Implement CORS properly
   - Validate all inputs

## Performance Optimization

1. **Frontend**:
   - Minify CSS/JavaScript
   - Optimize images
   - Enable compression

2. **Backend**:
   - Use production WSGI server (Gunicorn)
   - Enable caching
   - Optimize database queries

3. **CDN** (Optional):
   - Use CDN for static assets
   - Consider Cloudflare

## Monitoring & Maintenance

1. **Logging**:
   - Set up error logging
   - Monitor application performance

2. **Backups**:
   - Regular database backups
   - File storage backups

3. **Updates**:
   - Keep dependencies updated
   - Monitor security advisories

## Troubleshooting

### Common Issues

1. **Port Already in Use**:
   ```bash
   # Kill process using port 5000
   lsof -ti:5000 | xargs kill -9
   ```

2. **CORS Issues**:
   - Ensure CORS is properly configured
   - Check API endpoint URLs

3. **File Upload Errors**:
   - Check file permissions
   - Verify upload directory exists

4. **Database Connection**:
   - Ensure database files are writable
   - Check disk space

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review application logs
3. Test with minimal configuration
4. Check dependencies compatibility

## Next Steps

1. **Customize** the application for your needs
2. **Add** more biomarker types
3. **Integrate** with real medical databases
4. **Implement** advanced AI features
5. **Add** mobile app support

---

**Happy Deploying!** 🚀

For the most up-to-date deployment instructions, check the project repository or contact support.
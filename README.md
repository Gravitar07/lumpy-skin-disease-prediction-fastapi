# Lumpy Skin Disease Prediction System

A web-based application built with FastAPI that uses machine learning to predict Lumpy Skin Disease in cattle through image analysis and clinical data. The system combines both image-based detection and clinical data analysis to provide comprehensive diagnostic reports in multiple languages.

## Features

- Dual-model prediction system:
  - Image analysis using CNN (MobileNetV2)
  - Clinical data analysis using Random Forest
- Multi-language diagnostic reports
- Real-time weather data integration
- Secure user authentication
- Interactive dashboard
- Responsive web interface

## Prerequisites

- Python 3.10
- pip (Python package installer)
- Virtual environment (recommended)

## Installation

1. **Extract the ZIP file:**
   ```bash
   unzip lumpy-skin-disease-prediction.zip
   cd lumpy-skin-disease-prediction
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Linux/Mac
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Setup:**
   Create a `.env` file in the root directory:
   ```
   SECRET_KEY=your_secret_key_here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES="30"
   WEATHER_API_KEY=your_weather_api_key
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
   You can get generate the SECRET_KEY using the following python code and copy/paste in the .env file:
   ```python
   import os
   import base64
   secret_key = base64.b64encode(os.urandom(32)).decode('utf-8')
   print(f"Generated SECRET_KEY: {secret_key}")
   ```
   You can get the Gemini API Key from the following link:
   https://aistudio.google.com/app/apikey


## Running the Application

1. **Start the server:**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
   or
   ```bash
   python run.py
   ```

2. **Access the application:**
   - Web Interface: `http://localhost:8000`
   - API Documentation: `http://localhost:8000/docs`

## Project Structure
```
lumpy-skin-disease-prediction/
├── app/
│   ├── __init__.py
│   ├── auth.py          # Authentication and authorization
│   ├── config.py        # Configuration settings
│   ├── database.py      # Database connection and definitions
│   ├── llm.py          # Language model for report generation
│   ├── logger.py        # Logging configuration
│   ├── main.py         # FastAPI application entry point
│   ├── models.py        # SQLAlchemy database models
│   ├── prediction.py    # ML model prediction logic
│   ├── utils.py         # Utility functions
│   └── weather.py       # Weather API integration
│
├── final_models/        # Machine Learning Models
│   ├── mobilenet_lumpy_skin_model.h5
│   ├── randomforest_best_model.pkl
│   └── scaler_object.joblib
│
├── static/             # Static Files
│   ├── css/
│   │   └── style.css   # Custom CSS styles
│   └── js/
│       ├── location.js           # Location and weather handling
│       └── markdown-converter.js  # Markdown parsing utilities
│
├── templates/          # HTML Templates
│   ├── base.html      # Base template with common elements
│   ├── dashboard.html  # User dashboard template
│   ├── index.html     # Home page template
│   ├── login.html     # Login page template
│   └── signup.html    # Registration page template
│
├── .env               # Environment variables
├── requirements.txt   # Python dependencies
└── run.py            # Application runner script
```


## Using the System

1. **Login/Registration:**
   - Create a new account or login with existing credentials
   - System uses JWT tokens for secure authentication

2. **Making Predictions:**
   - Upload a clear image of the cattle skin
   - Enter clinical data and weather parameters
   - Select preferred language for the report
   - Submit for analysis

3. **Viewing Results:**
   - Get immediate prediction results
   - View detailed diagnostic reports
   - Access historical predictions in the dashboard

4. **Dashboard Features:**
   - View prediction history
   - Track local disease statistics

## Important Notes

- Ensure all ML model files are present in the `app/models/` directory
- Required model files:
  - `mobilenet_lumpy_skin_model.h5`
  - `randomforest_best_model.pkl`
  - `scaler_object.joblib`
- Internet connection required for weather data
- Recommended image specifications:
  - Format: JPG, JPEG, PNG
  - Clear focus on affected area

## Troubleshooting

If you encounter any issues:

1. **Application won't start:**
   - Verify Python version (3.10)
   - Check if all dependencies are installed
   - Ensure environment variables are set correctly

2. **Prediction errors:**
   - Verify model files are in correct location
   - Check image format and quality
   - Ensure all clinical data fields are properly filled

3. **Weather data issues:**
   - Verify internet connection
   - Check weather API key in .env file

4. **Page keeps loading on startup:**
   - Clear the Cookies and Site Data
   - Clear cache memory
   - Restart the server


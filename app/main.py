from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile, Form, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import json
from typing import Optional
from fastapi.responses import RedirectResponse
from jose import jwt
from PIL import Image
from io import BytesIO

from .database import engine, get_db, Base, SessionLocal
from .models import User
from .auth import (
    authenticate_user, create_access_token, get_current_user,
    create_user, UserCreate, Token, ACCESS_TOKEN_EXPIRE_MINUTES, get_user
)
from .prediction import (
    make_prediction, get_user_predictions,
    get_city_disease_count
)
from datetime import timedelta
from .config import SECRET_KEY, ALGORITHM, WEATHER_API_KEY
from app.logger import logger

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Lumpy Skin Disease Prediction")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Authentication routes
@app.post("/api/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/signup")
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    db_email = db.query(User).filter(User.email == user.email).first()
    if db_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    return create_user(db=db, user=user)

# Prediction routes
@app.post("/api/predict")
async def create_prediction(
    image: UploadFile = File(...),
    clinical_data: str = Form(...),
    language: str = Form("English"),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Process uploaded image in memory without saving to disk
    image_data = image.file.read()
    
    # Create a PIL Image from the bytes data
    image_obj = Image.open(BytesIO(image_data))
    
    # Parse clinical data
    clinical_features = json.loads(clinical_data)
    
    # Log the parsed clinical data
    logger.debug(f"Parsed clinical data: {clinical_features}")

    # Make prediction with image object
    prediction = make_prediction(
        db=db,
        user_id=current_user.id,
        image=image_obj,  # Pass image object directly
        clinical_data=clinical_features,
        latitude=latitude,
        longitude=longitude,
        language=language
    )
    
    # Log the prediction result
    logger.info(f"Prediction result: {prediction}")
    
    return {
        "id": prediction.id,
        "image_result": prediction.image_model_result,
        "clinical_result": prediction.clinical_model_result,
        "city": prediction.city,
        "temperature": prediction.temperature,
        "language": prediction.language,
        "report": prediction.report
    }

@app.get("/api/user/predictions")
async def user_predictions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    predictions = get_user_predictions(db, current_user.id)
    return predictions

@app.get("/api/city/disease-stats")
async def city_disease_stats(city: str, db: Session = Depends(get_db)):
    count = get_city_disease_count(db, city)
    return {"city": city, "disease_count": count}

# Page routes
@app.get("/")
async def get_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/signup")
async def get_signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.get("/home")
async def get_home_page(request: Request):
    # Get token from request cookies or headers
    token = request.cookies.get("access_token") or request.headers.get("Authorization")
    
    if not token:
        # If no token, redirect to login page
        return RedirectResponse(url="/", status_code=303)
    
    try:
        # Try to get the current user
        if token and token.startswith("Bearer "):
            token = token.replace("Bearer ", "")
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        
        if not username:
            return RedirectResponse(url="/", status_code=303)
            
        db = SessionLocal()
        user = get_user(db, username)
        db.close()
        
        if not user:
            return RedirectResponse(url="/", status_code=303)
            
        # If authentication successful, render the page with the API key
        return templates.TemplateResponse("index.html", {
            "request": request, 
            "user": user,
            "weather_api_key": WEATHER_API_KEY
        })
    except:
        # If authentication fails, redirect to login page
        return RedirectResponse(url="/", status_code=303)

@app.get("/dashboard")
async def get_dashboard_page(request: Request):
    # Get token from request cookies or headers
    token = request.cookies.get("access_token") or request.headers.get("Authorization")
    
    if not token:
        # If no token, redirect to login page
        return RedirectResponse(url="/", status_code=303)
    
    try:
        # Try to get the current user
        if token and token.startswith("Bearer "):
            token = token.replace("Bearer ", "")
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        
        if not username:
            return RedirectResponse(url="/", status_code=303)
            
        db = SessionLocal()
        user = get_user(db, username)
        
        # Get predictions for the user
        predictions = get_user_predictions(db, user.id)
        
        # Get city data for the first prediction that has city info
        city = None
        city_stats = None
        for p in predictions:
            if p.city:
                city = p.city
                city_stats = get_city_disease_count(db, city)
                break
        
        db.close()
        
        # If authentication successful, render the page with API key
        return templates.TemplateResponse(
            "dashboard.html", 
            {
                "request": request, 
                "user": user, 
                "predictions": predictions, 
                "city": city, 
                "city_stats": city_stats,
                "weather_api_key": WEATHER_API_KEY
            }
        )
    except:
        # If authentication fails, redirect to login page
        return RedirectResponse(url="/", status_code=303)


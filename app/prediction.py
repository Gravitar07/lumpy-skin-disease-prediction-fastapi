import os
import joblib
import numpy as np
import tensorflow as tf
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import json
from PIL import Image
from io import BytesIO
from app.logger import logger
from .models import Prediction, DiseaseStats
from .weather import get_temperature_by_coords, get_city_by_coords
from .llm import LLM
from .config import MODELS_DIR

# Custom exceptions
class ModelLoadingError(Exception):
    pass

class PreprocessingError(Exception):
    pass

class PredictionError(Exception):
    pass

# Data preprocessing class
class DataPreprocessor:
    """Handles data preprocessing for the ML model input."""
    def __init__(self):
        try:
            logger.info("Initializing DataPreprocessor")
            self.scaler = joblib.load(f"{MODELS_DIR}/scaler_object.joblib")
            logger.info("Scaler loaded successfully")
        except Exception as e:
            logger.error("Failed to load scaler", exc_info=True)
            raise ModelLoadingError("Could not load the scaler for data preprocessing.")

    def preprocess(self, input_data):
        """Preprocess input data using the loaded scaler."""
        try:
            logger.info(f"Preprocessing input data: {input_data}")
            scaled_data = self.scaler.transform(np.array(input_data).reshape(1, -1))
            return scaled_data
        except Exception as e:
            logger.error("Error in data preprocessing", exc_info=True)
            raise PreprocessingError("Preprocessing failed. Ensure input data format is correct.")

# ML model predictor
class ML_Model_Predictor:
    """Handles predictions using the Random Forest model."""
    def __init__(self):
        try:
            self.model_path = f"{MODELS_DIR}/randomforest_best_model.pkl"
            logger.info(f"Loading ML model from: {self.model_path}")
            
            if not os.path.exists(self.model_path):
                logger.error(f"ML model file not found at {self.model_path}")
                raise ModelLoadingError("ML model file not found")
                
            self.model = joblib.load(self.model_path)
            logger.info("ML model loaded successfully")
        except Exception as e:
            logger.error("Failed to load ML model", exc_info=True)
            raise ModelLoadingError("Could not load ML model")

    def predict(self, preprocessed_data):
        """Make predictions using the loaded ML model."""
        try:
            prediction = self.model.predict(preprocessed_data)
            result = prediction[0]
            logger.info(f"ML Model prediction: {'Lumpy' if result == 1 else 'Not Lumpy'}")
            return result
        except Exception as e:
            logger.error("Error during ML prediction", exc_info=True)
            raise PredictionError("ML prediction failed")

# CNN model predictor
class CNN_Model_Predictor:
    """Handles predictions using the CNN model."""
    def __init__(self):
        try:
            self.model_path = f"{MODELS_DIR}/mobilenet_lumpy_skin_model.h5"
            logger.info(f"Loading CNN model from: {self.model_path}")
            
            if not os.path.exists(self.model_path):
                logger.error(f"CNN model file not found at {self.model_path}")
                raise ModelLoadingError("CNN model file not found")
                
            self.model = tf.keras.models.load_model(self.model_path)
            logger.info("CNN model loaded successfully")
        except Exception as e:
            logger.error("Failed to load CNN model", exc_info=True)
            raise ModelLoadingError("Could not load CNN model")

    def predict(self, image):
        """Make predictions using the loaded CNN model."""
        try:
            # Preprocess image for model input
            image = image.resize((224, 224))
            image_array = np.array(image) / 255.0
            image_array = np.expand_dims(image_array, axis=0)
            image_array = tf.keras.applications.mobilenet_v2.preprocess_input(image_array)
            
            # Make prediction
            prediction = self.model.predict(image_array)
            result = np.argmax(prediction, axis=1)[0]
            logger.info(f"CNN Model prediction: {'Lumpy' if result == 0 else 'Not Lumpy'}")
            return result
        
        except Exception as e:
            logger.error("Error during CNN prediction", exc_info=True)
            raise PredictionError("CNN prediction failed")

# Global variables to store model instances
_preprocessor = None
_ml_predictor = None
_cnn_predictor = None
_llm = None

def initialize_models():
    """Initialize and load all models once during application startup"""
    global _preprocessor, _ml_predictor, _cnn_predictor, _llm
    
    try:
        logger.info("Initializing models on application startup")
        _preprocessor = DataPreprocessor()
        _ml_predictor = ML_Model_Predictor()
        _cnn_predictor = CNN_Model_Predictor()
        _llm = LLM()
        logger.info("All models loaded successfully")
    except Exception as e:
        logger.error("Failed to load models on startup", exc_info=True)
        raise ModelLoadingError(f"Could not load models during initialization: {str(e)}")
    
def clear_models():
    """Clear the models from memory"""
    global _preprocessor, _ml_predictor, _cnn_predictor
    _preprocessor = None
    _ml_predictor = None
    _cnn_predictor = None
    _llm = None

def get_models():
    """Get the initialized models"""
    global _preprocessor, _ml_predictor, _cnn_predictor, _llm
    
    if _preprocessor is None or _ml_predictor is None or _cnn_predictor is None or _llm is None:
        # If models aren't initialized yet, initialize them
        initialize_models()
    return _preprocessor, _ml_predictor, _cnn_predictor, _llm

def make_prediction(
    db: Session,
    user_id: int,
    image: Image.Image,  # Image object for in-memory processing
    clinical_data: Dict[str, Any],
    latitude: float = None,
    longitude: float = None,
    language: str = "English"
) -> Prediction:
    try:
        # Get the already initialized models
        preprocessor, ml_predictor, cnn_predictor, llm = get_models()
        
        # Get location data if coordinates provided
        city = None
        temperature = None
        
        if latitude and longitude:
            city = get_city_by_coords(latitude, longitude)
            temperature = get_temperature_by_coords(latitude, longitude)
        
        # Prepare structured data input for ML model (extract from clinical_data dict)
        structured_data = [
            clinical_data.get('longitude', longitude),
            clinical_data.get('latitude', latitude),
            clinical_data.get('cloud_cover'),
            clinical_data.get('evapotranspiration'),
            clinical_data.get('precipitation'),
            clinical_data.get('min_temp'),
            clinical_data.get('mean_temp'),
            clinical_data.get('max_temp'),
            clinical_data.get('vapour_pressure'),
            clinical_data.get('wet_day_freq')
        ]
        
        # Preprocess data
        preprocessed_data = preprocessor.preprocess(structured_data)
        
        # Get predictions from ML and CNN models
        ml_prediction = ml_predictor.predict(preprocessed_data)
        cnn_prediction = cnn_predictor.predict(image)  # Process image in memory
        
        # Log the final predictions
        logger.info(f"Final ML prediction (clinical model): {ml_prediction} - {'Affected' if ml_prediction == 1 else 'Not Affected'}")
        logger.info(f"Final CNN prediction (image model): {cnn_prediction} - {'Affected' if cnn_prediction == 0 else 'Not Affected'}")
        
        # Format result string (similar to your original approach)
        result = f"""
        Lumpy Skin Disease Diagnostic Report:
        
        **ML Model Prediction:** {'Lumpy' if ml_prediction == 1 else 'Not Lumpy'}
        **CNN Model Prediction:** {'Lumpy' if cnn_prediction == 0 else 'Not Lumpy'}
        
        **Input Data:**
        - Longitude: {clinical_data.get('longitude', longitude)}
        - Latitude: {clinical_data.get('latitude', latitude)}
        - Monthly Cloud Cover: {clinical_data.get('cloud_cover')}
        - Potential EvapoTranspiration: {clinical_data.get('evapotranspiration')}
        - Precipitation: {clinical_data.get('precipitation')}
        - Minimum Temperature: {clinical_data.get('min_temp')}
        - Mean Temperature: {clinical_data.get('mean_temp')}
        - Maximum Temperature: {clinical_data.get('max_temp')}
        - Vapour Pressure: {clinical_data.get('vapour_pressure')}
        - Wet Day Frequency: {clinical_data.get('wet_day_freq')}
        """
        
        # Generate LLM report using the LLM class
        report = llm.inference(image=image, result=result, language=language, temperature=temperature, city=city)
        
        # Create prediction record WITHOUT storing any image data
        prediction = Prediction(
            user_id=user_id,
            image_path=None,  # No image path stored
            clinical_features=clinical_data,
            image_model_result=bool(cnn_prediction == 0),
            clinical_model_result=bool(ml_prediction == 1),
            latitude=latitude,
            longitude=longitude,
            city=city,
            temperature=temperature,
            language=language,
            report=report
        )
        
        db.add(prediction)
        db.commit()
        db.refresh(prediction)
        
        # Update disease stats if disease detected
        if ml_prediction == 1 or cnn_prediction == 0:
            update_disease_stats(db, city)
        
        return prediction
        
    except Exception as e:
        logger.error("Error in prediction function", exc_info=True)
        db.rollback()
        raise PredictionError(f"Prediction function encountered an error: {str(e)}")

def update_disease_stats(db: Session, city: str):
    """Update disease stats for the given city"""
    if not city:
        return
        
    stats = db.query(DiseaseStats).filter(DiseaseStats.city == city).first()
    
    if stats:
        stats.disease_count += 1
    else:
        stats = DiseaseStats(city=city, disease_count=1)
        db.add(stats)
    
    db.commit()

def get_user_predictions(db: Session, user_id: int) -> List[Prediction]:
    """Get all predictions for a user"""
    return db.query(Prediction).filter(Prediction.user_id == user_id).order_by(Prediction.created_at.desc()).all()

def get_city_disease_count(db: Session, city: str) -> int:
    """Get disease count for a city"""
    stats = db.query(DiseaseStats).filter(DiseaseStats.city == city).first()
    return stats.disease_count if stats else 0
import datetime
import pytz
from sqlalchemy.orm import Session
from .models import Prediction
from .logger import logger

def convert_timestamps_to_ist(db: Session):
    """
    Convert all existing prediction timestamps to IST.
    This should be run once after deploying the updated code.
    """
    try:
        # Get all predictions
        predictions = db.query(Prediction).all()
        
        # Set up IST timezone
        ist_timezone = pytz.timezone('Asia/Kolkata')
        
        # Convert each timestamp
        conversion_count = 0
        for prediction in predictions:
            if prediction.created_at:
                # Assume current timestamps are in UTC
                utc_time = prediction.created_at.replace(tzinfo=pytz.UTC)
                # Convert to IST
                ist_time = utc_time.astimezone(ist_timezone)
                # Strip timezone for storage
                prediction.created_at = ist_time.replace(tzinfo=None)
                conversion_count += 1
        
        # Commit the changes
        db.commit()
        logger.info(f"Successfully converted {conversion_count} timestamps to IST")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to convert timestamps to IST: {str(e)}", exc_info=True)
        return False 
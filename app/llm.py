import google.generativeai as genai
from typing import Dict, Any, Optional
import os
from .config import GEMINI_API_KEY, GEMINI_MODEL_NAME
from PIL import Image
from io import BytesIO
from app.logger import logger

# Configure Gemini API with key from config
genai.configure(api_key=GEMINI_API_KEY)

class LLM:
    """Handles interaction with Google's Gemini LLM for report generation."""
    
    def __init__(self):
        """Initialize the LLM model."""
        try:
            self.model = genai.GenerativeModel(GEMINI_MODEL_NAME)
            logger.info("Gemini LLM model initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize LLM model", exc_info=True)
            raise Exception("Error initializing LLM model. Check API key and model name.")

    def prompt_template(self, result, language="English", temperature=None, city=None):
        """
        Generate a structured prompt for the LLM.
        Expected output should be around 600 words with detailed analysis.
        """
        temp_info = f"{temperature}°C" if temperature is not None else "not available"
        location_info = city if city else "not specified"
        
        prompt = f"""You are a veterinary expert specializing in Lumpy Skin Disease and cattle health. Based on the provided data, generate a comprehensive report (approximately 600 words) covering these sections:

1. Prediction Summary (50-75 words):
   - State the ML and CNN model predictions clearly
   - Confidence level assessment
   - Initial risk evaluation based on location and climate

2. Clinical Observations (100-125 words):
   - Detailed analysis of visible symptoms or their absence
   - Skin condition assessment
   - General health indicators
   - Body condition scoring (if visible)
   - Any secondary symptoms or complications

3. Environmental Risk Analysis (100-125 words):
   - Location: {location_info}
   - Current Temperature: {temp_info}
   - Vector activity potential
   - Seasonal disease patterns in this region
   - Climate-related stress factors
   - Local disease prevalence history

4. Differential Diagnosis (100-125 words):
   - Other possible conditions with similar presentations
   - Common cattle diseases in {location_info}
   - Season-specific health concerns
   - Age and breed-specific considerations
   - Stress-related conditions

5. Management Recommendations (150-175 words):
   A. Immediate Actions:
      - Isolation requirements (if any)
      - Monitoring parameters
      - Essential treatments
   
   B. Preventive Measures:
      - Vector control strategies
      - Environmental modifications
      - Vaccination schedules
      - Nutritional adjustments
   
   C. Long-term Management:
      - Herd health monitoring
      - Biosecurity measures
      - Record-keeping recommendations

6. Follow-up Protocol (50-75 words):
   - Monitoring timeline
   - Warning signs to watch for
   - When to seek veterinary consultation
   - Documentation requirements

Input Data:
{result}

IMPORTANT GUIDELINES:
1. Provide the report in {language} language
2. Maintain all six sections with their exact headings and don't mention no.of words in the headings or in the report
3. Include specific numbers, measurements, and timelines where applicable
4. Consider both individual animal and herd-level implications
5. Incorporate local weather patterns and regional disease prevalence
6. Provide actionable, practical recommendations
7. Use bullet points for clarity where appropriate
8. Include cost-effective solutions suitable for the region
9. Consider local veterinary resource availability
10. Address both immediate and long-term management strategies
11. Do not add any additional sections or explanatory text like "Here is the report in {language} language" or anything like that.
12. Provide the report in markdown format

Format each section clearly with headers and subheaders for easy reading. Use bullet points for lists and recommendations. Highlight critical information using bold text (**important text**)."""

        return prompt

    def inference(self, image: Any, result: str, language: str = "English", 
                 temperature: Optional[float] = None, 
                 city: Optional[str] = None) -> str:
        """
        Generate a report using the LLM model.
        
        Args:
            image: Image input (can be path, PIL Image, or bytes)
            result: Analysis results and clinical data
            language: Target language for the report
            temperature: Local temperature in Celsius
            city: Location of the case
        """
        try:
            # Generate prompt using template
            refined_prompt = self.prompt_template(result, language, temperature, city)
            logger.info("Generated LLM prompt template")
            
            # Process image input
            try:
                if isinstance(image, str) and os.path.exists(image):
                    image_obj = Image.open(image)
                elif isinstance(image, Image.Image):
                    image_obj = image
                elif isinstance(image, (bytes, BytesIO)):
                    image_obj = Image.open(image if isinstance(image, BytesIO) else BytesIO(image))
                else:
                    logger.warning("No valid image provided for LLM analysis")
                    image_obj = None
                
                # Prepare prompt with or without image
                prompt = [{'role': 'user', 'parts': [image_obj, refined_prompt] if image_obj else [refined_prompt]}]
                
            except Exception as e:
                logger.error("Error processing image for LLM", exc_info=True)
                prompt = [{'role': 'user', 'parts': [refined_prompt]}]
            
            # Generate response
            logger.info("Sending request to Gemini LLM")
            response = self.model.generate_content(prompt)
            
            if response.text:
                llm_response = response.text
                llm_response = llm_response.replace("```markdown", "").replace("```", "")
                logger.info("Successfully generated LLM report")
                return llm_response
            else:
                logger.error("LLM returned empty response")
                raise Exception("LLM response is empty")

        except Exception as e:
            logger.error("Error during LLM inference", exc_info=True)
            raise Exception(f"Error during LLM inference: {str(e)}")

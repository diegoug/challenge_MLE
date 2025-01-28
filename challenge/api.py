import fastapi
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, validator
import pandas as pd
from challenge.model import DelayModel

app = fastapi.FastAPI()

# Define the request model
class FlightData(BaseModel):
    OPERA: str
    TIPOVUELO: str
    MES: int

    @validator('TIPOVUELO')
    def validate_tipovuelo(cls, v):
        if v not in ['I', 'N']:
            raise ValueError('TIPOVUELO must be "I" or "N"')
        return v

    @validator('MES')
    def validate_mes(cls, v):
        if not 1 <= v <= 12:
            raise ValueError('MES must be between 1 and 12')
        return v

# Initialize the model
model = DelayModel()
# Load and preprocess the training data to fit the model
# This is a placeholder, replace with actual data loading
#df = pd.read_csv("/app/data/data.csv")
#X, y = model.preprocess(df, target_column="delay")
#model.fit(X, y)

@app.get("/health", status_code=200)
async def get_health() -> dict:
    return {
        "status": "OK"
    }

@app.post("/predict", status_code=200)
async def post_predict(request: Request) -> dict:
    # Parse the incoming JSON data
    try:
        body = await request.json()
        flights = body.get("flights", [])
        if not isinstance(flights, list):
            raise ValueError("The 'flights' field must be a list.")
        data = pd.DataFrame([FlightData(**flight).dict() for flight in flights])
    except Exception as e:
        print("Error parsing request data:", str(e))
        raise HTTPException(status_code=400, detail=f"Request parsing error: {str(e)}")
    
    # Preprocess the data
    try:
        print("Preprocessing data:", data)  # Log the input data
        features = model.preprocess(data)
    except Exception as e:
        print("Error during preprocessing:", str(e))  # Log the error
        raise HTTPException(status_code=400, detail=f"Preprocessing error: {str(e)}")
    
    # Predict using the model
    try:
        predictions = model.predict(features)
        print("Predictions:", predictions)  # Log the predictions
    except Exception as e:
        print("Error during prediction:", str(e))  # Log the error
        raise HTTPException(status_code=400, detail=f"Prediction error: {str(e)}")
    
    # Log the response before returning
    response = {"predict": predictions}
    print("Response:", response)
    
    return response  # Ensure predictions are serializable

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.errors()},
    )
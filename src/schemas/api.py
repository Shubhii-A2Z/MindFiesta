from datetime import datetime
from pydantic import BaseModel

class HealthResponse(BaseModel):
    status: str="ok"
    timestamp: datetime=datetime.now()
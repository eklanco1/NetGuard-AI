
from fastapi import FastAPI
from pydantic import BaseModel, Field

from fastapi.middleware.cors import CORSMiddleware



# Uvoz AI rutera
from pipeline.predict_api import router as predict_router
from pipeline.batch_predict_api import router as batch_router
from pipeline.chat_api import router as chat_router


app = FastAPI(
    title="NetGuard AI API",
    description="Backend for network attack detection",
    version="1.0.0"
)


# Omogucavanje komunikacije s React frontendom
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


app.include_router(chat_router, prefix="/api/v1")

# Povezivanje AI modela s FastAPI aplikacijom
app.include_router(
    predict_router,
    prefix="/api/v1",
    tags=["AI Predictions"]
)


# Povezivanje batch analize s FastAPI aplikacijom
app.include_router(
    batch_router,
    prefix="/api/v1",
    tags=["Batch Predictions"]
)



# Provjera rada backenda
@app.get("/api/v1/health")
def health_check():
    return {
        "status": "ok",
        "message": "NetGuard AI backend is running"
    }


# Model za jednostavnu analizu saobracaja
class NetworkTraffic(BaseModel):
    source_ip: str
    destination_ip: str
    protocol: str
    packets: int = Field(ge=0)
    duration: float = Field(gt=0)


# Analiza saobracaja pomocu pravila
@app.post("/api/v1/traffic/analyze")
def analyze_traffic(traffic: NetworkTraffic):

    packets_per_second = traffic.packets / traffic.duration

    suspicious = packets_per_second > 100

    return {
        "source_ip": traffic.source_ip,
        "protocol": traffic.protocol,
        "packets_per_second": round(packets_per_second, 2),
        "requires_review": suspicious
    }

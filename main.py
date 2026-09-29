import io
import time
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image

app = FastAPI(title="ФАЛЬКОН ReID API", version="1.0.0")

# Разрешаем CORS для локальной разработки фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/health")
async def health_check():
    """Проверка доступности инференс-сервиса фронтендом."""
    return {"status": "ok", "engine": "PyTorch + FAISS", "dimension": 512}


@app.post("/api/v1/search")
async def search(
        file: UploadFile = File(...),
        x: int = Form(...),
        y: int = Form(...),
        w: int = Form(...),
        h: int = Form(...),
        threshold: float = Form(0.72),
        top_k: int = Form(10)
):
    t0 = time.time()

    # 1. Чтение кадра и кроп по BBox
    contents = await file.read()
    image = Image.open(io.BytesIO(contents)).convert("RGB")
    crop = image.crop((x, y, x + w, y + h))

    # 2. МЕСТО ДЛЯ ML-МОДЕЛИ КОМАНДЫ:
    # embedding = model.extract_features(crop)
    # scores, indices = faiss_index.search(embedding, top_k)

    # 3. Формирование ответа
    # Если лучший скор < threshold -> status = "refusal", candidates = []
    # Иначе -> status = "matched", candidates = [...]

    latency_ms = round((time.time() - t0) * 1000, 2)
    return JSONResponse({
        "status": "matched",
        "threshold": threshold,
        "best_score": 0.884,
        "latency_ms": latency_ms,
        "candidates": [
            {
                "rank": i + 1,
                "vehicle_id": f"veh_test_{1000 + i}",
                "camera_id": f"CAM_MKAD_{101 + i}",
                "score": round(0.884 - i * 0.04, 4),
                "timestamp": "14:30:00",
                "image_url": "data:image/svg+xml;utf8,...",
                "heatmap_url": "data:image/svg+xml;utf8,..."
            } for i in range(top_k)
        ]
    })
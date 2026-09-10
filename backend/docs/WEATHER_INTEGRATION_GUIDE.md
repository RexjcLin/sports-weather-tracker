# 🌤️ 中央氣象局 API 集成指南

本文檔提供詳細的集成步驟、API 使用示例和最佳實踐。

---

## 📋 目錄

1. [快速開始](#快速開始)
2. [環境配置](#環境配置)
3. [API 端點使用](#api-端點使用)
4. [天氣建議系統](#天氣建議系統)
5. [定時任務](#定時任務)
6. [測試和調試](#測試和調試)
7. [常見問題](#常見問題)

---

## 🚀 快速開始

### 1. 申請中央氣象局 API Key

1. 訪問 [中央氣象局開放資料平台](https://opendata.cwa.gov.tw/index)
2. 點擊「會員中心」→「API 申請」
3. 填寫應用資訊並提交申請
4. 審核通過後會收到 **API Key**

### 2. 環境配置

在 `.env` 文件中添加：

```env
# 中央氣象局配置
CWB_API_KEY=your_api_key_here

# 數據庫配置
DATABASE_URL=postgresql+asyncpg://user:password@localhost/sports_weather_db

# 應用配置
DEBUG=True
LOG_LEVEL=INFO
```

### 3. 安裝依賴

```bash
pip install -r requirements.txt
```

關鍵依賴：
- `aiohttp` - 異步 HTTP 請求
- `sqlalchemy[asyncio]` - 異步 ORM
- `apscheduler` - 定時任務調度
- `fastapi` - Web 框架
- `pydantic` - 數據驗證

### 4. 初始化數據庫

```bash
# 使用 Alembic 進行遷移
alembic upgrade head

# 或者直接創建表
python -m app.models --create-all
```

### 5. 啟動應用

```bash
# 開發環境
uvicorn app.main:app --reload

# 生產環境
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

---

## ⚙️ 環境配置

### 配置文件結構

```
backend/
├── .env                 # 環境變數
├── .env.example        # 環境變數示例
├── app/
│   ├── config.py       # 配置管理
│   ├── models.py       # 數據模型
│   ├── database.py     # 數據庫連接
│   ├── main.py         # 應用入口
│   ├── services/
│   │   ├── weather_service.py      # 天氣服務
│   │   └── recommendation_engine.py # 建議引擎
│   ├── api/v1/
│   │   └── weather.py  # API 路由
│   ├── tasks/
│   │   └── scheduler.py # 定時任務
│   └── schemas/
│       └── weather.py   # 數據 Schema
```

### 配置示例 (config.py)

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 中央氣象局
    CWB_API_KEY: str
    
    # 數據庫
    DATABASE_URL: str = "postgresql+asyncpg://localhost/sports_weather"
    
    # 日誌
    LOG_LEVEL: str = "INFO"
    
    # 應用
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"

settings = Settings()
```

---

## 📡 API 端點使用

### 1. 獲取即時天氣

#### 請求
```bash
GET /api/v1/weather/current/台北市
```

#### 響應
```json
{
  "id": 1,
  "location_name": "台北市",
  "latitude": 25.0330,
  "longitude": 121.5653,
  "temperature": 28.5,
  "humidity": 75,
  "wind_speed": 3.2,
  "pressure": 1013,
  "visibility": 10000,
  "weather_main": "Partly Cloudy",
  "weather_description": "多雲",
  "data_time": "2024-09-10T12:00:00",
  "fetched_at": "2024-09-10T12:05:00"
}
```

#### Python 示例
```python
import httpx
import asyncio

async def get_weather():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8000/api/v1/weather/current/台北市"
        )
        weather = response.json()
        print(f"溫度: {weather['temperature']}°C")
        print(f"濕度: {weather['humidity']}%")
```

### 2. 獲取天氣預報

#### 請求
```bash
GET /api/v1/weather/forecast/台北市?days=7
```

#### 響應
```json
[
  {
    "id": 1,
    "location_name": "台北市",
    "latitude": 25.0330,
    "longitude": 121.5653,
    "forecast_time": "2024-09-11T12:00:00",
    "temperature_max": 32.0,
    "temperature_min": 26.0,
    "precipitation_probability": 40,
    "weather_main": "Partly Cloudy",
    "weather_description": "多雲時晴",
    "forecast_issued_at": "2024-09-10T06:00:00",
    "fetched_at": "2024-09-10T06:05:00"
  }
]
```

#### Python 示例
```python
async def get_forecast():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8000/api/v1/weather/forecast/台北市",
            params={"days": 7}
        )
        forecasts = response.json()
        for forecast in forecasts:
            date = forecast['forecast_time']
            max_temp = forecast['temperature_max']
            min_temp = forecast['temperature_min']
            print(f"{date}: {max_temp}°C ~ {min_temp}°C")
```

### 3. 獲取氣象警告

#### 請求
```bash
GET /api/v1/weather/alerts/台北市?active_only=true
```

#### 響應
```json
[
  {
    "id": 1,
    "location_name": "台北市",
    "latitude": 25.0330,
    "longitude": 121.5653,
    "alert_type": "豪雨特報",
    "alert_level": "Severe",
    "alert_description": "北部地區即將有豪雨，請注意防雨。",
    "alert_issued_at": "2024-09-10T15:00:00",
    "alert_expires_at": "2024-09-10T21:00:00",
    "is_active": true,
    "created_at": "2024-09-10T15:05:00"
  }
]
```

### 4. 獲取運動天氣建議

#### 請求
```bash
GET /api/v1/weather/recommendations/1
```

#### 響應
```json
{
  "id": 1,
  "activity_id": 1,
  "mode_id": 1,
  "recommendation_level": "warning",
  "reasons": ["temperature_high", "humidity_high"],
  "suggestions": "溫度過高，容易中暑。建議選擇清晨或傍晚進行運動。濕度過高，身體散熱困難。建議縮短運動時間。",
  "temperature_status": "warning",
  "humidity_status": "warning",
  "wind_status": "optimal",
  "precipitation_status": "optimal",
  "visibility_status": "optimal",
  "uv_status": "optimal",
  "created_at": "2024-09-10T12:00:00",
  "updated_at": "2024-09-10T12:00:00"
}
```

### 5. 手動更新天氣數據

#### 請求
```bash
POST /api/v1/weather/update/台北市
```

#### 響應
```json
{
  "status": "success",
  "message": "已更新台北市的天氣數據",
  "current_weather": "updated",
  "forecasts_count": 8,
  "alerts_count": 0
}
```

---

## 💡 天氣建議系統

### 建議等級

| 等級 | 描述 | 運動建議 |
|------|------|--------|
| 🟢 **SAFE** | 天氣良好 | 可正常進行運動 |
| 🟡 **WARNING** | 有輕微警告 | 建議調整運動強度或時間 |
| 🔴 **DANGER** | 有危險警告 | 不建議進行戶外運動 |

### 評估因素

#### 1. 溫度 (Temperature)
```python
# 危險溫度範圍根據運動模式定義
sport_mode.danger_temp_max  # 最高危險溫度
sport_mode.danger_temp_min  # 最低危險溫度
sport_mode.warning_temp_max # 最高警告溫度
sport_mode.warning_temp_min # 最低警告溫度
```

#### 2. 濕度 (Humidity)
```python
# 高濕度時身體散熱困難
sport_mode.warning_humidity_max = 85  # 濕度超過 85% 發出警告
```

#### 3. 風速 (Wind Speed)
```python
sport_mode.danger_wind_speed_max = 15.0  # m/s
sport_mode.warning_wind_speed_max = 10.0  # m/s
```

#### 4. 降水 (Precipitation)
```python
sport_mode.danger_precipitation_prob = 80  # 降水機率超過 80% 為危險
sport_mode.warning_precipitation_prob = 50  # 降水機率超過 50% 為警告
```

#### 5. 能見度 (Visibility)
```python
sport_mode.danger_visibility_min = 1000  # 公尺，低於 1000m 為危險
```

#### 6. 紫外線 (UV Index)
```python
# UV 指數分級
# 0-2: 低
# 3-5: 中
# 6-7: 高
# 8-10: 極高
# 11+: 危險
```

### 使用建議引擎

```python
from app.services.recommendation_engine import RecommendationEngine
from app.database import get_db_session

async def generate_recommendations():
    engine = RecommendationEngine()
    
    async with get_db_session() as db:
        # 為特定運動生成建議
        recommendation = await engine.generate_recommendation(
            activity_id=1,
            db=db
        )
        
        print(f"建議等級: {recommendation.recommendation_level}")
        print(f"建議原因: {recommendation.reasons}")
        print(f"詳細建議: {recommendation.suggestions}")
```

---

## ⏰ 定時任務

### 配置定時任務

```python
from app.tasks.scheduler import configure_scheduler, get_scheduler_manager

# 應用啟動時配置
scheduler_manager = get_scheduler_manager()
configure_scheduler()
scheduler_manager.start()

# 應用關閉時停止
scheduler_manager.stop()
```

### 定時任務清單

#### 1. 更新天氣數據 (每 30 分鐘)
```python
# 任務 ID: update_weather_data
# 觸發器: IntervalTrigger(minutes=30)
# 功能: 更新所有主要城市的天氣數據
```

#### 2. 清理舊數據 (每天 02:00)
```python
# 任務 ID: clean_old_weather_data
# 觸發器: CronTrigger(hour=2, minute=0)
# 功能: 刪除 7 天前的即時天氣和過期預報
```

#### 3. 檢查警告 (每 15 分鐘)
```python
# 任務 ID: check_weather_alerts
# 觸發器: IntervalTrigger(minutes=15)
# 功能: 檢查活躍警告，發送通知
```

#### 4. 生成建議 (每小時)
```python
# 任務 ID: generate_activity_recommendations
# 觸發器: IntervalTrigger(hours=1)
# 功能: 為最近完成的運動生成天氣建議
```

#### 5. 清理過期警告 (每小時)
```python
# 任務 ID: cleanup_expired_alerts
# 觸發器: IntervalTrigger(hours=1)
# 功能: 將過期警告標記為非活躍
```

### 自定義定時任務

```python
from apscheduler.triggers.interval import IntervalTrigger
from app.tasks.scheduler import get_scheduler_manager

async def my_custom_task():
    print("執行自定義任務...")
    # 你的任務邏輯

scheduler_manager = get_scheduler_manager()
scheduler = scheduler_manager.get_scheduler()

scheduler.add_job(
    my_custom_task,
    trigger=IntervalTrigger(hours=2),
    id='my_custom_task',
    name='我的自定義任務'
)
```

---

## 🧪 測試和調試

### 單元測試示例

```python
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_get_current_weather():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/weather/current/台北市")
        assert response.status_code == 200
        data = response.json()
        assert "location_name" in data
        assert data["location_name"] == "台北市"

@pytest.mark.asyncio
async def test_get_forecast():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/v1/weather/forecast/台北市",
            params={"days": 7}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

@pytest.mark.asyncio
async def test_weather_alert():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/weather/alerts/台北市")
        assert response.status_code in [200, 404]  # 沒有警告時返回空列表
```

### 調試技巧

#### 1. 查看日誌
```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug("這是調試信息")
logger.info("這是普通信息")
logger.warning("這是警告信息")
logger.error("這是錯誤信息")
```

#### 2. 測試 API 端點
```bash
# 使用 curl
curl -X GET "http://localhost:8000/api/v1/weather/current/台北市"

# 使用 httpie
http GET http://localhost:8000/api/v1/weather/current/台北市

# 使用 Python
python -c "
import httpx
import asyncio

async def test():
    async with httpx.AsyncClient() as client:
        r = await client.get('http://localhost:8000/api/v1/weather/current/台北市')
        print(r.json())

asyncio.run(test())
"
```

#### 3. 檢查數據庫
```python
from sqlalchemy import select
from app.database import get_db_session
from app.models import CurrentWeather

async def check_db():
    async with get_db_session() as db:
        stmt = select(CurrentWeather).limit(5)
        result = await db.execute(stmt)
        weathers = result.scalars().all()
        
        for w in weathers:
            print(f"{w.location_name}: {w.temperature}°C")

asyncio.run(check_db())
```

---

## ❓ 常見問題

### Q1: 如何更新特定位置的天氣？

**A:** 調用手動更新 API：

```bash
POST /api/v1/weather/update/台北市
```

或使用 Python：

```python
from app.services.weather_service import CWBWeatherService
from app.database import get_db_session

async def update_weather():
    async with get_db_session() as db:
        service = CWBWeatherService()
        weather = await service.get_current_weather("台北市", db)
        print(weather)

asyncio.run(update_weather())
```

### Q2: 天氣建議不準確怎麼辦？

**A:** 檢查以下幾點：

1. **運動模式配置** - 確認 `SportModes` 中的各項閾值是否合理
2. **天氣數據** - 確認天氣數據是否正確更新
3. **天氣快照** - 確認運動期間是否記錄了天氣快照

```python
# 檢查運動模式
from app.models import SportModes
from app.database import get_db_session

async def check_sport_mode():
    async with get_db_session() as db:
        mode = await db.get(SportModes, 1)
        print(f"危險溫度: {mode.danger_temp_max}°C")
        print(f"警告濕度: {mode.warning_humidity_max}%")
```

### Q3: API 返回 404 錯誤？

**A:** 可能原因：

1. 位置名稱不正確 - 使用支持的位置名稱（如 "台北市"）
2. 還沒有天氣數據 - 手動更新數據或等待定時任務執行
3. 數據已過期 - 檢查數據的 `fetched_at` 時間

```python
# 獲取所有可用位置
from app.services.weather_service import CWBWeatherService

service = CWBWeatherService()
print(service.MAJOR_CITIES.keys())
```

### Q4: 如何批量更新所有城市？

**A:** 調用批量更新 API：

```bash
POST /api/v1/weather/update-all
```

或手動執行：

```python
from app.services.weather_service import CWBWeatherService
from app.database import get_db_session

async def update_all():
    async with get_db_session() as db:
        service = CWBWeatherService()
        await service.update_all_locations(db)

asyncio.run(update_all())
```

### Q5: 定時任務沒有執行？

**A:** 檢查以下步驟：

1. 確認調度器已啟動
```python
scheduler_manager = get_scheduler_manager()
print(scheduler_manager.scheduler.running)  # 應為 True
```

2. 查看日誌
```python
import logging
logging.getLogger('apscheduler').setLevel(logging.DEBUG)
```

3. 列出所有任務
```python
scheduler = scheduler_manager.get_scheduler()
for job in scheduler.get_jobs():
    print(f"任務: {job.name}, 下次執行: {job.next_run_time}")
```

### Q6: 如何處理 API 限流？

**A:** 中央氣象局 API 有請求限制，建議：

1. 使用定時任務而不是即時查詢
2. 添加重試機制

```python
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def get_weather_with_retry(location_name):
    service = CWBWeatherService()
    async with get_db_session() as db:
        return await service.get_current_weather(location_name, db)
```

---

## 📞 支持和反饋

- 📧 Email: rex1005464058@gmail.com
- 🐛 Issue: GitHub Issues
- 💬 Discussion: GitHub Discussions

---

## 📝 更新日誌

### v1.0.0 (2024-09-10)
- ✅ 中央氣象局 API 集成
- ✅ 天氣建議引擎
- ✅ 定時任務調度
- ✅ FastAPI 路由
- ✅ 完整文檔

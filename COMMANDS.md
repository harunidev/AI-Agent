# AI4SE Test Generation System - Çalıştırma Komutları

## 1. Backend (FastAPI) Başlatma

Yeni bir PowerShell terminali açın ve şu komutları sırayla çalıştırın:

```powershell
cd "c:\Users\Aures\AI AGENT\server"
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Backend başarıyla çalıştığında şunu göreceksiniz:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

## 2. Frontend (React/Vite) Başlatma

BAŞKA BİR yeni PowerShell terminali açın ve şu komutları çalıştırın:

```powershell
cd "c:\Users\Aures\AI AGENT\client"
npm install
npm run dev
```

Frontend başarıyla çalıştığında şunu göreceksiniz:
```
VITE v5.x.x  ready in xxx ms
➜  Local:   http://localhost:5173/
```

## 3. Test

Tarayıcıda şu adresi açın:
```
http://localhost:5173
```

## 4. API Key Kontrolü

Eğer `.env` dosyasına API key eklemediyseniz:

```powershell
cd "c:\Users\Aures\AI AGENT"
notepad .env
```

İçine şunu yazın:
```
GEMINI_API_KEY=AIzaSy...
```

Kaydet ve backend'i yeniden başlat (Ctrl+C ile durdur, tekrar uvicorn komutunu çalıştır).

## 5. Health Check

Backend çalışıyor mu kontrol:
```
http://localhost:8000/health
```

Şunu görmelisiniz:
```json
{"status":"ok","service":"test-generation-engine","ai_mode":"connected"}
```

Eğer `"ai_mode":"missing_key"` görürseniz, `.env` dosyasındaki API key'i kontrol edin.

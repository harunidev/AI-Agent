# AI4SE Test Generation System

**Proje 2**: AI-Powered otomatik test üretim sistemi. ≥90% kod coverage hedefi.

## Kurulum

### Backend
```bash
cd server
pip install -r requirements.txt
```

### Frontend  
```bash
cd client
npm install
```

### Environment
1. Ana klasörde `.env` dosyasını düzenleyin:
```
GEMINI_API_KEY=your_api_key_here
```

## Çalıştırma

Projeyi çalıştırmak için ana klasörde:
```bash
.\run_dev.bat
```

veya manuel:

**Backend:**
```bash
cd server
uvicorn main:app --reload
```

**Frontend:**  
```bash
cd client
npm run dev
```

## Kullanım

1. `http://localhost:5173` adresine gidin
2. Python kodunuzu yapıştırın
3. "Generate Tests" butonuna tıklayın
4. AI sistem otomatik olarak testler oluşturacak ve coverage hesaplayacak
5. Eğer coverage <90% ise, sistem otomatik olarak iyileştirme yapacak

## Teknoloji Stack

- **Backend**: Python 3.13, FastAPI, Gemini AI
- **Frontend**: React, Vite
- **Design**: Emerald & Gold (No Blue/Purple)
- **AI**: Google Gemini 1.5 Flash
- **Testing**: pytest, coverage.py

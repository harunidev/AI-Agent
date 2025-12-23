import json
import os
from datetime import datetime

class BildirimServisi:
    def gonder(self, mesaj: str):
        print(f"Bildirim: {mesaj}")
        return True

class GorevYoneticisi:
    def __init__(self, veri_dosyasi: str):
        self.dosya = veri_dosyasi
        self.gorevler = {}
        self._yukle()

    def _yukle(self):
        if os.path.exists(self.dosya):
            with open(self.dosya, 'r') as f:
                try:
                    self.gorevler = json.load(f)
                except:
                    self.gorevler = {}

    def kaydet(self):
        with open(self.dosya, 'w') as f:
            json.dump(self.gorevler, f)

    def gorev_ekle(self, baslik: str, oncelik: int = 1):
        if oncelik < 1 or oncelik > 5:
            raise ValueError("Öncelik 1-5 arasında olmalı")
            
        if not baslik:
            raise ValueError("Başlık boş olamaz")

        gorev_id = str(len(self.gorevler) + 1)
        self.gorevler[gorev_id] = {
            "baslik": baslik,
            "oncelik": oncelik,
            "tamamlandi": False,
            "tarih": str(datetime.now())
        }
        self.kaydet()
        return gorev_id

    def gorev_tamamla(self, gorev_id: str, bildirim: BildirimServisi):
        if gorev_id not in self.gorevler:
            return "Görev bulunamadı"
            
        task = self.gorevler[gorev_id]
        if task["tamamlandi"]:
            return "Zaten tamamlanmış"
            
        task["tamamlandi"] = True
        self.kaydet()
        
        if bildirim:
            bildirim.gonder(f"{task['baslik']} tamamlandı")
            
        return "Başarılı"

    def raporla(self, filtre_oncelik: int = None):
        if not self.gorevler:
            return []
            
        sonuc = []
        for g_id, detay in self.gorevler.items():
            if filtre_oncelik and detay["oncelik"] != filtre_oncelik:
                continue
            sonuc.append(detay)
            
        return sonuc

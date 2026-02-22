import tkinter as tk
import requests
import datetime
import threading
from plyer import notification

class EzanVaktiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ezan Vakti - Kağıthane")
        self.root.geometry("300x450")
        self.root.configure(bg="#f4f4f4")
        self.root.resizable(False, False)
        
        self.vakitler = {}
        self.siradaki_vakit_adi = ""
        self.siradaki_vakit_saati = None
        self.bildirim_10dk_gonderildi = False
        self.bildirim_okunuyor_gonderildi = False
        
        self.baslik = tk.Label(root, text="Vakitler Çekiliyor...", font=("Segoe UI", 16, "bold"), bg="#f4f4f4")
        self.baslik.pack(pady=15)
        self.kalan_sure_label = tk.Label(root, text="", font=("Segoe UI", 14), fg="#d32f2f", bg="#f4f4f4")
        self.kalan_sure_label.pack(pady=10)
        
        self.vakit_frame = tk.Frame(root, bg="#f4f4f4")
        self.vakit_frame.pack(pady=10)
        self.vakit_labellari = {}
        vakit_isimleri = ["İmsak", "Güneş", "Öğle", "İkindi", "Akşam", "Yatsı"]
        
        for v in vakit_isimleri:
            lbl = tk.Label(self.vakit_frame, text=f"{v}:\t--:--", font=("Segoe UI", 12), bg="#f4f4f4")
            lbl.pack(anchor="w", pady=3)
            self.vakit_labellari[v] = lbl
            
        threading.Thread(target=self.api_guncelle, daemon=True).start()
        self.saati_guncelle()

    def api_guncelle(self):
        while True:
            try:
                url = "http://api.aladhan.com/v1/timingsByCity?city=Istanbul&country=Turkey&method=13"
                res = requests.get(url, timeout=10).json()
                t = res['data']['timings']
                self.vakitler = {
                    "İmsak": t["Fajr"], "Güneş": t["Sunrise"], "Öğle": t["Dhuhr"],
                    "İkindi": t["Asr"], "Akşam": t["Maghrib"], "Yatsı": t["Isha"]
                }
                self.root.after(0, self.ui_vakitleri_guncelle)
                threading.Event().wait(43200) 
            except Exception:
                threading.Event().wait(30)
                
    def ui_vakitleri_guncelle(self):
        self.baslik.config(text="İstanbul / Kağıthane")
        for v, saat in self.vakitler.items():
            self.vakit_labellari[v].config(text=f"{v}:\t{saat}")
            
    def saati_guncelle(self):
        if self.vakitler:
            su_an = datetime.datetime.now()
            siradaki = None
            for v, saat in self.vakitler.items():
                saat_obj = datetime.datetime.strptime(saat, "%H:%M").replace(
                    year=su_an.year, month=su_an.month, day=su_an.day, second=0, microsecond=0
                )
                if saat_obj > su_an:
                    siradaki = (v, saat_obj)
                    break
                    
            if siradaki:
                yeni_vakit_adi, yeni_vakit_saati = siradaki
            else:
                yeni_vakit_saati = datetime.datetime.strptime(self.vakitler["İmsak"], "%H:%M").replace(
                    year=su_an.year, month=su_an.month, day=su_an.day
                ) + datetime.timedelta(days=1)
                yeni_vakit_adi = "İmsak"
                
            if self.siradaki_vakit_adi != yeni_vakit_adi:
                self.siradaki_vakit_adi = yeni_vakit_adi
                self.siradaki_vakit_saati = yeni_vakit_saati
                self.bildirim_10dk_gonderildi = False
                self.bildirim_okunuyor_gonderildi = False
                
            fark = self.siradaki_vakit_saati - su_an
            saniye_farki = int(fark.total_seconds())
            dakika, saniye = divmod(saniye_farki, 60)
            saat, dakika = divmod(dakika, 60)
            
            self.kalan_sure_label.config(text=f"{self.siradaki_vakit_adi} vaktine kalan:\n{saat:02d}:{dakika:02d}:{saniye:02d}")
            
            if self.siradaki_vakit_adi != "Güneş":
                if 600 >= saniye_farki > 590 and not self.bildirim_10dk_gonderildi:
                    self.bildirim_gonder("Ezan Yaklaştı", f"{self.siradaki_vakit_adi} ezanına 10 dakika kaldı!")
                    self.bildirim_10dk_gonderildi = True
                elif saniye_farki <= 0 and not self.bildirim_okunuyor_gonderildi:
                    self.bildirim_gonder("Ezan Vakti", f"{self.siradaki_vakit_adi} ezanı okunuyor.")
                    self.bildirim_okunuyor_gonderildi = True

        self.root.after(1000, self.saati_guncelle)
        
    def bildirim_gonder(self, baslik, mesaj):
        try:
            notification.notify(title=baslik, message=mesaj, app_name='Ezan Vakti', timeout=10)
        except Exception:
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = EzanVaktiApp(root)
    root.mainloop()
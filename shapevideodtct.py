import cv2
import numpy as np
import json
import os


def analiz_et(original_img):
    
    scale_percent = 50 
    width = int(original_img.shape[1] * scale_percent / 100)
    height = int(original_img.shape[0] * scale_percent / 100)
    dim = (width, height)
    resized = cv2.resize(original_img, dim, interpolation = cv2.INTER_AREA)

    # RGB -> HSV Dönüşümü
    hsv = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)
    
    # Renk Sınırları 
    renk_sinirlari = {
        "kirmizi": [
            (np.array([0, 100, 100]), np.array([10, 255, 255])),
            (np.array([160, 100, 100]), np.array([180, 255, 255]))
        ],
        "yesil": [
            (np.array([35, 50, 50]), np.array([85, 255, 255]))
        ],
        "mavi": [
            (np.array([90, 50, 50]), np.array([130, 255, 255]))
        ],
        "sari": [
            (np.array([20, 100, 100]), np.array([35, 255, 255]))
        ]
    }
    
    sonuclar = []
    cizim_alani = resized.copy()
    
    # Her renk için tarama
    for renk_adi, araliklar in renk_sinirlari.items():
        maske = np.zeros(hsv.shape[:2], dtype="uint8")
        for (alt, ust) in araliklar:
            maske = cv2.bitwise_or(maske, cv2.inRange(hsv, alt, ust))
            
        # Gürültü temizliği
        kernel = np.ones((5,5), np.uint8)
        maske = cv2.morphologyEx(maske, cv2.MORPH_OPEN, kernel)
        maske = cv2.morphologyEx(maske, cv2.MORPH_CLOSE, kernel)
        
        # Kontür bulma
        konturler, _ = cv2.findContours(maske, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for cnt in konturler:
            alan = cv2.contourArea(cnt)
            if alan > 1000: 
                
                # Şekil Algılama 
                cevre = cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, 0.04 * cevre, True)
                kose_sayisi = len(approx)
                
                x, y, w, h = cv2.boundingRect(cnt)
                sekil_adi = "Bilinmiyor"
                
                if kose_sayisi == 3:
                    sekil_adi = "Ucgen"
                elif kose_sayisi == 4:
                    en_boy_orani = float(w) / h
                    if 0.90 <= en_boy_orani <= 1.10:
                        sekil_adi = "Kare"
                    else:
                        sekil_adi = "Dikdortgen"
                elif kose_sayisi > 4:
                    sekil_adi = "Daire"
                
                # Veriyi Kaydetme
                sonuclar.append({
                    "renk": renk_adi,
                    "sekil": sekil_adi,
                    "bbox": {"x": x, "y": y, "w": w, "h": h}
                })
                
                # Görselleştirme
                cv2.rectangle(cizim_alani, (x, y), (x + w, y + h), (0, 255, 0), 2)
                etiket = f"{renk_adi} {sekil_adi}"
                cv2.putText(cizim_alani, etiket, (x, y + h//2), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(cizim_alani, etiket, (x, y + h//2), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1) 

    return sonuclar, cizim_alani

# ÇALIŞTIRMA KISMI 

# Dosya adı yerine video dosyasının adı veya webcam için 0 yazılır.
video_kaynagi = "video.mp4"  # Webcam kullanacaksan buraya 0 yaz: cv2.VideoCapture(0)
cap = cv2.VideoCapture(0) #0 ile webcam çalışır 

frame_width = int(cap.get(3))
frame_height = int(cap.get(4))

kayit_genislik = int(frame_width * 0.50)  # %50 küçültme
kayit_yukseklik = int(frame_height * 0.50) # %50 küçültme

# 'video_kaydi.mp4' adında dosya oluşturur
dosya_adi = 'video_kaydi.avi'
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(dosya_adi, fourcc, 20.0, (kayit_genislik, kayit_yukseklik))

kayit_yolu = os.path.join(os.getcwd(), dosya_adi)
print("-" * 50)
print(f"!!! VİDEO ŞURAYA KAYDEDİLECEK: {kayit_yolu}")
print("-" * 50)
print("Çıkmak ve kaydetmek için ekrandaki pencereye tıklayıp 'q' tuşuna bas.")

tum_veriler = [] # Tüm videodaki verileri toplamak için liste
frame_sayaci = 0


while True:
    ret, frame = cap.read() # Videodan bir kare oku
    
    if not ret: # Video bittiyse veya hata varsa döngüden çık
        break
        
    frame_sayaci += 1
    
    # Fonksiyonu çağır 
    kare_verisi, sonuc_resmi = analiz_et(frame)

    out.write(sonuc_resmi)
    
    # Hangi karede ne bulunduysa genel listeye ekle 
    if kare_verisi:
        tum_veriler.append({
            "frame_no": frame_sayaci,
            "tespitler": kare_verisi
        })
    
    # Sonucu Göster
    cv2.imshow("Video Analiz", sonuc_resmi)
    
    # 'q' tuşuna basılırsa döngüyü kır (1 milisaniye bekle)
    # waitKey(0) videoyu dondurur, waitKey(1) akmasını sağlar.
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

out.release()

# Temizlik işlemleri
cap.release()
cv2.destroyAllWindows()

# JSON Kaydet (Döngü bittikten sonra hepsini kaydetmek daha mantıklı)
with open('video_sonuclar.json', 'w', encoding='utf-8') as f:
    json.dump(tum_veriler, f, ensure_ascii=False, indent=4)

print(f"Video bitti. Toplam {len(tum_veriler)} karede nesne tespit edildi.")
print("Sonuçlar 'video_sonuclar.json' dosyasına kaydedildi.")
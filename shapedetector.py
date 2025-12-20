import cv2
import numpy as np
import json

def analiz_et(image_path):
    original_img = cv2.imread(image_path)
    
    if original_img is None:
        print("Hata: Resim dosyası bulunamadı! Dosya adını kontrol et.")
        return [], None
    
    # Resim yüksek çözünürlüklü, o yüzden oranla küçültüyoruz.
    scale_percent = 50 
    width = int(original_img.shape[1] * scale_percent / 100)
    height = int(original_img.shape[0] * scale_percent / 100)
    dim = (width, height)
    resized = cv2.resize(original_img, dim, interpolation = cv2.INTER_AREA)

    #  RGB -> HSV Dönüşümü
    hsv = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)
    
    #  Renk Sınırları (Bu resimdeki tonlara göre geniş aralıklar)
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
    
    #  Her renk için tarama yap
    for renk_adi, araliklar in renk_sinirlari.items():
        maske = np.zeros(hsv.shape[:2], dtype="uint8")
        for (alt, ust) in araliklar:
            maske = cv2.bitwise_or(maske, cv2.inRange(hsv, alt, ust))
            
        # Gürültü temizliği (Morphology)
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
                    # En/Boy oranı 1'e yakınsa karedir
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
                # Yazıyı şeklin ortasına yazma
                cv2.putText(cizim_alani, etiket, (x, y + h//2), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(cizim_alani, etiket, (x, y + h//2), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1) 

    return sonuclar, cizim_alani

# Çalıştırma kısmı
dosya_adi = "deneme.png" 

veri, sonuc_resmi = analiz_et(dosya_adi)

if sonuc_resmi is not None:
    # JSON Kaydet
    with open('sonuclar.json', 'w', encoding='utf-8') as f:
        json.dump(veri, f, ensure_ascii=False, indent=4)

    cv2.imwrite("analiz_sonucu.jpg", sonuc_resmi)
    print(f"Toplam {len(veri)} nesne bulundu.")
    print("Sonuçlar 'sonuclar.json' dosyasına kaydedildi.")

    # Sonucu Göster
    cv2.imshow("sekil tanıma", sonuc_resmi)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
# RGB -> HSV dönüşümü
-> OpenCV resimleri varsayılan olarak BGR formatında okur. Ancak BGR (veya RGB), renk tespiti yapmak için kötü bir formattır. Işık değiştiğinde BGR'deki üç sayı birden değişir. 
Bilgisayara örneğin "Kırmızıyı bul" demek için yüzlerce farklı sayı kombinasyonu yazmak gerekir. Işık değiştikçe algoritma çöker. HSV (Hue, Saturation, Value) HSV formatı, 
rengi (Hue) ışıktan (Value) ayırır. Işık ne kadar değişirse değişsin, Hue (Renk Özü) değeri neredeyse sabit kalır.

# Renk Sınırları
-> np.array([x, y, z]) ifadesinde H (Hue). S (Saturation) Çok soluk renkleri (beyaza yakın) almamak için alt sınırı yüksek tuttuk. V (Value) Gölgeleri ve karanlık noktaları 
"renk" sanmasın diye alt sınırı yüksek tuttuk.
-> Kırmızının iki parça olmasının sebebi: HSV renk uzayında 0 kırmızıdan başlayıp 180de tekrar kırmızıya döner. Başlangıç: 0 ile 10 arası (Hafif turuncuya çalan kırmızılar). 
Bitiş: 160 ile 180 arası (Hafif mora/pembeye çalan kırmızılar).

# Her renk için tarama                                    
-> renk_sinirlari sözlüğünde bulunan her bir rengin adını ve o renge ait sınır değerlerini sırasıyla alıp işlemek için bir döngü başlattık. Daha sonra orijinal resmimle (hsv) 
aynı boy ve ende ([:2]), 0 ile 255 aralığında değerler alan (uint8), içi tamamen siyah (zeros) bir sayfa oluşturduk. Devamında belirlenen alt ve üst sınır aralığına giren pikselleri 
o anlık tespit edip, bu yeni parçayı önceki bulduklarımızı kaybetmeyecek şekilde ana maskemize (üzerine koyarak) ekliyoruz.

# Gürültü temizliği                                       
-> Kernel (Çekirdek), resmin üzerinde gezdirilen küçük bir sayı matrisidir, np.ones((5,5), np.uint8) yazdığında bilgisayara şunu diyoruz: Bana 5'e 5 boyutunda bir tablo yap (ones), 
içini 1 ile doldur ve bu sayılar resim formatına uygun (0-255 arası) formatta (uint8) olsun.
-> Bilgisayara; Bana delikli, kenarları pürüzlü ve etrafı tozlu bir şekil verme; bana pürüzsüz, bütün ve net bir şekil ver demek için erosion ve dilation yapıyoruz.
-> morphologyEx OpenCV'nin şekil değiştirme (morphology) fonksiyonudur. Sadece büyütme veya küçültme yapmaz; bunların kombinasyonlarını (ardı ardına uygulanmasını) yönetir. 
Bu kod, resimdeki her şeyi önce biraz aşındırıp küçülterek minik gereksiz noktaların silinip kaybolmasını sağlar, hemen ardından geriye kalan ana şekli tekrar şişirerek eski boyutuna geri döndürür.

# Kontür bulma
-> cv2.findContours(...) OpenCV'nin sınır bulma motorudur.
-> cv2.RETR_EXTERNAL en dıştaki ana çerçeveyi bulur.
-> cv2.CHAIN_APPROX_SIMPLE çizgi üzerindeki yüzlerce noktayı tek tek kaydetmek yerine köşe noktalarını kaydeder.
-> resimdeki şekiller büyük olduğu için eşiği yükselterek küçük detayları almamasını sağladık. cv2.contourArea: OpenCV'nin ölçüm fonksiyonudur, O anki şeklin  kapladığı alanı piksel cinsinden hesaplar.

# Şekil algılama
-> cv2.arcLength şeklin çevresinin ne kadar uzun olduğunu (piksel cinsinden) ölçer. True girdişi şeklin uçlarının birleşik olduğunu ifade eder.
cv2.approxPolyDP(cnt, epsilon, True), epsilon, şeklin orijinale ne kadar benzeyeceğini belirleyen maksimum mesafe hatasıdır. Geometrik şekiller için genellikle 0.02-0.05 aralığında kullanılır.  
Approx, şeklin yeni ve sadeleştirilmiş koordinat listesidir.
-> cv2.boundingRect 'şekli kutuya hapsetme fonksiyonu'. x ve y Kutunun sol üst köşesinin koordinatları. w  Kutunun genişliği h  Kutunun yüksekliği. 
-> köşe tespiti: kare ve dikdörtgenin ayırımında en boy oranlarından yararlanıp tespit edildi. 

# Verileri kaydetme
-> tek hamlede koordinatları çekebilecek şekilde yazdık

# Görselleştirme
-> cv2.BoundingRect matematiksel olarak şekli hesaplar, cv2.rectangle boyamasını yapar, beraber çalışırlar. Devamında yazılacak yazının boyut font kalınlık ve yerini ayarladık.

# Çalıştırma
-> türkçe karakterler bozulmayacak şekilde json dosyası oluşturduk






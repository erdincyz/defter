![GIF](https://raw.githubusercontent.com/erdincyz/gorseller/master/_defter/defter.gif)

### [ENGLISH](https://github.com/erdincyz/defter/blob/main/README_EN.md)

### Hoşgeldiniz

İnşallah, **Defter** vakit buldukça ve ihtiyaç duyuldukça halen geliştirilmekte olan açık kaynak bir yazılımdır.

* Sınırlandırılmamış bir sayfanın her hangi bir yerine çift tıklayıp, hızlıca not almak için,
* Şekiller diyagramlar çizmek için,
* İnternetten sürükle bırak veri toplamak için,
* Belli konulardaki toplanmış verileri bir araya toparlamak için kullanılabilir.
* Görsellik ön plandadır. Belgeye fotoğraf, video, (herhangi bir formatta)dosya ekleyebilme ve browserdan (ve diğer
  yazılımlardan) kopyala yapıştır, sürükle bırak yazı(HMTL destekler),ekleyebilme desteği vardır.
* HTML içeren yazi nesnelerini, nesneye sağ tıklayınca açılan menüdeki **Web Sayfası Olarak** göster özelliğini
  kullanarak tekrar içerdiği linklere tıklanabilir hale getirebilirsiniz.
* Mesela sayfaya taşıyacağınız, **veya** izlemekte olduğunuz bir videodan ekran görüntüsü alıp, sayfaya yapıştıracağınız
  o resmin üzerine çift tıklayınca, resmin tıkladığınız noktasında bir metin kutusu oluşur. Böylece resmin üzerine de
  dilediğiniz kadar not alabilirsiniz.
* Sayfayı veya tüm belgeyi PDF veya HTML dosyası olarak kaydedebilirsiniz.

_Bu yazılım kağıt kaleme alternatif değildir. Dijital ortamlardan verileri hızlıca bir araya toparlayabilmek için
faydalıdır belki en fazla._

**GPLv3** lisanslıdır.

**Birçok Bug (Hata)** ve **tam olarak eklenmemiş özellikler** içerir. İyice kurcalayıp denemeden **önemli işler** için
kullanma**MA**nız tavsiye edilir.

**Bilinen hataları ve eklenmek niyetinde olunan özellikleri (şu an güncel olmamakla beraber)** bu sayfadaki *
*[Issues](https://github.com/erdincyz/defter/issues)** kısmından takip edebilirsiniz.

---

### Windows için Alternatif Kurulum Dosyası

[Buradan](https://github.com/erdincyz/defter/releases/tag/v0.97.1-rc) "defter-installer.exe" dosyasını indirip kurmayı deneyebilirsiniz.

---

### KURULUM
Sisteminizde Python 3 yüklü olması gerekiyor.

Python 3' ü [https://www.python.org/downloads/](https://www.python.org/downloads/) adresinden indirip kurabilirsiniz.

Python 3 yüklü ise komut satirindan

```
python -m pip install defter-argekod

```

komutu ile programı kurabilirsiniz.

Kurulum tamamlanınca;

```
defter
```

komutu ile programı çalıştırabilirsiniz.

Varsa, programı yeni sürüme güncellemek için;

```
python -m pip install -U defter-argekod

```

ve dilerseniz programı silmek için;

```
python -m pip uninstall defter-argekod

```

komutlarını kullanabilirsiniz.

---

### [YARDIM SAYFALARI](https://github.com/erdincyz/defter/wiki)

---

### Dosya Yapısı:

Uzantısı "def" olarak değiştirilmiş sıkıştırma oranı 1 olan zip dosyalarıdır.
Zip dosyaları konteynır gibi kullanılmaktadır.
Dosyaları bir zip dosyası gibi açıp içindeki gömülü diger dosyalara erişebilirsiniz.
Ayrıca her dosya kaydedildiğinde, belgedeki her sayfa için bir html dosyası da def içine kaydedilir.
Böylelikle bu yazılıma ihtiyaç duymadan, def dosyasını bir klasore açıp içindeki html dosyalarını web gezgininde açarak
da belgenize erişebilirsiniz.

---

### İpuçları

#### Dosyaları daha hızlı kaydedebilmek için:

Sisteminizde 7z veya zip yüklü ise ve komut satırından direkt erişilebilir ise, Defter dosyaları daha hızlı
kaydedebiliyor.
Çünkü, 7z veya zip in desteklediği arşiv güncelleme özelliğini, python ile gelen zipfile modulu desteklememekte.
(Arşiv güncelleme özelliği: Sadece eklenen veya değişen dosyaları tekrar diske yazıyor. Belgeyi her kaydettiğimizde
belgenin içerdiği tüm dosyaları tekrar diske yazmaktan kurtarıyor. )

#### Ekran görüntüsü alıp deftere yapıştırabilirsiniz:

Defter panodan görüntü yapıştırmayı destekler. Aşağıdaki yöntemler veya tercih edeceğiniz başka yöntemler ile 
ekranınızdan dilediğiniz bir alanın görüntüsünü panoya kopyalayıp Deftere yapıştırabilirsiniz.

Mesela linuxta aşagıdaki komutu sistem çapında bir kısayola atayıp kullanabilirsiniz.

Aşağıdaki komut secilen alanın ekran görüntüsünü panoya kopyalar.

#### Linux için:

(Scrot ve xclip yazılımları sisteminizde yüklü değilse öncelikle paket yöneticiniz ile bunları kurmanız gerekiyor.)

```
scrot -s -q 100 '/tmp/foo.jpg' -e 'xclip -selection clipboard -t image/jpg -i $f'
```

#### Windows için:

Aşağıdaki kısayolu kullanabilirsiniz.

```
Win + Shift + S
```

#### OS X için:

Aşağıdaki kısayolu kullanabilirsiniz.

```
Command + Shift + 4
```

### Teşekkürler.

Python ile geliştirilmiş, HTTP/HTTPS web sitelerini ve TCP portlarını eşzamanlı (multi-threaded) kontrol eden, loglama destekli CLI tabanlı ağ sağlık tarama aracı.

Python 3

requests (HTTP istekleri için)

socket (TCP port kontrolü için)

concurrent.futures (Eşzamanlı asenkron tarama için)

argparse (CLI parametre yönetimi için)

1)Repoyu klonlayin.

2)Sanal ortami kurun: python3 -m venv venv

3)Aktif edin: source venv/bin/activate

4)Paketleri yukleyin: pip install requests

5)Calistirin: python app/main.py targets.json
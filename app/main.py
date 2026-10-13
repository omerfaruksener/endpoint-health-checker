import json
from pathlib import Path
import requests
import time
import argparse
import socket

def targets_read(file_path):
    text = Path(file_path).read_text(encoding="utf-8")
    data = json.loads(text)
    return data["targets"]

def check_health(url, timeout_time, max_try):
    for deneme in range(max_try):
        #starting stopwatch
        start_time = time.time()
        if url.startswith("tcp://"):

            try:  
                # "tcp://1.1.1.1:53" metnini temizleyip IP ve Port'a ayırıyoruz
                temiz_adres = url.replace("tcp://","")
                ip, port_str = temiz_adres.split(":")
                port = int(port_str)

                #soket nesnesi oluşturuyoruz
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(timeout_time)

                #bağlanmayı deniyoruz
                sonuc = sock.connect_ex((ip,port))
                sock.close()

                #stoping stopwatch
                stop_time = time.time()
                #calculate latency
                latency_ms = round((stop_time - start_time) * 1000)

                if sonuc == 0:
                    return 200, latency_ms
                else:
                    hata_kodu = 0
            except (socket.timeout, ValueError, Exception):
                hata_kodu = -1
        else:
            try:
         #Send HTTP GET request
                response = requests.get(url, timeout=timeout_time)
                stop_time = time.time()
                latency_ms = round((stop_time - start_time) * 1000)
            #return status code from site
                return response.status_code , latency_ms

            except requests.exceptions.Timeout:
                hata_kodu = -1
    
            except requests.RequestException:
                hata_kodu = 0
        
        if deneme < max_try -1:
            print(f"[RETRY] {url} yanit vermedi. Tekrar deneniyor... ({deneme + 1}/{max_try})")
            time.sleep(1) # Sistemi 1 saniyeliğine uyutur

    return hata_kodu,0

            

if __name__ == "__main__":

    parser =argparse.ArgumentParser(description="API & Network Health Checker")
    parser.add_argument("config_file", help="JSON path file")
    parser.add_argument("--timeout", type=int,default=3, help="Saniye cinsinden bekleme süresi")
    parser.add_argument("--retries", type=int, default=2, help="hata durumunda tekrar deneme sayisi")
    args = parser.parse_args()

    #gives targets.json file 
    list_of_url =targets_read(args.config_file)

    print(f"Sistem Sağlık Taramasi Basliyor... (Timeout: {args.timeout} sn)")
    print("-" * 65)

    for url in list_of_url:
        #check health for each Url
        status, latency = check_health(url, args.timeout, args.retries)
        protocol_label = "TCP" if url.startswith("tcp://") else "HTTP"


        if status == 200:
            print(f"[ UP ] {url:<35} {latency} ms")
        elif status == -1:
            print(f"[TIMEOUT] {url:<32} ({args.timeout} saniyede cevap vermedi!)")
        elif status == 0:
            print(f"[DOWN] {url:<35} (Baglanti Hatasi!)")
        else:
            print(f"[WARN] {url:<35} (Durum: {status})")

import json
from pathlib import Path
import requests
import time
import argparse
import logging
import socket
import concurrent.futures

def targets_read(file_path):
    text = Path(file_path).read_text(encoding="utf-8")
    data = json.loads(text)
    return data["targets"]

def check_health(url, timeout_time, max_try):
    for deneme in range(max_try):
        #starting stopwatch
        start_time = time.time()
        #TCP check
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

        #retry logic
        if deneme < max_try -1:
            messages = f"[RETRY] {url} yanit vermedi. Tekrar deneniyor... ({deneme + 1}/{max_try})"
            print(messages)
            logging.warning(messages)
            time.sleep(1) # Sistemi 1 saniyeliğine uyutur

    return hata_kodu,0

            

if __name__ == "__main__":

    parser =argparse.ArgumentParser(description="API & Network Health Checker")
    parser.add_argument("config_file", help="JSON path file")
    parser.add_argument("--timeout", type=int,default=3, help="Saniye cinsinden bekleme süresi")
    parser.add_argument("--retries", type=int, default=2, help="hata durumunda tekrar deneme sayisi")
    parser.add_argument("--log", type=str, default="health_check.log", help="Log dosyasinin adi")
    args = parser.parse_args()
    logging.basicConfig(
        filename=args.log,
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    #gives targets.json file 
    list_of_url =targets_read(args.config_file)

    print(f"Sistem Sağlık Taramasi Basliyor... (Timeout: {args.timeout} sn)")
    print("-" * 65)

    # NEW: MULTI-THREADING (ROTA B)
    #max workers(threads) = 10
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_tasks = {
            executor.submit(check_health, url, args.timeout, args.retries): url
            for url in list_of_url
        }

        for future in concurrent.futures.as_completed(future_tasks):
            url = future_tasks[future]
            status, latency = future.result()

            protocol_label = "TCP" if url.startswith("tcp://") else "HTTP"


            if status == 200:
                messages =f"[ UP ] [{protocol_label}] {url:<35} {latency} ms"
                print(messages)
                logging.info(messages)
            elif status == -1:
                messages = f"[TIMEOUT] [{protocol_label}] {url:<32} ({args.timeout} saniyede cevap vermedi!)"
                print(messages)
                logging.info(messages)
            elif status == 0:
                messages = f"[DOWN] [{protocol_label}] {url:<35} (Baglanti Hatasi!)"
                print(messages)
                logging.info(messages)
            else:
                messages = f"[WARN] [{protocol_label}] {url:<35} (Durum: {status})"
                print(messages)
                logging.info(messages)

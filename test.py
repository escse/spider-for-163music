import requests
from bs4 import BeautifulSoup
from Crypto.Cipher import AES
import base64, json
import threading, multiprocessing



url = "http://127.0.0.1:8000"

def task(url, i):
    response = requests.post(url)
    print i

def run():
    threads = [threading.Thread(target=task, args=(url, i)) for i in range(100)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

for i in range(100):
    run()
    
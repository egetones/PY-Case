import json
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from colorama import Fore, init

init(autoreset=True)

# Veritabanı dosyamız
DB_FILE = "sifrelerim.json"

def anahtar_uret(master_password):
    """
    Kullanıcının girdiği paroladan güvenli bir şifreleme anahtarı türetir.
    Normalde 'salt' rastgele olmalı ve saklanmalı, ancak eğitim amaçlı sabit tutuyoruz.
    """
    password = master_password.encode() # Byte'a çevir
    salt = b'\x00'*16 # Sabit bir tuz (Gerçek projelerde rastgele olmalı!)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    # Fernet için uygun base64 formatına çevir
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return key

def dosya_yukle():
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def dosya_kaydet(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f)

def main():
    print(Fore.CYAN + "### KIRILMAZ KASA v1.0 ###")
    master_pwd = input(Fore.YELLOW + "Lütfen Ana Anahtarınızı (Master Key) girin: ")
    
    # Anahtarı türet
    key = anahtar_uret(master_pwd)
    fernet = Fernet(key)

    # Mevcut verileri yükle
    sifreler = dosya_yukle()

    while True:
        print(Fore.WHITE + "\n[1] Yeni Şifre Ekle")
        print("[2] Şifreleri Göster")
        print("[3] Çıkış")
        secim = input("Seçiminiz: ")

        if secim == '1':
            site = input("Hangi Site/Uygulama?: ")
            pwd = input("Şifre: ")
            
            # Şifreyi şifrele (Encrypt)
            encrypted_pwd = fernet.encrypt(pwd.encode()).decode()
            
            sifreler[site] = encrypted_pwd
            dosya_kaydet(sifreler)
            print(Fore.GREEN + f"[+] {site} için şifre güvenle saklandı!")

        elif secim == '2':
            print(Fore.MAGENTA + "\n--- KAYITLI ŞİFRELER ---")
            if not sifreler:
                print("Henüz kayıtlı şifre yok.")
            
            for site, enc_pwd in sifreler.items():
                try:
                    # Şifreyi çöz (Decrypt)
                    decrypted_pwd = fernet.decrypt(enc_pwd.encode()).decode()
                    print(f"{Fore.CYAN}{site}: {Fore.WHITE}{decrypted_pwd}")
                except Exception:
                    # Eğer Ana Anahtar yanlışsa burası patlar
                    print(f"{Fore.RED}{site}: ŞİFRE ÇÖZÜLEMEDİ! (Yanlış Anahtar?)")
            print("-" * 25)

        elif secim == '3':
            print("Kasa kilitleniyor... Güle güle!")
            break

if __name__ == "__main__":
    main()

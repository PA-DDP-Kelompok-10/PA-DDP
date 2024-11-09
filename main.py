import csv
import os
import time
import pwinput
from prettytable import PrettyTable
from datetime import datetime, timedelta
from colorama import Fore, Back, Style, init

os.system("cls")
init()

account_file = "accounts.csv"
car_file = "cars.csv"
transaction_file = "transactions.csv"
voucher_file = "voucher.csv"

def read_csv(file):
    data = []
    try:
        with open(file, mode="r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
    except FileNotFoundError:
        open(file, mode="w").close()  # Create an empty file if not found
    return data

def write_csv(file, fieldnames, data):
    with open(file, mode="w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def display_table(data, fieldnames):
    if not data:
        print("Data tidak tersedia.")
        return
    translate = {
        "username" : "Username",
        "password" : "Password",
        "role" : "Role",
        "id": "ID",
        "nama": "Nama Mobil",
        "harga": "Harga Sewa",
        "no plat": "Nomor Plat",
        "status": "Status",
        "balance": "Saldo",
        "days": "Lama Sewa (hari)",
        "total": "Total Biaya",
        "date": "Tanggal Sewa",
        "return_date": "Tanggal Kembali",
        "plate": "Nomor Plat",
        "car": "Mobil"
    }
    table = PrettyTable([translate.get(field, field) for field in fieldnames])
    for row in data:
        table.add_row([row.get(field, "") for field in fieldnames])
    print(table)

def update_ids(file, id_field="id"):
    data = read_csv(file)
    for index, row in enumerate(data, start=1):
        row[id_field] = str(index)  
    fieldnames = data[0].keys() if data else []
    write_csv(file, fieldnames, data)

def confirm_password():
    chance = 3
    while chance > 0:
        password = pwinput.pwinput("Masukkan password: ")
        confirm_password = pwinput.pwinput("Konfirmasi password: ")
        if password == confirm_password:
            return password
        else: 
            chance -= 1
            print(f"Password tidak sama, silahkan coba lagi. {chance} kesempatan tersisa.")
        if chance == 0:
            print("Kesempatan habis, silahkan registrasi ulang.")
            return None

def register():
    os.system("cls")
    print("+----------------------------+")
    print("|        Menu Register       |")
    print("+----------------------------+")

    while True:
        username = input("Masukkan Username: ")
        if username.isalpha():
            break
        else:
            print("Username hanya boleh terdiri dari huruf alfabet. Silakan coba lagi.")

    password = confirm_password()
    
    if password is None:
        return

    role = "user"
    balance = "100000"

    accounts = read_csv(account_file)
    if not any(account["username"] == username for account in accounts):
        accounts.append({"username": username, "password": password, "role": role, "balance": balance})
        write_csv(account_file, ["username", "password", "role", "balance"], accounts)
        print("Registrasi berhasil! Silakan login.")
    else:
        print("Username sudah digunakan. Gunakan username lain.")

def login():
    os.system("cls")
    print("+----------------------------+")
    print("|         Menu Login         |")
    print("+----------------------------+")
    username = input("Masukkan Username: ")
    password = pwinput.pwinput("Masukkan Password: ")
    accounts = read_csv(account_file)
    chance = 3
    countdown = 30

    while chance > 0:
        for account in accounts:
            if account["username"] == username and account["password"] == password:
                if account["role"].lower() == "admin":
                    print(Fore.RED + f"Login berhasil! Selamat datang, {username}" + Style.RESET_ALL)
                else:
                    print(Fore.GREEN + f"Login berhasil! Selamat datang, {username}" + Style.RESET_ALL)
                return account
            
        chance -= 1
        print(f"Username atau password salah. {chance} kesempatan tersedia")
        
        if chance == 0:
            for i in range(countdown, -1, -1):
                print(f"Tunggu {i} detik. sebelum bisa login lagi", end="\r")
                time.sleep(1)
            
            chance = 3  
            print("\nSilakan coba login kembali.\n")

        username = input("Masukkan Username: ")
        password = pwinput.pwinput("Masukkan Password: ")

def add_car():
    print("+----------------------------+")
    print("|         Tambah Mobil       |")
    print("+----------------------------+")
    try:
        car_name = input("Masukkan Nama Mobil: ")
        car_price = int(input("Harga Sewa per Hari: "))
        car_plate = input("Nomor Plat: ")
        stock = "tersedia"

        cars = read_csv(car_file)
        cars.append({"id": str(len(cars)+1), "nama": car_name, "harga": car_price, "no plat": car_plate, "status": stock})
        write_csv(car_file, ["id", "nama", "harga", "no plat", "status"], cars)
        update_ids(car_file)
        print("Mobil berhasil ditambahkan.")
    except ValueError:
        print("Input berupa angka, bukan huruf.")

def list_cars():
    print("════════Data Mobil PT Rental Laju Sejahtera══════════")
    cars = read_csv(car_file)
    if cars:
        display_table(cars, ["id", "nama", "harga", "no plat", "status"])
        sort_order = (input("Urutkan berdasarkan harga (1.termurah / 2. termahal) atau lewati (tekan Enter): "))
        if sort_order == "1":
            cars.sort(key=lambda x: int(x["harga"]))
        elif sort_order == "2":
            cars.sort(key=lambda x: int(x["harga"]), reverse=True)
        else :
            print("input tidak valid")
            return
        
        display_table(cars, ["id", "nama", "harga", "no plat", "status"])
    else:
        print("Belum ada data mobil.")
        

def update_car():
    print("+----------------------------+")
    print("|         Update Mobil       |")
    print("+----------------------------+")
    try:
        list_cars()
        car_id = input("Masukkan ID Mobil yang ingin diedit: ")
        edit_car = read_csv(car_file)
        car = next((c for c in edit_car if c["id"] == car_id), None)
        if car:
            car["nama"] = input("Masukkan nama mobil baru: ")
            car["harga"] = int(input("Masukkan harga baru: "))
            car["no plat"] = input("Masukkan plat baru: ")
            car["status"] = input("Masukkan status mobil: ")
            write_csv(car_file, ["id", "nama", "harga", "no plat", "status"], edit_car)
            print("Data mobil berhasil diperbarui.")
        else:
            print("Mobil tidak ditemukan.")
    except ValueError:
        print("Input berupa angka, bukan huruf.")

def delete_car():
    print("+----------------------------+")
    print("|         Hapus Mobil        |")
    print("+----------------------------+")
    list_cars()
    car_id = input("Masukkan ID Mobil yang ingin dihapus: ")
    cars = read_csv(car_file)
    cars = [car for car in cars if car["id"] != car_id]
    write_csv(car_file, ["id", "nama", "harga", "no plat", "status"], cars)
    update_ids(car_file)
    print("Mobil berhasil dihapus.")

def rent_car(user):
    print("+----------------------------+")
    print("|         Rental Mobil       |")
    print("+----------------------------+")

    transactions = read_csv(transaction_file)
    user_transactions = [t for t in transactions if t["username"] == user["username"]]

    if any(t["return_date"] == "" for t in user_transactions):
        print("Anda masih memiliki mobil yang belum dikembalikan.")
        return

    cars = read_csv(car_file)
    status_cars = [car for car in cars if car["status"] == "tersedia"]

    if not status_cars:
        print("Tidak ada mobil yang tersedia untuk disewa.")
        return

    display_table(status_cars, ["id", "nama", "harga", "no plat", "status"])
    search_query = input("Masukkan nama mobil yang ingin dicari (biarkan kosong jika tidak): ").lower()
    if search_query:
        status_cars = [car for car in status_cars if search_query in car["nama"].lower()]
    
    if not status_cars:
        print("Tidak ada mobil yang sesuai dengan pencarian.")
        return

    sort_order = input("Urutkan berdasarkan harga (asc/desc) atau lewati (tekan Enter): ").lower()
    if sort_order == "asc":
        status_cars.sort(key=lambda x: int(x["harga"]))
    elif sort_order == "desc":
        status_cars.sort(key=lambda x: int(x["harga"]), reverse=True)

    display_table(status_cars, ["id", "nama", "harga", "no plat", "status"])

    car_id = input("Masukkan ID Mobil yang ingin disewa: ")
    car = next((c for c in status_cars if c["id"] == car_id), None)

    if car:
        days = int(input("Berapa hari Anda ingin menyewa mobil? "))
        total_price = int(car["harga"]) * days

        if int(user["balance"]) >= total_price:
            user["balance"] = str(int(user["balance"]) - total_price)
            
            transaction_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            transactions.append({
                "username": user["username"],
                "car": car["nama"],
                "days": str(days),
                "total": str(total_price),
                "date": transaction_date,
                "plate": car["no plat"],
                "return_date": (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
            })
            write_csv(transaction_file, ["username", "car", "days", "total", "date", "plate", "return_date"], transactions)
            
            car["status"] = "tidak tersedia"
            write_csv(car_file, ["id", "nama", "harga", "no plat", "status"], cars)
            
            accounts = read_csv(account_file)
            for acc in accounts:
                if acc["username"] == user["username"]:
                    acc["balance"] = user["balance"]
                elif acc["username"] == "admin":
                    acc["balance"] = str(int(acc["balance"]) + total_price)
            write_csv(account_file, ["username", "password", "role", "balance"], accounts)

            print("Rental berhasil.")

            print("\n                     Rental Laju Sejahtera")
            print("   Jl. Sambaliung, Sempaja Selatan Samarinda Utara, Indonesia   ")
            print("                          Customer Service")
            print("================================================================")
            print(f"Nama Penyewa         : {user["username"]}")
            print(f"Merk mobil           : {car["nama"]}")
            print(f"Lama Sewa            : {days} hari")
            print(f"Tanggal diambil      : {transaction_date}")
            print(f"Tanggal dikembalikan : {datetime.now() + timedelta(days=days)}")
            print(f"Biaya Sewa           : Rp{total_price}")
            print(f"Total Transaksi      : Rp{total_price}")
            print(f"Saldo Penyewa        : Rp{user["balance"]}")
            print("================================================================")
            print("Terima kasih sudah bertransaksi dengan kami. Harap kembalikan tepat waktu")

        else:
            print("Saldo tidak mencukupi.")
    else:
        print("ID mobil tidak valid.")


def return_car(user):
    print("+----------------------------+")
    print("|      Kembalikan Mobil      |")
    print("+----------------------------+")
    transactions = read_csv(transaction_file)
    user_transactions = [t for t in transactions if t["username"] == user["username"] and t["return_date"] != ""]

    if not user_transactions:
        print("Tidak ada mobil yang perlu dikembalikan.")
        return

    display_table(user_transactions, ["username", "car", "plate", "days", "total", "date"])

    username = input("Masukkan nama peminjam: ")
    car_name = input("Masukkan nama mobil yang ingin dikembalikan: ")
    plate = input("Masukkan nomor plat mobil: ")

    transaction = next((t for t in user_transactions if t["username"] == username and t["car"] == car_name and t["plate"] == plate), None)

    if transaction:
        return_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        transaction["return_date"] = return_date
        updated_transactions = [t for t in transactions if not (t["username"] == username and t["car"] == car_name and t["plate"] == plate)]
        write_csv(transaction_file, ["username", "car", "days", "total", "date", "plate", "return_date"], updated_transactions)
        
        cars = read_csv(car_file)
        for car in cars:
            if car["nama"] == transaction["car"] and car["no plat"] == transaction["plate"]:
                car["status"] = "tersedia"
        write_csv(car_file, ["id", "nama", "harga", "no plat", "status"], cars)

        print(f"Mobil {transaction['car']} berhasil dikembalikan pada {return_date}")
    else:
        print("Mobil atau nomor plat tidak ditemukan.")


def view_transactions():
    print("+----------------------------+")
    print("|      Daftar Transaksi      |")
    print("+----------------------------+")
    transactions = read_csv(transaction_file)
    if transactions:
        display_table(transactions, ["username", "car", "days","total", "date","plate","return_date"])
    else:
        print("Belum ada data mobil.")

def view_user():
    print("+----------------------------+")
    print("|         Daftar Akun        |")
    print("+----------------------------+")
    accounts = read_csv(account_file)
    if accounts :
        display_table(accounts, ["username", "password", "role", "balance"])
    else :
        print("Belum ada data user")

def topup(user):
    print("+----------------------------+")
    print("|         Topup Saldo        |")
    print("+----------------------------+")

    voucher_data = []
    with open(voucher_file, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            voucher_data.append(row)

    account_data = read_csv(account_file)
    topup_saldo = input("Masukkan kode voucher untuk mengisi saldo: ")

    voucher_found = next((voucher for voucher in voucher_data if voucher["voucher_name"] == topup_saldo), None)

    if voucher_found:
        balance_to_add = int(voucher_found["balance"])

        for account in account_data:
            if account["username"] == user["username"]:
                account["balance"] = str(int(account["balance"]) + balance_to_add)
                user["balance"] = account["balance"]
                break

        with open(account_file, mode="w", newline="") as file:
            fieldnames = account_data[0].keys()
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(account_data)

        print(f"Saldo berhasil ditambahkan sebesar {balance_to_add}. Saldo terbaru Anda: Rp{user['balance']}.")
    else:
        print("Kode voucher tidak ditemukan atau tidak valid.")

def add_voucher():
    print("+----------------------------+")
    print("|       Daftar Voucher       |")
    print("+----------------------------+")
    with open(voucher_file, mode="r") as vf :
        voucher_name = input("Nama voucher: ")
        voucher_balance = input("Masukkan harga voucher: ")
        
        voucher = read_csv(voucher_file)
        voucher.append({"voucher_name": voucher_name, "balance": voucher_balance})
        write_csv(voucher_file, ["voucher_name", "balance"], voucher)
    print("voucher berhasil ditambahkan")


def main_menu():
    table = PrettyTable()
    table.field_names = ["Rental Laju Sejahtera"]
    table.add_row(["Login"])
    table.add_row(["Register"])
    table.add_row(["Exit"])
    print(table)
    return input("Silahkan ketik(Login/Register/Exit): ").lower()

def run():
    os.system("cls")
    try :
        while True:
            choice = main_menu()
            if choice == "login":
                user = login()
                if user:
                    if user["role"] == "admin":
                        admin_menu(user)
                    else:
                        user_menu(user)
            elif choice == "register":
                register()
            elif choice == "exit":
                print("Terima kasih telah menggunakan program ini")
                exit()
            else:
                print("Opsi tidak valid.")
    except KeyboardInterrupt :
        print("Program dihentikan secara paksa")
        
def admin_menu(user):
    while True:
        table = PrettyTable()
        table.field_names = ["No", "Menu Admin"]
        table.add_row(["1","Tambah Mobil"])
        table.add_row(["2","Lihat Daftar Mobil"])
        table.add_row(["3","Hapus Mobil"])
        table.add_row(["4","Lihat Transaksi Aktif"])
        table.add_row(["5","Edit Daftar Mobil"])
        table.add_row(["6","Lihat Daftar User"])
        table.add_row(["7","Tambah Voucher"])
        table.add_row(["8","Logout"])
        print(table)

        choice = input("Pilih opsi: ")
        if choice == "1":
            add_car()
        elif choice == "2":
            list_cars()
        elif choice == "3":
            delete_car()
        elif choice == "4":
            view_transactions()
        elif choice == "5":
            update_car()
        elif choice == "6":
            view_user()
        elif choice == "7":
            add_voucher()
        elif choice == "8": 
            run()
        else:
            print("Opsi tidak valid.")

def user_menu(user):
    while True:
        table = PrettyTable()
        table.field_names = ["No", "Menu User"]
        table.add_row(["1","Sewa Mobil"])
        table.add_row(["2","Kembalikan Mobil"])
        table.add_row(["3","Lihat Daftar Mobil"])
        table.add_row(["4","Lihat Saldo"])
        table.add_row(["5","Topup Saldo"])
        table.add_row(["6","Logout"])
        print(table)

        choice = input("Pilih opsi: ")
        if choice == "1":
            rent_car(user)
        elif choice == "2":
            return_car(user)
        elif choice == "3":
            list_cars()
        elif choice == "4":
            print(f"Saldo E-Money Anda: Rp{user['balance']}")
        elif choice == "5":
            topup(user)
        elif choice == "6":
            run()
        else:
            print("Opsi tidak valid.")

run()

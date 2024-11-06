import csv
from prettytable import PrettyTable
from prettytable import from_csv
import pwinput
from datetime import datetime
import re

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
        open(file, mode="w").close()
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
    table = PrettyTable(fieldnames)
    for row in data:
        table.add_row([row.get(field, "") for field in fieldnames])
    print(table)

def confirm_password():
    while True:
        password = pwinput.pwinput("Masukkan password: ")
        confirm_password = pwinput.pwinput("Konfirmasi password: ")
        if password == confirm_password:
            return password
        print("Password tidak sama, silahkan coba lagi")

def validate_name_input(prompt):
    while True:
        name = input(prompt)
        if re.match("^[A-Za-z ]+$", name):
            return name
        print("Input tidak valid. Harap masukkan huruf saja.")

def register():
    print("+----------------------------+")
    print("|        Menu Register       |")
    print("+----------------------------+")
    username = validate_name_input("Masukkan Username: ")
    password = confirm_password()
    role = "user"
    balance = "100000"

    accounts = read_csv(account_file)
    if any(account["username"] == username for account in accounts):
        print("Username sudah digunakan. Gunakan username lain.")
    else:
        accounts.append({"username": username, "password": password, "role": role, "balance": balance})
        write_csv(account_file, ["username", "password", "role", "balance"], accounts)
        print("Registrasi berhasil! Silakan login.")

def login():
    print("+----------------------------+")
    print("|         Menu Login         |")
    print("+----------------------------+")
    username = input("Masukkan Username: ")
    password = pwinput.pwinput("Masukkan Password: ")
    accounts = read_csv(account_file)

    for account in accounts:
        if account["username"] == username and account["password"] == password:
            print(f"Login berhasil! Selamat datang, {username}.")
            return account
    print("Username atau password salah.")
    return None

def add_car():
    print("+----------------------------+")
    print("|         Tambah Mobil       |")
    print("+----------------------------+")
    car_name = validate_name_input("Nama Mobil: ")
    car_price = input("Harga Sewa per Hari: ")
    car_plate = input("Nomor Plat: ")
    stock = input("Jumlah Stok: ")

    cars = read_csv(car_file)
    cars.append({"id": str(len(cars)+1), "name": car_name, "price": car_price, "plate": car_plate, "stock": stock})
    write_csv(car_file, ["id", "name", "price", "plate", "stock"], cars)
    print("Mobil berhasil ditambahkan.")

def list_cars():
    cars = read_csv(car_file)
    if cars:
        display_table(cars, ["id", "name", "price", "plate", "stock"])
    else:
        print("Belum ada data mobil.")

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
    available_cars = [car for car in cars if int(car["stock"]) > 0]
    if not available_cars:
        print("Tidak ada mobil yang tersedia untuk disewa.")
        return

    display_table(available_cars, ["id", "name", "price", "plate", "stock"])
    car_id = input("Masukkan ID Mobil yang ingin disewa: ")
    car = next((c for c in available_cars if c["id"] == car_id), None)

    if car:
        days = int(input("Berapa hari Anda ingin menyewa mobil? "))
        total_price = int(car["price"]) * days

        if int(user["balance"]) >= total_price:
            user["balance"] = str(int(user["balance"]) - total_price)
            transaction_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            transactions.append({
                "username": user["username"],
                "car": car["name"],
                "days": str(days),
                "total": str(total_price),
                "date": transaction_date,
                "plate": car["plate"],
                "return_date": ""
            })
            write_csv(transaction_file, ["username", "car", "days", "total", "date", "plate", "return_date"], transactions)
            
            car["stock"] = str(int(car["stock"]) - 1)
            write_csv(car_file, ["id", "name", "price", "plate", "stock"], cars)
            
            accounts = read_csv(account_file)
            for acc in accounts:
                if acc["username"] == user["username"]:
                    acc["balance"] = user["balance"]
            write_csv(account_file, ["username", "password", "role", "balance"], accounts)

            print("Rental berhasil.")
        else:
            print("Saldo tidak mencukupi.")
    else:
        print("ID mobil tidak valid.")

def return_car(user):
    print("+----------------------------+")
    print("|      Kembalikan Mobil      |")
    print("+----------------------------+")
    transactions = read_csv(transaction_file)
    user_transactions = [t for t in transactions if t["username"] == user["username"] and t["return_date"] == ""]

    if not user_transactions:
        print("Tidak ada mobil yang perlu dikembalikan.")
        return

    display_table(user_transactions, ["car", "plate", "days", "total", "date"])
    car_name = validate_name_input("Masukkan nama mobil yang ingin dikembalikan: ")
    plate = input("Masukkan nomor plat mobil: ")

    transaction = next((t for t in user_transactions if t["car"] == car_name and t["plate"] == plate), None)

    if transaction:
        return_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        transaction["return_date"] = return_date
        write_csv(transaction_file, ["username", "car", "days", "total", "date", "plate", "return_date"], transactions)
        
        cars = read_csv(car_file)
        for car in cars:
            if car["name"] == transaction["car"] and car["plate"] == transaction["plate"]:
                car["stock"] = str(int(car["stock"]) + 1)
        write_csv(car_file, ["id", "name", "price", "plate", "stock"], cars)

        print(f"Mobil {transaction['car']} berhasil dikembalikan pada {return_date}")
    else:
        print("Mobil atau nomor plat tidak ditemukan.")

def main_menu():
    table = PrettyTable()
    table.field_names = ["Rental Laju Sejahtera"]
    table.add_row(["Login"])
    table.add_row(["Register"])
    table.add_row(["Exit"])
    print(table)
    return input("Silahkan ketik(Login/Register/Exit): ").lower()

def run():
    try:
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
                break
            else:
                print("Opsi tidak valid.")
    except KeyboardInterrupt:
        print("Program dihentikan secara paksa")
        
def admin_menu(user):
    while True:
        table = PrettyTable()
        table.field_names = ["No", "Menu Admin"]
        table.add_row(["1","Tambah Mobil"])
        table.add_row(["2","Lihat Daftar Mobil"])
        table.add_row(["3","Hapus Mobil"])
        table.add_row(["4","Lihat Riwayat Transaksi"])
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
            print("Pilihan tidak tersedia")

def user_menu(user):
    while True:
        table = PrettyTable()
        table.field_names = ["No", "Menu User"]
        table.add_row(["1","Rental Mobil"])
        table.add_row(["2","Daftar Mobil"])
        table.add_row(["3","Kembalikan Mobil"])
        table.add_row(["4","Logout"])
        print(table)
        
        choice = input("Pilih opsi: ")
        if choice == "1":
            rent_car(user)
        elif choice == "2":
            list_cars()
        elif choice == "3":
            return_car(user)
        elif choice == "4":
            run()
        else:
            print("Pilihan tidak tersedia")

if __name__ == "__main__":
    run()

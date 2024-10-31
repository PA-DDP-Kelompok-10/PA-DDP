import csv
from prettytable import PrettyTable
import pwinput
from datetime import datetime

account_file = "accounts.csv"
car_file = "cars.csv"
transaction_file = "transactions.csv"

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

def register():
    print("+----------------------------+")
    print("|        Menu Register       |")
    print("+----------------------------+")
    username = input("Masukkan Username: ")
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
    car_name = input("Nama Mobil: ")
    car_price = input("Harga Sewa per Hari: ")
    
    cars = read_csv(car_file)
    cars.append({"id": str(len(cars)+1), "name": car_name, "price": car_price})
    write_csv(car_file, ["id", "name", "price"], cars)
    print("Mobil berhasil ditambahkan.")

def list_cars():
    cars = read_csv(car_file)
    if cars:
        display_table(cars, ["id", "name", "price"])
    else:
        print("Belum ada data mobil.")

def update_car():
    print("+----------------------------+")
    print("|         Update Mobil       |")
    print("+----------------------------+")
    list_cars()
    car_name = input("Masukkan nama mobil yang ingin diperbarui: ")
    new_car_name = input("Masukkan nama mobil baru: ")
    new_car_price = input("Masukkan harga baru: ")

    updated_rows = []
    found = False

    with open(car_file, mode="r") as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if row[0] == car_name:
                updated_rows.append([car_name, new_car_name, new_car_price])
                found = True
                print(f"Data {car_name} berhasil diperbarui.")
            else:
                updated_rows.append(row)

    if not found:
        print(f"Data dengan nama {new_car_name} tidak ditemukan.")
        return


    with open(car_file, mode="w", newline="") as file:
        csv_writer = csv.writer(file)
        csv_writer.writerows(updated_rows)

def delete_car():
    print("+----------------------------+")
    print("|         Hapus Mobil        |")
    print("+----------------------------+")
    list_cars()
    car_id = input("Masukkan ID Mobil yang ingin dihapus: ")
    cars = read_csv(car_file)
    cars = [car for car in cars if car["id"] != car_id]
    write_csv(car_file, ["id", "name", "price"], cars)
    print("Mobil berhasil dihapus.")

def rent_car(user):
    print("+----------------------------+")
    print("|         Rental Mobil       |")
    print("+----------------------------+")
    list_cars()
    car_id = input("Masukkan ID Mobil yang ingin disewa: ")
    cars = read_csv(car_file)
    car = next((c for c in cars if c["id"] == car_id), None)

    if car:
        days = int(input("Berapa hari Anda ingin menyewa mobil? "))
        total_price = int(car["price"]) * days

        if int(user["balance"]) >= total_price:
            user["balance"] = str(int(user["balance"]) - total_price)
            transaction_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            transactions = read_csv(transaction_file)
            transactions.append({
                "username": user["username"],
                "car": car["name"],
                "days": str(days),
                "total": str(total_price),
                "date": transaction_date
            })
            write_csv(transaction_file, ["username", "car", "days", "total", "date"], transactions)
            
            accounts = read_csv(account_file)
            for acc in accounts:
                if acc["username"] == user["username"]:
                    acc["balance"] = user["balance"]
            write_csv(account_file, ["username", "password", "role", "balance"], accounts)
            
            print(f"Transaksi berhasil! Total harga: Rp{total_price}.")
        else:
            print("Saldo tidak mencukupi.")
    else:
        print("ID mobil tidak valid.")

def return_car():
    print("+----------------------------+")
    print("|      Kembalikan Mobil      |")
    print("+----------------------------+")
    view_transactions()
    rentman = input("Masukkan nama peminjam mobil: ")
    transaction_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    transactions = read_csv(transaction_file)
    for transaction in transactions:
        if transaction["username"] == rentman:
            print(f"Mobil {transaction['car']} telah dikembalikan pada {transaction_date}")
            transactions.remove(transaction)
            write_csv(transaction_file, ["username", "car", "days", "total", "date"], transactions)
            break
    else:
        print("Nama peminjam mobil tidak ditemukan.")

def view_transactions():
    print("=== Riwayat Transaksi ===")
    transactions = read_csv(transaction_file)
    if transactions:
        display_table(transactions, ["username", "car", "days", "total", "date"])
    else:
        print("Belum ada transaksi.")

def view_user():
    print("+----------------------------+")
    print("|         Daftar Akun        |")
    print("+----------------------------+")
    accounts = read_csv(account_file)
    display_table(accounts, ["username", "password", "role", "balance"])

def view_transactions() :
    print("+----------------------------+")
    print("|      Daftar Transaksi      |")
    print("+----------------------------+")
    transactions = read_csv(transaction_file)
    display_table(transactions, ["username", "car", "days", "total", "date"])

def main_menu():
    table = PrettyTable()
    table.field_names = ["Sistem Manajemen Rental Mobil"]
    table.add_row(["Login"])
    table.add_row(["Register"])
    print(table)
    return input("Silahkan ketik(Login/Register): ").lower()

def run():
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
        else:
            print("Opsi tidak valid.")

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
        table.add_row(["7","Logout"])
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
        table.add_row(["5","Logout"])
        print(table)

        choice = input("Pilih opsi: ")
        if choice == "1":
            rent_car(user)
        elif choice == "2":
            return_car()
        elif choice == "3":
            list_cars()
        elif choice == "4":
            print(f"Saldo E-Money Anda: Rp{user['balance']}")
        elif choice == "5":
            run()
        else:
            print("Opsi tidak valid.")

run()
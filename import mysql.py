import mysql.connector
import tkinter as tk
from tkinter import messagebox #used for message boxes using tkinter
from datetime import date

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",   # <-- Put your MySQL password here
    database="airlinedb"
)
cur = conn.cursor()

#  ADMIN LOGIN
print("==========================================")
print("   AIRLINE RESERVATION SYSTEM (ADMIN)     ")
print("==========================================")
username = input("Enter Admin Username: ").strip()
password = input("Enter Admin Password: ").strip()

if username != "admin" or password != "1234":
    print("\n[!] Invalid Username or Password. Access Denied.")
    cur.close()
    conn.close()
    raise SystemExit
elif username =="admin" and password == "1234":
    print("\nLogin Successful! Welcome, Admin.")

# MAIN ADMIN CONSOLE MENU LOOP

while True:
    print("\n==========================================")
    print("            ADMIN MAIN MENU               ")
    print("==========================================")
    print("1. View Available Flights")
    print("2. Search Flights (by source, destination, date)")
    print("3. Book Ticket for Passenger (opens Tkinter GUI)")
    print("4. Cancel Reservation")
    print("5. View Users' Bookings")
    print("6. Manage Flights (Add / Update / Delete flights)")
    print("7. Exit")
    print("==========================================")

    choice = input("Enter your choice (1-7): ").strip()

# OPTION 1: VIEW AVAILABLE FLIGHTS
    if choice == "1":
        cur.execute("SELECT * FROM flights ORDER BY date, departure_time")
        rows = cur.fetchall()

        print("\n=== AVAILABLE FLIGHTS ===")
        if len(rows) == 0:
            print("No flights found.")
        else:
            print("(Flight ID, Airline, Source, Destination, Dep, Arr, Price, Total Seats, Avail Seats, Date)")
            for r in rows:
                print(r)

# OPTION 2: SEARCHING FLIGHTS
    elif choice == "2":
        print("\n=== SEARCH FLIGHTS ===")
        src = input("Enter Source City: ").strip()
        dest = input("Enter Destination City: ").strip()
        f_date = input("Enter Date (YYYY-MM-DD): ").strip()

        sql = """
            SELECT * FROM flights
            WHERE LOWER(source) = LOWER(%s)
              AND LOWER(destination) = LOWER(%s)
              AND date = %s
        """
        cur.execute(sql, (src, dest, f_date))
        rows = cur.fetchall()

        if len(rows) == 0:
            print("\nNo matching flights found.")
        else:
            print("\n" + "-" * 95)
            print(f"{'Flight ID':<10} {'Airline':<14} {'From':<12} {'To':<12} "
                  f"{'Date':<12} {'Dep':<7} {'Arr':<7} {'Price':<9} {'Avail/Total'}")
            print("-" * 95)
            for r in rows:
                print(r[0], "|", r[1], "|", r[2], "->", r[3], "|", r[9], "|", r[4], "-", r[5], "| Rs.", r[6], "|", r[8], "/", r[7])
            print("-" * 95)
# OPTION 3: BOOK TICKET FOR PASSENGER (TKINTER GUI SEAT MAP & CHECKOUT)  
    elif choice == "3":
        cur.execute("SELECT * FROM flights ORDER BY date, departure_time")
        rows = cur.fetchall()

        print("\n=== SELECT A FLIGHT TO BOOK ===")
        print("-" * 95)
        print(f"{'Flight ID':<10} {'Airline':<14} {'From':<12} {'To':<12} "
              f"{'Date':<12} {'Dep':<7} {'Arr':<7} {'Price':<9} {'Avail/Total'}")
        print("-" * 95)
        for r in rows:
            print(r[0], "|", r[1], "|", r[2], "->", r[3], "|", r[9], "|", r[4], "-", r[5], "| Rs.", r[6], "|", r[8], "/", r[7])
        print("-" * 95)

        flight_id = input("\nEnter Flight ID to book ticket: ").strip().upper()
        if flight_id == "":
            continue

        cur.execute("SELECT * FROM flights WHERE flight_id = %s", (flight_id,))
        flight = cur.fetchone()

        if flight is None:
            print("[!] Flight ID not found.")
            continue

        if flight[8] <= 0:
            print("[!] Sorry, no seats are available on this flight.")
            continue

        airline = flight[1]
        source = flight[2]
        destination = flight[3]
        price_per_seat = float(flight[6])
        total_seats = int(flight[7])
        flight_date = flight[9]

        # Fetch already booked seats for this flight
        cur.execute(
            "SELECT seat_numbers FROM bookings WHERE flight_id = %s AND status = 'Confirmed'",
            (flight_id,)
        )
        booking_records = cur.fetchall()
        booked_seats = []
        for rec in booking_records:
            if rec[0]:
                for s in rec[0].split(","):
                    booked_seats.append(s.strip())

        print("Opening Tkinter Seat Selection Window...")

        # --- TKINTER GUI WINDOW ---
        root = tk.Tk()
        root.title("Seat Selection - " + flight_id)
        root.geometry("420x560")
        root.config(bg="#f8fafc")

        name_var = tk.StringVar(root)
        email_var = tk.StringVar(root)
        confirm_var = tk.IntVar(root, 0)
        seat_vars = {}

        # Header & Legend
        tk.Label(
            root,
            text=f"{airline} ({flight_id})  •  {source} to {destination}\nDate: {flight_date}  |  Rs. {price_per_seat:.0f} per seat",
            font=("Arial", 11, "bold"), bg="#1e293b", fg="white", pady=12
        ).pack(fill="x")

        tk.Label(
            root, text="Green: Available   |   Blue: Selected   |   Red: Booked",
            font=("Arial", 9, "bold"), bg="#e2e8f0", fg="#334155", pady=5
        ).pack(fill="x")

        # Seat Map Grid (8 Rows x 4 Columns: A, B, [Aisle], C, D)
        grid = tk.Frame(root, bg="#f8fafc", pady=12)
        grid.pack()

        cols = ["A", "B", "C", "D"]
        for r in range(1, 9):
            for c in range(4):
                seat_no = str(r) + cols[c]
                col_pos = c if c < 2 else c + 1

                if seat_no in booked_seats:
                    tk.Button(
                        grid, text=seat_no, width=5, bg="#ef4444", fg="white",
                        font=("Arial", 9, "bold"), relief="flat", state="disabled"
                    ).grid(row=r, column=col_pos, padx=4, pady=3)
                else:
                    var = tk.IntVar(root, 0)
                    seat_vars[seat_no] = var
                    tk.Checkbutton(
                        grid, text=seat_no, variable=var, indicatoron=0, width=5,
                        font=("Arial", 9, "bold"), relief="flat",
                        bg="#22c55e", fg="white", selectcolor="#2563eb",
                        activebackground="#2563eb", activeforeground="white"
                    ).grid(row=r, column=col_pos, padx=4, pady=3)

            tk.Label(grid, text="   ", bg="#f8fafc").grid(row=r, column=2)

        # Passenger Details
        tk.Label(root, text="Passenger Name", font=("Arial", 9, "bold"), bg="#f8fafc", fg="#334155").pack()
        tk.Entry(root, textvariable=name_var, width=30, font=("Arial", 10), justify="center").pack(pady=3)

        tk.Label(root, text="Passenger Email", font=("Arial", 9, "bold"), bg="#f8fafc", fg="#334155").pack()
        tk.Entry(root, textvariable=email_var, width=30, font=("Arial", 10), justify="center").pack(pady=3)

        # Buttons
        tk.Button(
            root, text="Confirm Booking", width=22, bg="#16a34a", fg="white",
            font=("Arial", 10, "bold"), relief="flat", pady=5,
            command=lambda: [confirm_var.set(1), root.destroy()]
        ).pack(pady=(12, 4))

        tk.Button(
            root, text="Cancel", width=22, bg="#94a3b8", fg="white",
            font=("Arial", 9, "bold"), relief="flat",
            command=root.destroy
        ).pack()

        root.mainloop()

        # --- SAVE BOOKING TO MYSQL AFTER GUI CLOSES ---
        if confirm_var.get() == 1:
            selected_seats = []
            for s_no, s_var in seat_vars.items():
                if s_var.get() == 1:
                    selected_seats.append(s_no)

            passenger_name = name_var.get().strip()
            passenger_email = email_var.get().strip()

            if len(selected_seats) == 0:
                print("\n[!] Booking failed: Please select at least one seat.")
            elif passenger_name == "" or passenger_email == "":
                print("\n[!] Booking failed: Passenger Name and Email cannot be empty.")
            else:
                seat_str = ", ".join(selected_seats)
                total_fare = len(selected_seats) * price_per_seat
                today_str = str(date.today())

                insert_sql = """
                    INSERT INTO bookings
                    (flight_id, passenger_name, passenger_email, seat_numbers, total_fare, booking_date, status)
                    VALUES (%s, %s, %s, %s, %s, %s, 'Confirmed')
                """
                cur.execute(
                    insert_sql,
                    (flight_id, passenger_name, passenger_email, seat_str, total_fare, today_str)
                )

                update_sql = """
                    UPDATE flights
                    SET available_seats = available_seats - %s
                    WHERE flight_id = %s
                """
                cur.execute(update_sql, (len(selected_seats), flight_id))
                conn.commit()

                booking_id = cur.lastrowid

                # Show popup message box
                msg_win = tk.Tk()
                msg_win.withdraw()
                messagebox.showinfo(
                    "Booking Confirmed",
                    f"Booking Successful!\n\n"
                    f"Booking ID: {booking_id}\n"
                    f"Passenger: {passenger_name}\n"
                    f"Seats: {seat_str}\n"
                    f"Total Fare: Rs. {total_fare:.0f}"
                )
                msg_win.destroy()

                print(f"\n[SUCCESS] Booking ID {booking_id} confirmed for {passenger_name}!")
                print(f"          Seats: {seat_str} | Total Fare: Rs. {total_fare:.0f}")
        else:
            print("\n[INFO] Booking cancelled.") 
# OPTION 4: CANCEL RESERVATION     
    elif choice == "4":
        cur.execute("SELECT * FROM bookings ORDER BY booking_id DESC")
        rows = cur.fetchall()

        print("\n=== ALL PASSENGER BOOKINGS ===")
        if len(rows) == 0:
            print("No bookings found.")
            continue

        print("-" * 100)
        print("ID | Flight | Passenger Name | Email | Seats | Fare | Date | Status")
        print("---------------------------------------------------------------------")
        for b in rows:
            print(b[0], "|", b[1], "|", b[2], "|", b[3], "|", b[4], "| Rs.", b[5], "|", b[6], "|", b[7])
        print("-" * 100)

        b_id_str = input("\nEnter Booking ID to cancel: ").strip()
        if not b_id_str.isdigit():
            print("[!] Invalid Booking ID.")
            continue

        b_id = int(b_id_str)
        cur.execute("SELECT flight_id, seat_numbers, status FROM bookings WHERE booking_id = %s", (b_id,))
        record = cur.fetchone()

        if record is None:
            print("[!] Booking ID not found.")
        elif record[2] == "Cancelled":
            print("[!] This booking is already cancelled.")
        else:
            f_id = record[0]
            seat_list = record[1].split(",")
            num_seats = len(seat_list)

            cur.execute("UPDATE bookings SET status = 'Cancelled' WHERE booking_id = %s", (b_id,))
            cur.execute(
                "UPDATE flights SET available_seats = available_seats + %s WHERE flight_id = %s",
                (num_seats, f_id)
            )
            conn.commit()
            print(f"[SUCCESS] Booking ID {b_id} cancelled! {num_seats} seat(s) restored to flight {f_id}.")

# OPTION 5: VIEW USERS' BOOKINGS
    elif choice == "5":
        cur.execute("SELECT * FROM bookings ORDER BY booking_id DESC")
        rows = cur.fetchall()

        print("\n=== ALL PASSENGER BOOKINGS ===")
        if len(rows) == 0:
            print("No bookings found.")
        else:
            print("-" * 100)
            print("ID | Flight | Passenger Name | Email | Seats | Fare | Date | Status")
            print("---------------------------------------------------------------------")
            for b in rows:
                print(b[0], "|", b[1], "|", b[2], "|", b[3], "|", b[4], "| Rs.", b[5], "|", b[6], "|", b[7])
            print("-" * 100)
# OPTION 6: MANAGE FLIGHTS (ADD / UPDATE / DELETE)
    elif choice == "6":
        while True:
            print("\n--- MANAGE FLIGHTS MENU ---")
            print("1. Add New Flight")
            print("2. Update Flight Price / Time / Date")
            print("3. Delete Flight")
            print("4. Back to Main Menu")

            sub_ch = input("Enter choice (1-4): ").strip()

            if sub_ch == "1":
                flight_id = input("Enter Flight ID (e.g. AI-205): ").strip().upper()
                airline = input("Enter Airline Name: ").strip()
                source = input("Enter Source City: ").strip()
                destination = input("Enter Destination City: ").strip()
                dep_time = input("Enter Departure Time (HH:MM): ").strip()
                arr_time = input("Enter Arrival Time (HH:MM): ").strip()
                f_date = input("Enter Flight Date (YYYY-MM-DD): ").strip()
                price = float(input("Enter Ticket Price: ").strip())
                total_seats = int(input("Enter Total Seats (e.g. 32): ").strip())

                sql = """
                    INSERT INTO flights
                    (flight_id, airline, source, destination, departure_time,
                     arrival_time, price, total_seats, available_seats, date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cur.execute(sql, (
                    flight_id, airline, source, destination, dep_time,
                    arr_time, price, total_seats, total_seats, f_date
                ))
                conn.commit()
                print(f"[SUCCESS] Flight {flight_id} added successfully!")

            elif sub_ch == "2":
                flight_id = input("\nEnter Flight ID to Update: ").strip().upper()
                dep_time = input("Enter New Departure Time (HH:MM): ").strip()
                arr_time = input("Enter New Arrival Time (HH:MM): ").strip()
                f_date = input("Enter New Flight Date (YYYY-MM-DD): ").strip()
                price = float(input("Enter New Ticket Price: ").strip())

                sql = """
                    UPDATE flights
                    SET departure_time = %s, arrival_time = %s, date = %s, price = %s
                    WHERE flight_id = %s
                """
                cur.execute(sql, (dep_time, arr_time, f_date, price, flight_id))
                conn.commit()
                print(f"[SUCCESS] Flight {flight_id} updated!")

            elif sub_ch == "3":
                flight_id = input("\nEnter Flight ID to Delete: ").strip().upper()
                cur.execute("DELETE FROM flights WHERE flight_id = %s", (flight_id,))
                conn.commit()
                print(f"[SUCCESS] Flight {flight_id} deleted!")

            elif sub_ch == "4":
                break
            else:
                print("[!] Invalid choice. Please enter 1 to 4.")
# OPTION 7: EXIT
    elif choice == "7":
        print("\nThank you for using the Airline Reservation System. Goodbye!")
        cur.close()
        conn.close()
        break

    else:
        print("\n[!] Invalid choice! Please enter a number between 1 and 7.")
import streamlit as st
import sqlite3
import pandas as pd

# Database Setup
conn = sqlite3.connect('travel_website.db', check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS packages
             (id INTEGER PRIMARY KEY AUTOINCREMENT, destination TEXT, duration TEXT, price REAL, category TEXT, image_url TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS bookings
             (id INTEGER PRIMARY KEY AUTOINCREMENT, customer_name TEXT, phone TEXT, package_id INTEGER, status TEXT)''')

# Initial Sample Data
if c.execute("SELECT COUNT(*) FROM packages").fetchone()[0] == 0:
    sample_data = [
        ("Goa Beach Paradise", "4 Days / 3 Nights", 12500.0, "Beach", "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2"),
        ("Manali Mountain Escape", "5 Days / 4 Nights", 15000.0, "Hill Station", "https://images.unsplash.com/photo-1626621341517-bbf3d9990a23"),
        ("Kerala Backwaters Tour", "3 Days / 2 Nights", 9800.0, "Nature", "https://images.unsplash.com/photo-1602216056096-3b40cc0c9944")
    ]
    c.executemany("INSERT INTO packages (destination, duration, price, category, image_url) VALUES (?, ?, ?, ?, ?)", sample_data)
    conn.commit()

# Page Setup
st.set_page_config(page_title="Incredible Tours - Travel & Tourism Website", layout="wide", page_icon="🌴")

# Header Section
st.markdown("<h1 style='text-align: center;'>🌍 Incredible Tours & Travels</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Explore the best holiday destinations around the world!</p>", unsafe_allow_html=True)
st.divider()

menu = ["🏠 Home & Packages", "✈️ Book A Tour", "📋 Customer Bookings", "⚙️️ Admin Control"]
choice = st.sidebar.selectbox("Navigation Menu", menu)

# 1. Home / Packages View
if choice == "🏠 Home & Packages":
    st.subheader("🌟 Featured Holiday Destinations")
    df_pkg = pd.read_sql_query("SELECT * FROM packages", conn)
    
    if not df_pkg.empty:
        cols = st.columns(3)
        for idx, row in df_pkg.iterrows():
            with cols[idx % 3]:
                st.image(row['image_url'], use_container_width=True)
                st.markdown(f"### {row['destination']}")
                st.write(f"⏱️ **Duration:** {row['duration']}")
                st.write(f"🏷️ **Category:** {row['category']}")
                st.markdown(f"### ₹{row['price']:,.2f}")
                st.divider()

# 2. Tour Booking Page
elif choice == "✈️ Book A Tour":
    st.subheader("📝 Reserve Your Trip")
    pkgs = c.execute("SELECT id, destination, price FROM packages").fetchall()
    
    if pkgs:
        pkg_dict = {f"{p[1]} - ₹{p[2]:,.2f}": p[0] for p in pkgs}
        
        with st.form("booking_form"):
            name = st.text_input("Full Name")
            phone = st.text_input("Mobile Number")
            selected_pkg = st.selectbox("Select Tour Destination", list(pkg_dict.keys()))
            submitted = st.form_submit_button("Confirm & Reserve Seat")
            
            if submitted:
                if name and phone:
                    p_id = pkg_dict[selected_pkg]
                    c.execute("INSERT INTO bookings (customer_name, phone, package_id, status) VALUES (?, ?, ?, ?)",
                              (name, phone, p_id, "Confirmed"))
                    conn.commit()
                    st.balloons()
                    st.success(f"🎉 Thank you {name}! Your booking has been successfully recorded.")
                else:
                    st.error("Please fill all contact details.")

# 3. View Bookings (Track Status)
elif choice == "📋 Customer Bookings":
    st.subheader("📌 Booking Records & Status")
    query = '''
        SELECT bookings.id AS [Booking ID], bookings.customer_name AS [Customer Name], 
               bookings.phone AS [Phone], packages.destination AS [Destination], 
               packages.price AS [Amount], bookings.status AS [Status]
        FROM bookings 
        JOIN packages ON bookings.package_id = packages.id
    '''
    df_book = pd.read_sql_query(query, conn)
    st.dataframe(df_book, use_container_width=True)

# 4. Admin Panel
elif choice == "⚙️ Admin Control":
    st.subheader("🛠️ Add New Tour Destination")
    
    dest = st.text_input("Destination Name")
    duration = st.text_input("Duration (e.g. 5 Days / 4 Nights)")
    category = st.selectbox("Category", ["Beach", "Hill Station", "Heritage", "Adventure", "International"])
    price = st.number_input("Package Price (₹)", min_value=1000.0, step=500.0)
    image_url = st.text_input("Image URL", "https://images.unsplash.com/photo-1507525428034-b723cf961d3e")
    
    if st.button("Publish Tour Package"):
        if dest and duration:
            c.execute("INSERT INTO packages (destination, duration, price, category, image_url) VALUES (?, ?, ?, ?, ?)",
                      (dest, duration, price, category, image_url))
            conn.commit()
            st.success("New package published on website successfully!")

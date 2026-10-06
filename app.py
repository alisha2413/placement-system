import streamlit as st
import sqlite3
import pandas as pd

# Database Setup
conn = sqlite3.connect('placement.db', check_same_thread=False)
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS students
             (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT, dept TEXT, cgpa REAL, status TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS companies
             (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, role TEXT, package TEXT, min_cgpa REAL)''')

c.execute('''CREATE TABLE IF NOT EXISTS applications
             (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INTEGER, company_id INTEGER, status TEXT)''')
conn.commit()

# Page Layout
st.set_page_config(page_title="College Placement Management System", layout="wide")
st.title("🎓 College Placement Management System")

menu = ["Dashboard", "Student Management", "Company Management", "Applications"]
choice = st.sidebar.selectbox("Navigation", menu)

if choice == "Dashboard":
    st.subheader("📊 System Overview")
    col1, col2, col3 = st.columns(3)
    
    total_students = c.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    total_companies = c.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
    placed_students = c.execute("SELECT COUNT(*) FROM students WHERE status='Placed'").fetchone()[0]
    
    col1.metric("Total Students", total_students)
    col2.metric("Registered Companies", total_companies)
    col3.metric("Students Placed", placed_students)

elif choice == "Student Management":
    st.subheader("👨‍🎓 Student Management")
    tab1, tab2 = st.tabs(["Add Student", "View Students"])
    
    with tab1:
        name = st.text_input("Student Name")
        email = st.text_input("Email")
        dept = st.selectbox("Department", ["CSE", "ECE", "ME", "CE", "EEE"])
        cgpa = st.number_input("CGPA", min_value=0.0, max_value=10.0, step=0.1)
        if st.button("Add Student"):
            c.execute("INSERT INTO students (name, email, dept, cgpa, status) VALUES (?, ?, ?, ?, ?)",
                      (name, email, dept, cgpa, "Unplaced"))
            conn.commit()
            st.success("Student Added Successfully!")
            
    with tab2:
        df = pd.read_sql_query("SELECT * FROM students", conn)
        st.dataframe(df, use_container_width=True)

elif choice == "Company Management":
    st.subheader("🏢 Company Management")
    tab1, tab2 = st.tabs(["Add Company", "View Companies"])
    
    with tab1:
        cname = st.text_input("Company Name")
        role = st.text_input("Role")
        package = st.text_input("Package (e.g., 6 LPA)")
        min_cgpa = st.number_input("Minimum CGPA Required", min_value=0.0, max_value=10.0, step=0.1)
        if st.button("Add Company"):
            c.execute("INSERT INTO companies (name, role, package, min_cgpa) VALUES (?, ?, ?, ?)",
                      (cname, role, package, min_cgpa))
            conn.commit()
            st.success("Company Added Successfully!")
            
    with tab2:
        df = pd.read_sql_query("SELECT * FROM companies", conn)
        st.dataframe(df, use_container_width=True)

elif choice == "Applications":
    st.subheader("📝 Apply & Track Applications")
    
    students = c.execute("SELECT id, name FROM students").fetchall()
    companies = c.execute("SELECT id, name FROM companies").fetchall()
    
    student_dict = {s[1]: s[0] for s in students}
    company_dict = {comp[1]: comp[0] for comp in companies}
    
    if student_dict and company_dict:
        selected_student = st.selectbox("Select Student", list(student_dict.keys()))
        selected_company = st.selectbox("Select Company", list(company_dict.keys()))
        
        if st.button("Submit Application"):
            s_id = student_dict[selected_student]
            c_id = company_dict[selected_company]
            c.execute("INSERT INTO applications (student_id, company_id, status) VALUES (?, ?, ?)",
                      (s_id, c_id, "Applied"))
            conn.commit()
            st.success("Application Submitted!")
    else:
        st.info("Please add students and companies first.")
        
    st.markdown("---")
    st.write("### All Applications")
    query = '''
        SELECT applications.id, students.name AS Student, companies.name AS Company, applications.status 
        FROM applications 
        JOIN students ON applications.student_id = students.id 
        JOIN companies ON applications.company_id = companies.id
    '''
    df_app = pd.read_sql_query(query, conn)
    st.dataframe(df_app, use_container_width=True)

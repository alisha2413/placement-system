import sqlite3
import datetime
import streamlit as st

# ==========================================
# 1. DATABASE SETUP & INITIALIZATION
# ==========================================
DB_FILE = "placement_portal.db"

def get_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT CHECK(role IN ('Student', 'Company', 'Admin')) NOT NULL
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Students (
        student_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        branch TEXT NOT NULL,
        course TEXT NOT NULL,
        semester INTEGER NOT NULL,
        cgpa REAL NOT NULL,
        skills TEXT,
        certifications TEXT,
        projects TEXT,
        FOREIGN KEY(student_id) REFERENCES Users(user_id) ON DELETE CASCADE
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Companies (
        company_id INTEGER PRIMARY KEY,
        company_name TEXT NOT NULL,
        website TEXT,
        contact_email TEXT NOT NULL,
        status TEXT CHECK(status IN ('Pending', 'Approved', 'Rejected')) DEFAULT 'Pending',
        FOREIGN KEY(company_id) REFERENCES Users(user_id) ON DELETE CASCADE
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS PlacementDrives (
        drive_id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER NOT NULL,
        job_role TEXT NOT NULL,
        package_lpa REAL NOT NULL,
        location TEXT NOT NULL,
        required_skills TEXT NOT NULL,
        min_cgpa REAL NOT NULL,
        eligible_branches TEXT NOT NULL,
        deadline DATE NOT NULL,
        selection_process TEXT NOT NULL,
        status TEXT CHECK(status IN ('Upcoming', 'Applications Open', 'Shortlisted', 'Interview Scheduled', 'Completed')) DEFAULT 'Applications Open',
        FOREIGN KEY(company_id) REFERENCES Companies(company_id) ON DELETE CASCADE
    );
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Applications (
        application_id INTEGER PRIMARY KEY AUTOINCREMENT,
        drive_id INTEGER NOT NULL,
        student_id INTEGER NOT NULL,
        applied_date DATE NOT NULL,
        status TEXT CHECK(status IN ('Applied', 'Shortlisted', 'Test/Interview', 'Selected', 'Rejected')) DEFAULT 'Applied',
        interview_date TEXT,
        FOREIGN KEY(drive_id) REFERENCES PlacementDrives(drive_id) ON DELETE CASCADE,
        FOREIGN KEY(student_id) REFERENCES Students(student_id) ON DELETE CASCADE,
        UNIQUE(drive_id, student_id)
    );
    ''')

    conn.commit()

    # Seed Demo Data if empty
    cursor.execute("SELECT COUNT(*) FROM Users")
    if cursor.fetchone()[0] == 0:
        seed_demo_data(cursor)
        conn.commit()

    conn.close()

def seed_demo_data(cursor):
    # 1. Admin
    cursor.execute("INSERT INTO Users (username, password, role) VALUES ('admin', 'admin123', 'Admin')")

    # 2. Companies
    companies_data = [
        ('google', 'pass123', 'Google Inc.', 'https://google.com', 'careers@google.com', 'Approved'),
        ('microsoft', 'pass123', 'Microsoft', 'https://microsoft.com', 'jobs@microsoft.com', 'Approved'),
        ('tcs', 'pass123', 'Tata Consultancy Services', 'https://tcs.com', 'campus@tcs.com', 'Approved'),
        ('amazon', 'pass123', 'Amazon', 'https://amazon.com', 'hr@amazon.com', 'Approved'),
        ('infosys', 'pass123', 'Infosys', 'https://infosys.com', 'recruitment@infosys.com', 'Pending')
    ]
    for un, pw, name, web, email, st_val in companies_data:
        cursor.execute("INSERT INTO Users (username, password, role) VALUES (?, ?, 'Company')", (un, pw))
        c_id = cursor.lastrowid
        cursor.execute("INSERT INTO Companies (company_id, company_name, website, contact_email, status) VALUES (?, ?, ?, ?, ?)",
                       (c_id, name, web, email, st_val))

    # 3. Students
    students_data = [
        ('alex', 'pass123', 'Alex Morgan', 'alex@college.edu', 'CSE', 'B.Tech', 8, 8.8, 'Python, React, SQL', 'AWS Certified', 'E-commerce App'),
        ('priya', 'pass123', 'Priya Sharma', 'priya@college.edu', 'CSE', 'B.Tech', 8, 9.2, 'Java, Spring Boot, MySQL', 'Oracle Java Certified', 'Banking System'),
        ('rahul', 'pass123', 'Rahul Verma', 'rahul@college.edu', 'ECE', 'B.Tech', 8, 7.5, 'C++, Embedded Systems, MATLAB', 'IoT Dev', 'Smart Home System'),
        ('sanya', 'pass123', 'Sanya Gupta', 'sanya@college.edu', 'IT', 'B.Tech', 8, 8.1, 'Python, Data Analytics, Tableau', 'Google Data Cert', 'Sales Dashboard'),
        ('david', 'pass123', 'David Miller', 'david@college.edu', 'MECH', 'B.Tech', 8, 6.8, 'AutoCAD, SolidWorks, Python', 'Lean Six Sigma', 'Solar Vehicle'),
        ('ananya', 'pass123', 'Ananya Roy', 'ananya@college.edu', 'CSE', 'B.Tech', 8, 9.5, 'Python, PyTorch, C++', 'Deep Learning Spec', 'Object Detector'),
        ('rohit', 'pass123', 'Rohit Kumar', 'rohit@college.edu', 'EEE', 'B.Tech', 8, 7.2, 'MATLAB, Power Systems, C', 'PLC Certification', 'Grid Monitor'),
        ('sneha', 'pass123', 'Sneha Patel', 'sneha@college.edu', 'IT', 'B.Tech', 8, 8.4, 'HTML/CSS, JS, Node.js', 'Full Stack Cert', 'Blog Engine'),
        ('vikram', 'pass123', 'Vikram Singh', 'vikram@college.edu', 'CSE', 'B.Tech', 8, 7.9, 'Java, Android, Firebase', 'Android Dev', 'Fitness App'),
        ('meera', 'pass123', 'Meera Nair', 'meera@college.edu', 'ECE', 'B.Tech', 8, 8.6, 'Python, VLSI, Verilog', 'FPGA Design', 'Digital Clock')
    ]
    for un, pw, name, email, branch, course, sem, cgpa, sk, cert, proj in students_data:
        cursor.execute("INSERT INTO Users (username, password, role) VALUES (?, ?, 'Student')", (un, pw))
        s_id = cursor.lastrowid
        cursor.execute("INSERT INTO Students (student_id, name, email, branch, course, semester, cgpa, skills, certifications, projects) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (s_id, name, email, branch, course, sem, cgpa, sk, cert, proj))

    # 4. Placement Drives
    drives_data = [
        (2, 'Software Engineer', 18.0, 'Bengaluru', 'Python, SQL, DSA', 8.0, 'CSE, IT', '2026-11-15', 'Online Test -> Tech Interview -> HR', 'Applications Open'),
        (3, 'SDE-1', 24.0, 'Hyderabad', 'Java, C++, DSA', 8.5, 'CSE, IT, ECE', '2026-11-20', 'Coding Round -> 2x Tech Interview', 'Applications Open'),
        (4, 'Systems Engineer', 7.0, 'Pune', 'C, C++, Java, SQL', 6.5, 'CSE, IT, ECE, EEE, MECH', '2026-10-30', 'Aptitude Test -> Interview', 'Applications Open'),
        (5, 'Cloud Developer', 20.0, 'Bengaluru', 'AWS, Python, Linux', 7.5, 'CSE, IT, ECE', '2026-12-01', 'Online Assessment -> Tech Round', 'Upcoming'),
        (2, 'Data Analyst', 12.0, 'Gurugram', 'Python, SQL, Tableau', 7.0, 'CSE, IT, ECE', '2026-10-15', 'Aptitude -> Data Assessment -> HR', 'Interview Scheduled')
    ]
    for cid, role, pkg, loc, sk, min_c, br, dead, proc, st_val in drives_data:
        cursor.execute('''INSERT INTO PlacementDrives 
            (company_id, job_role, package_lpa, location, required_skills, min_cgpa, eligible_branches, deadline, selection_process, status) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (cid, role, pkg, loc, sk, min_c, br, dead, proc, st_val))

    # 5. Applications
    apps_data = [
        (1, 7, '2026-10-01', 'Applied', None),         # Alex -> Google SE
        (1, 8, '2026-10-01', 'Shortlisted', None),     # Priya -> Google SE
        (1, 12, '2026-10-02', 'Selected', None),       # Ananya -> Google SE
        (2, 8, '2026-10-03', 'Applied', None),         # Priya -> Microsoft SDE
        (2, 12, '2026-10-03', 'Test/Interview', '2026-10-25 10:00 AM'), # Ananya -> Microsoft SDE
        (3, 9, '2026-10-04', 'Applied', None),         # Rahul -> TCS Systems
        (3, 11, '2026-10-04', 'Applied', None),        # David -> TCS Systems
        (5, 10, '2026-10-01', 'Test/Interview', '2026-10-20 02:00 PM'), # Sanya -> Google Data Analyst
        (5, 16, '2026-10-01', 'Selected', '2026-10-18 11:00 AM')  # Meera -> Google Data Analyst
    ]
    for dr_id, st_id, app_dt, app_st, int_dt in apps_data:
        cursor.execute("INSERT INTO Applications (drive_id, student_id, applied_date, status, interview_date) VALUES (?, ?, ?, ?, ?)",
                       (dr_id, st_id, app_dt, app_st, int_dt))

# ==========================================
# 2. HELPER FUNCTIONS & AUTH
# ==========================================
def authenticate_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

def register_user(username, password, role, details):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
        user_id = cursor.lastrowid

        if role == 'Student':
            cursor.execute('''INSERT INTO Students 
                (student_id, name, email, branch, course, semester, cgpa, skills, certifications, projects) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (user_id, details['name'], details['email'], details['branch'], details['course'],
                 details['semester'], details['cgpa'], details['skills'], details['certifications'], details['projects']))
        elif role == 'Company':
            cursor.execute('''INSERT INTO Companies (company_id, company_name, website, contact_email, status) 
                VALUES (?, ?, ?, ?, 'Pending')''',
                (user_id, details['company_name'], details['website'], details['contact_email']))
        
        conn.commit()
        conn.close()
        return True, "Registration successful!"
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Username already exists. Choose a different one."

# ==========================================
# 3. STREAMLIT APP LAYOUT & ROUTING
# ==========================================
st.set_page_config(page_title="Campus Placement Management System", page_icon="🎓", layout="wide")

init_db()

# Session State Initialization
if 'user' not in st.session_state:
    st.session_state['user'] = None

# Sidebar Authentication Controls
st.sidebar.title("🎓 Placement Portal")

if st.session_state['user'] is None:
    auth_mode = st.sidebar.radio("Navigation", ["Login", "Register"])
    
    if auth_mode == "Login":
        st.subheader("🔐 System Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                user = authenticate_user(username, password)
                if user:
                    st.session_state['user'] = dict(user)
                    st.success(f"Welcome back, {user['username']}!")
                    st.rerun()
                else:
                    st.error("Invalid Username or Password.")

    elif auth_mode == "Register":
        st.subheader("📝 New User Registration")
        role = st.selectbox("Select Role", ["Student", "Company"])
        
        with st.form("register_form"):
            reg_username = st.text_input("Username*")
            reg_password = st.text_input("Password*", type="password")
            
            details = {}
            if role == "Student":
                details['name'] = st.text_input("Full Name*")
                details['email'] = st.text_input("Email*")
                details['branch'] = st.selectbox("Branch*", ["CSE", "IT", "ECE", "EEE", "MECH", "CIVIL"])
                details['course'] = st.selectbox("Course*", ["B.Tech", "M.Tech", "MCA"])
                details['semester'] = st.number_input("Semester*", min_value=1, max_value=8, value=8)
                details['cgpa'] = st.number_input("CGPA*", min_value=0.0, max_value=10.0, value=8.0, step=0.1)
                details['skills'] = st.text_area("Skills (comma separated)", "Python, SQL")
                details['certifications'] = st.text_area("Certifications", "AWS Practitioner")
                details['projects'] = st.text_area("Major Projects", "Portfolio Web Application")
            
            elif role == "Company":
                details['company_name'] = st.text_input("Company Name*")
                details['website'] = st.text_input("Website URL", "https://")
                details['contact_email'] = st.text_input("HR Contact Email*")

            reg_submit = st.form_submit_button("Register Account")

            if reg_submit:
                if not reg_username or not reg_password:
                    st.error("Please fill in all required credentials.")
                else:
                    success, msg = register_user(reg_username, reg_password, role, details)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)

else:
    # Authenticated User Navigation
    user = st.session_state['user']
    st.sidebar.markdown(f"**Logged in as:** `{user['username']}`")
    st.sidebar.markdown(f"**Role:** `{user['role']}`")
    if st.sidebar.button("Logout"):
        st.session_state['user'] = None
        st.rerun()

    # ==========================================
    # 4. ADMIN MODULE
    # ==========================================
    if user['role'] == 'Admin':
        st.title("🛡️ Placement Officer / Admin Dashboard")
        
        # Key Performance Metrics
        conn = get_connection()
        c = conn.cursor()
        
        tot_students = c.execute("SELECT COUNT(*) FROM Students").fetchone()[0]
        tot_companies = c.execute("SELECT COUNT(*) FROM Companies WHERE status = 'Approved'").fetchone()[0]
        active_drives = c.execute("SELECT COUNT(*) FROM PlacementDrives WHERE status = 'Applications Open'").fetchone()[0]
        tot_apps = c.execute("SELECT COUNT(*) FROM Applications").fetchone()[0]
        selected_students = c.execute("SELECT COUNT(DISTINCT student_id) FROM Applications WHERE status = 'Selected'").fetchone()[0]
        placement_pct = round((selected_students / tot_students * 100), 1) if tot_students > 0 else 0

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        col1.metric("Total Students", tot_students)
        col2.metric("Approved Companies", tot_companies)
        col3.metric("Active Drives", active_drives)
        col4.metric("Applications", tot_apps)
        col5.metric("Placed Students", selected_students)
        col6.metric("Placement Rate", f"{placement_pct}%")

        st.divider()

        tab1, tab2, tab3, tab4 = st.tabs(["Manage Companies", "Manage Placement Drives", "Applications & Status", "Reports & Statistics"])

        with tab1:
            st.subheader("Company Registration Approvals")
            pending_comps = c.execute("SELECT * FROM Companies WHERE status = 'Pending'").fetchall()
            if pending_comps:
                for comp in pending_comps:
                    c1, c2, c3, c4 = st.columns([3, 3, 2, 2])
                    c1.write(f"**{comp['company_name']}** ({comp['contact_email']})")
                    c2.write(comp['website'])
                    if c3.button("Approve", key=f"app_{comp['company_id']}"):
                        c.execute("UPDATE Companies SET status = 'Approved' WHERE company_id = ?", (comp['company_id'],))
                        conn.commit()
                        st.rerun()
                    if c4.button("Reject", key=f"rej_{comp['company_id']}"):
                        c.execute("UPDATE Companies SET status = 'Rejected' WHERE company_id = ?", (comp['company_id'],))
                        conn.commit()
                        st.rerun()
            else:
                st.info("No pending company registrations.")

            st.subheader("All Registered Companies")
            all_comps = c.execute("SELECT * FROM Companies").fetchall()
            st.dataframe([dict(row) for row in all_comps], use_container_width=True)

        with tab2:
            st.subheader("Create / Manage Placement Drives")
            with st.expander("➕ Create New Placement Drive"):
                approved_comps = c.execute("SELECT company_id, company_name FROM Companies WHERE status = 'Approved'").fetchall()
                if not approved_comps:
                    st.warning("No approved companies available to create drives.")
                else:
                    comp_dict = {comp['company_name']: comp['company_id'] for comp in approved_comps}
                    with st.form("admin_create_drive"):
                        sel_comp = st.selectbox("Select Company", list(comp_dict.keys()))
                        job_role = st.text_input("Job Role")
                        package = st.number_input("Package (LPA)", min_value=1.0, value=8.0, step=0.5)
                        location = st.text_input("Job Location", "Pan India")
                        req_skills = st.text_input("Required Skills", "Python, SQL")
                        min_cgpa = st.number_input("Min CGPA Requirement", min_value=0.0, max_value=10.0, value=7.0)
                        branches = st.multiselect("Eligible Branches", ["CSE", "IT", "ECE", "EEE", "MECH", "CIVIL"], default=["CSE", "IT"])
                        deadline = st.date_input("Application Deadline", datetime.date.today() + datetime.timedelta(days=15))
                        process = st.text_area("Selection Process", "Online Test -> Technical Interview -> HR")
                        submit_drive = st.form_submit_button("Publish Drive")

                        if submit_drive:
                            c.execute('''INSERT INTO PlacementDrives 
                                (company_id, job_role, package_lpa, location, required_skills, min_cgpa, eligible_branches, deadline, selection_process, status)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Applications Open')''',
                                (comp_dict[sel_comp], job_role, package, location, req_skills, min_cgpa, ", ".join(branches), deadline, process))
                            conn.commit()
                            st.success("Placement Drive successfully published!")
                            st.rerun()

            st.subheader("Existing Placement Drives")
            drives = c.execute('''SELECT d.drive_id, c.company_name, d.job_role, d.package_lpa, d.location, d.min_cgpa, d.eligible_branches, d.status 
                                  FROM PlacementDrives d JOIN Companies c ON d.company_id = c.company_id''').fetchall()
            st.dataframe([dict(d) for d in drives], use_container_width=True)

        with tab3:
            st.subheader("Update Student Application Status")
            apps = c.execute('''SELECT a.application_id, s.name AS student_name, s.branch, s.cgpa, c.company_name, d.job_role, a.status, a.interview_date 
                                FROM Applications a 
                                JOIN Students s ON a.student_id = s.student_id 
                                JOIN PlacementDrives d ON a.drive_id = d.drive_id 
                                JOIN Companies c ON d.company_id = c.company_id''').fetchall()
            
            for app in apps:
                with st.expander(f"{app['student_name']} -> {app['company_name']} ({app['job_role']}) - Status: {app['status']}"):
                    col_a, col_b = st.columns(2)
                    col_a.write(f"**Branch:** {app['branch']} | **CGPA:** {app['cgpa']}")
                    col_a.write(f"**

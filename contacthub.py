import streamlit as st
import re
from dbconnection import get_db_connection
import mysql.connector.errors
import io
import pandas as pd
import time 

if "page" not in st.session_state:
    st.session_state.page = "login"

def set_page(page):
    st.session_state.page = page

def main():
    st.title("Contact Hub")
    
    if "user_id" not in st.session_state:
        login_tab, signup_tab = st.tabs(["Login", "Sign Up"])
        
        with login_tab:
            login_page()
        with signup_tab:
            signup_page()
    else:
        st.markdown(
            """
            <style>
                div[class="st-b0 st-eq st-e8 st-e9 st-ea st-eb st-ec st-ag st-ed st-bv st-ee st-av st-ef st-au st-bi st-eg st-eh st-ei st-bg st-co"],div[class ="st-b0 st-c1 st-e8 st-e9 st-ea st-eb st-ec st-ag st-ed st-bv st-ee st-av st-ef st-au st-bi st-eg st-eh st-ei st-bg st-co"]{
                    display: none !important;
                }
                div[role="radiogroup"] p:hover {
                    color: rgb(255, 75, 75);
                    font-weight: bold;
                    transform: scale(1.5);
                }
                div[role="radiogroup"] p {
                    margin-bottom:20px;
                    transition: 0.1s;
                }
            </style>
            """,
            unsafe_allow_html=True
        )

        tabs = ["Contacts", "Add Contact", "Import Contact", "Export Contact"]
        active_tab = st.sidebar.radio("Navigation", tabs, label_visibility="collapsed")

        if active_tab == "Contacts":
            dashboard()
        elif active_tab == "Add Contact":
            add_contact()
        elif active_tab == "Import Contact":
            import_contacts()
        elif active_tab == "Export Contact":
            export_contacts()

def login_page():
    user_input = st.text_input("Username or Email") 
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        conn = get_db_connection()  
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE (username = %s OR email = %s) AND password = %s",(user_input, user_input, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            st.session_state.user_id = user[0]
            st.rerun()
        else:
            st.error("Invalid credentials. Please try again.")

def signup_page():
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    email = st.text_input("Email")

    username_pattern = r'^[A-Za-z0-9_]+$'
    email_pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    password_pattern = r'^.{6,}$'
    if st.button("Register"):
        if not re.match(username_pattern, new_username):
            st.error("Username can only contain letters, numbers, and underscores.")
        elif not re.match(email_pattern, email):
            st.error("Invalid email format.")
        elif not re.match(password_pattern, new_password):
            st.error("Password must be at least 6 characters long.")
        elif new_password != confirm_password:
            st.error("Passwords do not match.")
        else:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (new_username,))
            if cursor.fetchone()[0] > 0:
                st.error("Username already exists. Choose a different one.")
            else:
                cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",(new_username, new_password, email))
                conn.commit()
                st.success("Account created successfully! Please login.")

            conn.close()

def dashboard():
    search_query = st.text_input("Search by Name or Number")
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
    SELECT contact_id, name, number 
    FROM contacts 
    WHERE user_id = %s AND (name LIKE %s OR number LIKE %s) 
    ORDER BY name
    """
    cursor.execute(query, (st.session_state.user_id, f"%{search_query}%", f"%{search_query}%"))
    contacts = cursor.fetchall()
    conn.close()
    
    if "selected_contact" in st.session_state:
        contact_details()
        if st.button("🔙 Back to Contacts"):
            del st.session_state.selected_contact 
            st.rerun()
        return  
    st.markdown(
        """
       <style>
        div.stButton > button {
            border: none;
            width: 100%;
            justify-content: start;
            background: transparent;
            padding: 12px;
            font-size: 16px;
            cursor: pointer;
            border-bottom: 1px solid gray;
            border-radius : 0;
        }

        div.stButton > button:hover {
            background: rgba(0, 0, 0, 0.05);
        }

        div.stButton > button:focus {
            border-bottom: 2px solid gray;
        }
    </style>
        """,unsafe_allow_html=True
    )
    for contact in contacts:
        if st.button(f"{contact[1]} - {contact[2]}"):
            st.session_state.selected_contact = contact[0]
            st.rerun()

def contact_details():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM contacts WHERE contact_id = %s", (st.session_state.selected_contact,))
    contact = cursor.fetchone()
    conn.close()

    st.title(contact["name"])
    st.write(f"**Number:** {contact['number']}")
    st.write(f"**Email:** {contact['email']}")
    st.write(f"**Job Title:** {contact['job_title']}")
    st.write(f"**Gender:** {contact['gender']}")
    st.write(f"**Notes:** {contact['note']}")

    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Edit Contact"):
            st.session_state.editing = True  

    with col2:
        if st.button("Remove Contact"):
            remove_contact()

    if st.session_state.get("editing", False):
        edit_contact()


def edit_contact():
    if "selected_contact" not in st.session_state or not st.session_state.selected_contact:
        st.error("⚠ No contact selected!")
        return

    if "contact_data" not in st.session_state or st.session_state.selected_contact != st.session_state.get("contact_id"):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute("SELECT * FROM contacts WHERE contact_id = %s", (st.session_state.selected_contact,))
            contact = cursor.fetchone()
            if not contact:
                st.error("⚠ Contact not found!")
                return

            # Store fetched data in session state
            st.session_state.contact_id = st.session_state.selected_contact
            st.session_state.name = contact["name"]
            st.session_state.number = contact["number"]
            st.session_state.job_title = contact["job_title"] or ""
            st.session_state.gender = contact["gender"] if contact["gender"] in ["M", "F", "N"] else "N"
            st.session_state.email = contact["email"] or ""
            st.session_state.note = contact["note"] or ""

        except mysql.connector.Error as err:
            st.error(f"Database error: {err}")
        finally:
            cursor.close()
            conn.close()

    # Editable fields
    name = st.text_input("Name", value=st.session_state.name)
    number = st.text_input("Number", value=st.session_state.number)
    job_title = st.text_input("Job Title", value=st.session_state.job_title)

    gender_options = ["M", "F", "N"]
    gender = st.selectbox("Gender", gender_options, index=gender_options.index(st.session_state.gender))

    email = st.text_input("Email", value=st.session_state.email)
    note = st.text_area("Notes", value=st.session_state.note)

    if st.button("Save Changes"):
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "UPDATE contacts SET name=%s, number=%s, job_title=%s, gender=%s, note=%s, email=%s WHERE contact_id=%s",
                (name, number, job_title, gender, note, email, st.session_state.selected_contact)
            )
            conn.commit()

            if cursor.rowcount > 0:
                st.success("✅ Contact updated successfully!")
                st.session_state.updated = True 
            else:
                st.warning("⚠ No changes detected or invalid contact ID.")

        except mysql.connector.Error as err:
            st.error(f"⚠ Database error: {err}")
        finally:
            cursor.close()
            conn.close()

        st.session_state.editing = False
        time.sleep(1.5)  
        st.rerun()


def remove_contact():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM contacts WHERE contact_id = %s", (st.session_state.selected_contact,))
    conn.commit()
    conn.close()
    st.success("Contact removed successfully!")
    del st.session_state.selected_contact
    st.rerun()

def add_contact():
    name = st.text_input("Name")
    number = st.text_input("Number")
    job_title = st.text_input("Job Title")
    gender = st.selectbox("Gender", ["M", "F", "N"], index=2)
    email = st.text_input("Email")
    note = st.text_area("Notes")

    if st.button("Save Contact"):
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "INSERT INTO contacts (user_id, name, number, job_title, gender, note, email) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (st.session_state.user_id, name, number, job_title, gender, note, email)
            )
            conn.commit()
            
            st.success("✅ Contact added successfully!")

            time.sleep(1.5)

            st.rerun()
        except mysql.connector.Error as err:
            st.error(f"⚠ Database error: {err}")
        finally:
            conn.close()

def export_contacts():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = "SELECT name, number, email, job_title FROM contacts WHERE user_id = %s ORDER BY name ASC"
    cursor.execute(query, (st.session_state.user_id,))
    contacts = cursor.fetchall()
    conn.close()

    if not contacts:
        st.warning("No contacts available to export.")
        return

    df = pd.DataFrame(contacts)
    
    # Splitting names into first, middle, and last
    name_parts = df["name"].str.split(" ", expand=True)
    df["First Name"] = name_parts[0]
    df["Middle Name"] = name_parts[1] if name_parts.shape[1] > 2 else ""
    df["Last Name"] = name_parts[name_parts.shape[1] - 1] if name_parts.shape[1] > 1 else ""
    
    df.rename(columns={"number": "Mobile Phone", "email": "E-mail Address", "job_title": "Job Title"}, inplace=True)
    df = df[["First Name", "Middle Name", "Last Name", "Mobile Phone", "E-mail Address", "Job Title"]]
    
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False, encoding="utf-8")
    
    st.download_button(
        label="📥 Download Contacts CSV",
        data=csv_buffer.getvalue(),
        file_name="google_contacts.csv",
        mime="text/csv"
    )

def import_contacts():
    uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])
    
    if uploaded_file:
        df = pd.read_csv(uploaded_file, encoding="utf-8")

        required_columns = {"First Name", "Middle Name", "Last Name", "Mobile Phone", "E-mail Address", "Job Title"}
        if not required_columns.issubset(df.columns):
            st.error(f"CSV must include: {', '.join(required_columns)}")
            return
        
        df = df.fillna("")

        conn = get_db_connection()
        cursor = conn.cursor()

        for _, row in df.iterrows():
            first_name = row["First Name"].strip()
            middle_name = row["Middle Name"].strip()
            last_name = row["Last Name"].strip()
            if middle_name != '' :
                full_name = f"{first_name} {middle_name} {last_name}".strip()
            else :
                full_name = f"{first_name} {last_name}".strip()

            cursor.execute(
                "INSERT INTO contacts (user_id, name, number, email, job_title) VALUES (%s, %s, %s, %s, %s)",
                (st.session_state.user_id, full_name, row["Mobile Phone"], row["E-mail Address"], row["Job Title"])
            )

        conn.commit()
        conn.close()
        st.success("Contacts imported successfully!")

if __name__ == "__main__":
    main()
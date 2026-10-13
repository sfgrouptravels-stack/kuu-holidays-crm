import streamlit as st
import pandas as pd
from datetime import datetime
import os
import json

# ==========================================
# PAGE CONFIGURATION & THEME
# ==========================================
st.set_page_config(page_title="KUU Holidays CRM", page_icon="✈️", layout="wide")

st.markdown("""
    <style>
    /* HIDE STREAMLIT BRANDING, MENUS & MANAGE APP BUTTON */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* HIDE BOTTOM RIGHT WATERMARK LOGO & BADGES */
    a[href^="https://streamlit.io/cloud"] {display: none !important;}
    [data-testid="stDecoration"] {display: none !important;}
    div[class^="viewerBadge"] {display: none !important;}
    .stDeployButton {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    [data-testid="stAppDeployButton"] {display: none !important;}
    
    /* CUSTOM STYLES */
    .main { background-color: #f4f6f9; }
    .summary-box { padding: 15px; border-radius: 8px; color: white; font-weight: bold; text-align: left; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }
    .stButton>button { background-color: #0d47a1; color: white; border-radius: 5px; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #082f6b; color: white; }
    .sidebar-footer { font-size: 12px; color: #555555; border-top: 1px solid #d1d1d1; padding-top: 15px; margin-top: 30px; line-height: 1.6; }
    .streamlit-expanderHeader { font-weight: bold !important; font-size: 16px !important; background-color: #ffffff !important; border-radius: 5px !important; border: 1px solid #e0e0e0 !important; }
    .history-box { background-color: #f8f9fa; border: 1px solid #e0e0e0; border-radius: 5px; padding: 12px; margin-bottom: 15px; font-size: 13px; height: 180px; overflow-y: auto; line-height: 1.5; }
    .compact-text { line-height: 1.4; font-size: 13px; color: #1a3024; background-color: #eaf2ed; padding: 12px; border-radius: 6px; border: 1px solid #c6d9cd; }
    .wa-button { text-decoration: none !important; color: #128C7E !important; font-weight: bold; font-size: 13px; background-color: #ffffff; padding: 2px 6px; border-radius: 8px; border: 1px solid #c8e6c9; display: inline-block; }
    .wa-button:hover { background-color: #e8f5e9; text-decoration: none !important; }
    .compact-text a { text-decoration: none !important; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# USER MANAGEMENT (DYNAMIC)
# ==========================================
USERS_FILE = "users.json"

def load_users():
    if not os.path.exists(USERS_FILE):
        default_admin = {"admin": {"password": "adminpassword", "name": "Admin", "role": "admin"}}
        with open(USERS_FILE, 'w') as f:
            json.dump(default_admin, f)
        return default_admin
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users_dict):
    with open(USERS_FILE, 'w') as f:
        json.dump(users_dict, f)

# ==========================================
# CONSTANTS & LOCAL DATABASE SETUP
# ==========================================
INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat", 
    "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", 
    "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", 
    "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", 
    "Uttarakhand", "West Bengal", "Andaman and Nicobar", "Chandigarh", "Dadra and Nagar Haveli", 
    "Daman and Diu", "Delhi", "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Puducherry"
]
ALL_WORLD_COUNTRIES = [
    "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua and Barbuda", "Argentina", 
    "Armenia", "Australia", "Austria", "Azerbaijan", "Bahamas", "Bahrain", "Bali (Indonesia)", 
    "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan", "Bolivia", 
    "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei", "Bulgaria", "Burkina Faso", "Burundi", 
    "Cambodia", "Cameroon", "Canada", "Chile", "China", "Colombia", "Costa Rica", "Croatia", "Cuba", 
    "Cyprus", "Czech Republic", "Denmark", "Dubai (UAE)", "Egypt", "Fiji", "Finland", "France", "Georgia", 
    "Germany", "Greece", "Hong Kong", "Hungary", "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland", 
    "Israel", "Italy", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kuwait", "Kyrgyzstan", "Laos", 
    "Lebanon", "Malaysia", "Maldives", "Mauritius", "Mexico", "Nepal", "Netherlands", "New Zealand", "Oman", 
    "Pakistan", "Philippines", "Poland", "Portugal", "Qatar", "Russia", "Saudi Arabia", "Seychelles", 
    "Singapore", "South Africa", "South Korea", "Spain", "Sri Lanka", "Sweden", "Switzerland", "Taiwan", 
    "Tajikistan", "Tanzania", "Thailand", "Turkey", "Turkmenistan", "Ukraine", "United Arab Emirates", 
    "United Kingdom", "United States", "Uzbekistan", "Vietnam", "Yemen", "Zambia", "Zimbabwe"
]
WORLD_COUNTRIES = sorted(list(set(ALL_WORLD_COUNTRIES + INDIAN_STATES)))

DB_FILE = "local_database.csv"
COLUMNS = ["Query ID", "Date", "Client Name", "Mobile Number", "Adult", "Child", "Child Age", "Infant", 
           "Guest Email", "Travel Date", "Lead Source", "Company", 
           "Duration(Night)", "Destination", "Departure From", "Description", "Status", "Sales Person", "Notes", "FollowUp"]
STATUS_OPTIONS = ["Active", "In Progress", "Hot", "Interested", "Converted", "Cancelled"]

def init_db():
    if not os.path.exists(DB_FILE):
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(DB_FILE, index=False)

def get_data():
    init_db()
    try:
        df = pd.read_csv(DB_FILE)
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = ""
        df = df.fillna("")
        return df
    except Exception:
        return pd.DataFrame(columns=COLUMNS)

def save_data(df):
    df.to_csv(DB_FILE, index=False)

def search_dataframe(df, search_term):
    if not search_term or df.empty:
        return df
    term = str(search_term).strip().lower()
    mask = df.apply(lambda row: row.astype(str).str.lower().str.contains(term, regex=False).any(), axis=1)
    return df[mask]

# ==========================================
# MAIN APP WITH LOGIN
# ==========================================
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login_page()
    else:
        crm_app()

def login_page():
    st.markdown("<h2 style='text-align: center; color: #0d47a1; margin-top: 100px;'>🔒 KUU Holidays CRM Login</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.form("login_form"):
            st.write("Please enter your credentials:")
            username = st.text_input("Username").strip()
            password = st.text_input("Password", type="password").strip()
            submitted = st.form_submit_button("Login", use_container_width=True)
            
            if submitted:
                users = load_users()
                if username in users and users[username]["password"] == password:
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.name = users[username]["name"]
                    st.session_state.role = users[username]["role"]
                    st.rerun()
                else:
                    st.error("Invalid Username or Password")

def crm_app():
    users_data = load_users()
    
    if "menu" not in st.session_state:
        st.session_state.menu = "Dashboard"

    # 1. SIDEBAR UI
    try:
        st.sidebar.image("logo.png", use_container_width=True)
    except:
        st.sidebar.write(" ")
        
    st.sidebar.title("KUU Holidays")
    st.sidebar.write(f"👤 **Logged in as:** {st.session_state.name} ({st.session_state.role.capitalize()})")
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()
        
    st.sidebar.divider()
    
    # Menu items based on role
    menu_options = ["Dashboard", "Query", "Add New Query"]
    if st.session_state.role == "admin":
        menu_options.append("Admin Panel")
        
    st.session_state.menu = st.sidebar.radio(
        "Navigation", 
        menu_options,
        index=menu_options.index(st.session_state.menu) if st.session_state.menu in menu_options else 0
    )
    
    st.sidebar.markdown("""
        <div class="sidebar-footer">
            <b>Regd. Address:</b><br>
            808B, DLF Prime Tower<br>
            Okhla Industrial Estate Phase 1<br>
            New Delhi, 110020, India<br><br>
            📞 +91 9220233312<br>
            ✉️ contact@kuuholidays.com<br>
            🌐 www.kuuholidays.com
        </div>
    """, unsafe_allow_html=True)

    # 2. LOAD & FILTER DATA
    df = get_data()
    
    if st.session_state.role == "employee":
        df = df[df["Sales Person"] == st.session_state.name]

    # 3. CALCULATE STATUS COUNTS
    total_queries = len(df)
    if not df.empty and 'Status' in df.columns:
        active_count = len(df[df['Status'] == 'Active'])
        inprogress_count = len(df[df['Status'] == 'In Progress'])
        converted_count = len(df[df['Status'] == 'Converted'])
        cancelled_count = len(df[df['Status'] == 'Cancelled'])
        hot_count = len(df[df['Status'] == 'Hot'])
        interested_count = len(df[df['Status'] == 'Interested'])
    else:
        active_count = inprogress_count = converted_count = cancelled_count = hot_count = interested_count = 0

    # ------------------------------------------
    # ADMIN PANEL PAGE
    # ------------------------------------------
    if st.session_state.menu == "Admin Panel":
        st.subheader("⚙️ Admin Panel - User Management")
        
        st.write("### Current Users")
        users_df = pd.DataFrame([{"Username": k, "Name": v["name"], "Role": v["role"].capitalize()} for k, v in users_data.items()])
        st.dataframe(users_df, use_container_width=True)
        
        col_new, col_pass = st.columns(2)
        
        with col_new:
            st.markdown("#### Add New Employee")
            with st.form("new_user_form"):
                n_user = st.text_input("New Username (Login ID)")
                n_name = st.text_input("Employee Full Name")
                n_pass = st.text_input("Password", type="password")
                n_role = st.selectbox("Role", ["Employee", "Admin"])
                
                if st.form_submit_button("Create User"):
                    if n_user and n_name and n_pass:
                        if n_user in users_data:
                            st.error("Username already exists!")
                        else:
                            users_data[n_user] = {"password": n_pass, "name": n_name, "role": n_role.lower()}
                            save_users(users_data)
                            st.success(f"User {n_user} created successfully!")
                            st.rerun()
                    else:
                        st.error("Please fill all fields.")
                        
        with col_pass:
            st.markdown("#### Change Password")
            with st.form("change_pass_form"):
                sel_user = st.selectbox("Select User", list(users_data.keys()))
                c_pass = st.text_input("New Password", type="password")
                
                if st.form_submit_button("Update Password"):
                    if c_pass:
                        users_data[sel_user]["password"] = c_pass
                        save_users(users_data)
                        st.success(f"Password updated for {sel_user}!")
                    else:
                        st.error("Please enter a new password.")

    # ------------------------------------------
    # DASHBOARD PAGE
    # ------------------------------------------
    elif st.session_state.menu == "Dashboard":
        st.markdown("<br>", unsafe_allow_html=True)
        search_col1, search_col2 = st.columns([3, 1])
        with search_col1:
            global_search_term = st.text_input("🔍 Global Search", placeholder="Type ID, Name, Mobile, Destination...", key="global_search_input")

        st.subheader("📊 CRM Dashboard")
        m1, m2, m3, m4, m5, m6 = st.columns(6)
        m1.metric("Today's Queries", "0")
        m2.metric("Yesterday Queries", "0")
        m3.metric("Total Queries", str(total_queries))
        m4.metric("Converted", str(converted_count))
        m5.metric("Hot Queries", str(hot_count))
        m6.metric("Invoice", "0")
        
        st.divider()
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("#### 🎯 Query Wise Status")
            st.write(f"Active: {active_count}")
            st.progress(active_count/total_queries if total_queries>0 else 0)
            st.write(f"In Progress: {inprogress_count}")
            st.progress(inprogress_count/total_queries if total_queries>0 else 0)
            st.write(f"Converted: {converted_count}")
            st.progress(converted_count/total_queries if total_queries>0 else 0)
            st.write(f"Cancel: {cancelled_count}")
            st.progress(cancelled_count/total_queries if total_queries>0 else 0)
        
        with col2:
            st.markdown("#### 📈 Month Wise Queries")
            months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            chart_data = pd.DataFrame({"Months": months, "Queries": [0] * 12})
            st.bar_chart(chart_data.set_index("Months"), color="#0d47a1")

    # ------------------------------------------
    # QUERY MANAGEMENT PAGE
    # ------------------------------------------
    elif st.session_state.menu == "Query":
        st.markdown("<br>", unsafe_allow_html=True)
        search_col1, search_col2 = st.columns([3, 1])
        with search_col1:
            global_search_term = st.text_input("🔍 Global Search", placeholder="Type ID, Name, Mobile, Destination...", key="global_search_input")

        with st.container():
            f1, f2, f3, f4, f5, f6 = st.columns(6)
            if f1.button("+ Add Query", use_container_width=True):
                st.session_state.menu = "Add New Query"
                st.rerun()
            f2.selectbox("All Query", ["All Query", "My Query"])
            f3.date_input("From Date")
            f4.date_input("To Date")
            
            sales_persons = ["All"] + [v["name"] for k, v in users_data.items() if v["role"] == "employee"]
            if st.session_state.role == "admin":
                sales_filter = f5.selectbox("Sales Person", sales_persons)
            else:
                sales_filter = f5.selectbox("Sales Person", [st.session_state.name])
                
            dest_filter = f6.selectbox("Destination", ["All"] + WORLD_COUNTRIES)
            
            g1, g2, g3, g4, g5 = st.columns(5)
            g1.selectbox("Lead Source", ["All", "Website", "Referral", "Walk-in", "Social Media", "B2B"])
            g2.selectbox("Month", ["All", "January", "February", "March", "April"])
            status_filter = g3.selectbox("Status", ["All"] + STATUS_OPTIONS)
            g4.selectbox("Trip Status", ["All", "Quoted", "Follow-up"])
            g5.selectbox("Operation Person", ["All"])
            
        st.write("<br>", unsafe_allow_html=True)
        
        c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(8)
        c1.markdown(f'<div class="summary-box" style="background-color: #1f3b5c; font-size:14px;">Total<br><h4>{total_queries}</h4></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="summary-box" style="background-color: #e5a732; font-size:14px;">Active<br><h4>{active_count}</h4></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="summary-box" style="background-color: #ff8c00; font-size:14px;">In Prog.<br><h4>{inprogress_count}</h4></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="summary-box" style="background-color: #c9302c; font-size:14px;">Hot<br><h4>{hot_count}</h4></div>', unsafe_allow_html=True)
        c5.markdown(f'<div class="summary-box" style="background-color: #9c27b0; font-size:14px;">Interest<br><h4>{interested_count}</h4></div>', unsafe_allow_html=True)
        c6.markdown(f'<div class="summary-box" style="background-color: #159588; font-size:14px;">Convert<br><h4>{converted_count}</h4></div>', unsafe_allow_html=True)
        c7.markdown('<div class="summary-box" style="background-color: #0275d8; font-size:14px;">Invoice<br><h4>0</h4></div>', unsafe_allow_html=True)
        c8.markdown(f'<div class="summary-box" style="background-color: #a94442; font-size:14px;">Cancel<br><h4>{cancelled_count}</h4></div>', unsafe_allow_html=True)

        st.divider()
        st.subheader("📋 Lead Pipeline")

        display_df = df.copy()
        if global_search_term:
            display_df = search_dataframe(display_df, global_search_term)
        if dest_filter != "All":
            display_df = display_df[display_df["Destination"] == dest_filter]
        if status_filter != "All":
            display_df = display_df[display_df["Status"] == status_filter]
        if st.session_state.role == "admin" and sales_filter != "All":
            display_df = display_df[display_df["Sales Person"] == sales_filter]

        if display_df.empty:
            st.info("No queries found based on your filters.")
        else:
            display_df = display_df.iloc[::-1] 
            
            for index, row in display_df.iterrows():
                status_emoji = {"Active": "🟡", "In Progress": "🔄", "Hot": "🔥", "Interested": "🟣", "Converted": "✅", "Cancelled": "❌"}.get(row['Status'], "📝")
                expander_title = f"{status_emoji} {row['Query ID']} | {row['Client Name']} | 📍 {row['Destination']} | 👤 {row.get('Sales Person', 'N/A')} | 🏷️ {row['Status']}"
                
                with st.expander(expander_title):
                    col_left, col_right = st.columns([1.2, 1])
                    
                    with col_left:
                        st.markdown("##### 👤 Client & Trip Details")
                        
                        phone_num = str(row['Mobile Number']).strip()
                        wa_num = "".join(filter(str.isdigit, phone_num))
                        wa_link = f"https://web.whatsapp.com/send?phone={wa_num}" if wa_num else "#"
                        
                        st.markdown(f"""
                            <div class="compact-text">
                                <b>📱 Mobile:</b> <a href="{wa_link}" class="wa-button" target="whatsapp_web">💬 {phone_num}</a><br>
                                <b>✉️ Email:</b> {row.get('Guest Email', 'N/A')}<br><br>
                                <b>👥 Pax:</b> {row['Adult']} Adult, {row['Child']} Child (Age: {row.get('Child Age', 'N/A')}), {row['Infant']} Infant &nbsp;|&nbsp; <b>🌙 Duration:</b> {row['Duration(Night)']} Nights<br><br>
                                <b>🛫 Departure:</b> {row['Departure From']} &nbsp;|&nbsp; <b>📍 Destination:</b> {row['Destination']} &nbsp;|&nbsp; <b>🏢 Company:</b> {row['Company']}<br><br>
                                <b>📝 Query:</b> {row['Description']}<br>
                                <b>🧑‍💼 Handled By:</b> {row.get('Sales Person', 'Admin')}
                            </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.markdown("##### ⚙️ Update Lead")
                        with st.form(key=f"update_form_{row['Query ID']}"):
                            
                            c_stat, c_fup = st.columns(2)
                            curr_status_idx = STATUS_OPTIONS.index(row['Status']) if row['Status'] in STATUS_OPTIONS else 0
                            new_status = c_stat.selectbox("Update Status", STATUS_OPTIONS, index=curr_status_idx)
                            new_followup = c_fup.text_input("Next Follow-up (Date/Time)")
                            
                            new_notes = st.text_input("Add New Internal Note")
                            submit_update = st.form_submit_button("💾 Save Update")
                            
                            if submit_update:
                                full_df = get_data() 
                                timestamp = datetime.now().strftime("%d-%b %I:%M %p")
                                
                                updated_notes = row.get('Notes', '')
                                if new_notes.strip():
                                    new_note_entry = f"[{timestamp} by {st.session_state.name}] {new_notes.strip()}"
                                    updated_notes = f"{updated_notes}\n{new_note_entry}" if updated_notes.strip() else new_note_entry
                                
                                updated_fup = row.get('FollowUp', '')
                                if new_followup.strip():
                                    new_fup_entry = f"[{timestamp} by {st.session_state.name}] {new_followup.strip()}"
                                    updated_fup = f"{updated_fup}\n{new_fup_entry}" if updated_fup.strip() else new_fup_entry
                                
                                full_df.loc[full_df['Query ID'] == row['Query ID'], 'Status'] = new_status
                                full_df.loc[full_df['Query ID'] == row['Query ID'], 'Notes'] = updated_notes
                                full_df.loc[full_df['Query ID'] == row['Query ID'], 'FollowUp'] = updated_fup
                                
                                save_data(full_df)
                                st.success("Lead successfully updated!")
                                st.rerun()

                    with col_right:
                        st.markdown("##### 🕒 Interaction History")
                        
                        st.write("**📝 Previous Notes & Comments:**")
                        prev_notes = row.get('Notes', '')
                        if prev_notes.strip():
                            st.markdown(f"<div class='history-box'>{prev_notes.replace(chr(10), '<br><br>')}</div>", unsafe_allow_html=True)
                        else:
                            st.markdown("<div class='history-box' style='color:#999;'>No internal notes added yet.</div>", unsafe_allow_html=True)
                            
                        st.write("**📅 Previous Follow-ups:**")
                        prev_fup = row.get('FollowUp', '')
                        if prev_fup.strip():
                            st.markdown(f"<div class='history-box'>{prev_fup.replace(chr(10), '<br><br>')}</div>", unsafe_allow_html=True)
                        else:
                            st.markdown("<div class='history-box' style='color:#999;'>No follow-ups scheduled yet.</div>", unsafe_allow_html=True)

    # ------------------------------------------
    # ADD NEW QUERY PAGE
    # ------------------------------------------
    elif st.session_state.menu == "Add New Query":
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("➕ Create New Lead")
        
        with st.form("add_query_form"):
            col1, col2, col3, col4, col_cage, col5 = st.columns([2, 2, 1, 1, 1, 1])
            client_name = col1.text_input("Client Name *")
            mobile = col2.text_input("Mobile Number *")
            adult = col3.text_input("Adult", value="0")
            child = col4.text_input("Child", value="0")
            child_age = col_cage.text_input("Child Age", value="0")
            infant = col5.text_input("Infant", value="0")
            
            col6, col7, col8, col9 = st.columns(4)
            guest_email = col6.text_input("Guest Email")
            travel_date = col7.date_input("Travel Date *")
            lead_source = col8.selectbox("Lead Source", ["Choose...", "Website", "Reference", "Social Media", "Walk-in", "B2B"])
            company = col9.selectbox("Company", ["KUU HOLIDAYS", "SF GROUP TRAVELS"])
            
            col10, col11, col12 = st.columns([1, 1, 2])
            duration = col10.text_input("Duration(Night) *")
            destination = col11.selectbox("Destination *", ["Choose..."] + WORLD_COUNTRIES)
            description = col12.text_area("Description / Initial Query")
            
            col13, col14 = st.columns([1, 3])
            departure_from = col13.text_input("Departure From *")
            
            sales_persons = [v["name"] for k, v in users_data.items() if v["role"] == "employee"]
            if st.session_state.role == "admin":
                assigned_to = st.selectbox("Assign To Employee", ["Admin"] + sales_persons)
            else:
                assigned_to = st.session_state.name
            
            st.write("")
            b1, b2, b3 = st.columns([8, 1, 1])
            cancel_btn = b2.form_submit_button("Cancel")
            save_btn = b3.form_submit_button("Save Lead", type="primary")
            
            if save_btn:
                if client_name and mobile and travel_date and duration and destination != "Choose...":
                    full_df = get_data()
                    date_str = datetime.now().strftime("%Y-%m-%d")
                    travel_date_str = travel_date.strftime("%Y-%m-%d")
                    
                    if full_df.empty:
                        new_qid = "KUU-1001"
                    else:
                        last_qid = full_df.iloc[-1]["Query ID"]
                        try:
                            num = int(last_qid.split("-")[1])
                            new_qid = f"KUU-{num+1}"
                        except:
                            new_qid = f"KUU-{len(full_df)+1001}"
                    
                    new_row = {
                        "Query ID": new_qid,
                        "Date": date_str, "Client Name": client_name, "Mobile Number": mobile, 
                        "Adult": adult, "Child": child, "Child Age": child_age, "Infant": infant, 
                        "Guest Email": guest_email, "Travel Date": travel_date_str, 
                        "Lead Source": lead_source, "Company": company, 
                        "Duration(Night)": duration, "Destination": destination, 
                        "Departure From": departure_from, "Description": description, 
                        "Status": "Active", "Sales Person": assigned_to, "Notes": "", "FollowUp": ""
                    }
                    
                    try:
                        full_df = pd.concat([full_df, pd.DataFrame([new_row])], ignore_index=True)
                        save_data(full_df)
                        st.success(f"✅ Lead '{client_name}' successfully created and assigned to {assigned_to}! Query ID: {new_qid}")
                    except Exception as e:
                        st.error(f"Error saving data: {e}")
                else:
                    st.error("⚠️ Please fill all mandatory fields marked with (*)")

if __name__ == "__main__":
    main()

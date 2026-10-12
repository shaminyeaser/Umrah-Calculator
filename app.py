import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="Umrah Package Calculator", layout="wide")

# --- PASSWORD PROTECTION CONFIGURATION ---
APP_PASSWORD = "share123"

def check_password():
    """Returns True if the user entered the correct password."""
    def password_entered():
        if st.session_state["password"] == APP_PASSWORD:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("<h2 style='color: #0A192F; text-align: center; margin-top: 50px;'>Umrah Package Calculator - Login</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #1E3A8A;'>Please enter your team password to access the calculator.</p>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.markdown("<h2 style='color: #0A192F; text-align: center; margin-top: 50px;'>Umrah Package Calculator - Login</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.text_input("Password", type="password", on_change=password_entered, key="password")
            st.error("😕 Password incorrect. Please try again.")
        return False
    else:
        return True

# If password is correct, run the main app
if check_password():

    # --- DATABASE SETUP (Built-in SQLite) ---
    conn = sqlite3.connect('umrah_quotes.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS quotations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            client_name TEXT,
            pax INTEGER,
            makkah_hotel TEXT,
            madinah_hotel TEXT,
            jeddah_hotel TEXT,
            total_price_bdt REAL,
            per_person_bdt REAL
        )
    ''')
    conn.commit()

    # Dynamic Column Addition for existing DBs
    try:
        c.execute("ALTER TABLE quotations ADD COLUMN jeddah_hotel TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass

    # --- CUSTOM CSS FOR UNIQUE BLUE BACKGROUND & HIGH CONTRAST VISIBILITY ---
    st.markdown("""
        <style>
        .stApp {
            background-color: #EBF2FA !important;
        }
        .main-header {
            font-size: 32px; 
            font-weight: 800; 
            color: #0A192F;
            margin-bottom: 0px;
        }
        .sub-header {
            font-size: 16px; 
            font-weight: 700; 
            color: #1E3A8A;
            margin-bottom: 20px;
        }
        section[data-testid="stSidebar"] {
            background-color: #DCE7F5 !important;
            border-right: 2px solid #93C5FD;
        }
        section[data-testid="stSidebar"] h2 {
            color: #0A192F !important;
            font-weight: 800 !important;
            font-size: 18px !important;
            border-bottom: 2px solid #1E3A8A;
            padding-bottom: 5px;
            margin-top: 15px;
        }
        section[data-testid="stSidebar"] label {
            color: #0F172A !important;
            font-weight: 800 !important;
            font-size: 14px !important;
        }
        section[data-testid="stSidebar"] input, section[data-testid="stSidebar"] div[role="combobox"] {
            background-color: #FFFFFF !important;
            color: #0F172A !important;
            font-weight: 600 !important;
            border-radius: 6px !important;
        }
        .summary-card {
            background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 100%);
            padding: 20px;
            border-radius: 12px;
            color: white;
            text-align: center;
            box-shadow: 0 4px 12px rgba(15, 23, 42, 0.15);
        }
        .summary-card-light {
            background-color: #FFFFFF;
            border: 2px solid #60A5FA;
            padding: 18px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        }
        .card-label {
            font-size: 14px;
            font-weight: 700;
            color: #93C5FD;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .card-label-dark {
            font-size: 14px;
            font-weight: 700;
            color: #1E3A8A;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .card-value {
            font-size: 26px;
            font-weight: 800;
            color: #FFFFFF;
            margin-top: 5px;
        }
        .card-value-dark {
            font-size: 26px;
            font-weight: 800;
            color: #0F172A;
            margin-top: 5px;
        }
        div[data-testid="stDataFrame"] {
            background-color: #FFFFFF !important;
            border: 2px solid #93C5FD;
            border-radius: 10px;
            overflow: hidden;
        }
        hr {
            border-top: 2px solid #93C5FD;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- HEADER SECTION ---
    st.markdown('<p class="main-header">Umrah Package Cost Calculator</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">ShareTrip Operations | Zero-Error Vendor Quote & Land Package Estimator</p>', unsafe_allow_html=True)
    st.divider()

    # --- SIDEBAR: INPUTS ---
    st.sidebar.markdown("## 0. Client Details")
    client_name = st.sidebar.text_input("Client Name", value="")

    st.sidebar.markdown("## 1. General Inputs")
    pax = st.sidebar.number_input("Total Pilgrims (Pax)", min_value=1, max_value=100, value=2)
    exchange_rate = st.sidebar.number_input("SAR to BDT Exchange Rate", min_value=1.0, value=32.0, step=0.5)
    profit_margin = st.sidebar.slider("Agency Profit Margin (%)", min_value=0, value=10, max_value=50) / 100.0

    st.sidebar.markdown("## 2. Makkah Hotel (Vendor Quote)")
    makkah_name = st.sidebar.text_input("Makkah Hotel Name", value="")
    makkah_rate = st.sidebar.number_input("Makkah DBL Rate / Night (SAR)", min_value=0.0, value=660.0, step=10.0)
    makkah_nights = st.sidebar.number_input("Makkah Total Nights", min_value=1, value=4)

    add_makkah_ex = st.sidebar.checkbox("Add Makkah Extra Bed (EX)?", value=True)
    makkah_ex_rate = 0.0
    if add_makkah_ex:
        makkah_ex_rate = st.sidebar.number_input("Makkah EX Rate / Night (SAR)", min_value=0.0, value=90.0, step=10.0)

    st.sidebar.markdown("## 3. Madinah Hotel (Vendor Quote)")
    madinah_name = st.sidebar.text_input("Madinah Hotel Name", value="")
    madinah_rate = st.sidebar.number_input("Madinah DBL Rate / Night (SAR)", min_value=0.0, value=500.0, step=10.0)
    madinah_nights = st.sidebar.number_input("Madinah Total Nights", min_value=1, value=3)

    add_madinah_ex = st.sidebar.checkbox("Add Madinah Extra Bed (EX)?", value=False)
    madinah_ex_rate = 0.0
    if add_madinah_ex:
        madinah_ex_rate = st.sidebar.number_input("Madinah EX Rate / Night (SAR)", min_value=0.0, value=90.0, step=10.0)

    st.sidebar.markdown("## 4. Sightseeing & Tours Inclusion")
    include_makkah_mazarat = st.sidebar.checkbox("Include Makkah Mazarat", value=True)
    include_madinah_mazarat = st.sidebar.checkbox("Include Madinah Mazarat", value=True)
    include_jeddah_tour = st.sidebar.selectbox("Jeddah Tour", ["No", "Yes"], index=0)
    include_taif_tour = st.sidebar.selectbox("Taif Tour", ["No", "Yes"], index=0)

    # --- JEDDAH HOTEL OPTIONAL SECTION ---
    include_jeddah_hotel = False
    jeddah_name = ""
    jeddah_rate = 0.0
    jeddah_nights = 0
    add_jeddah_ex = False
    jeddah_ex_rate = 0.0

    if include_jeddah_tour == "Yes":
        st.sidebar.markdown("## 5. Jeddah Hotel (Optional Stay)")
        include_jeddah_hotel = st.sidebar.checkbox("Add Jeddah Hotel Stay?", value=False)
        if include_jeddah_hotel:
            jeddah_name = st.sidebar.text_input("Jeddah Hotel Name", value="")
            jeddah_rate = st.sidebar.number_input("Jeddah DBL Rate / Night (SAR)", min_value=0.0, value=450.0, step=10.0)
            jeddah_nights = st.sidebar.number_input("Jeddah Total Nights", min_value=1, value=1)
            add_jeddah_ex = st.sidebar.checkbox("Add Jeddah Extra Bed (EX)?", value=False)
            if add_jeddah_ex:
                jeddah_ex_rate = st.sidebar.number_input("Jeddah EX Rate / Night (SAR)", min_value=0.0, value=90.0, step=10.0)

    st.sidebar.markdown("## 6. Mandatory Services & Inclusions")
    include_visa = st.sidebar.checkbox("Include Visa Processing Fee?", value=True)
    visa_fee_per_pax = 0.0
    if include_visa:
        visa_fee_per_pax = st.sidebar.number_input("Visa Fee Per Person (BDT)", min_value=0.0, value=22000.0, step=500.0)

    include_muallem = st.sidebar.checkbox("Include Muallem Fee?", value=True)
    muallem_fee_group = 0.0
    if include_muallem:
        muallem_fee_group = st.sidebar.number_input("Muallem Fee Per Group (SAR)", min_value=0.0, value=150.0, step=10.0)

    st.sidebar.markdown("## 7. Transport & Luggage Override")
    force_larger_vehicle = st.sidebar.checkbox("Force Larger Vehicle (Extra Luggage / Bags)?", value=False)

    # --- TRANSPORT DATA ---
    transport_data = {
        "Route": [
            "Jeddah Airport to Makkah", "Makkah to Jeddah Airport", 
            "Jeddah Airport to Madinah", "Madinah to Jeddah Airport", 
            "Madinah Airport to Madinah", "Madinah to Madinah Airport", 
            "Makkah to Madinah (Vice Versa)", "Makkah Mazarat", 
            "Madinah Mazarat", "Badr Mazarat", "Jeddah Tour", "Taif Tour"
        ],
        "Car (4 Pax)": [220, 160, 460, 410, 160, 100, 440, 220, 450, 400, 500, 400],
        "Starex (7 Pax)": [245, 170, 560, 510, 170, 120, 470, 245, 480, 450, 600, 550],
        "Staria (7 Pax)": [245, 170, 560, 510, 170, 120, 470, 245, 480, 450, 600, 550],
        "Hiace (10 Pax)": [340, 210, 610, 560, 190, 170, 515, 290, 520, 600, 700, 650],
        "Bus (47 Pax)": [800, 500, 1000, 1000, 500, 400, 1000, 500, 800, 1000, 1000, 1000]
    }
    df_transport = pd.DataFrame(transport_data)

    # Vehicle Logic
    if pax <= 4:
        if force_larger_vehicle:
            vehicle_name = "Starex / Staria (7 Pax) [Luggage Upgraded]"
            col_idx = "Starex (7 Pax)"
        else:
            vehicle_name = "Car (4 Pax)"
            col_idx = "Car (4 Pax)"
    elif pax <= 7:
        if force_larger_vehicle:
            vehicle_name = "Hiace (10 Pax) [Luggage Upgraded]"
            col_idx = "Hiace (10 Pax)"
        else:
            vehicle_name = "Starex / Staria (7 Pax)"
            col_idx = "Starex (7 Pax)"
    elif pax <= 10:
        if force_larger_vehicle:
            vehicle_name = "Bus (47 Pax) [Luggage Upgraded]"
            col_idx = "Bus (47 Pax)"
        else:
            vehicle_name = "Hiace (10 Pax)"
            col_idx = "Hiace (10 Pax)"
    else:
        vehicle_name = "Bus (47 Pax)"
        col_idx = "Bus (47 Pax)"

    # --- CALCULATIONS ---
    eff_makkah_rate = makkah_rate + (makkah_ex_rate if add_makkah_ex else 0.0)
    makkah_total_sar = eff_makkah_rate * makkah_nights

    eff_madinah_rate = madinah_rate + (madinah_ex_rate if add_madinah_ex else 0.0)
    madinah_total_sar = eff_madinah_rate * madinah_nights

    eff_jeddah_rate = jeddah_rate + (jeddah_ex_rate if add_jeddah_ex else 0.0)
    jeddah_total_sar = (eff_jeddah_rate * jeddah_nights) if include_jeddah_hotel else 0.0

    hotel_total_sar = makkah_total_sar + madinah_total_sar + jeddah_total_sar
    hotel_total_bdt = hotel_total_sar * exchange_rate

    visa_total_bdt = pax * visa_fee_per_pax
    muallem_total_bdt = muallem_fee_group * exchange_rate

    def get_route_cost(route_name):
        row = df_transport[df_transport["Route"] == route_name]
        if not row.empty:
            return float(row[col_idx].values[0])
        return 0.0

    routes_needed = [
        "Jeddah Airport to Makkah", 
        "Makkah to Madinah (Vice Versa)", 
        "Madinah to Jeddah Airport"
    ]

    if include_makkah_mazarat:
        routes_needed.append("Makkah Mazarat")
    if include_madinah_mazarat:
        routes_needed.append("Madinah Mazarat")

    service_rows = []
    transport_sar = 0.0

    for r in routes_needed:
        cost = get_route_cost(r)
        transport_sar += cost
        service_rows.append({"Service": r, "Details": vehicle_name, "Cost (SAR)": cost, "Cost (BDT)": cost * exchange_rate})

    if include_jeddah_tour == "Yes":
        cost_jed = get_route_cost("Jeddah Tour")
        transport_sar += cost_jed
        service_rows.append({"Service": "Jeddah City Tour", "Details": vehicle_name, "Cost (SAR)": cost_jed, "Cost (BDT)": cost_jed * exchange_rate})

    if include_taif_tour == "Yes":
        cost_taif = get_route_cost("Taif Tour")
        transport_sar += cost_taif
        service_rows.append({"Service": "Taif City Tour", "Details": vehicle_name, "Cost (SAR)": cost_taif, "Cost (BDT)": cost_taif * exchange_rate})

    transport_bdt = transport_sar * exchange_rate
    total_services_bdt = visa_total_bdt + muallem_total_bdt + transport_bdt

    net_cost_bdt = hotel_total_bdt + total_services_bdt
    profit_amount_bdt = net_cost_bdt * profit_margin
    client_total_bdt = net_cost_bdt + profit_amount_bdt
    per_person_bdt = client_total_bdt / pax

    # --- MAIN DISPLAY AREA ---
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<h3 style='color: #1E3A8A;'>Hotel Accommodation</h3>", unsafe_allow_html=True)
        
        makkah_hotel_display = makkah_name if makkah_name.strip() else "To be specified"
        madinah_hotel_display = madinah_name if madinah_name.strip() else "To be specified"
        jeddah_hotel_display = (jeddah_name if jeddah_name.strip() else "To be specified") if include_jeddah_hotel else "N/A"
        
        makkah_label = f"{makkah_hotel_display} (DBL + EX)" if add_makkah_ex else f"{makkah_hotel_display} (DBL)"
        madinah_label = f"{madinah_hotel_display} (DBL + EX)" if add_madinah_ex else f"{madinah_hotel_display} (DBL)"
        
        hotel_list = [
            {"City": "Makkah", "Hotel": makkah_label, "Rate/Night (SAR)": eff_makkah_rate, "Nights": makkah_nights, "Total (SAR)": makkah_total_sar, "Total (BDT)": makkah_total_sar * exchange_rate},
            {"City": "Madinah", "Hotel": madinah_label, "Rate/Night (SAR)": eff_madinah_rate, "Nights": madinah_nights, "Total (SAR)": madinah_total_sar, "Total (BDT)": madinah_total_sar * exchange_rate}
        ]

        if include_jeddah_hotel:
            jeddah_label = f"{jeddah_hotel_display} (DBL + EX)" if add_jeddah_ex else f"{jeddah_hotel_display} (DBL)"
            hotel_list.append({"City": "Jeddah", "Hotel": jeddah_label, "Rate/Night (SAR)": eff_jeddah_rate, "Nights": jeddah_nights, "Total (SAR)": jeddah_total_sar, "Total (BDT)": jeddah_total_sar * exchange_rate})

        hotel_df = pd.DataFrame(hotel_list)
        st.dataframe(hotel_df, use_container_width=True)
        st.info(f"**Total Hotel Expense:** ৳ {hotel_total_bdt:,.2f} ({hotel_total_sar:,.2f} SAR)")

    with col2:
        st.markdown(f"<h3 style='color: #1E3A8A;'>Transport & Services (<span style='color: #0A192F;'>{vehicle_name}</span>)</h3>", unsafe_allow_html=True)
        
        service_summary_list = []
        if include_visa:
            service_summary_list.append({"Service": "Visa Fee", "Details": f"{pax} Pax × ৳{visa_fee_per_pax:,.0f}", "Cost (SAR)": 0, "Cost (BDT)": visa_total_bdt})
        else:
            service_summary_list.append({"Service": "Visa Fee", "Details": "Excluded by Client", "Cost (SAR)": 0, "Cost (BDT)": 0})
            
        if include_muallem:
            service_summary_list.append({"Service": "Muallem Fee", "Details": "Fixed Group Fee", "Cost (SAR)": muallem_fee_group, "Cost (BDT)": muallem_total_bdt})
        else:
            service_summary_list.append({"Service": "Muallem Fee", "Details": "Excluded by Client", "Cost (SAR)": 0, "Cost (BDT)": 0})
            
        serv_df = pd.DataFrame(service_summary_list + service_rows)
        st.dataframe(serv_df, use_container_width=True)
        st.info(f"**Total Services Expense:** ৳ {total_services_bdt:,.2f} ({transport_sar + muallem_fee_group:,.2f} SAR)")

    st.divider()

    # --- FINAL SUMMARY SECTION WITH BRANDED CARDS ---
    st.markdown("<h3 style='color: #0A192F; text-align: center;'>Final Quotation Summary</h3>", unsafe_allow_html=True)
    st.write("")

    sum_col1, sum_col2, sum_col3 = st.columns(3)

    with sum_col1:
        st.markdown(f"""
            <div class="summary-card-light">
                <div class="card-label-dark">Total Net Cost (Agency)</div>
                <div class="card-value-dark">৳ {net_cost_bdt:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)

    with sum_col2:
        st.markdown(f"""
            <div class="summary-card">
                <div class="card-label">Client Package Price ({int(profit_margin*100)}% Margin)</div>
                <div class="card-value">৳ {client_total_bdt:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)

    with sum_col3:
        st.markdown(f"""
            <div class="summary-card-light">
                <div class="card-label-dark">Per Person Package Price</div>
                <div class="card-value-dark">৳ {per_person_bdt:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)

    st.divider()

    # --- CLIENT READY TEXT GENERATOR SECTION ---
    st.markdown("<h3 style='color: #0A192F;'>Client-Ready Quotation Text (Copy & Paste)</h3>", unsafe_allow_html=True)
    st.write("You can directly copy the text below and send it to your client via WhatsApp or Email:")

    client_display_name = client_name.strip() if client_name.strip() else "Valued Client"

    makkah_room_type = "Double Room Sharing with Extra Bed" if add_makkah_ex else "Double Room Sharing"
    madinah_room_type = "Double Room Sharing with Extra Bed" if add_madinah_ex else "Double Room Sharing"
    jeddah_room_type = "Double Room Sharing with Extra Bed" if add_jeddah_ex else "Double Room Sharing"

    hotel_text_lines = f"• Makkah ({makkah_nights} Nights): {makkah_hotel_display} ({makkah_room_type})\n• Madinah ({madinah_nights} Nights): {madinah_hotel_display} ({madinah_room_type})"
    if include_jeddah_hotel:
        hotel_text_lines += f"\n• Jeddah ({jeddah_nights} Nights): {jeddah_hotel_display} ({jeddah_room_type})"

    quotation_text = f"""UMRAH LAND PACKAGE QUOTATION
-----------------------------------------
Client Name: {client_display_name}
Total Pilgrims (Pax): {pax} Persons

Hotel Accommodation:
{hotel_text_lines}

Transport & Services Included:
• Private Assigned Vehicle ({vehicle_name})
• Airport Transfers & Intercity Transfers
• Makkah Mazarat: {"Included" if include_makkah_mazarat else "Excluded"}
• Madinah Mazarat: {"Included" if include_madinah_mazarat else "Excluded"}
• Jeddah Tour: {include_jeddah_tour}
• Taif Tour: {include_taif_tour}
• Umrah Visa Processing: {"Included" if include_visa else "Excluded"}
• Ground Support & Muallem Service: {"Included" if include_muallem else "Excluded"}

Package Investment:
• Total Package Price: BDT {client_total_bdt:,.2f}
• Per Person Price: BDT {per_person_bdt:,.2f}

(Note: Air ticket is excluded. Rates are subject to availability upon confirmation.)
"""

    st.text_area("Copy Quotation Text Below:", value=quotation_text, height=290)

    st.divider()

    # --- SAVE TO DATABASE & HISTORY SECTION ---
    st.markdown("<h3 style='color: #0A192F;'>Save & View Saved Quotations History</h3>", unsafe_allow_html=True)

    col_save, col_dl = st.columns([1, 1])

    with col_save:
        if st.button("Save Current Quotation to History", use_container_width=True):
            today_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            c.execute('''
                INSERT INTO quotations (date, client_name, pax, makkah_hotel, madinah_hotel, jeddah_hotel, total_price_bdt, per_person_bdt)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (today_str, client_display_name, pax, makkah_hotel_display, madinah_hotel_display, jeddah_hotel_display, client_total_bdt, per_person_bdt))
            conn.commit()
            st.success(f"Quotation for '{client_display_name}' saved successfully!")

    history_df = pd.read_sql_query("SELECT id AS 'ID', date AS 'Date', client_name AS 'Client Name', pax AS 'Pax', makkah_hotel AS 'Makkah Hotel', madinah_hotel AS 'Madinah Hotel', jeddah_hotel AS 'Jeddah Hotel', total_price_bdt AS 'Total (BDT)', per_person_bdt AS 'Per Person (BDT)' FROM quotations ORDER BY id DESC", conn)

    if not history_df.empty:
        with col_dl:
            csv_data = history_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download History as Excel (CSV)",
                data=csv_data,
                file_name=f"umrah_quotations_history_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )

        st.write("#### Previously Saved Quotations History:")
        st.dataframe(history_df, use_container_width=True)
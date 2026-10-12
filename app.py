import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, date, timedelta

st.set_page_config(page_title="Umrah Package Calculator", layout="wide")

APP_PASSWORD = "share123"

def check_password():
    def password_entered():
        if st.session_state.get("password") == APP_PASSWORD:
            st.session_state["password_correct"] = True
            if "password" in st.session_state:
                del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.markdown("<h2 style='text-align: center; margin-top: 50px;'>Umrah Package Calculator - Login</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Please enter your team password to access the calculator.</p>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.markdown("<h2 style='text-align: center; margin-top: 50px;'>Umrah Package Calculator - Login</h2>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.text_input("Password", type="password", on_change=password_entered, key="password")
            st.error("Password incorrect. Please try again.")
        return False
    else:
        return True

if check_password():
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

    try:
        c.execute("ALTER TABLE quotations ADD COLUMN jeddah_hotel TEXT")
        conn.commit()
    except sqlite3.OperationalError:
        pass

    st.title("Umrah Package Cost Calculator")
    st.write("ShareTrip Operations | Zero-Error Vendor Quote & Land Package Estimator")
    st.divider()

    st.sidebar.markdown("### 0. Client Details")
    client_name = st.sidebar.text_input("Client Name", value="")

    st.sidebar.markdown("### 1. General Inputs")
    pax = st.sidebar.number_input("Total Pilgrims (Pax)", min_value=1, max_value=100, value=2)
    exchange_rate = st.sidebar.number_input("SAR to BDT Exchange Rate", min_value=1.0, value=32.0, step=0.5)
    profit_margin = st.sidebar.slider("Agency Profit Margin (%)", min_value=0, value=10, max_value=50) / 100.0

    today = date.today()

    st.sidebar.markdown("### 2. Makkah Hotel (Vendor Quote)")
    makkah_name = st.sidebar.text_input("Makkah Hotel Name", value="")
    makkah_rate = st.sidebar.number_input("Makkah DBL Rate / Night (SAR)", min_value=0.0, value=660.0, step=10.0)
    
    makkah_dates = st.sidebar.date_input("Makkah Stay Dates", value=(today, today + timedelta(days=4)))
    if isinstance(makkah_dates, (tuple, list)) and len(makkah_dates) == 2:
        makkah_checkin, makkah_checkout = makkah_dates
        makkah_nights = max(1, (makkah_checkout - makkah_checkin).days)
    else:
        makkah_checkin, makkah_checkout = today, today + timedelta(days=4)
        makkah_nights = 4

    add_makkah_ex = st.sidebar.checkbox("Add Makkah Extra Bed (EX)?", value=True)
    makkah_ex_rate = st.sidebar.number_input("Makkah EX Rate / Night (SAR)", min_value=0.0, value=90.0, step=10.0) if add_makkah_ex else 0.0

    st.sidebar.markdown("### 3. Madinah Hotel (Vendor Quote)")
    madinah_name = st.sidebar.text_input("Madinah Hotel Name", value="")
    madinah_rate = st.sidebar.number_input("Madinah DBL Rate / Night (SAR)", min_value=0.0, value=500.0, step=10.0)
    
    madinah_dates = st.sidebar.date_input("Madinah Stay Dates", value=(makkah_checkout, makkah_checkout + timedelta(days=3)))
    if isinstance(madinah_dates, (tuple, list)) and len(madinah_dates) == 2:
        madinah_checkin, madinah_checkout = madinah_dates
        madinah_nights = max(1, (madinah_checkout - madinah_checkin).days)
    else:
        madinah_checkin, madinah_checkout = makkah_checkout, makkah_checkout + timedelta(days=3)
        madinah_nights = 3

    add_madinah_ex = st.sidebar.checkbox("Add Madinah Extra Bed (EX)?", value=False)
    madinah_ex_rate = st.sidebar.number_input("Madinah EX Rate / Night (SAR)", min_value=0.0, value=90.0, step=10.0) if add_madinah_ex else 0.0

    st.sidebar.markdown("### 4. Sightseeing & Tours")
    include_makkah_mazarat = st.sidebar.checkbox("Include Makkah Mazarat", value=True)
    include_madinah_mazarat = st.sidebar.checkbox("Include Madinah Mazarat", value=True)
    include_jeddah_tour = st.sidebar.selectbox("Jeddah Tour", ["No", "Yes"], index=0)
    include_taif_tour = st.sidebar.selectbox("Taif Tour", ["No", "Yes"], index=0)

    include_jeddah_hotel = False
    jeddah_name = ""
    jeddah_rate = 0.0
    jeddah_nights = 0
    add_jeddah_ex = False
    jeddah_ex_rate = 0.0
    jeddah_checkin, jeddah_checkout = madinah_checkout, madinah_checkout + timedelta(days=1)

    if include_jeddah_tour == "Yes":
        st.sidebar.markdown("### 5. Jeddah Hotel (Optional Stay)")
        include_jeddah_hotel = st.sidebar.checkbox("Add Jeddah Hotel Stay?", value=False)
        if include_jeddah_hotel:
            jeddah_name = st.sidebar.text_input("Jeddah Hotel Name", value="")
            jeddah_rate = st.sidebar.number_input("Jeddah DBL Rate / Night (SAR)", min_value=0.0, value=450.0, step=10.0)
            jeddah_dates = st.sidebar.date_input("Jeddah Stay Dates", value=(madinah_checkout, madinah_checkout + timedelta(days=1)))
            if isinstance(jeddah_dates, (tuple, list)) and len(jeddah_dates) == 2:
                jeddah_checkin, jeddah_checkout = jeddah_dates
                jeddah_nights = max(1, (jeddah_checkout - jeddah_checkin).days)
            else:
                jeddah_nights = 1
            add_jeddah_ex = st.sidebar.checkbox("Add Jeddah Extra Bed (EX)?", value=False)
            if add_jeddah_ex:
                jeddah_ex_rate = st.sidebar.number_input("Jeddah EX Rate / Night (SAR)", min_value=0.0, value=90.0, step=10.0)

    st.sidebar.markdown("### 6. Mandatory Services")
    include_visa = st.sidebar.checkbox("Include Visa Processing Fee?", value=True)
    visa_fee_per_pax = st.sidebar.number_input("Visa Fee Per Person (BDT)", min_value=0.0, value=22000.0, step=500.0) if include_visa else 0.0

    include_muallem = st.sidebar.checkbox("Include Muallem Fee?", value=True)
    muallem_fee_group = st.sidebar.number_input("Muallem Fee Per Group (SAR)", min_value=0.0, value=150.0, step=10.0) if include_muallem else 0.0

    st.sidebar.markdown("### 7. Transport Override")
    force_larger_vehicle = st.sidebar.checkbox("Force Larger Vehicle (Extra Luggage)?", value=False)

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

    if pax <= 4:
        vehicle_name = "Starex / Staria (7 Pax) [Luggage Upgraded]" if force_larger_vehicle else "Car (4 Pax)"
        col_idx = "Starex (7 Pax)" if force_larger_vehicle else "Car (4 Pax)"
    elif pax <= 7:
        vehicle_name = "Hiace (10 Pax) [Luggage Upgraded]" if force_larger_vehicle else "Starex / Staria (7 Pax)"
        col_idx = "Hiace (10 Pax)" if force_larger_vehicle else "Starex (7 Pax)"
    elif pax <= 10:
        vehicle_name = "Bus (47 Pax) [Luggage Upgraded]" if force_larger_vehicle else "Hiace (10 Pax)"
        col_idx = "Bus (47 Pax)" if force_larger_vehicle else "Hiace (10 Pax)"
    else:
        vehicle_name = "Bus (47 Pax)"
        col_idx = "Bus (47 Pax)"

    eff_makkah_rate = makkah_rate + makkah_ex_rate
    makkah_total_sar = eff_makkah_rate * makkah_nights

    eff_madinah_rate = madinah_rate + madinah_ex_rate
    madinah_total_sar = eff_madinah_rate * madinah_nights

    eff_jeddah_rate = jeddah_rate + jeddah_ex_rate
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

    routes_needed = ["Jeddah Airport to Makkah", "Makkah to Madinah (Vice Versa)", "Madinah to Jeddah Airport"]
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

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Hotel Accommodation")
        makkah_h_disp = makkah_name if makkah_name.strip() else "To be specified"
        madinah_h_disp = madinah_name if madinah_name.strip() else "To be specified"
        jeddah_h_disp = (jeddah_name if jeddah_name.strip() else "To be specified") if include_jeddah_hotel else "N/A"
        
        m_label = f"{makkah_h_disp} (DBL + EX)" if add_makkah_ex else f"{makkah_h_disp} (DBL)"
        md_label = f"{madinah_h_disp} (DBL + EX)" if add_madinah_ex else f"{madinah_h_disp} (DBL)"
        
        h_list = [
            {"City": "Makkah", "Hotel": m_label, "Rate/Night (SAR)": eff_makkah_rate, "Nights": makkah_nights, "Total (SAR)": makkah_total_sar, "Total (BDT)": makkah_total_sar * exchange_rate},
            {"City": "Madinah", "Hotel": md_label, "Rate/Night (SAR)": eff_madinah_rate, "Nights": madinah_nights, "Total (SAR)": madinah_total_sar, "Total (BDT)": madinah_total_sar * exchange_rate}
        ]
        if include_jeddah_hotel:
            j_label = f"{jeddah_h_disp} (DBL + EX)" if add_jeddah_ex else f"{jeddah_h_disp} (DBL)"
            h_list.append({"City": "Jeddah", "Hotel": j_label, "Rate/Night (SAR)": eff_jeddah_rate, "Nights": jeddah_nights, "Total (SAR)": jeddah_total_sar, "Total (BDT)": jeddah_total_sar * exchange_rate})

        st.dataframe(pd.DataFrame(h_list), use_container_width=True)
        st.info(f"Total Hotel Expense: BDT {hotel_total_bdt:,.2f}")

    with col2:
        st.subheader(f"Transport & Services ({vehicle_name})")
        serv_summary = []
        if include_visa:
            serv_summary.append({"Service": "Visa Fee", "Details": f"{pax} Pax", "Cost (SAR)": 0, "Cost (BDT)": visa_total_bdt})
        if include_muallem:
            serv_summary.append({"Service": "Muallem Fee", "Details": "Fixed Group", "Cost (SAR)": muallem_fee_group, "Cost (BDT)": muallem_total_bdt})
        st.dataframe(pd.DataFrame(serv_summary + service_rows), use_container_width=True)
        st.info(f"Total Services Expense: BDT {total_services_bdt:,.2f}")

    st.divider()
    st.subheader("Final Quotation Summary")
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        st.metric("Total Net Cost (Agency)", f"BDT {net_cost_bdt:,.2f}")
    with sc2:
        st.metric(f"Client Package Price ({int(profit_margin*100)}%)", f"BDT {client_total_bdt:,.2f}")
    with sc3:
        st.metric("Per Person Price", f"BDT {per_person_bdt:,.2f}")

    st.divider()
    st.subheader("Client-Ready Quotation Text")
    client_display = client_name.strip() if client_name.strip() else "Valued Client"
    
    makkah_dt_str = f"{makkah_checkin.strftime('%d %b %Y')} to {makkah_checkout.strftime('%d %b %Y')}"
    madinah_dt_str = f"{madinah_checkin.strftime('%d %b %Y')} to {madinah_checkout.strftime('%d %b %Y')}"
    jeddah_dt_str = f"{jeddah_checkin.strftime('%d %b %Y')} to {jeddah_checkout.strftime('%d %b %Y')}"

    hotel_lines = f"• Makkah ({makkah_nights} Nights | {makkah_dt_str}): {makkah_h_disp}\n• Madinah ({madinah_nights} Nights | {madinah_dt_str}): {madinah_h_disp}"
    if include_jeddah_hotel:
        hotel_lines += f"\n• Jeddah ({jeddah_nights} Nights | {jeddah_dt_str}): {jeddah_h_disp}"

    q_text = f"""UMRAH LAND PACKAGE QUOTATION
-----------------------------------------
Client Name: {client_display}
Total Pilgrims (Pax): {pax} Persons

Hotel Accommodation:
{hotel_lines}

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

(Note: Air ticket is excluded. Rates are subject to availability.)"""

    st.text_area("Copy Text:", value=q_text, height=280)

    st.divider()
    st.subheader("Save & History")
    col_s, col_d = st.columns(2)
    with col_s:
        if st.button("Save Quotation", use_container_width=True):
            today_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            c.execute('INSERT INTO quotations (date, client_name, pax, makkah_hotel, madinah_hotel, jeddah_hotel, total_price_bdt, per_person_bdt) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', 
                      (today_str, client_display, pax, makkah_h_disp, madinah_h_disp, jeddah_h_disp, client_total_bdt, per_person_bdt))
            conn.commit()
            st.success("Saved successfully!")

    history_df = pd.read_sql_query("SELECT id AS 'ID', date AS 'Date', client_name AS 'Client Name', pax AS 'Pax', makkah_hotel AS 'Makkah', madinah_hotel AS 'Madinah', jeddah_hotel AS 'Jeddah', total_price_bdt AS 'Total (BDT)', per_person_bdt AS 'Per Person' FROM quotations ORDER BY id DESC", conn)
    if not history_df.empty:
        with col_d:
            st.download_button("Download History as CSV", data=history_df.to_csv(index=False).encode('utf-8'), file_name="history.csv", mime="text/csv", use_container_width=True)
        st.dataframe(history_df, use_container_width=True)
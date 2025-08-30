import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Configuration
API_URL = "http://localhost:5000/api"
ADMIN_PASSWORD = "admin123"  # In production, use environment variables

# Page config
st.set_page_config(
    page_title="De Kinta Homestay Admin",
    page_icon="🔐",
    layout="wide"
)

# Session state initialization
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Login form
def login():
    with st.form("login_form"):
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log Masuk")
        
        if submitted:
            if password == ADMIN_PASSWORD:
                st.session_state.authenticated = True
                st.experimental_rerun()
            else:
                st.error("Password tidak sah")

# Admin dashboard
def admin_dashboard():
    st.title("🏠 De Kinta Homestay Admin Panel")
    
    # Fetch bookings
    try:
        response = requests.get(f"{API_URL}/bookings")
        if response.status_code == 200:
            bookings = response.json()
            
            # Convert to DataFrame
            df = pd.DataFrame(bookings)
            df['created_at'] = pd.to_datetime(df['created_at'])
            df['updated_at'] = pd.to_datetime(df['updated_at'])
            
            # Display statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Jumlah Tempahan", len(df))
            with col2:
                pending = len(df[df['status'] == 'pending'])
                st.metric("Tempahan Menunggu", pending)
            with col3:
                confirmed = len(df[df['status'] == 'confirmed'])
                st.metric("Tempahan Disahkan", confirmed)
            
            # Bookings table
            st.subheader("Senarai Tempahan")
            
            # Add filters
            status_filter = st.selectbox(
                "Tapis mengikut status",
                ["Semua", "pending", "confirmed", "cancelled"]
            )
            
            if status_filter != "Semua":
                df = df[df['status'] == status_filter]
            
            # Display table
            st.dataframe(df[[
                'nama_penuh', 'nama_panggilan', 'tarikh_check_in',
                'tarikh_check_out', 'no_reference', 'status', 'created_at'
            ]])
            
            # Booking management
            st.subheader("Urus Tempahan")
            booking_id = st.selectbox(
                "Pilih ID Tempahan",
                df['id'].tolist()
            )
            
            if booking_id:
                booking = df[df['id'] == booking_id].iloc[0]
                
                col1, col2 = st.columns(2)
                with col1:
                    if booking['status'] != 'confirmed':
                        if st.button("Sahkan Tempahan", key=f"confirm_{booking_id}"):
                            response = requests.put(
                                f"{API_URL}/bookings/{booking_id}",
                                json={"status": "confirmed"}
                            )
                            if response.status_code == 200:
                                st.success("Tempahan disahkan!")
                                st.experimental_rerun()
                
                with col2:
                    if booking['status'] != 'cancelled':
                        if st.button("Batal Tempahan", key=f"cancel_{booking_id}"):
                            response = requests.delete(f"{API_URL}/bookings/{booking_id}")
                            if response.status_code == 200:
                                st.success("Tempahan dibatalkan!")
                                st.experimental_rerun()
                
        else:
            st.error("Tidak dapat memuat data tempahan")
    except Exception as e:
        st.error(f"Ralat: {str(e)}")

# Main app logic
if not st.session_state.authenticated:
    login()
else:
    admin_dashboard()

import streamlit as st
import requests
from datetime import datetime, timedelta
import pandas as pd

# Configuration
API_URL = st.secrets.get("API_URL", "http://localhost:5000/api")  # Will use the secret in production

# Page config
st.set_page_config(
    page_title="De Kinta Homestay Booking",
    page_icon="🏠",
    layout="centered"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton > button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# Title and Info
st.title("🏠 DE KINTA HOMESTAY")
st.markdown("### 📍 Alamat:")
st.markdown("[Klik untuk lihat lokasi di Google Maps](https://maps.app.goo.gl/aCcBEU6VgxuPjq4K8)")

# Get blocked dates from API
def get_blocked_dates():
    try:
        response = requests.get(f"{API_URL}/blocked-dates")
        if response.status_code == 200:
            return [datetime.strptime(date, '%Y-%m-%d').date() for date in response.json()]
        return []
    except:
        return []

# Booking form
with st.form("booking_form"):
    # Personal details
    nama_penuh = st.text_input("Nama Penuh", placeholder="Masukkan nama penuh anda")
    nama_panggilan = st.text_input("Nama Panggilan", placeholder="Masukkan nama panggilan anda")
    
    # Date selection
    col1, col2 = st.columns(2)
    with col1:
        check_in = st.date_input(
            "Tarikh Check-in",
            min_value=datetime.today(),
            value=datetime.today(),
            disabled_dates=get_blocked_dates()
        )
    with col2:
        check_out = st.date_input(
            "Tarikh Check-out",
            min_value=check_in + timedelta(days=1),
            value=check_in + timedelta(days=1),
            disabled_dates=get_blocked_dates()
        )

    # Payment info
    st.markdown("### 💳 Maklumat Pembayaran")
    st.info("""
    Sila buat pembayaran ke akaun:
    
    **MAYBANK: 1570 9149 8195**
    **(MOHAMAD SAFWAN B MD NAZAR)**
    
    Sila gunakan nama panggilan anda sebagai rujukan pembayaran.
    """)
    
    no_reference = st.text_input("No. Reference Resit", placeholder="Masukkan nombor rujukan pembayaran")

    # Submit button
    submitted = st.form_submit_button("Hantar Tempahan")

    if submitted:
        if not all([nama_penuh, nama_panggilan, no_reference]):
            st.error("Sila isi semua maklumat yang diperlukan")
        else:
            # Submit booking to API
            booking_data = {
                "nama_penuh": nama_penuh,
                "nama_panggilan": nama_panggilan,
                "tarikh_check_in": check_in.strftime('%Y-%m-%d'),
                "tarikh_check_out": check_out.strftime('%Y-%m-%d'),
                "no_reference": no_reference
            }
            
            try:
                response = requests.post(f"{API_URL}/bookings", json=booking_data)
                if response.status_code == 201:
                    st.success("Tempahan anda telah berjaya!")
                    st.info("Sila berikan No reference anda kepada nombor yang anda hubungi di Whatsapp")
                    
                    # Clear form (by rerunning the app)
                    st.experimental_rerun()
                else:
                    st.error(response.json().get('error', 'Ralat semasa membuat tempahan'))
            except Exception as e:
                st.error(f"Ralat: {str(e)}")

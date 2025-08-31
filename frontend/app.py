import streamlit as st
import requests
from datetime import datetime, timedelta, date
import pandas as pd
import os

API_URL = os.environ.get("API_URL", "http://localhost:5000/api")

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
    .demo-warning {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #ffc107;
    }
    </style>
    """, unsafe_allow_html=True)

# Demo warning (since API is not deployed yet)
if API_URL == "http://localhost:5000/api":
    st.markdown("""
    <div class="demo-warning">
        <h4>⚠️ Demo Mode</h4>
        <p>Backend API belum disambungkan. Form ini akan berfungsi untuk testing UI sahaja.</p>
    </div>
    """, unsafe_allow_html=True)

# Title and Info
st.title("🏠 DE KINTA HOMESTAY")
st.markdown("### 📍 Alamat:")
st.markdown("[Klik untuk lihat lokasi di Google Maps](https://maps.app.goo.gl/aCcBEU6VgxuPjq4K8)")

# Get blocked dates from API (with fallback for demo)
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_blocked_dates():
    try:
        response = requests.get(f"{API_URL}/blocked-dates", timeout=5)
        if response.status_code == 200:
            dates_data = response.json()
            # Handle different response formats
            if isinstance(dates_data, list):
                return [datetime.strptime(date_str, '%Y-%m-%d').date() for date_str in dates_data]
            elif isinstance(dates_data, dict) and 'blockedDates' in dates_data:
                return [datetime.strptime(date_str, '%Y-%m-%d').date() for date_str in dates_data['blockedDates']]
        return []
    except (requests.RequestException, requests.Timeout):
        # Return demo blocked dates if API is not available
        today = date.today()
        return [
            today + timedelta(days=5),
            today + timedelta(days=6),
            today + timedelta(days=12),
        ]
    except Exception:
        return []

# Get blocked dates
blocked_dates = get_blocked_dates()

# Show blocked dates info
if blocked_dates:
    blocked_dates_str = ", ".join([d.strftime('%d/%m/%Y') for d in blocked_dates[:3]])
    if len(blocked_dates) > 3:
        blocked_dates_str += f" dan {len(blocked_dates) - 3} lagi..."
    st.info(f"📅 Tarikh yang telah ditempah: {blocked_dates_str}")

# Booking form
with st.form("booking_form"):
    # Personal details
    nama_penuh = st.text_input("Nama Penuh *", placeholder="Masukkan nama penuh anda")
    nama_panggilan = st.text_input("Nama Panggilan *", placeholder="Masukkan nama panggilan anda")
    
    # Date selection (FIXED: removed disabled_dates parameter)
    col1, col2 = st.columns(2)
    with col1:
        check_in = st.date_input(
            "Tarikh Check-in *",
            min_value=datetime.today().date(),
            value=datetime.today().date(),
            help="Pilih tarikh check-in anda"
        )
    
    # Check if check-in date is blocked
    if check_in in blocked_dates:
        st.error(f"⚠️ Tarikh {check_in.strftime('%d/%m/%Y')} sudah ditempah. Sila pilih tarikh lain.")
    
    with col2:
        min_checkout = check_in + timedelta(days=1) if check_in else datetime.today().date() + timedelta(days=1)
        check_out = st.date_input(
            "Tarikh Check-out *",
            min_value=min_checkout,
            value=min_checkout,
            help="Pilih tarikh check-out anda"
        )
    
    # Check for blocked dates in range
    if check_in and check_out:
        current_date = check_in
        blocked_in_range = []
        while current_date < check_out:
            if current_date in blocked_dates:
                blocked_in_range.append(current_date.strftime('%d/%m/%Y'))
            current_date += timedelta(days=1)
        
        if blocked_in_range:
            st.error(f"⚠️ Tarikh berikut dalam tempoh anda sudah ditempah: {', '.join(blocked_in_range)}")
    
    # Payment info
    st.markdown("### 💳 Maklumat Pembayaran")
    st.info("""
    Sila buat pembayaran ke akaun:
    
    **MAYBANK: 1570 9149 8195**
    **(MOHAMAD SAFWAN B MD NAZAR)**
    
    Sila gunakan nama panggilan anda sebagai rujukan pembayaran.
    """)
    
    no_reference = st.text_input("No. Reference Resit *", placeholder="Masukkan nombor rujukan pembayaran")
    
    # Submit button
    submitted = st.form_submit_button("📤 Hantar Tempahan", use_container_width=True)
    
    if submitted:
        # Validation
        errors = []
        
        if not nama_penuh.strip():
            errors.append("Nama Penuh diperlukan")
        if not nama_panggilan.strip():
            errors.append("Nama Panggilan diperlukan")
        if not no_reference.strip():
            errors.append("No. Reference Resit diperlukan")
        if not check_in:
            errors.append("Tarikh Check-in diperlukan")
        if not check_out:
            errors.append("Tarikh Check-out diperlukan")
        if check_in and check_out and check_out <= check_in:
            errors.append("Tarikh Check-out mesti selepas tarikh Check-in")
        
        # Check for blocked dates
        if check_in and check_out:
            current_date = check_in
            blocked_found = False
            while current_date < check_out and not blocked_found:
                if current_date in blocked_dates:
                    errors.append(f"Tarikh {current_date.strftime('%d/%m/%Y')} sudah ditempah")
                    blocked_found = True
                current_date += timedelta(days=1)
        
        if errors:
            for error in errors:
                st.error(f"❌ {error}")
        else:
            # Submit booking to API
            booking_data = {
                "nama_penuh": nama_penuh.strip(),
                "nama_panggilan": nama_panggilan.strip(),
                "tarikh_check_in": check_in.strftime('%Y-%m-%d'),
                "tarikh_check_out": check_out.strftime('%Y-%m-%d'),
                "no_reference": no_reference.strip()
            }
            
            with st.spinner("Menghantar tempahan..."):
                try:
                    response = requests.post(f"{API_URL}/bookings", json=booking_data, timeout=10)
                    
                    if response.status_code == 201:
                        st.success("✅ Tempahan anda telah berjaya dihantar!")
                        st.info("📱 Sila berikan No reference anda kepada nombor yang anda hubungi di WhatsApp")
                        st.balloons()
                        
                        # Show booking summary
                        with st.expander("📋 Ringkasan Tempahan"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write("**Nama:**", nama_penuh)
                                st.write("**Panggilan:**", nama_panggilan)
                            with col2:
                                st.write("**Check-in:**", check_in.strftime('%d/%m/%Y'))
                                st.write("**Check-out:**", check_out.strftime('%d/%m/%Y'))
                                duration = (check_out - check_in).days
                                st.write("**Tempoh:**", f"{duration} hari")
                        
                        # Clear cache to refresh blocked dates
                        st.cache_data.clear()
                        
                    elif response.status_code == 400:
                        error_data = response.json()
                        st.error(f"❌ {error_data.get('error', 'Data tidak sah')}")
                    else:
                        st.error(f"❌ Ralat server: {response.status_code}")
                        
                except requests.Timeout:
                    st.error("❌ Masa tamat. Sila cuba lagi.")
                except requests.ConnectionError:
                    if API_URL == "http://localhost:5000/api":
                        st.warning("⚠️ Demo Mode: Tempahan tidak dapat dihantar kerana backend belum disambungkan.")
                        st.info("✅ Namun, form anda telah divalidasi dengan jayanya!")
                    else:
                        st.error("❌ Tidak dapat menyambung ke server. Sila cuba lagi.")
                except Exception as e:
                    st.error(f"❌ Ralat: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 20px;">
    <p>© 2024 DE KINTA HOMESTAY - Sistem Tempahan</p>
    <p>📱 Untuk pertanyaan lanjut, sila hubungi melalui WhatsApp</p>
</div>
""", unsafe_allow_html=True)
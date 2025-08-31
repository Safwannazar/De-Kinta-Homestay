import streamlit as st
import datetime
from datetime import date, timedelta
import time

# Page configuration
st.set_page_config(
    page_title="DE KINTA HOMESTAY - Booking Form",
    page_icon="🏠",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
<style>
.main-header {
    text-align: center;
    color: #2E86C1;
    font-size: 2.5em;
    font-weight: bold;
    margin-bottom: 30px;
}
.info-box {
    background-color: #EBF5FB;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
    border-left: 5px solid #2E86C1;
}
.payment-info {
    background-color: #FDEAA7;
    padding: 20px;
    border-radius: 10px;
    margin: 20px 0;
    border-left: 5px solid #F39C12;
}
.success-message {
    background-color: #D5F4E6;
    padding: 20px;
    border-radius: 10px;
    border-left: 5px solid #27AE60;
    text-align: center;
}
.error-message {
    background-color: #FADBD8;
    padding: 15px;
    border-radius: 10px;
    border-left: 5px solid #E74C3C;
}
.demo-notice {
    background-color: #E8F6F3;
    padding: 15px;
    border-radius: 10px;
    border-left: 5px solid #1ABC9C;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# Demo Notice
st.markdown("""
<div class="demo-notice">
    <h4>🚀 Frontend Demo Mode</h4>
    <p>This is a standalone demo of the frontend interface. Backend and database are not connected yet.</p>
    <p>You can test all the form features - data will be simulated for testing purposes.</p>
</div>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🏠 DE KINTA HOMESTAY</h1>', unsafe_allow_html=True)
st.markdown('<h2 style="text-align: center; color: #5D6D7E;">Booking Form</h2>', unsafe_allow_html=True)

# Homestay Information
st.markdown("""
<div class="info-box">
    <h3>📍 Info DE KINTA HOMESTAY</h3>
    <p><strong>Alamat:</strong> <a href="https://maps.app.goo.gl/aCcBEU6VgxuPjq4K8" target="_blank">
    📍 Klik untuk lihat lokasi di Google Maps</a></p>
</div>
""", unsafe_allow_html=True)

# Mock blocked dates (for demo purposes)
def get_mock_blocked_dates():
    """Return some sample blocked dates for demonstration"""
    today = date.today()
    blocked_dates = [
        today + timedelta(days=5),
        today + timedelta(days=6),
        today + timedelta(days=12),
        today + timedelta(days=13),
        today + timedelta(days=20),
    ]
    return blocked_dates

# Mock booking submission
def mock_submit_booking(nama_penuh, nama_panggilan, check_in, check_out, payment_reference):
    """Simulate booking submission"""
    # Simulate processing time
    time.sleep(2)
    
    # For demo, randomly succeed or show validation errors
    if len(payment_reference) < 5:
        return {'success': False, 'message': 'Reference number terlalu pendek'}, 400
    
    return {'success': True, 'message': 'Booking submitted successfully', 'bookingId': 'DEMO123'}, 200

# Main booking form
st.markdown("## 📝 Maklumat Booking")

# Initialize session state for form data
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False

# Create form with proper submit button
with st.form("booking_form", clear_on_submit=False):
    col1, col2 = st.columns(2)
    
    with col1:
        nama_penuh = st.text_input("Nama Penuh *", placeholder="Masukkan nama penuh anda")
        nama_panggilan = st.text_input("Nama Panggilan *", placeholder="Masukkan nama panggilan anda")
    
    with col2:
        # Date selection with blocked dates
        st.markdown("### 📅 Tarikh Booking")
        
        # Get mock blocked dates
        blocked_dates = get_mock_blocked_dates()
        
        # Show blocked dates info
        if blocked_dates:
            blocked_dates_str = ", ".join([d.strftime('%d/%m/%Y') for d in blocked_dates[:3]])
            if len(blocked_dates) > 3:
                blocked_dates_str += f" dan {len(blocked_dates) - 3} lagi..."
            
            st.info(f"📅 Contoh tarikh yang sudah ditempah: {blocked_dates_str}")
        
        # Date input for check-in (FIXED: removed disabled_dates parameter)
        min_date = date.today()
        max_date = date.today() + timedelta(days=365)
        
        check_in_date = st.date_input(
            "Tarikh Check-in *",
            min_value=min_date,
            max_value=max_date,
            value=min_date,
            help="Pilih tarikh check-in anda"
        )
        
        # Date input for check-out
        if check_in_date:
            min_checkout = check_in_date + timedelta(days=1)
        else:
            min_checkout = min_date + timedelta(days=1)
            
        check_out_date = st.date_input(
            "Tarikh Check-out *",
            min_value=min_checkout,
            max_value=max_date,
            value=min_checkout,
            help="Pilih tarikh check-out anda"
        )
    
    # Show blocked dates warning if any dates in range are blocked
    if check_in_date and check_out_date and blocked_dates:
        current_date = check_in_date
        blocked_in_range = []
        while current_date < check_out_date:
            if current_date in blocked_dates:
                blocked_in_range.append(current_date.strftime('%d/%m/%Y'))
            current_date += timedelta(days=1)
        
        if blocked_in_range:
            st.markdown(f"""
            <div class="error-message">
                <strong>⚠️ Perhatian:</strong> Tarikh berikut tidak tersedia: {', '.join(blocked_in_range)}
                <br>Sila pilih tarikh lain.
            </div>
            """, unsafe_allow_html=True)

    # Payment Information
    st.markdown("""
    <div class="payment-info">
        <h3>💳 Sila buat pembayaran booking ke akaun ini:</h3>
        <p><strong>1570 9149 8195 (Maybank)</strong></p>
        <p><strong>MOHAMAD SAFWAN B MD NAZAR</strong></p>
        <p>📝 Sila letakkan <strong>nama panggilan</strong> seperti di atas sebagai reference.</p>
        <p>Masukkan <strong>No Reference resit sahaja</strong> di bawah:</p>
    </div>
    """, unsafe_allow_html=True)
    
    payment_reference = st.text_input(
        "No Reference Resit *", 
        placeholder="Contoh: TXN123456789",
        help="Masukkan nombor rujukan dari resit pembayaran anda"
    )
    
    # Submit button (FIXED: Added proper submit button)
    st.markdown("---")
    submitted = st.form_submit_button("📤 Submit Booking (Demo Mode)", use_container_width=True, type="primary")

# Form validation and submission (outside the form)
if submitted:
    # Validation
    errors = []
    
    if not nama_penuh.strip():
        errors.append("Nama Penuh diperlukan")
    if not nama_panggilan.strip():
        errors.append("Nama Panggilan diperlukan")
    if not payment_reference.strip():
        errors.append("No Reference Resit diperlukan")
    if not check_in_date:
        errors.append("Tarikh Check-in diperlukan")
    if not check_out_date:
        errors.append("Tarikh Check-out diperlukan")
    if check_in_date and check_out_date and check_out_date <= check_in_date:
        errors.append("Tarikh Check-out mesti selepas tarikh Check-in")
    if check_in_date and check_in_date < date.today():
        errors.append("Tarikh Check-in tidak boleh pada masa lalu")
    
    # Check if dates are blocked
    if check_in_date and check_out_date and blocked_dates:
        current_date = check_in_date
        blocked_found = False
        while current_date < check_out_date and not blocked_found:
            if current_date in blocked_dates:
                errors.append(f"Tarikh {current_date.strftime('%d/%m/%Y')} sudah ditempah")
                blocked_found = True
            current_date += timedelta(days=1)
    
    if errors:
        st.error("❌ Sila betulkan ralat berikut:")
        for error in errors:
            st.error(f"• {error}")
    else:
        # Mock submit booking
        with st.spinner("Menghantar booking... (Demo simulation)"):
            result, status_code = mock_submit_booking(
                nama_penuh.strip(),
                nama_panggilan.strip(),
                check_in_date,
                check_out_date,
                payment_reference.strip()
            )
        
        if result['success']:
            st.markdown("""
            <div class="success-message">
                <h2>✅ Booking Berjaya Dihantar! (Demo)</h2>
                <p><strong>Sila berikan No reference anda kepada nombor yang anda hubungi di WhatsApp</strong></p>
                <p>Terima kasih kerana memilih DE KINTA HOMESTAY! 🏠</p>
                <p><em>Nota: Ini adalah mod demo - tiada tempahan sebenar dibuat</em></p>
            </div>
            """, unsafe_allow_html=True)
            
            # Success balloons
            st.balloons()
            
            # Show submitted data for demo
            with st.expander("📋 Data yang Dihantar (Demo)"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Nama Penuh:**", nama_penuh)
                    st.write("**Nama Panggilan:**", nama_panggilan)
                    st.write("**Reference:**", payment_reference)
                with col2:
                    st.write("**Check-in:**", check_in_date.strftime('%d/%m/%Y'))
                    st.write("**Check-out:**", check_out_date.strftime('%d/%m/%Y'))
                    st.write("**Booking ID:**", "DEMO123")
                
                # Calculate stay duration
                if check_in_date and check_out_date:
                    duration = (check_out_date - check_in_date).days
                    st.write("**Tempoh Penginapan:**", f"{duration} hari")
            
        else:
            st.error(f"❌ {result.get('message', 'Ralat tidak diketahui')}")

# Demo Info Section
st.markdown("---")
st.markdown("## 🧪 Demo Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **✅ Working Features:**
    - Form validation
    - Date selection
    - Blocked dates checking
    - Payment info display
    - Success/error messages
    - Submit button
    """)

with col2:
    st.markdown("""
    **🔄 Simulated:**
    - Booking submission
    - Database connection
    - Date blocking system
    - WhatsApp notification
    - Payment processing
    """)

with col3:
    st.markdown("""
    **📱 Test Scenarios:**
    - Try empty fields
    - Select blocked dates
    - Use short reference number
    - Submit valid form
    - Check mobile view
    """)

# Test Data Section
st.markdown("---")
st.markdown("## 📋 Test Data untuk Demo")

with st.expander("🧪 Contoh Data untuk Testing"):
    col1, col2 = st.columns(2)
    with col1:
        st.code("""
Nama Penuh: Ahmad bin Abdullah
Nama Panggilan: Ahmad
Check-in: Esok
Check-out: Lusa
Reference: TXN123456789
        """)
    with col2:
        st.code("""
Nama Penuh: Siti Fatimah
Nama Panggilan: Siti  
Check-in: 3 hari dari sekarang
Check-out: 5 hari dari sekarang
Reference: REF987654321
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #85929E; padding: 20px;">
    <p>© 2024 DE KINTA HOMESTAY - Sistem Tempahan (Frontend Demo)</p>
    <p>📱 Untuk pertanyaan, sila hubungi melalui WhatsApp</p>
    <p><em>🚀 Ready to connect with backend and database!</em></p>
</div>
""", unsafe_allow_html=True)
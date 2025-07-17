import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import json
import uuid
from geopy.distance import geodesic
import plotly.express as px
import plotly.graph_objects as go

# Configure page
st.set_page_config(
    page_title="BloodConnect - Save Lives",
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #ff6b6b, #ee5a52);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
    }
    .donor-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin-bottom: 1rem;
    }
    .request-card {
        background: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin-bottom: 1rem;
    }
    .urgent-card {
        background: #f8d7da;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
        margin-bottom: 1rem;
    }
    .success-card {
        background: #d4edda;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin-bottom: 1rem;
    }
    .stats-container {
        display: flex;
        justify-content: space-around;
        margin: 1rem 0;
    }
    .stat-item {
        text-align: center;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 8px;
        margin: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'donors' not in st.session_state:
    st.session_state.donors = []
if 'requests' not in st.session_state:
    st.session_state.requests = []
if 'donations' not in st.session_state:
    st.session_state.donations = []
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'notifications' not in st.session_state:
    st.session_state.notifications = []

# Sample data for demonstration
def initialize_sample_data():
    if not st.session_state.donors:
        sample_donors = [
            {
                'id': str(uuid.uuid4()),
                'name': 'John Doe',
                'blood_type': 'O+',
                'phone': '+91-9876543210',
                'location': 'Banjara Hills, Hyderabad',
                'latitude': 17.4126,
                'longitude': 78.4438,
                'status': 'Available',
                'last_donation': datetime.now() - timedelta(days=120),
                'points': 150,
                'badges': ['First Time Donor', 'Regular Donor']
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Sarah Wilson',
                'blood_type': 'A+',
                'phone': '+91-9876543211',
                'location': 'Jubilee Hills, Hyderabad',
                'latitude': 17.4239,
                'longitude': 78.4738,
                'status': 'Available',
                'last_donation': datetime.now() - timedelta(days=90),
                'points': 280,
                'badges': ['Life Saver', 'Hero Donor']
            },
            {
                'id': str(uuid.uuid4()),
                'name': 'Mike Johnson',
                'blood_type': 'B-',
                'phone': '+91-9876543212',
                'location': 'Gachibowli, Hyderabad',
                'latitude': 17.4400,
                'longitude': 78.3489,
                'status': 'Available',
                'last_donation': datetime.now() - timedelta(days=95),
                'points': 200,
                'badges': ['Rare Blood Hero']
            }
        ]
        st.session_state.donors.extend(sample_donors)

# Blood type compatibility
BLOOD_COMPATIBILITY = {
    'O-': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],
    'O+': ['O+', 'A+', 'B+', 'AB+'],
    'A-': ['A-', 'A+', 'AB-', 'AB+'],
    'A+': ['A+', 'AB+'],
    'B-': ['B-', 'B+', 'AB-', 'AB+'],
    'B+': ['B+', 'AB+'],
    'AB-': ['AB-', 'AB+'],
    'AB+': ['AB+']
}

# Main header
st.markdown("""
<div class="main-header">
    <h1>🩸 BloodConnect</h1>
    <p>Connecting Lives, One Donation at a Time</p>
</div>
""", unsafe_allow_html=True)

# Initialize sample data
initialize_sample_data()

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", [
    "🏠 Dashboard",
    "👤 Donor Registration",
    "🆘 Request Blood",
    "🔍 Find Donors",
    "📱 Notifications",
    "📊 Analytics",
    "🏆 Leaderboard"
])

# Helper functions
def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using geopy"""
    return geodesic((lat1, lon1), (lat2, lon2)).kilometers

def find_compatible_donors(blood_type, patient_lat, patient_lon, radius=10):
    """Find compatible donors within radius"""
    compatible_donors = []
    
    for donor in st.session_state.donors:
        if donor['status'] == 'Available':
            # Check blood compatibility
            if blood_type in BLOOD_COMPATIBILITY.get(donor['blood_type'], []):
                # Check distance
                distance = calculate_distance(
                    patient_lat, patient_lon,
                    donor['latitude'], donor['longitude']
                )
                if distance <= radius:
                    donor_info = donor.copy()
                    donor_info['distance'] = distance
                    compatible_donors.append(donor_info)
    
    return sorted(compatible_donors, key=lambda x: x['distance'])

def send_notification(donor_id, message, request_id=None):
    """Send notification to donor"""
    notification = {
        'id': str(uuid.uuid4()),
        'donor_id': donor_id,
        'message': message,
        'timestamp': datetime.now(),
        'request_id': request_id,
        'status': 'unread'
    }
    st.session_state.notifications.append(notification)

# Page content based on navigation
if page == "🏠 Dashboard":
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Donors", len(st.session_state.donors))
    
    with col2:
        active_donors = len([d for d in st.session_state.donors if d['status'] == 'Available'])
        st.metric("Active Donors", active_donors)
    
    with col3:
        pending_requests = len([r for r in st.session_state.requests if r['status'] == 'Active'])
        st.metric("Pending Requests", pending_requests)
    
    with col4:
        total_donations = len(st.session_state.donations)
        st.metric("Completed Donations", total_donations)
    
    # Recent activity
    st.subheader("Recent Activity")
    
    # Show recent requests
    if st.session_state.requests:
        st.write("**Recent Blood Requests:**")
        for request in st.session_state.requests[-3:]:
            urgency_class = "urgent-card" if request['urgency'] == 'Critical' else "request-card"
            st.markdown(f"""
            <div class="{urgency_class}">
                <strong>{request['patient_name']}</strong> needs {request['blood_type']} blood<br>
                Location: {request['location']}<br>
                Urgency: {request['urgency']}<br>
                Contact: {request['contact']}
            </div>
            """, unsafe_allow_html=True)
    
    # Blood type distribution chart
    if st.session_state.donors:
        st.subheader("Blood Type Distribution")
        blood_types = [donor['blood_type'] for donor in st.session_state.donors]
        blood_type_counts = pd.Series(blood_types).value_counts()
        
        fig = px.pie(values=blood_type_counts.values, 
                    names=blood_type_counts.index,
                    title="Available Donors by Blood Type")
        st.plotly_chart(fig, use_container_width=True)

elif page == "👤 Donor Registration":
    st.header("Donor Registration")
    
    with st.form("donor_registration"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name*", placeholder="Enter your full name")
            blood_type = st.selectbox("Blood Type*", 
                                    ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'])
            phone = st.text_input("Phone Number*", placeholder="+91-XXXXXXXXXX")
            age = st.number_input("Age", min_value=18, max_value=65, value=25)
        
        with col2:
            location = st.text_input("Location*", placeholder="Area, City")
            latitude = st.number_input("Latitude", value=17.4126, format="%.6f")
            longitude = st.number_input("Longitude", value=78.4438, format="%.6f")
            medical_conditions = st.multiselect("Medical Conditions", 
                                              ['Diabetes', 'Hypertension', 'Heart Disease', 'None'])
        
        # Terms and conditions
        terms_accepted = st.checkbox("I agree to the terms and conditions*")
        
        submitted = st.form_submit_button("Register as Donor")
        
        if submitted:
            if name and blood_type and phone and location and terms_accepted:
                # Create new donor
                new_donor = {
                    'id': str(uuid.uuid4()),
                    'name': name,
                    'blood_type': blood_type,
                    'phone': phone,
                    'location': location,
                    'latitude': latitude,
                    'longitude': longitude,
                    'age': age,
                    'medical_conditions': medical_conditions,
                    'status': 'Available',
                    'last_donation': None,
                    'points': 0,
                    'badges': ['New Donor'],
                    'registered_date': datetime.now()
                }
                
                st.session_state.donors.append(new_donor)
                st.session_state.current_user = new_donor['id']
                
                st.success("Registration successful! Welcome to BloodConnect!")
                st.balloons()
            else:
                st.error("Please fill all required fields and accept terms.")

elif page == "🆘 Request Blood":
    st.header("Request Blood")
    
    with st.form("blood_request"):
        col1, col2 = st.columns(2)
        
        with col1:
            patient_name = st.text_input("Patient Name*", placeholder="Enter patient name")
            blood_type = st.selectbox("Blood Type Needed*", 
                                    ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'])
            units_needed = st.number_input("Units Needed", min_value=1, max_value=10, value=1)
            urgency = st.selectbox("Urgency Level*", 
                                 ['Critical', 'High', 'Medium', 'Low'])
        
        with col2:
            hospital_name = st.text_input("Hospital Name*", placeholder="Enter hospital name")
            contact = st.text_input("Contact Number*", placeholder="+91-XXXXXXXXXX")
            location = st.text_input("Location*", placeholder="Hospital address")
            additional_info = st.text_area("Additional Information", 
                                         placeholder="Any specific requirements or notes")
        
        # Location coordinates
        req_latitude = st.number_input("Hospital Latitude", value=17.4126, format="%.6f")
        req_longitude = st.number_input("Hospital Longitude", value=78.4438, format="%.6f")
        
        submitted = st.form_submit_button("Submit Request")
        
        if submitted:
            if patient_name and blood_type and hospital_name and contact and location:
                # Create new request
                new_request = {
                    'id': str(uuid.uuid4()),
                    'patient_name': patient_name,
                    'blood_type': blood_type,
                    'units_needed': units_needed,
                    'urgency': urgency,
                    'hospital_name': hospital_name,
                    'contact': contact,
                    'location': location,
                    'latitude': req_latitude,
                    'longitude': req_longitude,
                    'additional_info': additional_info,
                    'status': 'Active',
                    'created_at': datetime.now(),
                    'responses': []
                }
                
                st.session_state.requests.append(new_request)
                
                # Find compatible donors and send notifications
                compatible_donors = find_compatible_donors(
                    blood_type, req_latitude, req_longitude, radius=15
                )
                
                notification_count = 0
                for donor in compatible_donors[:10]:  # Notify top 10 closest donors
                    message = f"🚨 URGENT: {patient_name} needs {blood_type} blood at {hospital_name}. Distance: {donor['distance']:.1f}km"
                    send_notification(donor['id'], message, new_request['id'])
                    notification_count += 1
                
                st.success(f"Request submitted successfully! {notification_count} nearby donors have been notified.")
                
                # Show matched donors
                if compatible_donors:
                    st.subheader("Nearby Compatible Donors")
                    for donor in compatible_donors[:5]:
                        st.markdown(f"""
                        <div class="donor-card">
                            <strong>{donor['name']}</strong> - {donor['blood_type']}<br>
                            Distance: {donor['distance']:.1f}km<br>
                            Location: {donor['location']}<br>
                            Contact: {donor['phone']}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.warning("No compatible donors found in the area. Request has been posted for wider notification.")
            else:
                st.error("Please fill all required fields.")

elif page == "🔍 Find Donors":
    st.header("Find Donors")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        search_blood_type = st.selectbox("Blood Type", 
                                       ['All'] + ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'])
        search_location = st.text_input("Location (optional)", placeholder="Enter location to search")
        radius = st.slider("Search Radius (km)", 1, 50, 10)
        
        # Filter donors
        filtered_donors = st.session_state.donors.copy()
        
        if search_blood_type != 'All':
            filtered_donors = [d for d in filtered_donors if d['blood_type'] == search_blood_type]
        
        # Sort by availability
        filtered_donors.sort(key=lambda x: x['status'] == 'Available', reverse=True)
    
    with col2:
        st.subheader(f"Found {len(filtered_donors)} donors")
        
        for donor in filtered_donors:
            status_color = "28a745" if donor['status'] == 'Available' else "6c757d"
            last_donation = donor['last_donation'].strftime("%B %Y") if donor['last_donation'] else "Never"
            
            st.markdown(f"""
            <div class="donor-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>{donor['name']}</strong> - {donor['blood_type']}<br>
                        Location: {donor['location']}<br>
                        Last Donation: {last_donation}<br>
                        Points: {donor['points']} | Badges: {', '.join(donor['badges'])}
                    </div>
                    <div>
                        <span style="color: #{status_color}; font-weight: bold;">●</span> {donor['status']}<br>
                        <button style="background: #007bff; color: white; border: none; padding: 5px 10px; border-radius: 3px; cursor: pointer;">
                            Contact
                        </button>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Map visualization
    if st.session_state.donors:
        st.subheader("Donor Locations")
        
        # Create map data
        map_data = []
        for donor in filtered_donors:
            map_data.append({
                'lat': donor['latitude'],
                'lon': donor['longitude'],
                'name': donor['name'],
                'blood_type': donor['blood_type'],
                'status': donor['status']
            })
        
        if map_data:
            df = pd.DataFrame(map_data)
            
            # Create map
            fig = px.scatter_mapbox(
                df, lat="lat", lon="lon", 
                hover_name="name",
                hover_data=["blood_type", "status"],
                color="blood_type",
                size_max=15,
                zoom=10,
                height=400
            )
            
            fig.update_layout(
                mapbox_style="open-street-map",
                mapbox=dict(center=dict(lat=17.4126, lon=78.4438))
            )
            
            st.plotly_chart(fig, use_container_width=True)

elif page == "📱 Notifications":
    st.header("Notifications")
    
    # Filter notifications for current user (if logged in)
    user_notifications = st.session_state.notifications
    
    if not user_notifications:
        st.info("No notifications yet.")
    else:
        # Sort by timestamp (newest first)
        user_notifications.sort(key=lambda x: x['timestamp'], reverse=True)
        
        for notification in user_notifications:
            status_class = "success-card" if notification['status'] == 'read' else "request-card"
            
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"""
                <div class="{status_class}">
                    <strong>{notification['message']}</strong><br>
                    <small>{notification['timestamp'].strftime("%Y-%m-%d %H:%M")}</small>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if notification['request_id']:
                    if st.button("Accept", key=f"accept_{notification['id']}"):
                        # Handle acceptance
                        notification['status'] = 'read'
                        st.success("Request accepted! Patient will be notified.")
                    
                    if st.button("Decline", key=f"decline_{notification['id']}"):
                        # Handle decline
                        notification['status'] = 'read'
                        st.info("Request declined.")

elif page == "📊 Analytics":
    st.header("Platform Analytics")
    
    # Time series data for donations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Donation Trends")
        
        # Generate sample time series data
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='M')
        donations_per_month = np.random.randint(10, 50, len(dates))
        
        trend_df = pd.DataFrame({
            'Date': dates,
            'Donations': donations_per_month
        })
        
        fig = px.line(trend_df, x='Date', y='Donations', title='Monthly Donations')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Response Time")
        
        # Sample response time data
        response_times = np.random.normal(15, 5, 100)  # Average 15 minutes
        
        fig = px.histogram(response_times, nbins=20, title='Average Response Time (minutes)')
        st.plotly_chart(fig, use_container_width=True)
    
    # Geographic distribution
    st.subheader("Geographic Distribution")
    
    if st.session_state.donors:
        location_counts = {}
        for donor in st.session_state.donors:
            area = donor['location'].split(',')[0]  # Get area name
            location_counts[area] = location_counts.get(area, 0) + 1
        
        location_df = pd.DataFrame(list(location_counts.items()), columns=['Area', 'Count'])
        
        fig = px.bar(location_df, x='Area', y='Count', title='Donors by Area')
        st.plotly_chart(fig, use_container_width=True)
    
    # Key metrics
    st.subheader("Key Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Average Response Time", "12 minutes", "-2 min")
    
    with col2:
        st.metric("Success Rate", "85%", "+5%")
    
    with col3:
        st.metric("User Satisfaction", "4.8/5", "+0.2")

elif page == "🏆 Leaderboard":
    st.header("Donor Leaderboard")
    
    # Sort donors by points
    top_donors = sorted(st.session_state.donors, key=lambda x: x['points'], reverse=True)
    
    st.subheader("Top Donors")
    
    for i, donor in enumerate(top_donors[:10], 1):
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
        
        st.markdown(f"""
        <div class="donor-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong>{medal} {donor['name']}</strong> - {donor['blood_type']}<br>
                    Badges: {', '.join(donor['badges'])}<br>
                    Location: {donor['location']}
                </div>
                <div style="text-align: right;">
                    <h3 style="margin: 0; color: #007bff;">{donor['points']}</h3>
                    <small>points</small>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Achievement system
    st.subheader("Available Badges")
    
    badges = [
        ("🩸 First Time Donor", "Complete your first donation"),
        ("⭐ Regular Donor", "Donate 3 times"),
        ("🏆 Life Saver", "Donate 10 times"),
        ("💎 Hero Donor", "Donate 25 times"),
        ("🔥 Emergency Responder", "Respond to 5 urgent requests"),
        ("🌟 Rare Blood Hero", "Donate rare blood type"),
        ("📍 Local Champion", "Top donor in your area")
    ]
    
    for badge, description in badges:
        st.markdown(f"""
        <div style="display: flex; align-items: center; margin: 10px 0;">
            <span style="font-size: 24px; margin-right: 10px;">{badge.split()[0]}</span>
            <div>
                <strong>{badge.split(' ', 1)[1]}</strong><br>
                <small>{description}</small>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; margin-top: 2rem;">
    <p>BloodConnect - Connecting Lives, One Donation at a Time</p>
    <p>🚨 Emergency Helpline: 1910 | 📧 Support: help@bloodconnect.org</p>
</div>
""", unsafe_allow_html=True)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import speech_recognition as sr
import threading
import time
import random
import pyttsx3
from streamlit_lottie import st_lottie
import requests
import json
from PIL import Image
import io
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# Set page configuration
st.set_page_config(
    page_title="AI Voice-Controlled Dashboard",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to enhance the UI
st.markdown("""
<style>
    .main-header {
        font-size: 42px !important;
        font-weight: bold;
        color: #4169E1;
        text-align: center;
        margin-bottom: 20px;
    }
    .sub-header {
        font-size: 28px !important;
        font-weight: bold;
        color: #1E90FF;
        margin-top: 30px;
        margin-bottom: 15px;
    }
    .dashboard-section {
        padding: 15px;
        border-radius: 10px;
        background-color: #f0f8ff;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: #333;
    }
    .metric-label {
        font-size: 16px;
        color: #666;
    }
    .voice-button {
        background-color: #4169E1;
        color: white;
        border-radius: 20px;
        padding: 10px 20px;
        margin: 10px;
        text-align: center;
    }
    .status-card {
        padding: 10px;
        border-radius: 5px;
        margin-top: 10px;
        text-align: center;
    }
    .listening {
        background-color: #d4edda;
        color: #155724;
    }
    .not-listening {
        background-color: #f8d7da;
        color: #721c24;
    }
    .help-text {
        font-style: italic;
        color: #6c757d;
        font-size: 14px;
        margin-top: 5px;
    }
    .sidebar-header {
        font-size: 20px !important;
        font-weight: bold;
        color: #4169E1;
        margin-bottom: 10px;
    }
    .footer {
        text-align: center;
        margin-top: 40px;
        padding: 20px;
        font-size: 14px;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

# Function to load Lottie animations
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Load animations
voice_animation = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_49rdyysj.json")
data_animation = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_mbrocy0r.json")
ai_animation = load_lottieurl("https://assets9.lottiefiles.com/packages/lf20_bsPjO9.json")

# Initialize session state variables if they don't exist
if 'listening' not in st.session_state:
    st.session_state.listening = False
if 'last_command' not in st.session_state:
    st.session_state.last_command = "No command received yet"
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "Dashboard"
if 'tts_enabled' not in st.session_state:
    st.session_state.tts_enabled = True
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False
if 'data' not in st.session_state:
    # Create sample data for demonstration
    dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
    sales = np.random.randint(100, 1000, size=len(dates))
    traffic = np.random.randint(1000, 5000, size=len(dates))
    conversion = np.random.uniform(0.01, 0.05, size=len(dates))
    
    # Create regions and categories
    regions = ['North', 'South', 'East', 'West', 'Central']
    categories = ['Electronics', 'Clothing', 'Food', 'Books', 'Home Goods']
    
    # Create customer data
    n_customers = 100
    customer_data = {
        'customer_id': range(1, n_customers + 1),
        'age': np.random.randint(18, 70, size=n_customers),
        'total_spent': np.random.uniform(100, 5000, size=n_customers),
        'purchases': np.random.randint(1, 50, size=n_customers),
        'loyalty_score': np.random.uniform(0, 100, size=n_customers),
        'days_since_last_purchase': np.random.randint(1, 365, size=n_customers),
        'region': np.random.choice(regions, size=n_customers),
        'preferred_category': np.random.choice(categories, size=n_customers)
    }
    
    # Create main dataframe for time series
    st.session_state.data = pd.DataFrame({
        'date': dates,
        'sales': sales,
        'traffic': traffic,
        'conversion_rate': conversion
    })
    
    # Create customer dataframe
    st.session_state.customer_data = pd.DataFrame(customer_data)
    
    # Create product data
    n_products = 50
    product_data = {
        'product_id': range(1, n_products + 1),
        'category': np.random.choice(categories, size=n_products),
        'price': np.random.uniform(10, 500, size=n_products),
        'inventory': np.random.randint(0, 200, size=n_products),
        'rating': np.random.uniform(1, 5, size=n_products),
        'reviews': np.random.randint(0, 500, size=n_products)
    }
    st.session_state.product_data = pd.DataFrame(product_data)

# Voice recognition functions
def recognize_speech():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source, timeout=5, phrase_time_limit=5)
    
    try:
        command = r.recognize_google(audio).lower()
        return command
    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError:
        return "Could not request results"
    except:
        return "Error occurred during speech recognition"

def text_to_speech(text):
    if st.session_state.tts_enabled:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

def listening_thread():
    while st.session_state.listening:
        command = recognize_speech()
        if command and command != "Could not understand audio" and command != "Could not request results" and "error" not in command.lower():
            st.session_state.last_command = command
            
            # Simple command processing
            if "dashboard" in command or "home" in command:
                st.session_state.active_tab = "Dashboard"
                text_to_speech("Showing dashboard view")
            
            elif "customer" in command or "customers" in command:
                st.session_state.active_tab = "Customer Analytics"
                text_to_speech("Showing customer analytics")
            
            elif "product" in command or "products" in command or "inventory" in command:
                st.session_state.active_tab = "Product Analytics"
                text_to_speech("Showing product analytics")
            
            elif "prediction" in command or "predict" in command or "forecast" in command:
                st.session_state.active_tab = "Predictive Analytics"
                text_to_speech("Showing predictive analytics")
                
            elif "setting" in command or "settings" in command or "configuration" in command:
                st.session_state.active_tab = "Settings"
                text_to_speech("Opening settings")
                
            elif "help" in command:
                st.session_state.active_tab = "Help"
                text_to_speech("Showing help information")
                
            elif "stop listening" in command or "stop" in command:
                st.session_state.listening = False
                text_to_speech("Voice control deactivated")
        
        time.sleep(0.1)

# Toggle listening state
def toggle_listening():
    st.session_state.listening = not st.session_state.listening
    if st.session_state.listening:
        text_to_speech("Voice control activated. What would you like to see?")
        threading.Thread(target=listening_thread, daemon=True).start()
    else:
        text_to_speech("Voice control deactivated")

# AI Features for demonstration
def perform_clustering(data, n_clusters=3):
    # Standardize the data
    features = ['total_spent', 'purchases', 'loyalty_score', 'days_since_last_purchase', 'age']
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(data[features])
    
    # Perform K-means clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(scaled_data)
    
    # Add cluster labels to the dataset
    data_with_clusters = data.copy()
    data_with_clusters['cluster'] = clusters
    
    return data_with_clusters, kmeans.cluster_centers_

def perform_pca(data):
    features = ['total_spent', 'purchases', 'loyalty_score', 'days_since_last_purchase', 'age']
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(data[features])
    
    pca = PCA(n_components=2)
    pca_result = pca.fit_transform(scaled_data)
    
    data_pca = data.copy()
    data_pca['pca_1'] = pca_result[:, 0]
    data_pca['pca_2'] = pca_result[:, 1]
    
    return data_pca, pca.explained_variance_ratio_

def forecast_sales(data, periods=7):
    # Very simple forecasting for demonstration
    # In a real application, you'd use more sophisticated methods like ARIMA, Prophet, etc.
    last_date = data['date'].max()
    future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=periods)
    
    # Use a simple linear trend with some randomness
    last_sales = data['sales'].iloc[-periods:].mean()
    trend = (data['sales'].iloc[-1] - data['sales'].iloc[-periods]) / periods
    
    forecast_sales = [last_sales + trend * i + np.random.normal(0, trend) for i in range(1, periods + 1)]
    
    forecast_df = pd.DataFrame({
        'date': future_dates,
        'forecasted_sales': forecast_sales
    })
    
    return forecast_df

# Sidebar
with st.sidebar:
    st.markdown('<div class="sidebar-header">Navigation</div>', unsafe_allow_html=True)
    
    # Voice control animation and button
    col1, col2 = st.columns([1, 2])
    with col1:
        st_lottie(voice_animation, height=80, key="voice_animation")
    with col2:
        st.button("🎙️ Toggle Voice Control", on_click=toggle_listening, key="voice_control_button")
    
    if st.session_state.listening:
        st.markdown('<div class="status-card listening">Listening...</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-card not-listening">Voice Control Inactive</div>', unsafe_allow_html=True)
    
    st.markdown(f"**Last command:** {st.session_state.last_command}")
    
    st.markdown("---")
    
    # Traditional navigation
    options = ["Dashboard", "Customer Analytics", "Product Analytics", "Predictive Analytics", "Settings", "Help"]
    for option in options:
        if st.button(option, key=f"nav_{option}"):
            st.session_state.active_tab = option
    
    st.markdown("---")
    st.markdown('<div class="sidebar-header">Quick Stats</div>', unsafe_allow_html=True)
    
    # Quick stats
    total_sales = st.session_state.data['sales'].sum()
    avg_conversion = st.session_state.data['conversion_rate'].mean() * 100
    total_customers = len(st.session_state.customer_data)
    
    st.metric("Total Sales", f"${total_sales:,.2f}")
    st.metric("Avg. Conversion", f"{avg_conversion:.2f}%")
    st.metric("Total Customers", f"{total_customers}")
    
    st.markdown("---")
    st.markdown('<p class="help-text">Say "show dashboard", "show customers", "show products", "show predictions", or "open settings" to navigate using voice.</p>', unsafe_allow_html=True)

# Main content based on active tab
st.markdown('<h1 class="main-header">AI Voice-Controlled Analytics Dashboard</h1>', unsafe_allow_html=True)

# Dashboard Tab
if st.session_state.active_tab == "Dashboard":
    st.markdown('<div class="dashboard-section">', unsafe_allow_html=True)
    
    # Header with animation
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown('<h2 class="sub-header">Business Overview</h2>', unsafe_allow_html=True)
    with col2:
        st_lottie(data_animation, height=100, key="data_anim")
    
    # Key metrics in cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<p class="metric-value">${st.session_state.data["sales"].iloc[-1]:,.2f}</p>', unsafe_allow_html=True)
        st.markdown('<p class="metric-label">Today\'s Sales</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<p class="metric-value">{st.session_state.data["traffic"].iloc[-1]:,}</p>', unsafe_allow_html=True)
        st.markdown('<p class="metric-label">Today\'s Traffic</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        current_conversion = st.session_state.data["conversion_rate"].iloc[-1] * 100
        st.markdown(f'<p class="metric-value">{current_conversion:.2f}%</p>', unsafe_allow_html=True)
        st.markdown('<p class="metric-label">Conversion Rate</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        active_regions = len(st.session_state.customer_data['region'].unique())
        st.markdown(f'<p class="metric-value">{active_regions}</p>', unsafe_allow_html=True)
        st.markdown('<p class="metric-label">Active Regions</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Sales and Traffic Charts
    st.markdown('<div class="dashboard-section">', unsafe_allow_html=True)
    st.markdown('<h2 class="sub-header">Sales & Traffic Trends</h2>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Line Charts", "Area Charts"])
    
    with tab1:
        fig = px.line(st.session_state.data, x='date', y=['sales', 'traffic'], 
                     title='Sales and Traffic Over Time',
                     labels={'value': 'Value', 'date': 'Date', 'variable': 'Metric'},
                     color_discrete_sequence=['#1E90FF', '#32CD32'])
        fig.update_layout(legend_title_text='', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        fig = px.area(st.session_state.data, x='date', y=['sales', 'traffic'], 
                     title='Sales and Traffic Area Chart',
                     labels={'value': 'Value', 'date': 'Date', 'variable': 'Metric'},
                     color_discrete_sequence=['#1E90FF', '#32CD32'])
        fig.update_layout(legend_title_text='', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Regional Performance
    st.markdown('<div class="dashboard-section">', unsafe_allow_html=True)
    st.markdown('<h2 class="sub-header">Regional Performance</h2>', unsafe_allow_html=True)
    
    region_data = st.session_state.customer_data.groupby('region').agg(
        total_customers=('customer_id', 'count'),
        avg_spend=('total_spent', 'mean'),
        loyalty=('loyalty_score', 'mean')
    ).reset_index()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(region_data, x='region', y='total_customers', 
                     title='Customers by Region',
                     color='region',
                     labels={'total_customers': 'Total Customers', 'region': 'Region'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(region_data, x='region', y='avg_spend', 
                     title='Average Spend by Region',
                     color='region',
                     labels={'avg_spend': 'Average Spend ($)', 'region': 'Region'})
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Category Performance
    st.markdown('<div class="dashboard-section">', unsafe_allow_html=True)
    st.markdown('<h2 class="sub-header">Category Performance</h2>', unsafe_allow_html=True)
    
    category_data = st.session_state.customer_data.groupby('preferred_category').agg(
        total_customers=('customer_id', 'count'),
        avg_spend=('total_spent', 'mean')
    ).reset_index()
    
    fig = px.pie(category_data, values='total_customers', names='preferred_category', 
                 title='Customer Preferences by Category',
                 hole=0.4)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Customer Analytics Tab
elif st.session_state.active_tab == "Customer Analytics":
    st.markdown('<div class="dashboard-section">', unsafe_allow_html=True)
    
    # Header with animation
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown('<h2 class="sub-header">Customer Analytics</h2>', unsafe_allow_html=True)
    with col2:
        st_lottie(ai_animation, height=100, key="ai_anim")
        
    # Customer segmentation with AI
    st.markdown("### Customer Segmentation with AI")
    
    n_clusters = st.slider("Number of Customer Segments", min_value=2, max_value=6, value=3)
    
    # Perform K-means clustering
    clustered_data, centers = perform_clustering(st.session_state.customer_data, n_clusters)
    
    # Display clusters
    fig = px.scatter(clustered_data, x='total_spent', y='loyalty_score', 
                    color='cluster', 
                    hover_data=['age', 'purchases', 'days_since_last_purchase'],
                    title='Customer Segmentation: Spending vs. Loyalty',
                    labels={'total_spent': 'Total Spent ($)', 'loyalty_score': 'Loyalty Score'})
    
    # Add cluster centers
    for i, center in enumerate(centers):
        fig.add_trace(go.Scatter(
            x=[center[0]],  # total_spent
            y=[center[2]],  # loyalty_score
            mode='markers',
            marker=dict(
                color='black',
                size=15,
                symbol='x'
            ),
            name=f'Cluster {i} Center'
        ))
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Cluster profiles
    st.markdown("### Cluster Profiles")
    
    cluster_profiles = clustered_data.groupby('cluster').agg(
        count=('customer_id', 'count'),
        avg_age=('age', 'mean'),
        avg_spent=('total_spent', 'mean'),
        avg_purchases=('purchases', 'mean'),
        avg_loyalty=('loyalty_score', 'mean'),
        avg_days_since_purchase=('days_since_last_purchase', 'mean')
    ).reset_index()
    
    st.dataframe(cluster_profiles.style.highlight_max(axis=0, subset=['count', 'avg_spent', 'avg_loyalty']), use_container_width=True)
    
    # Dimension reduction with PCA
    st.markdown("### Customer Distribution (PCA)")
    
    pca_data, explained_var = perform_pca(st.session_state.customer_data)
    
    fig = px.scatter(pca_data, x='pca_1', y='pca_2', 
                    color='region', 
                    hover_data=['total_spent', 'loyalty_score', 'preferred_category'],
                    title=f'Customer PCA Visualization (Explained Variance: {explained_var[0]:.2%}, {explained_var[1]:.2%})',
                    labels={'pca_1': 'Component 1', 'pca_2': 'Component 2'})
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Customer distribution
    st.markdown("### Customer Demographics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.histogram(st.session_state.customer_data, x='age', 
                         title='Customer Age Distribution',
                         labels={'age': 'Age', 'count': 'Number of Customers'},
                         nbins=10)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.histogram(st.session_state.customer_data, x='days_since_last_purchase', 
                         title='Days Since Last Purchase',
                         labels={'days_since_last_purchase': 'Days', 'count': 'Number of Customers'},
                         nbins=10)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Product Analytics Tab
elif st.session_state.active_tab == "Product Analytics":
    st.markdown('<div class="dashboard-section">', unsafe_allow_html=True)
    
    st.markdown('<h2 class="sub-header">Product Analytics</h2>', unsafe_allow_html=True)
    
    # Product inventory
    st.markdown("### Inventory Status")
    
    # Calculate inventory status
    low_inventory = st.session_state.product_data[st.session_state.product_data['inventory'] < 20]
    out_of_stock = st.session_state.product_data[st.session_state.product_data['inventory'] == 0]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<p class="metric-value">{len(st.session_state.product_data)}</p>', unsafe_allow_html=True)
        st.markdown('<p class="metric-label">Total Products</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<p class="metric-value">{len(low_inventory)}</p>', unsafe_allow_html=True)
        st.markdown('<p class="metric-label">Low Inventory (<20)</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f'<p class="metric-value">{len(out_of_stock)}</p>', unsafe_allow_html=True)
        st.markdown('<p class="metric-label">Out of Stock</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Inventory by category
    st.markdown("### Inventory by Category")
    
    category_inventory = st.session_state.product_data.groupby('category').agg(
        total_products=('product_id', 'count'),
        avg_price=('price', 'mean'),
        total_inventory=('inventory', 'sum'),
        avg_rating=('rating', 'mean')
    ).reset_index()
    
    fig = px.bar(category_inventory, x='category', y='total_inventory', 
                color='category',
                title='Total Inventory by Category',
                labels={'total_inventory': 'Total Inventory', 'category': 'Category'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Price distribution
    st.markdown("### Price Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.box(st.session_state.product_data, x='category', y='price', 
                    color='category',
                    title='Price Distribution by Category',
                    labels={'price': 'Price ($)', 'category': 'Category'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.histogram(st.session_state.product_data, x='price', 
                         title='Overall Price Distribution',
                         labels={'price': 'Price ($)', 'count': 'Number of Products'},
                         nbins=20)
        st.plotly_chart(fig, use_container_width=True)
    
    # Product ratings
    st.markdown("### Product Ratings")
    
    fig = px.scatter(st.session_state.product_data, x='price', y='rating', 
                    color='category', size='reviews',
                    hover_data=['inventory', 'product_id'],
                    title='Product Ratings vs Price',
                    labels={'price': 'Price ($)', 'rating': 'Rating (1-5)', 'reviews': 'Number of Reviews'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Top and bottom products
    st.markdown("### Product Performance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Top Rated Products")
        top_products = st.session_state.product_data.sort_values('rating', ascending=False).head(5)
        st.dataframe(top_products[['product_id', 'category', 'price', 'rating', 'reviews']], use_container_width=True)
    
    with col2:
        st.markdown("#### Lowest Inventory Products")
        low_inv_products = st.session_state.product_data.sort_values('inventory').head(5)
        st.dataframe(low_inv_products[['product_id', 'category', 'price', 'inventory']], use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Predictive Analytics Tab
elif st.session_state.active_tab == "Predictive Analytics":
    st.markdown('<div class="dashboard-section">', unsafe_allow_html=True)
    
    # Header with animation
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown('<h2 class="sub-header">Predictive Analytics</h2>', unsafe_allow_html=True)
    with col2:
        st_lottie(ai_animation, height=100, key="ai_prediction")
    
    # Sales forecasting
    st.markdown("### Sales Forecast")
    
    forecast_days = st.slider("Forecast Horizon (Days)", min_value=7, max_value=30, value=7)
    
    # Generate forecast
    forecast = forecast_sales(st.session_state.data, periods=forecast_days)
    
    # Combine historical and forecasted data
    historical = st.session_state.data[['date', 'sales']].copy()
    historical.columns = ['date', 'value']
    historical['type'] = 'Historical'
    
    forecasted = forecast.copy()
    forecasted.columns = ['date', 'value']
    forecasted['type'] = 'Forecast'
    
    combined = pd.concat([historical, forecasted])
    
    fig = px.line(combined, x='date', y='value', color='type',
                 title='Sales Forecast',
                 labels={'value': 'Sales ($)', 'date': 'Date', 'type': ''},
                 color_discrete_map={'Historical': '#1E90FF', 'Forecast': '#FF4500'})
    
    # Add confidence interval (simplified)
    upper_bound = forecasted.copy()
    upper_bound['value'] = upper_bound['value'] * 1.1
    lower_bound = forecasted.copy()
    lower_bound['value'] = lower_bound['value'] * 0.9
    
    fig.add_scatter(x=upper_bound['date'], y=upper_bound['value'], fill=None, mode='lines', line_color='rgba(255, 69, 0, 0.2)', showlegend=False)
    fig.add_scatter(x=lower_bound['date'], y=lower_bound['value'], fill='tonexty', mode='lines', line_color='rgba(255, 69, 0, 0.2)', showlegend=False)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Customer churn risk prediction (simplified demo)
    st.markdown("### Customer Churn Risk Prediction")
    
    # Calculate a simple churn risk score for demonstration
    st.session_state.customer_data['churn_risk'] = (
        (st.session_state.customer_data['days_since_last_purchase'] / 365) * 0.5 +
        (1 - st.session_state.customer_data['loyalty_score'] / 100) * 0.3 +
        (1 - st.session_state.customer_data['total_spent'] / st.session_state.customer_data['total_spent'].max()) * 0.2
    )
    
    # Normalize to 0-100
    st.session_state.customer_data['churn_risk'] = st.session_state.customer_data['churn_risk'] * 100
    st.session_state.customer_data['churn_risk'] = st.session_state.customer_data['churn_risk'].clip(0, 100)
    
    # Define risk categories
    def risk_category(risk):
        if risk < 30:
            return 'Low'
        elif risk < 60:
            return 'Medium'
        else:
            return 'High'
    
    st.session_state.customer_data['risk_category'] = st.session_state.customer_data['churn_risk'].apply(risk_category)
    
    # Display risk distribution
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.histogram(st.session_state.customer_data, x='churn_risk', 
                         color='risk_category',
                         title='Customer Churn Risk Distribution',
                         labels={'churn_risk': 'Churn Risk Score', 'count': 'Number of Customers'},
                         color_discrete_map={'Low': 'green', 'Medium': 'orange', 'High': 'red'},
                         nbins=20)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        risk_counts = st.session_state.customer_data['risk_category'].value_counts().reset_index()
        risk_counts.columns = ['Risk Category', 'Count']
        
        fig = px.pie(risk_counts, values='Count', names='Risk Category',
                   title='Customer Risk Distribution',
                   color='Risk Category',
                   color_discrete_map={'Low': 'green', 'Medium': 'orange', 'High': 'red'})
        st.plotly_chart(fig, use_container_width=True)
    
    # High-risk customers
    st.markdown("### High-Risk Customers")
    high_risk = st.session_state.customer_data[st.session_state.customer_data['risk_category'] == 'High'].sort_values('churn_risk', ascending=False)
    
    if not high_risk.empty:
        st.dataframe(high_risk[['customer_id', 'region', 'preferred_category', 'total_spent', 'loyalty_score', 'days_since_last_purchase', 'churn_risk']], use_container_width=True)
    else:
        st.info("No high-risk customers detected")
    
    # Product recommendation (simplified demo)
    st.markdown("### Product Recommendation Demo")
    
    selected_customer = st.selectbox("Select Customer ID", st.session_state.customer_data['customer_id'].tolist())
    
    if selected_customer:
        customer_info = st.session_state.customer_data[st.session_state.customer_data['customer_id'] == selected_customer].iloc[0]
        
        # Display customer info
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"**Region:** {customer_info['region']}")
            st.markdown(f"**Age:** {customer_info['age']}")
        
        with col2:
            st.markdown(f"**Total Spent:** ${customer_info['total_spent']:.2f}")
            st.markdown(f"**Purchases:** {customer_info['purchases']}")
        
        with col3:
            st.markdown(f"**Preferred Category:** {customer_info['preferred_category']}")
            st.markdown(f"**Loyalty Score:** {customer_info['loyalty_score']:.2f}")
        
        # Simple recommendation based on category preference
        preferred_category = customer_info['preferred_category']
        
        # Find top rated products in preferred category
        top_recommendations = st.session_state.product_data[
            (st.session_state.product_data['category'] == preferred_category) & 
            (st.session_state.product_data['inventory'] > 0)
        ].sort_values('rating', ascending=False).head(3)
        
        # Find similar products in other categories
        other_recommendations = st.session_state.product_data[
            (st.session_state.product_data['category'] != preferred_category) & 
            (st.session_state.product_data['inventory'] > 0)
        ].sort_values('rating', ascending=False).head(2)
        
        # Combine recommendations
        all_recommendations = pd.concat([top_recommendations, other_recommendations])
        
        st.markdown("#### Recommended Products")
        st.dataframe(all_recommendations[['product_id', 'category', 'price', 'rating', 'reviews']], use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Settings Tab
elif st.session_state.active_tab == "Settings":
    st.markdown('<div class="dashboard-section">', unsafe_allow_html=True)
    st.markdown('<h2 class="sub-header">Settings</h2>', unsafe_allow_html=True)
    
    st.markdown("### Voice Control Settings")
    
    tts_enabled = st.toggle("Enable Text-to-Speech", value=st.session_state.tts_enabled)
    if tts_enabled != st.session_state.tts_enabled:
        st.session_state.tts_enabled = tts_enabled
        if tts_enabled:
            text_to_speech("Text-to-speech enabled")
    
    st.markdown("### Data Settings")
    
    if st.button("Generate New Sample Data"):
        # Generate new sample data
        dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
        sales = np.random.randint(100, 1000, size=len(dates))
        traffic = np.random.randint(1000, 5000, size=len(dates))
        conversion = np.random.uniform(0.01, 0.05, size=len(dates))
        
        # Create main dataframe for time series
        st.session_state.data = pd.DataFrame({
            'date': dates,
            'sales': sales,
            'traffic': traffic,
            'conversion_rate': conversion
        })
        
        # Create customer data
        n_customers = 100
        regions = ['North', 'South', 'East', 'West', 'Central']
        categories = ['Electronics', 'Clothing', 'Food', 'Books', 'Home Goods']
        
        customer_data = {
            'customer_id': range(1, n_customers + 1),
            'age': np.random.randint(18, 70, size=n_customers),
            'total_spent': np.random.uniform(100, 5000, size=n_customers),
            'purchases': np.random.randint(1, 50, size=n_customers),
            'loyalty_score': np.random.uniform(0, 100, size=n_customers),
            'days_since_last_purchase': np.random.randint(1, 365, size=n_customers),
            'region': np.random.choice(regions, size=n_customers),
            'preferred_category': np.random.choice(categories, size=n_customers)
        }
        st.session_state.customer_data = pd.DataFrame(customer_data)
        
        # Create product data
        n_products = 50
        product_data = {
            'product_id': range(1, n_products + 1),
            'category': np.random.choice(categories, size=n_products),
            'price': np.random.uniform(10, 500, size=n_products),
            'inventory': np.random.randint(0, 200, size=n_products),
            'rating': np.random.uniform(1, 5, size=n_products),
            'reviews': np.random.randint(0, 500, size=n_products)
        }
        st.session_state.product_data = pd.DataFrame(product_data)
        
        st.success("New sample data generated!")
        if st.session_state.tts_enabled:
            text_to_speech("New sample data has been generated")
    
    st.markdown("### UI Settings")
    
    dark_mode = st.toggle("Dark Mode (Experimental)", value=st.session_state.dark_mode)
    if dark_mode != st.session_state.dark_mode:
        st.session_state.dark_mode = dark_mode
        if dark_mode:
            st.markdown("""
            <style>
                .main {
                    background-color: #1E1E1E;
                    color: #D8D8D8;
                }
                .dashboard-section {
                    background-color: #2D2D2D;
                }
                .metric-card {
                    background-color: #3D3D3D;
                }
                .metric-value {
                    color: #D8D8D8;
                }
                .metric-label {
                    color: #A0A0A0;
                }
                .status-card.listening {
                    background-color: #143C22;
                    color: #81C784;
                }
                .status-card.not-listening {
                    background-color: #5C1E12;
                    color: #E57373;
                }
                h1, h2, h3, h4, h5, h6 {
                    color: #82AAFF !important;
                }
            </style>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <style>
                .main {
                    background-color: white;
                    color: black;
                }
                .dashboard-section {
                    background-color: #f0f8ff;
                }
                .metric-card {
                    background-color: #f8f9fa;
                }
                .metric-value {
                    color: #333;
                }
                .metric-label {
                    color: #666;
                }
                .status-card.listening {
                    background-color: #d4edda;
                    color: #155724;
                }
                .status-card.not-listening {
                    background-color: #f8d7da;
                    color: #721c24;
                }
                h1, h2, h3, h4, h5, h6 {
                    color: #4169E1 !important;
                }
            </style>
            """, unsafe_allow_html=True)
    
    st.markdown("### About")
    st.markdown("""
    This dashboard was created using:
    - Streamlit
    - SpeechRecognition for voice commands
    - pyttsx3 for text-to-speech
    - Plotly for interactive charts
    - Scikit-learn for AI features
    
    The dashboard demonstrates how voice commands can be used to control a data analytics interface,
    making data exploration more accessible and hands-free.
    """)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Help Tab
elif st.session_state.active_tab == "Help":
    st.markdown('<div class="dashboard-section">', unsafe_allow_html=True)
    st.markdown('<h2 class="sub-header">Help & Voice Commands</h2>', unsafe_allow_html=True)
    
    st.markdown("### Available Voice Commands")
    
    st.markdown("""
    Use the following voice commands to navigate through the dashboard:
    
    - **"Show dashboard"** or **"Home"**: Navigate to the main dashboard view
    - **"Show customers"** or **"Customer analytics"**: View customer analytics and segmentation
    - **"Show products"** or **"Product analytics"**: View product inventory and performance
    - **"Show predictions"** or **"Forecast"**: Access predictive analytics and forecasts
    - **"Open settings"** or **"Settings"**: Access dashboard settings
    - **"Help"**: Show this help screen
    - **"Stop listening"** or **"Stop"**: Deactivate voice control
    
    To activate voice control, click the "Toggle Voice Control" button in the sidebar.
    """)
    
    st.markdown("### Using This Dashboard")
    
    st.markdown("""
    This dashboard provides:
    
    1. **Business Overview**: Key metrics and trends for your business
    2. **Customer Analytics**: AI-powered segmentation and analysis of customer behavior
    3. **Product Analytics**: Inventory status and product performance metrics
    4. **Predictive Analytics**: Sales forecasts, churn prediction, and product recommendations
    5. **Settings**: Customize dashboard behavior and appearance
    
    You can navigate using either the sidebar buttons or voice commands.
    """)
    
    st.markdown("### Setup Instructions")
    
    st.markdown("""
    To deploy this dashboard yourself:
    
    1. **Install Required Packages**:
       ```
       pip install streamlit pandas numpy plotly matplotlib seaborn scikit-learn SpeechRecognition pyttsx3 streamlit-lottie pillow
       ```
    
    2. **PyAudio Requirement**:
       For voice recognition, you'll need PyAudio:
       - Windows: `pip install pyaudio`
       - macOS: `brew install portaudio` then `pip install pyaudio`
       - Linux: `sudo apt-get install python3-pyaudio` or `pip install pyaudio`
    
    3. **Run the Application**:
       ```
       streamlit run app.py
       ```
    
    4. **Deployment on Streamlit Cloud**:
       - Push your code to a GitHub repository
       - Visit [https://streamlit.io/cloud](https://streamlit.io/cloud)
       - Connect your GitHub repository
       - Deploy your app
    """)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div class="footer">
    Voice-Controlled AI Dashboard | Created with Streamlit | Python 3.10
</div>
""", unsafe_allow_html=True)

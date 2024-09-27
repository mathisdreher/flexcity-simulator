# energy_simulator.py

import streamlit as st
import pandas as pd
import numpy as np
import requests

# Initialize session state
if 'step' not in st.session_state:
    st.session_state['step'] = 0

st.title("Simulation of Earnings")

if st.session_state['step'] == 0:
    # Asset Type Selection
    asset_types = ["Battery", "Genset", "CHP", "E-boiler", "Heat Pump"]
    asset_type = st.selectbox("Select Flexible Technology:", asset_types)
    
    # Power Available Input
    power = st.number_input("Power Available for Flexibility (MW):", min_value=0.1, max_value=100.0, step=0.1)
    
    # Proceed Button
    if st.button("Start Simulation"):
        st.session_state['asset_type'] = asset_type
        st.session_state['power'] = power
        st.session_state['step'] = 1

# Step 1: Asset Information
if st.session_state.get('step') == 1:
    st.header("Step 1: Asset Information")
    
    max_loading_capacity = st.number_input("Maximum (Un)loading Capacity (MW):", min_value=0.1, max_value=100.0, step=0.1)
    storage_size = st.number_input("Maximum Total Size of the Storage Reservoir (MWh):", min_value=0.1, max_value=1000.0, step=0.1)
    
    # Calculate upward and downward capacity
    upward_capacity = max_loading_capacity  # Simplified for PoC
    downward_capacity = max_loading_capacity  # Simplified for PoC
    
    st.write(f"Upward Capacity: {upward_capacity} MW")
    st.write(f"Downward Capacity: {downward_capacity} MW")
    
    steerability = st.selectbox("Is the asset fully controllable?", ["Yes", "No"])
    
    if st.button("Next"):
        st.session_state['max_loading_capacity'] = max_loading_capacity
        st.session_state['storage_size'] = storage_size
        st.session_state['steerability'] = steerability
        st.session_state['step'] = 2

# Step 2: Flexibility Constraints
if st.session_state.get('step') == 2:
    st.header("Step 2: Flexibility Constraints")
    
    activation_frequency = st.selectbox("How often can the asset be activated?", ["Every day", "Once a week", "Other"])
    max_activation_time = st.slider("Maximum Activation Time per Day (hours):", min_value=0.25, max_value=24.0, step=0.25)
    
    availability_constraints = st.checkbox("Set Availability Constraints (e.g., maintenance schedules)")
    if availability_constraints:
        unavailable_dates = st.date_input("Select Unavailable Dates", [])
    
    capacity_bidding_price_up = st.number_input("Capacity Bidding Price for Upward Flexibility (€ per MW):", min_value=0.0, step=1.0)
    capacity_bidding_price_down = st.number_input("Capacity Bidding Price for Downward Flexibility (€ per MW):", min_value=0.0, step=1.0)
    
    if st.button("Next"):
        st.session_state['activation_frequency'] = activation_frequency
        st.session_state['max_activation_time'] = max_activation_time
        st.session_state['availability_constraints'] = availability_constraints
        st.session_state['unavailable_dates'] = unavailable_dates if availability_constraints else None
        st.session_state['capacity_bidding_price_up'] = capacity_bidding_price_up
        st.session_state['capacity_bidding_price_down'] = capacity_bidding_price_down
        st.session_state['step'] = 3

# Step 3: Company Information
if st.session_state.get('step') == 3:
    st.header("Step 3: Company Information")
    
    industry_sector = st.selectbox("Industry Sector:", ["Manufacturing", "Energy", "Transportation", "Other"])
    asset_status = st.radio("Asset Status:", ["Existing", "Planned Addition"])
    connection_type = st.radio("Connection Type:", ["TSO (e.g., Elia)", "DSO"])
    location = st.selectbox("Geographical Location:", ["Flanders", "Wallonia", "Brussels"])
    purpose = st.radio("Purpose of Simulation:", ["For Own Company", "As Consultant/Advisor"])
    
    if st.button("View Results"):
        st.session_state['industry_sector'] = industry_sector
        st.session_state['asset_status'] = asset_status
        st.session_state['connection_type'] = connection_type
        st.session_state['location'] = location
        st.session_state['purpose'] = purpose
        st.session_state['step'] = 4

def check_technical_suitability(asset_type, market):
    # Simplified suitability check
    suitable_assets = {
        "FCR": ["Battery", "Genset", "CHP"],
        "aFRR": ["Battery", "CHP"],
        "mFRR": ["Battery", "Genset", "CHP", "E-boiler"],
        "CRM": ["Battery", "Genset", "CHP", "E-boiler", "Heat Pump"]
    }
    return asset_type in suitable_assets.get(market, [])

def estimate_earnings(asset_data, market):
    # Simplified earnings estimation
    base_earnings = {
        "FCR": 50000,
        "aFRR": 40000,
        "mFRR": 30000,
        "CRM": 20000
    }
    power_factor = asset_data['power'] / 10  # Scale earnings by power
    earnings = base_earnings[market] * power_factor
    return earnings

# Step 4: Results
if st.session_state.get('step') == 4:
    st.header("Simulation Results")
    
    asset_data = {
        'asset_type': st.session_state['asset_type'],
        'power': st.session_state['power'],
        'max_loading_capacity': st.session_state['max_loading_capacity'],
        'storage_size': st.session_state['storage_size'],
        'steerability': st.session_state['steerability'],
        'activation_frequency': st.session_state['activation_frequency'],
        'max_activation_time': st.session_state['max_activation_time'],
        'capacity_bidding_price_up': st.session_state['capacity_bidding_price_up'],
        'capacity_bidding_price_down': st.session_state['capacity_bidding_price_down'],
        'industry_sector': st.session_state['industry_sector'],
        'asset_status': st.session_state['asset_status'],
        'connection_type': st.session_state['connection_type'],
        'location': st.session_state['location'],
        'purpose': st.session_state['purpose']
    }
    
    markets = ["FCR", "aFRR", "mFRR", "CRM"]
    
    for market in markets:
        st.subheader(f"{market}")
        suitable = check_technical_suitability(asset_data['asset_type'], market)
        st.write(f"Technical Suitability: {'Yes' if suitable else 'No'}")
        
        if suitable:
            earnings = estimate_earnings(asset_data, market)
            st.write(f"Estimated Annual Earnings: €{earnings:,.2f}")
            
            # Revenue breakdown (simplified)
            capacity_revenue = earnings * 0.7
            energy_revenue = earnings * 0.3
            st.write(f"Capacity Remuneration: €{capacity_revenue:,.2f}")
            st.write(f"Energy Remuneration: €{energy_revenue:,.2f}")
        else:
            st.write("This asset is not suitable for this market.")
    
    st.markdown("[Contact Us](mailto:info@example.com)")

    if st.checkbox("Show Assumptions and Data Sources"):
        st.subheader("Data Sources & Assumptions")
        st.write("""
        - **Market Data**: For this PoC, market data is simulated.
        - **Assumptions**:
            - Pay-as-bid remuneration for aFRR and mFRR.
            - Availability factors are set to 100%.
            - Capacity and energy remuneration percentages are assumed to be 70% and 30%, respectively.
        - **Activation Profiles**: Not implemented in this PoC.
        """)


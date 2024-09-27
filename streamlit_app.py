# energy_simulator.py

import streamlit as st
import pandas as pd
import numpy as np

# Initialize session state
if 'page' not in st.session_state:
    st.session_state['page'] = 'Homepage'

st.set_page_config(page_title="MFRR Revenue Simulator for Flexcity", layout="wide")

# Display Logo and Title
logo = 'https://www.flexcity.energy/sites/g/files/dvc3216/files/Logo-Flexcity-by-Veolia---480x128.jpg'
st.image(logo, width=300)
st.title('MFRR Revenue Simulator for Flexcity')

def navigate_to(page):
    st.session_state['page'] = page

# Define pages
def homepage():
    st.header("Welcome to the Simulation")
    st.write("""
    This tool allows you to simulate potential earnings by participating in the mFRR energy flexibility market.
    Please provide some basic information about your asset to get started.
    """)

    with st.form("asset_form"):
        asset_types = ["Battery", "Genset", "CHP", "E-boiler", "Heat Pump"]
        asset_type = st.selectbox("Select Flexible Technology:", asset_types)

        power = st.number_input(
            "Power Available for Flexibility (MW):",
            value=1.0,
            step=0.1,
            help="Specify the maximum power your asset can provide for flexibility services."
        )

        if asset_type == "Battery":
            storage_size = st.number_input(
                "Total Storage Capacity (MWh):",
                value=1.0,
                step=0.1,
                help="Enter the total energy capacity of your battery."
            )
            st.session_state['storage_size'] = storage_size
        else:
            st.session_state['storage_size'] = None

        steerability = st.selectbox(
            "Is the asset fully controllable?",
            ["Yes", "No"],
            help="Select 'Yes' if your asset's output can be precisely controlled."
        )

        submit = st.form_submit_button("Next")
        if submit:
            st.session_state['asset_type'] = asset_type
            st.session_state['power'] = power
            st.session_state['steerability'] = steerability
            navigate_to('Flexibility Constraints')

def flexibility_constraints():
    st.header("Flexibility Constraints")

    with st.form("constraints_form"):
        activation_frequency = st.selectbox(
            "How often can the asset be activated?",
            ["Multiple times per day", "Once per day", "Once per week", "Other"],
            help="Specify the frequency at which your asset can respond to activation signals."
        )

        max_activation_time = st.slider(
            "Maximum Activation Time per Activation (hours):",
            min_value=0.0,
            max_value=24.0,
            step=0.25,
            value=1.0,
            help="Select the maximum duration your asset can be activated each time."
        )

        availability_constraints = st.selectbox(
            "Do you have any availability constraints?",
            ["No", "Yes"],
            help="Select 'Yes' if there are periods when your asset is unavailable."
        )
        if availability_constraints == "Yes":
            unavailable_dates = st.date_input("Select Unavailable Dates", [])
            st.session_state['unavailable_dates'] = unavailable_dates
        else:
            st.session_state['unavailable_dates'] = None

        capacity_bidding_price = st.number_input(
            "Capacity Bidding Price (€ per MW):",
            value=100.0,
            step=1.0,
            help="Enter your bid price for providing capacity."
        )

        submit = st.form_submit_button("Next")
        if submit:
            st.session_state['activation_frequency'] = activation_frequency
            st.session_state['max_activation_time'] = max_activation_time
            st.session_state['availability_constraints'] = availability_constraints
            st.session_state['capacity_bidding_price'] = capacity_bidding_price
            navigate_to('Company Information')

def company_information():
    st.header("Company Information")

    with st.form("company_form"):
        industry_sector = st.selectbox(
            "Industry Sector:",
            ["Manufacturing", "Energy", "Transportation", "Other"],
            help="Select the industry sector your company operates in."
        )
        asset_status = st.radio(
            "Asset Status:",
            ["Existing", "Planned Addition"],
            help="Indicate whether the asset is currently operational or planned."
        )
        connection_type = st.radio(
            "Connection Type:",
            ["TSO (e.g., Elia)", "DSO"],
            help="Specify if your asset is connected to a Transmission System Operator or Distribution System Operator."
        )
        location = st.selectbox(
            "Geographical Location:",
            ["Flanders", "Wallonia", "Brussels"],
            help="Select the region where your asset is located."
        )
        purpose = st.radio(
            "Purpose of Simulation:",
            ["For Own Company", "As Consultant/Advisor"],
            help="Indicate whether you're simulating for your own company or on behalf of a client."
        )

        submit = st.form_submit_button("View Results")
        if submit:
            st.session_state['industry_sector'] = industry_sector
            st.session_state['asset_status'] = asset_status
            st.session_state['connection_type'] = connection_type
            st.session_state['location'] = location
            st.session_state['purpose'] = purpose
            navigate_to('Results')

def results():
    st.header("Simulation Results")

    asset_data = {
        'asset_type': st.session_state.get('asset_type'),
        'power': st.session_state.get('power'),
        'storage_size': st.session_state.get('storage_size'),
        'steerability': st.session_state.get('steerability'),
        'activation_frequency': st.session_state.get('activation_frequency'),
        'max_activation_time': st.session_state.get('max_activation_time'),
        'availability_constraints': st.session_state.get('availability_constraints'),
        'unavailable_dates': st.session_state.get('unavailable_dates'),
        'capacity_bidding_price': st.session_state.get('capacity_bidding_price'),
        'industry_sector': st.session_state.get('industry_sector'),
        'asset_status': st.session_state.get('asset_status'),
        'connection_type': st.session_state.get('connection_type'),
        'location': st.session_state.get('location'),
        'purpose': st.session_state.get('purpose')
    }

    # Function to check technical suitability
    def check_technical_suitability(asset_type):
        suitable_assets = ["Battery", "Genset", "CHP", "E-boiler"]
        return asset_type in suitable_assets

    # Function to estimate earnings with improved calculations
    def estimate_earnings(asset_data):
        # Assume some base capacity prices (€ per MW per year)
        capacity_price = 50000  # For mFRR
        # Assume some activation probabilities based on activation frequency
        activation_profiles = {
            "Multiple times per day": 0.8,
            "Once per day": 0.5,
            "Once per week": 0.2,
            "Other": 0.1
        }
        activation_probability = activation_profiles.get(asset_data['activation_frequency'], 0.1)
        # Calculate capacity remuneration
        capacity_remuneration = capacity_price * (asset_data['power'])
        # Adjust capacity remuneration based on bidding price
        capacity_remuneration *= (100 / (asset_data['capacity_bidding_price'] or 100))  # Avoid division by zero
        # Calculate energy remuneration
        energy_price = 80  # €/MWh for mFRR
        # Assume average activation time per activation
        avg_activation_time = asset_data['max_activation_time'] * activation_probability
        energy_remuneration = energy_price * asset_data['power'] * avg_activation_time * 365  # Annual estimation
        # Total earnings
        total_earnings = capacity_remuneration + energy_remuneration
        return total_earnings, capacity_remuneration, energy_remuneration

    st.subheader("mFRR Market")
    suitable = check_technical_suitability(asset_data['asset_type'])
    st.write(f"**Technical Suitability**: {'✅ Yes' if suitable else '❌ No'}")

    if suitable:
        total_earnings, capacity_revenue, energy_revenue = estimate_earnings(asset_data)
        st.write(f"**Estimated Annual Earnings**: €{total_earnings:,.2f}")
        st.write(f"- **Capacity Remuneration**: €{capacity_revenue:,.2f}")
        st.write(f"- **Energy Remuneration**: €{energy_revenue:,.2f}")
        # Visualize revenue breakdown
        data = {
            'Revenue Type': ['Capacity', 'Energy'],
            'Earnings (€)': [capacity_revenue, energy_revenue]
        }
        df = pd.DataFrame(data)
        st.bar_chart(df.set_index('Revenue Type'))
    else:
        st.write("This asset is not suitable for the mFRR market.")

    st.markdown("### Next Steps")
    st.write("""
    To proceed with participating in this market or to get more detailed analysis, please [contact us](mailto:info@example.com).
    """)

    if st.checkbox("Show Assumptions and Data Sources"):
        st.subheader("Data Sources & Assumptions")
        st.write("""
        - **Market Data**: Simulated based on average market prices and activation statistics.
        - **Assumptions**:
            - **mFRR** remuneration calculated using pay-as-clear mechanisms.
            - **Availability Factors**: Set to 100% unless availability constraints are specified.
            - **Activation Profiles**: Based on the selected activation frequency.
            - **Energy Prices**: Assumed average energy prices for mFRR market.
        - **Note**: These estimations are for simulation purposes and may not reflect actual market conditions.
        """)

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Previous"):
            navigate_to('Company Information')
    with col2:
        if st.button("Start Over"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state['page'] = 'Homepage'

# Page routing
if st.session_state['page'] == 'Homepage':
    homepage()
elif st.session_state['page'] == 'Flexibility Constraints':
    flexibility_constraints()
elif st.session_state['page'] == 'Company Information':
    company_information()
elif st.session_state['page'] == 'Results':
    results()

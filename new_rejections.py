import streamlit as st
import pandas as pd
from datetime import datetime

# Streamlit app title
st.title("New Rejections Finder 📦")

# File uploaders for yesterday's and today's data
yesterday_file = st.file_uploader("Upload Yesterday's Orders Excel File", type=["xlsx"])
today_file = st.file_uploader("Upload Today's Orders Excel File", type=["xlsx"])


def generate_rejections_filter(df):
    """Filters rejected orders based on status and phase."""
    filter_status = df['Status Name'].isin(["Rejected", 'Confirm Cancellation', 
                                            'Confirmed received by merchant', 
                                            'Ready for Return', 'Received by Merchant'])
    filter_phase = df['Phase Name'].isin(['reject'])
    return df[filter_status | filter_phase]


if yesterday_file and today_file:
    # Read uploaded files
    all_yesterdays_orders = pd.read_excel(yesterday_file, header=3)
    all_todays_orders = pd.read_excel(today_file, header=3)
    
    # Fix phone number formatting
    all_yesterdays_orders['Contact Telephone'] = '+20' + all_yesterdays_orders['Contact Telephone'].astype(str).str[:-2]
    all_todays_orders['Contact Telephone'] = '+20' + all_todays_orders['Contact Telephone'].astype(str).str[:-2]

    # Convert "Created Date" column to datetime using the correct format
    all_todays_orders['Created Date'] = pd.to_datetime(
        all_todays_orders['Created Date'], format="%d/%m/%Y %H:%M:%S", errors='coerce'
    )

    # Calculate days since order was placed
    today = datetime.today()
    all_todays_orders['Days passed'] = (today - all_todays_orders['Created Date']).dt.days

    # Filter rejections
    Yesterdays_Rejections = generate_rejections_filter(all_yesterdays_orders)
    Todays_Rejections = generate_rejections_filter(all_todays_orders)

    # Find new rejections (not in yesterday's file)
    new_rejections = Todays_Rejections[~Todays_Rejections['BareCode'].isin(Yesterdays_Rejections['BareCode'])]

    # Select relevant columns
    columns_to_display = ['BareCode','Customer Name','Contact Telephone', 'City', ' Description', 'Reason','Days passed']
    new_rejections = new_rejections[columns_to_display]

    # Display results
    st.subheader("New Rejections Today")
    st.write(new_rejections)

    # Download button for filtered results
    if not new_rejections.empty:
        @st.cache_data
        def convert_df(df):
            return df.to_csv(index=False).encode('utf-8')

        csv = convert_df(new_rejections)
        st.download_button(
            label="Download New Rejections as CSV",
            data=csv,
            file_name="new_rejections.csv",
            mime="text/csv",
        )

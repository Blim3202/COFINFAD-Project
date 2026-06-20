import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

# Page configuration
st.set_page_config(
    page_title="Customer Behavior Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Get the working directory
print("Current working directory:", os.getcwd())

# Get data function
def get_data():

    # Start Loading
    print("Loading Data:")
    # Transaction data
    transactions = pd.read_csv("data/customer_data.csv")
    # Customer data
    customers = pd.read_csv("data/transactions_data.csv")
    print("Data Loaded:")


    return transactions, customers


transactions, customers = get_data()
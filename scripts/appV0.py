import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import plotly.io as pio

#------------------------------------------- Setup -------------------------------------------#
# Get the working directory
print("Current working directory:", os.getcwd())

# Get data function
def get_data():

    # Start Loading
    print("Loading Data:")
    # Transaction data
    transactions = pd.read_csv("data/transactions_data.csv")
    # Customer data
    customers = pd.read_csv("data/customer_data.csv")
    print("Data Loaded:")


    return transactions, customers

# Load the transactional data and customer data
transactions, customers = get_data()

#------------------------------------------- Calculations -------------------------------------------#
# Calculate key metrics
total_customers = len(customers)
total_lifetime_value = customers['customer_lifetime_value'].sum() / 1_000_000  # Convert to millions
total_monthly_transactions = customers['monthly_transaction_count'].sum()

# Define custom colors for clv_segment
clv_segment_colors = {
    'Bronze': '#CD7F32',
    'Silver': '#8B8A89',
    'Gold': '#FFD700',
    'Platinum': '#EEEEEC'
}

# Get categorical columns with reasonable unique values (< 5)
reasonable_number_categorical = 5
categorical_columns = [col for col in customers.columns 
                      if customers[col].nunique() < reasonable_number_categorical and 
                      col not in ['customer_id', 'customer_lifetime_value']]

#------------------------------------------- Streamlit App -------------------------------------------#
# Page configuration
st.set_page_config(
    page_title="Customer Behavior Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

#  Main app
st.title("Customer Behavior Analytics Dashboard")
st.markdown("Interactive dashboard showcasing customer transaction patterns and behavioral insights")

# Create sidebar filters
st.sidebar.header("Filters")

# Create a metrics row
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Total Customers Surveyed",
        value=f"{total_customers:,}",
        help="Total number of unique customers in the dataset"
    )

with col2:
    st.metric(
        label="Total Lifetime Value (Millions)",
        value=f"${total_lifetime_value:,.0f}M",
        help="Sum of all customer lifetime values in millions"
    )

with col3:
    st.metric(
        label="Total Monthly Transactions",
        value=f"${total_monthly_transactions:,.0f}M",
        help="Sum of all monthly transaction counts"
    )

# Add a divider
st.markdown("---")

# Dropdown for categorical variable
selected_category = st.sidebar.selectbox(
    "Select Categorical Variable",
    categorical_columns
)

# Dropdown for aggregation method (Mean or Median)
aggregation_method = st.sidebar.selectbox(
    "Aggregation Method",
    ['Mean', 'Median']
)

# Prepare data for visualization
clv_by_category = customers.groupby(selected_category)['customer_lifetime_value'].agg(
    aggregation_method.lower() # to format input
).reset_index()
# Shift index to start at 1
clv_by_category.index += 1

# Special case. Define the clv_segment order
segment_order = ['Bronze', 'Silver', 'Gold', 'Platinum']

# If the selected category is 'clv_segment', enforce the order
if selected_category == 'clv_segment':
    clv_by_category[selected_category] = pd.Categorical(
        clv_by_category[selected_category],
        categories=segment_order,
        ordered=True
    )
    clv_by_category = clv_by_category.sort_values(selected_category)

# Create bar chart with interactivity (special colouring for clv_segment)
if selected_category == 'clv_segment':
    fig = px.bar(
        clv_by_category,
        x=selected_category,
        y='customer_lifetime_value',
        title=f'Customer Lifetime Value by {selected_category}',
        labels={'customer_lifetime_value': f'CLV ({aggregation_method})'},
        color=selected_category,
        color_discrete_map=clv_segment_colors,  # Use custom colors
        text='customer_lifetime_value',
        hover_data={'customer_lifetime_value': ':,.2f'}
    )
else:
    fig = px.bar(
        clv_by_category,
        x=selected_category,
        y='customer_lifetime_value',
        title=f'Customer Lifetime Value by {selected_category}',
        labels={'customer_lifetime_value': f'CLV ({aggregation_method})'},
        color=selected_category,
        color_discrete_sequence=px.colors.qualitative.Plotly,  # Default colors
        text='customer_lifetime_value',
        hover_data={'customer_lifetime_value': ':,.2f'}
    )

# Format chart
fig.update_traces(
    texttemplate='%{y:,.0f}',
    textposition='outside',
    hovertemplate='<b>%{x}</b><br>CLV: %{y:,.2f}<extra></extra>'
)

# Add interactivity
fig.update_layout(
    clickmode='event+select',
    hoverlabel=dict(bgcolor='white', font_size=14),
    title={
        'font': {'size': 24}  # Adjust size here
    }
)

# Display chart
st.plotly_chart(fig, use_container_width=True)

# Add data table for detailed view
# st.subheader("Detailed Values")
st.markdown(f"**Customer Lifetime Value: Table Breakdown ({aggregation_method})**")
st.dataframe(
    clv_by_category.style.format({'customer_lifetime_value': '${:,.0f}'}),
    use_container_width=True
)

#-----------------------------------------------------------------------------------------------------#







#--------------------------Archive Testing
# # List the relevant segments
# segments = ['Bronze', 'Silver', 'Gold', 'Platinum']


# # Get numerical columns
# numerical_cols = customers.select_dtypes(include=[np.number]).columns.tolist()
# # print(numerical_cols)

# # Create aggregation filter (Mean or Median)
# # aggregation_method = st.selectbox("Select Aggregation Method", ["Mean", "Median"])

# # Pre calculate the dataframes
# clv_segment_stats_mean = customers.groupby('clv_segment')[numerical_cols].mean()
# clv_segment_stats_median = customers.groupby('clv_segment')[numerical_cols].median()


# clv_segment_stats = clv_segment_stats_mean
# # Swap the statistics
# # if aggregation_method == "Mean":
# #     clv_segment_stats = clv_segment_stats_mean
# # else:
# #     clv_segment_stats = clv_segment_stats_median

# # Reindex to ensure segment order
# # clv_segment_stats = clv_segment_stats.reindex(segments)
# print(clv_segment_stats)


# # Create heatmap
# fig = go.Figure(data=go.Heatmap(
#     z=clv_segment_stats.values,
#     x=clv_segment_stats.columns,
#     y=clv_segment_stats.index,
#     colorscale='Viridis',
#     hoverongaps=False
# ))

# # Update layout for better visualization
# fig.update_layout(
#     title='Customer Segments by Numerical Attributes',
#     xaxis=dict(
#         tickangle=45,
#         title='Customer Descriptors (Numerical)',
#         automargin=True
#     ),
#     yaxis=dict(
#         title='Customer Segment Tier'
#     ),
#     height=600,
#     width=1200
# )

# pio.show(fig)
# # Display the plot
# # st.plotly_chart(fig, use_container_width=True)
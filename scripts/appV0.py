import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

#-----------------------------------------------------------------------------------------------------#
#----------------------------------------------- Setup -----------------------------------------------#
#-----------------------------------------------------------------------------------------------------#

# Get the working directory
# print("Current working directory:", os.getcwd())

# Get data function
@st.cache_data # Cache the loading IMPORTANT
def get_data():

    # Start Loading
    # print("Loading Data:")
    # Transaction data
    transactions = pd.read_csv("data/transactions_data.csv")
    # Customer data
    customers = pd.read_csv("data/customer_data.csv")
    # print("Data Loaded:")


    return transactions, customers

# Load the transactional data and customer data
transactions, customers = get_data()

# Define color palette
colors = {
    'primary_maroon': '#360829',
    'bright_pink': '#ff57bf',
    'soft_white': "#fdf7fc",
    'soft_gray':'#faf5f7',
    'gray':"#ccc9ca",
    'white': '#ffffff',
    'black': '#000000'
}

# Define custom colors for clv_segment
clv_segment_colors = {
    'Bronze': '#CD7F32',
    'Silver': '#8B8A89',
    'Gold': '#FFD700',
    'Platinum': '#f7f7f7'
}

pcolors = px.colors.qualitative.Plotly  # This gives you the standard Plotly colors

#----------------------------------------------------------------------------------------------------#
#------------------------------------------- Calculations -------------------------------------------#
#----------------------------------------------------------------------------------------------------#

# Calculate key customer metrics
total_customers = len(customers)
total_lifetime_value = customers['customer_lifetime_value'].sum() / 1_000_000  # Convert to millions
total_monthly_transactions = customers['monthly_transaction_count'].sum()

# Calculate key transaction metrics
total_transactions = len(transactions)
average_transaction_value = transactions['amount'].mean()

# Get categorical columns with reasonable unique values (< 5)
reasonable_number_categorical = 5
categorical_columns = [col for col in customers.columns 
                        if customers[col].nunique() < reasonable_number_categorical and 
                        col not in ['customer_id', 'customer_lifetime_value'] and
                        customers[col].notnull().all()]

# Special treatment for CLV segment
segment_order = ['Bronze', 'Silver', 'Gold', 'Platinum']
customers['clv_segment'] = pd.Categorical(
        customers['clv_segment'],
        categories=segment_order,
        ordered=True
    )

# Identify numerical columns (excluding columns with missing values or non-numeric types)
# numerical_columns = []
# for col in customers.columns:
#     if pd.api.types.is_numeric_dtype(customers[col]) and customers[col].notnull().all() and col != 'churn_probability':
#             numerical_columns.append(col) 

# These are the only numerical ones that make sense to be plotted for churn
numerical_columns = ['active_products','app_logins_frequency','app_logins_frequency','international_transactions','failed_transactions',
                     'failed_transactions','satisfaction_score','satisfaction_score','satisfaction_score','app_store_rating']

# Transaction Analysis Calculations
# Convert date to datetime and extract month
transactions['date'] = pd.to_datetime(transactions['date'], format='%Y-%m-%d', errors='coerce')
transactions['month'] = transactions['date'].dt.to_period('M')
# print(transactions.head(20))

# Get the minimum and maximum month
min_month = transactions['month'].min()
max_month = transactions['month'].max()
months_list = [str(month) for month in pd.period_range(start=min_month, end=max_month, freq="M")]
# print(months_list)
min_month = min_month.strftime('%Y-%m')
max_month = max_month.strftime('%Y-%m')
# print(min_month,type(min_month),max_month,type(max_month))

#Cache the pivoting
@st.cache_data
def create_transaction_pivot(transactions):

    # Group by month and transaction type, summing amounts
    monthly_transactions = transactions.groupby(['month', 'type'])['amount'].sum().reset_index()

    # Get all unique months in order
    all_months = pd.period_range(start=transactions['month'].min(),
                                end=transactions['month'].max(),
                                freq='M')

    # Pivot the data for plotting
    pivot = monthly_transactions.pivot(index='month', columns='type', values='amount').fillna(0)
    return pivot.reindex(all_months, fill_value=0)

# Load the cachecd function
transaction_pivot = create_transaction_pivot(transactions)
#-----------------------------------------------------------------------------------------------------#
#------------------------------------------- Streamlit App -------------------------------------------#
#-----------------------------------------------------------------------------------------------------#

# Page configuration
st.set_page_config(
    page_title="Customer Behavior Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject custom CSS – Streamlit needs the `unsafe_allow_html=True` flag
st.markdown(
    f"""
    <style>
        /* 1. Reduce the top padding of the main block‑container */
        .reportview-container .main .block-container {{
        padding-top: 0.1rem;   /* try 0.2rem‑1rem until it looks right */
        }}

        /* 2. Target the main sidebar container and heading levels */
        section[data-testid="stSidebar"] {{
            background-color: {colors['soft_gray']};
        }}
        section[data-testid="stSidebar"] .stSelectbox label, {{
            color: {colors['black']} !important;
        }}
        [data-testid="stSidebar"] h2 {{
            color: {colors['primary_maroon']} !important;
        }}

        /* 3. Targets titles, section headers, subheaders, etc */
        h1 {{
            color: {colors['bright_pink']} !important;
        }}
        h2, h3, h4, h5, h6
        [data-testid="stHeader"] h1 {{
            color: {colors['primary_maroon']} !important;
        }}

        /* 4. Create the Metric Card effect */
        [data-testid="stMetric"] {{
            # background-color: {colors['soft_white']}; 
            border: 1px solid {colors['gray']};
            border-radius: 15px;
            padding: 10px 50px;
            # box-shadow: 2px 2px 10px rgba(0,0,0,0.25);
            transition: transform 0.3s ease;
        }}

        /* 5. Style the plotly chart container */
        .stPlotlyChart {{
            # background-color: {colors['soft_white']};
            # border: 1px solid {colors['primary_maroon']};
            border-radius: 15px;
            # padding: 10px 20px;  /* 0 vertical padding, 20px horizontal padding */
            # margin: 10px;   /* Add margin to ensure space around the container */
            # box-shadow: 2px 2px 10px rgba(0,0,0,0.25);
            transition: transform 0.3s ease;
        }}

    </style>
    """,
    unsafe_allow_html=True
)

# Add a logo to the top left
st.logo("resources/Octicons-mark-github.svg",
        link="https://github.com/Blim3202/COFINFAD-Project",
        size="large")


#  Main app
st.title("Customer Behavior Analytics Dashboard")
st.markdown("Interactive dashboard showcasing customer transaction patterns and behavioral insights. All $ values are in Columbian Pesos. \n\n" \
"***About the data***: *This data was based on behavioral and transactional data from 48,723 customers of a Colombian fintech company, collected over 12 months from January 4, 2023, to December 29, 2023. Comprises 3,159,157 individual transactions and was designed to support research on customer retention, financial behavior analysis, and digital financial service adoption in Latin American emerging markets.*")

#---------------------------------------------------------------------------------------------------------#

# # Add a divider
# st.markdown("---")

# Add a quick overview
st.header("Overview")

# Create sidebar filters
st.sidebar.header(":material/filter_alt: Filters")


# Dropdown for categorical variable
selected_category = st.sidebar.selectbox(
    "Select Categorical Variable",
    categorical_columns,
    index=categorical_columns.index('clv_segment'),
    help="Select the main categorical variable to analyse"
)

# Dropdown for SECONDARY categorical variable
selected_category_secondary = st.sidebar.selectbox(
    "Select Secondary Categorical Variable",
    categorical_columns,
    index=categorical_columns.index('preferred_transaction_type'),
    help="Secondary categorical variable to plot against. Used for Churn Heatmap"
)

# Dropdown for numerical column
selected_numerical_column = st.sidebar.selectbox(
    "Select Numerical Column",
    numerical_columns,
    index=0, # Active products
    help="Non-Continuous numerical variables only"
)

# Dropdown for aggregation method (Mean or Median)
aggregation_method = st.sidebar.selectbox(
    "Aggregation Method",
    ['Mean', 'Median'],
    index=1,
    help="Aggregation method to be applied where applicable"
)

# Dropdown for selecting a numerical column

# Create a customer metrics row
col1a, col2a, col3a = st.columns(3)

with col1a:
    st.metric(
        label="Total Customers Surveyed",
        value=f"{total_customers:,}",
        help="Total number of unique customers in the dataset"
    )
with col2a:
    st.metric(
        label="Total Lifetime Value (Millions)",
        value=f"${total_lifetime_value:,.0f}M",
        help="Sum of all customer lifetime values in millions"
    )
with col3a:
    st.metric(
        label="Total Monthly Transactions",
        value=f"${total_monthly_transactions:,.0f}M",
        help="Sum of all monthly transaction counts"
    )

# Create a transaction metrics row
col1b, col2b = st.columns(2)

with col1b:
    st.metric(
        label="Total Amount of Transactions",
        value=f"{total_transactions:,}",
        help="Total number of unique transactions in the dataset"
    )
with col2b:
    st.metric(
        label="Average Tansaction Value",
        value=f"${average_transaction_value:,.0f}",
        help="Average transaction value over all customer trasactions"
    )

#---------------------------------------------------------------------------------------------------------#

# # Add a divider
# st.markdown("---")

## CLV Section
# Add a header for customer lifetime value plot
st.header("Customer Lifetime Value")

# Prepare data for visualization
clv_by_category = customers.groupby(selected_category)['customer_lifetime_value'].agg(
    aggregation_method.lower() # to format input
).reset_index()
# Shift index to start at 1
clv_by_category.index += 1

# Create bar chart with interactivity (special colouring for clv_segment)
if selected_category == 'clv_segment':
    fig = px.bar(
        clv_by_category,
        x=selected_category,
        y='customer_lifetime_value',
        title=f'{aggregation_method} Customer Lifetime Value by {selected_category}',
        labels={'customer_lifetime_value': f'CLV ({aggregation_method}) In $'},
        color=selected_category,
        color_discrete_map=clv_segment_colors,  # Use custom colors
        text='customer_lifetime_value',
        hover_data={'customer_lifetime_value': ':,.2f'}
    )
else: # All other columns
    fig = px.bar(
        clv_by_category,
        x=selected_category,
        y='customer_lifetime_value',
        title=f'{aggregation_method} Customer Lifetime Value by {selected_category}',
        labels={'customer_lifetime_value': f'CLV ({aggregation_method}) In $'},
        color=selected_category,
        color_discrete_sequence=pcolors,  # Default colors
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
    # width=2000,  # Set a fixed width
    # height=400,  # Set a fixed height
    clickmode='event+select',
    hoverlabel=dict(bgcolor='white', font_size=14),
    title={
        'font': {'size': 24}  # Adjust size here
    }
)

# Make the plot transparent to allow CSS formatting to take over:
fig.update_layout(
    plot_bgcolor='rgba(255, 255, 255, 0)',
    paper_bgcolor='rgba(255, 255, 255, 0)',
    margin=dict(l=200, r=200, t=50, b=50),  # Start with small base margins
)

# Display chart
st.plotly_chart(fig, width='stretch')

# Add data table for detailed view
with st.expander("Table View", icon=":material/table_view:"):
    st.dataframe(
        clv_by_category.style
        .format({'customer_lifetime_value': '${:,.0f}'})
        .set_table_styles([{
            'selector': 'th',
            'props': [('background-color', colors['soft_white'])]
        }]),
        width='stretch'
    )

#---------------------------------------------------------------------------------------------------------#

## Transactions Section
# Add a header for transaction history section
st.header("Transaction Behaviours")

# Placeholder for col to be visualised first
colc_placeholder = st.empty()


# Slider that lets the user pick a single month (or you can use a range slider)
selected_month = st.select_slider(
    "Select month",
    options=months_list,
    value=months_list[0]          # default to the first month
)
selected_month_name = datetime.strptime(selected_month, "%Y-%m").strftime("%B %Y")
# st.write(f"You selected: {selected_month}")
st.write(selected_month_name)

# Render the placeholder
with colc_placeholder.container():

    # Add transaction behavior analysis in columns
    col1c, col2c = st.columns(2)
    with col1c:
        # Create stacked area chart
        fig_transactions = go.Figure()

        for i, transaction_type in enumerate(transaction_pivot.columns):
            fig_transactions.add_trace(go.Scatter(
                x=transaction_pivot.index.astype(str),
                y=transaction_pivot[transaction_type],
                name=transaction_type,
                mode='lines',
                stackgroup='one',
                line=dict(color=pcolors[i % len(pcolors)]),  # Cycle through colors
                hovertemplate='<b>%{x}</b><br>' +
                            f'{transaction_type}: $%{{y:,.0f}}<br>' +
                            '<extra></extra>'
            ))
        
        
        # The slider value (`selected_month`) is a string like "2023‑01"
        max_y = transaction_pivot.loc[selected_month].sum()         # Get the sum of the transactions in the month
        # Add vertical line
        fig_transactions.add_shape(
            type="line",
            x0=selected_month,
            x1=selected_month,
            y0=0,
            y1=max_y,
            line=dict(color="gray", dash="dot")
        )

        # Update layout
        fig_transactions.update_layout(
            title='Monthly Transaction Volume by Transaction Type',
            xaxis_title='Month',
            yaxis_title='Total monthly transaction ($)',
            hovermode='x unified',
            plot_bgcolor='rgba(255, 255, 255, 0)',
            paper_bgcolor='rgba(255, 255, 255, 0)',
        )

        # Add interactivity
        fig_transactions.update_layout(
            title={
                'font': {'size': 24}  # Adjust size here
            },
            clickmode='event+select',
            hoverlabel=dict(bgcolor='white', font_size=14),
            legend_title="Transaction type"
        )

        fig_transactions.update_xaxes(
            tickmode='array',                     # "array" → one tick per entry
            # tickvals=transaction_pivot.index,    # where the ticks go
            # ticktext=transaction_pivot.index,    # what label to show (keeps “2023‑01” etc.)
            tickangle=45,                         # rotate 45° counter‑clockwise
            type='category'                       # treat the axis as categorical (no auto‑spacing)
        )

        # Display chart
        st.plotly_chart(fig_transactions, width='stretch')

    with col2c:
        # Filter the dataframe to the chosen month - Calculations
        filtered = transactions[transactions["month"] == selected_month]

        # Plot the histogram
        fig = px.histogram(
            filtered,
            x="amount",                     # X‑axis: transaction amount (will be binned)
            y="amount",                     # Y‑axis: we’ll sum the amount per bin
            color="type",                   # colour by transaction type (Withdrawal, Transfer, …)
            histfunc="sum",                 # sum the amounts in each bin
            # nbins=20,                     # adjust the number of bins as you like
            title=f"Total Monthly Transaction Distribution: {selected_month_name}",
            color_discrete_sequence=pcolors,  # Default colors
            category_orders={
                "type": ["Deposit", "Payment", "Transfer", "Withdrawal"]
            }
        )

        # Cap the x_axis
        fig.update_traces(
            xbins=dict( 
                start=0,
                end=100000000,
                size=10000000
            )
        )

        # Other updates to the layout
        fig.update_layout(
            yaxis_title="All Customers Transaction Sum ($)",
            xaxis_title="Per Customer Monthly Transaction",
            bargap=0.1,
            legend_title="Transaction type",
            legend_traceorder="reversed", #This matches the stacked line graph chart
            title={
                'font': {'size': 24}  # Adjust size here
            },
            yaxis=dict(range=[0, 600_000_000_000], rangemode="tozero") # Keep Y axis the same through the months
        )

        st.plotly_chart(fig, width='stretch')
#-----------------------------------------------------------------------------------------------------#

## Begin Churn Visualisations
# Add a header for transaction history section
st.header("Churn Drivers")

# Add columns for 2 graphs one categorical comparisons and the other for numerical
col1d, col2d = st.columns(2)

with col1d:
    if selected_category == selected_category_secondary:
        st.error("Please select different categorical variables for the X and Y axes on the left sidebar.")
    else:
        # Pivot the data for the heatmap - Calculations need to be below since streamlit varibles not declared earlier
        pivot_df = customers.pivot_table(
            values='churn_probability',
            index=selected_category,
            columns=selected_category_secondary,
            # aggfunc='mean' if aggregation_method == 'Mean' else 'median'
            aggfunc=lambda x: x.mean().round(3) if aggregation_method == 'Mean' else x.median().round(3) # For 2 dp aggregations
        )

            # Create the heatmap using Plotly Express
        fig = px.imshow(
            pivot_df,
            title=f"Churn Probability Heatmap: {selected_category} vs {selected_category_secondary} ",
            labels=dict(x=selected_category_secondary, y=selected_category, color="Churn Probability"),
            x=pivot_df.columns,
            y=pivot_df.index,
            color_continuous_scale='Sunsetdark',  # Blue-Red color scale
            text_auto=True  # Display values on the heatmap
        )

        # Display the heatmap in Streamlit
        st.plotly_chart(fig, use_container_width=True)
with col2d:
# Create the violin plot
    fig_violin = px.violin(
        customers,
        x=selected_numerical_column,
        y='churn_probability',
        title=f'Churn Probability Distribution by {selected_numerical_column}',
        labels={'churn_probability': 'Churn Probability', selected_numerical_column: selected_numerical_column},
        box=True,  # Add a box plot inside the violin plot for better visualization
        points='outliers',  # Show outliers as individual points
        # color=selected_numerical_column,  # Color by the numerical column for clarity
        template='plotly_white'  # Use a clean white background
    )

    st.plotly_chart(fig_violin, use_container_width=True)

#---------------------------------------------------------------------------------------------------------#



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
# # st.plotly_chart(fig, width='stretch')

        # /* 2. Style the static selectbox field when closed */
        # section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div {{
        #     background-color: {colors["soft_white"]} !important;
        # }}
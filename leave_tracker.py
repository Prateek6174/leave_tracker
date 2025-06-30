import streamlit as st
import pandas as pd
import calendar
from datetime import datetime
import os
from io import BytesIO
import sys
import matplotlib.pyplot as plt

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

@st.cache_data
def load_data(file):
    try:
        if hasattr(file, "read"):
            file_bytes = BytesIO(file.read())
        else:
            file_bytes = file

        df = pd.read_excel(file_bytes, engine="openpyxl")
        df = df.iloc[:, 3:]
        df.columns = ['Email', 'Name', 'Leave Date', 'Leave Type', 'Duration']
        df['Leave Date'] = pd.to_datetime(df['Leave Date'])
        df['Duration'] = df['Duration'].map({1: 'Full Day', 0.5: 'Half Day'})
        df['Details'] = df.apply(
            lambda row: {
                "name": row['Name'],
                "type": row['Leave Type'],
                "duration": row['Duration']
            }, axis=1
        )
        return df

    except Exception as e:
        st.error(f"⚠️ Error while loading file: {e}")
        return pd.DataFrame()

def display_calendar(df, year, month, filter_name):

    # Precompute calendar data
    _, num_days = calendar.monthrange(year, month)
    days = [datetime(year, month, day) for day in range(1, num_days + 1)]
    
    # Create leave dictionary
    leave_dict = df.groupby('Leave Date')['Details'].apply(list).to_dict()
    
    weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    # Weekday headers
    week_row = st.columns(7)
    for i, day in enumerate(weekdays):
        week_row[i].markdown(f"<div style='text-align: center; font-weight: bold; font-size: 11px; color: #34495e;'>{day}</div>", unsafe_allow_html=True)

    # Calendar grid
    day_idx = 0
    row = st.columns(7)
    first_weekday = days[0].weekday()
    
    # Fill empty days at start of month
    # Fill empty days at start of month
    for i in range(first_weekday):
        empty_html = """
            <div style='height: 60px; visibility: hidden;'></div>
        """
        row[i].markdown(empty_html, unsafe_allow_html=True)
        day_idx += 1


    # Render each day
    for day in days:
        if day_idx % 7 == 0:
            row = st.columns(7)

        leaves_today = leave_dict.get(day, [])
        leave_applied = False
        hover_details = ""

        # Apply name filter
        if filter_name != "All":
            leaves_today = [leave for leave in leaves_today if leave['name'] == filter_name]
            
        if leaves_today:
            leave_applied = True
            for leave in leaves_today:
                hover_details += f"<div style='margin-bottom: 5px;'><strong style='color: #1f4e79;'>{leave['name']}</strong><br><span style='font-size: 9px;'>{leave['type']} ({leave['duration']})</span></div>"

        is_today = (day.date() == datetime.today().date())
        today_style = "border: 2px solid #e67e22;" if is_today else ""

        weekday = day.weekday()
        # Position tooltips away from sidebar for left columns
        if weekday in [0, 1, 2]:  # Mon, Tue, Wed
            tooltip_position = "left: 5px; right: auto;"
        elif weekday in [3, 4]:    # Thu, Fri
            tooltip_position = "left: 50%; transform: translateX(-50%);"
        else:                      # Sat, Sun
            tooltip_position = "right: 5px; left: auto;"

        if leave_applied:
            cell_html = f"""
                <div class='day-box leave-day hover-trigger' style="{today_style}">
                    <div style="font-weight: bold;">{day.day}</div>
                    <div class='hover-box' style="{tooltip_position}">{hover_details}</div>
                </div>
            """
        else:
            cell_html = f"""
                <div class='day-box' style="{today_style}">
                    {day.day}
                </div>
            """

        row[weekday].markdown(cell_html, unsafe_allow_html=True)
        day_idx += 1

def calculate_employee_stats(df, employee_name, year):
    # Filter data for the selected employee and year
    emp_df = df[(df['Name'] == employee_name) & (df['Leave Date'].dt.year == year)].copy()
    
    # Calculate basic stats
    stats = {}
    stats['total_leaves'] = len(emp_df)
    stats['full_days'] = emp_df[emp_df['Duration'] == 'Full Day'].shape[0]
    stats['half_days'] = emp_df[emp_df['Duration'] == 'Half Day'].shape[0]
    
    # Calculate leave type distribution
    stats['leave_types'] = emp_df['Leave Type'].value_counts().to_dict()
    
    # Calculate monthly distribution
    monthly_counts = emp_df['Leave Date'].dt.month.value_counts().reindex(range(1, 13), fill_value=0)
    monthly_counts.index = monthly_counts.index.map(lambda x: calendar.month_abbr[x])
    stats['monthly_distribution'] = monthly_counts
    
    # Calculate most common leave type
    if stats['leave_types']:
        stats['most_common_type'] = max(stats['leave_types'], key=stats['leave_types'].get)
    else:
        stats['most_common_type'] = "No leaves"
    
    return stats

def display_stats_panel(stats, employee_name, year):
    with st.expander(f"📊 Leave Statistics for {employee_name}", expanded=True):
        # Create summary cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Leaves", stats['total_leaves'])
        
        with col2:
            st.metric("Full Days", stats['full_days'])
        
        with col3:
            st.metric("Half Days", stats['half_days'])
        
        # Create two columns for charts
        chart_col1, chart_col2 = st.columns([1, 1])
        
        with chart_col1:
            if stats['monthly_distribution'].sum() > 0:
                st.subheader("Monthly Distribution")
                fig, ax = plt.subplots(figsize=(8, 4))
                stats['monthly_distribution'].plot(kind='bar', color='#4b86b4', ax=ax)
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.info("No leave data for this year")
        
        with chart_col2:
            if stats['leave_types']:
                st.subheader("Leave Type Distribution")
                fig, ax = plt.subplots(figsize=(8, 4))
                pd.Series(stats['leave_types']).plot(
                    kind='pie', 
                    autopct='%1.1f%%', 
                    colors=['#3498db', '#2ecc71', '#e74c3c', '#f39c12'],
                    ax=ax
                )
                ax.set_ylabel('')
                st.pyplot(fig)
            else:
                st.info("No leave type data available")
        
        # Display most common leave type
        st.markdown(f"**Most Common Leave Type:** `{stats['most_common_type']}`")
        
        # Show raw data
        with st.expander("View Leave Details"):
            st.dataframe(df[df['Name'] == employee_name][['Leave Date', 'Leave Type', 'Duration']]
                         .sort_values('Leave Date', ascending=False)
                         .reset_index(drop=True))

# ---------- Streamlit Layout ----------
st.set_page_config(
    page_title="YED Leave Tracker",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with guaranteed tooltip visibility
st.markdown("""
    <style>
    :root {
        --primary: #1f4e79;
        --primary-light: #4b86b4;
        --secondary: #3498db;
        --accent: #e67e22;
        --background: #f8f9fa;
        --text: #2c3e50;
        --text-light: #7f8c8d;
        --border: #dfe6e9;
    }
    
    html, body, .main, .block-container {
        margin: 0;
        padding: 0;
        height: 100vh;
        overflow: hidden !important;
        background-color: var(--background);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    body::-webkit-scrollbar {
        display: none;
    }
    header, footer, .stDeployButton {
        display: none !important;
    }
    
    /* Calendar styling */
    .day-box {
        border: 2px solid #34495e;  /* darker grey */
        border-radius: 6px;
        padding: 3px;
        height: 60px;
        font-size: 11px;
        background-color: transparent !important;
        color: var(--text);
        position: relative;
        transition: all 0.3s ease;
        z-index: 100;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }

    .day-box:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        z-index: 1000;
    }

    .leave-day {
        background: linear-gradient(135deg, var(--primary), var(--primary-light)) !important;
        color: white !important;
        font-weight: bold;
    }

    /* GUARANTEED VISIBLE TOOLTIPS */
    .hover-box {
        display: none;
        position: absolute;
        top: calc(100% + 5px);
        z-index: 9999;
        background: white;
        border: 1px solid var(--border);
        padding: 12px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        font-size: 11px;
        width: 180px;
        color: var(--text);
        max-height: 300px;
        overflow-y: auto;
    }

    .hover-trigger:hover .hover-box {
        display: block;
        animation: fadeIn 0.3s ease;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    /* Month buttons styling */
    .stButton>button {
        width: 100%;
        padding: 4px 3px;
        font-size: 10px;
        transition: all 0.3s;
        margin: 0px 0;
        border-radius: 6px;
        min-height: 26px;
        background-color: white;
        border: 1px solid var(--border);
        color: var(--text);
        font-weight: 500;
    }
    
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        background-color: #f8f9fa;
    }
    
    /* Primary button (selected month) */
    .stButton>button[kind="primary"] {
        background: linear-gradient(135deg, var(--primary), var(--primary-light));
        color: white;
        border: none;
        font-weight: 600;
    }
    
    /* Status message styling */
    .status-msg {
        font-size: 11px;
        color: var(--text-light);
        text-align: center;
        padding: 6px;
        margin-top: 6px;
        border-radius: 6px;
        background-color: white;
        border: 1px solid var(--border);
    }
    
    /* Current month indicator */
    .current-month-indicator {
        font-size: 12px;
        color: var(--accent);
        text-align: center;
        margin-top: -6px;
        margin-bottom: 2px;
        font-weight: bold;
    }
    
    /* Header styling */
    .app-title {
    text-align: center;
    font-size: 20px;
    font-weight: 600;
    color: #2c3e50; /* Dark Slate Gray */
    letter-spacing: 0.5px;
    margin-top: 0px;
    margin-bottom: 5px;
    
     }

    
    /* Footer styling */
    .app-footer {
        text-align: center; 
        font-size: 10px; 
        color: var(--text-light); 
        margin-top: 10px;
        padding: 8px;
        background-color: white;
        border-radius: 6px;
        border: 1px solid var(--border);
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background-color: white;
        border-right: 1px solid var(--border);
        z-index: 100;
    }
    
    /* Section headers */
    .section-header {
        color: var(--primary);
        font-weight: 600;
        border-bottom: 2px solid var(--primary-light);
        padding-bottom: 5px;
        margin-bottom: 15px;
    }
    
    /* Export button styling */
    .export-btn {
        background: linear-gradient(135deg, var(--primary), var(--primary-light)) !important;
        color: white !important;
        border: none !important;
    }
    
    /* Refresh button styling */
    .refresh-btn {
        background: linear-gradient(135deg, #27ae60, #2ecc71) !important;
        color: white !important;
        border: none !important;
    }
    
    /* Compact spacing */
    .compact-spacing {
        margin-top: -8px;
        margin-bottom: -8px;
    }
    
    /* Ensure calendar cells have proper stacking context */
    .stColumn > div {
        position: relative;
        overflow: visible !important;
    }
            
       /* Calendar section background */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) > div {
        background-color: #f0f8ff !important;
        padding: 10px;
        border-radius: 10px;
        margin-right: 10px;
    }
    
    /* Month selector section background */
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) > div {
        background-color: #f8f8f8 !important;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
     /* Fix ghost white box issue on Tuesday column */
    .stColumn {
    background-color: transparent !important;
    }

/* Ensure hidden day boxes are truly invisible and don't show borders */
    .day-box[style*="visibility: hidden"] {
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin: 0 !important;
    height: 60px;
    }

/* Fix internal padding/margin issues in Tuesday's column */
    .stColumn:nth-child(2) > div {
    margin: 0 !important;
    padding: 0 !important;
    }
            
    .day-box[style*="visibility: hidden"] {
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin: 0 !important;
    height: 60px;
    }

/* Fix internal padding/margin issues in Tuesday's column */
    .stColumn:nth-child(2) > div {
    margin: 0 !important;
    padding: 0 !important;
    }
            
    .stButton button {
    margin-top: 0 !important;
    margin-bottom: 0 !important;
    padding-top: 4px !important;
    padding-bottom: 4px !important;
    }
            
    /* Add this to your existing CSS */
    .stButton > button {
    margin: 1px 0 !important;
    padding: 2px 0 !important;
    min-height: 24px !important;
    }

    .current-month-indicator {
    margin-top: -5px !important;
    margin-bottom: 5px !important;
    }
            
    
    .app-title {
    margin: 0 auto;  /* Center with auto margins */
    padding: 0;
    width: 100%;
    text-align: center; /* Ensure text is centered */
    }

/* Remove top space from calendar container */
   div[data-testid="stHorizontalBlock"] > div:nth-child(1) > div {
    margin-top: 0 !important;
   }
            
    </style>
""", unsafe_allow_html=True)

# Header with integrated month selector title
# Aligned header: main title and month section header

# ---------- Load Excel ----------
@st.cache_resource
def load_excel_data():
    file_path = os.path.join(os.path.dirname(__file__), "Leave Tracker (YED).xlsx")
    if os.path.exists(file_path):
        return load_data(file_path)
    else:
        st.error("Leave Tracker Excel file not found.")
        st.stop()
        return pd.DataFrame()

# Load data with spinner
with st.spinner("🔄 Loading leave data..."):
    df = load_excel_data()

# Initialize session state
if 'selected_month' not in st.session_state:
    st.session_state.selected_month = datetime.now().month
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now().strftime("%H:%M:%S")

# ---------- Sidebar Filters ----------
with st.sidebar:
    st.markdown("<div class='section-header'>🔍 Filter Calendar</div>", unsafe_allow_html=True)
    year = st.selectbox("Year", list(range(2024, 2027)), index=1)
    all_names = ["All"] + sorted(df["Name"].unique())
    filter_name = st.selectbox("Employee", all_names)
    
    # Display data freshness
    st.markdown(f"<div class='status-msg'>Data loaded: {st.session_state.last_update}</div>", unsafe_allow_html=True)
    
    # Export button
    if st.button("📥 Export to Excel", use_container_width=True, key="export_btn"):
        with BytesIO() as buffer:
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            st.download_button(
                label="💾 Download Export",
                data=buffer.getvalue(),
                file_name="leave_export.xlsx",
                mime="application/vnd.ms-excel",
                use_container_width=True,
                key="download_btn"
            )

# ====== MODIFIED COLUMN SECTION ======
# Create two-column layout with adjusted ratios
left_col, right_col = st.columns([0.75, 0.25])

# Left column: Calendar display with centered title
with left_col:
    # Add centered title for calendar section
    st.markdown(
        """
        <div style="display: flex; justify-content: center; margin-bottom: 10px;">
            <h2 class='app-title'>YED Leave Tracker</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    display_calendar(df, year, st.session_state.selected_month, filter_name)

# Right column: Month selector with vertical alignment fix
with right_col:
    # Add spacer to match the title height in left column
    st.markdown('<div style="height: 36px;"></div>', unsafe_allow_html=True)
    
    # Month selector title with adjusted margins
    st.markdown(
        "<div style='text-align: center; font-weight: 600; "
        "color: #1f4e79; margin-bottom: 20px;'>Select Month</div>",
        unsafe_allow_html=True
    )
    
    # Month buttons with improved styling
    months = list(calendar.month_abbr)[1:]
    for i, month_name in enumerate(months):
        month_num = i + 1
        is_current = (month_num == datetime.now().month and year == datetime.now().year)
        is_selected = (month_num == st.session_state.selected_month)
        
        # Create button
        btn = st.button(
            month_name,
            key=f"month_{month_num}",
            use_container_width=True,
            type="primary" if is_selected else "secondary"
        )
        
        if btn:
            st.session_state.selected_month = month_num
            st.rerun()

if filter_name != "All":
    stats = calculate_employee_stats(df, filter_name, year)
    display_stats_panel(stats, filter_name, year)

# Footer with status information
st.markdown(f"""
    <div class="app-footer">
        Showing: <strong>{filter_name}</strong> | Last refresh: {st.session_state.last_update}
    </div>
""", unsafe_allow_html=True)
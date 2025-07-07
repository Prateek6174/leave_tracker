import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import calendar
import numpy as np

# Configure page
st.set_page_config(
    page_title="YED Leave Tracker",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'leave_data' not in st.session_state:
    st.session_state.leave_data = pd.DataFrame(columns=[
        'Employee Name', 'Leave Type', 'Start Date', 'End Date', 'Days'
    ])

if 'page' not in st.session_state:
    st.session_state.page = 'home'

if 'selected_employee' not in st.session_state:
    st.session_state.selected_employee = None

# Sample data for demonstration
def load_sample_data():
    sample_data = [
        ['Prateek Pandey', 'Earned Leave', '2025-07-01', '2025-07-01', 1,],
        ['Nitant Kothari', 'Sick Leave', '2025-07-05', '2025-07-05', 1,],
        ['Shailya Patel', 'Personal Leave', '2025-06-10', '2025-06-10', 1,],
        ['Sanchit Garg', 'Sick Leave', '2025-05-15', '2025-05-15', 1, ],
        ['Mahek Mehta', 'Sick Leave', '2025-05-24', '2025-05-24', 1,],
        ['Ashok Kumar Mani', 'Casual Leave', '2025-04-24', '2025-04-24', 1,],
        ['Abhishek Singh', 'Personal Leave', '2025-04-09', '2025-04-09', 1, ],
        ['Sri Ruthvik', 'Sick Leave', '2025-02-02', '2025-02-02', 1, ],
        ['Nitant Kothari', 'Sick Leave', '2025-02-15', '2025-02-15', 1,],
        ['Sanchit Garg', 'Personal Leave', '2025-03-21', '2025-03-21', 1,],
        ['Shailya Patel', 'Earned Leave', '2025-04-05', '2025-04-05', 1,],
    ]
    
    df = pd.DataFrame(sample_data, columns=[
        'Employee Name', 'Leave Type', 'Start Date', 'End Date', 'Days',
    ])
    df['Start Date'] = pd.to_datetime(df['Start Date'])
    df['End Date'] = pd.to_datetime(df['End Date'])
    return df

# Load sample data if empty
if st.session_state.leave_data.empty:
    st.session_state.leave_data = load_sample_data()

# Navigation functions
def go_to_page(page_name):
    st.session_state.page = page_name
    st.rerun()

def go_to_employee_detail(employee_name):
    st.session_state.selected_employee = employee_name
    st.session_state.page = 'employee_detail'
    st.rerun()

# Helper functions
def get_leave_dates(start_date, end_date):
    """Generate all dates between start and end date"""
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(days=1)
    return dates

def get_leave_color(leave_type):
    """Return color based on leave type"""
    colors = {
        'Earned Leave': '#FF6B6B',
        'Sick Leave': '#4ECDC4',
        'Personal Leave': '#45B7D1',
        'Emergency Leave': '#96CEB4',
        'Joining Transfer Leave': '#FFEAA7',
            }
    return colors.get(leave_type, '#95A5A6')

# Main application
def main():
    # Enhanced Custom CSS
    st.markdown("""
    <style>
    /* Main styling */
    .main-header {
        text-align: center;
        padding: 3rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        margin-bottom: 3rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    .main-header h1 {
        font-size: 3rem;
        margin-bottom: 0.5rem;
        font-weight: 700;
    }
    
    .main-header p {
        font-size: 1.3rem;
        opacity: 0.9;
    }
    
    /* Button styling */
    .option-card {
        background: white;
        padding: 3rem 2rem;
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        text-align: center;
        transition: all 0.3s ease;
        border: 2px solid transparent;
        height: 250px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        cursor: pointer;
    }
    
    .option-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
        border-color: #667eea;
    }
    
    .option-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }
    
    .option-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 0.5rem;
    }
    
    .option-desc {
        color: #666;
        font-size: 1rem;
    }
    
    /* Calendar styling */
    .calendar-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        margin: 2rem 0;
    }
    
    .calendar-header {
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        font-size: 1.5rem;
        font-weight: 600;
    }
    
    .calendar-day-header {
        background: #f8f9fa;
        padding: 1rem;
        text-align: center;
        font-weight: 600;
        color: #333;
        border-radius: 8px;
        margin-bottom: 0.5rem;
    }
    
    .calendar-day {
        background: white;
        padding: 1rem;
        margin: 0.2rem;
        border-radius: 8px;
        text-align: center;
        border: 1px solid #e9ecef;
        font-weight: 500;
        transition: all 0.3s ease;
        min-height: 60px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .calendar-day:hover {
        background: #f8f9fa;
        border-color: #667eea;
    }
    
    .calendar-day-today {
        border: 3px solid #ffd700 !important;
        background: #fffacd;
        font-weight: 700;
    }
    
    .calendar-day-leave {
        color: white;
        font-weight: 600;
        border: none;
        position: relative;
        cursor: pointer;
    }
    
    .calendar-day-leave:hover {
        opacity: 0.9;
        transform: scale(1.05);
    }
    
    .calendar-day-leave.calendar-day-today {
        border: 3px solid #ffd700 !important;
        box-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
    }
    
    /* Form styling */
    .form-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        margin: 2rem 0;
    }
    
    /* Legend styling */
    .legend-container {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 3px 15px rgba(0,0,0,0.1);
        margin-top: 2rem;
    }
    
    .legend-item {
        display: flex;
        align-items: center;
        margin: 0.5rem 0;
        padding: 0.5rem;
        border-radius: 5px;
        transition: background 0.3s ease;
    }
    
    .legend-item:hover {
        background: #f8f9fa;
    }
    
    .legend-color {
        width: 20px;
        height: 20px;
        border-radius: 4px;
        margin-right: 15px;
        border: 2px solid white;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    
    /* Filter styling */
    .filter-container {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 3px 15px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    
    /* Employee stats container */
    .employee-stats {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        margin: 2rem 0;
    }
    
    /* Navigation buttons */
    .nav-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 25px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .nav-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    /* Hide streamlit elements */
    .stDeployButton {display:none;}
    footer {visibility: hidden;}
    .stApp > header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

    if st.session_state.page == 'home':
        show_home_page()
    elif st.session_state.page == 'apply_leave':
        show_apply_leave_page()
    elif st.session_state.page == 'view_tracker':
        show_view_tracker_page()
    elif st.session_state.page == 'employee_detail':
        show_employee_detail_page()

def show_home_page():
    # Enhanced Header
    st.markdown("""
    <div class="main-header">
        <h1>🏢 YED Leave Tracker</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Main options side by side
    st.markdown("### Choose an Option")
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("""
        <div class="option-card">
            <div class="option-icon">📝</div>
            <div class="option-title">Apply for a Leave</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Apply for Leave", key="apply_btn", type="primary", use_container_width=True):
            go_to_page('apply_leave')
    
    with col2:
        st.markdown("""
        <div class="option-card">
            <div class="option-icon">📊</div>
            <div class="option-title">View Leave Tracker</div>
            
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("View Leave Tracker", key="view_btn", type="primary", use_container_width=True):
            go_to_page('view_tracker')

def show_apply_leave_page():
    st.markdown("# 📝 Apply for Leave")
    
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    
    with st.form("leave_application"):
        st.markdown("### Leave Application Form")
        
        col1, col2 = st.columns(2)
        
        with col1:
            employee_name = st.text_input("Employee Name*", placeholder="Enter your full name")
            leave_type = st.selectbox("Leave Type*", [
                "Earned Leave", "Sick Leave", "Personal Leave", 
                "Emergency Leave", "Joining Transfer Leave"
            ])
        
        with col2:
            start_date = st.date_input("Start Date*", value=date.today())
            end_date = st.date_input("End Date*", value=date.today())
        
        reason = st.text_area("Reason for Leave", placeholder="Please provide a brief reason for your leave request...")
        
        st.markdown("---")
        submitted = st.form_submit_button("Submit Leave Application", type="primary")
        
        if submitted:
            if employee_name and start_date and end_date:
                if start_date <= end_date:
                    days = (end_date - start_date).days + 1
                    
                    new_leave = pd.DataFrame({
                        'Employee Name': [employee_name],
                        'Leave Type': [leave_type],
                        'Start Date': [pd.to_datetime(start_date)],
                        'End Date': [pd.to_datetime(end_date)],
                        'Days': [days],
                    
                    })
                    
                    st.session_state.leave_data = pd.concat([st.session_state.leave_data, new_leave], ignore_index=True)
                    st.success(f"✅ Leave application submitted successfully! Application ID: LA{len(st.session_state.leave_data):04d}")
                else:
                    st.error("❌ End date must be after or equal to start date!")
            else:
                st.error("❌ Please fill in all required fields!")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Navigation
    st.markdown("---")
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🏠 Back to Home", type="secondary"):
            go_to_page('home')

def show_view_tracker_page():
    st.markdown("# 📊 Leave Tracker Dashboard")
    
    # Enhanced filters
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    st.markdown("### 🔍 Filters")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_month = st.selectbox("📅 Select Month", range(1, 13), 
                                    index=datetime.now().month - 1,
                                    format_func=lambda x: calendar.month_name[x])
    with col2:
        current_year = datetime.now().year
        year_options = list(range(2023, 2026))
        default_year_index = year_options.index(current_year) if current_year in year_options else 1
        selected_year = st.selectbox("📅 Select Year", year_options, 
                                   index=default_year_index)
    
    with col3:
        employees = ['All Employees'] + sorted(st.session_state.leave_data['Employee Name'].unique().tolist())
        selected_employee = st.selectbox("👤 Select Employee", employees)
        
        if selected_employee != 'All Employees':
            go_to_employee_detail(selected_employee)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Show calendar
    show_calendar_view(selected_month, selected_year)

def show_calendar_view(selected_month, selected_year):
    # Create calendar
    cal = calendar.monthcalendar(selected_year, selected_month)
    
    # Get leaves for the selected month
    month_start = datetime(selected_year, selected_month, 1)
    if selected_month == 12:
        month_end = datetime(selected_year + 1, 1, 1) - timedelta(days=1)
    else:
        month_end = datetime(selected_year, selected_month + 1, 1) - timedelta(days=1)
    
    month_leaves = st.session_state.leave_data[
        (st.session_state.leave_data['Start Date'] <= month_end) & 
        (st.session_state.leave_data['End Date'] >= month_start)
    ]
    
    # Create leave date mapping
    leave_dates = {}
    for _, leave in month_leaves.iterrows():
        dates = get_leave_dates(max(leave['Start Date'], month_start), 
                               min(leave['End Date'], month_end))
        for date_obj in dates:
            if date_obj.day not in leave_dates:
                leave_dates[date_obj.day] = []
            leave_dates[date_obj.day].append({
                'employee': leave['Employee Name'],
                'type': leave['Leave Type'],
                'color': get_leave_color(leave['Leave Type'])
            })
    
    # Display calendar
    st.markdown('<div class="calendar-container">', unsafe_allow_html=True)
    
    st.markdown(f'<div class="calendar-header">{calendar.month_name[selected_month]} {selected_year}</div>', 
                unsafe_allow_html=True)
    
    # Calendar header
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    cols = st.columns(7)
    for i, day in enumerate(days):
        cols[i].markdown(f'<div class="calendar-day-header">{day}</div>', unsafe_allow_html=True)
    
    # Calendar body
    today = datetime.now()
    
    for week in cal:
        cols = st.columns(7)
        for i, day in enumerate(week):
            if day == 0:
                cols[i].markdown('<div class="calendar-day"></div>', unsafe_allow_html=True)
            else:
                # Check if this is today
                is_today = (day == today.day and 
                           selected_month == today.month and 
                           selected_year == today.year)
                
                if day in leave_dates:
                    # Day with leaves
                    leave_info = leave_dates[day]
                    color = leave_info[0]['color']
                    tooltip_text = f"📅 {day} {calendar.month_name[selected_month]}"
                    
                    # Create hover content
                    hover_content = ""
                    for leave in leave_info:
                        hover_content += f"• {leave['employee']} - {leave['type']}\\n"
                    
                    today_class = " calendar-day-today" if is_today else ""
                    
                    cols[i].markdown(f"""
                    <div class="calendar-day calendar-day-leave{today_class}" 
                         style="background-color: {color};" 
                         title="{tooltip_text}&#10;{hover_content}">
                        <strong>{day}</strong>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Regular day
                    today_class = " calendar-day-today" if is_today else ""
                    cols[i].markdown(f'<div class="calendar-day{today_class}">{day}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Enhanced Legend
    st.markdown('<div class="legend-container">', unsafe_allow_html=True)
    st.markdown("### 🎨 Leave Types Legend")
    
    leave_types = st.session_state.leave_data['Leave Type'].unique()
    
    # Calculate columns needed
    num_cols = min(len(leave_types), 3)
    if num_cols > 0:
        legend_cols = st.columns(num_cols)
        
        for i, leave_type in enumerate(leave_types):
            col_index = i % num_cols
            color = get_leave_color(leave_type)
            
            legend_cols[col_index].markdown(f"""
            <div class="legend-item">
                <div class="legend-color" style="background-color: {color};"></div>
                <span style="font-weight: 500;">{leave_type}</span>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_employee_detail_page():
    if st.session_state.selected_employee is None:
        st.error("No employee selected!")
        return
    
    employee = st.session_state.selected_employee
    st.markdown(f"# 👤 {employee} - Leave Statistics")
    
    # Filter data for selected employee
    employee_data = st.session_state.leave_data[
        st.session_state.leave_data['Employee Name'] == employee
    ]
    
    if employee_data.empty:
        st.warning(f"No leave records found for {employee}")
        if st.button("⬅️ Back to Tracker"):
            go_to_page('view_tracker')
        return
    
    # Employee statistics in a professional container
    st.markdown('<div class="employee-stats">', unsafe_allow_html=True)
    
    # Key metrics
    st.markdown("### 📊 Leave Summary")
    col1, col2 = st.columns(2)
    
    with col1:
        total_leaves = employee_data['Days'].sum()
        st.metric("Total Leave Days", total_leaves, delta=None)
    
    with col2:
        unique_leave_types = employee_data['Leave Type'].nunique()
        st.metric("Types of Leaves Used", unique_leave_types)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive Charts
    st.markdown("### 📈 Interactive Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Monthly leaves bar chart
        st.markdown("#### Monthly Leave Days")
        if len(employee_data) > 0:
            # Create monthly data
            employee_data_copy = employee_data.copy()
            employee_data_copy['Month'] = employee_data_copy['Start Date'].dt.to_period('M')
            monthly_leaves = employee_data_copy.groupby('Month')['Days'].sum().reset_index()
            monthly_leaves['Month'] = monthly_leaves['Month'].astype(str)
            
            if len(monthly_leaves) > 0:
                fig_bar = px.bar(
                    monthly_leaves, 
                    x='Month', 
                    y='Days',
                    title=f"Monthly Leave Pattern for {employee}",
                    color='Days',
                    color_continuous_scale='viridis'
                )
                fig_bar.update_layout(
                    showlegend=False,
                    height=400,
                    title_x=0.5,
                    xaxis_title="Month",
                    yaxis_title="Leave Days"
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("No monthly data available")
    
    with col2:
        # Leave types pie chart
        st.markdown("#### Leave Types Distribution")
        leave_types = employee_data['Leave Type'].value_counts()
        
        if len(leave_types) > 0:
            fig_pie = px.pie(
                values=leave_types.values, 
                names=leave_types.index,
                title=f"Leave Types for {employee}",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_pie.update_layout(
                height=400,
                title_x=0.5,
                showlegend=True
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No leave type data available")
    
    # Leave History Table
    st.markdown("### 📋 Leave History")
    
    # Format the data for better display
    display_data = employee_data.copy()
    display_data['Start Date'] = display_data['Start Date'].dt.strftime('%Y-%m-%d')
    display_data['End Date'] = display_data['End Date'].dt.strftime('%Y-%m-%d')
    display_data = display_data.sort_values('Start Date', ascending=False)
    
    st.dataframe(
        display_data[['Leave Type', 'Start Date', 'End Date', 'Days']], 
        use_container_width=True,
        hide_index=True
    )
    
    # Navigation
    st.markdown("---")
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("⬅️ Back to Tracker", type="secondary"):
            st.session_state.selected_employee = None
            go_to_page('view_tracker')

# Simplified Sidebar
with st.sidebar:
    st.markdown("### 🧭 Navigation")
    
    if st.button("🏠 Home", type="secondary"):
        go_to_page('home')
    
    if st.button("📝 Apply Leave", type="secondary"):
        go_to_page('apply_leave')
    
    if st.button("📊 View Tracker", type="secondary"):
        go_to_page('view_tracker')

# Run the main function
if __name__ == "__main__":
    main()
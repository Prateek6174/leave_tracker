# leave_dashboard.py

import streamlit as st
import pandas as pd
import calendar
from datetime import datetime
import os
import socket

# ---------- STEP 1: Load and Clean Data ----------
@st.cache_data
def load_data(file):
    df = pd.read_excel(file)
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

# ---------- STEP 2: Calendar Display with Hover Popup ----------
def display_calendar(df, year, month, filter_name):
    st.markdown(f"<h2 style='text-align: center; font-size: 28px;'>\
                 {calendar.month_name[month]} {year}</h2>", unsafe_allow_html=True)

    days = [datetime(year, month, day) for day in range(1, calendar.monthrange(year, month)[1] + 1)]
    leave_dict = df.groupby('Leave Date')['Details'].apply(list).to_dict()

    weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    st.markdown("""
        <style>
            body {
                background-color: #f2f6fa;
            }
            .day-box {
                border: 1px solid #ccc;
                border-radius: 10px;
                padding: 20px;
                height: 180px;
                box-shadow: 2px 2px 8px #ddd;
                font-size: 18px;
                position: relative;
                background-color: #eaf0f6;
                overflow: visible;
            }
            .hover-box {
                display: none;
                position: absolute;
                top: 50px;
                left: 10px;
                z-index: 1000;
                background: #fff;
                border: 1px solid #ccc;
                padding: 10px;
                border-radius: 8px;
                box-shadow: 0px 0px 10px rgba(0,0,0,0.2);
                font-size: 14px;
                width: 250px;
            }
            .dot {
                height: 12px;
                width: 12px;
                background-color: #ff4b4b;
                border-radius: 50%;
                display: inline-block;
                margin-top: 10px;
            }
            .hover-trigger:hover .hover-box {
                display: block;
            }
        </style>
    """, unsafe_allow_html=True)

    week_row = st.columns(7)
    for i, day in enumerate(weekdays):
        week_row[i].markdown(f"<div style='text-align: center; font-weight: bold; font-size: 20px;'>{day}</div>", unsafe_allow_html=True)

    day_idx = 0
    row = st.columns(7)
    first_weekday = days[0].weekday()
    for i in range(first_weekday):
        row[i].markdown(" ")

    for day in days:
        if day_idx % 7 == 0:
            row = st.columns(7)

        leaves_today = leave_dict.get(day, [])
        dot = ""
        hover_details = ""

        for leave in leaves_today:
            if filter_name != "All" and leave['name'] != filter_name:
                continue

            dot = "<div class='dot'></div>"
            hover_details += f"<div><strong>{leave['name']}</strong><br>{leave['type']} ({leave['duration']})</div><hr>"

        if dot:
            cell_html = f"""
                <div class='day-box hover-trigger'>
                    {day.day}<br>
                    {dot}
                    <div class='hover-box'>{hover_details}</div>
                </div>
            """
        else:
            cell_html = f"""
                <div class='day-box'>
                    {day.day}
                </div>
            """

        row[day.weekday()].markdown(cell_html, unsafe_allow_html=True)
        day_idx += 1

# ---------- STEP 3: Streamlit UI ----------
st.set_page_config(page_title="YED Leave Tracker", layout="wide")
st.title("YED Leave Tracker")


def is_local_environment():
    return socket.gethostname().lower().startswith("desktop") or os.path.exists("Leave Tracker (YED).xlsx")

if is_local_environment():
    file_path = os.path.join(os.getcwd(), "Leave Tracker (YED).xlsx")
    if os.path.exists(file_path):
        df = load_data(file_path)
    else:
        st.error("Excel file not found locally. Please ensure it's in the same folder.")
        st.stop()
else:
    uploaded_file = st.file_uploader("📤 Upload the team leave Excel file", type=["xlsx"], label_visibility="collapsed")
    if uploaded_file:
        df = load_data(uploaded_file)
        st.experimental_rerun()
    else:
        st.info("Please upload the Excel file to begin.")
        st.stop()

# Only show calendar if df is loaded
if 'df' in locals():
    st.sidebar.header("🔍 Filter")
    year = st.sidebar.selectbox("Year", list(range(2024, 2027)), index=1)
    month = st.sidebar.selectbox("Month", list(range(1, 13)), format_func=lambda m: calendar.month_name[m])

    all_names = ["All"] + sorted(df["Name"].unique())
    filter_name = st.sidebar.selectbox("Employee", all_names)

    display_calendar(df, year, month, filter_name)

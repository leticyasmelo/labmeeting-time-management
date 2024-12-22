import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os

# File to save data
data_file = "lab_meeting_data.xlsx"

# Load existing data or create a new file if it doesn't exist
def load_data():
    if os.path.exists(data_file):
        return pd.read_excel(data_file)
    else:
        df = pd.DataFrame(columns=["Name", "Time (min)", "Week"])
        df.to_excel(data_file, index=False)
        return df

# Save data to Excel
def save_data(data):
    data.to_excel(data_file, index=False)

# Clear data for the new week
def reset_data():
    df = load_data()
    current_week = datetime.now().isocalendar().week
    df = df[df["Week"] != current_week]
    save_data(df)

# Get remaining time
def remaining_time(data):
    total_time = data["Time (min)"].sum()
    return max(120 - total_time, 0)

# Generate pie chart
def generate_pie_chart(data):
    if data.empty:
        st.write("No data available to display the chart.")
    else:
        fig, ax = plt.subplots()
        times = data.groupby("Name")["Time (min)"].sum()
        times["Free Time"] = remaining_time(data)
        times.plot.pie(ax=ax, autopct="%1.1f%%", startangle=90)
        ax.set_ylabel("")
        ax.set_title("Time Allocation for Lab Meeting")
        st.pyplot(fig)

# Main application
def main():
    st.title("Lab Meeting Time Planner")

    # Load data
    df = load_data()

    # Show input form
    with st.form("time_input_form"):
        name = st.text_input("Name:")
        time_needed = st.number_input("Time Needed (minutes):", min_value=1, max_value=120)
        submitted = st.form_submit_button("Submit")

        if submitted:
            if remaining_time(df) >= time_needed:
                current_week = datetime.now().isocalendar().week
                new_entry = pd.DataFrame({"Name": [name], "Time (min)": [time_needed], "Week": [current_week]})
                df = pd.concat([df, new_entry], ignore_index=True)
                save_data(df)
                st.success("Time allocated successfully!")
            else:
                st.error("Not enough time remaining for this request.")

    # Add a button to reset a specific entry
    st.header("Manage Entries")
    selected_name = st.selectbox("Select a name to modify or delete:", options=df["Name"].unique())
    modify_time = st.number_input("Modify Time (minutes):", min_value=1, max_value=120, value=1)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Update Entry"):
            current_week = datetime.now().isocalendar().week
            df.loc[(df["Name"] == selected_name) & (df["Week"] == current_week), "Time (min)"] = modify_time
            save_data(df)
            st.success("Entry updated successfully!")

    with col2:
        if st.button("Delete Entry"):
            current_week = datetime.now().isocalendar().week
            df = df[~((df["Name"] == selected_name) & (df["Week"] == current_week))]
            save_data(df)
            st.success("Entry deleted successfully!")

    # Show remaining time
    st.write(f"**Remaining Time:** {remaining_time(df)} minutes")

    # Show pie chart
    st.header("Time Allocation Chart")
    current_week = datetime.now().isocalendar().week
    generate_pie_chart(df[df["Week"] == current_week])

    # Reset data every Thursday
    if datetime.now().weekday() == 3:  # Thursday
        reset_data()

    # Show history
    st.header("History")
    st.dataframe(df)

if __name__ == "__main__":
    main()

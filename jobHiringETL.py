import requests
import pandas as pd
import streamlit as st
from datetime import datetime

# -----------------------------
# STEP 1: EXTRACT
# -----------------------------
def fetch_jobs():
    url = "https://remoteok.io/api"
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        raise Exception(f"Failed to fetch jobs: {res.status_code}")

    data = res.json()[1:]  # Skip the first metadata element
    df = pd.DataFrame(data)

    # Select relevant columns
    df = df[['company', 'position', 'tags', 'location', 'date']]
    return df

# -----------------------------
# STEP 2: TRANSFORM
# -----------------------------
def clean_jobs(df):
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])  # Drop rows with invalid dates
    df['tags'] = df['tags'].apply(lambda x: ', '.join(x) if isinstance(x, list) else '')
    df['year_month'] = df['date'].dt.to_period('M').astype(str)
    return df

# -----------------------------
# STEP 3: LOAD
# -----------------------------
def save_to_csv(df, filename='cleaned_jobs.csv'):
    df.to_csv(filename, index=False)
    print(f"✅ Data saved to {filename}")

# -----------------------------
# STEP 4: OPTIONAL DASHBOARD
# -----------------------------
def show_dashboard():
    df = pd.read_csv("cleaned_jobs.csv")
    
    st.title("📊 Hiring Trends Dashboard")
    st.markdown("Analyzing remote job trends from RemoteOK")

    st.subheader("📅 Jobs Over Time")
    jobs_over_time = df['year_month'].value_counts().sort_index()
    st.bar_chart(jobs_over_time)

    st.subheader("🏷️ Top 10 Skills/Tags")
    top_tags = df['tags'].str.split(', ').explode().value_counts().head(10)
    st.dataframe(top_tags)

    st.subheader("🌍 Jobs by Location")
    st.dataframe(df['location'].value_counts().head(10))


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    try:
        print("🔄 Running ETL pipeline...")
        df_raw = fetch_jobs()
        df_clean = clean_jobs(df_raw)
        save_to_csv(df_clean)

        launch_dashboard = input("Do you want to launch the Streamlit dashboard? (y/n): ").lower()
        if launch_dashboard == 'y':
            print("🚀 Launching Streamlit...")
            import subprocess
            subprocess.run(["streamlit", "run", __file__])

    except Exception as e:
        print(f"❌ Error: {e}")

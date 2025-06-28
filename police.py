import pandas as pd
from sqlalchemy import create_engine
import streamlit as st
import psycopg2
import plotly.express as px

#Load Dataset
Traffic = pd.read_csv("F:\\vscode\\traffic_stops.csv", low_memory=False)

print(Traffic)

# Replace with your connection details
host = "localhost"
port = "5432"  
database = "testing_db"
username = "postgres"
password = "Nikila"

# Create the connection string (URL format) -> postgres
engine_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"

# Create the SQLAlchemy engine
Connection = create_engine(engine_string)

# Push the DataFrame to the PostgreSQL table
Traffic.to_sql("traffic_stops_two", Connection,if_exists='replace', index=False)

print("Data successfully pushed to PostgreSQL table!")

#Database connection
def create_connection():
    try:
        connection = psycopg2.connect(
            host = "localhost",
            user = "postgres",
            port = 5432,
            password = "Nikila",
            database = "testing_db"
        )
        print("Database Connection Successful✅")
        return connection
    except Exception as e:
        print("Database Connection failed❌", e)
        return None

#Fetch data from Database
def fetch_data(query):
    connection = create_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                col = [col[0] for col in cursor.description]
                result = cursor.fetchall()
                df = pd.DataFrame(result, columns=col)
                return df
        except Exception as e:
             print("Error executing query:",e)
             return pd.DataFrame()
        finally:
            connection.close()
    else:
        print("Failed to Connect to the Database.")
        return pd.DataFrame()        
    
#------------Stearmlit Page Config-------------
st.set_page_config(page_title="SecureCheck Police DashBoard", page_icon="📝",layout="wide")
st.title("👮🚨SecureCheck:Police Check Post Digital Ledger🚨👮")
st.markdown("📝Real-Time Monitoring and Records📝")

#-------------SQL Query & Load Data-------------

st.header("🚦 Traffic Stop Records📝")
Query = "Select * From traffic_stops_two"
data = fetch_data(Query)
st.dataframe(data, use_container_width=True)

#--------------KEY METRICS--------------

with st.container():
    
    st.subheader("📊KEY METRICS📊")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        col1.metric("Total Police Stops", len(data))
        
    with col2:  
        col2.metric("Total Arrests",data["is_arrested"].sum())

    with col3:  
        col3.metric("Unique Drivers",data["driver_gender"].nunique())

    with col4: 
        col4.metric("Durg Related Stops",(data["drugs_related_stop"] == True).sum())

#----------VISUAL DATA SECTION----------

st.subheader("📈VISUAL DATA📈")
tab1,tab2,tab3,tab4 = st.tabs([
    "Stops by Violation",
    "Driver Gender Distribution",
    "Driver Race BreakDown",
    "Stop Outcome Status"
])

#Tab 1: Bar Chart - Violation Types with tab1:

violation_counts = data["violation"].value_counts().reset_index()
violation_counts.columns = ["Violation","Count"]
fig1 = px.bar(violation_counts,
              x="Violation",
              y="Count",
              color="Violation",
              title="🛑🚫Stops by Violation🚫🛑")
st.plotly_chart(fig1, use_container_width=True)

#Tab 2: Pie Chart - Gender with tab2:

gender_counts = data["driver_gender"].value_counts().reset_index()
gender_counts.columns = ["Gender","Count"]
fig2 = px.pie(gender_counts,
              names="Gender",
              values="Count",
              title="♂️♀️Drive Gender Distribution♂️♀️")
st.plotly_chart(fig2, use_container_width=True)

#Tab 3: Pie Chart - Race with tab3

race_counts = data["driver_race"].value_counts().reset_index()
race_counts.columns = ["Race","Count"]
fig3 = px.pie(race_counts,
              names="Race",
              values="Count",
              title="🚔Driver Race Breakdown🚔")
st.plotly_chart(fig3, use_container_width=True)

#Tab 4: Pie Chart - Stop Outcome with tab4

stop_counts = data["stop_outcome"].value_counts().reset_index()
stop_counts.columns = ["Stop","Count"]
fig4 = px.pie(stop_counts,
              names="Stop",
              values="Count",
              title="❌⚠️Stop Outcome Status⚠️❌")
st.plotly_chart(fig4, use_container_width=True)

#--------Query Section---------
st.header("🫧Queries🫧")

Query_Title = "☁️Medium Level Queries☁️"

selected_query = st.selectbox("**☁️Select a Medium Level Query to Run☁️**", [
"1.What are the top 10 vehicle_Number involved in drug-related stops",
"2.Which vehicles were most frequently searched",
"3.Which driver age group had the highest arrest rate",
"4.What is the gender distribution of drivers stopped in each country",
"5.Which race and gender combination has the highest search rate",
"6.What time of day sees the most traffic stops",
"7.What is the average stop duration for different violations",
"8.Are stops during the night more likely to lead to arrests",
"9.Which violations are most associated with searches or arrests",
"10.Which violations are most common among younger drivers (<25)",
"11.Is there a violation that rarely results in search or arrest",
"12.Which countries report the highest rate of drug-related stops",
"13.What is the arrest rate by country and violation",
"14.Which country has the most stops with search conducted"
])

Query_map = {
    "1.What are the top 10 vehicle_Number involved in drug-related stops": "SELECT vehicle_number,COUNT(*) AS Drugs_Related_Stop FROM traffic_stops_two WHERE drugs_related_stop = TRUE GROUP BY vehicle_number ORDER BY Drugs_Related_Stop DESC LIMIT 10;",
    "2.Which vehicles were most frequently searched": "SELECT vehicle_number,COUNT(*) AS Total_Searches FROM traffic_stops_two WHERE search_conducted = TRUE GROUP BY vehicle_number ORDER BY Total_Searches DESC LIMIT 5;",
    "3.Which driver age group had the highest arrest rate": "SELECT driver_age,COUNT(*) AS Total_Stops, SUM(CASE WHEN is_arrested = 'TRUE' THEN 1 ELSE 0 END) AS Total_Arrests, ROUND(SUM(CASE WHEN is_arrested = 'TRUE' THEN 1 ELSE 0 END * 100) / COUNT(*), 2) AS Arrest_Rate FROM traffic_stops_two GROUP BY driver_age ORDER BY Arrest_Rate DESC;",
    "4.What is the gender distribution of drivers stopped in each country": "SELECT country_name,driver_gender,COUNT(*) AS Total_Stopped FROM traffic_stops_two  GROUP BY driver_gender,country_name ORDER BY driver_gender,country_name DESC;",
    "5.Which race and gender combination has the highest search rate": "SELECT driver_race,driver_gender, COUNT(*) AS total_stops, SUM(CASE WHEN search_conducted = 'TRUE' THEN 1 ELSE 0 END) AS total_searches, ROUND(SUM(CASE WHEN search_conducted = 'TRUE' THEN 1 ELSE 0 END * 100) / COUNT(*), 2) AS search_rate_percent FROM traffic_stops_two GROUP BY driver_race, driver_gender ORDER BY search_rate_percent DESC;",
    "6.What time of day sees the most traffic stops": "SELECT stop_time AS Stop_Hour, COUNT(*) AS Most_Traffic_Stops FROM traffic_stops_two GROUP BY Stop_Hour ORDER BY Most_Traffic_Stops DESC",
    "7.What is the average stop duration for different violations": "SELECT violation, AVG( CASE Stop_Duration WHEN'0-15 Min' THEN 5 WHEN'16-30 Min' THEN 10 WHEN'30+ Min' THEN 15 ELSE NULL END ) AS avg_stop_duration FROM traffic_stops_two GROUP BY violation ORDER BY avg_stop_duration DESC;",
    "8.Are stops during the night more likely to lead to arrests": "SELECT CASE WHEN stop_time BETWEEN '04:00:00' AND '11:59:59' THEN 'MORNING' WHEN stop_time BETWEEN '12:00:00' AND '15:59:59' THEN 'AFTERNOON' WHEN stop_time BETWEEN '16:00:00' AND '18:59:59' THEN 'EVENING' ELSE 'NIGHT' END AS time_of_day, COUNT(*) AS total_stops, SUM(CASE WHEN is_arrested = 'TRUE' THEN 1 ELSE 0 END) AS Total_Arrests, ROUND(SUM(CASE WHEN is_arrested = 'TRUE' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS Arrest_Rate_Percent FROM traffic_stops_two GROUP BY time_of_day;",
    "9.Which violations are most associated with searches or arrests": "SELECT violation,COUNT(*) AS Total_Stops, SUM(CASE WHEN search_conducted = 'TRUE' THEN 1 ELSE 0 END) AS total_searches, SUM(CASE WHEN is_arrested = 'TRUE' THEN 1 ELSE 0 END) AS total_arrests, ROUND(SUM(CASE WHEN search_conducted = 'TRUE' THEN 1 ELSE 0 END * 100) / COUNT(*), 2) AS Search_Rate, ROUND(SUM(CASE WHEN is_arrested = 'TRUE' THEN 1 ELSE 0 END * 100) / COUNT(*), 2) AS Arrest_Rate FROM traffic_stops_two GROUP BY violation HAVING  ROUND(SUM(CASE WHEN search_conducted = 'TRUE' THEN 1 ELSE 0 END * 100) / COUNT(*), 2) > 10 OR ROUND(SUM(CASE WHEN is_arrested = 'TRUE' THEN 1 ELSE 0 END * 100) / COUNT(*), 2) > 10 ORDER BY Search_Rate DESC, Arrest_Rate DESC;",
    "10.Which violations are most common among younger drivers (<25)": "SELECT violation,COUNT(*) AS Total_Violations FROM traffic_stops_two WHERE driver_age < 25 GROUP BY violation ORDER BY Total_Violations DESC LIMIT 5;",
    "11.Is there a violation that rarely results in search or arrest": "SELECT violation,COUNT(*) AS Total_Stop, SUM(CASE WHEN search_conducted = 'TRUE' THEN 1 ELSE 0 END) AS Searches, SUM(CASE WHEN is_arrested = 'TRUE' THEN 1 ELSE 0 END) AS Arrests, ROUND(SUM(CASE WHEN search_conducted = 'TRUE' THEN 1 ELSE 0 END) * 100 / COUNT(*) , 2) AS Total_Searches, ROUND(SUM(CASE WHEN is_arrested = 'TRUE' THEN 1 ELSE 0 END) * 100 / COUNT(*) , 2) AS Total_Arrests FROM traffic_stops_two GROUP BY violation ORDER BY Total_Searches ASC, Total_Arrests ASC;",
    "12.Which countries report the highest rate of drug-related stops": "SELECT country_name,SUM(CASE WHEN drugs_related_stop = 'TRUE' THEN 1 ELSE 0 END) AS Drug_Related_Stops FROM traffic_stops_two GROUP BY country_name ORDER BY Drug_Related_Stops DESC;",
    "13.What is the arrest rate by country and violation": "SELECT country_name,violation, COUNT(*) AS Total_Stops, SUM(CASE WHEN is_arrested = 'TRUE' THEN 1 ELSE 0 END) AS Total_Arrests, ROUND(SUM(CASE WHEN is_arrested = 'TRUE' THEN 1 ELSE 0 END * 100) / COUNT(*), 2) AS Arrest_Rate FROM traffic_stops_two GROUP BY country_name, violation ORDER BY Arrest_Rate DESC;",
    "14.Which country has the most stops with search conducted": "SELECT Country_Name,COUNT(*) AS Search_Conducted FROM traffic_stops_two WHERE Search_Conducted = 'TRUE' GROUP BY Country_Name ORDER BY Search_Conducted DESC;"
}

if st.button("▶️Run Query▶️"):
    result = fetch_data(Query_map[selected_query])
    if not result.empty:
        st.write(result)
    else:
        st.warning("⚠️No result found⚠️")

Query_Title = "☁️Complex Level Queries☁️"

selected_query = st.selectbox("**☁️Select Complex Level Query to Run☁️**", [
"1.Yearly Breakdown of Stops and Arrests by Country (Using Subquery and Window Functions)",
"2.Driver Violation Trends Based on Age and Race (Join with Subquery)",
"3.Time Period Analysis of Stops (Joining with Date Functions) , Number of Stops by Year,Month, Hour of the Day",
"4.Violations with High Search and Arrest Rates (Window Function)",
"5.Driver Demographics by Country (Age, Gender, and Race)",
"6.Top 5 Violations with Highest Arrest Rates"

])

Query_map = {
  "1.Yearly Breakdown of Stops and Arrests by Country (Using Subquery and Window Functions)": "SELECT year,country_name,total_stops,arrests, ROUND(arrests * 100 / NULLIF(total_stops, 0), 2) AS arrest_rate, LAG(arrests) OVER(PARTITION BY country_name ORDER BY year) AS prev_year_arrests, arrests - LAG(arrests) OVER(PARTITION BY country_name ORDER BY year) AS arrest_change FROM ( SELECT  EXTRACT(YEAR FROM stop_date::date) AS year, country_name, COUNT(*) AS total_stops, SUM(CASE WHEN is_arrested = 'TRUE' THEN 1 ELSE 0 END) AS arrests FROM traffic_stops_two GROUP BY country_name, EXTRACT(YEAR FROM stop_date::date)) AS yearly_data ORDER BY country_name, year DESC;",
  "2.Driver Violation Trends Based on Age and Race (Join with Subquery)": "WITH age_grouped AS (SELECT driver_race,violation,driver_age, CASE  WHEN driver_age < 18 THEN 'Under 18' WHEN driver_age BETWEEN 18 AND 25 THEN '18-25' WHEN driver_age BETWEEN 26 AND 40 THEN '26-40' WHEN driver_age BETWEEN 41 AND 60 THEN '41-60' ELSE '60+'  END AS age_group FROM traffic_stops_two WHERE driver_age IS NOT NULL AND violation IS NOT NULL) SELECT age_group,driver_race,violation, COUNT(*) AS violation_count FROM age_grouped GROUP BY age_group, driver_race, violation ORDER BY age_group, driver_race, violation_count DESC LIMIT 5;",
  "3.Time Period Analysis of Stops (Joining with Date Functions) , Number of Stops by Year,Month, Hour of the Day": "SELECT EXTRACT(YEAR FROM stop_date::date) AS Year, EXTRACT(MONTH FROM stop_date::date) AS Month, EXTRACT(HOUR FROM stop_time::time) AS Hour, COUNT(*) AS total_stops FROM traffic_stops_two WHERE stop_date IS NOT NULL AND stop_time IS NOT NULL GROUP BY Year, Month, Hour ORDER BY Year, Month, Hour;",
  "4.Violations with High Search and Arrest Rates (Window Function)": "WITH violation_stats AS (SELECT violation,COUNT(*) AS total_stops, SUM(CASE WHEN search_conducted = 'TRUE' THEN 1 ELSE 0 END) AS total_searches, SUM(CASE WHEN is_arrested = 'TRUE' THEN 1 ELSE 0 END) AS total_arrests FROM traffic_stops_two WHERE violation IS NOT NULL GROUP BY violation) SELECT violation,total_stops,total_searches,total_arrests, ROUND(total_searches * 100.0/ total_stops, 2) AS search_rate_percent, RANK() OVER (ORDER BY ROUND(total_searches * 100.0/ total_stops, 2) DESC) AS search_rank, ROUND(total_arrests * 100.0/ total_stops, 2) AS arrest_rate_percent, RANK() OVER (ORDER BY ROUND(total_arrests * 100.0/ total_stops, 2) DESC) AS arrest_rank FROM violation_stats ORDER BY arrest_rate_percent DESC;",
  "5.Driver Demographics by Country (Age, Gender, and Race)": "SELECT country_name,driver_gender,driver_race, COUNT(*) AS total_stops, ROUND(AVG(driver_age),1) AS Avg_Age FROM traffic_stops_two WHERE driver_gender IS NOT NULL AND driver_race IS NOT NULL GROUP BY country_name, driver_gender, driver_race ORDER BY country_name, driver_gender;",
  "6.Top 5 Violations with Highest Arrest Rates": "SELECT violation, COUNT(*) AS Total_Stops, SUM(CASE WHEN is_arrested = 'TRUE' THEN 1 ELSE 0 END) AS Total_Arrests, ROUND(100.0 * SUM(CASE WHEN is_arrested = 'TRUE' THEN 1 ELSE 0 END) / COUNT(*), 2) AS Arrest_Rate FROM traffic_stops_two WHERE violation IS NOT NULL GROUP BY violation ORDER BY Arrest_Rate DESC LIMIT 5;"
  
}

if st.button("▶️Run Query▶️", key="run_query_button"):
    result = fetch_data(Query_map[selected_query])
    if not result.empty:
        st.write(result)
    else:
        st.warning("⚠️No result found⚠️")

#--------STREAMLIT DASHBROAD---------

st.header("🚔Add New Police Log & Predict Outcome and Violation📋")
 
#Inuput Form
with st.form("Log_Form"):
    stop_date = st.date_input("Stop Date")
    stop_time = st.time_input("Stop Time")
    country_name = st.text_input("Country Name")
    driver_gender = st.selectbox("Driver Gender",["Male","Female"])
    driver_age = st.number_input("Driver Age ",min_value=18,max_value=85)
    driver_race = st.text_input("Driver Race")
    search_conducted = st.selectbox("Was Search Conducted?",["Yes","No"])
    search_type = st.text_input("Search Type")
    is_arrested = st.selectbox("Was Driver Arrested?",["Yes","No"])
    stop_duration = st.selectbox("Stop Duration",["0-15Min","16-30Min","30+Min"])
    vehicle_number = st.text_input("Vehicle Number")

    if st.form_submit_button("Predict Stop Outcome & Violation"):

        st.subheader("📍Prediction Summary📍")

        predicted_violation = "Speeding"
        predicted_Outcome = "Warning"

        st.markdown(f"""
                    **Predicted Violation**:{predicted_violation}
                    **Predicted Stop Outcome**:{predicted_Outcome}
""")
        
        st.markdown(f"""
        📤 A **{driver_age}**-year-old **{driver_gender}** driver in was stopped at **{stop_time}** on **{stop_date}**
        No search was conducted,and the stop was not drug-related.
        Stop duration:**{stop_duration}**
        .Vehicle Number:**{vehicle_number
                           if vehicle_number
                           else '****'}**.          
 """)









create table traffic_stops(stop_date DATE,stop_time TIME,country_name text,driver_gender char(1),driver_age_raw int,driver_age int,driver_race text,violation_raw text,violation text,search_conducted bool,search_type text,stop_outcome text,is_arrested boolean,stop_duration text,drugs_related_stop boolean,vehicle_number varchar(10));
select * from traffic_stops_two

create table traffic_stops_two(stop_date date,stop_time time,country_name TEXT,driver_gender VARCHAR(1),driver_age_raw INT,driver_age int,driver_race TEXT,violation_raw TEXT,violation TEXT,search_conducted BOOL,search_type TEXT,stop_outcome TEXT,is_arrested BOOL,stop_duration TEXT,drugs_related_stop BOOL,vehicle_number VARCHAR(10))
copy traffic_stops_two from 'F:\traffic_stops.csv' delimiter ',' csv header

--1.What are the top 10 vehicle_Number involved in drug-related stops?
SELECT vehicle_number,COUNT(*) AS Drugs_Related_Stop
FROM traffic_stops_two WHERE drugs_related_stop = TRUE 
GROUP BY vehicle_number ORDER BY Drugs_Related_Stop DESC LIMIT 10;

--2.Which vehicles were most frequently searched?
SELECT vehicle_number,COUNT(*) AS Total_Searches
FROM traffic_stops_two WHERE search_conducted = TRUE
GROUP BY vehicle_number ORDER BY Total_Searches DESC LIMIT 5;

--3.Which driver age group had the highest arrest rate?
SELECT driver_age,
  COUNT(*) AS Total_Stops,
  SUM(CASE WHEN is_arrested = 'TRUE' THEN 1 ELSE 0 END) AS Total_Arrests,
  ROUND(SUM(CASE WHEN is_arrested = 'TRUE' THEN 1 ELSE 0 END * 100) / COUNT(*), 2) AS Arrest_Rate
FROM traffic_stops_two
GROUP BY driver_age
ORDER BY Arrest_Rate DESC;

--4.What is the gender distribution of drivers stopped in each country?
SELECT country_name,driver_gender,COUNT(*) AS Total_Stopped
FROM traffic_stops_two 
GROUP BY driver_gender,country_name ORDER BY driver_gender,country_name DESC;

--5.Which race and gender combination has the highest search rate?
SELECT driver_race,driver_gender,
  COUNT(*) AS total_stops,
  SUM(CASE WHEN search_conducted = 'TRUE' THEN 1 ELSE 0 END) AS total_searches,
  ROUND(SUM(CASE WHEN search_conducted = 'TRUE' THEN 1 ELSE 0 END * 100) / COUNT(*), 2) AS search_rate_percent
FROM traffic_stops_two
GROUP BY driver_race, driver_gender
ORDER BY search_rate_percent DESC;

--6.What time of day sees the most traffic stops?
SELECT stop_time AS Stop_Hour,COUNT(*) AS Most_Traffic_Stops
FROM traffic_stops_two
GROUP BY Stop_Hour ORDER BY Most_Traffic_Stops DESC

--7.What is the average stop duration for different violations?
SELECT violation,
AVG(
CASE Stop_Duration
    WHEN'0-15 Min' THEN 5
    WHEN'16-30 Min' THEN 10
    WHEN'30+ Min' THEN 15
    ELSE NULL
END
	) AS avg_stop_duration
FROM traffic_stops_two
GROUP BY violation ORDER BY avg_stop_duration DESC;

--8.Are stops during the night more likely to lead to arrests?
SELECT 
  CASE 
    WHEN stop_time BETWEEN '04:00:00' AND '11:59:59' THEN 'MORNING'
	WHEN stop_time BETWEEN '12:00:00' AND '15:59:59' THEN 'AFTERNOON'
    WHEN stop_time BETWEEN '16:00:00' AND '18:59:59' THEN 'EVENING'
    ELSE 'NIGHT'
  END AS time_of_day,
  COUNT(*) AS total_stops,
  SUM(CASE WHEN is_arrested = 'TRUE' THEN 1 ELSE 0 END) AS Total_Arrests,
  ROUND(SUM(CASE WHEN is_arrested = 'TRUE' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS Arrest_Rate_Percent
FROM traffic_stops_two
GROUP BY time_of_day;

--9.Which violations are most associated with searches or arrests?
SELECT violation,COUNT(*) AS Total_Stops,
  SUM(CASE WHEN search_conducted = 'TRUE' THEN 1 ELSE 0 END) AS total_searches,
  SUM(CASE WHEN is_arrested = 'TRUE' THEN 1 ELSE 0 END) AS total_arrests,
  ROUND(SUM(CASE WHEN search_conducted = 'TRUE' THEN 1 ELSE 0 END * 100) / COUNT(*), 2) AS Search_Rate,
  ROUND(SUM(CASE WHEN is_arrested = 'TRUE' THEN 1 ELSE 0 END * 100) / COUNT(*), 2) AS Arrest_Rate
FROM traffic_stops_two
GROUP BY violation
HAVING 
  ROUND(SUM(CASE WHEN search_conducted = 'TRUE' THEN 1 ELSE 0 END * 100) / COUNT(*), 2) > 10
  OR
  ROUND(SUM(CASE WHEN is_arrested = 'TRUE' THEN 1 ELSE 0 END * 100) / COUNT(*), 2) > 10
ORDER BY Search_Rate DESC, Arrest_Rate DESC;

--10.Which violations are most common among younger drivers (<25)?
SELECT violation,COUNT(*) AS Total_Violations
FROM traffic_stops_two WHERE driver_age < 25
GROUP BY violation ORDER BY Total_Violations DESC
LIMIT 5;

--11.Is there a violation that rarely results in search or arrest?
SELECT violation,COUNT(*) AS Total_Stop,
   SUM(CASE WHEN search_conducted = 'TRUE' THEN 1 ELSE 0 END) AS Searches,
   SUM(CASE WHEN is_arrested = 'TRUE' THEN 1 ELSE 0 END) AS Arrests,
   ROUND(SUM(CASE WHEN search_conducted = 'TRUE' THEN 1 ELSE 0 END) * 100 / COUNT(*) , 2) AS Total_Searches,
   ROUND(SUM(CASE WHEN is_arrested = 'TRUE' THEN 1 ELSE 0 END) * 100 / COUNT(*) , 2) AS Total_Arrests
FROM traffic_stops_two
GROUP BY violation
ORDER BY Total_Searches ASC, Total_Arrests ASC;

--12.Which countries report the highest rate of drug-related stops?
SELECT country_name,SUM(CASE WHEN drugs_related_stop = 'TRUE' THEN 1 ELSE 0 END) AS Drug_Related_Stops
FROM traffic_stops_two
GROUP BY country_name ORDER BY Drug_Related_Stops DESC;

--13.What is the arrest rate by country and violation?
SELECT country_name,violation,
COUNT(*) AS Total_Stops,
  SUM(CASE WHEN is_arrested = 'TRUE' THEN 1 ELSE 0 END) AS Total_Arrests,
  ROUND(SUM(CASE WHEN is_arrested = 'TRUE' THEN 1 ELSE 0 END * 100) / COUNT(*), 2) AS Arrest_Rate
FROM traffic_stops_two
GROUP BY country_name, violation
ORDER BY Arrest_Rate DESC;

--14.Which country has the most stops with search conducted?
SELECT Country_Name,COUNT(*) AS Search_Conducted
FROM traffic_stops_two
WHERE Search_Conducted = 'TRUE'
GROUP BY Country_Name
ORDER BY Search_Conducted DESC;

--(Complex): 

--1.Yearly Breakdown of Stops and Arrests by Country (Using Subquery and Window Functions)
SELECT year,country_name,total_stops,arrests,
  ROUND(arrests * 100 / NULLIF(total_stops, 0), 2) AS arrest_rate,
  LAG(arrests) OVER(PARTITION BY country_name ORDER BY year) AS prev_year_arrests,
  arrests - LAG(arrests) OVER(PARTITION BY country_name ORDER BY year) AS arrest_change 
FROM (
  SELECT 
    EXTRACT(YEAR FROM stop_date::date) AS year,
    country_name,
    COUNT(*) AS total_stops,
    SUM(CASE WHEN is_arrested = 'TRUE' THEN 1 ELSE 0 END) AS arrests
  FROM traffic_stops_two
  GROUP BY country_name, EXTRACT(YEAR FROM stop_date::date)
) AS yearly_data
ORDER BY country_name, year DESC;

--2.Driver Violation Trends Based on Age and Race (Join with Subquery)
-- Subquery to categorize age groups
WITH age_grouped AS (
  SELECT driver_race,violation,driver_age,
    CASE 
      WHEN driver_age < 18 THEN 'Under 18'
      WHEN driver_age BETWEEN 18 AND 25 THEN '18-25'
      WHEN driver_age BETWEEN 26 AND 40 THEN '26-40'
      WHEN driver_age BETWEEN 41 AND 60 THEN '41-60'
      ELSE '60+' 
    END AS age_group
  FROM traffic_stops_two
  WHERE driver_age IS NOT NULL AND violation IS NOT NULL
)

-- Join subquery and count violation trends
SELECT age_group,driver_race,violation,
  COUNT(*) AS violation_count
FROM age_grouped
GROUP BY age_group, driver_race, violation
ORDER BY age_group, driver_race, violation_count DESC LIMIT 5;

--3.Time Period Analysis of Stops (Joining with Date Functions) , Number of Stops by Year,Month, Hour of the Day
SELECT
  EXTRACT(YEAR FROM stop_date::date) AS Year,
  EXTRACT(MONTH FROM stop_date::date) AS Month,
  EXTRACT(HOUR FROM stop_time::time) AS Hour,
  COUNT(*) AS total_stops
FROM traffic_stops_two
WHERE stop_date IS NOT NULL AND stop_time IS NOT NULL
GROUP BY Year, Month, Hour
ORDER BY Year, Month, Hour;

--4.Violations with High Search and Arrest Rates (Window Function)
WITH violation_stats AS (
  SELECT violation,COUNT(*) AS total_stops,
    SUM(CASE WHEN search_conducted = 'TRUE' THEN 1 ELSE 0 END) AS total_searches,
    SUM(CASE WHEN is_arrested = 'TRUE' THEN 1 ELSE 0 END) AS total_arrests
  FROM traffic_stops_two WHERE violation IS NOT NULL
  GROUP BY violation
)

SELECT violation,total_stops,total_searches,total_arrests,
  ROUND(total_searches * 100.0/ total_stops, 2) AS search_rate_percent,
  RANK() OVER (ORDER BY ROUND(total_searches * 100.0/ total_stops, 2) DESC) AS search_rank,
  ROUND(total_arrests * 100.0/ total_stops, 2) AS arrest_rate_percent,
  RANK() OVER (ORDER BY ROUND(total_arrests * 100.0/ total_stops, 2) DESC) AS arrest_rank
FROM violation_stats
ORDER BY arrest_rate_percent DESC;

--5.Driver Demographics by Country (Age, Gender, and Race)
SELECT country_name,driver_gender,driver_race,
  COUNT(*) AS total_stops,
  ROUND(AVG(driver_age),1) AS Avg_Age
FROM traffic_stops_two
WHERE driver_gender IS NOT NULL AND driver_race IS NOT NULL
GROUP BY country_name, driver_gender, driver_race
ORDER BY country_name, driver_gender;

--6.Top 5 Violations with Highest Arrest Rates
SELECT violation,
  COUNT(*) AS Total_Stops,
  SUM(CASE WHEN is_arrested = 'TRUE' THEN 1 ELSE 0 END) AS Total_Arrests,
  ROUND(100.0 * SUM(CASE WHEN is_arrested = 'TRUE' THEN 1 ELSE 0 END) / COUNT(*), 2) AS Arrest_Rate
FROM traffic_stops_two
WHERE violation IS NOT NULL
GROUP BY violation
ORDER BY Arrest_Rate DESC
LIMIT 5;






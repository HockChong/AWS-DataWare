
## Introduction
A music streaming startup, Sparkify, has grown their user base and song database and want to move their processes and data onto the cloud. Their data resides in S3, in a directory of JSON logs on user activity on the app, as well as a directory with JSON metadata on the songs in their app.

As their data engineer, you are tasked with building an ETL pipeline that extracts their data from S3, stages them in Redshift, and transforms data into a set of dimensional tables for their analytics team to continue finding insights into what songs their users are listening to.


## DataSets
- Song data: s3://udacity-dend/song_data 
- Log data: s3://udacity-dend/log_data
- Log metadata: s3://udacity-dend/log_json_path.json

## Data Schema

### Fact Table
1. songplays - records in event data associated with song plays i.e. records with page
- songplay_id, start_time, user_id, level, song_id, artist_id, session_id, location, user_agent

### Dimension Tables
2. users - users in the app
- user_id, first_name, last_name, gender, level
3. songs - songs in music database
- song_id, title, artist_id, year, duration
4. artists - artists in music database
- artist_id, name, location, latitude, longitude
5. time - timestamps of records in songplays broken down into specific units
- start_time, hour, day, week, month, year, weekday

## Project File
- create_table.py is where I'll create my fact and dimension tables for the star schema in Redshift.
- etl.py is where I'll load data from S3 into staging tables on Redshift and then process that data into your analytics tables on Redshift.
- sql_queries.py is where I define my SQL statements, which will be imported into the two other files above.

## How to run this file
1. run create_table.py
2. run etl.py

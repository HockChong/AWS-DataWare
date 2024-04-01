import configparser
import psycopg2
import configparser
import psycopg2


# CONFIG
config = configparser.ConfigParser()
config.read('dwh.cfg')


# CREATE DROP TABLES IN THE BEGINNING IF TABLES EXIST IN CASE WE WANT TO RESET THE DATABASE AND TEST ETL PIPELINE

staging_events_table_drop = "DROP TABLE IF EXISTS staging_events;"
staging_songs_table_drop = "DROP TABLE IF EXISTS staging_songs;"
songplay_table_drop = "DROP TABLE IF EXISTS songplay;"
user_table_drop = "DROP TABLE IF EXISTS users;"
song_table_drop = "DROP TABLE IF EXISTS songs;"
artist_table_drop = "DROP TABLE IF EXISTS artists;"
time_table_drop = "DROP TABLE IF EXISTS time;"

# CREATE TABLES

staging_events_table_create= ("""CREATE TABLE IF NOT EXISTS staging_events (
    artist VARCHAR(50),
    auth VARCHAR(50),
    first_name VARCHAR(50),
    gender VARCHAR(10),
    itemInSession INT,
    last_name VARCHAR(50),
    length FLOAT,
    level VARCHAR(50),
    location VARCHAR(50),
    method VARCHAR(50),
    page VARCHAR(50),
    registration FLOAT,
    sessionId INT,
    song VARCHAR(50),
    status INT,
    ts BIGINT,
    userAgent VARCHAR(50),
    userId INT)
""")

staging_songs_table_create = ("""CREATE TABLE IF NOT EXISTS staging_songs (
    num_songs INT NOT NULL,
    artist_id VARCHAR NOT NULL,
    artist_latitude FLOAT,
    artist_longitude FLOAT,
    artist_location VARCHAR(30),
    artist_name VARCHAR(30),
    song_id VARCHAR NOT NULL,
    title VARCHAR(30),
    duration FLOAT,
    year INT)
""")

songplay_table_create = ("""CREATE TABLE IF NOT EXISTS songplay (
    songplay_id INT PRIMARY KEY NOT NULL IDENTITY(1,1),
    start_time TIMESTAMP,
    user_id INT,
    level VARCHAR(30),
    song_id VARCHAR(30),
    artist_id VARCHAR(30),
    session_id INT,
    location VARCHAR(30),
    user_agent VARCHAR(30))
""")

user_table_create = ("""CREATE TABLE IF NOT EXISTS users (
    user_id INT PRIMARY KEY NOT NULL,
    first_name VARCHAR(30),
    last_name VARCHAR(30),
    gender VARCHAR(30),
    level VARCHAR(30))
""")

song_table_create = ("""CREATE TABLE IF NOT EXISTS songs (
    song_id VARCHAR PRIMARY KEY NOT NULL,
    title VARCHAR(30),
    artist_id VARCHAR(30),
    year INT,
    duration FLOAT)
""")


artist_table_create = ("""CREATE TABLE IF NOT EXISTS artists (
    artist_id VARCHAR(30) PRIMARY KEY NOT NULL,
    name VARCHAR(30),
    location VARCHAR(30),
    latitude FLOAT,
    longitude FLOAT)
""")

time_table_create = ("""CREATE TABLE IF NOT EXISTS time (
    start_time TIMESTAMP PRIMARY KEY NOT NULL,
    hour INT,
    day INT,
    week INT,
    month INT,
    year INT,
    weekday INT)
""")

# STAGING TABLES

staging_events_copy = ("""
    COPY staging_events FROM {}
    CREDENTIALS 'aws_iam_role={}'
    FORMAT AS JSON {}
    REGION 'us-west-2';
""").format(config.get('S3', 'LOG_DATA'), config.get('IAM_ROLE', 'ARN'), config.get('S3', 'LOG_JSONPATH'))

staging_songs_copy = ("""
                      
    COPY staging_songs FROM {}
    CREDENTIALS 'aws_iam_role={}'
    FORMAT AS JSON 'auto'
    REGION 'us-west-2';
""").format(config.get('S3', 'SONG_DATA'), config.get('IAM_ROLE', 'ARN'))

# FINAL TABLES

songplay_table_insert = ("""
    INSERT INTO songplay (start_time, user_id, level, song_id, artist_id, session_id, location, user_agent)
    SELECT 
        TIMESTAMP 'epoch' + se.ts/1000 * INTERVAL '1 second' AS start_time,
        se.userId AS user_id,
        se.level AS level,
        ss.song_id AS song_id,
        ss.artist_id AS artist_id,
        se.sessionId AS session_id,
        se.location AS location,
        se.userAgent AS user_agent
    FROM staging_events se
    JOIN staging_songs ss ON (se.song = ss.title AND se.artist = ss.artist_name)
    WHERE se.page = 'NextSong';
""")

user_table_insert = ("""
    INSERT INTO users (user_id, first_name, last_name, gender, level)
    SELECT DISTINCT
        userId,
        first_name,
        last_name,
        gender,
        level
    FROM staging_events
    WHERE page = 'NextSong';
""")

song_table_insert = ("""
    INSERT INTO songs (song_id, title, artist_id, year, duration)
    SELECT DISTINCT
        song_id,
        title,
        artist_id,
        year,
        duration
    FROM staging_songs;
""")

artist_table_insert = ("""
    INSERT INTO artists (artist_id, name, location, latitude, longitude)
    SELECT DISTINCT
        artist_id,
        artist_name,
        artist_location,
        artist_latitude,
        artist_longitude
    FROM staging_songs;
""")

time_table_insert = ("""
    INSERT INTO time (start_time, hour, day, week, month, year, weekday)
    SELECT DISTINCT
        start_time AS start_time,
        EXTRACT(hour FROM start_time) AS hour,
        EXTRACT(day FROM start_time) AS day,
        EXTRACT(week FROM start_time) AS week,
        EXTRACT(month FROM start_time) AS month,
        EXTRACT(year FROM start_time) AS year,
        EXTRACT(weekday FROM start_time) AS weekday
    FROM songplay;
""")

# QUERY LISTS

create_table_queries = [staging_events_table_create, staging_songs_table_create, songplay_table_create, user_table_create, song_table_create, artist_table_create, time_table_create]
drop_table_queries = [staging_events_table_drop, staging_songs_table_drop, songplay_table_drop, user_table_drop, song_table_drop, artist_table_drop, time_table_drop]
copy_table_queries = [staging_events_copy, staging_songs_copy]
insert_table_queries = [songplay_table_insert, user_table_insert, song_table_insert, artist_table_insert, time_table_insert]

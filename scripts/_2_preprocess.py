import pandas as pd
import re

def preprocess(data):

    # Define regex pattern for WhatsApp date-time format :-
    pattern = r"\[\d{1,2}/\d{1,2}/\d{2},\s\d{1,2}:\d{2}:\d{2}\s?(?:AM|PM|am|pm)\]"

    # Split data into messages and extract corresponding timestamps :-
    message = re.split(pattern, data)[1:]    
    dates = re.findall(pattern, data)           

    # Create initial DataFrame :-
    df = pd.DataFrame({'user_msg':message, 'msg_dates':dates})

    # Clean and convert 'message_date' column :-
    df['msg_dates'] = df['msg_dates'].str.replace(r"[\[\]]", "", regex=True)
    df['msg_dates'] = df['msg_dates'].str.replace('\u202f', " ", regex=True)
    df['msg_dates'] = df['msg_dates'].str.replace('\xa0', " ", regex=True)
    df['msg_dates'] = pd.to_datetime(df['msg_dates'], dayfirst=True, errors='coerce')
    df['date'] = df['msg_dates'].dt.strftime('%d-%m-%Y, %I:%M:%S %p')

    # Separate user and actual message content :-
    user = []
    messages = []

    for message in df['user_msg']:
        entry = re.split(r'([\w\W]+?):\s', message)
        if entry[1:]:
            user.append(entry[1])
            messages.append(entry[2])
        else:
            user.append('group_notification')
            messages.append(entry[0])

    df['user'] = user
    df['message'] = messages
    df.drop(columns=['user_msg'], inplace=True)

    # Extract useful datetime features :-
    df['month_num'] = df['msg_dates'].dt.month
    df['only_date'] = df['msg_dates'].dt.date
    df['day_name'] = df['msg_dates'].dt.day_name()
    df['year'] = df['msg_dates'].dt.year
    df['month'] = df['msg_dates'].dt.month_name()
    df['day'] = df['msg_dates'].dt.day
    df['hour'] = df['msg_dates'].dt.hour
    df['minute'] = df['msg_dates'].dt.minute

    # Create 'period' column for hourly time ranges in AM/PM format :-
    period = []

    for hour in df['hour']:
        # Convert 24-hour time to 12-hour format with AM/PM
        start_hour = hour % 12 or 12
        end_hour = (hour + 1) % 12 or 12

        start_ampm = "AM" if hour < 12 else "PM"
        end_ampm = "AM" if (hour + 1) < 12 or (hour + 1) == 24 else "PM"

        period.append(f"{start_hour} {start_ampm} - {end_hour} {end_ampm}")

    df['period'] = period

    # Return final structured DataFrame :-
    return df

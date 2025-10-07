from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji
import re
import matplotlib.pyplot as plt
from matplotlib import font_manager
import os

# Initialize URL extractor (used to find all URLs in messages) :-
extract = URLExtract()

# Global list of phrases/messages to ignore (e.g., media or call notifications) :-
omitted_list = [
    "media omitted",
    "image omitted",
    "sticker omitted",
    "audio omitted",
    "call",
    "missed call",
    "voice call",
    "video call",
    "video omitted"
]

# Utility functions :-

def set_emoji_font():
    project_root = os.path.dirname(os.path.dirname(__file__))  
    emoji_font_path = os.path.join(project_root, "file/NotoEmoji-Regular.ttf")

    if os.path.exists(emoji_font_path):
        print(f"✅ Using emoji font: {emoji_font_path}")
        return font_manager.FontProperties(fname=emoji_font_path)
    else:
        print("⚠️ NotoEmoji-Regular.ttf not found. Emojis may not render correctly.")
        return None

emoji_prop = set_emoji_font()

def clean_message(message):
    return re.sub(r'[\u200e\u200f\u202a-\u202e]', '', message).strip().lower()

def count_media_messages(df):
    messages = df['message'].apply(clean_message)
    return messages[messages.isin(omitted_list)].shape[0]

# Fetch stats :-
def fetch_stats(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Total number of messages :-
    num_messages = df.shape[0]

    # Total number of words :-
    words = []

    for message in df['message']:
        words.extend(message.split())

    # Total number of media messages :-
    num_media_messages = count_media_messages(df)

    # Total number of links :-
    links = []

    for message in df['message']:
        links.extend(extract.find_urls(message))

    return num_messages, len(words), num_media_messages, len(links)

# Most busy users :-
def most_busy_users(df):
    x = df['user'].value_counts().head()
    df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(columns={'index': 'Name', 'user': 'Percent (%)'})

    return x, df

# Time analysis :-

# Monthly timeline :-
def monthly_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    time = []

    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + '-' + str(timeline['year'][i]))

    timeline['time'] = time
    return timeline

# Daily timeline :-
def daily_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    daily_timeline = df.groupby('only_date').count()['message'].reset_index()
    return daily_timeline

# Activity maps :-

def weekly_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df['day_name'].value_counts()


def monthly_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df['month'].value_counts()


def activity_heatmap(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    user_heatmap = (
        df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count')
        .fillna(0)
    )
    return user_heatmap

# Text analysis :-

def create_wordcloud(selected_user, df):
    f = open('file/stop_hinglish.txt', 'r')
    stop_words = f.read()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Clean and filter messages :-
    temp = df.copy()
    temp['message'] = temp['message'].apply(clean_message)
    temp = temp[~temp['message'].isin(omitted_list)]

    # Remove stop words :-
    def remove_stop_words(message):
        y = []
        for word in message.lower().split():
            if word not in stop_words:
                y.append(word)
        return " ".join(y)

    temp['message'] = temp['message'].apply(remove_stop_words)

    # Generate WordCloud image :-
    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    df_wc = wc.generate(temp['message'].str.cat(sep=" "))
    return df_wc


def most_common_words(selected_user, df):
    f = open('file/stop_hinglish.txt', 'r')
    stop_words = f.read().split()

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    # Remove group notifications and omitted messages :-
    temp = df[df['user'] != 'group_notification']
    temp['message'] = temp['message'].apply(clean_message)
    temp = temp[~temp['message'].isin(omitted_list)]

    # Tokenize and count words :-
    words = []
    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    # Return top 20 most common words :-
    most_common_df = pd.DataFrame(Counter(words).most_common(20))
    return most_common_df

# Emoji analysis :-

def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if emoji.is_emoji(c)])

    emoji_df = pd.DataFrame(Counter(emojis).most_common(),
                            columns=['Emoji', 'Count'])
    return emoji_df


    
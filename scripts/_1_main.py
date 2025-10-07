import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import _2_preprocess as preprocessor
import _3_functions as helper
from _3_functions import emoji_prop

# Streamlit page configuration :-
st.set_page_config(
    layout="wide",          
    initial_sidebar_state="expanded"  
)

# Streamlit page title :-
st.title("📊 WhatsApp Chat Analyzer")

# Upload WhatsApp chat file :-
uploaded_file = st.sidebar.file_uploader("📂 Choose a chat file")

if uploaded_file is not None:
    # Read and decode the uploaded chat data :-
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode('utf-8')

    # Preprocess the chat data :-
    df = preprocessor.preprocess(data)
    # st.dataframe(df)

    # Prepare user_list for selection :-
    user_list = df['user'].unique().tolist()
    user_list.sort()
    user_list.insert(0, 'Overall')

    selected_user = st.sidebar.selectbox("👥 Show analysis w.r.t.", user_list)

    # Trigger analysis when button is clicked :-
    if st.sidebar.button('Show Analysis'):
        # SECTION 1 - Top Stats :-
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)

        st.title('📈 Top Statistics')
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header('Total Messages')
            st.title(num_messages)
        with col2:
            st.header('Total Words')
            st.title(words)
        with col3:
            st.header('Media Shared')
            st.title(num_media_messages)
        with col4:
            st.header('Links Shared')
            st.title(num_links)

        # SECTION 2 - Timeline :-

        # Monthly timeline :-
        st.title('📅 Monthly Timeline')
        monthly_timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(monthly_timeline['time'], monthly_timeline['message'], color='green')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # Daily timeline :-
        st.title('📅 Daily Timeline')
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='purple')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        #  SECTION 3 — Activity map :-
        st.title('🕒 Activity Map')
        col1, col2 = st.columns(2)

        # Weekly Activity :-
        with col1:
            st.header('Most Busy Day')
            busy_day = helper.weekly_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color='orange')
            plt.xticks(rotation=45)
            st.pyplot(fig)

        # Monthly Activity :-
        with col2:
            st.header('Most Busy Month')
            busy_month = helper.monthly_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='red')
            plt.xticks(rotation=45)
            st.pyplot(fig)

        # Weekly Heatmap (Day vs Hour) :-
        st.title('🔥 Weekly Activity Heatmap')
        user_heatmap = helper.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots()
        ax = sns.heatmap(user_heatmap)
        st.pyplot(fig)

        # SECTION 4 — Busy users :-
        if selected_user == 'Overall':
            st.title('👥 Most Busy Users')
            x, new_df = helper.most_busy_users(df)
            fig, ax = plt.subplots()

            col1, col2 = st.columns(2)
            with col1:
                ax.bar(x.index, x.values, color='skyblue')
                plt.xticks(rotation=45)
                st.pyplot(fig)
            with col2:
                st.dataframe(new_df)  

        # SECTION 5 — Word analysis :-

        # Word Cloud :-
        st.title('☁️ WordCloud')
        df_wc = helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        st.pyplot(fig)

        # Most Common Words :-
        st.title('🔠 Most Common Words')
        most_common_df = helper.most_common_words(selected_user, df)
        fig, ax = plt.subplots()
        ax.barh(most_common_df[0], most_common_df[1], color='teal')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # SECTION 6 — Emoji analysis :-
        st.title('😀 Emoji Analysis')
        emoji_df = helper.emoji_helper(selected_user, df)

        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(emoji_df)  

        with col2:
            fig, ax = plt.subplots()
            wedges, texts, autotexts = ax.pie(
            emoji_df['Count'].head(),
            labels=emoji_df['Emoji'].head(),
            autopct="%0.2f%%",
            textprops={'fontsize': 12} 
            )

            # Apply emoji font only to labels (not numbers)
            for i, text in enumerate(texts):
                text.set_fontproperties(emoji_prop)

            st.pyplot(fig)

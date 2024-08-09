import streamlit as st
import pandas as pd
from streamlit_chat import message
from preprocessing import DataProcessor
from bot import FinancialChatbot

from warnings import filterwarnings
import os

filterwarnings('ignore')

st.title("Financial Advisor Chatbot")


@st.cache_resource
def get_data(alloc_file, financ_file):
    df_alloc = pd.read_csv(alloc_file)
    df_financial = pd.read_csv(financ_file)

    processor = DataProcessor(df_alloc, df_financial)

    # create folder if it does not exist
    if not os.path.exists(processor.save_path):
        os.makedirs(processor.save_path)
    processor.save_processed_data()

    return df_alloc, df_financial


# sidebar settings - api key and data upload
with st.sidebar:
    data_ready = False
    api_key = st.text_input("OpenAI API key", type="password")

    alloc_file = st.file_uploader("Upload target allocations file")
    financ_file = st.file_uploader("Upload financial data file")

    if alloc_file and financ_file:
        try:
            df_alloc, df_financial = get_data(alloc_file, financ_file)
            data_ready = True
            st.success('Data is ready to use!')
        except Exception as e:
            st.error('Something went wrong with data processing.')

# Initialize chatbot
if data_ready:
    bot = FinancialChatbot(df_alloc, df_financial, api_key=api_key)
    eval_metrics = []

    # initialize conversation history
    if 'history' not in st.session_state:
        st.session_state.history = []

    user_input = st.chat_input("You: ")

    if user_input:
        # Add user input to history
        st.session_state.history.append({"message": user_input, "is_user": True})

        # Generate response
        with st.spinner('Generating response...'):
            response_text, tokens_used, cost = bot.generate_response(user_input)
            # get evaluation score
            eval_score, _ = bot.evaluate_response_by_relevancy(
                user_input, response_text
            )
            eval_metrics.append(eval_score)
            with st.sidebar:
                eval_metrics_mean = (
                    round(sum(eval_metrics) / len(eval_metrics), 2)
                    if len(eval_metrics) > 0
                    else 0
                )
                st.info(
                    f"Last message relevancy score: {eval_score}\nAverage relevancy score: {eval_metrics_mean}"
                )

        # Add response to history
        st.session_state.history.append({"message": response_text, "is_user": False})

        # Clear the input field
        st.session_state.user_input = ''

        # Display the conversation history
        count_key = 0
        for chat in st.session_state.history:
            count_key += 1
            message(chat["message"], is_user=chat["is_user"], key=str(count_key))

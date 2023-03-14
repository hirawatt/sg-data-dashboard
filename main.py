import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime

# credentials
page_title = st.secrets['initialize']['page_title']
sidebar_title = st.secrets['initialize']['sidebar_title']
website = st.secrets['credits']['website']
name = st.secrets['credits']['name']
buymeacoffee = st.secrets['credits']['buymeacoffee']
api_key = st.secrets['api_key']
api_secret = st.secrets['api_secret']

# customers
customer1 = st.secrets['customers']['customer1']
customer2 = st.secrets['customers']['customer2']
customer3 = st.secrets['customers']['customer3']

# streamlit
st.set_page_config(
    '{}'.format(page_title),
    '⛽',
    layout='wide',
    initial_sidebar_state='expanded',
    menu_items={
        "Get Help": "https://softgun.in",
        "About": "Softgun Dashboard App",
    },
)

# footer & credits section
def footer():
    st.markdown('<div style="text-align: center">Made with ❤️ by <a href="{}">{}</a></div>'.format(website, name), unsafe_allow_html=True)
    with st.sidebar.expander("Credits", expanded=True):
        components.html(
            '{}'.format(buymeacoffee),
            height=80
        )

# USERS
ADMIN_USERS = {
    'customer1@gmail.com',
    'customer2@gmail.com',
    'customer3@gmail.com'
}

# hide col0 in streamlit
# CSS to inject contained in a string
hide_table_row_index = """
            <style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
            </style>
            """

# Inject CSS with Markdown
st.markdown(hide_table_row_index, unsafe_allow_html=True)

# functions
def display_content(email):
    col1, col2 = st.columns([5, 2])
    col1.title('⛽ ' + page_title )
    col2.subheader('Welcome, %s!' % email)
    st.sidebar.title(':cyclone: ' +  sidebar_title)
    date = st.sidebar.date_input("Select Date")
    st.sidebar.info("Data only available for present date")

    tab1, tab2, tab3 = st.tabs(["Daily Report", "Pump Details", "Pump-Wise Sales"])
    #data_file_1 = "./data/" + email.replace(".com", "") + "/daily-report.csv"
    data_file_1 = "./data/" + email.split("@")[0] + "/daily-report.csv"
    data_file_2 = "./data/" + email.split("@")[0] + "/pump-details.csv"
    data_file_3 = "./data/" + email.split("@")[0] + "/pump-wise-sales.csv"


    with tab1:
        st.header("{}".format(date.strftime('%d %B %Y')))
        df1 = pd.read_csv(data_file_1)
        st.table(df1)
    with tab2:
        st.header("{}".format(date.strftime('%d %B %Y')))
        df2 = pd.read_csv(data_file_2)
        st.table(df2)
    with tab3:
        st.header("{}".format(date.strftime('%d %B %Y')))
        df3 = pd.read_csv(data_file_3)
        st.table(df3)
    return None

def main() -> None:
    # Start Writing Code Here
    #footer()
    if st.experimental_user.email == customer1:
        display_content(email=customer1)
    elif st.experimental_user.email == customer2:
        display_content(email=customer2)
    elif st.experimental_user.email == customer3:
        display_content(email=customer3)
    elif st.experimental_user.email == 'test@localhost.com':
        display_content(email='test@localhost.com')
    else:
        st.header("Please contact us to get access!")
        st.subheader(st.experimental_user.email)
        st.write("Share this email for access")


if __name__ == '__main__':
    main()

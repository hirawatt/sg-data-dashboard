import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime
import boto3
from io import BytesIO
import zipfile

# credentials
page_title = st.secrets['initialize']['page_title']
sidebar_title = st.secrets['initialize']['sidebar_title']
website = st.secrets['credits']['website']
name = st.secrets['credits']['name']
buymeacoffee = st.secrets['credits']['buymeacoffee']
api_key = st.secrets['api_key']
api_secret = st.secrets['api_secret']

# customers
#customer1 = st.secrets['customers']['customer1']
#customer2 = st.secrets['customers']['customer2']
# R2 config
accountid = st.secrets['cloudflare']['accountid']
access_key_id = st.secrets['cloudflare']['access_key_id']
access_key_secret = st.secrets['cloudflare']['access_key_secret']

# R2 buckets setup
@st.cache_resource()
def database_r2():
    s3 = boto3.client('s3',
        endpoint_url = 'https://{}.r2.cloudflarestorage.com'.format(accountid),
        aws_access_key_id = '{}'.format(access_key_id),
        aws_secret_access_key = '{}'.format(access_key_secret)
    )
    return s3

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

# R2 data operations
bucketName = 'softgun'
#objectName = 'softgun-data-f1.zip'
objectName = 'master-data.csv'
fileName = 'datafile.zip'
file_list = []
last_modified = []

# download file
s3 = database_r2()
zipped_keys =  s3.list_objects_v2(Bucket=bucketName)
for key in zipped_keys['Contents']:
    file_list.append(key['Key'])
    last_modified.append(key['LastModified'])
st.write(file_list, last_modified)

for i in range(len(file_list)):
    obj = s3.get_object(Bucket=bucketName, Key=file_list[i])
    contents = obj['Body'].read()
    try:
        st.write(contents.decode("utf-8"))
    except:
        buffer = BytesIO(contents)
        z = zipfile.ZipFile(buffer)
        for filename in z.namelist():
            file_info = z.getinfo(filename)
            st.write(file_info)


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
    'test@localhost.com'
}
#for i in ADMIN_USERS:
#    print(i)

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
    # Form
    with st.form("my_form", clear_on_submit=True):
        st.write("Login with email")
        email = st.text_input("Enter email")
        # Every form must have a submit button.
        submitted = st.form_submit_button("Submit")
        st.success("Test Email : test@localhost.com")

    if submitted:
        if email in ADMIN_USERS:
            display_content(email=email)
        else:
            st.error("Access Denied")
            st.header("Please contact us to get access!")
    else:
        st.info("Enter email to continue")

if __name__ == '__main__':
    main()

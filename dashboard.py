import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime
import boto3
from io import BytesIO, StringIO
import zipfile
from supabase import create_client, Client
import numpy as np

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
# Supabase config
supabase_url = st.secrets['supabase']['supabase_url']
supabase_key = st.secrets['supabase']['supabase_key']

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

# download files list from s3
s3 = database_r2()
zipped_keys =  s3.list_objects_v2(Bucket=bucketName)
for key in zipped_keys['Contents']:
    file_list.append(key['Key'])

# get data for zip files stored in s3 buckets
def get_data(filename, userid):
    obj = s3.get_object(Bucket=bucketName, Key=filename)
    contents = obj['Body'].read()
    buffer = BytesIO(contents)
    z = zipfile.ZipFile(buffer)
    st.download_button(
        label="Download all files",
        data=buffer,
        file_name='softgun-{}.zip'.format(userid),
        mime='application/zip',
        use_container_width=True
    )
    return z

# footer & credits section
def footer():
    st.markdown('<div style="text-align: center">Made with ❤️ by <a href="{}">{}</a></div>'.format(website, name), unsafe_allow_html=True)
    with st.sidebar.expander("Credits", expanded=True):
        components.html(
            '{}'.format(buymeacoffee),
            height=80
        )

# hide col0 in streamlit
# CSS to inject contained in a string
hide_table_row_index = """
            <style>
            thead tr th:first-child {display:none}
            tbody th {display:none}
            </style>
            """

# Inject CSS with Markdown
#st.markdown(hide_table_row_index, unsafe_allow_html=True)

# functions
@st.cache_resource
def init_connection():
    return create_client(supabase_url, supabase_key)

supabase = init_connection()

@st.cache_data(ttl=60000)
def run_query():
    return supabase.table("owner_creds").select("*").execute()

@st.cache_data()
def insert_query(filename, pin):
    return supabase.table("owner_creds").update({"pin": pin, "pin_set": True}).eq("filename", filename).execute()

def zip_info_to_csv(z, files):
    strdata = []
    for f in files:
        file_date_time = f.date_time # file last modified datetime
        #file_name = f.filename
        # Use - Decode in csv format
        data = z.read(f).decode("utf-8")
        str_data = StringIO(data)
        str_data.seek(0)
        strdata.append(str_data)

    return strdata

def logout():
    del st.session_state.user
    del st.session_state.userid
    del st.session_state.passwd

def tab_display(date, data_file):
    st.header("{}".format(date.strftime('%d %B %Y')))
    df = pd.read_csv(data_file)
    newdf1 = df.dropna(thresh=2)
    newdf2 = newdf1.dropna(axis="columns")
    newdf = newdf2.fillna(0)
    return newdf

def display_content(userid):
    col1, col2 = st.columns([5, 2])
    col2.button("Logout", on_click=logout, use_container_width=True)
    col1.header('⛽ ' + page_title )
    col2.subheader('{}'.format(userid))
    st.sidebar.title(':cyclone: ' +  sidebar_title)
    date = st.sidebar.date_input("Select Date")
    st.sidebar.info("Data only available for present date")

    tab1, tab2, tab3, tab4 = st.tabs(["Summary", "Meter Details", "Tank Details", "Memo Report"])
    # zipinfo file - z
    file_str = "softgun-{}".format(userid)
    index = [idx for idx, s in enumerate(file_list) if file_str in s][0]
    z = get_data(filename=file_list[index], userid=userid)
    file_info = z.infolist()
    # skip 1st element of list which is not a file
    f1 = file_info[3] # sr_sum.csv
    f2 = file_info[1] # sr_m.csv
    f3 = file_info[4] # sr_t.csv
    f4 = file_info[2] # sr_mr.csv
    files = [f1, f2, f3, f4]
    data_list = zip_info_to_csv(z, files)
    
    # TD - add filename logic based on login credentials from supabase
    # TD - use st.dataframe to freeze 1st column in summary
    with tab1:
        df = tab_display(date, data_list[0])
        st.dataframe(df, use_container_width=True)
    with tab2:
        df = tab_display(date, data_list[1])
        st.dataframe(df, use_container_width=True)
    with tab3:
        df = tab_display(date, data_list[2])
        st.dataframe(df, use_container_width=True)
    with tab4:
        df = tab_display(date, data_list[3])
        st.dataframe(df, use_container_width=True)
    return None

def new_user_setup(rows, filename, index, phone_no, form1, form2):
    # TD - setup Phone No. Verification with OTP
    with form2.form("new_user_setup", clear_on_submit=True):
        form1.empty()
        st.success("New User Setup")
        st.info("Verify you phone no using OTP")
        st.session_state.phone = st.text_input("Enter Mobile Number")
        st.text_input("Enter password", type="password", key="password")
        st.form_submit_button("Set Password")
    # TD - add to database - error - st.session_state.submit_pass
    if st.session_state["FormSubmitter:new_user_setup-Set Password"]:
        if (st.session_state.phone == phone_no):
            response = insert_query(filename, st.session_state.password)
            st.write(response)
            st.session_state.user = rows.data[index]["user_id"]
        else:
            st.warning("Enter same password")

def main() -> None:
    #footer()
    form1 = st.empty()
    form2 = st.empty()
    if 'form_submit' not in st.session_state:
        st.session_state.form_submit = False

    if (st.session_state.get('user')) is None:
        # Get data from supabase
        rows = run_query()
        userid_list = []
        for i in range(len(rows.data)):
            # TD - set userid as phone_no
            userid_list.append(rows.data[i]['user_id'])

        # login form
        with form1.form("login_form", clear_on_submit=True):
            st.write("Login Form")
            st.session_state.userid = st.text_input("Userid")
            st.session_state.passwd = st.text_input("Password", type="password")
            st.session_state.form_submit = st.form_submit_button("Enter")
        
        # on userid submit
        if st.session_state.form_submit:
            # TD - setup phone_no & pin login setup
            # userid correct
            if (st.session_state.userid in userid_list):
                index = userid_list.index(st.session_state.userid)
                pin = rows.data[index]["pin"]
                pin_set = rows.data[index]["pin_set"]
                filename = rows.data[index]["filename"]
                phone_no = rows.data[index]["phone_no"]
                if pin_set:
                    # old user dashboard success
                    if (st.session_state.userid in userid_list) and (st.session_state.passwd == pin):
                        form1.empty()
                        st.session_state.user = rows.data[index]["user_id"]
                        display_content(userid=st.session_state.userid)
                    elif (st.session_state.passwd != pin):
                        st.warning("Incorrect Password")
                # new user setup
                elif not pin_set:
                    new_user_setup(rows, filename, index, phone_no, form1, form2)
                else:
                    st.write("Encountered Edge Case")

            # userid not correct
            else:
                col1, col2 = st.columns(2)
                col1.error("Access Denied")
                col2.header("Please Contact to get access!")
        # userid not submitted
        else:
            col1, col2 = st.columns(2)
            col1.info("Demo Userid")
            col2.code("SG001")
            col1.info("Demo Password")
            col2.code("123456")
    else:
        form1.empty()
        display_content(userid=st.session_state.userid)

if __name__ == '__main__':
    main()
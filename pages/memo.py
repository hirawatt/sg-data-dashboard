import streamlit as st
import pandas as pd
from datetime import datetime
from supabase import create_client, Client

# Supabase config
supabase_url = st.secrets['supabase']['supabase_url']
supabase_key = st.secrets['supabase']['supabase_key']

st.info("Login from Dashboard")
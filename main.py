import json
from scripts import streamlit_funcs as st
from scripts import sql_scripts as sql

# Connect Database
cursor, mydb = sql.connect_database()

st.set_page_config()

st.set_page_header()

option_selected = st.set_option_menu()

if option_selected == 'Home':
    st.home(cursor)

if option_selected == 'Exploration':
    st.explore(cursor)

if option_selected == 'Insights':
    st.insights(cursor)
    
if option_selected == 'About':
    st.about()
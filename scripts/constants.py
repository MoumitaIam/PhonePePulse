from PIL import Image
import pandas as pd

#Streamlit properties
page_icon = Image.open('assets/phonepe.png')
page_title = 'PhonePe Pulse | PhonePe Pulse'
page_header = ['PhonePe Pulse','THE BEAT OF PROGRESS']
nav_menu_option = ["Home", "Exploration", "Insights", "About"]
nav_menu_icons = ["house-fill", "tools", "bar-chart-fill", "person-fill"]

quarter_select_box = ['Q1 (Jan - Mar)', 
                    'Q2 (Apr - Jun)',
                    'Q3 (Jul - Sep)',
                    'Q4 (Oct - Dec)']

#specifying the geojson URL
geojson_url = 'https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson'

#Getting the statenames as per the geojson file
geojson_state_df = pd.read_csv('data/csv_data/Statenames.csv')
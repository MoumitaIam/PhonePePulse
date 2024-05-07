# Import necessary libraries
import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
import plotly.express as px
import mysql.connector as sql

#Local modules
import scripts.constants as c
import scripts.sql_scripts as sql
import scripts.essential_funcs as e

# Streamlit page configuration
def set_page_config():
    st.set_page_config(
        page_title=c.page_title,
        page_icon=c.page_icon,
        layout="wide",
    )

# Setting page header
def set_page_header():
    st.markdown(
        f'<center><span style="color:white; font-size:30px">{c.page_header[0]}</span></center>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<center><span style="color:purple;font-size:24px">{c.page_header[1]}</span></center>',
        unsafe_allow_html=True,
    )

# Option nav menu
def set_option_menu():
    selected = option_menu(
        None,
        options=["Home", "Exploration", "Insights", "About"],
        # options =["",  "Analysis", "About"],
        icons=["house-fill", "tools", "bar-chart-fill", "person-fill"],
        menu_icon="cast",  # optional
        default_index=0,  # optional
        orientation="horizontal",
        styles={
            "container": {
                "padding": "0!important",
                "background-color": "#391c59",
                "width": "100%",
            },
            "icon": {"color": "yellow", "font-size": "20px"},
            "nav-link": {
                'font-face':'bold',
                "font-size": "20px",
                "text-align": "center",
                "margin": "0px",
                "--hover-color": "magenta",
            },
            "nav-link-selected": {"background-color": "#c25857"},
        },
    )
    return selected

# -------------------------------------Home option--------------------------------
def home(cursor):
    
    col1,col2,col3 = st.columns(3)
    with col1:
        
        #Select type
        type_options = ["Transactions", "Users","Insurance"]
        data_type = st.selectbox("Choose Type:[Transactions,User,Insurance]", type_options)

    with col2:
        # Getting year list from a table
        if data_type == type_options[2]:
            year_list = sql.get_year_list("agg_insurance", cursor)
        else:
            year_list = sql.get_year_list("agg_transaction", cursor)

        #Select year and quarter    
        year = st.selectbox("Choose year", year_list,index = len(year_list)-1)
    
    with col3:
        # Getting year list from a table
        if data_type == type_options[2]:
            quarter_list = sql.get_quarter_list("agg_insurance", cursor,year)
        else:
            quarter_list = sql.get_quarter_list("agg_transaction", cursor,year)
        
        quarter = st.selectbox("Choose quarter", quarter_list,index = len(quarter_list)-1)
        quarter = int(quarter[1])
    
    st.header(f'Showing data for Q{quarter} {year}')

    #Dividing map and data to separate columns
    map_col, data_col = st.columns([5, 2])
    with map_col:
        if data_type == "Transactions":
            transaction_map(cursor, year, quarter)#Transaction data map
        elif data_type == "Users" :
            user_map(cursor, year, quarter)#user data map
        else:
            insurance_map(cursor,year,quarter)
    with data_col:
        if data_type == "Transactions":
            transaction_data(cursor,year,quarter)#Show transaction 
        elif data_type == "Users" :
            user_data(cursor,year,quarter)#Show user data
        else:
            insurance_data(cursor,year,quarter)#Sow insurance data

# Plot the map
def create_map_plot(df, color,hover_data,scale,hovertemplate):
    show_legend = st.checkbox("Show_legend")

    fig = px.choropleth_mapbox(
        df,
        geojson= c.geojson_url,
        featureidkey="properties.ST_NM",
        locations="state",
        color=color,
        color_continuous_scale= scale,
        hover_name="state",
        mapbox_style='carto-positron',
        center={"lat": 24, "lon": 79},
        color_continuous_midpoint=0,
        zoom=3.6,
        width=800, 
        height=800,
        hover_data=hover_data,
    )

    fig.update_geos(fitbounds="locations", visible=True)

    if not show_legend:
        fig.update_coloraxes(showscale=False)

    fig.update_layout(coloraxis_colorbar=dict(showticklabels=True),
                    hoverlabel_font={'size': 15,'family': 'comic sans ms'},
                    hoverlabel={
                        'bgcolor':'#2c1942',
                        'bordercolor':'red',
                        # 'xanchor':'center',
                        # 'yanchor':'bottom'
                        
                    }
                    )
    fig.update_traces(hovertemplate = hovertemplate)
    
    st.plotly_chart(fig, use_container_width=True)

# Function for map visualize transactions
def transaction_map(cursor, year, quarter):
    query = f"select state,sum(Transaction_amount) as Total_amount,sum(Transaction_count) as Total_count from map_transaction where year = {year} and quarter = {quarter} group by state order by state"

    data = sql.execute_select(query, cursor)
    df = pd.DataFrame(data.fetchall(), columns=data.column_names)

    df["state"] = c.geojson_state_df

    df['average'] = df['Total_amount'] / df['Total_count']
    df['average'] = '₹' + df['average'].apply(e.simplify_number)
    
    df['count'] = df['Total_count'].apply(e.simplify_number)
    
    df['Total_amount'] = '₹' + df['Total_amount'].apply(e.simplify_number, args=[True])
    
    hover_data = ['state','count','Total_amount','average']
    scale = 'burgyl'

    hovertemplate='%{hovertext}<br><br>All transactions<br>%{customdata[1]}<br><br>Total payment value<br>%{customdata[2]}<br><br>Avg. payment value<br>%{customdata[3]}'

    
    create_map_plot(df, "Total_count",hover_data,scale,hovertemplate)

# Function for map visualize transactions
def user_map(cursor, year, quarter):
    query = f"select state, sum(Registered_User) as Total_users,sum(app_opens) as app from map_user where year = {year} and quarter = {quarter} group by state order by state"

    data = sql.execute_select(query, cursor)
    df = pd.DataFrame(data.fetchall(), columns=data.column_names)

    df["state"] = c.geojson_state_df
    
    df['count'] = df['Total_users'].apply(e.simplify_number)
    
    df['app'] = df['app'].apply(e.simplify_number)
    
    hover_data = ['state','count','app']
    hovertemplate='%{hovertext}<br><br>Registered Users<br>%{customdata[1]}<br><br>App Opens<br>%{customdata[2]}'
    scale = 'blues'
    
    create_map_plot(df, "Total_users",hover_data,scale,hovertemplate)

#Function to show insurance data
def insurance_map(cursor, year,quarter):
    query = f"select state, sum(Policy_amount) as Total_amount,sum(Policy_count) as Total_count from map_insurance where year = {year} and quarter = {quarter} group by state order by state"

    data = sql.execute_select(query, cursor)
    df = pd.DataFrame(data.fetchall(), columns=data.column_names)

    df["state"] = c.geojson_state_df
    
    df['average'] = df['Total_amount'] / df['Total_count']
    df['average'] = '₹' + df['average'].apply(e.simplify_number)
    
    df['count'] = df['Total_count'].apply(e.simplify_number)
    
    df['Total_amount'] = '₹' + df['Total_amount'].apply(e.simplify_number, args=[True])
    
    hover_data = ['state','count','Total_amount','average']
    hovertemplate='%{hovertext}<br><br>Insurance Policies(Nos.)<br>%{customdata[1]}<br><br>Total premium value<br>%{customdata[2]}<br><br>Avg. premium value<br>%{customdata[3]}'
    scale = 'greens'
    
    create_map_plot(df, "Total_count",hover_data,scale,hovertemplate)

#Function to show transaction data
def transaction_data(cursor,year,quarter):

    with st.container(height = 750):
        #Total transaction data
        query = f"select year, quarter,sum(Transaction_count) as Total_Transactions,sum(Transaction_amount) as Total_amount,AVG(Transaction_amount) as Average_amount from agg_transaction where year = {year} and quarter = {quarter} group by year,quarter"
        trans_df = e.extract_convert_to_dataframe(query, cursor)

        total_transactions = trans_df["Total_Transactions"][0]
        total_amount = trans_df["Total_amount"][0]
        average_amount = total_amount / float(total_transactions)

        st.header(":blue[Transactions]")
        st.write("All PhonePe transactions (UPI + Cards + Wallets)")
        st.markdown(
            f"<h3 style = 'color:#60b4ff;'>{e.simplify_number(total_transactions)}</h3>", unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)
        with col1:
            st.write("Total payment value")
            st.markdown(
                f"<h3 style = 'color:#60b4ff;'>₹{e.simplify_number(total_amount,True)}</h3>", unsafe_allow_html=True
            )

        with col2:
            st.write("Avg. transaction value")
            st.markdown(
                f"<h3 style = 'color:#60b4ff;'>₹{e.simplify_number(average_amount)}</h3>", unsafe_allow_html=True
            )
            
        st.divider()
        
        #Type wise data
        query = f'select year, quarter, Transaction_type as type, sum(Transaction_count) as total_transaction from agg_transaction where year = {year} and quarter = {quarter} group by year,quarter,Transaction_type'
        type_df = e.extract_convert_to_dataframe(query, cursor)
        
        st.header('Categories')
        for i,row in type_df.iterrows():
            type_name = row['type']
            type_amount = row['total_transaction']
            
            col1,col2 = st.columns([3,1])
            col1.write(type_name)
            col2.write(f':blue[{e.simplify_number(type_amount)}]')
                
        st.divider()
        
        col1,col2,col3 = st.columns(3)
        
        with col1:
            state = st.button('States')
        with col2:
            district = st.button('Districts')
        with col3:
            pin = st.button('Postal Codes')
        
        state = True
        if(district):
            state =pin= False
        elif(pin):
            state =district= False
        elif(state):
            district =pin= False  
        
        if state:
            st.header('Top 10 States')
            query = f'select state, sum(Transaction_count) as total_transaction from agg_transaction where year = {year} and quarter = {quarter} group by state order by total_transaction desc Limit 10'
            state_df = e.extract_convert_to_dataframe(query,cursor)
            
            for i,row in state_df.iterrows():
                show_state_data(i+1,
                                row['state'].title(),
                                e.simplify_number(row['total_transaction'],True,True)
                                )

        if district:
            st.header('Top 10 Districts')
            query = f'select district, sum(Transaction_count) as total_transaction from map_transaction where year = {year} and quarter = {quarter} group by district order by total_transaction desc Limit 10'
            state_df =e. extract_convert_to_dataframe(query,cursor)
            
            for i,row in state_df.iterrows():
                show_state_data(i+1,
                                row['district'].replace(' district','').title(),
                                e.simplify_number(row['total_transaction'],True,True)
                                )
        if pin:
            st.header('Top 10 Pincodes')
            query = f'select pincode, sum(Transaction_count) as total_transaction from top_transaction where year = {year} and quarter = {quarter} group by pincode order by total_transaction desc Limit 10'
            state_df = e.extract_convert_to_dataframe(query,cursor)
            
            for i,row in state_df.iterrows():
                show_state_data(i+1,
                                int(row['pincode']),
                                e.simplify_number(row['total_transaction'],True,True)
                                )
            
#Function to show user data
def user_data(cursor,year,quarter):
    with st.container(height = 750,border=True):
        
        #Total transaction data
        query = f"select year, quarter,sum(Registered_User) as Total_users,sum(App_opens) as app from map_user where year = {year} and quarter = {quarter} group by year,quarter"
        user_df = e.extract_convert_to_dataframe(query, cursor)

        total_users = e.simplify_number(user_df["Total_users"][0])
        total_app_open = user_df["app"][0]
        if total_app_open == 0:
            total_app_open = 'Unavailable'
        else:
            total_app_open = e.simplify_number(total_app_open)

        st.header(":blue[Users]")
        st.write(f"Registered PhonePe users till Q{quarter} {year}")
        st.markdown(
            f"<h3 style = 'color:#60b4ff;'>{total_users}</h3>", unsafe_allow_html=True
        )

        st.write(f"PhonePe app opens in Q{quarter} {year}")
        st.markdown(
            f"<h3 style = 'color:#60b4ff;'>{total_app_open}</h3>", unsafe_allow_html=True
        )
            
        st.divider()
        
        col1,col2,col3 = st.columns(3)
        
        with col1:
            state = st.button('States')
        with col2:
            district = st.button('Districts')
        with col3:
            pin = st.button('Postal Codes')
        
        state = True
        if(district):
            state =pin= False
        elif(pin):
            state =district= False
        elif(state):
            district =pin= False  
        
        if state:
            st.header('Top 10 States')
            query = f'select state, sum(Registered_User) as total_user from map_user where year = {year} and quarter = {quarter} group by state order by total_user desc Limit 10'
            state_df = e.extract_convert_to_dataframe(query,cursor)
            
            for i,row in state_df.iterrows():
                show_state_data(i+1,
                                row['state'].title(),
                                e.simplify_number(row['total_user'],True,True)
                                )
        if district:
            st.header('Top 10 Districts')
            query = f'select district, sum(Registered_User) as total_user from map_user where year = {year} and quarter = {quarter} group by district order by total_user desc Limit 10'
            state_df = e.extract_convert_to_dataframe(query,cursor)
            
            for i,row in state_df.iterrows():
                show_state_data(i+1,
                                row['district'].replace(' district','').title(),
                                e.simplify_number(row['total_user'],True,True)
                                )
        if pin:
            st.header('Top 10 Pincodes')
            query = f'select pincode, sum(Registered_User) as total_user from top_user where year = {year} and quarter = {quarter} group by pincode order by total_user desc Limit 10'
            state_df = e.extract_convert_to_dataframe(query,cursor)
            
            for i,row in state_df.iterrows():
                show_state_data(i+1,
                                int(row['pincode']),
                                e.simplify_number(row['total_user'],True,True)
                                )

#Function to show insurance data
def insurance_data(cursor, year,quarter):
    with st.container(height = 750):
        #Total insurance data
        query = f"select year, quarter,sum(Policy_count) as Total_insurance,sum(Policy_amount) as Total_amount from agg_insurance  where year = {year} and quarter = {quarter} group by year,quarter"
        trans_df = e.extract_convert_to_dataframe(query, cursor)

        total_insurances = trans_df["Total_insurance"][0]
        total_amount = trans_df["Total_amount"][0]
        average_amount = total_amount / float(total_insurances)

        st.header(":blue[Insurance]")
        st.write("All India Insurance Policies Purchased (Nos.)")
        st.markdown(
            f"<h3 style = 'color:#60b4ff;'>{e.simplify_number(total_insurances)}</h3>", unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)
        with col1:
            st.write("Total premium value")
            st.markdown(
                f"<h3 style = 'color:#60b4ff;'>₹{e.simplify_number(total_amount,True)}</h3>", unsafe_allow_html=True
            )

        with col2:
            st.write("Avg. premium value")
            st.markdown(
                f"<h3  style = 'color:#60b4ff;'>₹{e.simplify_number(average_amount)}</h3>", unsafe_allow_html=True
            )
            
        st.divider()
                
        col1,col2,col3 = st.columns(3)
        
        with col1:
            state = st.button('States')
        with col2:
            district = st.button('Districts')
        with col3:
            pin = st.button('Postal Codes')
        
        state = True
        if(district):
            state =pin= False
        elif(pin):
            state =district= False
        elif(state):
            district =pin= False  
        
        if state:
            st.header('Top 10 States')
            query = f'select state, sum(Policy_count) as total_policies from agg_insurance where year = {year} and quarter = {quarter} group by state order by total_policies desc Limit 10'
            state_df = e.extract_convert_to_dataframe(query,cursor)
            
            for i,row in state_df.iterrows():
                show_state_data(i+1,
                                row['state'].title(),
                                e.simplify_number(row['total_policies'],True,True)
                                )

        if district:
            st.header('Top 10 Districts')
            query = f'select district, sum(Policy_count) as total_policies from map_insurance where year = {year} and quarter = {quarter} group by district order by total_policies desc Limit 10'
            state_df =e. extract_convert_to_dataframe(query,cursor)
            
            for i,row in state_df.iterrows():
                show_state_data(i+1,
                                row['district'].replace(' district','').title(),
                                e.simplify_number(row['total_policies'],True,True)
                                )
        if pin:
            st.header('Top 10 Pincodes')
            query = f'select pincode, sum(Policy_count) as total_policies from top_insurance where year = {year} and quarter = {quarter} group by pincode order by total_policies desc Limit 10'
            state_df = e.extract_convert_to_dataframe(query,cursor)
            
            for i,row in state_df.iterrows():
                show_state_data(i+1,
                                int(row['pincode']),
                                e.simplify_number(row['total_policies'],True,True)
                                )

#Function to simplify showing data of state,district,pincode in home page
def show_state_data(index,title,value):
    c1,c2, = st.columns([5,1])
    c1.write(f'{index}. {title}')
    c2.write(f':blue[{value}]')

# -------------------------------------Home option--------------------------------

# -------------------------------------Explore option--------------------------------
def explore(cursor):
    
    data_category = st.selectbox('Choose Category[Insurance,Transaction,User]',
                                options = ['INSURANCE DATA',
                                        'TRANSACTION DATA',
                                        'USER DATA'],
                                index = 0)
    
    category = {
        'INSURANCE DATA':ins,
        'TRANSACTION DATA':trans,
        'USER DATA':user
    }
    
    category.get(data_category)(cursor)

#Insurance analysis
def ins(cursor):
    st.header(':violet[INSURANCE ANALYSIS]	:heavy_dollar_sign:')
    st.divider()
    
    with st.expander('FILTERS',expanded=True):
        search_type = st.radio('SEARCH BY:',
                    options=['STATE','DISTRICT', 
                            'OVERALL']
                    ,horizontal=True)
        view = st.toggle('Switch to Tabular view')
        
    if search_type == 'STATE':
        query = 'select year as Year, quarter as Quarter, sum(Policy_amount) as Total_amount,sum(policy_count) as Total_policies from agg_insurance group by  Year,Quarter'
        data_df = e.extract_convert_to_dataframe(query,cursor)
        
        col1,col2 = st.columns(2)
        with col1:
            year = make_selectbox(data_df,'Select year:','Year')
        with col2:
            quarter = make_selectbox(data_df,'Select quarter:','Quarter')
        
        if view:
            col1,col2 = st.columns(2)
            with col1:
                if year:
                    query = f"select state as State, sum(Policy_amount) as Total_amount, sum(policy_count) as Total_policies from agg_insurance where year = {year} group by State, Year"
                    tab_view(query,f'Data for {year}',cursor)
            with col2:
                if year and quarter:
                    query = f"select state as State,sum(Policy_amount) as Total_amount, sum(policy_count) as Total_policies from agg_insurance where year = {year} and quarter = {quarter} group by State, Year,Quarter"
                    tab_view(query,f'Data for Q{quarter}-{year}',cursor)
        else:
            col1,col2 = st.columns(2)
            with col1:
                if year:
                    query = f"select state as State, year as Year, quarter as Quarter,sum(Policy_amount) as Total_amount, sum(policy_count) as Total_policies from agg_insurance where year = {year} group by State, Year,Quarter"
                    formatted_df = e.extract_convert_to_dataframe(query,cursor)
                    
                    tab1,tab2 = st.tabs(['Total Policy', 'Total Policy Amount'])
                    with tab1:
                        plot_bar(formatted_df,'State','Total_policies',f'Total policy for {year}','Quarter')
                    with tab2:
                        plot_bar(formatted_df,'State','Total_amount',f'Total amount for {year}','Quarter')

            with col2:
                if year and quarter:
                    query = f"select state as State, year as Year, quarter as Quarter,sum(Policy_amount) as Total_amount, sum(policy_count) as Total_policies from agg_insurance where year = {year} and quarter = {quarter} group by State, Year,Quarter"
                    formatted_df = e.extract_convert_to_dataframe(query,cursor)
                    
                    tab1,tab2 = st.tabs(['Total Policy ', 'Total Policy Amount'])
                    
                    with tab1:
                        plot_bar(formatted_df,'State','Total_policies',f'Total policy for Q{quarter}-{year}')
                    with tab2:
                        plot_bar(formatted_df,'State','Total_amount',f'Total amount for Q{quarter}-{year}')

    if search_type == 'DISTRICT':
        query = 'select district as District,state as State,year as Year, sum(Policy_amount) as Total_amount,sum(policy_count) as Total_policies from map_insurance group by  District,State,Year'
        data_df = e.extract_convert_to_dataframe(query,cursor)
        
        col1,col2 = st.columns(2)
        with col1:
            state = make_selectbox(data_df,'Select state:','State')
        with col2:
            year = make_selectbox(data_df,'Select year:','Year')

        if view:
            col1,col2 = st.columns(2)
            with col1:
                if state:
                    query = f"select district as district, sum(Policy_amount) as Total_amount, sum(policy_count) as Total_policies from map_insurance where state = '{state}' group by District"
                    tab_view(query,f'Data for {state}',cursor)
            with col2:
                if state and year:
                    query = f"select district as district, sum(Policy_amount) as Total_amount, sum(policy_count) as Total_policies from map_insurance where state = '{state}' and year = {year} group by District"
                    tab_view(query,f'Data for {state}-{year}',cursor)
        else:
            col1,col2 = st.columns(2)
            with col1:
                if state:
                    query = f"select quarter as Quarter,district as District, sum(Policy_amount) as Total_amount, sum(policy_count) as Total_policies from map_insurance where state = '{state}' group by District,Quarter"
                    formatted_df = e.extract_convert_to_dataframe(query,cursor)
                    
                    tab1,tab2 = st.tabs(['Total Policy', 'Total Policy Amount'])
                    with tab1:
                        plot_bar(formatted_df,'District','Total_policies',f'Total policy for {state}','Quarter')
                    with tab2:
                        plot_bar(formatted_df,'District','Total_amount',f'Total amount for {state}')
            
            with col2:
                if state and year:
                    query = f"select district as District, year as Year, sum(Policy_amount) as Total_amount, sum(policy_count) as Total_policies from map_insurance where state = '{state}' and year = {year} group by District"
                    formatted_df = e.extract_convert_to_dataframe(query,cursor)
                    
                    tab1,tab2 = st.tabs(['Total Policy', 'Total Policy Amount'])
                    with tab1:
                        plot_bar(formatted_df,'District','Total_policies',f'Total policy for {state} in {year}')
                    with tab2:
                        plot_bar(formatted_df,'District','Total_amount',f'Total amount for {state} in {year}')
                    
    if search_type == 'OVERALL':
        #Overall Analysis
        st.header(':violet[OVERALL ANALYSIS]')
        query = 'select year,sum(Policy_amount) Total_amount,sum(policy_count) as Total_policies from agg_insurance group by  year'
        data_df = e.extract_convert_to_dataframe(query,cursor)
        col1,col2 = st.columns(2)
        
        with col1:
            tab1,tab2 = st.tabs(['Total Policy', 'Total Policy Amount'])
            
            with tab1:
                fig = px.pie(data_df,values='Total_policies',names = 'year',
                            title='TOTAL POLICIES (2020-2023)')

                st.plotly_chart(fig)
            with tab2:
                fig = px.bar(data_df,x = 'year',y = 'Total_amount',
                            color= 'year',
                            title='YEAR WISE POLICY AMOUNT',
                            labels={'Total_amount':'Total amount','year':'Year'})
                
                st.plotly_chart(fig)
                
        with col2:
            num_formatted_df = {'Amount':[]}
            for row in data_df['Total_amount'] :
                num_formatted_df['Amount'].append(e.simplify_number(row,True))
            
            num_formatted_df = pd.DataFrame(num_formatted_df)
            data_df['Total_amount'] = num_formatted_df['Amount']
            
            st.table(data_df)
            st.info(
                """                
                -TOTAL POLICIES:\n
                We can see how much percentage of total policies
                has been issued per year\n
                """)
            st.info(
                """
                -TOTAL POLICY AMOUNT\n
                The bar graph shows the amount of premium issued per year.\n
                """)
            st.info(
                """
                -OBSERVATION\n
                We can clearly see that every year the policy count and the\n
                premium amount has been increasing
                """)

#Transaction analysis
def trans(cursor):
    st.header(':violet[TRANSACTION ANALYSIS]	:dollar:')
    st.divider()
    
    with st.expander('FILTERS',expanded=True):
        search_type = st.radio('SEARCH BY:',
                    options=['TYPE','STATE','DISTRICT', 
                            'OVERALL']
                    ,horizontal=True)
        view = st.toggle('Switch to Tabular view')
        
    if search_type == 'TYPE':
        query = 'select state as State,transaction_type as type,year as Year, sum(transaction_amount) as Total_amount,sum(transaction_count) as Total_count from agg_transaction group by state,type,Year,Quarter'
        data_df = e.extract_convert_to_dataframe(query,cursor)
        
        col1,col2,col3 = st.columns(3)
        with col1:
            type = make_selectbox(data_df,'Select type:','type')
        with col2:
            year = make_selectbox(data_df,'Select year:','Year')
        with col3:
            state = make_selectbox(data_df,'Select state:','State')
        
        if view:
            col1,col2,col3 = st.columns(3)
            with col1:
                if type:
                    query = f" SELECT DISTINCT State,Quarter,Year,Transaction_type,Transaction_count,Transaction_amount FROM agg_transaction WHERE Transaction_type = 'Recharge & bill payments' ORDER BY State,Quarter,Year"
                    tab_view(query,f'Data for {type}',cursor)
            with col2:
                if type and year:
                    query = f" SELECT CONCAT('Q', quarter, ' ', year) AS Quarter_Year,SUM(transaction_count) AS Total_count,sum(transaction_amount) as Total_amount FROM agg_transaction WHERE transaction_type = '{type}' AND year = {year} GROUP BY year, quarter ORDER BY year, quarter;"
                    tab_view(query,f'Data for {type}-{year}',cursor)
            with col3:
                if type and year and state:
                    query = f" SELECT CONCAT('Q', quarter, ' ', year) AS Quarter_Year,SUM(transaction_count) AS Total_count,sum(transaction_amount) as Total_amount FROM agg_transaction WHERE transaction_type = '{type}' AND year = {year} and state = '{state}' GROUP BY year, quarter ORDER BY year, quarter;"
                    tab_view(query,f'Data for {type}-{year} for {state}',cursor)
        else:
            col1,col2,col3 = st.columns(3)
            with col1:
                if type:
                    query = f" SELECT DISTINCT State,Quarter,Year,Transaction_type,Transaction_count,Transaction_amount FROM agg_transaction WHERE Transaction_type = 'Recharge & bill payments' ORDER BY State,Quarter,Year"
                    formatted_df = e.extract_convert_to_dataframe(query,cursor)
                    
                    tab1,tab2 = st.tabs(['Total transaction count', 'Total transaction amount'])
                    with tab1:
                        plot_bar(formatted_df,'State','Transaction_count',f'Total count for {type}','Quarter')
                    with tab2:
                        plot_bar(formatted_df,'State','Transaction_amount',f'Total amount for {type}','Quarter')

            with col2:
                if type and year:
                    query = f" SELECT CONCAT('Q', quarter, ' ', year) AS Quarter_Year,SUM(transaction_count) AS Total_count,sum(transaction_amount) as Total_amount FROM agg_transaction WHERE transaction_type = '{type}' AND year = {year} GROUP BY year, quarter ORDER BY year, quarter;"
                    formatted_df = e.extract_convert_to_dataframe(query,cursor)
                    
                    tab1,tab2 = st.tabs(['Total transaction count', 'Total transaction amount'])
                    
                    with tab1:
                        plot_bar(formatted_df,'Quarter_Year','Total_count',f'Total count for {type} {year}')
                    with tab2:
                        plot_bar(formatted_df,'Quarter_Year','Total_amount',f'Total amount for {type} {year}')
            with col3:
                if type and year and state:
                    query = f" SELECT CONCAT('Q', quarter, ' ', year) AS Quarter_Year,SUM(transaction_count) AS Total_count,sum(transaction_amount) as Total_amount FROM agg_transaction WHERE transaction_type = '{type}' AND year = {year} and state = '{state}' GROUP BY year, quarter ORDER BY year, quarter;"
                    formatted_df = e.extract_convert_to_dataframe(query,cursor)
                    
                    tab1,tab2 = st.tabs(['Total transaction count', 'Total transaction amount'])
                    
                    with tab1:
                        plot_bar(formatted_df,'Quarter_Year','Total_count',f'Total count for {type} {year} for {state}')
                    with tab2:
                        plot_bar(formatted_df,'Quarter_Year','Total_amount',f'Total amount for {type} {year} for {state}')

    if search_type == 'STATE':
        query = 'select year as Year, quarter as Quarter, sum(Transaction_amount) as Total_amount,sum(transaction_count) as Total_count from agg_transaction group by  Year,Quarter'
        data_df = e.extract_convert_to_dataframe(query,cursor)
        
        col1,col2 = st.columns(2)
        with col1:
            year = make_selectbox(data_df,'Select year:','Year')
        with col2:
            quarter = make_selectbox(data_df,'Select quarter:','Quarter')
        
        if view:
            col1,col2 = st.columns(2)
            with col1:
                if year:
                    query = f"select state as State, sum(Transaction_amount) as Total_amount, sum(transaction_count) as Total_count from agg_transaction where year = {year} group by State, Year"
                    tab_view(query,f'Data for {year}',cursor)
            with col2:
                if year and quarter:
                    query = f"select state as State,sum(Transaction_amount) as Total_amount, sum(transaction_count) as Total_count from agg_transaction where year = {year} and quarter = {quarter} group by State, Year,Quarter"
                    tab_view(query,f'Data for Q{quarter}-{year}',cursor)
        else:
            col1,col2 = st.columns(2)
            with col1:
                if year:
                    query = f"select state as State, year as Year, quarter as Quarter,sum(Transaction_amount) as Total_amount, sum(transaction_count) as Total_count from agg_transaction where year = {year} group by State, Year,Quarter"
                    formatted_df = e.extract_convert_to_dataframe(query,cursor)
                    
                    tab1,tab2 = st.tabs(['Total transaction count', 'Total transaction amount'])
                    with tab1:
                        plot_bar(formatted_df,'State','Total_count',f'Total count for {year}','Quarter')
                    with tab2:
                        plot_bar(formatted_df,'State','Total_amount',f'Total amount for {year}')

            with col2:
                if year and quarter:
                    query = f"select state as State, year as Year, quarter as Quarter,sum(Transaction_amount) as Total_amount, sum(transaction_count) as Total_count from agg_transaction where year = {year} and quarter = {quarter} group by State, Year,Quarter"
                    formatted_df = e.extract_convert_to_dataframe(query,cursor)
                    
                    tab1,tab2 = st.tabs(['Total transaction count', 'Total transaction amount'])
                    
                    with tab1:
                        plot_bar(formatted_df,'State','Total_count',f'Total count for Q{quarter}-{year}')
                    with tab2:
                        plot_bar(formatted_df,'State','Total_amount',f'Total amount for Q{quarter}-{year}')
    
    if search_type == 'DISTRICT':
        query = 'select state as State,year as Year,quarter as Quarter from map_transaction group by  state,Quarter,Year'
        data_df = e.extract_convert_to_dataframe(query,cursor)
        
        col1,col2,col3 = st.columns(3)
        with col1:
            state = make_selectbox(data_df,'Select state:','State')
        with col2:
            year = make_selectbox(data_df,'Select year:','Year')
        with col3:
            quarter = make_selectbox(data_df,'Select year:','Quarter')

        if view:
            if state and year and quarter:
                query = f"select upper(left(district,length(district)-9)) as District, sum(Transaction_amount) as Total_amount, sum(transaction_count) as Total_count from map_transaction where state = '{state}' and year = {year} and quarter = {quarter} group by District,year,quarter"
                tab_view(query,f'Data for {state} districts-Q{quarter}-{year}',cursor)
        else:
            if state and year and quarter:
                query = f"select upper(left(district,length(district)-9)) as District, sum(Transaction_amount) as Total_amount, sum(transaction_count) as Total_count from map_transaction where state = '{state}' and year = {year} and quarter = {quarter} group by District,year,quarter"
                formatted_df = e.extract_convert_to_dataframe(query,cursor)
                
                tab1,tab2 = st.tabs(['Total transaction count', 'Total transaction Amount'])
                with tab1:
                    plot_bar(formatted_df,'District','Total_count',f'Total count for districts of {state} for Q{quarter}-{year}')
                with tab2:
                    plot_bar(formatted_df,'District','Total_amount',f'Total amount for {year}')
                    
    if search_type == 'OVERALL':
        #Overall Analysis
        st.header(':violet[OVERALL ANALYSIS]')
        query = 'select year,sum(transaction_amount) Total_amount,sum(transaction_count) as Total_count from agg_transaction group by  year'
        data_df = e.extract_convert_to_dataframe(query,cursor)
        col1,col2 = st.columns([2,1])
        
        with col1:
            tab1,tab2 = st.tabs(['Total count', 'Total transaction Amount'])
            
            with tab1:
                fig = px.pie(data_df,values='Total_count',names = 'year',
                            title='TOTAL TRANSACTIONS (2020-2023)')

                st.plotly_chart(fig)
            with tab2:
                fig = px.bar(data_df,x = 'year',y = 'Total_amount',
                            color= 'year',
                            title='YEAR WISE TRANSACTION AMOUNT',
                            labels={'Total_amount':'Total amount','year':'Year'})
                
                st.plotly_chart(fig)
                
        with col2:
            num_formatted_df = {'Amount':[]}
            for row in data_df['Total_amount'] :
                num_formatted_df['Amount'].append(e.simplify_number(row,True))
            
            num_formatted_df = pd.DataFrame(num_formatted_df)
            data_df['Total_amount'] = num_formatted_df['Amount']
            
            st.table(data_df)
            st.info(
                """                
                -TOTAL TRANSACTION COUNT:\n
                We can see how much percentage of total transactions
                has been done per year\n
                """)
            st.info(
                """
                -TOTAL TRANSACTION AMOUNT\n
                The bar graph shows the amount of premium issued per year.\n
                """)
            st.info(
                """
                -OBSERVATION\n
                We can clearly see that every year the transaction count and the\n
                amount has been increasing
                """)

#User analysis
def user(cursor):
    st.header(':violet[USER ANALYSIS]	:dollar:')
    st.divider()
        
    query = 'select state,year,quarter,district from map_user'
    state_df = e.extract_convert_to_dataframe(query,cursor)
    
    filters = []
    labels = []
    
    st.header('Filters:')
    col1,col2,col3 = st.columns(3)
    with col1:
        with st.container(height = 100):
            state = st.radio('Select state:', options = [None] + [row for row in state_df['state'].unique()],horizontal= True,index = 0)
        year = st.radio('Select year:',options=[None] + [row for row in state_df['year'].unique()],horizontal= True,index = 0)
        quarter = st.radio('Select quarter:',options=[None] + [row for row in state_df['quarter'].unique()],horizontal= True,index = 0)
        if state:
            query = f"select left(district, length(district)-9) as District from map_user where state = '{state}'"
            df = e.extract_convert_to_dataframe(query,cursor)
            with st.container(height = 100):
                district = st.radio('Select district:', options = [None] + [row for row in df['District'].unique()],horizontal= True,index = 0)
            district = f'{district} district'

        if state:
            filters.append(f"state = '{state}'")
            labels.append(f' in :blue[{state}]')
            if district[:4] != 'None':
                st.write('Enter')
                filters.append(f"district = '{district}'")
                labels.append(f' for :blue[{district}]')
        if quarter:
            filters.append(f"quarter = {quarter}")
            labels.append(f' for :red[Q{quarter} ]')
        if year:
            filters.append(f"year = {year}")
            labels.append(f' :violet[{year}]')

    label = ' '.join(labels)
        
    where_clause = " AND ".join(filters)
        
    if where_clause:
        where_clause = 'where ' + where_clause

    query = f"select sum(app_opens) as app, sum(registered_user) as users from map_user {where_clause}"
    data_df = e.extract_convert_to_dataframe(query,cursor)
    
    with col2:
        st.header(f':green[:orange[Registered users] and :orange[App Opens] {label}]')
        
        users = e.simplify_number(int(data_df['users']))
        app_opens = e.simplify_number(int(data_df['app']))
            
        st.metric('Registered users', users)
        st.metric('App Opens ', app_opens)
    
    with col3:
        query = f"select sum(app_opens) as app, sum(registered_user) as users from map_user"
        data_df = e.extract_convert_to_dataframe(query,cursor)
        
        st.header(f':green[:orange[Registered users] and :orange[App Opens] (2018-2023)]')
        
        users = e.simplify_number(int(data_df['users']))
        app_opens = e.simplify_number(int(data_df['app']))
            
        st.metric('Registered users', users)
        st.metric('App Opens ', app_opens)

    st.divider()
    
    st.header(':green[:orange[State] and :orange[District] wise analysis of percentage of :blue[Registered Users] and percentage of :red[App Openings]]')    
    col1,col2 = st.columns(2)
    with col1:
        state = st.selectbox('Select state:', [row for row in state_df['state'].unique()])
        if state:
            query = f"select state,year as Year,sum(registered_user) as Users,sum(app_opens) as App_opens from map_user where state = '{state}' group by state,year;"
            data_df = e.extract_convert_to_dataframe(query,cursor)
            
            data_df['App_Open%'] = data_df['App_opens'].mul(100/(data_df['App_opens'].sum()))
            data_df['Users%'] = data_df['Users'].mul(100/(data_df['Users'].sum()))

            fig = px.bar(data_df,x = 'Year',y = ['Users%','App_Open%'],
                    barmode='group', title = f'Users and App opens for {state}')

            st.plotly_chart(fig,theme=None,use_container_width=True)
        
    with col2:
        if state:
            query = f"select distinct upper(left(district, length(district)-9)) as District from map_user where state = '{state}'"
            data_df = e.extract_convert_to_dataframe(query,cursor)

            district = st.selectbox('Select district:', [row for row in data_df['District'].unique()],index = 0)

            if district:
                query = f"select district,year as Year,sum(registered_user) as Users,sum(app_opens) as App_opens from map_user where district = '{district} district' group by state,year;"
                data_df = e.extract_convert_to_dataframe(query,cursor)
                
                data_df['App_Open%'] = data_df['App_opens'].mul(100/(data_df['App_opens'].sum()))
                data_df['Users%'] = data_df['Users'].mul(100/(data_df['Users'].sum()))

                fig = px.bar(data_df,x = 'Year',y = ['Users%','App_Open%'],
                        barmode='group', title = f'Users and App opens for {district.lower()} district')

                st.plotly_chart(fig,theme=None,use_container_width=True)
    
    st.divider()

    st.header(':green[Brand share analysis per :blue[STATE] and :red[YEAR]]')
    
    query = f"select brand, state, year from agg_user"
    df = e.extract_convert_to_dataframe(query,cursor)
    
    col1,col2 = st.columns(2)
    with col1:
        state = st.selectbox('Select state:', [row for row in df['state'].unique()],key='state_brand')

        query = f"select brand, sum(registered_users_per_brand) users,sum(percentage) percent from agg_user where state = '{state}' group by brand;"
        brand_df = e.extract_convert_to_dataframe(query,cursor)
        
        brand_analysis_pie(brand_df,'percent','brand',f'Brand share for {state}')
        
    with col2:
        year = st.selectbox('Select year:', [row for row in df['year'].unique()],key='year_brand')

        query = f"select brand, sum(registered_users_per_brand) users,sum(percentage) percent from agg_user where state = '{state}' and year = {year} group by brand;"
        brand_df = e.extract_convert_to_dataframe(query,cursor)
        
        brand_analysis_pie(brand_df,'percent','brand',f'Brand share for {state} in {year}')

    st.divider()
    
    st.header(':green[Registered users analysis for :orange[Brand] per :blue[STATE] and per :red[YEAR] ]')

    brand = st.selectbox('Select brand:', [row for row in sorted(df['brand'].unique())],key='brand')

    col1,col2 = st.columns(2)
    
    with col1:
        state = st.selectbox('Select state:', [row for row in df['state'].unique()],key='state')
        
    with col2:
        year = st.selectbox('Select year:', [row for row in df['year'].unique()],key='year')

    col1,col2,col3 = st.columns(3)
    with col1:
        query = f"select state,brand, year, sum(registered_users_per_brand) users from agg_user where brand = '{brand}' group by brand,state ,year;"
        brand_df = e.extract_convert_to_dataframe(query,cursor)
            
        plot_bar(brand_df,'state','users',f'{brand} users','year')
    
    with col2:
        query = f"select state,brand, year, quarter,sum(registered_users_per_brand) users from agg_user where brand = '{brand}' and  state = '{state}' group by brand,state ,year,quarter;"
        brand_df = e.extract_convert_to_dataframe(query,cursor)
            
        plot_bar(brand_df,'quarter','users',f'{brand} users in {state}','year')
        
    with col3:
        query = f"select state,brand, year,quarter, sum(registered_users_per_brand) users from agg_user where brand = '{brand}' and year = {year} group by brand,state ,year,quarter;"
        brand_df = e.extract_convert_to_dataframe(query,cursor)
            
        plot_bar(brand_df,'state','users',f'{brand} users in {year}','quarter')
    
#Brand analysis pie chart
def brand_analysis_pie(df,values,names,title):
    fig = px.pie(df,values = values,names = names,
                    title = title,hole = 0.4)
        
    fig.update_traces(textposition='inside', textinfo='percent+label')

    st.plotly_chart(fig,use_container_width=True)
    
#Common selectbox
def make_selectbox(df,label,option_col):
    state = st.selectbox(label,options=[val for val in df[option_col].unique()],
                        placeholder='Select',index = None)
    return state

#Plot bar chart
def plot_bar(df,x,y,title,color = None):
    if color is not None:
        fig = px.bar(df,
                x = x, 
                y = y,
                color = color,
                title=title,
                barmode='group'
                )
    else:
        fig = px.bar(df,
                x = x, 
                y = y,
                color = y,
                title=title,
                barmode='group'
                )
    
    st.plotly_chart(fig,theme = None,use_container_width=True)

#View as a dataframe  
def tab_view(query,header,cursor):
    formatted_df = e.extract_convert_to_dataframe(query,cursor)
    st.header(header)
    st.dataframe(formatted_df,use_container_width=True,hide_index = True)
                    
# -------------------------------------Explore option--------------------------------

# -------------------------------------Insights option--------------------------------

def insights(cursor):

    question = st.selectbox(
        "Select question to analyze:",
        get_questions(),
        index=0,
    )

    if question:
        question = question[:1]
        get_answer(question, cursor)
        
def get_questions():
    questions = [
        "1. Top 10 states based on year and amount of transaction",
        "2. Least 10 states based on number of transactions",
        "3. Top 10 mobile brands based on percentage of transaction",
        "4. Top 10 districts based on Registered-users per district",
        "5. Top 10 Districts based on states and amount of transaction",
        "6. Least 10 states based on app openings in 2018",
        "7. Percentage of payment types in West bengal for year 2022",
        "8 Top 10 states based on transaction_amount for year 2023 in Q4"]
    return questions

# QUERY SQL AND GET ANSWER
def get_answer(question, cursor,):
    answer_df = e.extract_convert_to_dataframe(get_query(question),cursor)
    
    col1,col2 = st.columns(2)
    with col1:
        st.dataframe(answer_df, use_container_width=True, hide_index=True)
    with col2:
        make_chart(question, answer_df)

# GET THE CORRESPONDING SQL QUERY
def get_query(question):
    question_dict = {
        "1": "SELECT distinct(state) as State,year as Year,sum(Transaction_amount) as Total_amount from agg_transaction group by state,year order by total_amount DESC Limit 10",
        "2": "SELECT DISTINCT state as State, SUM(Transaction_Count) as Total FROM agg_transaction GROUP BY State ORDER BY Total ASC LIMIT 10",
        "3": "SELECT brand as Brand,Round(sum(Percentage) * 100,2) as Total_percentage from agg_user group by brand order by total_percentage desc limit 10",
        "4": "SELECT state as State,district as District, sum(Registered_User) as Total_User from map_user group by State,District order by Total_User desc limit 10",
        "5": "SELECT DISTINCT state as State,district as District, sum(Transaction_amount) as total_amount from map_transaction group by State,District order by total_amount DESC LIMIT 10;",
        "6": "SELECT state as State,sum(App_opens) as Total_opens from  map_user where year = 2020 group by State order by Total_opens limit 10",
        "7": "SELECT transaction_type as Payment_type, sum(Transaction_amount) as Total_amount from agg_transaction where year = 2018 and state = 'West bengal' group by Payment_type",
        "8": "SELECT state as State, sum(Transaction_amount) as Total_amount from agg_transaction where year = 2021 and quarter = 4 group by State order by Total_amount desc limit 10",
    }
    return question_dict[question]

# MAKE CHARTED VIEW
def make_chart(question, df):
    if question == '1':
        fig = px.area(df, x='State', y='Total_amount', color='Year', 
            labels={'Total_amount': 'Transaction Sum'})
        fig.update_layout(barmode='stack')  # stack bars on top of each other
        st.plotly_chart(fig,use_container_width=True)
    
    elif question == '2':
        fig = px.bar(df, x='State', y='Total',)
        st.plotly_chart(fig,use_container_width=True)
    
    elif question == '3':
        total_sum = df['Total_percentage'].sum()
        df['Normalized'] = (df['Total_percentage'] / total_sum) * 100
        
        fig = px.pie(df, values='Normalized', names='Brand',)
        st.plotly_chart(fig,use_container_width=True)
        
    elif question == '4':
        fig = px.bar(df, x='District', y='Total_User', 
            labels={'Total_User': 'Users'})
        st.plotly_chart(fig,use_container_width=True)
        
    elif question == '5':
        fig = px.area(df, x='District', y='total_amount', color='State', 
            labels={'total_amount': 'Total Amount'})
        fig.update_layout(barmode='stack')  # stack bars on top of each other
        st.plotly_chart(fig,use_container_width=True)
        
    elif question == '6':
        fig = px.bar(df, x='State', y='Total_opens', color='State', 
            labels={'Total_opens': 'App Opens'})
        fig.update_layout(barmode='stack')  # stack bars on top of each other
        st.plotly_chart(fig,use_container_width=True)
        
    elif question == '7':
        fig = px.pie(df, values='Total_amount', names='Payment_type',)
        st.plotly_chart(fig,use_container_width=True)
        
    elif question == '8':
        fig = px.bar(df, x='State', y='Total_amount', color='State', 
            labels={'Total_amount': 'Total Amount'})
        st.plotly_chart(fig,use_container_width=True)
        
# -------------------------------------Insights option--------------------------------

# -------------------------------------About option--------------------------------

def about():
    st.markdown(
        "## :blue[Project Title] : Phonepe Pulse Data Visualization and Exploration.A User-Friendly Tool Using Streamlit and Plotly"
    )
    st.markdown(
        "## :blue[Technologies used] : Python, Plotly, JSON, SQL, Streamlit"
    )
    st.markdown(
        "## :blue[Overview] : Retrieving the Phonepe pulse data from the github, storing it in a SQL then querying the data and displaying it in the Streamlit app."
        "Visualization contains map of india showing states and various charts."
    )

# -------------------------------------About option--------------------------------

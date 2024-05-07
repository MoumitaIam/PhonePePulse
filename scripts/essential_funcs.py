import pandas as pd
import locale
import scripts.sql_scripts as sql

#Function to convert numbers to comma separated and with Cr
def simplify_number(number,is_format = False,is_with_point = False):
    
    suffix = ''
    
    locale.setlocale(locale.LC_NUMERIC, "en_IN")

    if not is_format:
        return locale.format_string("%.0f", number, grouping=True)

    if number >= 10000000:
        value =number / 10000000
        suffix = 'Cr'
    elif number >= 100000:
        value =number / 100000
        suffix = 'L'
    elif number >= 1000:
        value =number / 1000
        suffix = 'k'
        
        
    if is_with_point:
        value = locale.format_string("%.2f", value, grouping=True)
    else:
        value = locale.format_string("%.0f", value, grouping=True)
            
    return f'{value}{suffix}'

#Function to extract from sql and convert to dataframe
def extract_convert_to_dataframe(query, cursor):
    data = sql.execute_select(query, cursor)
    return pd.DataFrame(data.fetchall(), columns=data.column_names)

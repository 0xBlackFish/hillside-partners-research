import pandas as pd
import altair as alt
import numpy as np
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import streamlit as st

st.set_page_config(layout="wide")
password = st.text_input('Enter the password to access the site: ')

if password == st.secrets['site_password']:

    # Import file
    category_df = pd.read_csv('Amazon Category Data Jan 2017 Through April 2021.csv')


    # Process file
    category_long_df = pd.melt(category_df,id_vars=['Category'],value_vars=category_df.columns[1:],var_name='month',value_name='spend')
    category_long_df['month'] = category_long_df['month'].apply(pd.to_datetime)
    category_long_df.sort_values(by=['Category','month'],inplace=True)
    category_long_df.reset_index(inplace=True)
    category_long_df.drop(labels=['index'],inplace=True,axis=1)


    # Functions
    def get_previous_year_month(as_of_year_month):
        '''Takes current year-month and returns the previous year'''
        # Get previous year month
        previous_year_month = as_of_year_month - relativedelta(years=1)
        
        return previous_year_month


    def get_py_value(category, as_of_date):
        
        py_value_list = category_long_df[(category_long_df['Category'] == category) & (category_long_df['month'] == as_of_date)]['spend'].tolist()
        
        if not py_value_list:
            return None
        else:
            return py_value_list[0]


    def calculate_yoy_growth(spend, py_spend):
        
        try:
            yoy_growth = (spend - py_spend) / py_spend
        except:
            yoy_growth = 1
        
        return yoy_growth


    def yoy_growth_color(yoy_growth):

        if yoy_growth >= 0:
            return 'positive'
        
        else:
            return 'negative'


    # Execute functions
    category_long_df['py_month'] = category_long_df['month'].apply(get_previous_year_month)
    category_long_df['py_spend'] = np.vectorize(get_py_value)(category_long_df['Category'], category_long_df['py_month'])


    # Eliminate periods without PY history
    category_processed_df = category_long_df[(category_long_df['month'] >= '2018-01-01')]


    # Execute functions (again)
    category_processed_df['yoy_growth'] = np.vectorize(calculate_yoy_growth)(category_processed_df['spend'],category_processed_df['py_spend'])
    category_processed_df['yoy_growth_color'] = category_processed_df['yoy_growth'].apply(yoy_growth_color)


    # Page formatting and category selectbox
    st.title('Hillside Partners Research')
    st.header('Amazon Category Analysis')
    st.write('')
    st.write('')
    category = st.selectbox('Select a category to analyze:',category_processed_df['Category'].unique())
    st.write('')
    st.write('')
    st.write('**Legend**')
    st.write('The *grey line* represents the current year and the *blue line* represents the prior year')
    st.write('')
    st.write('')


    # YoY Comparison Line Chart

    base = alt.Chart(category_processed_df[(category_processed_df['Category'] == category)]).encode(
        x=alt.X('yearmonth(month)',axis=alt.Axis(title='', labelFontSize=12, labelPadding=10, labelAngle=-45))
    )

    cy = base.mark_line(point=True).encode(
        y=alt.Y('spend',axis=alt.Axis(title='Spend',format='$,.0f',labelFontSize=12, labelPadding=10, titleFontSize=16, titlePadding=20)),
        color=alt.value('grey'),
        tooltip=[alt.Tooltip('yearmonth(month)',title='As of Date'),alt.Tooltip('spend',title='CY Spend',format='$,.0f'),alt.Tooltip('py_month',title='PY - As of Date'),alt.Tooltip('py_spend',title='PY Spend',format='$,.0f')]
    )

    py = base.mark_line(point=True).encode(
        y=alt.Y('py_spend',axis=alt.Axis(title='Spend',format='$,.0f',labelFontSize=12, labelPadding=10, titleFontSize=16, titlePadding=20)),
        tooltip=[alt.Tooltip('yearmonth(month)',title='As of Date'),alt.Tooltip('spend',title='CY Spend',format='$,.0f'),alt.Tooltip('py_month',title='PY - As of Date'),alt.Tooltip('py_spend',title='PY Spend',format='$,.0f')]
    )

    st.altair_chart((cy + py).properties(height=400, width=1400),use_container_width=True)

    st.write('')
    st.write('')

    domain = ['negative','positive']
    range_ = ['red', 'grey']

    bar = base.mark_bar().encode(
        y=alt.Y('yoy_growth',axis=alt.Axis(title='YoY Growth',format='%',labelFontSize=12, labelPadding=10, titleFontSize=16, titlePadding=20)),
        color=alt.Color('yoy_growth_color', scale=alt.Scale(domain=domain, range=range_), legend=None),
        tooltip=[alt.Tooltip('yearmonth(month)',title='As of Date'),alt.Tooltip('yoy_growth',title='YoY Growth',format='.1%')]
    ).properties(height=400,width=1400)

    st.altair_chart(bar,use_container_width=True)

else:

    st.header('Please enter the password or if you already tried, try again.')

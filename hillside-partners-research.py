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


    @st.cache
    def get_py_value(category, as_of_date):
        
        py_value_list = category_long_df[(category_long_df['Category'] == category) & (category_long_df['month'] == as_of_date)]['spend'].tolist()
        
        if not py_value_list:
            return None
        else:
            return py_value_list[0]

    
    @st.cache
    def get_py_value_brand(brand, as_of_date):
    
        py_value_list = amazon_brand_long_df[(amazon_brand_long_df['adjusted_brand'] == brand) & (amazon_brand_long_df['month'] == as_of_date)]['spend'].tolist()
        
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


    def adjust_brand(brand):
    
        if brand in lst_365_by_wholefoods:
            return '365 by whole foods'
        elif brand in lst_amazon_basics:
            return 'amazon basics'
        elif brand in lst_daily_ritual:
            return 'daily ritual'
        else:
            return brand


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
    st.write('')
    st.write('')
    st.write('')
    st.write('')


    # All Categories Heat Map

    all_categories_heatmap = alt.Chart(category_processed_df).mark_rect().encode(
        x=alt.X('yearmonth(month):O',axis=alt.Axis(title='',labelFontSize=12,labelPadding=10)),
        y=alt.Y('Category',axis=alt.Axis(title='Category',labelFontSize=12,labelPadding=10,titleFontSize=16,titlePadding=20)),
        color=alt.Color('spend',legend=alt.Legend(format='$,.0f',title='Spend')),
        tooltip=[alt.Tooltip('Category'), alt.Tooltip('yearmonth(month)',title='As of Date'),alt.Tooltip('spend',title='Spend',format='$,.0f')]
    ).properties(width=1400)


    st.subheader('All Categories Heatmap')
    st.write('')
    st.write('')
    st.altair_chart(all_categories_heatmap,use_container_width=True)


    st.write('')
    st.write('')
    st.write('')
    st.write('')
    st.write('')
    st.write('')

    brand_df = pd.read_csv('Amazon Brand Data Jan 2017 Thru April 2021 May 19 2021.csv')
    brand_df['brandName'].fillna('N/A',inplace=True)
    brand_long_df = pd.melt(brand_df,id_vars=['brandName'],value_vars=brand_df.columns[1:],var_name='month',value_name='spend')


    ## Amazon Brands ##
    lst_365_by_wholefoods = ['365 by whole foods','365 by whole foods market','wfm 365','365 by wfm','whole foods','whole foods market']
    lst_amazon_basics = ['amazon basics licensing','amazon basics']
    lst_amazon_collection = ['amazon collection']
    lst_amazon_essentials = ['amazon essentials']
    lst_buttoned_down = ['buttoned down']
    lst_daily_ritual = ['daily ritual','the daily ritual']
    lst_goodthreads = ['goodthreads']
    lst_happy_belly = ['happy belly']
    lst_lark_and_ro = ['lark & ro']
    lst_mae = ['mae']
    lst_mama_bear = ['mama bear']
    lst_mountain_falls = ['mountain falls']
    lst_pinzon = ['pinzon']
    lst_presto = ['presto!']
    lst_rivet = ['rivet']
    lst_solimo = ['solimo']
    lst_stone_and_beam = ['stone & beam']
    lst_vist_cable_stitch = []
    lst_store = ['store']
    lst_wickedly_prime = ['wickedly prime']
    lst_amazon_brands = ['365 by whole foods','amazon basics','amazon collection','amazon essentials','buttoned down','daily ritual','goodthreads','happy belly','lark & ro','mae','mama bear','mountain falls','pinzon','presto!','rivet','solimo','stone & beam','store','wickedly prime']

    brand_long_df['adjusted_brand'] = brand_long_df['brandName'].apply(adjust_brand)

    amazon_brand_long_df = brand_long_df[brand_long_df['adjusted_brand'].isin(lst_amazon_brands)].groupby(['adjusted_brand','month']).sum()
    amazon_brand_long_df.reset_index(inplace=True)
    amazon_brand_long_df['month'] = amazon_brand_long_df['month'].apply(pd.to_datetime)
    amazon_brand_long_df['py_month'] = amazon_brand_long_df['month'].apply(get_previous_year_month)
    amazon_brand_long_df['py_spend'] = np.vectorize(get_py_value_brand)(amazon_brand_long_df['adjusted_brand'], amazon_brand_long_df['py_month'])

    amazon_brand_processed_df = amazon_brand_long_df[amazon_brand_long_df['month'] >= '2018-01-01']
    amazon_brand_processed_df['yoy_growth'] = np.vectorize(calculate_yoy_growth)(amazon_brand_processed_df['spend'],amazon_brand_processed_df['py_spend'])
    amazon_brand_processed_df['yoy_growth_color'] = amazon_brand_processed_df['yoy_growth'].apply(yoy_growth_color)

    st.header('Amazon Brand Analysis')
    st.write('')
    st.write('')
    amazon_brand = st.selectbox('Select an Amazon brand to analyze:',amazon_brand_processed_df['adjusted_brand'].unique())
    st.write('')
    st.write('')
    st.write('**Legend**')
    st.write('The *grey line* represents the current year and the *blue line* represents the prior year')
    st.write('')
    st.write('')

    # YoY Comparison Line Chart

    brand_base = alt.Chart(amazon_brand_processed_df[(amazon_brand_processed_df['adjusted_brand'] == amazon_brand)]).encode(
        x=alt.X('yearmonth(month)',axis=alt.Axis(title='', labelFontSize=12, labelPadding=10, labelAngle=-45))
    )

    cy_brand = brand_base.mark_line(point=True).encode(
        y=alt.Y('spend',axis=alt.Axis(title='Spend',format='$,.0f',labelFontSize=12, labelPadding=10, titleFontSize=16, titlePadding=20)),
        color=alt.value('grey'),
        tooltip=[alt.Tooltip('yearmonth(month)',title='As of Date'),alt.Tooltip('spend',title='CY Spend',format='$,.0f'),alt.Tooltip('py_month',title='PY - As of Date'),alt.Tooltip('py_spend',title='PY Spend',format='$,.0f')]
    )

    py_brand = brand_base.mark_line(point=True).encode(
        y=alt.Y('py_spend',axis=alt.Axis(title='Spend',format='$,.0f',labelFontSize=12, labelPadding=10, titleFontSize=16, titlePadding=20)),
        tooltip=[alt.Tooltip('yearmonth(month)',title='As of Date'),alt.Tooltip('spend',title='CY Spend',format='$,.0f'),alt.Tooltip('py_month',title='PY - As of Date'),alt.Tooltip('py_spend',title='PY Spend',format='$,.0f')]
    )


    st.altair_chart((cy_brand + py_brand).properties(height=400, width=1400),use_container_width=True)

    st.write('')
    st.write('')

    domain = ['negative','positive']
    range_ = ['red', 'grey']

    bar_brand = brand_base.mark_bar().encode(
        y=alt.Y('yoy_growth',axis=alt.Axis(title='YoY Growth',format='%',labelFontSize=12, labelPadding=10, titleFontSize=16, titlePadding=20)),
        color=alt.Color('yoy_growth_color', scale=alt.Scale(domain=domain, range=range_), legend=None),
        tooltip=[alt.Tooltip('yearmonth(month)',title='As of Date'),alt.Tooltip('yoy_growth',title='YoY Growth',format='.1%')]
    ).properties(height=400,width=1400)

    st.altair_chart(bar_brand,use_container_width=True)
    st.write('')
    st.write('')
    st.write('')
    st.write('')


else:

    st.header('Please enter the password or if you already tried, try again.')

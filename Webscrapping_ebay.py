#!/usr/bin/env python
# coding: utf-8

# ## Web Scrapping Project

# In[8]:


import requests
import json
from bs4 import BeautifulSoup
import pandas as pd

import re
import dash
# import dash_core_components as dcc
# import dash_html_components as html
from dash import dcc, html
from dash.dependencies import Input, Output
from jupyter_dash import JupyterDash
from dash import dash_table
from dash_table import DataTable, FormatTemplate
import plotly.express as px
from dash.dash_table.Format import Group

import numpy as np
import dash_bootstrap_components as dbc


# In[23]:


def items(search_value):
            url =f' https://www.ebay.com/sch/i.html?_from=R40&_trksid=p4432023.m570.l1312&_nkw={search_value}&_sacat=0&_pgn ='
            #url = f'https://www.ebay.com/sch/i.html?_from=R40&_trksid=p4432023.m570.l1313&_nkw={brand}&ipg=120&_pgn={pages}&rt=nc'
        #     url = f'https://www.ebay.com {item}'
            main_dic = {}
            k=0
            for page in range(1):
                response = requests.get(url+str(page)).text
                html_text = BeautifulSoup(response, "html.parser")

                items = html_text.find_all('div', class_ ="s-item__info clearfix")

                for item in items[1:]:
                    k=k+1
                    item_info = {}# Create a emptt dictionary for all the index 
                    #in the emptly dictionary, put the keys as desired value name, value of which is scrapped.
                    item_info['item_name']=  item.find('div', class_="s-item__title").text.strip(" ")
                    item_info['condition'] = item.find('span', class_ ='SECONDARY_INFO' ).text
                    item_info['price_raw'] = item.find('span', class_="s-item__price").text
#                     item_info['min_price'] = 
                    item_info['min_price'] = float(" ".join(re.findall('[\d,\.]+',item.find('span', class_="s-item__price").text[:10])).replace(",","")) if " ".join(re.findall('[\d,\.]+',item.find('span', class_="s-item__price").text[:10])) != "" else np.nan
                    item_info['max_price'] = float(' '.join(re.findall('[\d,\.]+',item.find('span', class_="s-item__price").text[-9:])).replace(",", "")) if " ".join(re.findall('[\d.\.]+', item.find('span', class_="s-item__price").text[-9:])) !="" else np.nan
                    
#                     item_info['shipping'] =  item.find('span', class_='s-item__dynamic s-item__freeXDays').text if item.find('span', class_='s-item__dynamic s-item__freeXDays') is not None else item.find('span', class_='s-item__shipping s-item__logisticsCost').text
#                     item_info['shipping_cost'] = float(0) if  item_info['shipping'].startswith('Free') else float(re.sub('[^[0-9]+\.[0-9]+$]', "", item_info['shipping'][2:7])) 
                    item_info['free return'] = 'Yes' if item.find('span', class_="s-item__free-returns s-item__freeReturnsNoFee") is not None else 'No'
#                     item_info['percent_dropped'] = float(re.sub('\W', "", item.find('span', class_="s-item__discount s-item__discount").text[:2])) if item.find('span', class_="s-item__discount s-item__discount") is not None else float (0)
                    item_info['review_star'] = float(item.find('div', class_="x-star-rating").text[:3]) if item.find('div', class_="x-star-rating") is not None else np.nan
                    item_info['review_count'] = float(re.sub('[a-zA-Z]+',"",item.find('span', class_="s-item__reviews-count").text[:4]))if item.find('span', class_='s-item__reviews-count') is not None else np.nan
    
                    item_info['bid']= 'Yes' if item.find('span', class_="s-item__bids s-item__bidCount") is not None else 'No'
#                     item_info['No_of_bids'] = re.sub('[a-zA-Z]+',"", item.find('span', class_="s-item__bids s-item__bidCount").text) if item.find('span', class_="s-item__bids s-item__bidCount") is not None else np.nan
                    item_info['bids_ends_on'] = item.find('span', class_="s-item__time-end").text if item.find('span', class_="s-item__time-end") is not None else np.nan
                    del item_info['price_raw']


                    # Assign the created dictionary of shoe information to the main dictionary, which key is index and value is shoe_info(dictionary of scrapped variables)
                    main_dic[k]= item_info
            json_object = json.dumps(main_dic, indent = 5)
    #         from IPython.display import display
            table= pd.read_json(json_object).T
        #     data.to_csv(f'{brand}.csv')
        #     display(data)
        #     print (data.head(3))
            return table


# In[24]:


app = dash.Dash(prevent_initial_callbacks =True, external_stylesheets = [dbc.themes.PULSE],
               meta_tags =[{'name':'viewport',
                           'content':'width=device-width, initial-scale = 0.9, maximum-scale = 1.9, minimum-scale = 0.5'}])

app.layout = html.Div([
#     dbc.Button('Success', color ="success", className ="mr-1"),
    html.H1('EBAY Webscraping and Analytics', style= {'margin': "1px", 'text-align':'center'}),
    html.Br(),
    html.Br(),
    html.Div(
     children =[
        html.Div(
            children = [
            html.H2('Get product data from EBAY', style = {"font-size": '20px', "margin": '5px 15px 2px 5px'}),
#             html.H3('Enter any electronic brand or product name! (eg. Iphone 14)'),
            html.Br(),
            # Add the required input
            dcc.Input(id = "search_desc", type = 'text',
            placeholder = 'Enter any brand or product name! (eg. Iphone 14)',
            debounce = True,
                      # Ensure the table can load without a search 
            required = True,
            style = {"width":'360px', 'height':'30px', 'border': '0.5px dashed black', 'margin': '-3px 10px 20px 10px'})
            ],
            style = {'width':'380px', 'height':'100px','vertical-align':'center', 'border': '0.5px solid black',
                  'display': 'inline-block', 'margin':'5px 10px 10px 15px'}),
         
        html.Div(
            children=[
#             html.H3 (id = "search product table", style = {'width':'900px', 'height':'50px','vertical-align':'top',
#                   'display': 'inline-block', 'margin':'10px 10px 1px 10px'}), 
            
            html.Div(id ='table_container', style = {"margin": '1px 17px 5px 15px', 'overflowX':'scroll', 'height':230}),
            
             html.Div (id = "search product table", style = { "font-size": '10px', 'background-color':'rgb(255, 153, 153)',
                  'display': 'inline-block', 'margin':'0px 10px 15px 15px'})
        ], 
         style = {'text-align':'left', 'display':'inline-block', 'width':'100%'}),
         
         
         html.Div(
             children = [
                   html.H6('Basic descriptive statistics of searched product', 
                            style ={'text-align':'left', 
                                    'margin':'0px 10px 15px 15px',
                                    'background-color':'rgb(0, 153, 200)'}
#                  html.H4(f'Basic descriptive statisctics of searched product', style = {"margin": '20px 10px 10px 10px'}
#                  dcc.Dropdown(
#                  id= 'condition_dd',
# #                  options =[{'label':category, 'value':category} for category in condition_categories],
#                 style ={'width':'300px', 'margin': '10 auto'}


                 )
                 
#                  dcc.Graph(id = "bar1_condition_distribution", style ={"display":'inline-block'}),
                 
#                  dcc.Graph(id = "piechart_bid", style ={"display": 'inline-block'})
             ])]),
        

               

    html.Div(
           children = [
         dcc.Graph(id = "bar1_condition_distribution", style ={"display":'inline-block', "margin":'0px 0px 0px 1px', 'overflowY':'scroll'}),
         dcc.Graph(id = "stackchart_bid", style ={"display": 'inline-block', "margin":'0px 0px 0px 1px', 'overflowY':'scroll'})
     ]
    ),
    
    
#     html.Div(
#            children = [
               
#                html.H4 (id = "highest_price_listing", style = {"display": "inline-block", 'margin': '10px 10px 1px 10px', 'background-color':'rgb(255, 153, 153)' }),
               
#                html.H4 (id = 'lowest_price_listing', style = {'display': 'inline-block', 'margin': '10px 10px 50px 170px','background-color':'LightBlue'})
#            ]
    
    
#     ),
    
    html.Div(
           children =[
               html.H3('List of selected products having rating of 4 stars or above', style ={"font-size": '14px', 
                                                                                              'margin':'0px 10px 15px 15px',
                                                                                             'background-color':'rgb(32,178,170)'}),
               
               html.Div(
               children=[
                   html.H4 ('Select product condition type',
                           style ={"font-size": '14px', 'margin':'0px 50px 15px 15px',
                                  'text-color':'rgb(0, 0, 0)'}),
                   dcc.Dropdown(
                   id ="dynamic-dropdown", 
#                    
                   style = {'width':'300px', 'margin':'0px 10px 15px 10px'}
                   ),
                   
                    html.Div(
                        id = "table_container2", style = {"margin": '1px 17px 5px 15px', 'overflowX':'scroll', 'height':230})
               ]
               
                 
               
               )
               
               
           ])
    
    
    ])

# one callback to set minor values & HTML output

##### commentout for a while

@app.callback(
    Output(component_id ='table_container', component_property ='children', allow_duplicate= True),
    
    Output('search product table', 
           component_property = 'children'),
    
    Output(component_id='bar1_condition_distribution',
           component_property ='figure'),
    
    Output(component_id = 'stackchart_bid', 
           component_property="figure"),
    
    Output (component_id = "dynamic-dropdown", 
             component_property = 'options'),
    
    
    
    Input(component_id ='search_desc', 
          component_property ='value'), prevent_initial_call = True
)
         
         
         
def generate_table_and_title_figure_dd (search_value):
    if search_value is None:
        search_value = "Fender"
    else:
        global dataframe

        dataframe = items(search_value)

        
        
        dataframe_dash = DataTable(data = dataframe.to_dict('records'),
            columns=[{'name': col, 'id': col} for col in dataframe.columns],
                                  cell_selectable = False,
                                  sort_action = 'native',
                                  filter_action='native',
                                  #Add pagination
                                  page_action = 'native',
                                  page_current = 0,
                                  page_size = 4,
                                  style_cell ={'textAlign':'left'})
        title = f'The above table is the data result for the entered search description "{search_value}".'
        
        
        
        
        dataframe1 = dataframe.copy(deep = True)
        data = pd.DataFrame(dataframe1['condition'].unique())[0]
        option = [{'label':i, 'value':i} for i in data]

        
        bar_data = dataframe1.groupby('condition')['item_name'].count().sort_values(ascending  = False).reset_index()
        stackdata = pd.DataFrame(round(dataframe1.groupby("condition")['bid'].value_counts(normalize = True), 2))
        
        
        barfig_1 = px.bar(data_frame =bar_data, 
                          x ='condition',
                          y= 'item_name',
                          labels ={'condition':'', "item_name":'number of item listed'},
                          title =f'Number of listed products by condition type <br> <sub> product: {search_value}', text_auto = True)
#                          marker_color = 'LightSeagreen')

        barfig_1.update_traces(marker_color = "LightSeaGreen")
        barfig_1.update_layout(width =400, height = 350, yaxis = {"visible":False},
                              font=dict(
#         family="Courier New, monospace",
        size=11,
        color="RebeccaPurple"))
        
        
        stackchart_norm = stackdata.rename(columns = {'condition':"condition",'bid':'rate'}).reset_index().sort_values(ascending = False, by='rate')
        stackchart_fig = px.bar(data_frame = stackchart_norm, 
                               x = 'condition',
                               y= 'rate',
                               color ='bid',
                               color_discrete_map = {'Yes':'Grey', 'No':'LightSeaGreen'},
                               title = '% of product listed in bid', text_auto = True, 
                           labels ={'condition':"", 'rate': ""})
        stackchart_fig.update_layout(height = 350, width = 400, yaxis = {'visible':False}, 
                                 font=dict(
#         family="Courier New, monospace",
        size=11,
        color="RebeccaPurple")
                                )
        
        
        
        return dataframe_dash, title, barfig_1, stackchart_fig, option






@app.callback(
    Output(component_id ='table_container2', component_property ='children'),
    Input(component_id='search_desc', component_property = 'value'),
    Input(component_id='dynamic-dropdown', component_property = 'value'), prevent_initial_call = True)


def table(search_value, option):
    if not option:
        selection = 'Brand New'
    else: 
        global df_dash
        selection = option
        dataframe = items(search_value)
#         data_json = json.dumps(df_dash)
#         dataframe = pd.read_json(data_json)
        filter_data = dataframe[(dataframe['condition']==option) & (dataframe['review_star']>=4)]
        filter_data = filter_data[['item_name','condition', 'min_price', 'max_price', 'review_count' ]]
        
        df_dash = DataTable(data = filter_data.to_dict('records'),
                                                columns=[{'name': col, 'id': col} for col in filter_data.columns],
                                              cell_selectable = False,
                                              sort_action = 'native',
                                              filter_action='native',
                                              #Add pagination
                                              page_action = 'native',
                                              page_current = 0,
                                              page_size = 4,
                                              style_cell ={"textAlign":'left'}
                           
                           )
           
 
    
        return df_dash





    
    

    

    

    
if __name__ == '__main__':
    app.run_server(debug = True, port = 8052, jupyter_mode = 'external')
# app.run_server(debug = False)


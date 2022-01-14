import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px  # pip install plotly-express
import plotly.io as pio
from io import BytesIO
from datetime import datetime
from PIL import Image
import plotly.graph_objects as go
from datetime import timedelta

######################
# Initialize variables
######################
# background nutanix logo for diagrams
background_image = dict(source=Image.open("images/nutanix-x.png"), xref="paper", yref="paper", x=0.5, y=0.5, sizex=0.95, sizey=0.95, xanchor="center", yanchor="middle", opacity=0.04, layer="below", sizing="contain")

######################
# Custom Functions
######################
# Use local CSS
def local_css(file_name):
    with open(file_name) as f:
        #st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        return f.read()

@st.cache
def get_data_from_csv(uploaded_file):

    # Normal export should include the following columns
    columns_to_read = ['Time (s)','CPU (%)','Mem (%)','Mem Total (MB)','Mem Used (MB)','Protocol (FPS)','Protocol RTT (ms)','GPU0 (%)','GPU0 Mem (%)','GPU0 Encode (%)','GPU0 Decode (%)','GPU0 Mem Total (MB)','GPU0 Mem Used (MB)']

    # create dataframe from CSV file and read all columns (rather than only predefined ones for now)
    df = pd.read_csv(uploaded_file, encoding="ISO-8859-1", error_bad_lines=False)#, usecols=columns_to_read)
    
    return df

@st.cache
def generate_utilization_linechart(main_df):

    line_chart = go.Figure()
    line_chart.add_trace(go.Scatter(x=main_df['Time (s)'], y=main_df['CPU (%)'], mode='lines', name='CPU (%)', line=dict(color="#4379BD")))
    line_chart.add_trace(go.Scatter(x=main_df['Time (s)'], y=main_df['Mem (%)'], mode='lines', name='Memory (%)',line=dict(color="#F4B324")))
    line_chart.add_trace(go.Scatter(x=main_df['Time (s)'], y=main_df['GPU0 (%)'], mode='lines', name='GPU0 (%)',line=dict(color="#F36D21")))
    line_chart.add_trace(go.Scatter(x=main_df['Time (s)'], y=main_df['GPU0 Mem (%)'], mode='lines', name='GPU0 Memory (%)',line=dict(color="#3ABFEF")))
    line_chart.add_trace(go.Scatter(x=main_df['Time (s)'], y=main_df['GPU0 Encode (%)'], mode='lines', 
        name='GPU0 Encode (%)',line=dict(color="#6560AB"), visible='legendonly'))
    line_chart.add_trace(go.Scatter(x=main_df['Time (s)'], y=main_df['GPU0 Decode (%)'], mode='lines', 
        name='GPU0 Decode (%)',line=dict(color="#76787A"), visible='legendonly'))

    line_chart.add_layout_image(background_image)

    line_chart.update_layout(
            margin=dict(l=10, r=10, t=20, b=10,pad=4), autosize=True,
            xaxis={'visible': True, 'showticklabels': True},
            xaxis_title_text="Duration {:0>8} (h/m/s)".format(str(timedelta(seconds=int(main_df['Time (s)'].max())))),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0.001),
            hovermode="x unified",
            #legend_title_text='Trend'
        )

    line_chart_config = { 
            "displaylogo": False, 'modeBarButtonsToRemove': ['zoom2d', 'toggleSpikelines', 'pan2d', 'select2d',
             'lasso2d', 'autoScale2d', 'hoverClosestCartesian', 'hoverCompareCartesian']
        }    

    return line_chart, line_chart_config

@st.cache
def generate_histogram(main_df,x_axis):

    hist, bins = np.histogram(main_df[x_axis], bins=np.arange(0, 110, 10), density=True)
    bins = 0.5 * (bins[:-1] + bins[1:])    
    histogram_chart = px.bar(
            x=bins,
            y=hist*1000,
            text=np.where((hist*1000)>0.9,[f'{round(i*1000,2)}%' for i in hist] ,'')               
        )

    histogram_chart.update_yaxes(dtick=10,tick0=10,range=[0, 100])
    histogram_chart.update_xaxes(dtick=10,tick0=10)
    histogram_chart.update_layout(
        margin=dict(l=10, r=10, t=20, b=10,pad=4), autosize=True,
        xaxis_title_text=x_axis, # xaxis label
        #yaxis_title_text='Count', # yaxis label
        #title_text='Sampled Results', # title of plot
        xaxis={'visible': True, 'showticklabels': True},
        yaxis_title_text='Probability (%', # yaxis label
        yaxis={'visible': True, 'showticklabels': True},
        bargap=0.1, # gap between bars of adjacent location coordinates
        #bargroupgap=0.1 # gap between bars of the same location coordinates
    )    
    histogram_chart.update_traces(marker=dict(color='#034EA2'),texttemplate='%{text}', textposition='outside',textfont_size=14, cliponaxis= False)
    histogram_chart.add_layout_image(background_image)
    histogram_chart_config = {'staticPlot': True}

    return histogram_chart, histogram_chart_config


@st.cache(allow_output_mutation=True)
def generate_CPU_table_df(main_df,x_percentile,column_name):

    CPU_min = str(round(main_df[column_name].min()))+' %'
    CPU_median = str(round(main_df[column_name].median()))+' %'
    CPU_average = str(round(main_df[column_name].mean()))+' %'
    CPU_percentile = str(round(main_df[column_name].quantile(x_percentile/100)))+' %'
    CPU_max = str(round(main_df[column_name].max()))+' %'
    percentile_string = 'CPU '+str(x_percentile)+'th Percentile:'
    CPU_table_first_column = {'Analysis': ['CPU Min:','CPU Median:','CPU Average:',percentile_string,'CPU Max:']}
    CPU_table_df = pd.DataFrame(CPU_table_first_column)
    CPU_table_second_column = [CPU_min,CPU_median,CPU_average,CPU_percentile,CPU_max]
    CPU_table_df.loc[:,'Value'] = CPU_table_second_column

    return CPU_table_df


@st.cache(allow_output_mutation=True)
def generate_Memory_table_percentages_df(main_df,x_percentile,column_name):

    Memory_min = str(round(main_df[column_name].min()))+' %'
    Memory_median = str(round(main_df[column_name].median()))+' %'
    Memory_average = str(round(main_df[column_name].mean()))+' %'
    Memory_percentile = str(round(main_df[column_name].quantile(x_percentile/100)))+' %'
    Memory_max = str(round(main_df[column_name].max()))+' %'
    percentile_string = 'Memory '+str(x_percentile)+'th Percentile:'
    Memory_table_first_column = {'Analysis': ['Memory Min:','Memory Median:','Memory Average:',percentile_string,'Memory Max:']}
    Memory_table_df = pd.DataFrame(Memory_table_first_column)
    Memory_table_second_column = [Memory_min,Memory_median,Memory_average,Memory_percentile,Memory_max]
    Memory_table_df.loc[:,'Value'] = Memory_table_second_column

    return Memory_table_df


@st.cache(allow_output_mutation=True)
def generate_Memory_table_total_df(main_df,x_percentile,column_name):

    Memory_min = str(round(main_df[column_name].min()))+' MB / ~'+str(round(main_df[column_name].min()/1024))+' GB'
    Memory_median = str(round(main_df[column_name].median()))+' MB / ~'+str(round(main_df[column_name].median()/1024))+' GB'
    Memory_average = str(round(main_df[column_name].mean()))+' MB / ~'+str(round(main_df[column_name].mean()/1024))+' GB'
    Memory_percentile = str(round(main_df[column_name].quantile(x_percentile/100)))+' MB / ~'+str(round(main_df[column_name].quantile(x_percentile/100)/1024))+' GB'
    Memory_max = str(round(main_df[column_name].max()))+' MB / ~'+str(round(main_df[column_name].max()/1024))+' GB'

    percentile_string = 'Memory '+str(x_percentile)+'th Percentile:'
    Memory_table_first_column = {'Analysis': ['Memory Min:','Memory Median:','Memory Average:',percentile_string,'Memory Max:']}
    Memory_table_df = pd.DataFrame(Memory_table_first_column)
    Memory_table_second_column = [Memory_min,Memory_median,Memory_average,Memory_percentile,Memory_max]
    Memory_table_df.loc[:,'Value'] = Memory_table_second_column
   
    return Memory_table_df


@st.cache(allow_output_mutation=True)
def generate_GPU0_table_df(main_df,x_percentile,column_name):

    GPU0_min = str(round(main_df[column_name].min()))+' %'
    GPU0_median = str(round(main_df[column_name].median()))+' %'
    GPU0_average = str(round(main_df[column_name].mean()))+' %'
    GPU0_percentile = str(round(main_df[column_name].quantile(x_percentile/100)))+' %'
    GPU0_max = str(round(main_df[column_name].max()))+' %'
    percentile_string = 'GPU0 '+str(x_percentile)+'th Percentile:'
    GPU0_table_first_column = {'Analysis': ['GPU0 Min:','GPU0 Median:','GPU0 Average:',percentile_string,'GPU0 Max:']}
    GPU0_table_df = pd.DataFrame(GPU0_table_first_column)
    GPU0_table_second_column = [GPU0_min,GPU0_median,GPU0_average,GPU0_percentile,GPU0_max]
    GPU0_table_df.loc[:,'Value'] = GPU0_table_second_column

    return GPU0_table_df


@st.cache(allow_output_mutation=True)
def generate_GPU0_memory_table_percentages_df(main_df,x_percentile,column_name):

    GPU0_memory_min = str(round(main_df[column_name].min()))+' %'
    GPU0_memory_median = str(round(main_df[column_name].median()))+' %'
    GPU0_memory_average = str(round(main_df[column_name].mean()))+' %'
    GPU0_memory_percentile = str(round(main_df[column_name].quantile(x_percentile/100)))+' %'
    GPU0_memory_max = str(round(main_df[column_name].max()))+' %'
    percentile_string = 'GPU0 Memory '+str(x_percentile)+'th Percentile:'
    GPU0_memory_table_first_column = {'Analysis': ['GPU0 Memory Min:','GPU0 Memory Median:','GPU0 Memory Average:',percentile_string,'GPU0 Memory Max:']}
    GPU0_memory_table_df = pd.DataFrame(GPU0_memory_table_first_column)
    GPU0_memory_table_second_column = [GPU0_memory_min,GPU0_memory_median,GPU0_memory_average,GPU0_memory_percentile,GPU0_memory_max]
    GPU0_memory_table_df.loc[:,'Value'] = GPU0_memory_table_second_column

    return GPU0_memory_table_df


@st.cache(allow_output_mutation=True)
def generate_GPU0_Memory_table_total_df(main_df,x_percentile,column_name):

    GPU0_Memory_min = str(round(main_df[column_name].min()))+' MB / ~'+str(round(main_df[column_name].min()/1024))+' GB'
    GPU0_Memory_median = str(round(main_df[column_name].median()))+' MB / ~'+str(round(main_df[column_name].median()/1024))+' GB'
    GPU0_Memory_average = str(round(main_df[column_name].mean()))+' MB / ~'+str(round(main_df[column_name].mean()/1024))+' GB'
    GPU0_Memory_percentile = str(round(main_df[column_name].quantile(x_percentile/100)))+' MB / ~'+str(round(main_df[column_name].quantile(x_percentile/100)/1024))+' GB'
    GPU0_Memory_max = str(round(main_df[column_name].max()))+' MB / '+str(round(main_df[column_name].max()/1024))+' GB'

    percentile_string = 'GPU0 Memory '+str(x_percentile)+'th Percentile:'
    GPU0_Memory_table_first_column = {'Analysis': ['GPU0 Memory Min:','GPU0 Memory Median:','GPU0 Memory Average:',percentile_string,'GPU0 Memory Max:']}
    GPU0_Memory_table_df = pd.DataFrame(GPU0_Memory_table_first_column)
    GPU0_Memory_table_second_column = [GPU0_Memory_min,GPU0_Memory_median,GPU0_Memory_average,GPU0_Memory_percentile,GPU0_Memory_max]
    GPU0_Memory_table_df.loc[:,'Value'] = GPU0_Memory_table_second_column
  
    return GPU0_Memory_table_df
import plotly.express as px  # pip install plotly-express
import streamlit as st  # pip install streamlit
import custom_functions
import pandas as pd
from PIL import Image

######################
# Page Config
######################
st.set_page_config(page_title="NVIDIA GPU Profiler Analysis", page_icon='./style/favicon.png', layout="wide")
# Use CSS Modifications stored in CSS file            
st.markdown(f"<style>{custom_functions.local_css('style/style.css')}</style>", unsafe_allow_html=True)

######################
# Initialize variables
######################
main_df = pd.DataFrame() # Initialize Main Dataframe as Empty in order to check whether it has been filled

######################
# Page sections
######################
header_section = st.container() # Description of page & what it is about
content_section = st.container() # Content of page - either error message if wrong excel file or analysis content

######################
# Page content
######################
with st.sidebar:
    st.markdown('# **Upload**')
    uploaded_file = st.sidebar.file_uploader(label="Upload here your CSV based NVIDIA GPU Profiler Export.", type=['csv'], help='You can generate this Excel Report directly from the "NVIDIA GPU Profiler" Application via the "Export" button.')

    if uploaded_file is not None:
        try:
            # load CSV in Dataframe
            main_df = custom_functions.get_data_from_csv(uploaded_file)            

            x_percentile = st.slider('Choose custom X-Percentile:', 0, 100,95,help='Select custom Percentile for analysis. 95th Percentile as default.')

            if 'GPU1 (%)' in main_df.columns:
                st.sidebar.warning('More than 1 GPU detected. Due to Lack of Multi-GPU-Samples only the first GPU0 is analysed. Please contact me with this Multi-GPU sample file to add multiple GPUs to analysis.')           

        except Exception as e:
            content_section.error("##### ERROR: CSV file could not be read.")
            content_section.markdown("---")
            content_section.markdown("The following error occurred for further troubleshooting:")
            content_section.exception(e)

with header_section:
    
    st.markdown("<h1 style='text-align: left; color:#034ea2;'>NVIDIA GPU Profiler Analysis</h1>", unsafe_allow_html=True)
    st.markdown('A hobby project by [**Martin Stenke**](https://www.linkedin.com/in/mstenke/) for easy analysis of a [**GPUProfiler**](https://github.com/JeremyMain/GPUProfiler/) evaluation regarding VDI/vGPU recommendations.')

    howto = st.expander(label='HowTo')
    with howto:
        howto_col1, howto_col2, howto_col3 = st.columns(3)
        with howto_col1:
            st.write('After the GPU Profiler has recorded the utilization on the system for the defined period of time, the evaluation can be exported (Export Button) as a ".CSV" or saved (Save button) as a ".GPD" file. For this analysis tool only the CSV file is required.')
        with howto_col2:
            gpuprofiler_image = Image.open('images/gpuprofiler.png')
            st.image(gpuprofiler_image, caption='GPU Profiler Screenshot', use_column_width=True)
        with howto_col3:
            csv_image = Image.open('images/csv.png')
            st.image(csv_image, caption='CSV Export File Screenshot', use_column_width=True)
    
    st.info('***Disclaimer: This is just a hobby project - no guarantee of completeness or correctness of the evaluation / data.***')
    st.markdown("---")

with content_section: 

    if not main_df.empty:

        st.markdown("<h5 style='text-align: left; color:#034ea2; '>General Utilization Overview</h5>", unsafe_allow_html=True)
        st.write('Use the legend entries above the diagramm to show or hide certain graphs.')
        line_chart, line_chart_config = custom_functions.generate_utilization_linechart(main_df)
        st.plotly_chart(line_chart,use_container_width=True, config=line_chart_config)

        CPU_expander = st.expander(label='CPU Details')
        with CPU_expander:
            st.markdown("<h5 style='text-align: left; color:#034ea2; '>CPU Analysis</h5>", unsafe_allow_html=True)

            CPU_plot, CPU_table = st.columns(2)
            with CPU_plot:  
                cpu_chart, cpu_config = custom_functions.generate_histogram(main_df,'CPU (%)')
                st.plotly_chart(cpu_chart,use_container_width=True, config=cpu_config)
            with CPU_table:
                CPU_table_df = custom_functions.generate_CPU_table_df(main_df,x_percentile,'CPU (%)')
                st.table(CPU_table_df)
        
        Memory_expander = st.expander(label='Memory Details')
        with Memory_expander:
            st.markdown("<h5 style='text-align: left; color:#034ea2; '>Memory Analysis</h5>", unsafe_allow_html=True)

            Memory_plot, Memory_table = st.columns(2)            
            with Memory_plot:  
                memory_chart, memory_config = custom_functions.generate_histogram(main_df,'Mem (%)')
                st.plotly_chart(memory_chart,use_container_width=True, config=memory_config)
            with Memory_table:
                Memory_table_df_percentages = custom_functions.generate_Memory_table_percentages_df(main_df,x_percentile,'Mem (%)')            
                st.table(Memory_table_df_percentages)

                st.markdown("<p><strong>Total Memory Available: "+str(round(main_df['Mem Total (MB)'].mean()))+" MB / "+str(round(main_df['Mem Total (MB)'].mean()/1024))+" GB</strong></p>", unsafe_allow_html=True)

                Memory_table_total_df = custom_functions.generate_Memory_table_total_df(main_df,x_percentile,'Mem Used (MB)')
                st.table(Memory_table_total_df)
        
        GPU0_expander = st.expander(label='GPU0 Details')
        with GPU0_expander:
            st.markdown("<h5 style='text-align: left; color:#034ea2; '>GPU0 Analysis</h5>", unsafe_allow_html=True)
            GPU0_plot, GPU0_table = st.columns(2)        
            with GPU0_plot:  
                GPU0_chart, GPU0_config = custom_functions.generate_histogram(main_df,'GPU0 (%)')
                st.plotly_chart(GPU0_chart,use_container_width=True, config=GPU0_config)
            with GPU0_table:
                GPU0_table_df = custom_functions.generate_GPU0_table_df(main_df,x_percentile,'GPU0 (%)')
                st.table(GPU0_table_df)
        
        GPU0_Memory_expander = st.expander(label='GPU0 Memory Details')
        with GPU0_Memory_expander:
            st.markdown("<h5 style='text-align: left; color:#034ea2; '>GPU0 Memory Analysis</h5>", unsafe_allow_html=True)
            GPU0_memory_plot, GPU0_memory_table = st.columns(2)
            
            with GPU0_memory_plot:  
                GPU0_memory_chart, GPU0_memory_config = custom_functions.generate_histogram(main_df,'GPU0 Mem (%)')
                st.plotly_chart(GPU0_memory_chart,use_container_width=True, config=GPU0_memory_config)
            with GPU0_memory_table:
                GPU0_memory_table_df_percentages = custom_functions.generate_GPU0_memory_table_percentages_df(main_df,x_percentile,'GPU0 Mem (%)')            
                st.table(GPU0_memory_table_df_percentages)

                st.markdown("<p><strong>Total GPU0 Memory Available: "+str(round(main_df['GPU0 Mem Total (MB)'].mean()))+" MB / "+str(round(main_df['GPU0 Mem Total (MB)'].mean()/1024))+" GB</strong></p>", unsafe_allow_html=True)

                GPU0_Memory_table_total_df = custom_functions.generate_GPU0_Memory_table_total_df(main_df,x_percentile,'GPU0 Mem Used (MB)')
                st.table(GPU0_Memory_table_total_df)

        GPU0_Encode_expander = st.expander(label='GPU0 Encode Details')
        with GPU0_Encode_expander:
            st.markdown("<h5 style='text-align: left; color:#034ea2; '>GPU0 Encode Analysis</h5>", unsafe_allow_html=True)
            GPU0_plot, GPU0_table = st.columns(2)        
            with GPU0_plot:  
                GPU0_chart, GPU0_config = custom_functions.generate_histogram(main_df,'GPU0 Encode (%)')
                st.plotly_chart(GPU0_chart,use_container_width=True, config=GPU0_config)
            with GPU0_table:
                GPU0_table_df = custom_functions.generate_GPU0_table_df(main_df,x_percentile,'GPU0 Encode (%)')
                st.table(GPU0_table_df)
        
        GPU0_Decode_expander = st.expander(label='GPU0 Decode Details')
        with GPU0_Decode_expander:
            st.markdown("<h5 style='text-align: left; color:#034ea2; '>GPU0 Decode Analysis</h5>", unsafe_allow_html=True)
            GPU0_plot, GPU0_table = st.columns(2)        
            with GPU0_plot:  
                GPU0_chart, GPU0_config = custom_functions.generate_histogram(main_df,'GPU0 Decode (%)')
                st.plotly_chart(GPU0_chart,use_container_width=True, config=GPU0_config)
            with GPU0_table:
                GPU0_table_df = custom_functions.generate_GPU0_table_df(main_df,x_percentile,'GPU0 Decode (%)')
                st.table(GPU0_table_df)
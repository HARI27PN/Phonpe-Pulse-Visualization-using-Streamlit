import pandas as pd 
import plotly.express as px
import streamlit as st 
import warnings
import pymysql
import plotly.graph_objects as go
from plotly.subplots import make_subplots
warnings.filterwarnings("ignore")
st.set_page_config(layout="wide", initial_sidebar_state="auto")

@st.cache_resource
# Set the background color
def set_background():
    # Add CSS to change the background color
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #371560;
            color: magneta;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
# Call the function to set the background color 6739B7
set_background()

# DATASETS
Data_Aggregated_Transaction_df= pd.read_csv(r'Data_Files/Data_Aggregated_Transaction_Table.csv')
Data_Aggregated_User_Summary_df= pd.read_csv(r'Data_Files/Data_Aggregated_User_Summary_Table.csv')
Data_Aggregated_User_df= pd.read_csv(r'Data_Files/Data_Aggregated_User_Table.csv')
Scatter_Geo_Dataset =  pd.read_csv(r'Data_Files/Data_Map_Districts_Longitude_Latitude.csv')
Coropleth_Dataset =  pd.read_csv(r'Data_Files/Data_Map_IndiaStates_TU.csv')
Data_Map_Transaction_df = pd.read_csv(r'Data_Files/Data_Map_Transaction_Table.csv')
Data_Map_User_Table= pd.read_csv(r'Data_Files/Data_Map_User_Table.csv')
Indian_States= pd.read_csv(r'Data_Files/Longitude_Latitude_State_Table.csv')

st.markdown("<h1 style='text-align: left; font-weight: bold; color: #ffffff; font-size: 55px;'>PhonePe Pulse Visualization Dashboard</h1>", unsafe_allow_html=True)
  
    
# INDIA MAP ANALYSIS
st.write("# :orange[PHONEPE INDIA MAP]")
c1,c2=st.columns(2)
with c1:
    Year = st.selectbox(
            'Select the Year',
            ('2018', '2019', '2020','2021','2022'))
with c2:
    Quarter = st.selectbox(
            'Select the Quarter',
            ('Q1 (Jan-Mar)', 'Q2 (Apr-Jun)', 'Q3 (Jul-Sep)','Q4 (Oct-Dec)'))
year=int(Year)
string_value = Quarter
quarter= int(''.join(filter(str.isdigit, string_value)))
Transaction_scatter_districts=Data_Map_Transaction_df.loc[(Data_Map_Transaction_df['Year'] == year ) & (Data_Map_Transaction_df['Quarter']==quarter) ].copy()
Transaction_Coropleth_States=Transaction_scatter_districts[Transaction_scatter_districts["State"] == "india"]
Transaction_scatter_districts.drop(Transaction_scatter_districts.index[(Transaction_scatter_districts["State"] == "india")],axis=0,inplace=True)
# Dynamic Scattergeo Data Generation
Transaction_scatter_districts = Transaction_scatter_districts.sort_values(by=['Place_Name'], ascending=False)
Scatter_Geo_Dataset = Scatter_Geo_Dataset.sort_values(by=['District'], ascending=False) 
Total_Amount=[]
for i in Transaction_scatter_districts['Total_Amount']:
    Total_Amount.append(i)
Scatter_Geo_Dataset['Total_Amount']=Total_Amount
Total_Transaction=[]
for i in Transaction_scatter_districts['Total_Transactions_count']:
    Total_Transaction.append(i)
Scatter_Geo_Dataset['Total_Transactions']=Total_Transaction
Scatter_Geo_Dataset['Year_Quarter']=str(year)+'-Q'+str(quarter)
# Dynamic Coropleth
Coropleth_Dataset = Coropleth_Dataset.sort_values(by=['state'], ascending=False)
Transaction_Coropleth_States = Transaction_Coropleth_States.sort_values(by=['Place_Name'], ascending=False)
Total_Amount=[]
for i in Transaction_Coropleth_States['Total_Amount']:
    Total_Amount.append(i)
Coropleth_Dataset['Total_Amount']=Total_Amount
Total_Transaction=[]
for i in Transaction_Coropleth_States['Total_Transactions_count']:
    Total_Transaction.append(i)
Coropleth_Dataset['Total_Transactions']=Total_Transaction

# -------------------------------------FIGURE1 INDIA MAP------------------------------------------------------------------
#scatter plotting the states codes 
Indian_States = Indian_States.sort_values(by=['state'], ascending=False)
Indian_States['Registered_Users']=Coropleth_Dataset['Registered_Users']
Indian_States['Total_Amount']=Coropleth_Dataset['Total_Amount']
Indian_States['Total_Transactions']=Coropleth_Dataset['Total_Transactions']
Indian_States['Year_Quarter']=str(year)+'-Q'+str(quarter)
fig=px.scatter_geo(Indian_States,
                    lon=Indian_States['Longitude'],
                    lat=Indian_States['Latitude'],                                
                    text = Indian_States['code'], #It will display district names on map
                    hover_name="state", 
                    hover_data=['Total_Amount',"Total_Transactions","Year_Quarter"],
                    )
fig.update_traces(marker=dict(color="white" ,size=0.3))
fig.update_geos(fitbounds="locations", visible=False,)
    # scatter plotting districts
Scatter_Geo_Dataset['col']=Scatter_Geo_Dataset['Total_Transactions']
fig1=px.scatter_geo(Scatter_Geo_Dataset,
                    lon=Scatter_Geo_Dataset['Longitude'],
                    lat=Scatter_Geo_Dataset['Latitude'],
                    color=Scatter_Geo_Dataset['col'],
                    size=Scatter_Geo_Dataset['Total_Transactions'],     
                    #text = Scatter_Geo_Dataset['District'], #It will display district names on map
                    hover_name="District", 
                    hover_data=["State", "Total_Amount","Total_Transactions","Year_Quarter"],
                    title='District',
                    size_max=22,)
fig1.update_traces(marker=dict(color="forestgreen" ,line_width=1))    #rebeccapurple
#coropleth mapping india
fig_ch = px.choropleth(
                    Coropleth_Dataset,
                    geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
                    featureidkey='properties.ST_NM',                
                    locations='state',
                    color="Total_Transactions",                                       
                    )
fig_ch.update_geos(fitbounds="locations", visible=False,)
#combining districts states and coropleth
fig_ch.add_trace( fig.data[0])
fig_ch.add_trace(fig1.data[0])

colT1,colT2 = st.columns([6,4])
with colT1:
    st.plotly_chart(fig_ch, use_container_width=True)
with colT2:
    st.markdown(
    """
    <div style="color: white;">
    <h3><span style="color: white;">Details of Map:</span></h3>
    <ul>
    <li>The darkness of each state's color represents the total transactions.</li>
    <li>The size of the circles on the map corresponds to the total transactions in each district. The bigger the circle, the higher the transactions.</li>
    <li>Hovering over the data on the map shows details like the total transactions and amount.</li>
    </ul>
    </div>
    """,
    unsafe_allow_html=True
    )

    st.markdown(
    """
    <div style="color: white;">
    <h3><span style="color: white;">Important Observations:</span></h3>
    <ul>
    <li>Users can view PhonePe transactions both statewide and districtwise.</li>
    <li>The map clearly shows which states have the highest transactions during the given year and quarter.</li>
    <li>The map provides a basic understanding of transactions in different districts.</li>
    </ul>
    </div>
    """,
    unsafe_allow_html=True
    )

# -----------------------------------------------FIGURE2 BARGRAPH------------------------------------------------------------------------
st.info('**:red[The bar graph below displays Indian states with the highest PhonePe transactions in increasing order for the same data.]**')
Coropleth_Dataset = Coropleth_Dataset.sort_values(by=['Total_Transactions'])
fig = px.bar(Coropleth_Dataset, x='state', y='Total_Transactions', title=str(year)+" Quarter-"+str(quarter))
fig.update_layout(title_font=dict(size=27, color='blue'))
st.plotly_chart(fig, use_container_width=True)


# TRANSACTIONS ANALYSIS

st.write('# :orange[TRANSACTIONS ANALYSIS]')
tab1, tab2, tab3, tab4 = st.tabs(["STATE ANALYSIS", "DISTRICT ANALYSIS", "YEAR ANALYSIS", "OVERALL ANALYSIS"])
# === T FIGURE1 STATE ANALYSIS ===
with tab1:
    Data_Aggregated_Transaction=Data_Aggregated_Transaction_df.copy()
    Data_Aggregated_Transaction.drop(Data_Aggregated_Transaction.index[(Data_Aggregated_Transaction["State"] == "india")],axis=0,inplace=True)
    State_PaymentMode=Data_Aggregated_Transaction.copy()
    # st.write('### :white[State & PaymentMode]')
    col1, col2= st.columns(2)
    with col1:
        mode = st.selectbox(
            'Please select the Mode',
            ('Recharge & bill payments', 'Peer-to-peer payments', 'Merchant payments', 'Financial Services','Others'),key='a')
    with col2:
        state = st.selectbox(
        'Please select the State',
        ('andaman-&-nicobar-islands', 'andhra-pradesh', 'arunachal-pradesh',
        'assam', 'bihar', 'chandigarh', 'chhattisgarh',
        'dadra-&-nagar-haveli-&-daman-&-diu', 'delhi', 'goa', 'gujarat',
        'haryana', 'himachal-pradesh', 'jammu-&-kashmir',
        'jharkhand', 'karnataka', 'kerala', 'ladakh', 'lakshadweep',
        'madhya-pradesh', 'maharashtra', 'manipur', 'meghalaya', 'mizoram',
        'nagaland', 'odisha', 'puducherry', 'punjab', 'rajasthan',
        'sikkim', 'tamil-nadu', 'telangana', 'tripura', 'uttar-pradesh',
        'uttarakhand', 'west-bengal'),key='b')
    State= state
    Year_List=[2018,2019,2020,2021,2022]
    Mode=mode
    State_PaymentMode=State_PaymentMode.loc[(State_PaymentMode['State'] == State ) & (State_PaymentMode['Year'].isin(Year_List)) & 
                            (State_PaymentMode['Payment_Mode']==Mode )]
    State_PaymentMode = State_PaymentMode.sort_values(by=['Year'])
    State_PaymentMode["Quarter"] = "Q"+State_PaymentMode['Quarter'].astype(str)
    State_PaymentMode["Year_Quarter"] = State_PaymentMode['Year'].astype(str) +"-"+ State_PaymentMode["Quarter"].astype(str)
    fig = px.bar(State_PaymentMode, x='Year_Quarter', y='Total_Transactions_count',color="Total_Transactions_count",
                 color_continuous_scale="Viridis")
    
    colT1,colT2 = st.columns([6,4])
    with colT1:
        st.write('#### '+State.upper()) 
        st.plotly_chart(fig,use_container_width=True)
    with colT2:
        st.markdown(
        """
        <div style="color: white;">
        <h3><span style="color: white;"> Details of BarGraph:</span></h3>
        <ul>
        <li>The data pertains to a specific state selected by you.</li>
        <li>The X axis represents all years with all quarters.</li>
        <li>The Y axis represents the total transactions in the selected mode.</li>     
        </ul>
        </div>
        """,
        unsafe_allow_html=True
        )
        st.markdown(
        """
        <div style="color: white;">
        <h3><span style="color: white;"> Important Observations:</span></h3>
        <ul>
        <li>The data visualizes the pattern of payment modes in a state over time.</li>
        <li>Users can analyze the Y-axis data to understand which modes of payments are increasing or decreasing in the state. An upward trend in the Y-axis data for a particular payment mode indicates an increase in usage. A downward trend in the Y-axis data for a particular payment mode indicates a decrease in usage.</li>
        <li>Observing these patterns over time can provide insights into the changing payment behavior of people in the state.</li>
        </ul>
        </div>
        """,
        unsafe_allow_html=True
        )
# === T FIGURE2 DISTRICTS ANALYSIS ===
with tab2:
    col1, col2, col3= st.columns(3)
    with col1:
        Year = st.selectbox(
            'Please select the Year',
            ('2018', '2019', '2020','2021','2022'),key='y1')
    with col2:
        state = st.selectbox(
        'Please select the State',
        ('andaman-&-nicobar-islands', 'andhra-pradesh', 'arunachal-pradesh',
        'assam', 'bihar', 'chandigarh', 'chhattisgarh',
        'dadra-&-nagar-haveli-&-daman-&-diu', 'delhi', 'goa', 'gujarat',
        'haryana', 'himachal-pradesh', 'jammu-&-kashmir',
        'jharkhand', 'karnataka', 'kerala', 'ladakh', 'lakshadweep',
        'madhya-pradesh', 'maharashtra', 'manipur', 'meghalaya', 'mizoram',
        'nagaland', 'odisha', 'puducherry', 'punjab', 'rajasthan',
        'sikkim', 'tamil-nadu', 'telangana', 'tripura', 'uttar-pradesh',
        'uttarakhand', 'west-bengal'),key='dk')
    with col3:
        Quarter = st.selectbox(
            'Please select the Quarter',
            ('1', '2', '3','4'),key='qwe')
    districts=Data_Map_Transaction_df.loc[(Data_Map_Transaction_df['State'] == state ) & (Data_Map_Transaction_df['Year']==int(Year))
                                          & (Data_Map_Transaction_df['Quarter']==int(Quarter))]
    l=len(districts)    
    fig = px.bar(districts, x='Place_Name', y='Total_Transactions_count',color="Total_Transactions_count",
                 color_continuous_scale="Viridis")   
    colT1,colT2 = st.columns([6,4])
    with colT1:
        st.write('#### '+state.upper()+' WITH '+str(l)+' DISTRICTS')
        st.plotly_chart(fig,use_container_width=True)
    with colT2:
        st.markdown(
        """
        <div style="color: white;">
        <h3><span style="color: white;"> Details of BarGraph:</span></h3>
        <ul>
        <li>This entire data belongs to state selected by you</li>
        <li>X Axis represents the districts of selected state</li>
        <li>Y Axis represents total transactions </li>    
        </ul>
        </div>
        """,
        unsafe_allow_html=True
        )
        st.markdown(
        """
        <div style="color: white;">
        <h3><span style="color: white;"> Important Observations:</span></h3>
        <ul>
        <li>User can observe how transactions are happening in districts of a selected state </li>
        <li>We can observe the leading distric in a state </li>
        </ul>
        </div>
        """,
        unsafe_allow_html=True
        )
# === T FIGURE3 YEAR ANALYSIS ===
with tab3:
    #st.write('### :white[PaymentMode and Year]')
    col1, col2= st.columns(2)
    with col1:
        M = st.selectbox(
            'Please select the Mode',
            ('Recharge & bill payments', 'Peer-to-peer payments', 'Merchant payments', 'Financial Services','Others'),key='D')
    with col2:
        Y = st.selectbox(
        'Please select the Year',
        ('2018', '2019', '2020','2021','2022'),key='F')
    Year_PaymentMode=Data_Aggregated_Transaction.copy()
    Year=int(Y)
    Mode=M
    Year_PaymentMode=Year_PaymentMode.loc[(Year_PaymentMode['Year']==Year) & 
                            (Year_PaymentMode['Payment_Mode']==Mode )]
    States_List=Year_PaymentMode['State'].unique()
    State_groupby_YP=Year_PaymentMode.groupby('State')
    Year_PaymentMode_Table=State_groupby_YP.sum()
    Year_PaymentMode_Table['states']=States_List
    del Year_PaymentMode_Table['Quarter'] # ylgnbu', 'ylorbr', 'ylorrd teal
    del Year_PaymentMode_Table['Year']
    Year_PaymentMode_Table = Year_PaymentMode_Table.sort_values(by=['Total_Transactions_count'])
    fig2= px.bar(Year_PaymentMode_Table, x='states', y='Total_Transactions_count',color="Total_Transactions_count",
                color_continuous_scale="Viridis",)   
    colT1,colT2 = st.columns([6,4])
    with colT1:
        st.write('#### '+str(Year)+' DATA ANALYSIS')
        st.plotly_chart(fig2,use_container_width=True) 
    with colT2:
        st.markdown(
        """
        <div style="color: white;">
        <h3><span style="color: white;"> Details of BarGraph:</span></h3>
        <ul>
        <li>This entire data belongs to selected Year</li>
        <li>X Axis is all the states in increasing order of Total transactions</li>
        <li>Y Axis represents total transactions in selected mode</li>
        </ul>
        </div>
        """,
        unsafe_allow_html=True
        )
        st.markdown(
        """
        <div style="color: white;">
        <h3><span style="color: white;"> Important Observations:</span></h3>
        <ul>
        <li>We can observe the leading state with highest transactions in particular mode</li>
        <li>We get basic idea about regional performance of Phonepe</li>
        <li>Depending on the regional performance Phonepe can provide offers to particular place</li>
        </ul>
        </div>
        """,
        unsafe_allow_html=True
        )
# === FIGURE4 OVERALL ANALYSIS ===
with tab4:    
    years=Data_Aggregated_Transaction.groupby('Year')
    years_List=Data_Aggregated_Transaction['Year'].unique()
    years_Table=years.sum()
    del years_Table['Quarter']
    years_Table['year']=years_List
    total_trans=years_Table['Total_Transactions_count'].sum() # this data is used in sidebar    
    fig1 = px.pie(years_Table, values='Total_Transactions_count', names='year',color_discrete_sequence=px.colors.sequential.Viridis, title='TOTAL TRANSACTIONS (2018 TO 2022)')
    col1, col2= st.columns([0.6,0.4])
    with col1:
        st.write('### :green[Drastical Increase in Transactions :rocket:]')
        st.plotly_chart(fig1)
    with col2:  
        st.write('#### :green[Year Wise Transaction Analysis in INDIA]')      
        st.markdown(years_Table.style.hide(axis="index").to_html(), unsafe_allow_html=True)
        st.markdown(
        """
        <div style="color: white;">
        <h3><span style="color: white;"> Important Observations:</span></h3>
        <ul>
        <li>Its very clearly understood that online transactions drasticall increased</li>
        <li>Initially in 2018,2019 the transactions are less but with time the online payments are increased at a high scale via PhonePe.</li>
        <li>We can clearly see that more than 50% of total Phonepe transactions in india happened are from the year 2022</li>
        </ul>
        </div>
        """,
        unsafe_allow_html=True
        )

        
# USER ANALYSIS

st.write('# :orange[USERS DATA ANALYSIS ]')
tab1, tab2, tab3, tab4 = st.tabs(["STATE ANALYSIS", "DISTRICT ANALYSIS","YEAR ANALYSIS","OVERALL ANALYSIS"])

# === U STATE ANALYSIS ===
with tab1:
    st.write('### :blue[State & Userbase]')
    state = st.selectbox(
        'Please select the State',
        ('andaman-&-nicobar-islands', 'andhra-pradesh', 'arunachal-pradesh',
        'assam', 'bihar', 'chandigarh', 'chhattisgarh',
        'dadra-&-nagar-haveli-&-daman-&-diu', 'delhi', 'goa', 'gujarat',
        'haryana', 'himachal-pradesh', 'jammu-&-kashmir',
        'jharkhand', 'karnataka', 'kerala', 'ladakh', 'lakshadweep',
        'madhya-pradesh', 'maharashtra', 'manipur', 'meghalaya', 'mizoram',
        'nagaland', 'odisha', 'puducherry', 'punjab', 'rajasthan',
        'sikkim', 'tamil-nadu', 'telangana', 'tripura', 'uttar-pradesh',
        'uttarakhand', 'west-bengal'),key='W')
    app_opening=Data_Aggregated_User_Summary_df.groupby(['State','Year'])
    a_state=app_opening.sum()
    la=Data_Aggregated_User_Summary_df['State'] +"-"+ Data_Aggregated_User_Summary_df["Year"].astype(str)
    a_state["state_year"] = la.unique()
    sta=a_state["state_year"].str[:-5]
    a_state["state"] = sta
    sout=a_state.loc[(a_state['state'] == state) ]
    ta=sout['AppOpenings'].sum()
    tr=sout['Registered_Users'].sum()
    sout['AppOpenings']=sout['AppOpenings'].mul(100/ta)
    sout['Registered_Users']=sout['Registered_Users'].mul(100/tr).copy()
    fig = go.Figure(data=[
        go.Bar(name='AppOpenings %', y=sout['AppOpenings'], x=sout['state_year'], marker={'color': 'pink'}),
        go.Bar(name='Registered Users %', y=sout['Registered_Users'], x=sout['state_year'],marker={'color': 'orange'})
    ])
    # Change the bar mode
    fig.update_layout(barmode='group')
    colT1,colT2 = st.columns([6,4])
    with colT1:
        st.write("#### ",state.upper())
        st.plotly_chart(fig, use_container_width=True, height=200)
    with colT2:
        st.markdown(
        """
        <div style="color: white;">
        <h3><span style="color: white;"> Details of BarGraph:</span></h3>
        <ul>
        <li>user need to select a state </li>
        <li>The X Axis shows both Registered users and App openings </li>
        <li>The Y Axis shows the Percentage of Registered users and App openings</li>
        </ul>
        </div>
        """,
        unsafe_allow_html=True
        )
        st.markdown(
        """
        <div style="color: white;">
        <h3><span style="color: white;"> Important Observations:</span></h3>
        <ul>
        <li>User can observe how the App Openings are growing and how Registered users are growing in a state</li>
        <li>We can clearly obseve these two parameters with time</li>
        <li>one can observe how user base is growing</li>
        </ul>
        </div>
        """,
        unsafe_allow_html=True
        )
# === U DISTRICT ANALYSIS ===
with tab2:
    col1, col2, col3= st.columns(3)
    with col1:
        Year = st.selectbox(
            'Please select the Year',
            ('2022', '2021','2020','2019','2018'),key='y12')
    with col2:
        state = st.selectbox(
        'Please select the State',
        ('andaman-&-nicobar-islands', 'andhra-pradesh', 'arunachal-pradesh',
        'assam', 'bihar', 'chandigarh', 'chhattisgarh',
        'dadra-&-nagar-haveli-&-daman-&-diu', 'delhi', 'goa', 'gujarat',
        'haryana', 'himachal-pradesh', 'jammu-&-kashmir',
        'jharkhand', 'karnataka', 'kerala', 'ladakh', 'lakshadweep',
        'madhya-pradesh', 'maharashtra', 'manipur', 'meghalaya', 'mizoram',
        'nagaland', 'odisha', 'puducherry', 'punjab', 'rajasthan',
        'sikkim', 'tamil-nadu', 'telangana', 'tripura', 'uttar-pradesh',
        'uttarakhand', 'west-bengal'),key='dk2')
    with col3:
        Quarter = st.selectbox(
            'Please select the Quarter',
            ('1', '2', '3','4'),key='qwe2')
    districts=Data_Map_User_Table.loc[(Data_Map_User_Table['State'] == state ) & (Data_Map_User_Table['Year']==int(Year))
                                          & (Data_Map_User_Table['Quarter']==int(Quarter))]
    l=len(districts)    
    fig = px.bar(districts, x='Place_Name', y='App_Openings',color="App_Openings",
                 color_continuous_scale="reds")   
    colT1,colT2 = st.columns([6,4])
    with colT1:
        if l:
            st.write('#### '+state.upper()+' WITH '+str(l)+' DISTRICTS')
            st.plotly_chart(fig,use_container_width=True)
        else:
            st.write('#### NO DISTRICTS DATA AVAILABLE FOR '+state.upper())

    with colT2:
        if l:
            st.markdown(
            """
            <div style="color: white;">
            <h3><span style="color: white;"> Details of BarGraph:</span></h3>
            <ul>
            <li>This entire data belongs to state selected by you</li>
            <li>X Axis represents the districts of selected state</li>
            <li>Y Axis represents App Openings</li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True
            )
            st.markdown(
            """
            <div style="color: white;">
            <h3><span style="color: white;"> Important Observations:</span></h3>
            <ul>
            <li>User can observe how App Openings are happening in districts of a selected state </li>
            <li>We can observe the leading distric in a state </li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True
            )
# === U YEAR ANALYSIS ===
with tab3:
    st.write('### :orange[Brand Share] ')
    col1, col2= st.columns(2)
    with col1:
        state = st.selectbox(
        'Please select the State',
        ('india','andaman-&-nicobar-islands', 'andhra-pradesh', 'arunachal-pradesh',
        'assam', 'bihar', 'chandigarh', 'chhattisgarh',
        'dadra-&-nagar-haveli-&-daman-&-diu', 'delhi', 'goa', 'gujarat',
        'haryana', 'himachal-pradesh', 'jammu-&-kashmir',
        'jharkhand', 'karnataka', 'kerala', 'ladakh', 'lakshadweep',
        'madhya-pradesh', 'maharashtra', 'manipur', 'meghalaya', 'mizoram',
        'nagaland', 'odisha', 'puducherry', 'punjab', 'rajasthan',
        'sikkim', 'tamil-nadu', 'telangana', 'tripura', 'uttar-pradesh',
        'uttarakhand', 'west-bengal'),key='Z')
    with col2:
        Y = st.selectbox(
        'Please select the Year',
        ('2018', '2019', '2020','2021','2022'),key='X')
    y=int(Y)
    s=state
    brand=Data_Aggregated_User_df[Data_Aggregated_User_df['Year']==y] 
    brand=Data_Aggregated_User_df.loc[(Data_Aggregated_User_df['Year'] == y) & (Data_Aggregated_User_df['State'] ==s)]
    myb= brand['Brand_Name'].unique()
    x = sorted(myb).copy()
    b=brand.groupby('Brand_Name').sum()
    b['brand']=x
    br=b['Registered_Users_Count'].sum()
    labels = b['brand']
    values = b['Registered_Users_Count'] # customdata=labels,
    fig3 = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.4,textinfo='label+percent',texttemplate='%{label}<br>%{percent:1%f}',insidetextorientation='horizontal',textfont=dict(color='#000000'),marker_colors=px.colors.qualitative.Prism)])
    
    colT1,colT2 = st.columns([6,4])
    with colT1:
        st.write("#### ",state.upper()+' IN '+Y)
        st.plotly_chart(fig3, use_container_width=True)        
    with colT2:
        st.markdown(
        """
        <div style="color: white;">
        <h3><span style="color: white;"> Details of Donut Chart: </span></h3>   
        <ul>
        <li>Initially we select data by means of State and Year</li>
        <li>Percentage of registered users is represented with dounut chat through Device Brand</li>
        </ul>
        </div>
        """,
        unsafe_allow_html=True
        )
        st.markdown(
        """
        <div style="color: white;">
        <h3><span style="color: white;"> Important Observations:</span></h3>
        <ul>
        <li>User can observe the top leading brands in a particular state</li>
        <li>Brands with less users</li>
        <li>Brands with high users</li>
        <li>Can make app download advices to growing brands</li>
        </ul>
        </div>
        """,
        unsafe_allow_html=True
        )

    b = b.sort_values(by=['Registered_Users_Count'])
    fig4= px.bar(b, x='brand', y='Registered_Users_Count',color="Registered_Users_Count",
                title='In '+state+'in '+str(y),
                color_continuous_scale="oranges",)
    with st.expander("See Bar graph for the same data"):
        st.plotly_chart(fig4,use_container_width=True) 
        
# === U OVERALL ANALYSIS ===
    with tab4:
        years=Data_Aggregated_User_Summary_df.groupby('Year')
        years_List=Data_Aggregated_User_Summary_df['Year'].unique()
        years_Table=years.sum()
        del years_Table['Quarter']
        years_Table['year']=years_List
        total_trans=years_Table['Registered_Users'].sum() # this data is used in sidebar    
        fig1 = px.pie(years_Table, values='Registered_Users', names='year',color_discrete_sequence=px.colors.sequential.RdBu, title='TOTAL REGISTERED USERS (2018 TO 2022)')
        col1, col2= st.columns([0.6,0.4])
        with col1:
            # st.write('### :green[Drastical Increase in Transactions :rocket:]')
            labels = ["US", "China", "European Union", "Russian Federation", "Brazil", "India",
                "Rest of World"]

            # Create subplots: use 'domain' type for Pie subplot
            fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]])
            fig.add_trace(go.Pie(labels=years_Table['year'], values=years_Table['Registered_Users'], name="REGISTERED USERS"),
                        1, 1)
            fig.add_trace(go.Pie(labels=years_Table['year'], values=years_Table['AppOpenings'], name="APP OPENINGS"),
                        1, 2)

            # Use `hole` to create a donut-like pie chart
            fig.update_traces(hole=.6, hoverinfo="label+percent+name")

            fig.update_layout(
                title_text="USERS DATA (2018 TO 2022)",
                # Add annotations in the center of the donut pies.
                annotations=[dict(text='USERS', x=0.18, y=0.5, font_size=20, showarrow=False),
                            dict(text='APP', x=0.82, y=0.5, font_size=20, showarrow=False)])
            # st.plotly_chart(fig1)
            st.plotly_chart(fig)
        with col2:  
            # st.write('#### :green[Year Wise Transaction Analysis in INDIA]')      
            st.markdown(years_Table.style.hide(axis="index").to_html(), unsafe_allow_html=True)
            st.markdown(
            """
            <div style="color: white;">
            <h3><span style="color: white;"> Important Observations:</span></h3>
            <ul>
            <li>We can see that the Registered Users and App openings are increasing year by year</li>
            </ul>
            </div>
            """,
            unsafe_allow_html=True
            )

            
# TOP 3 STATES DATA

st.write('# :orange[TOP 5 STATE-WISE DATA]')
c1,c2=st.columns(2)
with c1:
    Year = st.selectbox(
            'Please select the Year',
            ('2022', '2021','2020','2019','2018'),key='y1h2k')
with c2:
    Quarter = st.selectbox(
            'Please select the Quarter',
            ('1', '2', '3','4'),key='qgwe2')
Data_Map_User_df=Data_Aggregated_User_Summary_df.copy() 
top_states=Data_Map_User_df.loc[(Data_Map_User_df['Year'] == int(Year)) & (Data_Map_User_df['Quarter'] ==int(Quarter))]
top_states_r = top_states.sort_values(by=['Registered_Users'], ascending=False)
top_states_a = top_states.sort_values(by=['AppOpenings'], ascending=False) 

top_states_T=Data_Aggregated_Transaction_df.loc[(Data_Aggregated_Transaction_df['Year'] == int(Year)) & (Data_Aggregated_Transaction_df['Quarter'] ==int(Quarter))]
topst=top_states_T.groupby('State')
x=topst.sum().sort_values(by=['Total_Transactions_count'], ascending=False)
y=topst.sum().sort_values(by=['Total_Amount'], ascending=False)

col1, col2, col3, col4= st.columns([2.5,2.5,2.5,2.5])
# Style for the tables
table_style = '''
    <style>
    table {
        border-collapse: collapse;
        width: 100%;
    }
    th, td {
        background-color: #ffffff;
        text-align: left;
        padding: 8px;
        border-bottom: 1px solid #ddd;
        font-family: Arial, sans-serif;
        font-size: 12px;
    }
    th {
        background-color: #ffffff;
        font-weight: bold;
    }
    </style>
'''
# Displaying the tables with the updated style
with col1:
    rt = top_states_r[1:6]
    st.markdown("#### :blue[Registered Users]")
    st.markdown(table_style, unsafe_allow_html=True)
    st.markdown(rt[['State', 'Registered_Users']].style.hide_index().render(), unsafe_allow_html=True)
with col2:
    at = top_states_a[1:6]
    st.markdown("#### :blue[PhonePe App Openings]")
    st.markdown(table_style, unsafe_allow_html=True)
    st.markdown(at[['State', 'AppOpenings']].style.hide_index().render(), unsafe_allow_html=True)
with col3:
    st.markdown("#### :blue[Total Transactions]")
    st.markdown(table_style, unsafe_allow_html=True)
    st.write(x[['Total_Transactions_count']][1:6])
with col4:
    st.markdown("#### :blue[Total Amount]")
    st.markdown(table_style, unsafe_allow_html=True)
    st.write(y['Total_Amount'][1:6])

    
# Getting Secrets from Streamlit Secret File
# username=st.secrets['AWS_RDS_username']
# password=st.secrets['AWS_RDS_password']
# Endpoint=st.secrets['Endpoint']

# # CONNECTED TO (AWS)Amazon-Web-Services ----> (RDS)Relational-Database-Service 
# conn=pymysql.connect(
#     host=Endpoint,
#     user=username,
#     password=password
# )

# # USING PhonepeDB I HAVE CREATED IN DATABASE-INSTANCE OF RDS
# mycursor=conn.cursor()
# sql='''USE PhonepeDB'''
# mycursor.execute(sql)

# # RETRIEVING DATA FROM CLOUD DATABASE
# query = 'select * from Longitude_Latitude_State_Table'
# Indian_States = pd.read_sql(query, con = conn)

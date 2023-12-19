import streamlit as st
from streamlit_option_menu import option_menu
import plotly.express as px
import pandas as pd
import os
from PIL import Image
import warnings
import pymongo

#warnings.filterwarnings('ignore')

# SETTING PAGE CONFIGURATIONS
icon = Image.open("airbnb.png")
st.set_page_config(page_title= "AirBnb-Analysis",
                   page_icon= icon,
                   layout= "wide",
                   initial_sidebar_state= "expanded"
                   )
st.markdown("<h1 style='text-align: center; color: black;'>Airbnb Analysis</h1>", unsafe_allow_html=True)

selected = option_menu(
        menu_title=None,
        options=["Home", "Explore Data"],
        icons=["house", "bar-chart"],
        default_index=0,
        orientation="horizontal",
        styles={"nav-link": {"font-size": "20px", "text-align": "center", "margin": "-2px", "--hover-color": "#F56464"},
                "nav-link-selected": {"background-color": "#F56464"}})

#Home#

if selected == "Home":
    col1,col2 = st.columns([3,2],gap="medium")
    with col1:
# Set font size using HTML-style tags
        st.markdown("<h2 style='color:red;font-size:20px;'>Technologies Used</h2>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:18px;'>Python, MongoDB, Streamlit, Plotly Express, Pandas</p>", unsafe_allow_html=True)
        st.markdown("<h2 style='color:red;font-size:20px;'>Overview</h2>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:18px;'> This Airbnb analysis app provides users with interactive geospatial maps to explore the distribution of listings, insights into pricing dynamics based on location and season, a visual overview of property ratings, occupancy patterns, and detailed information on specific regions, all presented through dynamic visualizations and a comprehensive dashboard for informed decision-making.</p>", unsafe_allow_html=True)
        st.markdown("<h2 style='color:red;font-size:20px;'>Domain</h2>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:18px;'>Travel Industry, Property Management, and Tourism</p>", unsafe_allow_html=True)

    with col2:
      with col2:
        image = Image.open("air_img.png")
        st.image(image, caption='Airbnb', use_column_width=True)

#Bridging a connection with MongoDB Atlas and Creating a new database(youtube_data)
client = pymongo.MongoClient("mongodb+srv://gnanambigai:gnanambigai@cluster0.g6y23xg.mongodb.net/")
db = client.Airbnb

if selected == "Explore Data":
    df=pd.DataFrame(db.Airbnb_data.find())
    st.sidebar.header("Choose your filter: ")
# Create for neighbourhood_group
    neighbourhood_group = st.sidebar.multiselect("Pick your neighbourhood group", df["neighbourhood_group"].unique())
    if not neighbourhood_group:
        df2 = df.copy()
    else:
        df2 = df[df["neighbourhood_group"].isin(neighbourhood_group)]

    # Create for neighbourhood
    neighbourhood = st.sidebar.multiselect("Pick the neighbourhood", df2["neighbourhood"].unique())
    if not neighbourhood:
        df3 = df2.copy()
    else:
        df3 = df2[df2["neighbourhood"].isin(neighbourhood)]
 # Filter the data based on neighbourhood_group, neighbourhood

    if not neighbourhood_group and not neighbourhood:
        filtered_df = df
    elif not neighbourhood:
        filtered_df = df[df["neighbourhood_group"].isin(neighbourhood_group)]
    elif not neighbourhood_group:
        filtered_df = df[df["neighbourhood"].isin(neighbourhood)]
    elif neighbourhood:
        filtered_df = df3[df["neighbourhood"].isin(neighbourhood)]
    elif neighbourhood_group:
        filtered_df = df3[df["neighbourhood_group"].isin(neighbourhood_group)]
    elif neighbourhood_group and neighbourhood:
        filtered_df = df3[df["neighbourhood_group"].isin(neighbourhood_group) & df3["neighbourhood"].isin(neighbourhood)]
    else:
        filtered_df = df3[df3["neighbourhood_group"].isin(neighbourhood_group) & df3["neighbourhood"].isin(neighbourhood)]

    room_type_df = filtered_df.groupby(by=["room_type"], as_index=False)["price"].sum()
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Price By Room Type")
        fig = px.bar(room_type_df, x="room_type", y="price", text=['${:,.2f}'.format(x) for x in room_type_df["price"]],
                    template="seaborn")
        st.plotly_chart(fig, use_container_width=True, height=200)

    with col2:
        st.subheader("Price By Neighbourhood Group")
        fig = px.pie(filtered_df, values="price", names="neighbourhood_group", hole=0.5)
        fig.update_traces(text=filtered_df["neighbourhood_group"], textposition="outside")
        st.plotly_chart(fig, use_container_width=True)
        
    cl1, cl2 = st.columns((2))
    with cl1:
        with st.expander("Room Type Wise Price"):
            st.write(room_type_df.style.background_gradient(cmap="Blues"))
            csv = room_type_df.to_csv(index=False).encode('utf-8')
            st.download_button("Download Data", data=csv, file_name="room_type.csv", mime="text/csv",
                            help='Click here to download the data as a CSV file')

    with cl2:
        with st.expander("Neighbourhood Group Wise Price"):
            neighbourhood_group = filtered_df.groupby(by="neighbourhood_group", as_index=False)["price"].sum()
            st.write(neighbourhood_group.style.background_gradient(cmap="Oranges"))
            csv = neighbourhood_group.to_csv(index=False).encode('utf-8')
            st.download_button("Download Data", data=csv, file_name="neighbourhood_group.csv", mime="text/csv",
                            help='Click here to download the data as a CSV file')

    # Create a scatter plot
    data1 = px.scatter(filtered_df, x="neighbourhood_group", y="neighbourhood", color="room_type")
    data1['layout'].update(title="Room Type in the Neighbourhood and Neighbourhood Group",
                            titlefont=dict(size=20), xaxis=dict(title="Neighbourhood_Group", titlefont=dict(size=20)),
                            yaxis=dict(title="Neighbourhood", titlefont=dict(size=20)))
    st.plotly_chart(data1, use_container_width=True)

    with st.expander("Room Availability and Price Details"):
        st.write(filtered_df.iloc[:500, 1:20:2].style.background_gradient(cmap="Oranges"))

    # Download orginal DataSet
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button('Download Data', data=csv, file_name="Data.csv", mime="text/csv")

    import plotly.figure_factory as ff

    st.subheader(":point_right: Neighbourhood group wise Room type and Minimum stay nights")
    with st.expander("Summary_Table"):
        df_sample = df[0:5][["neighbourhood_group", "neighbourhood", "reviews_per_month", "room_type", "price", "minimum_nights", "host_name"]]
        fig = ff.create_table(df_sample, colorscale="Cividis")
        st.plotly_chart(fig, use_container_width=True)

    # map function for room_type

    # If your DataFrame has columns 'Latitude' and 'Longitude':
    st.subheader("Airbnb Analysis in Map view")
    df = df.rename(columns={"Latitude": "lat", "Longitude": "lon"})

    st.map(df)




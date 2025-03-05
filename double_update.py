import streamlit as st, pandas as pd, numpy as np, plotly.graph_objects as go
from dateutil.relativedelta import relativedelta

#below set the page to wide format, much easier to view things
st.set_page_config(layout="wide")
# st.image('Logo.png',width=500)
#this caches the data so each interaction doesnt require reloading the data set
@st.cache_data
def load_data():
    df = pd.read_csv('https://github.com/es42289/DeclineCurveAnalysis/raw/master/MB_latest_prd%20Producing%20Entity%20Monthly%20Production.CSV')
    return df
@st.cache_data
def load_data2():
	df_params=pd.read_csv('https://raw.githubusercontent.com/es42289/DeclineCurveAnalysis/master/MB_DCA_parameters_per_Well.csv')
	return df_params
@st.cache_data
def load_data3():
	df_headers=pd.read_csv('https://github.com/es42289/DeclineCurveAnalysis/raw/master/MB_latest_prd%20Production%20Headers.CSV')
	return df_headers

#This is Arps equation turned into a function
def dca(t,qi,b,d):
    if b==0:
        return qi*np.exp(-1*d*t) #exponential
    elif b==1:
        return qi/(1+d*t) #harmonic
    elif b>=1:
        return 0 #limiting b to values equal to or less than 1
    else:
        return qi*((1+b*d*t)**(-1/b)) #exponential    

#load in the data cache
df = load_data() 
df_params=load_data2()
df_headers=load_data3()
# df=df.groupby('Monthly Production Date').sum()

#The main program is within here
def main(): 
	page = st.sidebar.selectbox("Choose a page", [ "Individual Wells","Field Map"])#"Full Field",
	if page == "Full Field":
		#give a title to the page that is the well name
		st.header('Full Field Production')
		st.text('*This project has been stripped of proprietary data/logos etc from the original project*')
		st.text('This app was created from scratch by Elii Skeans using python and Streamlit')
		
		#subset the data to only use singel well data
		df_sub=df.groupby('Monthly Production Date').sum().reset_index()
		df_sub['Monthly Production Date']=pd.to_datetime(df_sub['Monthly Production Date'])
		df_sub=df_sub[df_sub['Monthly Production Date']>'1/1/2000']
		
		#set three columns for high -low-mid cases
		cols = st.columns(3)
		
		#first column is the P50 case
		cols[0].write("Mid Case (P50)")
		Di50 = float(cols[0].text_input("Decline Rate, 1/year", 0.12))
		Qi50 = cols[0].text_input('Initial Rate, bbl/month',185000)
		Qi50 = float(Qi50)
		b50 = cols[0].text_input('b-factor',0.5)
		b50 = float(b50)
		
		#second column is the P90 case
		cols[1].write("Low Case (P90)")
		Di90 = float(cols[1].text_input("P90 Decline Rate, 1/year", 0.12))
		Qi90 = cols[1].text_input('P90 Initial Rate, bbl/month',185000)
		Qi90 = float(Qi90)
		b90 = cols[1].text_input('P90 b-factor',0)
		b90 = float(b90)
		
		#third column is the P10 case
		cols[2].write("High Case (P10)")
		Di10 = float(cols[2].text_input("P10 Decline Rate, 1/year", 0.12))
		Qi10 = cols[2].text_input('P10 Initial Rate, bbl/month',185000)
		Qi10 = float(Qi10)
		b10 = cols[2].text_input('P10 b-factor',1)
		b10 = float(b10)
		
		df_dca=pd.DataFrame({'Months':list(range(-48,173))})
		df_dca['Qcalc_50']=dca(df_dca['Months'],Qi50,b50,Di50/12)
		df_dca['Qcalc_90']=dca(df_dca['Months'],Qi90,b90,Di90/12)
		df_dca['Qcalc_10']=dca(df_dca['Months'],Qi10,b10,Di10/12)
		
		dates=[]
		for month in df_dca.Months:
			dates.append(pd.to_datetime(df_sub['Monthly Production Date'][-1:].values[0])+relativedelta(months=+month))
		df_dca['Date']=dates

		# df_sub=df_sub[df_sub['Monthly Production Date']>pd.to_datetime('1/1/2016')]
		cols=st.columns(2)
		if cols[0].button('Zoom In'):
			df_sub=df_sub[df_sub['Monthly Production Date']>pd.to_datetime('1/1/2016')]
		else:
			pass
		if cols[1].button('Zoom Out'):
			df_sub=df.groupby('Monthly Production Date').sum().reset_index()
			df_sub['Monthly Production Date']=pd.to_datetime(df_sub['Monthly Production Date'])
		else:
			pass
		df_dca_yr=df_dca.groupby(df_dca.Date.dt.year).sum()
		df_sub_yr=df_sub.groupby(df_sub['Monthly Production Date'].dt.year).sum()
		
		fig=go.Figure()
		fig.add_trace(go.Scatter(marker_color='green',name='History',mode='markers',x=df_sub['Monthly Production Date'],y=df_sub['Monthly Oil']))
		fig.add_trace(go.Scatter(name='P50',x=df_dca['Date'],y=df_dca['Qcalc_50']))
		fig.add_trace(go.Scatter(name='P90',x=df_dca['Date'],y=df_dca['Qcalc_90']))
		fig.add_trace(go.Scatter(name='P10',x=df_dca['Date'],y=df_dca['Qcalc_10']))
		fig.add_trace(go.Scatter(name='Historic Yearly Average',x=df_sub_yr.index,y=df_sub_yr['Monthly Oil'][:-1]/12))
		fig.update_yaxes(type="log")
		fig.update_layout(title='Log Scale',yaxis_title='Monthly Oil, bbl')
		
		fig2=go.Figure()
		fig2.add_trace(go.Scatter(marker_color='green',name='History',mode='markers',x=df_sub['Monthly Production Date'],y=df_sub['Monthly Oil']))
		fig2.add_trace(go.Scatter(name='P50',x=df_dca['Date'],y=df_dca['Qcalc_50']))
		fig2.add_trace(go.Scatter(name='P90',x=df_dca['Date'],y=df_dca['Qcalc_90']))
		fig2.add_trace(go.Scatter(name='P10',x=df_dca['Date'],y=df_dca['Qcalc_10']))
		fig2.add_trace(go.Scatter(name='Historic Yearly Average',x=df_sub_yr.index,y=df_sub_yr['Monthly Oil'][:-1]/12))
		fig2.update_layout(title='Normal Scale',yaxis_title='Monthly Oil, bbl')
		
		cols[0].plotly_chart(fig)
		cols[1].plotly_chart(fig2)
		
		df_dca_cum=df_dca[df_dca.Date>'8/1/2020']
		df_dca_cum=df_dca_cum.groupby(df_dca_cum.Date.dt.year).sum()
		df_dca_cum['50_cum'],df_dca_cum['90_cum'],df_dca_cum['10_cum']=df_dca_cum['Qcalc_50'].cumsum(),df_dca_cum['Qcalc_90'].cumsum(),df_dca_cum['Qcalc_10'].cumsum()

		df_summary=pd.DataFrame({'Year':df_dca_cum.index,'P50':df_dca_cum['Qcalc_50'].to_list(),'P90':df_dca_cum['Qcalc_90'].to_list(),'P10':df_dca_cum['Qcalc_10'].to_list()})
		df_summary['P50'],df_summary['P90'],df_summary['P10']=df_summary['P50']/1000,df_summary['P90']/1000,df_summary['P10']/1000

		fig3=go.Figure()
		fig3.add_trace(go.Scatter(name='P50',x=df_dca_cum.index,y=df_dca_cum['50_cum']))
		fig3.add_trace(go.Scatter(name='P90',x=df_dca_cum.index,y=df_dca_cum['90_cum']))
		fig3.add_trace(go.Scatter(name='P10',x=df_dca_cum.index,y=df_dca_cum['10_cum']))
		fig3.update_layout(title='Cumulatives',yaxis_title='Cum. Oil, bbl')

		cols[0].plotly_chart(fig3)

		if cols[1].button('Export data to csv (MB_DCA)'):
			df_summary.to_csv('MB_DCA.csv')
		else:
			pass

		cols[1].write('Yearly Rates, Mbbl')
		cols[1].write(df_summary)
		cols[1].write('Cumulative Sums, Mbbl')
		cols[1].write(pd.concat([df_summary.Year,df_summary.cumsum().drop(columns=['Year'])],axis=1))

	if page == "Individual Wells":
		#Create a sidebar that allows for cycling through each well
		well = st.selectbox("Choose a well", df['API/UWI'].unique())
		#give a title to the page that is the well name
		st.header(well)
		
		#subset the data to only use singel well data
		df_sub=df[df['API/UWI']==well]
		
		#set three columns for high -low-mid cases
		cols = st.columns(3)
		
		#first column is the P50 case
		cols[0].write("Mid Case (P50)")
		Di50 = float(cols[0].text_input("Decline Rate, 1/year", float(df_params[df_params['Well']==well]['Di_50'])))
		Qi50 = cols[0].text_input('Initial Rate, bbl/month',float(df_params[df_params['Well']==well]['Qi_50']))
		Qi50 = float(Qi50)
		b50 = cols[0].text_input('b-factor',float(df_params[df_params['Well']==well]['b_50']))
		b50 = float(b50)
		df_params.loc[df_params.index[df_params['Well']==well],'Qi_50']=Qi50
		df_params.loc[df_params.index[df_params['Well']==well],'b_50']=b50
		df_params.loc[df_params.index[df_params['Well']==well],'Di_50']=Di50
		
		#second column is the P90 case
		cols[1].write("Low Case (P90)")
		Di90 = float(cols[1].text_input("P90 Decline Rate, 1/year", float(df_params[df_params['Well']==well]['Di_90'])))
		Qi90 = cols[1].text_input('P90 Initial Rate, bbl/month',float(df_params[df_params['Well']==well]['Qi_90']))
		Qi90 = float(Qi90)
		b90 = cols[1].text_input('P90 b-factor',float(df_params[df_params['Well']==well]['b_90']))
		b90 = float(b90)
		df_params.loc[df_params.index[df_params['Well']==well],'Qi_90']=Qi90
		df_params.loc[df_params.index[df_params['Well']==well],'b_90']=b90
		df_params.loc[df_params.index[df_params['Well']==well],'Di_90']=Di90
		
		#third column is the P10 case
		cols[2].write("High Case (P10)")
		Di10 = float(cols[2].text_input("P10 Decline Rate, 1/year", float(df_params[df_params['Well']==well]['Di_10'])))
		Qi10 = cols[2].text_input('P10 Initial Rate, bbl/month',float(df_params[df_params['Well']==well]['Qi_10']))
		Qi10 = float(Qi10)
		b10 = cols[2].text_input('P10 b-factor',float(df_params[df_params['Well']==well]['b_10']))
		b10 = float(b10)
		df_params.loc[df_params.index[df_params['Well']==well],'Qi_10']=Qi10
		df_params.loc[df_params.index[df_params['Well']==well],'b_10']=b10
		df_params.loc[df_params.index[df_params['Well']==well],'Di_10']=Di10
		
		df_dca=pd.DataFrame({'Months':list(range(-24,173))})
		df_dca['Qcalc_50']=dca(df_dca['Months'],Qi50,b50,Di50/12)
		df_dca['Qcalc_90']=dca(df_dca['Months'],Qi90,b90,Di90/12)
		df_dca['Qcalc_10']=dca(df_dca['Months'],Qi10,b10,Di10/12)
		
		dates=[]
		for month in df_dca.Months:
			dates.append(pd.to_datetime(df_sub['Monthly Production Date'][-1:].values[0])+relativedelta(months=+month))
		df_dca['Date']=dates
		df_dca['API']=well

		#st.write('Total Future PDP: %.0f' %(df_dca['Qcalc_50'][1:].sum()))

		fig=go.Figure()
		fig.add_trace(go.Scatter(marker_color='green',name='History',mode='markers',x=df_sub['Monthly Production Date'],y=df_sub['Monthly Oil']))
		fig.add_trace(go.Scatter(name='P50',x=df_dca['Date'],y=df_dca['Qcalc_50']))
		fig.add_trace(go.Scatter(name='P90',x=df_dca['Date'],y=df_dca['Qcalc_90']))
		fig.add_trace(go.Scatter(name='P10',x=df_dca['Date'],y=df_dca['Qcalc_10']))
		fig.update_yaxes(type="log")
		
		fig2=go.Figure()
		fig2.add_trace(go.Scatter(marker_color='green',name='History',mode='markers',x=df_sub['Monthly Production Date'],y=df_sub['Monthly Oil']))
		fig2.add_trace(go.Scatter(name='P50',x=df_dca['Date'],y=df_dca['Qcalc_50']))
		fig2.add_trace(go.Scatter(name='P90',x=df_dca['Date'],y=df_dca['Qcalc_90']))
		fig2.add_trace(go.Scatter(name='P10',x=df_dca['Date'],y=df_dca['Qcalc_10']))
		##reset columns
		cols = st.columns(2)
		cols[0].plotly_chart(fig)
		cols[1].plotly_chart(fig2)
		# cols[0].write(df_params)
		
		if st.button('Save Decline Parameters'):
			df_params.to_csv('MB_DCA_parameters_per_Well.csv')
		else:
			pass

		#Map Below
		df_headers2=df_headers

		df_headers2['Class_Color']=df_headers['Production Type'].map({'WTR INJ':'cyan','OIL':'green','GAS':'red','DRY':'black','WTR SRC':'blue','Test Well':'black'})
		fig = go.Figure(go.Scattermapbox(
			fill = 'none',
			lon = df_headers2['Surface Longitude (WGS84)'], lat = df_headers2['Surface Latitude (WGS84)'],
			marker = { 'size': 6 ,'color':df_headers2['Class_Color']},
		hovertext=df_headers2['API/UWI']))
		fig.add_trace(go.Scattermapbox(
			fill = 'none',
			lon = df_headers2['Surface Longitude (WGS84)'][df_headers2['API/UWI']==well], lat = df_headers2['Surface Latitude (WGS84)'][df_headers2['API/UWI']==well],
			marker = {'size': 25 ,'color':'magenta'},
			hovertext=df_headers2['API/UWI'][df_headers2['API/UWI']==well]))

		fig.update_layout(
			mapbox = {
				'style': "stamen-toner",
				'center': {'lon': df_headers2['Surface Longitude (WGS84)'].mean(), 'lat': df_headers2['Surface Latitude (WGS84)'].mean() },
				'zoom': 11},
			showlegend = False)

		fig.update_layout(width=1500,height=800,
			mapbox_style="white-bg",
			mapbox_layers=[
				{
					"below": 'traces',
					"sourcetype": "raster",
					"sourceattribution": "United States Geological Survey",
					"source": [
						"https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
					]
				}
			])
		st.plotly_chart(fig)

	if page == "Field Map":
		df_headers2=df_headers
		if st.button('Only Show ACTIVE wells'):
			df_headers2=df_headers[df_headers['Producing Status']=='ACTIVE']
		else:
			df_headers2=df_headers

			
		df_headers2['Class_Color']=df_headers['Production Type'].map({'WTR INJ':'cyan','OIL':'green','GAS':'red','DRY':'black','WTR SRC':'blue','Test Well':'black'})
		fig = go.Figure(go.Scattermapbox(
			fill = 'none',
			lon = df_headers2['Surface Longitude (WGS84)'], lat = df_headers2['Surface Latitude (WGS84)'],
			marker = { 'size': 6 ,'color':df_headers2['Class_Color']},
		hovertext=df_headers2['API/UWI']))

		fig.update_layout(
			mapbox = {
				'style': "stamen-toner",
				'center': {'lon': df_headers2['Surface Longitude (WGS84)'].mean(), 'lat': df_headers2['Surface Latitude (WGS84)'].mean() },
				'zoom': 11},
			showlegend = False)

		fig.update_layout(width=1500,height=800,
			mapbox_style="white-bg",
			mapbox_layers=[
				{
					"below": 'traces',
					"sourcetype": "raster",
					"sourceattribution": "United States Geological Survey",
					"source": [
						"https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
					]
				}
			])
		st.plotly_chart(fig)

if __name__ == "__main__":
    main()
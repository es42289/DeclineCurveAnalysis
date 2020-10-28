import streamlit as st, pandas as pd, numpy as np, plotly.graph_objects as go
from dateutil.relativedelta import relativedelta

@st.cache
def load_data():
    df = pd.read_csv('C:/Users/Elii/Desktop/Working/X Oil/Rangeley/app/Rangeley-Sam Producing Entity Monthly Production.csv')
    return df
@st.cache(allow_output_mutation=True)
def load_data2():
	qis=[]
	for well in df['API/UWI'].unique():
		qis.append(float(df[df['API/UWI']==well]['Monthly Oil'][-1:]))
	df_params=pd.DataFrame({'Well':df['API/UWI'].unique(),'Qi':qis})
	return df_params
    
    
def dca(t,qi,d):
	return qi*math.exp(-1*d*t) #exponential
df = load_data() 
df_params=load_data2()

def main(): 
	page = st.sidebar.selectbox("Choose a well", df['API/UWI'].unique())
	df_sub=df[df['API/UWI']==page]
	
	Di = float(st.text_input("Decline Rate, 1/year", 0.1))
	Qi = st.text_input('Initial Rate, bbl/month',float(df_params[df_params['Well']==page]['Qi']))
	Qi = float(Qi)
	df_params.loc[df_params.index[df_params['Well']==page],'Qi']=Qi
	st.header(page)
	
	df_dca=pd.DataFrame({'Months':list(range(0,173))})
	df_dca['Qcalc']=Qi*np.exp(-1*Di/12*df_dca['Months'])
	
	dates=[]
	for month in df_dca.Months:
	    dates.append(pd.to_datetime(df_sub['Monthly Production Date'][-1:].values[0])+relativedelta(months=+month))
	df_dca['Date']=dates
	df_dca['API']=page

	st.write('Total Future PDP: %.0f' %(df_dca['Qcalc'][1:].sum()))

	fig=go.Figure()
	fig.add_trace(go.Scatter(marker_color='green',name='History',mode='markers',x=df_sub['Monthly Production Date'],y=df_sub['Monthly Oil']))
	fig.add_trace(go.Scatter(name='Future',x=df_dca['Date'],y=df_dca['Qcalc']))
	fig.update_yaxes(type="log")
	
	st.plotly_chart(fig)
	st.write(df_params)
	st.write(df_dca)
	
	if st.button('Say hello'):
		df_params.to_csv('df_params.csv')
	else:
		pass


if __name__ == "__main__":
    main()
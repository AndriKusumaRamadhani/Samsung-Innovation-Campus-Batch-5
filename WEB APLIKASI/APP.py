import streamlit as st
from pymongo import MongoClient
import pandas as pd
from darts import TimeSeries
from darts.models import LightGBMModel
import numpy as np
from streamlit_echarts import st_echarts
import plotly.graph_objects as go
import plotly.express as px

model = LightGBMModel.load("modelv1java.pkl")

client = MongoClient("mongodb+srv://JavaJunction:majesa1234@javajunction.mssuddt.mongodb.net/?retryWrites=true&w=majority&appName=JavaJunction")
db = client["java-database"]
collection = db["final-project"]

def opsi():
    mint = st.number_input('Pilihlah berapa menit kedepan:', min_value=30, max_value=3000, value=30,step=30)
    return int(mint/30)

def lakukan_forecast():
    data_list = list(collection.find({}))
    data_raw = pd.DataFrame(data_list).drop("_id", axis=1)
    data_raw["timestamp"] = pd.to_datetime(data_raw["timestamp"]).dt.round("30min")
    data = (
        data_raw.groupby("timestamp")
        .agg(
            {
                "ldr1": "mean",
                "ldr2": "mean",
                "ldr3": "mean",
                "ldr4": "mean",
                "ldr5": "mean",
            }
        )
        .reset_index()
    )
    target_series = TimeSeries.from_dataframe(
        data,
        time_col="timestamp",
        fill_missing_dates=True,
        freq="30min",
    )
    
    input_value = opsi()
    
    if st.button('Prediksi'):
        predicted = model.predict(
            input_value,
            series=target_series,
        )
        target_series[-10:].plot(c="black", label="historical")
        predicted.plot(c="blue", label="forecast")

        predicted_df = predicted.pd_dataframe()
        
        st.write("Berikut adalah data prediksi dari panel surya Anda:")
        column_to_degree = {"ldr1": 0, "ldr2": 45, "ldr3": 90, "ldr4": 135, "ldr5": 180}
        for col in predicted_df.columns:
            st.metric(label=f"{column_to_degree[col]} Derajat", value=int(predicted_df[col].iloc[-1]))

        min_value = predicted_df.min().min()
        min_value_column = predicted_df.min(axis=0).idxmin()
        
        st.write(f"Nilai terkecil dari prediksi adalah: {int(min_value)} jadi lokasi Matahari berada pada arah : {column_to_degree[min_value_column]} Derajat")
        
        st.title("Lokasi Matahari")

        # Map min_value_column to corresponding degree value
        value = column_to_degree[min_value_column]

        # Create the gauge chart
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = value,
            gauge = {
                'axis': {'range': [0, 180]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 90], 'color': "lightgray"},
                    {'range': [90, 180], 'color': "gray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90}}))

        fig.update_layout(title="Lokasi matahari berada pada sudut :")

        # Display the gauge chart
        st.plotly_chart(fig)

        # Displaying the weather condition based on min_value
        condition = "Cerah" if min_value < 500 else "Berawan"
        st.metric(label="Kondisi Cuaca", value=condition)

        # Plotting historical and forecast data
        historical_data = target_series.pd_dataframe().tail(20)  # Adjust this to show more historical data if needed
        forecast_data = predicted_df

        fig = go.Figure()

        for col in historical_data.columns:
            fig.add_trace(go.Scatter(x=historical_data.index, y=historical_data[col], mode='lines', name=f'Historical {col}'))

        for col in forecast_data.columns:
            fig.add_trace(go.Scatter(x=forecast_data.index, y=forecast_data[col], mode='lines', name=f'Forecast {col}', line=dict(dash='dash')))

        fig.update_layout(title="Historical and Forecast Data", xaxis_title="Timestamp", yaxis_title="LDR Values")

        st.plotly_chart(fig)

# Fungsi untuk halaman Data
def data_page():
    st.title("Data Treker Solar Panel")

    # Mengambil data dari MongoDB
    data = list(collection.find())
    
    
    if data:
        df = pd.DataFrame(data)
        st.write("Berikut adalah data dari panel surya Anda:")
        chart_data = pd.DataFrame(np.random.randn(30,5), columns=["ldr1","ldr2","ldr3","ldr4","ldr5",])
        st.dataframe(df.drop("_id",axis=1))

        st.line_chart(chart_data)
    else:
        st.write("Tidak ada data yang tersedia.")

# Fungsi untuk halaman Pemecahan Masalah
def troubleshooting_page():
    st.title("Problem")
    st.write("Panduan untuk memberi peringatan akan problem yang:")
    # Tambahkan informasi pemecahan masalah di sini
    st.title("Coming Soon")

# Fungsi untuk halaman Energi Panel Surya
def energy_page():
    st.title("Energi Panel Surya")
    st.write("Informasi tentang energi yang dihasilkan oleh panel surya:")
    # Tambahkan informasi energi di sini
    st.title("Coming Soon")
# Fungsi untuk halaman Informasi
def info_page():
    st.title("Informasi")
    st.write("Informasi umum tentang cara kerja dari Treker Solar Panel:")
    # Tambahkan informasi umum di sini
    st.title("Coming Soon")

# Fungsi utama untuk menjalankan aplikasi
def main():
    st.sidebar.title("Navigasi")
    page = st.sidebar.selectbox("Pilih halaman", ["Riwayat","Prediksi","Problem", "Energi Panel Surya", "Informasi"])

    if page == "Riwayat":
        data_page()
    elif page == "Prediksi":
        lakukan_forecast()
    elif page == "Problem":
        troubleshooting_page()
    elif page == "Energi Panel Surya":
        energy_page()
    elif page == "Informasi":
        info_page()

if __name__ == "__main__":
    main()

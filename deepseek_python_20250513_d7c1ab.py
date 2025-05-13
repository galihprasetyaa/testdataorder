import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Sales Dashboard", layout="wide")
st.title("📊 Sales Dashboard - Analisis Penjualan")

# Upload CSV
uploaded_file = st.file_uploader("📁 Unggah file CSV", type=["csv"])
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)

        # Konversi tanggal
        for col in ["Order Date", "Invoice Date", "Payment Status Date"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")

        st.subheader("🔍 Pratinjau Data")
        st.dataframe(df.head())

        # Sidebar filters
        st.sidebar.header("🎛️ Filter Data")
        start_date = st.sidebar.date_input("Mulai Tanggal", value=df["Order Date"].min())
        end_date = st.sidebar.date_input("Akhir Tanggal", value=df["Order Date"].max())

        # Filter berdasarkan tanggal
        df_filtered = df[(df["Order Date"] >= pd.to_datetime(start_date)) & 
                         (df["Order Date"] <= pd.to_datetime(end_date))]

        # Ringkasan
        st.subheader("📌 Ringkasan Penjualan")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🧾 Total Transaksi", f"{df_filtered['TrxID'].nunique():,}")
        col2.metric("💰 Total Pembayaran", f"Rp {df_filtered['Total Payment'].sum():,.0f}")
        col3.metric("🎯 Total Diskon", f"Rp {df_filtered['Discount'].sum():,.0f}")
        col4.metric("📦 Jumlah Produk Terjual", f"{df_filtered['Qty'].sum():,.0f}")

        # Tren penjualan per bulan
        st.subheader("📅 Tren Penjualan per Bulan")
        df_filtered["Bulan"] = df_filtered["Order Date"].dt.to_period("M").astype(str)
        trend = df_filtered.groupby("Bulan")["Total Payment"].sum().reset_index()
        fig = px.line(trend, x="Bulan", y="Total Payment", title="Tren Pembayaran Bulanan", markers=True)
        st.plotly_chart(fig, use_container_width=True)

        # Pie chart status pembayaran
        if "Payment Status" in df_filtered.columns:
            st.subheader("💳 Distribusi Status Pembayaran")
            payment_pie = df_filtered["Payment Status"].value_counts().reset_index()
            payment_pie.columns = ["Status", "Jumlah"]
            fig2 = px.pie(payment_pie, values="Jumlah", names="Status", title="Distribusi Status Pembayaran")
            st.plotly_chart(fig2, use_container_width=True)

        # Bar chart produk terlaris
        st.subheader("🏆 Produk Terlaris")
        top_products = df_filtered.groupby("Product Name")["Qty"].sum().nlargest(10).reset_index()
        fig3 = px.bar(top_products, x="Qty", y="Product Name", orientation="h", title="Top 10 Produk Terjual")
        st.plotly_chart(fig3, use_container_width=True)

        # Tabel per partner atau PIC
        st.subheader("📈 Kinerja Partner")
        partner_summary = df_filtered.groupby("Partner")[["Total Payment", "Qty"]].sum().sort_values("Total Payment", ascending=False)
        st.dataframe(partner_summary)

        # Export
        st.download_button("⬇️ Unduh Data yang Difilter", df_filtered.to_csv(index=False).encode("utf-8"), file_name="hasil_filter.csv")

    except Exception as e:
        st.error(f"Terjadi kesalahan: {str(e)}")
else:
    st.info("Silakan unggah file CSV berisi data penjualan.")


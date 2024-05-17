import streamlit as st
import pyodbc
import pandas as pd
import io
import plotly.express as px

# Streamlit uygulamasını özelleştirme
st.set_page_config(page_title="Oyun Raporlama Uygulaması", page_icon="🎮", layout="wide", initial_sidebar_state="expanded")
st.markdown(
    """
    <style>
        .sidebar .sidebar-content {
            background-image: linear-gradient(#f5f7fa, #c3d1e4);
            color: #0e1117;
        }
        .streamlit-button {
            color: white;
            background-color: #4f8bf9;
        }
        .streamlit-button:hover {
            background-color: #0056b3;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Streamlit uygulamasını oluştur
st.title('SQL Server Veri Raporlama Uygulaması')

# Kullanıcıdan bağlantı parametrelerini al
server = st.text_input("Sunucu Adı", "DESKTOP-VLTDF7D")
database = st.text_input("Veritabanı Adı", "Oyun satın alma platformu")

# Bağlantıyı test etme ve durumu gösterme
@st.cache_data
def test_connection(server, database):
    try:
        conn_str = (
            'DRIVER={SQL Server};'
            'SERVER=' + server + ';'
            'DATABASE=' + database
        )
        with pyodbc.connect(conn_str):
            return True
    except:
        return False

if test_connection(server, database):
    st.success('Bağlantı başarılı!')
else:
    st.error('Bağlantı başarısız. Lütfen bilgileri kontrol edin.')

# Kullanıcıdan SQL sorgusunu al veya ön tanımlı sorguları sun
default_query = "SELECT * FROM Kullanicilar"
queries = {
    "Kullanıcılar": "SELECT * FROM Kullanicilar",
    "Oyunlar": "SELECT * FROM Oyunlar",
    "Ödemeler": "SELECT * FROM Odeme_Bilgileri",
    # Diğer sorgular buraya eklenebilir
}

query_option = st.selectbox("Ön Tanımlı Sorgular", list(queries.keys()))
sql_query = st.text_area("SQL Sorgusu", queries[query_option])

# Veritabanı bağlantı dizesi oluştur
conn_str = (
    'DRIVER={SQL Server};'
    'SERVER=' + server + ';'
    'DATABASE=' + database
)

# Veritabanı bağlantısını kur
with pyodbc.connect(conn_str) as conn:
    cursor = conn.cursor()
    cursor.execute(sql_query)
    
    # Sorgu sonuçlarını bir DataFrame'e yükle
    rows = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    df = pd.DataFrame.from_records(rows, columns=columns)
    
    # Tabloyu filtreleme menüsü ekle
    if not df.empty:
        st.subheader("Tabloyu Filtrele")
        selected_columns = st.multiselect("Sütunları Seçin", columns, default=columns)
        filtered_df = df[selected_columns]
        st.write(filtered_df)
        
        # CSV olarak indirme seçeneği ekle
        csv = filtered_df.to_csv(index=False).encode('utf-8-sig')  # utf-8-sig ile BOM eklenerek Excel'de Türkçe karakter sorunu çözülür
        csv_filename = "sorgu_sonuclari.csv"
        csv_button = st.download_button(
            label="CSV olarak indir",
            data=csv,
            file_name=csv_filename,
            mime='text/csv',
            key='csv-download'
        )

        # Excel olarak indirme seçeneği ekle
        excel = io.BytesIO()  # Excel dosyasını bellekte oluştur
        filtered_df.to_excel(excel, index=False)  # DataFrame'i Excel'e yaz
        excel.seek(0)  # Dosya başına dön
        excel_filename = "sorgu_sonuclari.xlsx"
        excel_button = st.download_button(
            label="Excel olarak indir",
            data=excel,
            file_name=excel_filename,
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            key='excel-download'
        )

        # Sorgu sonuçlarını çubuk grafikle görselleştirme
        st.subheader("Sorgu Sonuçlarını Görselleştirme")
        fig = px.bar(filtered_df, x=filtered_df.columns[0], y=filtered_df.columns[1])
        fig.update_layout(
            title="Sonuçların Çubuk Grafiği",
            xaxis_title=filtered_df.columns[0],
            yaxis_title=filtered_df.columns[1],
            template="plotly",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)"
        )
        st.plotly_chart(fig)

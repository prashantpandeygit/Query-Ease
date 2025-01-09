import streamlit as st
import pandas as pd
import sqlite3
import os
import tempfile
from sql import *
from config import generate_sql_query
import requests
import threading
import time
from datetime import datetime

page_bg_img = '''
<style>
[data-testid="stAppViewContainer"] {
    background-image: url("https://static.vecteezy.com/system/resources/previews/008/311/935/original/the-illustration-graphic-consists-of-abstract-background-with-a-blue-gradient-dynamic-shapes-composition-eps10-perfect-for-presentation-background-website-landing-page-wallpaper-vector.jpg");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}
[data-testid="stHeader"] {
    background: rgba(0, 0, 0, 0);
}
[data-testid="stSidebar"] {
    background: rgba(0, 0, 0, 0);
}
</style>
'''
st.markdown(page_bg_img, unsafe_allow_html=True)

def keep_alive():
    while True:
        try:
            url = "https://eda-webapp-603r.onrender.com"
            response = requests.get(url)
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{current_time}] Keep-alive ping sent. Status: {response.status_code}")
        except Exception as e:
            print(f"[{datetime.now()}] Ping failed: {str(e)}")
        time.sleep(840)
        
keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
keep_alive_thread.start()

def main():
    st.title("Query Ease")
    st.write('-------')

    db_option = st.radio("Choose a database option:", ("Use test database", "Upload your own database"))

    if db_option == "Use test database":
        db_path = "test_database.db"
        conn = connect_to_database(db_path)
    else:
        st.info("Please upload a database file (.db, .sqlite, .sqlite3, or .sql)")
        uploaded_file = st.file_uploader("Upload your database file", type=["db", "sqlite", "sqlite3", "sql"], accept_multiple_files=False)
        if uploaded_file is not None:
            file_extension = os.path.splitext(uploaded_file.name)[1].lower()
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                db_path = tmp_file.name
            
            try:
                conn = connect_to_database(db_path)
                st.success(f"Successfully uploaded and connected to {uploaded_file.name}")
            except ValueError as e:
                st.error(str(e))
                st.info("Make sure the uploaded file is a valid SQLite database or SQL script.")
                return
            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")
                return
        else:
            st.warning("Please upload a database file to continue.")
            return

    if 'conn' in locals():
        tables = list_tables(conn)
        if tables:
            st.success(f"Connected to the database. Available tables: {', '.join(tables)}")
        else:
            st.warning("The database is empty. No tables found.")

        table_names = get_table_names(conn)
        if not table_names:
            st.warning("The selected database has no tables. Would you like to create a test table?")
            if st.button("Create Test Table"):
                create_test_table(conn)
                table_names = get_table_names(conn)
        
        if table_names:
            table_name = st.selectbox("Select a table:", table_names)

            st.subheader(f"Table: {table_name}")
            df = get_table_data(conn, table_name)
            st.dataframe(df)

            table_info = f"Table: {table_name}\nColumns: {', '.join(df.columns)}"

            user_question = st.text_input("Ask a question about the data:")
            if user_question:
                try:
                    sql_query = generate_sql_query(user_question, table_info)
                    
                    sql_query = sql_query.strip().rstrip(';')
                    
                    st.subheader("Generated SQL Query:")
                    st.code(sql_query, language="sql")

                    result = execute_query(conn, sql_query)
                    st.subheader("Query Result:")
                    st.dataframe(result)
                except sqlite3.Error as e:
                    st.error(f"SQLite error occurred: {str(e)}")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

        conn.close()

        if db_option != "Use test database" and os.path.exists(db_path):
            os.unlink(db_path)

if __name__ == "__main__":
    main()


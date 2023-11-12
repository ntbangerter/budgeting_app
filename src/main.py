import streamlit as st
import pandas as pd
from os.path import isfile

from process_data import create_upload_file_form


DATA_PATH = '../data/data.csv'

COLUMN_NAMES = ['date',
                'amount',
                'description',
                'source',
                'category']


def load_data():

    if isfile(DATA_PATH):
        st.session_state['data'] = pd.read_csv(DATA_PATH)

    else:
        df = pd.DataFrame(columns=COLUMN_NAMES)
        df.index.name = 'id'
        st.session_state['data'] = df


def main(parent):
    home, upload = parent.tabs(['Home', 'Upload'])

    if 'data' not in st.session_state:
        load_data()

    create_upload_file_form(upload)

    if len(st.session_state['data']) > 0:
        home.dataframe(st.session_state['data'])
    else:
        home.write('No data found.')


main(st.container())

import pandas as pd
import streamlit as st
from uuid import uuid3, NAMESPACE_OID


FORMATS = ['Wells Fargo',
           'UCCU']

LABELS = ['Checking',
          'Savings',
          'Credit Card - Tanner',
          'Credit Card - Sarah']

COLUMN_NAMES = ['date',
                'amount',
                'description',
                'source']


def generate_ids(df):
    df['entry_number'] = df.sort_values(COLUMN_NAMES).groupby(COLUMN_NAMES).cumcount()

    df['id'] = (df['date']
                + df['amount'].astype(str)
                + df['description']
                + df['entry_number'].astype(str)
                ).apply(lambda x: uuid3(NAMESPACE_OID, x)).astype(str)

    df.set_index('id', drop=True, inplace=True)

    return df[COLUMN_NAMES]


def read_wells_fargo(file_path, source):
    df = pd.read_csv(file_path, header=None)
    df = df[[0, 1, 4]]

    df['source'] = source
    df.columns = COLUMN_NAMES

    df['date'] = pd.to_datetime(df['date']).dt.date.astype(str)

    df = generate_ids(df)

    return df


def read_uccu(file_path, source):
    df = pd.read_csv(file_path)
    df = df[['Post Date', 'Description', 'Debit', 'Credit', 'Status', 'Balance', 'Classification']]

    df['amount'] = df['Credit'].fillna(0.0) - df['Debit'].fillna(0.0)
    df['source'] = source

    df = df[['Post Date', 'amount', 'Description', 'source']]
    df.columns = COLUMN_NAMES

    df['date'] = pd.to_datetime(df['date']).dt.date.astype(str)

    df = generate_ids(df)

    return df


def read_file(file, format, label):
    source = format + ' ' + label

    if format == 'Wells Fargo':
        return read_wells_fargo(file, source)
    elif format == 'UCCU':
        return read_uccu(file, source)


def remove_existing_rows(df):
    return df[~df.index.isin(st.session_state['data'].index)]


def get_current_categories():
    data = st.session_state['data']
    return data[['description', 'category']].groupby('description').agg(pd.Series.mode)


def append_to_existing_data(df):
    st.session_state['data'] = pd.concat([st.session_state['data'], df], axis=0)


def create_upload_file_form(parent):
    form = parent.form('Upload CSV')

    file = form.file_uploader('Select CSV:', label_visibility='collapsed')
    format = form.selectbox('Format:', options=FORMATS)
    label = form.selectbox('Label:', options=LABELS)

    submit = form.form_submit_button('**Upload**')

    if submit and file is not None:
        df = read_file(file, format, label)
        df = remove_existing_rows(df)
        append_to_existing_data(df)
        parent.dataframe(df)

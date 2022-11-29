import base64
import json
import pickle
import uuid
import re
import pandas as pd
import streamlit as st
## -- Functions -- ## 

## function to reverse a dictionary 
def reverse_dictionary(dictionary:dict) -> dict: 
    """Reverses the dictionary. {k:v} -> {v:k}"""
    return {v:k for k,v in dictionary.items()}

## function to filter a list of strings by a specific value    
def _filter_columns(column_list:list, filter:str) -> list:
    """Filters a list of columns by a filter string."""
    return [x for x in column_list if filter in x]

def download_button(object_to_download, download_filename:str, button_text:str, pickle_it:bool = False):
    """
    Generates a link to download the given object_to_download.
    Params:
    ------
    object_to_download:  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv,
    some_txt_output.txt download_link_text (str): Text to display for download
    link.
    button_text (str): Text to display on download button (e.g. 'click here to download file')
    pickle_it (bool): If True, pickle file.
    Returns:
    -------
    (str): the anchor tag to download object_to_download
    Examples:
    --------
    download_link(your_df, 'YOUR_DF.csv', 'Click to download data!')
    download_link(your_str, 'YOUR_STRING.txt', 'Click to download text!')
    """
    if pickle_it:
        try:
            object_to_download = pickle.dumps(object_to_download)
        except pickle.PicklingError as e:
            st.write(e)
            return None

    else:
        if isinstance(object_to_download, bytes):
            pass

        elif isinstance(object_to_download, pd.DataFrame):
            object_to_download = object_to_download.to_csv(index=False, compression='zip')

        # Try JSON encode for everything else
        else:
            object_to_download = json.dumps(object_to_download)

    try:
        # some strings <-> bytes conversions necessary here
        b64 = base64.b64encode(object_to_download.encode()).decode()

    except AttributeError as e:
        b64 = base64.b64encode(object_to_download).decode()

    button_uuid = str(uuid.uuid4()).replace('-', '')
    button_id = re.sub('\d+', '', button_uuid)

    custom_css = f""" 
        <style>
            #{button_id} {{
                background-color: rgb(255, 255, 255);
                color: rgb(38, 39, 48);
                padding: 0.25em 0.38em;
                position: relative;
                text-decoration: none;
                border-radius: 4px;
                border-width: 1px;
                border-style: solid;
                border-color: rgb(230, 234, 241);
                border-image: initial;
            }} 
            #{button_id}:hover {{
                border-color: rgb(246, 51, 102);
                color: rgb(246, 51, 102);
            }}
            #{button_id}:active {{
                box-shadow: none;
                background-color: rgb(246, 51, 102);
                color: white;
                }}
        </style> """

    dl_link = custom_css + f'<a download="{download_filename}" id="{button_id}" href="data:file/txt;base64,{b64}">{button_text}</a><br></br>'

    return dl_link

def open_json(fname: str) -> dict:
        """Opens a json file and returns a dictionary"""
        with open(fname) as f:
            return json.load(f)

def remove_punctuation(text: str) -> str:
        """Removes punctuation from a string"""
        pattern = '[^A-Za-z0-9]+'
        return re.sub(pattern, ' ', text).strip()


def check_text_valid(text: str) -> bool:
        """Checks if a string is valid or not"""
        if text is not None and text != 0:
            return True
        else:
            return False

## -- End Functions -- ##
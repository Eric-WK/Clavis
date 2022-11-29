import streamlit as st
import pandas as pd 
import numpy as np
from collections import UserDict
from typing import Dict
import sys 
import time
sys.path.append("../")
from utils import download_button

## -- Define the Page Config -- ##
st.set_page_config(
    page_title="Clavis",
    page_icon="random",
    layout="centered",
    initial_sidebar_state="collapsed",
)

## -- End of Page Config -- ##

# """
# Todo: 

# Add the Keyword search volume extractor from Matias as a separate button 

# something like: 

# from KeywordSearchVolume.main import run_search_volume

# # keywords = ['mate','messi','argentina']
# # ideas = True
# # language = 'Spanish'
# # geo = 'Argentina'
# # results = run_search_volume(keywords,language,geo,ideas)

# ## buttons to customize the search volume: Ideas, Language and Geo 
# ideas = st.checkbox('Include Ideas', value=True)
# language = st.input('Language', value='Spanish')
# geo = st.input('Geo', value='Argentina')


# ## button to run the search volume
# search_volume = st.button("Get Search Volume")

# if search_volume:
#     ## run the search volume extractor
#     kws = list(get_data()['keywords']['keywords'].values)
#     payload = dict(keywords=kws, language=language, geo=geo, ideas=ideas)
#     results = run_search_volume(**payload)
#     ## add the results to the dataframe
#     get_data()['keywords']['Search Volume'] = results
#     ## display the results
#     st.write(results)
# """


###-----------------------------------###  
### HELPER FUNCTIONS FOR THE KEYWORDS ###
###-----------------------------------###

class CategoryDict(UserDict):
    def __missing__(self, key):
        return "__no_match__"

def retrieve_replacement_category(dictionary: Dict[str, str]) -> Dict[str,str]:
    """Assigns the value of the corresponding key if found in the keyword"""
    l = {}
    all_keywords = sorted(get_data()['keywords']['keywords'].values)
    for category, replace_val in dictionary.items():
        for words in all_keywords:
            if isinstance(category, str):
                if category in words:
                    l[words] = replace_val
            else: 
                if isinstance(category, type(np.nan)):
                    l[words] = replace_val
    return l

## function to replace them
def replace_keywords(dictionary: Dict[str, str]) -> list:
    """Generates the map"""
    # holder = [None] * len(dictionary)
    holder = {}
    ## iterate over the keys only 
    for k in dictionary.keys():
        ## extract the current dictionary 
        current_dictionary = dictionary[k]
        ## add the resulting dict to the holder 
        # holder[idx] = retrieve_replacement_category(current_dictionary, k)
        holder[k] = retrieve_replacement_category(current_dictionary)
    return holder


def new_column_from_map(dataframe: pd.DataFrame, dictionary: Dict[str, str], anchor_col: str) -> pd.DataFrame:
    """Maps the different key-value pairs onto the anchoring colun"""
    ## iterate over the dictionary 
    for category_name, final_mapping in dictionary.items():
        ## append a new column to the dataframe
        dataframe[category_name]  = dataframe[anchor_col].map(final_mapping)
    return dataframe


## -- Function to display the dictionary as dataframe -- ## 
def display_dict_df(dictionary: Dict[str, str]) -> pd.DataFrame:
    """Displays the dictionary as a dataframe"""
    return pd.DataFrame(dictionary, index=[0]).T.reset_index().rename(columns={'index': 'SearchFor', 0: 'Return'})


def check_upload_state(keywords_upload: st.button, categories_upload: st.button) -> bool:
    """Validation check whether the files have been uploaded"""
    ## first check if it is a demo
    # if get_data()['is_demo']:
    #     return True
    # else:
    if keywords_upload is None or categories_upload is None:
        return False
    else:
        return True


## -- Data Reading -- ##
@st.cache(persist=True)
def load_keywords(file_name: str) -> pd.DataFrame: 
    """Loads the Keywords File"""
    return pd.read_csv(file_name, sep='\t', header=None, dtype=str).rename(columns={0: 'keywords'})

@st.cache(persist=True)
def load_categories(file_name: str) -> pd.DataFrame: 
    """Loads the categories file"""
    return pd.read_csv(file_name, sep=';',dtype=str).rename(columns={"Search For":"SearchFor"})


## -- End Data Reading -- ##

## -- function for caching intermediate data -- ##
@st.cache(allow_output_mutation=True)
def get_data() -> list:
    """Returns the data to be cached"""
    return {}

@st.cache(allow_output_mutation=True)
def cache_button_clicked() -> bool:
    """Returns the state of the cache button"""
    return {}

## -- end of caching function -- ##

## -- Map the categories -- ## 
@st.cache(persist=True)
def map_categories(dataframe: pd.DataFrame) -> Dict[str, str]:
    """Maps the values of the Category column to the SearchFor & Return
    
    {Category:
        {SearchFor: Return} 
        }
    """
    ## create a dictionary to map the categories
    mapped_categories = {}
    for category in dataframe['Category'].unique():
        ## filter the dataframe
        filtered = dataframe[dataframe['Category'] == category]
        ## create a dictionary to map the categories
        mapped_categories[category] = dict(zip(filtered['SearchFor'], filtered['Return']))
    return mapped_categories
## -- End Map the categories -- ##


## -- Function to run the final mapping -- ##




###-----------------------------------###  
### END OF HELPER FUNCTIONS FOR KWDS  ###
###-----------------------------------###



##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~###
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~###
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~###
##             FRONT END              ###
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~###
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~###
##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~###


## -- Title -- ##
st.title("Clavis")
## -- End Title -- ##

## -- Description -- ## 
st.markdown("## Description \nPlease upload the corresponding file to be checked in the form **below**.")
st.markdown("---")
## -- End Description -- ##

## -- File Upload -- ## 
st.markdown("#### Inputs")
## make two columns 
kws, cats= st.columns(2)
keywords_upload = kws.file_uploader("Upload your keywords file", type=["csv"])
categories_upload = cats.file_uploader("Upload your categories file", type=["csv"])
## -- End File Upload -- ##

## -- End function for caching intermediate data -- ##
## make two columns 
load_data_col, map_categories_col = st.columns(2)
## -- Button for Loading Data -- ## 
if load_data_col.button("Process Files"):
    cache_button_clicked()['Load_Data'] = True
    ## check the uploaded files
    if check_upload_state(keywords_upload, categories_upload):
    # if keywords_upload is not None and categories_upload is not None:
        ## load the files
        keywords = load_keywords(keywords_upload)
        # get_data().append(keywords)
        get_data()['keywords'] = keywords
        categories = load_categories(categories_upload)
        # get_data().append(categories)
        get_data()['categories'] = categories
        ## check the data
        if keywords.empty or categories.empty:
            st.error("Please check your files")
        else:
            st.success("Data Loaded")
    else: 
        st.error("Please upload the correct files")
## -- End Button for Loading Data -- ##

## -- Button for Mapping the Categories -- ##
if "Load_Data" in cache_button_clicked():
    if "keywords" and "categories" in get_data().keys():
        if map_categories_col.button("Extract Categories"):
            ## map the categories
            categories = get_data()['categories']
            mapped_categories = map_categories(categories)
            get_data()['mapped_categories'] = mapped_categories
            cache_button_clicked()['Map_Categories'] = True
            ## check the data
            if mapped_categories is not None:
                st.success("Categories Mapped")
            else:
                st.error("Please check your data")

## check that mapped categories is in the get_data dictionary
if 'Map_Categories' in cache_button_clicked().keys():
    st.markdown("#### Mapped Categories")
    ## create tabs with the length of the keys in the mapped_categories dictionary
    tabs = st.tabs([x for x in get_data()['mapped_categories'].keys()])
    ## map the tabs to the categories
    tab_key_map = dict(zip(tabs,[x for x in get_data()['mapped_categories'].keys()]))
    cache_button_clicked()['Ready'] = True
    ## loop through the tabs
    for tab in tabs:
        with tab:
            data = get_data()['mapped_categories'][tab_key_map[tab]]
            ## show the corresponding information 
            st.write(f"Number of values : {len(data)}")
            ## show the data
            with st.expander("Show Data"):
                df = display_dict_df(data)
                st.dataframe(df)


##
def run_clavis() -> pd.DataFrame:
    """Runs the final mapping"""
    ## copy the dataframe with the keywords 
    keyword_dataframe = get_data()['keywords'].copy()
    ## get the corresponding mappings 
    mapped_categories = replace_keywords(get_data()['mapped_categories'])
    ## create the new columns from a map 
    keyword_dataframe = new_column_from_map(keyword_dataframe, mapped_categories, 'keywords')
    ## replace the empty values in the Delete column with a "" 
    keyword_dataframe['Delete'] = keyword_dataframe['Delete'].fillna("")
    ## replace the empty values in the Topic column with a -99 for easier filtering
    keyword_dataframe['Topic'] = keyword_dataframe['Topic'].fillna(-99)
    return keyword_dataframe

## the final part of the code
st.markdown("---")
## check that the previous data has been cached
if "Ready" in cache_button_clicked().keys():
    if st.button("Run Clavis"):
        with st.spinner("Clavis is running..."):
            kwds_df = get_data()['keywords'], 
            mapped_categories = get_data()['mapped_categories'],
            final_df = run_clavis()
            ## add to the cache
            get_data()['final_df'] = final_df
            cache_button_clicked()['clavis_ran'] = True
            st.success("Mapping Complete")
            ## show the final dataframe

## download buttons 
if "clavis_ran" in cache_button_clicked().keys():
    ## make three columns
    col1, col2, col3 = st.columns(3)
    ## data to save 
    final_dataframe = dict(
        object_to_download = get_data()['final_df'],
        download_filename = "clavis_output.csv",
        button_text = "Download Output",
        pickle_it = False
        )
    ## download the category mapping as well 
    category_mapping = dict(
        object_to_download = get_data()['mapped_categories'],
        download_filename = "clavis_category_mapping.csv",
        button_text = "Download Category Mapping",
        pickle_it = False
    )
    ## download the keywords
    keywords = dict(
        object_to_download = get_data()['keywords'],
        download_filename = "clavis_keywords.csv",
        button_text = "Download Keywords",
        pickle_it = False
    )
    ## show the final visualization button for the dataframe 
    if st.button("Show Final DataFrame"):
        # show_df = get_data()['final_df']
        # styler = show_df.style.hide_index()
        # # st.dataframe(get_data()['final_df'])
        # if get_data()['is_demo']:
        #     demo_kws = load_categories("/Users/eric/Documents/Locaria/Projects/LocariaToolBox/data/clavis/demo/eng/demo_keywords_eng.csv")
        #     demo_kws['Delete'].fillna("", inplace=True)
        #     demo_cats= load_categories("/Users/eric/Documents/Locaria/Projects/LocariaToolBox/data/clavis/demo/eng/demo_opportunity_eng.csv")
        #     demo_irrelevant = load_categories("/Users/eric/Documents/Locaria/Projects/LocariaToolBox/data/clavis/demo/eng/demo_irrelevant_kws.csv")
        #     st.dataframe(demo_kws)
        #     st.markdown("---")
        #     st.dataframe(demo_cats)
        #     st.markdown("---")
        #     st.dataframe(demo_irrelevant)
        # else: 
        st.dataframe(get_data()['final_df'])
        # df = pd.read_csv("/Users/eric/Documents/Locaria/Projects/LocariaToolBox/data/clavis/dataframe_sample_for_sam.csv")
        # df['Search Volume'].fillna(0, inplace=True)
        # df['Search Volume'] = df['Search Volume'].apply(lambda x: round(x, 2)).astype(str).apply(lambda x: x.split(".")[0])
        # df['Delete'].fillna("",inplace=True)
        # styler = df[['Topic','keywords','Search Volume']].sample(100)
        ## assign randomly "Missed Opportunity" or "Editorial Opportunity" to the Topic column
        # styler['Topic'] = styler['Topic'].apply(lambda x: np.random.choice(['Missed Opportunity','Editorial Opportunity']))
        # styler.sort_values(by='Search Volume', ascending=False,inplace=True)
        # styler = styler.style.hide_index()
        # st.write(styler.to_html(), unsafe_allow_html=True)
        # st.write(styler.to_html(), unsafe_allow_html=True)
    ## generate the download buttons
    final_data_download_button = download_button(**final_dataframe)
    category_mapping_download_button = download_button(**category_mapping)
    keywords_download_button = download_button(**keywords)
    ## add the buttons to the columns
    col1.markdown(final_data_download_button, unsafe_allow_html=True)
    col2.markdown(category_mapping_download_button, unsafe_allow_html=True)
    col3.markdown(keywords_download_button, unsafe_allow_html=True)
    ## save the state that clavis has been run and the final dataframe has been generated
    cache_button_clicked()['ran_successfully'] = True

## -- End Button for Mapping the Categories -- ##

## -- Section for URL Generation -- ##
if "ran_successfully" in cache_button_clicked().keys():
    st.markdown("---")
    st.markdown("#### URL Generation")
    ## check that the data has been generated
    generate_url = st.button("Generate URLs")
    if generate_url:
        with st.spinner("Generating URLs.."):
            time.sleep(5)
            urls_df = pd.DataFrame(columns=['URL'])
            ## generate the payload to download 
            url_payload = dict(
                object_to_download=urls_df,
                download_filename="clavis_urls.csv",
                button_text="Download URLs",
                pickle_it=False)
            ## generate the button 
            url_download_button = download_button(**url_payload)
            ## show it 
            st.markdown(url_download_button, unsafe_allow_html=True)
            cache_button_clicked()['urls_generated'] = True
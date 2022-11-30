import streamlit as st
import pandas as pd
import time
from utils import download_button, open_json
from KeywordSearchVolume.search_volume_extractor import run_search_volume
from clavis_helpers import (
    does_file_exist,
    parse_search_volume,
    load_excel_and_clean,
    get_payload,
    clean_categories_df,
    categorize_keywords,
    apply_clean_dataframe_for_categorization,
)

## -- Define the Page Config -- ##
st.set_page_config(
    page_title="Clavis",
    page_icon="random",
    layout="centered",
    initial_sidebar_state="collapsed",
)
## -- End of Page Config -- ##
lang_loc_dict = open_json("./allowed_langs_locs/lang_loc_dict.json")

## title and description
st.title("Clavis")
st.write("Keyword Search Volume & Expansion Tool")
st.markdown(
    """
    This tool allows you to extract search volume data from Google Keyword Planner.
    Set your language and location, upload your keywords, and run the Expander.
    """
)

## separator
st.markdown("---")
st.markdown("Upload your keywords in a .csv or .xlsx file.")

## two columns
config_col, keywords_col = st.columns(2)

## file upload: Config file and Keywords file
config_file = config_col.file_uploader("Upload your config file", type=["xlsx", "xls"])
keywords_file = keywords_col.file_uploader(
    "Upload your keywords file", type=["xlsx", "xls", "csv"]
)

st.markdown("---")

## -- START OF CONFIGURATION -- ##
st.write("### Keyword Search Volume & Expansion Configuration")

## make three columns
col1, col2, col3 = st.columns(3)

## Location Selection: Only those available from the lang_loc_dict
GEOLOCATION = col1.selectbox(
    "Select a location",
    options=list(lang_loc_dict.keys()),
    index=86,
)
## selectbox for the language
LANGUAGE = col2.selectbox(
    "Select a language",
    options=lang_loc_dict[GEOLOCATION],
)
## radio button for expanding the search
EXPAND_KEYWORDS = col3.radio(
    "Expand the search?",
    options=["Yes", "No"],
    index=0,
)
st.markdown("---")
st.write("### Clavis Configuration File")

## input for the sheet name of the clavis config file
SHEET_NAME = st.text_input(
    "Enter the sheet name of the Clavis config file",
    value="Config - Categorisation",
)
st.markdown("---")

## -- END OF CONFIGURATION -- ##
expansions_col, clavis_col = st.columns(2)
expand_keywords_button = expansions_col.button("Search Volume / Expand Keywords")
clavis_button = clavis_col.button("Run Clavis")


## -- Start of processing -- ##

## -- Session state -- ##
if "parsed_search_volume" not in st.session_state:
    st.session_state.parsed_search_volume = None

if "categorised_keywords" not in st.session_state:
    st.session_state.categorised_keywords = None

if "clavis_df" not in st.session_state:
    st.session_state.clavis_df = None

if "expansion_factor" not in st.session_state:
    st.session_state.expansion_factor = 0

if "clavis_end_result" not in st.session_state:
    st.session_state.clavis_end_result = None


## -- Start of Expanding Keywords -- ##
if expand_keywords_button:
    if does_file_exist("sample_data/intermediate_results.csv"):
        st.write("Intermediate results file already exists. Loading it for testing.")
        ## load it and add it to the session state to bypass the search volume extraction
        st.session_state.parsed_search_volume = pd.read_csv(
            "sample_data/intermediate_results.csv"
        )
    if keywords_file is None:
        # st.write("Please upload a keywords file.")
        st.error("ERROR: No keywords file uploaded.")
        st.info("INFO: Please upload a keywords file.")
    else:
        if st.session_state_parsed_search_volume is None:
            ## load the keywords file
            KEYWORDS_FILE = pd.read_csv(keywords_file)
            ## define the payload
            PAYLOAD = get_payload(KEYWORDS_FILE, LANGUAGE, EXPAND_KEYWORDS, GEOLOCATION)
            ## run the search volume extractor
            # time_limit = 60 * 1.5 ## 4 minutes
            # tic = time.time()
            ## with a time limit
            with st.spinner("Expanding Keywords..."):
                # while time.time() - tic < time_limit:
                try:
                    search_volume = run_search_volume(**PAYLOAD)
                    parsed_search_volume, _ = parse_search_volume(
                        search_volume, PAYLOAD
                    )
                    st.session_state.parsed_search_volume = parsed_search_volume
                    # st.session_state.expansion_factor = expansion_factor
                    st.success("Keywords Expanded!")
                    # break
                except Exception as e:
                    st.error(e)
                    # break
        # st.metric(
        #     "Expansion Factor",
        #     value=round(st.session_state["expansion_factor"], 2),
        #     delta=0,
        #     delta_color="normal",
        # )

## -- End of Expanding Keywords -- ##
## -- Start of Categorizing Keywords -- ##

if clavis_button:
    if config_file is None:
        st.error("ERROR: No config file uploaded.")
        st.info("INFO: Please upload a config file.")
    else:
        ## load the clavis config file
        clavis_config = load_excel_and_clean(config_file, SHEET_NAME)

        ## function to perform the above steps
        separated_categories_dict = clean_categories_df(clavis_config)

        ## cleaned dataframe
        cleaned_categories_df = apply_clean_dataframe_for_categorization(
            separated_categories_dict
        )

        ## separate the URL generation from the categorization
        url_generation_df = cleaned_categories_df[
            cleaned_categories_df["Category"].str.contains("URL")
        ]

        ## separate the categorization from the URL generation
        categorization_df = cleaned_categories_df[
            ~cleaned_categories_df["Category"].str.contains("URL")
        ]

        categorized_keywords = categorize_keywords(
            st.session_state.parsed_search_volume, categorization_df
        )

        ## add the categorized keywords to the session state
        st.session_state.categorised_keywords = categorized_keywords

        ## now URL generation
        generated_urls = categorize_keywords(
            st.session_state.parsed_search_volume, url_generation_df
        )

        ## get the columns that are not keywords, search volume, idea, or 0
        columns_to_concatenate = generated_urls.columns[
            ~generated_urls.columns.isin(["keywords", "search_volume", "idea"])
        ]

        ## in all of the columns to concatenate, replace 0 with "", 0 is a str ("0")
        generated_urls[columns_to_concatenate] = generated_urls[
            columns_to_concatenate
        ].replace("0", "")

        # ## concatenate the columns
        generated_urls["url"] = generated_urls[columns_to_concatenate].apply(
            lambda x: "-".join(x.dropna().astype(str)), axis=1
        )

        ## cleaning - remove the hyphen
        generated_urls["url"] = generated_urls["url"].replace(
            "-", "", regex=True, inplace=False
        )

        ## replace the ampersand & with ""
        generated_urls["url"] = generated_urls["url"].replace(
            "&", "", regex=True, inplace=False
        )

        ## join back the two dataframes
        final_df = pd.merge(
            categorized_keywords,
            generated_urls,
            on=["keywords", "search_volume", "idea"],
            how="left",
        )
        ## add the final df to the session state
        st.session_state.clavis_end_result = final_df
        st.success("Clavis Complete!")

## -- End of Categorizing Keywords -- ##
## -- Start of Downloading the Results -- ##
if st.session_state.clavis_end_result is not None:
    ## download button
    # download_clavis_results = st.button("Download Clavis Results")
    ## create the payload
    download_payload = dict(
        object_to_download=st.session_state.clavis_end_result,
        download_filename="clavis_results.csv",
        button_text="Download Clavis Results",
        pickle_it=False,
    )
    ## generate the button
    clavis_download_button = download_button(**download_payload)
    ## display the button
    st.markdown(clavis_download_button, unsafe_allow_html=True)

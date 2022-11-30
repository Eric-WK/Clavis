import os
from typing import Dict, Union, List
import pandas as pd
import numpy as np

## HELPER FUNCTIONS


def does_file_exist(file_name: str) -> bool:
    """Checks if a file exists"""
    return os.path.isfile(file_name)


def get_payload(
    keywords: pd.DataFrame, language: str, expand_keywords: bool, geo: str
) -> Dict[str, Union[str, List[str]]]:
    """Generates the payload for the API call"""
    return dict(
        keywords=keywords["keywords"].tolist(),
        language=language,
        geo=geo,
        ideas=expand_keywords,
    )


def parse_search_volume(
    search_volume_result: Dict[str, int], payload: Dict[str, Union[List[str], str]]
) -> pd.DataFrame:
    """Runs the search volume extractor and parses the results"""
    ## parse the results
    results_df = (
        pd.DataFrame.from_dict(
            search_volume_result, orient="index", columns=["search_volume"]
        )
        .reset_index()
        .rename(columns={"index": "keywords"})
    )
    ## add a column to the dataframe to label the keywords as "idea" or "not idea"
    results_df["idea"] = np.where(
        results_df["keywords"].isin(payload["keywords"]), "Expanded", "Original"
    )
    ## calculate the expansion factor
    expansion_factor = len(results_df) / len(payload["keywords"])
    ## return the results
    return results_df, expansion_factor


def load_excel_and_clean(
    clavis_config_file_path: str, sheet_name: str = "Config - Categorisation"
) -> pd.DataFrame:
    """Loads and cleans the Clavis Configuration File Given a sheet name"""
    ## load the file
    categories_df = pd.read_excel(clavis_config_file_path, sheet_name=sheet_name)
    ## define the columns to drop
    to_drop = [x for x in categories_df.columns[2::3]]
    ## drop them
    categories_df = categories_df.drop(to_drop, axis=1)
    ## return the dataframe
    return categories_df


def clean_categories_df(categories_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Converts a dataframe with multiple columns into a dictionary of dataframes"""
    ## create a list of dataframes every two columns
    new_dfs = [
        categories_df.iloc[:, i : i + 2]
        for i in range(0, len(categories_df.columns), 2)
    ]
    ## remove the nans of each dataframe, on the rows
    new_dfs = [x.dropna(axis=0) for x in new_dfs]
    ## convert to a dictionary of dataframes, where the key is the category name (i.e. the column name)
    new_dfs_dict = {x.columns[0]: x for x in new_dfs}
    return new_dfs_dict


## define a function to perform the above steps
def clean_dataframe_for_categorization(df: pd.DataFrame, key_name: str) -> pd.DataFrame:
    """Function to clean the dataframe for the categorization function"""
    ## shift the columns upwards
    df.columns = df.iloc[0].values.tolist()
    ## drop the first row
    df = df.drop(0, axis=0)
    ## add the category name as a column
    df["Category"] = key_name
    return df


## define a function to apply clean_dataframe_for_categorization to a dictionary of dataframes
def apply_clean_dataframe_for_categorization(
    categories_dict: Dict[str, pd.DataFrame]
) -> pd.DataFrame:
    """applies the clean_dataframe_for_categorization function to a dictionary of dataframes"""
    ## dictionary of cleaned dataframes
    cleaned_dfs_dict = {
        x: clean_dataframe_for_categorization(categories_dict[x], x)
        for x in categories_dict.keys()
    }
    ## concatenate the dataframes
    return pd.concat(cleaned_dfs_dict.values(), axis=0)


## Part 2. Keyword Categorization
## we will use the categories.csv file to categorize the keywords

## first we will create a function to categorize the keywords
def categorize_keywords(
    keywords_df: pd.DataFrame, categories_df: pd.DataFrame
) -> pd.DataFrame:
    """Function to categorize the keywords given the categories file"""
    ## copy the df just in case
    df = keywords_df.copy()
    ## we will loop through the categories file and apply the rules to the keywords
    for _, row in categories_df.iterrows():
        ## if the search for column is empty, we will apply the return column to the keywords
        if pd.isna(row["Search For"]):
            df[row["Category"]] = row["Return"]
        ## if the search for column is not empty, we will apply the return column to the keywords
        ## that contain the search for column
        else:
            try:
                df[row["Category"]] = np.where(
                    df["keywords"].str.contains(row["Search For"], case=False),
                    row["Return"],
                    df[row["Category"]],
                )
            ## except a KeyError if the category column does not exist in the dataframe
            except KeyError:
                df[row["Category"]] = np.where(
                    df["keywords"].str.contains(row["Search For"], case=False),
                    row["Return"],
                    0,
                )
    return df
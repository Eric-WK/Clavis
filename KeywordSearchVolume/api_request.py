from .client import RestClient
import streamlit as st

# helpful modules
def getKwInfo(q: str, language: str, geo: str) -> dict:
    login = st.secrets["DB_USERNAME"]
    passw = st.secrets["DB_PASSWORD"]
    client = RestClient(login, passw)
    post_data = dict()
    # simple way to set a task
    post_data[len(post_data)] = dict(
        location_name=geo, keywords=q, language_name=language, search_partners=False
    )
    # POST /v3/keywords_data/google_ads/search_volume/live
    # the full list of possible parameters is available in documentation
    response = client.post("/v3/keywords_data/google_ads/search_volume/live", post_data)
    # you can find the full list of the response codes here https://docs.dataforseo.com/v3/appendix/errors

    if response["status_code"] == 20000:
        return response

    else:
        print(
            "error. Code: %d Message: %s"
            % (response["status_code"], response["status_message"])
        )


def getKwIdea(q: str, language: str, geo: str) -> dict:
    login = st.secrets["DB_USERNAME"]
    passw = st.secrets["DB_PASSWORD"]
    client = RestClient(login, passw)
    post_data = dict()
    # simple way to set a task
    post_data[len(post_data)] = dict(
        location_name=geo, keywords=q, language_name=language, search_partners=True
    )

    # the full list of possible parameters is available in documentation
    response = client.post(
        "/v3/keywords_data/google_ads/keywords_for_keywords/live", post_data
    )
    # you can find the full list of the response codes here https://docs.dataforseo.com/v3/appendix/errors
    if response["status_code"] == 20000:
        return response
    else:
        print(
            "error. Code: %d Message: %s"
            % (response["status_code"], response["status_message"])
        )

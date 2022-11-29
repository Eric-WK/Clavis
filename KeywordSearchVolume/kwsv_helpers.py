from .api_request import getKwInfo, getKwIdea

def break_keywords(keywords_list, limit):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(keywords_list), limit):
        yield keywords_list[i:i + limit]



def get_keywords_sv(keywords: list, language: str, geo: str):
    # We can't request more that 1000 keywords per API call
    # New list with keywords in sets of 1000
    Not_none_values = filter(None.__ne__, keywords)
    keywords = list(Not_none_values)

    limit = 1000
    kwq = break_keywords(keywords,limit)

    outputKeywords = {}
    # For each set of 1000 keywords we make the API request
    for kw in kwq:
        if not kw or kw == '':
            continue
        q = kw

        try:
        #We make the API call
            response = getKwInfo(q,language,geo)
            for r in response['tasks'][0]['result']:
                if r['keyword'] not in outputKeywords:
                    outputKeywords[r['keyword']] = r['search_volume'] 
        except:
            break #mirar que quiero que haga aca

    return outputKeywords

def get_keywords_ideas_sv(keywords: list, outputKeywords: list, language: str, geo: str):
    # We can't request more that 20 keywords ideas per API call
    # New list with keywords in sets of 20
    Not_none_values = filter(None.__ne__, keywords)
    keywords = list(Not_none_values)

    limit = 20
    kwq = break_keywords(keywords,limit)

    # For each set of 20 keywords we make the API request
    for kw in kwq:
        if not kw or kw == '':
            continue
        q = kw

        #We make the API call
        try:
            response = getKwIdea(q,language,geo)
            for r in response['tasks'][0]['result']:
                if r['keyword'] not in outputKeywords:
                    outputKeywords[r['keyword']] = r['search_volume'] 
        except:
            break #mirar que quiero que haga aca

    return outputKeywords





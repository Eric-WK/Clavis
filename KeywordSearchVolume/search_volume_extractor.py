# helpful modules
from .kwsv_helpers import get_keywords_sv,get_keywords_ideas_sv


def run_search_volume(keywords: list, language: str, geo: str, ideas: bool):
    outputKeywords = get_keywords_sv(keywords, language, geo)
    if ideas:
        outputKeywords = get_keywords_ideas_sv(keywords, outputKeywords, language, geo)
    return outputKeywords
        

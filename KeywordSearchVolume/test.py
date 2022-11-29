from .search_volume_extractor import run_search_volume


keywords = ['mate','messi','argentina']
ideas = True
language = 'Spanish'
geo = 'Argentina'


results = run_search_volume(keywords,language,geo,ideas)

print(results)
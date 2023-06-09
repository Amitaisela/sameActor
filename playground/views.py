import imdb
import requests
from django.shortcuts import render
from django.http import HttpResponse
import datetime
import config

# Create your views here.
api_key = config.API_KEY
base_url = 'https://api.themoviedb.org/3'


def home(request):
    return render(request, 'home.html')


def getActors(request):
    return render(request, 'findActors.html', {'isEmpty': False})


def get_common_actors(request, movie_titles, htmlSite):
    ia = imdb.IMDb()
    movie_ids = []
    # find movies based on given title
    for title in movie_titles:
        search_results = ia.search_movie(title)
        if search_results:
            movie_id = search_results[0].getID()
            movie_ids.append(movie_id)
    common_actors = set()
    print("found movies")
    # if we have more than one movie. ( redundant )
    if len(movie_ids) > 0:
        # make sure that we have at least one actor in the set ( redundant )
        first_movie = ia.get_movie(movie_ids[0])
        common_actors.update([actor['name'] for actor in first_movie['cast']])

        # addes all the other actors from the other movies
        for movie_id in movie_ids[1:]:
            movie = ia.get_movie(movie_id)
            common_actors.intersection_update(
                [actor['name'] for actor in movie['cast']])

    results = list(common_actors)
    actorsDict = {}
    print("found actors")
    # find the rest of the information on the actors from the results list
    for result in results:
        search_url = f'{base_url}/search/person'
        params = {
            'api_key': api_key,
            'query': f'{result}'
        }

        response = requests.get(search_url, params=params)
        results = response.json()['results']

        # if for some reason the actor didnt have any info, continue to the next one
        if len(results) == 0:
            continue
        actor = results[0]
        details_url = f'{base_url}/person/{actor["id"]}'
        params = {'api_key': api_key}
        response = requests.get(details_url, params=params)
        actor_details = response.json()

        # find age
        if actor_details['birthday'] != None:
            date_format = '%Y-%m-%d'
            birth_date = datetime.datetime.strptime(
                actor_details['birthday'], date_format).date()
            today = datetime.date.today()
            age = today.year - birth_date.year - \
                ((today.month, today.day) < (birth_date.month, birth_date.day))
            age = "Age: " + str(age)
        else:
            age = "No age in DB"

        actorsDict[actor_details['name']] = [
            age, f'https://image.tmdb.org/t/p/w500{actor_details["profile_path"]}']
    print("found actors information")
    actorsDict = dict(sorted(actorsDict.items()))
    return render(request, htmlSite, {'my_dict': actorsDict})


def result(request):
    if request.method == 'POST':
        value1 = request.POST['value1']
        result = value1.split(";")
        if len(result) == 1:
            return render(request, 'findActors.html', {'isEmpty': True})
        return get_common_actors(request, movie_titles=result, htmlSite='result.html')
    else:
        return render(request, 'findActors.html', {'isEmpty': False})

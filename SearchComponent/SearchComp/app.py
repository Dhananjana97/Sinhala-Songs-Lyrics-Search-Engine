from flask import Flask, redirect, url_for, render_template, request, json
from sinling import word_splitter
import requests
app = Flask(__name__, template_folder='template')


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/result/<result>')
def res(result):
    print(result)
    lyrics = json.loads(result)

    return render_template('home.html', result=lyrics)


@app.route('/', methods=['POST'])
def admin():
    text = request.form['qry']
    searchResults = json.dumps(getSearchResults(text))
    text = None
    print(text)
    return redirect(url_for("res", result=searchResults))


def getSearchResults(text):

    # searching process keywords

    lyrics_by_keys = ['ලියූ', 'රචිත', 'ලියන ලද', 'ලිව්ව', 'ලියපු', 'ලියා ඇති', 'හැදුව',
                      'රචනා', 'ලියා', 'ලීව', 'හදපු', 'ලිඛිත', 'පද', 'පද මාලාව', 'රචනය', 'හැදූ', 'ලිව්']
    artist_keys = ['කිව්ව', 'කී', 'කියනු ලැබූ', 'ගැයු', 'ගැයූ', 'ගායනා කල', 'ගයනු ලැබූ', 'ගයන',
                   'කියපු', 'කීව', 'ගේ', 'හඩින්', 'ගායනය', 'කිව්', 'කියනා', 'ගායනා කරන', 'කිව', 'ගායනා']
    music_by_keys = ['සංගීතය', 'සංගීත', 'අධ්‍යක්ෂණය',
                     'සංගීතවත්', 'සංගීත', 'සංගීතමය', 'තනුව']
    movie_keys = ['චිත්‍රපට', 'සිනමා']
    genere_keys = ['පරණ', 'පොප්ස්', 'පොප්', 'පැරණි', 'ගෝල්ඩන් පොප්', 'පැරණි පොප්ස්',
                   'චිත්‍රපට', 'නව පොප්', 'කැලිප්සෝ', 'වත්මන්', 'ක්ලැසික්']
    popular_key = ['ජනප්රියම', 'ජනප්‍රිය', 'ජනප්‍රියම', 'ජනප්රිය', 'ප්‍රකට', 'ප්‍රසිද්ධ',
                   'හොඳම','හොදම','සුපිරි','' 'වැඩිපුරම බැලූ', 'වැඩිපුර බැලූ','ප්‍රසිද්දම','ප්‍රසිද්ද','ප්‍රසිද්ධම' 'වැඩිපුර', 'වැඩිපුරම']

    lyrics_by_avail = False
    artist_avail = False
    music_by_avail = False
    movie_avil = False
    genere_avail = False
    popular_avail = False

    keys_list = [lyrics_by_keys, artist_keys,
                 music_by_keys, movie_keys, genere_keys, popular_key]
    key_bool_list = [lyrics_by_avail, artist_avail,
                     music_by_avail, movie_avil, genere_avail, popular_avail]

    # split query, search tockens and process search query
    words_set = getWords(text)
    searchQry = " ".join(words_set)
    noOfRes = getNumbers(words_set)

    # search field selection and field boosting
    idx = 0
    for key_set in keys_list:
        if(len(set(words_set).intersection(key_set)) > 0):
            key_bool_list[idx] = True
        idx = idx+1

    search_fields = []

    if(key_bool_list[0]):
        lyrics_by_field = "lyrics by^3"
        search_fields.append(lyrics_by_field)
    else:
        lyrics_by_field = "lyrics by"
    if(key_bool_list[1]):
        artist_field = "artist^3"
        search_fields.append(artist_field)
    else:
        artist_field = "artist"
    if(key_bool_list[2]):
        music_field = "music by^3"
        search_fields.append(music_field)
    else:
        music_field = "music by"
    if(key_bool_list[3]):
        movie_field = "movie^3"
        search_fields.append(movie_field)
    else:
        movie_field = "movie"
    if(key_bool_list[4]):
        genere_field = "genere^3"
        search_fields.append(genere_field)
    else:
        genere_field = "genere"

    lyrics_field = "lyrics"
    name_field = "name"

    if(len(search_fields) == 0 and key_bool_list[5]==False):
        search_fields = [lyrics_by_field, artist_field, music_field,
                         movie_field, genere_field, lyrics_field, name_field]

    if(key_bool_list[5] and len(search_fields) == 0):

        reqBody = {
            "query": {
                "match_all": {}
            },
            "sort": {
                "views": {"order": "desc"}
            },
            "size": noOfRes,
            "aggs": {
                "name": {
                    "range": {
                        "field": "views",
                        "ranges": [
                            {
                                "from": 0,
                                "to": 200
                            },
                            {
                                "from": 200,
                                "to": 400
                            },
                            {
                                "from": 400,
                                "to": 600
                            },
                            {
                                "from": 600,
                                "to": 800
                            },
                            {
                                "from": 800,
                                "to": 1000
                            },

                        ]
                    }
                }
            }
        }

        response = requests.get(
            "http://localhost:9200/lyrics/_search", json=reqBody)
    

    elif(key_bool_list[5]):
        reqBody = {
            "query": {
                "multi_match": {
                    "type": "most_fields",
                    "query": searchQry,
                    "fields": search_fields
                }
            },
            "sort": {
                "views": {"order": "desc"}
            },
            "size": noOfRes,
            "aggs": {
                "name": {
                    "range": {
                        "field": "views",
                        "ranges": [
                            {
                                "from": 0,
                                "to": 200
                            },
                            {
                                "from": 200,
                                "to": 400
                            },
                            {
                                "from": 400,
                                "to": 600
                            },
                            {
                                "from": 600,
                                "to": 800
                            },
                            {
                                "from": 800,
                                "to": 1000
                            },

                        ]
                    }
                }
            }
        }

        response = requests.get(
            "http://localhost:9200/lyrics/_search", json=reqBody)
    else:
        reqBody = {
            "query": {
                "multi_match": {
                    "type": "most_fields",
                    "query": searchQry,
                    "fields": search_fields
                }
            },
            "sort": {
                "_score": {"order": "desc"}
            },
            "size": noOfRes,
            "aggs": {
                "name": {
                    "range": {
                        "field": "views",
                        "ranges": [
                            {
                                "from": 0,
                                "to": 200
                            },
                            {
                                "from": 200,
                                "to": 400
                            },
                            {
                                "from": 400,
                                "to": 600
                            },
                            {
                                "from": 600,
                                "to": 800
                            },
                            {
                                "from": 800,
                                "to": 1000
                            },

                        ]
                    }
                }
            }
        }
        response = requests.get(
            "http://localhost:9200/lyrics/_search", json=reqBody)

    return response.json()

# curl -XGET "http://localhost:9200/lyrics/_search" -H 'Content-Type: application/json' -d'{  "query": {    "multi_match" : {      "query":    "මිනිසුන්  ",      "fields": [ "lyrics"]     }  }}'


def getWords(text):
    wordSet = []
    words = text.split(" ")

    for word in words:
        if(len(word) > 7):
            splittedWords = word_splitter.split(word)
            base = splittedWords['base']
            affix = splittedWords['affix']
            wordSet.append(base)
            wordSet.append(affix)
        else:
            wordSet.append(word)

    return wordSet


def getNumbers(words_set):
    num = 10
    for word in words_set:
        if(word.isdigit()):
            num = word
            break

    return num


def get_agg_json():
    agg = {

    }

import math, sys
import xmltodict
import json
import requests

from ratelimit import limits, sleep_and_retry

LIMIT = 100
ROOT_URL = 'https://www.boardgamegeek.com/xmlapi2/thing?type=boardgame&ratingcomments=1&pagesize=100&id={}&page={}'

GAME_IDS = [96848, 102794, 164928, 177736, 31260, 175914, 205059, 170216, 221107, 266192, 55690, 209010, 2651, 25613, 164153, 126163, 72125, 230802, 237182, 35677, 171623, 121921, 216132, 124742, 185343, 68448, 28143, 122515, 62219, 18602, 159675, 110327, 157354, 12493, 205896, 93, 125153, 201808, 146021, 40834, 178900, 172386, 163412, 37111, 73439, 2511, 132531, 161533, 144733, 521, 42, 102680, 191189, 36218, 229853, 30549, 200680, 146508, 103885, 170042, 127023, 198928, 236457, 150376, 192135, 167355, 196340, 175155, 104162, 34635, 161970, 182874, 172287, 147020, 146652, 9609, 148949, 103343]

#GAME = int(sys.argv[1])
START = int(sys.argv[1])


@sleep_and_retry
@limits(calls=1, period=3)
def get_bgg_data(game_id, current_page):
    return xmltodict.parse(requests.get(ROOT_URL.format(game_id, current_page)).text)

def get_comments(game_id):
    # current_page = 1
    current_page = START

    uri = ROOT_URL.format(game_id, current_page)
    doc = xmltodict.parse(requests.get(uri).text)
    # print(json.dumps(doc))

    item = doc['items']['item']
    names = item['name']
    if isinstance(names, list):
        primary_name = names[0]['@value'] 
    else:
        primary_name = names['@value']
    f = open("comments_"+str(game_id)+".json", "a+")
    comments = item['comments']

    total_items = int(comments['@totalitems'])
    total_pages = math.ceil(float(total_items)/float(LIMIT))

    while current_page <= total_pages: 
        for c in comments['comment']:
            # convert to desired dict
            new_comment = {}
            new_comment['username'] = c['@username']
            new_comment['rating'] = float(c['@rating'])
            new_comment['comment'] = c['@value']
            new_comment['game'] = primary_name
            new_comment['game_id'] = game_id
            f.write(json.dumps(new_comment)+"\n")
 
        print('Progress ({}): {}/{} {}'.format(primary_name, current_page, total_pages, uri))

        if current_page+1 > total_pages:
            break

        doc = get_bgg_data(game_id, current_page+1)
        item = doc['items'].get('item')
        comments = item['comments']
        current_page = int(comments['@page'])
        uri = ROOT_URL.format(game_id, current_page)
        total_items = int(comments['@totalitems'])

    f.close()

if __name__ == '__main__':
    for gid in GAME_IDS:
        get_comments(gid)

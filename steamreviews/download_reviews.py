# Objective: download every Steam review for the games of your choice.
#
# Input:
#   - idlist.txt
#
# Output:
#   - idprocessed.txt
#   - data/review_APPID.json for each APPID in idlist.txt
#
# Reference:
#   https://raw.githubusercontent.com/CraigKelly/steam-data/master/data/games.py

import json
import pathlib
import time

import requests


def parse_app_id(app_id):
    # Objective: return an app_id as an integer, no matter whether the input app_id is a string or an integer.
    try:
        return int(str(app_id).strip())
    except ValueError:
        return None


def get_input_app_ids_filename():
    # Objective: return the filename where input app_ids are stored.
    return 'idlist.txt'


def app_id_reader(filename=None):
    # Objective: return a generator of the app_ids to process.

    if filename is None:
        filename = get_input_app_ids_filename()

    with open(filename, 'r') as f:
        for row in f.readlines():
            yield parse_app_id(row)


def get_processed_app_ids_filename(filename_root='idprocessed'):
    # Objective: return the filename where processed app_ids are saved.

    # Get current day as yyyymmdd format
    current_date = time.strftime('%Y%m%d')

    processed_app_ids_filename = filename_root + '_on_' + current_date + '.txt'

    return processed_app_ids_filename


def get_processed_app_ids():
    # Objective: return a set of all previously processed app_ids.

    processed_app_ids_filename = get_processed_app_ids_filename()

    all_app_ids = set()
    try:
        for app_id in app_id_reader(processed_app_ids_filename):
            all_app_ids.add(app_id)
    except FileNotFoundError:
        print('Creating ' + processed_app_ids_filename)
        pathlib.Path(processed_app_ids_filename).touch()
    return all_app_ids


def get_default_request_parameters():
    # Objective: return a dict of default paramters for a request to Steam API.
    #
    # Reference:
    #   https://gist.github.com/adambuczek/95906b0c899c5311daeac515f740bf33

    default_request_parameters = {
        'json': '1',
        'language': 'all',  # e.g. english or schinese
        'filter': 'recent',  # e.g. funny or helpful
        'review_type': 'all',
        'purchase_type': 'all',
    }

    return default_request_parameters


def get_data_path():
    # Objective: return the path to the directory where reviews are stored.

    data_path = 'data/'

    # Reference of the following line: https://stackoverflow.com/a/14364249
    pathlib.Path(data_path).mkdir(parents=True, exist_ok=True)

    return data_path


def get_steam_api_url():
    # Objective: return the url of Steam API for reviews.

    return 'http://store.steampowered.com/appreviews/'


def get_steam_api_rate_limits():
    # Objective: return the rate limits of Steam API for reviews.

    rate_limits = {
        'max_num_queries': 150,
        'cooldown': (5 * 60) + 10,  # 5 minutes plus a cushion
    }

    return rate_limits


def get_output_filename(app_id):
    return get_data_path() + 'review_' + str(app_id) + '.json'


def load_review_dict(app_id):
    review_data_filename = get_output_filename(app_id)

    try:
        with open(review_data_filename, 'r', encoding='utf8') as in_json_file:
            review_dict = json.load(in_json_file)
    except FileNotFoundError:
        review_dict = dict()
        review_dict['reviews'] = dict()

    return review_dict


def get_request(app_id):
    request = dict(get_default_request_parameters())
    request['appids'] = str(app_id)

    return request


def download_reviews_for_app_id_with_offset(app_id, offset=0):
    req_data = get_request(app_id)
    req_data['start_offset'] = str(offset)

    resp_data = requests.get(get_steam_api_url() + req_data['appids'], params=req_data)

    result = resp_data.json()

    success_flag = result['success']

    try:
        downloaded_reviews = result['reviews']
        query_summary = result['query_summary']
    except KeyError:
        success_flag = False
        downloaded_reviews = []
        query_summary = dict()

    return success_flag, downloaded_reviews, query_summary


def download_reviews_for_app_id(app_id, query_count=0):
    rate_limits = get_steam_api_rate_limits()

    review_dict = load_review_dict(app_id)

    previous_review_ids = review_dict['reviews']

    num_reviews = None

    offset = 0
    new_reviews = []

    while (num_reviews is None) or (offset < num_reviews):
        success_flag, downloaded_reviews, query_summary = download_reviews_for_app_id_with_offset(app_id, offset)

        if success_flag:
            new_reviews.extend(downloaded_reviews)
        else:
            break

        offset += len(downloaded_reviews)
        query_count += 1

        if num_reviews is None:
            review_dict['query_summary'] = query_summary
            num_reviews = query_summary['total_reviews']

        if query_count >= rate_limits['max_num_queries']:
            cooldown_duration = rate_limits['cooldown']
            print('Number of queries {} reached. Cooldown: {} seconds'.format(query_count, cooldown_duration))
            time.sleep(cooldown_duration)
            query_count = 0

        if any([review['recommendationid'] in previous_review_ids for review in downloaded_reviews]):
            break

    for review in new_reviews:
        review_id = review['recommendationid']
        if review_id not in previous_review_ids:
            review_dict['reviews'][review_id] = review

    with open(get_output_filename(app_id), 'w') as f:
        f.write(json.dumps(review_dict) + '\n')

    return review_dict, query_count


def download_reviews_for_app_id_batch(input_app_ids=None, previously_processed_app_ids=None):
    if input_app_ids is None:
        print('Loading {}'.format(get_input_app_ids_filename()))
        input_app_ids = [app_id for app_id in app_id_reader()]

    if previously_processed_app_ids is None:
        print('Loading {}'.format(get_processed_app_ids_filename()))
        previously_processed_app_ids = get_processed_app_ids()

    query_count = 0
    game_count = 0

    for app_id in input_app_ids:

        if app_id in previously_processed_app_ids:
            print('Skipping previously found appID = {}'.format(app_id))
            continue
        else:
            print('Downloading reviews for appID = {}'.format(app_id))

        review_dict, query_count = download_reviews_for_app_id(app_id, query_count)

        game_count += 1

        with open(get_processed_app_ids_filename(), 'a') as f:
            f.write(str(app_id) + '\n')

        print('[appID = {}] num_reviews = {} (expected: {})'.format(app_id, len(review_dict['reviews']),
                                                                    review_dict['query_summary']['total_reviews']))

    print('Game records written: {}'.format(game_count))

    return True


if __name__ == '__main__':
    # noinspection PyTypeChecker
    download_reviews_for_app_id_batch(input_app_ids=None, previously_processed_app_ids=None)

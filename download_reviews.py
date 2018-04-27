#!/usr/env/bin python

"""Create idprocessed.txt, and data/review_APPID.json for each APPID in idlist.txt."""

# Heavily inspired from: https://raw.githubusercontent.com/CraigKelly/steam-data/master/data/games.py

import csv
import json
import time
import requests
import logging
import os.path

def parse_id(i):
    """Since we deal with both strings and ints, force appid to be correct."""
    try:
        return int(str(i).strip())
    except ValueError:
        return None


def id_reader():
    """Read the previous created idlist.txt."""
    with open("idlist.txt") as basefile:
        reader = csv.reader(basefile)
        for row in reader:
            yield parse_id(row[0])

def get_id_processed_filename(use_date = True):
    import time

    # Get current day as yyyymmdd format
    date_format = "%Y%m%d"
    current_date = time.strftime(date_format)

    if use_date:
        id_processed_filename = "idprocessed_on_" + current_date + ".txt"
    else:
        id_processed_filename = "idprocessed.txt"

    return id_processed_filename

def previous_results():
    """Return a set of all previous found ID's."""
    temp_filename = get_id_processed_filename()
    all_ids = set()
    try:
        with open(temp_filename, "r") as f:
            for line in f:
                appid = parse_id(line)
                if appid:
                    all_ids.add(appid)
    except FileNotFoundError:
        with open(temp_filename, "w") as f:
            print('Creating ' + temp_filename)
    return all_ids


def main(download_reference_hidden_gems_as_well = False):
    """Entry point."""

    from appids import appid_hidden_gems_reference_set

    import pathlib

    # Data folder
    data_path = "data/"
    # Reference of the following line: https://stackoverflow.com/a/14364249
    pathlib.Path(data_path).mkdir(parents=True, exist_ok=True)

    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger('requests').setLevel(logging.DEBUG)
    log = logging.getLogger(__name__)

    defaults = {
        # Copied from: https://gist.github.com/adambuczek/95906b0c899c5311daeac515f740bf33
        'json': '1',
        'language': "all",  # e.g. english or schinese
        'filter': "recent",  # e.g. funny or helpful
        'review_type': "all",
        'purchase_type': "all",
    }
    log.info("Default parameters: %s", repr(defaults))

    api_url = "http://store.steampowered.com/appreviews/"
    query_limit = 150
    wait_time = (5 * 60) + 10  # 5 minutes plus a cushion

    # Initialization of maximal number of reviews with a large number
    # NB: Any number greater than 20 should have been ok, since:
    #   - this variable will be overrided after the first API request,
    #   - an API request cannot return more than 20 reviews (or so, I read).
    max_num_reviews = pow(10, 4)

    log.info("Getting previous results from " + get_id_processed_filename())
    previos_ids = previous_results()

    log.info("Opening " + get_id_processed_filename())
    query_count = 0
    game_count = 0
    game = dict()

    temp_filename = get_id_processed_filename()

    log.info("Opening idlist.txt")
    appid_list = [appid for appid in id_reader()]

    if download_reference_hidden_gems_as_well:
        appid_list = list(set(appid_list).union(appid_hidden_gems_reference_set))

    for appid in appid_list:

        output_file = "review_" + str(appid) + ".json"
        data_filename = data_path + output_file

        if os.path.isfile(data_filename):
            if appid in previos_ids:
                log.info("Skipping previously found id %d", appid)
                continue
            else:
                log.info("Updating previously found id %d", appid)

        try:
            with open(data_filename, 'r', encoding="utf8") as in_json_file:
                review_dict = json.load(in_json_file)
        except:
            review_dict = dict()
            review_dict["reviews"] = dict()

        previous_reviewIDs = set( review_dict["reviews"].keys() )

        url = api_url + str(appid)

        req_data = dict(defaults)
        req_data['appids'] = str(appid)

        new_reviews = []

        # Initialize
        offset = 0
        num_reviews = max_num_reviews
        try_count = 0
        while (offset < num_reviews) and (try_count < 3):
            req_data['start_offset'] = str(offset)

            resp_data = requests.get(url, params=req_data)

            result = resp_data.json()

            request_success_flag = result['success']

            try:
                downloaded_reviews = result["reviews"]
                new_reviews.extend(downloaded_reviews)
            except KeyError:
                print('\nThe request returned an empty response with flag: ', str(request_success_flag) + '\n')
                break

            num_reviews_with_this_request = result["query_summary"]["num_reviews"]
            offset += num_reviews_with_this_request

            if num_reviews_with_this_request == 0:
                try_count += 1

            if num_reviews == max_num_reviews:
                # Real number of reviews for the given appID
                num_reviews = result["query_summary"]["total_reviews"]

                print(result["query_summary"])

                # To be saved to JSON
                review_dict["query_summary"] = result["query_summary"]

            query_count += 1

            if query_count >= query_limit:
                log.info("query count is %d, waiting for %d secs", query_count, wait_time)
                time.sleep(wait_time)
                query_count = 0

            if any([ review["recommendationid"] in previous_reviewIDs for review in downloaded_reviews ]):
                break

        for review in [r for r in new_reviews if r["recommendationid"] not in previous_reviewIDs]:
            reviewID = review["recommendationid"]
            review_dict["reviews"][reviewID] = review

        with open(data_filename, "w") as g:
            g.write(json.dumps(review_dict) + '\n')

        log.info("Review records written for %s: %d (expected: %d)",
                 appid, len(review_dict["reviews"]), num_reviews)

        game_count += 1

        with open(temp_filename, "a") as f:
            f.write(str(appid) + '\n')

    log.info("Game records written: %d", game_count)


if __name__ == "__main__":
    download_reference_hidden_gems_as_well = True
    main(download_reference_hidden_gems_as_well)

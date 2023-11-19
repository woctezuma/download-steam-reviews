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

import copy
import datetime
import json
import pathlib
import time
from http import HTTPStatus
from pathlib import Path

import requests


def parse_app_id(app_id):
    # Objective: return an app_id as an integer, no matter whether the input app_id is a string or an integer.
    try:
        return int(str(app_id).strip())
    except ValueError:
        return None


def get_input_app_ids_filename() -> str:
    # Objective: return the filename where input app_ids are stored.
    return "idlist.txt"


def app_id_reader(filename=None):
    # Objective: return a generator of the app_ids to process.

    if filename is None:
        filename = get_input_app_ids_filename()

    with Path(filename).open() as f:
        for row in f.readlines():
            yield parse_app_id(row)


def get_processed_app_ids_filename(filename_root="idprocessed"):
    # Objective: return the filename where processed app_ids are saved.

    # Get current day as yyyymmdd format
    current_date = time.strftime("%Y%m%d")

    return filename_root + "_on_" + current_date + ".txt"


def get_processed_app_ids():
    # Objective: return a set of all previously processed app_ids.

    processed_app_ids_filename = get_processed_app_ids_filename()

    all_app_ids = set()
    try:
        for app_id in app_id_reader(processed_app_ids_filename):
            all_app_ids.add(app_id)
    except FileNotFoundError:
        print("Creating " + processed_app_ids_filename)
        pathlib.Path(processed_app_ids_filename).touch()
    return all_app_ids


def get_default_review_type() -> str:
    # Reference: https://partner.steamgames.com/doc/store/getreviews
    return "all"


def get_default_request_parameters(chosen_request_params=None):
    # Objective: return a dict of default paramters for a request to Steam API.
    #
    # References:
    #   https://partner.steamgames.com/doc/store/getreviews
    #   https://partner.steamgames.com/doc/store/localization#supported_languages
    #   https://gist.github.com/adambuczek/95906b0c899c5311daeac515f740bf33

    default_request_parameters = {
        "json": "1",
        "language": "all",  # API language code e.g. english or schinese
        "filter": "recent",  # To work with 'start_offset', 'filter' has to be set to either recent or updated, not all.
        "review_type": "all",  # e.g. positive or negative
        "purchase_type": "all",  # e.g. steam or non_steam_purchase
        "num_per_page": "100",  # default is 20, maximum is 100
    }

    if chosen_request_params is not None:
        for element in chosen_request_params:
            default_request_parameters[element] = chosen_request_params[element]

    return default_request_parameters


def get_data_path():
    # Objective: return the path to the directory where reviews are stored.

    data_path = "data/"

    # Reference of the following line: https://stackoverflow.com/a/14364249
    pathlib.Path(data_path).mkdir(parents=True, exist_ok=True)

    return data_path


def get_steam_api_url() -> str:
    # Objective: return the url of Steam API for reviews.

    return "https://store.steampowered.com/appreviews/"


def get_steam_api_rate_limits():
    # Objective: return the rate limits of Steam API for reviews.

    return {
        "max_num_queries": 150,
        "cooldown": (5 * 60) + 10,  # 5 minutes plus a cushion
        "cooldown_bad_gateway": 10,  # arbitrary value to tackle 502 Bad Gateway due to saturated servers (during sales)
    }


def get_output_filename(app_id):
    return get_data_path() + "review_" + str(app_id) + ".json"


def get_dummy_query_summary():
    query_summary = {}
    query_summary["total_reviews"] = -1

    return query_summary


def load_review_dict(app_id):
    review_data_filename = get_output_filename(app_id)

    try:
        with Path(review_data_filename).open(encoding="utf8") as in_json_file:
            review_dict = json.load(in_json_file)

        # Compatibility with data downloaded with previous versions of steamreviews:
        if "cursors" not in review_dict:
            review_dict["cursors"] = {}
    except FileNotFoundError:
        review_dict = {}
        review_dict["reviews"] = {}
        review_dict["query_summary"] = get_dummy_query_summary()
        review_dict["cursors"] = {}

    return review_dict


def get_request(app_id, chosen_request_params=None):
    request = dict(get_default_request_parameters(chosen_request_params))
    request["appids"] = str(app_id)

    return request


def download_the_full_query_summary(
    app_id,
    query_count,
    chosen_request_params,
    override_total_reviews=True,
):
    try:
        original_review_type = chosen_request_params["review_type"]
    except KeyError:
        original_review_type = None

    # Override the filtering by review type:
    # Reference: https://stackoverflow.com/a/5105554/
    overriden_params = copy.deepcopy(chosen_request_params)
    overriden_params["review_type"] = get_default_review_type()
    # Otherwise, the query summary would miss the fields:
    # - 'total_positive' (total number of positive reviews),
    # - 'total_negative' (total number of negative reviews),
    # - 'total_reviews' (total number of reviews),
    # and query summary would only contain the field 'num_reviews' (number of reviews downloaded with the GET request).

    (
        success_flag,
        downloaded_reviews,
        query_summary,
        query_count,
        next_cursor,
    ) = download_reviews_for_app_id_with_offset(
        app_id,
        query_count,
        chosen_request_params=overriden_params,
    )

    if (
        override_total_reviews
        and original_review_type is not None
        and original_review_type != get_default_review_type()
    ):
        # Either 'total_positive' or 'total_negative'
        total_str = "total_" + original_review_type
        # Override the total number of reviews with the total number of reviews of the chosen type:
        query_summary["total_reviews"] = query_summary[total_str]

    return success_flag, query_summary, query_count


def download_reviews_for_app_id_with_offset(
    app_id,
    query_count,
    cursor="*",
    chosen_request_params=None,
):
    rate_limits = get_steam_api_rate_limits()

    req_data = get_request(app_id, chosen_request_params)
    req_data["cursor"] = str(cursor)

    resp_data = requests.get(get_steam_api_url() + req_data["appids"], params=req_data)
    status_code = resp_data.status_code
    query_count += 1

    while (status_code == HTTPStatus.BAD_GATEWAY) and (
        query_count < rate_limits["max_num_queries"]
    ):
        cooldown_duration_for_bad_gateway = rate_limits["cooldown_bad_gateway"]
        print(
            "{} Bad Gateway for appID = {} and cursor = {}. Cooldown: {} seconds".format(
                status_code,
                app_id,
                cursor,
                cooldown_duration_for_bad_gateway,
            ),
        )
        time.sleep(cooldown_duration_for_bad_gateway)

        resp_data = requests.get(
            get_steam_api_url() + req_data["appids"],
            params=req_data,
        )
        status_code = resp_data.status_code
        query_count += 1

    if status_code == HTTPStatus.OK:
        result = resp_data.json()
    else:
        result = {"success": 0}
        print(
            "Faulty response status code = {} for appID = {} and cursor = {}".format(
                status_code,
                app_id,
                cursor,
            ),
        )

    success_flag = bool(result["success"] == 1)

    try:
        downloaded_reviews = result["reviews"]
        query_summary = result["query_summary"]
        next_cursor = result["cursor"]
    except KeyError:
        success_flag = False
        downloaded_reviews = []
        query_summary = get_dummy_query_summary()
        next_cursor = cursor

    return success_flag, downloaded_reviews, query_summary, query_count, next_cursor


def download_reviews_for_app_id(
    app_id,
    query_count=0,
    chosen_request_params=None,
    start_cursor="*",  # this could be useful to resume a failed download of older reviews
    verbose=False,
):
    rate_limits = get_steam_api_rate_limits()

    request = dict(get_default_request_parameters(chosen_request_params))
    check_review_timestamp = bool(
        "day_range" in request and request["filter"] != "all",
    )
    if check_review_timestamp:
        current_date = datetime.datetime.now(tz=datetime.UTC)
        num_days = int(request["day_range"])
        date_threshold = current_date - datetime.timedelta(days=num_days)
        timestamp_threshold = datetime.datetime.timestamp(date_threshold)
        if verbose:
            if request["filter"] == "updated":
                collection_keyword = "edited"
            else:
                collection_keyword = "first posted"
            print(
                f"Collecting reviews {collection_keyword} after {date_threshold}",
            )

    review_dict = load_review_dict(app_id)

    previous_review_ids = set(review_dict["reviews"])

    num_reviews = None

    offset = 0
    cursor = start_cursor
    new_reviews = []
    new_review_ids = set()

    while (num_reviews is None) or (offset < num_reviews):
        if verbose:
            print(f"Cursor: {cursor}")

        (
            success_flag,
            downloaded_reviews,
            query_summary,
            query_count,
            cursor,
        ) = download_reviews_for_app_id_with_offset(
            app_id,
            query_count,
            cursor,
            chosen_request_params,
        )

        delta_reviews = len(downloaded_reviews)

        offset += delta_reviews

        if success_flag and delta_reviews > 0:
            if check_review_timestamp:
                if request["filter"] == "updated":
                    timestamp_str_field = "timestamp_updated"
                else:
                    timestamp_str_field = "timestamp_created"

                checked_reviews = list(
                    filter(
                        lambda x: x[timestamp_str_field] > timestamp_threshold,
                        downloaded_reviews,
                    ),
                )

                delta_checked_reviews = len(checked_reviews)

                if delta_checked_reviews == 0:
                    if verbose:
                        print(
                            "Exiting the loop to query Steam API, because the timestamp threshold was reached.",
                        )
                    break

                downloaded_reviews = checked_reviews

            new_reviews.extend(downloaded_reviews)

            downloaded_review_ids = [
                review["recommendationid"] for review in downloaded_reviews
            ]

            # Detect full redundancy in the latest downloaded reviews
            if new_review_ids.issuperset(downloaded_review_ids):
                if verbose:
                    print(
                        "Exiting the loop to query Steam API, because this request only returned redundant reviews.",
                    )
                break

            new_review_ids = new_review_ids.union(downloaded_review_ids)

        else:
            if verbose:
                print(
                    "Exiting the loop to query Steam API, because this request failed.",
                )
            break

        if num_reviews is None:
            if "total_reviews" not in query_summary:
                (
                    success_flag,
                    query_summary,
                    query_count,
                ) = download_the_full_query_summary(
                    app_id,
                    query_count,
                    chosen_request_params,
                )

            review_dict["query_summary"] = query_summary
            # Initialize num_reviews with the correct value (this is crucial for the loop, do not change variable name):
            num_reviews = query_summary["total_reviews"]
            # Also rely on num_reviews for display:
            print(f"[appID = {app_id}] expected #reviews = {num_reviews}")

        if query_count >= rate_limits["max_num_queries"]:
            cooldown_duration = rate_limits["cooldown"]
            print(
                "Number of queries {} reached. Cooldown: {} seconds".format(
                    query_count,
                    cooldown_duration,
                ),
            )
            time.sleep(cooldown_duration)
            query_count = 0

        if not previous_review_ids.isdisjoint(downloaded_review_ids):
            if verbose:
                print(
                    "Exiting the loop to query Steam API, because this request partially returned redundant reviews.",
                )
            break

    # Keep track of the date (in string format) associated with the cursor at save time.
    review_dict["cursors"][str(cursor)] = time.asctime()

    for review in new_reviews:
        review_id = review["recommendationid"]
        if review_id not in previous_review_ids:
            review_dict["reviews"][review_id] = review

    with Path(get_output_filename(app_id)).open("w") as f:
        f.write(json.dumps(review_dict) + "\n")

    return review_dict, query_count


def download_reviews_for_app_id_batch(
    input_app_ids=None,
    previously_processed_app_ids=None,
    chosen_request_params=None,
    verbose=False,
) -> bool:
    if input_app_ids is None:
        print(f"Loading {get_input_app_ids_filename()}")
        input_app_ids = list(app_id_reader())

    if previously_processed_app_ids is None:
        print(f"Loading {get_processed_app_ids_filename()}")
        previously_processed_app_ids = get_processed_app_ids()

    query_count = 0
    game_count = 0

    for app_id in input_app_ids:
        if app_id in previously_processed_app_ids:
            print(f"Skipping previously found appID = {app_id}")
            continue

        print(f"Downloading reviews for appID = {app_id}")

        review_dict, query_count = download_reviews_for_app_id(
            app_id,
            query_count,
            chosen_request_params,
            verbose=verbose,
        )

        game_count += 1

        with Path(get_processed_app_ids_filename()).open("a") as f:
            f.write(str(app_id) + "\n")

        num_downloaded_reviews = len(review_dict["reviews"])
        num_expected_reviews = review_dict["query_summary"]["total_reviews"]
        print(
            "[appID = {}] num_reviews = {} (expected: {})".format(
                app_id,
                num_downloaded_reviews,
                num_expected_reviews,
            ),
        )

    print(f"Game records written: {game_count}")

    return True


if __name__ == "__main__":
    # noinspection PyTypeChecker
    download_reviews_for_app_id_batch(
        input_app_ids=None,
        previously_processed_app_ids=None,
        verbose=False,
    )

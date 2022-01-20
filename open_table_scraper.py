from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
from util import calc_distance, normalize


def generate_restaurant_url(latitude, longitude):
    """Generate a url string with coordinates information for web scraping

    :param latitude: latitude of a house
    :param longitude: longitude of a house
    :return: A concatenated url string
    """
    base_url = r"https://www.opentable.com/s?"
    url = f"{base_url}latitude={latitude}&longitude={longitude}"
    return url


def get_restaurant_dataframe(url, save_csv=False, save_path=None):
    """Organize and extract information of restaurants from web page using BeautilfulSoup

    :param url: The url for web scraping
    :param save_csv: Whether save the dataframe to a csv file
    :param save_path: If save, then the path for the csv file
    :return: The dataframe object
    """
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    restaurant_str = list(soup.body.children)[1].string

    left_start = restaurant_str.find("\"restaurants\":[") + 15  # Count the length of "restaurants":[
    right_start = restaurant_str.rfind(",\"totalRestaurantCount\"") - 1  # Count the length of ]
    restaurant_str = restaurant_str[left_start:right_start]

    # Change the key words in JavaScript to Python
    restaurant_str = restaurant_str.replace("true", "True")
    restaurant_str = restaurant_str.replace("false", "False")
    restaurant_str = restaurant_str.replace("null", "None")

    # Parse the json string to a dict object
    restaurants = eval(restaurant_str)

    # Merge all the restaurants
    restaurant_dict = {}
    for restaurant in restaurants:
        for key in restaurant.keys():
            if key in restaurant_dict.keys():
                restaurant_dict[key].append(restaurant[key])
            else:
                restaurant_dict[key] = [restaurant[key]]

    restaurant_df = pd.DataFrame(restaurant_dict)
    restaurant_df = transform_restaurant_dataframe(restaurant_df)

    if save_csv:
        assert save_path, "If you want to save the restaurants' information as csv files, " \
                          "you need to pass `save_path` parameter"
        save_path += "/rest_data.csv" if not save_path.endswith(r".csv") else ""
        restaurant_df.to_csv(save_path, index=False)

    return restaurant_df


def transform_restaurant_dataframe(restaurant_df):
    """ Transform the dataframe to an ideal form

    The modified columns:
        urls: Only keep the `link` key-value pair and remove others
        priceBand: Only keep the `name` key-value pair and remove others
        neighborhood: Only keep the `name` key-value pair and remove others
        statistics: Split this column to `recentReservationCount`, `allTimeTextReviewCount` and `Ratings`,
                    and drop this column
        primaryCuisine: Only keep the `name` key-value pair and remove others
        campaignId: dropped
        features: Split this column to `hasBar`, `hasCounter`, `hasHighTop`, `hasOutdoor` and `pickupEnabled`,
                  and drop this column
        restaurantAvailabilityToken: dropped
        groups: dropped
        __typename: dropped
        isPinned: dropped
        photos: dropped
        justAddedDetails: dropped
        offers: dropped
        coordinates: Split this column into `latitude` and `longitude`, and drop this column
        description: Replace some invalid characters
        highlightedText: extract 'highlightedText' column and remove others
        matchRelevance: dropped
        contactInformation: extract 'formattedPhoneNumber' column and remove others
        deliveryPartners: extract 'deliveryPartnerName' column and remove others

    :param restaurant_df: The dataframe before transformation
    :return: The dataframe after transformation
    """

    # urls
    restaurant_df["urls"] = restaurant_df["urls"].apply(lambda line: line["profileLink"]["link"])
    # priceBand
    restaurant_df["priceBand"] = restaurant_df["priceBand"].apply(lambda line: line["name"])
    # neighborhood
    restaurant_df["neighborhood"] = restaurant_df["neighborhood"].apply(lambda line: line["name"])
    # statistics
    restaurant_df["recentReservationCount"] = restaurant_df["statistics"]\
        .apply(lambda line: line["recentReservationCount"])
    restaurant_df["recentReservationCount"] = restaurant_df["recentReservationCount"].fillna(0)
    restaurant_df["allTimeTextReviewCount"] = restaurant_df["statistics"]\
        .apply(lambda line: line["reviews"]["allTimeTextReviewCount"])
    restaurant_df["ratings"] = restaurant_df["statistics"]\
        .apply(lambda line: line["reviews"]["ratings"]["overall"]["rating"])
    restaurant_df = restaurant_df.drop("statistics", axis=1, inplace=False)
    # primaryCuisine
    restaurant_df["primaryCuisine"] = restaurant_df["primaryCuisine"].apply(lambda line: line["name"])
    # campaignId
    restaurant_df = restaurant_df.drop("campaignId", axis=1, inplace=False)
    # features
    restaurant_df["hasBar"] = restaurant_df["features"].apply(lambda line: line["bar"])
    restaurant_df["hasCounter"] = restaurant_df["features"].apply(lambda line: line["counter"])
    restaurant_df["hasHighTop"] = restaurant_df["features"].apply(lambda line: line["highTop"])
    restaurant_df["hasOutdoor"] = restaurant_df["features"].apply(lambda line: line["outdoor"])
    restaurant_df["pickupEnabled"] = restaurant_df["features"].apply(lambda line: line["pickupEnabled"])
    restaurant_df = restaurant_df.drop("features", axis=1, inplace=False)
    # restaurantAvailabilityToken
    restaurant_df = restaurant_df.drop("restaurantAvailabilityToken", axis=1, inplace=False)
    # groups
    restaurant_df = restaurant_df.drop("groups", axis=1, inplace=False)
    # __typename
    restaurant_df = restaurant_df.drop("__typename", axis=1, inplace=False)
    # isPinned
    restaurant_df = restaurant_df.drop("isPinned", axis=1, inplace=False)
    # photos
    restaurant_df = restaurant_df.drop("photos", axis=1, inplace=False)
    # justAddedDetails
    restaurant_df = restaurant_df.drop("justAddedDetails", axis=1, inplace=False)
    # offers
    restaurant_df = restaurant_df.drop("offers", axis=1, inplace=False)
    # coordinates
    restaurant_df["latitude"] = restaurant_df["coordinates"].apply(lambda line: line["latitude"])
    restaurant_df["longitude"] = restaurant_df["coordinates"].apply(lambda line: line["longitude"])
    restaurant_df = restaurant_df.drop("coordinates", axis=1, inplace=False)
    # address
    restaurant_df["address"] = restaurant_df["address"]\
        .apply(lambda line: ", ".join([line["line1"], line["line2"], line["city"], line["state"], line["postCode"]])
               if line["line2"] else ", ".join([line["line1"], line["city"], line["state"], line["postCode"]]))
    # topReview
    restaurant_df["topReview"] = restaurant_df["topReview"].apply(
        lambda line: line["highlightedText"] if line else None)
    # matchRelevance
    restaurant_df = restaurant_df.drop("matchRelevance", axis=1, inplace=False)
    # contactInformation
    restaurant_df["contactInformation"] = restaurant_df["contactInformation"].apply(
        lambda line: line["formattedPhoneNumber"] if line else None)
    # deliveryPartners
    restaurant_df["deliveryPartners"] = restaurant_df["deliveryPartners"].apply(
        lambda line: line[0]["deliveryPartnerName"] if line else None)

    return restaurant_df


def filter_by_distance_func(restaurant_df, distance, house_coordinates):
    """Filter the restaurant dataframe by the distance between the house and the restaurant

    :param restaurant_df: The restaurant dataframes with all the information
    :param distance: The range for searching, IN MILES !!
    :param house_coordinates: The tuple of latitude and longitude pair of the house
    :return: The dataframe of restaurants in the range
    """
    km_distance = distance * 1.609344
    restaurant_df["distance"] = restaurant_df.apply(
        lambda row: calc_distance((row["latitude"], row["longitude"]), house_coordinates)/1000, axis=1)
    result_df = restaurant_df[restaurant_df["distance"] <= km_distance].reset_index()

    return result_df


def calculate_restaurant_score(row):
    """Calculate the score of a restaurant with a customized formula

    Given function s(var) = 1 if var == True else 0 and n(var) is the normalization function

    score = [ratings^2*(1 + s(hasBar) + s(hasCounter) + s(hasHighTop) + s(hasOutdoor) + s(pickupEnabled)
             + s(deliveryPartners) + s(hasTakeout) + n(recentReservationCount) + n(allTimeTextReviewCount))] /
             (sqrt(n(distance)))

    Overall, this scoring mechanism recommends the restaurants with bar, counter, etc. , and a higher rating by user,\
             In additions, this formula favors the restaurants in a shorter distance

    :param row: A line of DataFrame, should be a pd.Series object
                Note that the data in the row should already been normalized before invoking this function
    :return: A score of float type
    """

    rating_ratio = row["ratings"] ** 2
    distance_ratio = np.sqrt(row["distance"])

    def s(obj):
        if obj:
            return 1
        else:
            return 0

    stats = 1 + s(row["hasBar"]) + s(row["hasCounter"]) + s(row["hasHighTop"]) + s(row["hasOutdoor"]) + \
            s(row["pickupEnabled"]) + s(row["deliveryPartners"]) + s(row["hasTakeout"]) + \
            row["recentReservationCount"] + row["allTimeTextReviewCount"]

    score = stats * rating_ratio / distance_ratio

    return score


def calculate_table_score(rest_df):
    """Calculate the score of the dataframe by adding the score of each restaurant

    This mechanism favors the house surrounded by more restaurants

    :param rest_df: The restaurant dataframe
    :return: The score, the restaurant dataframe with score as the final column
    """
    cal_df = rest_df.copy()

    if cal_df.shape[0] == 0:
        print("Sorry, we don't find any restaurants matched with your requirement.")
        return

    cal_df["recentReservationCount"] = normalize(cal_df["recentReservationCount"])
    cal_df["allTimeTextReviewCount"] = normalize(cal_df["allTimeTextReviewCount"])

    rest_df["score"] = cal_df.apply(calculate_restaurant_score, axis=1)

    return np.sum(rest_df["score"]), rest_df


def generate_restaurant_score(house_latitute, house_longitude, filter_by_distance=True, search_range=3,
                              sort=True, top_k=100, save_csv=False, save_path=None):
    """ Encapsulate everything in one function

    Enter the latitude and longitude of the house, and then return a dataframe of recommended restaurants
    and their scores, with an averaged total score

    Note that this score has not been normalized, and should be normalized with other houses' recommendation result

    :param house_latitute: The latitude of the house
    :param house_longitude: The longitude of the house
    :param filter_by_distance: Whether to filter the restaurants with a given range
    :param search_range: If to filter the restaurants, this is the distance range, we will keep all the restaurants
                         in this range
    :param sort: Whether to sort the restaurants by their scores
    :param top_k: Restaurants with top K score
    :param save_csv: Whether to save the dataframe to a csv file
    :param save_path: If so, this is the path for saving the csv file
    :return: The averaged total score of all the recommended restaurants, their corresponding information in a df
    """

    url = generate_restaurant_url(house_latitute, house_longitude)
    rest_df = get_restaurant_dataframe(url, save_csv=save_csv, save_path=save_path)

    if filter_by_distance:
        rest_df = filter_by_distance_func(rest_df, search_range, (house_latitute, house_longitude))

    result = calculate_table_score(rest_df)
    if result is None:
        return
    else:
        table_score, rest_df = result

    if sort:
        rest_df = rest_df.sort_values("score", ascending=False).reset_index()

    if sort and top_k < rest_df.shape[0]:
        rest_df = rest_df.head(top_k)

    return table_score, rest_df


if __name__ == '__main__':
    score, df = generate_restaurant_score(40.448328, -79.9304626)
    print(score)
    print(df)
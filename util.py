from math import radians, cos, sin, asin, sqrt
import os


def normalize(col):
    """Scaling all the values in the series between 50 and 100

    new_value = 50 + ((col - min_value) / (max_value - min_value)) * 50

    :param col: a column of the dataframe, should be an Iterable
    :return: The column after normalization
    """
    min_value = min(col)
    max_value = max(col)
    return 65 + ((col - min_value) / (max_value - min_value)) * 35


def calc_distance(pair1, pair2):
    # input 2 coordinate pairs in the format of (latitude,longitude)
    # Haversine method
    lat1 = float(pair1[0])
    lon1 = float(pair1[1])
    lat2 = float(pair2[0])
    lon2 = float(pair2[1])
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    distance = 2 * asin(sqrt(a)) * 6371 * 1000
    distance = round(distance, 3)
    return distance


def check_path(path):
    """Check if the path exists, if not then create it

    :param path: A given path
    """
    if not os.path.exists(path):
        os.makedirs(path)


def check_numerical_input(user_input, mode="int", max_input=None, min_input=None):
    """Check if the input could be converted into an integer value

    If `max` or `min` is given, then this function will check if `user_input` is in the range

    :param user_input: Input from user to convert into integers
    :param mode: `int` or `float`
    :param max_input: The max value for user input, default None
    :param min_input: The min value for user input, default None
    :return: The integer value after converting
    """

    while True:
        try:
            user_input = user_input.replace("%", "") if user_input.endswith("%") else user_input
            if mode == "int":
                user_input = user_input.split(".")[0] if "." in user_input else user_input
                user_input = int(user_input)
            elif mode == "float":
                user_input = float(user_input)

            if max_input is not None and min_input is not None and max_input == min_input and max_input == user_input:
                return user_input
            elif max_input is not None and min_input is not None and max_input == min_input and max_input != user_input:
                if mode == "int":
                    print("Your input must be %d, please try again." % min_input)
                else:
                    print("Your input must be %.2f, please try again." % min_input)
                user_input = input("\nYour last input is not valid, please input again: ")
                continue
            elif max_input is not None and min_input is not None and min_input <= user_input <= max_input:
                return user_input
            elif max_input is not None and min_input is not None and (min_input > user_input or max_input < user_input):
                if mode == "int":
                    print("Your input must be between %d and %d, please try again." % (min_input, max_input))
                else:
                    print("Your input must be betteen %.2f and %.2f, please try again." % (min_input, max_input))
                user_input = input("\nYour last input is not valid, please input again: ")
                continue
            elif max_input is not None and user_input <= max_input:
                return user_input
            elif max_input is not None and user_input > max_input:
                if mode == "int":
                    print("Your input must be less than %d, please try again.".format(max_input))
                else:
                    print("Your input must be less than %.2f, please try again.".format(max_input))
                user_input = input("\nYour last input is not valid, please input again: ")
                continue
            elif min_input is not None and user_input >= min_input:
                return user_input
            elif min_input is not None and user_input < min_input:
                if mode == "int":
                    print("Your input must be greater than %d, please try again.".format(min_input))
                else:
                    print("Your input must be greater than %.2f, please try again.".format(min_input))
                user_input = input("\nYour last input is not valid, please input again: ")
                continue
        except:
            user_input = input("\nYour last input is not valid, please input again: ")


def check_yes_no(user_input):

    while True:
        if user_input.strip() in ["Yes", "yes", "YES", "y"]:
            return True
        elif user_input.strip() in ["No", "no", "NO", "n"]:
            return False
        else:
            user_input = input("Your input must be `Yes` or `No`. Please try again.")

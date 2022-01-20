from util import check_numerical_input, check_yes_no


def handle_user_input():
    print("Please set your preferences in percent number for the following three criteria.")
    print("1. Good Restaurants")
    print("2. Entertainment Places (shoppings, parks, nightclubs etc.)")
    print("3. High Transportation Accessibility")
    print("The sum of all input numbers should be 100%\n")

    res = input('Good Restaurants:')
    res = res.replace("%", "") if res.endswith("%") else res
    res = check_numerical_input(res, min_input=0, max_input=100, mode="int")
    shopping = input('Entertainment:')
    shopping = shopping.replace("%", "") if shopping.endswith("%") else shopping
    shopping = check_numerical_input(shopping, min_input=0, max_input=100 - res, mode="int")
    trans = input('Transportation Accessibility (%d%%):' % (100 - res - shopping))
    trans = trans.replace("%", "") if trans.endswith("%") else trans
    trans = check_numerical_input(trans, min_input=100-res-shopping, max_input=100-res-shopping, mode="int")
    print('\nPreference for good restaurants is ', res, '%', sep="")
    print('Preference for entertainment places is ', shopping, '%', sep="")
    print('Preference for transportation accessibility is ', trans, '%', sep="")
    print("\nPlease enter 'Yes' to confirm your choice, otherwise, enter 'No' to re-enter")
    confirm = input()
    confirm = check_yes_no(confirm)
    if confirm:
        return res, shopping, trans
    else:
        return handle_user_input()


def display_neighborhood():
    print('\nYou can choose from 4 main neighborhoods in Pittsburgh. Each has their own pros and cons.')
    print('Please read the following descriptions carefully.\n')
    print(
        '1. Downtown: relatively far away from CMU and PITT; plenty of restaurants, supermarkets, business districts, '
        'bars and clubs')
    print(
        '2. Oakland: close to CMU and PITT (within walking distance); about 15-minute walk to shadyside and '
        'squirrel hill; most choices are apartments')
    print(
        '3. Shadyside: most choices are apartments; fewer buses; plenty of supermarkets and grocery stores; has a '
        'shopping street; many interesting bars.')
    print(
        '4. Squirrel Hill: prosperous business district; multiple bus choices; most choices are house; rents are '
        'relatively cheap')
    print('\nYou can choose 1-4 neighborhoods to search. Please enter your neighborhood choice in numbers.')
    print("Example: '1,2' stands for Downtown and Oakland,'1,3,4' stands for Downtown, Shadyside and Squirrel Hill.")
    neighbor = handle_neigh_control()
    return neighbor


def handle_neigh_control():
    neighbor = input('Enter here:')
    could_break = True
    while True:
        try:
            neighbor = [int(i) for i in neighbor.split(",")]
            for num in neighbor:
                if num not in [1, 2, 3, 4]:
                    neighbor = input("Your input must be between 1 and 4, please try again:")
                    could_break = False
            if could_break:
                break
            else:
                could_break = True
                continue
        except:
            neighbor = input("Your last input is invalid, please try again:")
    return neighbor


def handle_price():
    price = input('Please enter the highest monthly rent price that you can accept (at least 500): ')
    if price not in ['no', 'No', 'NO']:
        price = check_numerical_input(price, mode="float", min_input=500)
        return price
    else:
        return 100000


def handle_daily_commute():
    address = input("Please enter the address or name of your company or school: ")
    print("\nNext, please enter your choice of daily commute:")
    print("1. Driving \n2. Public Transit \n3. Walking \n4. Bicycle")
    transit_option = input("Enter here: ")
    transit_option = check_numerical_input(transit_option, mode="int", min_input=1, max_input=4)
    transit_mode_dict = {1: "driving", 2: "transit", 3: "walking", 4: "bicycling"}
    if address not in ['no', 'No', 'NO'] and transit_option:
        return address, transit_mode_dict[transit_option]
    else:
        return 0


def handle_show_map(m):
    if m not in ['no', 'No', 'NO']:
        return True
    else:
        return False

# Early version - Ignore it
# if __name__ == '__main__':
#     res, shopping, trans = handle_user_input()
#     print("\nThank you for setting your preferences. Now, Pillow will help you to pick a neighborhood.")
#     neigh = display_neighborhood()
#     print(
#         "\nThank you for choosing the neighborhoods. Now please set your acceptable price range. Enter 'No' if you "
#         "don't care about price:")
#     price_ceiling = handle_price()
#     print(
#         "\nCould you please provide the address of your company or school? Enter 'No' if you don't want to provide "
#         "this information.")
#     school_company = handle_daily_commute()
#     print(
#         "\nYou are all set. Pillow is calculating your preference and singling out the most suitable housing for you.")

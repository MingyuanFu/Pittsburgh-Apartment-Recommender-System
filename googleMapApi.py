import googlemaps
import gmplot
import re
import pprint
import webbrowser
import os


class googleMapApi:

    def __init__(self):
        """Initializer of googleMapApi class

        This method read the Google API key from file, and create GoogleMap Client

        """
        self.api_key = open('GOOG_API_KEY.txt', 'r').read()
        self.gmaps = googlemaps.Client(self.api_key)
        self.gmPlotter = None
        self.pp = pprint.PrettyPrinter()

    def get_coordinator_by_address(self, addr_string):
        response = self.gmaps.places(addr_string)
        # self.pp.pprint(response)
        location = response.get('results')[0].get('geometry').get('location')
        return location.get('lat'), location.get('lng')

    def search_nearby(self, location, search_string, distance=2000):
        """Make the GoogleMap places API call and reformat the response

        This method extract only the 'name' and 'rating' field from API response

        :param location: The latitude and longitude tuple of the house
        :param search_string: search_string used for GoogleMap places API keyword arg
        :param distance: distance used for GoogleMap places API radius arg, default=2000 meters
        :return: The result_dict, result dictionary of GoogleMap places API call
        """
        # time.sleep(1)
        response = self.gmaps.places_nearby(
            location=location,
            keyword=search_string,
            radius=distance,
        )
        # self.pp.pprint(response)
        result_dict = {}
        for result in response.get('results'):
            result_dict[result["name"]] = float(result['rating'])

        return result_dict

    def get_distance_matrix(self, src_loc, dst_loc, mode="transit", avoid="tolls", ):
        """Make the GoogleMap Distance Matrix API call and reformat the response

        This method extract only the 'distance' and 'duration' field from API response

        :param src_loc: The latitude and longitude tuple of the origin
        :param dst_loc: The latitude and longitude tuple of the destination
        :param mode: The mode of transit that from user inputs, default="transit"
        :param avoid: avoid used for GoogleMap Distance Matrix API avoid arg
        :return: The result_dict, result dictionary of GoogleMap places API call
        """
        response = self.gmaps.directions(src_loc, dst_loc,
                                         mode=mode, avoid=avoid,
                                         departure_time="now")
        # self.pp.pprint(response)
        distance = response[0]['legs'][0]['distance']['text']
        duration = response[0]['legs'][0]['duration']['text']
        return {"distance": distance, "duration": duration}

    def calculate_transportation_score(self, src_loc, dst_loc, transit_mode):
        """Calculate the score of the transportation by considering number of nearby bus stops,
            distance and duration to workplace or schools

        This mechanism favors the house location close to work place and had more bus stops

        :param src_loc: The latitude and longitude tuple of the house
        :param dst_loc: The latitude and longitude tuple of the workplace or school
        :param transit_mode: The transit method that from user input
        :return: The transit score, total score of house location normalized to out of 100
        """
        dist_matrix = self.get_distance_matrix(src_loc, dst_loc, transit_mode)
        bus_stops = self.search_nearby(src_loc, 'bus stop', distance=500)
        duration = [int(s) for s in dist_matrix.get('duration').split() if s.isdigit()][0]
        distance = float(re.findall("\d+\.\d+", dist_matrix.get('distance'))[0])
        return (100 - duration) * 0.8 + (100 - distance) * 0.1 + len(bus_stops.keys())

    def calculate_entertainment_score(self, location):
        """Calculate the score of the entertainment by considering number of nearby theaters,
            shopping centres, parks, night clubs with their ratings

        This mechanism favors the house location surrounded by more above entertaining places

        :param location: The latitude and longitude tuple of the house
        :return: The score, total score of related places before normalizing
        """
        theaters = self.search_nearby(location, "theater");
        shopping = self.search_nearby(location, "shopping centre");
        parks = self.search_nearby(location, "parks");
        nightclubs = self.search_nearby(location, "night club");
        return sum(theaters.values()) + sum(shopping.values()) + sum(parks.values()) + sum(nightclubs.values())

    def gmPlotter_init(self, location):
        """Initialize GoogleMap Plotter object

        This method setup api key and centre coordinate of the house location
        Add red marker on the house coordinate

        :param location: The latitude and longitude tuple of the house
        """
        latitude = float(location[0])
        longitude = float(location[1])
        self.gmPlotter = gmplot.GoogleMapPlotter(latitude, longitude, 13)
        self.gmPlotter.apikey = self.api_key
        self.gmPlotter.marker(latitude, longitude, 'red')

    def add_plotter_marker(self, coordinate, color='blue'):
        """Add markers to the Google Map plot you are going to draw

        This method ddd marker on the coordinate

        :param coordinate: The latitude and longitude tuple of the marker
        """
        latitude = float(coordinate[0])
        longitude = float(coordinate[1])
        self.gmPlotter.marker(latitude, longitude, color)

    def draw_and_display_gm_plot(self, filename='my_map.html'):
        """Draw Google Map plot, save to filename and display on browser tab

        This method generate html file of the Google Map drawn, and open on the browser

        :param filename: The file name of output html file
        """
        self.gmPlotter.draw(filename)
        url = 'file:///' + os.getcwd() + '/' + filename
        webbrowser.open_new_tab(url)  # open in new tab


if __name__ == '__main__':
    print("Testing Google Map API")

    my_geolocation = (40.448328, -79.9304626)
    cmu_geolocation = (40.443322, -79.943583)

    gma = googleMapApi()

    # Test calculate scores
    print(gma.calculate_entertainment_score(my_geolocation))
    print(gma.calculate_entertainment_score(cmu_geolocation))
    print(gma.calculate_transportation_score(my_geolocation, cmu_geolocation, "transit"))

    # Test gmPlotter
    gma.gmPlotter_init(my_geolocation)
    gma.add_plotter_marker(cmu_geolocation, 'blue')
    gma.draw_and_display_gm_plot()

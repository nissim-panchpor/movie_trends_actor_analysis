
def access_api(url, payload):
    """
    Given the API url and the desired parameters, makes a GET call to retrieve 
    information from the API and returns it as a dictionary.
    """
    import requests
    request = requests.get(url, params=payload)
    return request.json()

def get_movie_ids(actorname):
    """
    Finds ID of the actor and gets all their movie IDs in a list
    Input: Name of an actor as a string
    Return Value: A list of movie IDs
    """
    actor_payload = {"api_key": TMDB_KEY, "query": actorname, "include_adult" : True}   #Form paramters for API call
    response_actor = access_api("https://api.themoviedb.org/3/search/person", actor_payload)    #Call TMDb API through access_api() to search an actor
    person_id = response_actor['results'][0]['id']  #Store ID of the actor

    movie_credit_url = "https://api.themoviedb.org/3/person/"+str(person_id)+"/movie_credits"
    actor_movie_payload = {"api_key": TMDB_KEY, "person_id": person_id}
    movie_credits = access_api(movie_credit_url, actor_movie_payload) #Call access_api() to search for movies

    movie_id_list = []
    for num in range(len(movie_credits['cast'])):
        movie_id_list.append(movie_credits['cast'][num]['id'])  #Append movie IDs to list

    return(movie_id_list)

def movies_popularity(movie_id_list):
    """
    Creates a list of dictionaries of certain info of actor's movies that have revenue and budget greater than $1000 as a filter
    Input: List of movie IDs
    Return Value: A list of dictionaries each containing movie ID, name, release date and profit (revenue - budget)
    """
    movie_details_list = []
    movie_details_list_sorted=[]

    for id in movie_id_list:
        movie_dict = {}
        movie_url = "https://api.themoviedb.org/3/movie/"+str(id)
        movies_list_payload = {"api_key": TMDB_KEY, "movie_id": id}
        movie_response = access_api(movie_url, movies_list_payload)     #Access API using access_api()
        print('.',end='')                                               #Print dots to show progress
        sys.stdout.flush()                                              #Flush dots from buffer
        if movie_response['revenue'] > 1000 and movie_response['budget'] > 1000:      #Filter for movies
            movie_dict['release_date'] = movie_response['release_date']
            movie_dict['profit'] = movie_response['revenue'] - movie_response['budget']
            movie_details_list.append(movie_dict)
    
    print('\n\n'+actorname+' acted in total '+str(len(movie_id_list))+' movies but after cleaning the data, '+str(len(movie_details_list))+ ' movies were considered')
    
    movie_details_list_sorted = sorted(movie_details_list, key=lambda k: k['release_date'])     #Sort the list according to release_dates
    return(movie_details_list_sorted)


def plot_actor_popularity(actorname,movie_details_list_sorted):
    """
    Plots actor popularity using Bokeh library as movie profit vs date
    Inputs: Actor name, list of dictionaries of movie attributes
    Return value: N/A
    """
    from datetime import datetime                                       #import datetime and bokeh functions
    from bokeh.plotting import figure, output_file, show

    output_file("actor_popularity.html")                                #Create a html output file

    profits =[]
    releaseyears=[]
    
    for i in range(len(movie_details_list_sorted)):
        datestring = movie_details_list_sorted[i]['release_date']
        datetime_object = datetime.strptime(datestring, '%Y-%m-%d').date()         #Convert release dates to date object
        releaseyears.append(datetime_object.year)                                  #Append years of the above date object to a list
        profits.append(movie_details_list_sorted[i]['profit'])                            #Append movie profits to another list
    
    #Create a plot using figure(), give title and axis labels
    p = figure(title=actorname+ " popularity over time", x_axis_label='Date', y_axis_label='Revenue($)')

    #Plot a line graph using release years and profits
    p.line(releaseyears, profits, line_width=2)

    show(p)

def print_instructions(genres):
    """
    Prints out the instructions to graph out the graph by seasons plot, and obtains responses for what to plot
    from the user.
    Inputs: A list of all the genres in IMDB
    Return value: A list with  a list of desired genres to plot during the desired year, and the desired year
    itself.
    """
    print("\nSelect six genres you would like to visualize by typing in its number.\n")
    for i in range(0, len(genres)):
        print("(" + str(i + 1)+ ") " + genres[i].get("name"))
    # Obtain user input for six genres
    genre1 = int(input("\nWhat is the first genre would you like to visualize?  "))
    genre2 = int(input("What is the second genre would you like to visualize? "))
    genre3 = int(input("What is the third genre would you like to visualize?  "))
    genre4 = int(input("What is the fourth genre would you like to visualize? "))
    genre5 = int(input("What is the fifth genre would you like to visualize?  "))
    genre6 = int(input("What is the sixth genre would you like to visualize?  "))
    # Obtain user input for what year to visualize
    year = int(input("From what year? "))
    print("\nRetrieving data. This may take a while...")
    return [get_genre([genre1, genre2, genre3, genre4, genre5, genre6], genres), year]

def get_genre(indexes, genres):
    """
    Retrives information about the genres the users selects to visualize.
    Inputs: A list of indexes of genres to look at, a list of dictionaries about all the genres on the IMDB database
    Return value: A list of dictionaries, where each entry is about a IMDB genre
    """
    for i in range(0, len(indexes)):
        # Replace each index with a dictionary of the information about the genre it corresopnds to
        indexes[i] = genres[indexes[i] - 1]
    return indexes

def visualize_genres_by_season(selected):
    """
    Retrieves information about genres during the year and plots it.
    Input: A list containing a list of desired genres to visualize and a year
    Return value: N/A
    """
    # Retrieve data about the selected genres during the given year
    data = get_genre_data(selected)
    # Plot the data generated
    plot_genres_by_season(data, selected)

def plot_genres_by_season(data, selected):
    """
    Plots the graphs for desired genres during the desired year through Bokeh.
    Input: A list containing a list of the number of movies made for each genre during a given month in a year, a list
    containing information about genres to plot, and the desired year
    Return value: N/A
    """
    from math import ceil
    from bokeh.plotting import figure, output_file, show
    import bokeh.palettes
    colors = bokeh.palettes.small_palettes['Viridis'][6]
    # Calculate max to increase y-range to prevent legend from covering up too much of the graph
    max_num = 0
    for genre in data:
        for num in genre:
            max_num = max(max_num, num)
    # Where to store the results of the graph
    output_file("genre_by_season.html")
    # X-values the plot corresopnds to
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    # Create plot for the figure
    p = figure(title="Releases by Genre: " + str(selected[1]), x_axis_label='Month', y_axis_label='Releases', y_range=[0, ceil(max_num / 100.0) * 100.0 + 75.0], x_range=months)
    for i in range(0, 6):
        # Plot a line for each genre
        p.line(months, data[i], legend=selected[0][i].get("name"), line_color = colors[i], line_width=2)

    # Render results
    show(p)

def get_genre_data(genre_info):
    """
    Retrieves information about genres over a year.
    Input: A list containing a list of dictionary of genre information, and the desired year
    Return value: A list containing lists of the number of movies made for each genre during a given month in a year
    """
    url = "https://api.themoviedb.org/3/discover/movie"
    data = []
    payload = {"api_key": TMDB_KEY, "page": 1}
    # For each genre
    for i in range(0, 6):
        genre_data = []
        # For each month
        for j in range(1, 13):
            print('.',end='')
            sys.stdout.flush()
            payload["with_genres"] = genre_info[0][i].get("id")
            # Setting lower boundary for release date
            payload["primary_release_date.gte"] = get_release_date(j, genre_info[1], "gte")
            # Setting upper boundary for release date
            payload["primary_release_date.lte"] = get_release_date(j, genre_info[1], "lte")
            genre_data.append(access_api(url, payload).get("total_results"))
        data.append(genre_data)

    print("\n\nRetrieved data! Plotting now...")
    return data

def get_release_date(month, year, date_type):
    """
    Determines what day a given boundary lies during a particular part of the year.
    Inputs: Integer representing a month, integer representing the year, and a string representing which
    boundary is being calulated
    Return value: String representing the selected boundary of the release date
    """
    if date_type == "gte":
        if month < 10:
            return str(year) + "-0" + str(month) + "-01"
        else:
            return str(year) + "-" + str(month) + "-01"
    else:
        if month < 9:
            return str(year) + "-0" + str(month + 1) + "-01"
        elif month < 12:
            return str(year) + "-" + str(month + 1) + "-01"
        else:
            return str(year + 1) + "-01-01"


if __name__ == "__main__":
    from apikeys import TMDB_KEY
    import sys
    choice = input("\nWhat would you like to visualize, genres by season or actor popularity? \n (1) Type \"1\" for genres by season \n (2) Type \"2\" for actor popularity \n\n Your choice:  ")

    if choice == "1":
        # List of all the IMDB genres
        genres = access_api("https://api.themoviedb.org/3/genre/movie/list", {"api_key": TMDB_KEY}).get("genres")
        # Retrieve user input
        selected = print_instructions(genres)
        # Plot accordin to user input
        visualize_genres_by_season(selected)
    else:
        actorname = input('\nPlease enter the actor whose popularity you want to analysis: ')  #Get actor's name from user
        movie_id_list = get_movie_ids(actorname)                                             #Get actor's movie IDs
        print('\nRetrieved list of movies for '+actorname)
        print('Now finding popularity of each movie')

        movie_details_list_sorted = movies_popularity(movie_id_list)                         #Call function to get actor's movies and related info
        print('\n')
        plot_actor_popularity(actorname,movie_details_list_sorted)                           #Call function to plot using bokeh

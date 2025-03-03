import random
import matplotlib.pyplot as plt
from thefuzz import fuzz
from colorama import init, Fore, Style
import movie_storage
import datetime

init()


def input_colour(text):
    """Contains the colour setup used for inputs"""
    return Fore.GREEN + text + Fore.YELLOW


def error_colour(text):
    """Contains the colour setup used for errors"""
    return Fore.RED + text


def title():
    """Prints the title"""
    print('\n********** My Movies Database **********\n')


def menu():
    """Prints the menu"""
    print(f'''{Fore.BLUE}Menu:
0. Exit    
1. List movies
2. Add movie
3. Delete movie
4. Update movie
5. Stats
6. Random movie
7. Search movie
8. Movies sorted by rating
9. Movies sorted by year
10. Create rating histogram
11. Filter movies
''')
    print(Style.RESET_ALL)


def return_to_menu():
    """Designed to print the menu after each youser's action"""
    input(input_colour('Press enter to continue'))
    print(Style.RESET_ALL)


def list_movies(movies):
    """Prints all movies from the database"""
    print(f'{len(movies)} movies in total')
    for movie in movies:
        name, rating, year = tuple(movie.values())
        print(f'{name}, rating: {rating}, year: {year}')


def in_database(movies, movie_input):
    """Checks if movie is in database and returns movie's index if it was found"""
    is_found = False
    for movie_index, movie in enumerate(movies):
        if movie_input.lower() == movie['Title'].lower():
            is_found = True
            return is_found, movie_index
    return is_found

#created new functions
def get_valid_rating():
    """Validates the inputted rating and returns it if it's correct"""
    while True:
        try:
            rating_input = float(input(input_colour('Enter the movie rating (0-10): ')))
            if rating_input > 10 or rating_input < 0:
                raise Exception(error_colour(f'Rating {rating_input} is invalid'))
            return rating_input
        except ValueError:
            print(error_colour('The field must not be blank. Only integers are allowed'))
        except Exception as e:
            print(error_colour(f'The following error has occurred: {e}'))


def get_valid_year():
    """Validates the inputted year and returns it if it's correct"""
    MIN_YEAR = 1900
    MAX_YEAR = datetime.datetime.now().year
    while True:
        try:
            year_input = int(input(input_colour('Enter the year: ')))
            if year_input < MIN_YEAR or year_input > MAX_YEAR:
                raise Exception(error_colour(f'Year {year_input} is invalid'))
            return year_input
        except ValueError:
            print(error_colour('The field must not be blank. Only integers are allowed'))
        except Exception as e:
            print(error_colour(f'The following error has occurred: {e}'))


def add_movie(movies):
    """Adds a movie to the database"""
    while True:
        try:
            movie_input = input(input_colour('Enter the movie you would like to add: '))
            if len(movie_input) == 0 or movie_input.isspace():
                raise Exception(error_colour('Movie title must not be blank'))
            if in_database(movies, movie_input):
                print(error_colour('The movie is already in the database.'))
                return None
            #implemented new functions
            rating_input = get_valid_rating()
            year_input = get_valid_year()
            print(Style.RESET_ALL)
            movie_storage.add_movie(movie_input, year_input, rating_input, movies)
            print(f'The movie {movie_input} is successfully added.')
            break
        except Exception as e:
            print(error_colour(f'The following error has occurred: {e}'))


def delete_movie(movies):
    """Deletes a movie from the database"""
    while True:
        try:
            movie_input = input(input_colour('Enter the movie you would like to delete: '))
            if len(movie_input) == 0 or movie_input.isspace():
                raise Exception(error_colour('Movie title must not be blank'))
            break
        except Exception as e:
            print(error_colour(f'The following error has occurred: {e}'))
    print(Style.RESET_ALL)
    #refactored
    movie_in_database = in_database(movies, movie_input)
    if movie_in_database:
        movie_index = movie_in_database[1]
        movie_storage.delete_movie(movie_index)
        print(f'The movie {movie_input} is successfully deleted.')

    else:
        print(error_colour('There is no such movie in the database :('))


def update_movie(movies):
    """Updates a movie in the database"""
    while True:
        try:
            movie_input = input(input_colour('Enter the movie which rating you would like to change: '))
            if len(movie_input) == 0 or movie_input.isspace():
                raise Exception(error_colour('Movie title must not be blank'))
            break
        except Exception as e:
            print(error_colour(f'The following error has occurred: {e}'))
    is_in_database = in_database(movies, movie_input)
    if not is_in_database:
        print(error_colour('There is no such movie in the database :('))
        return None
    #implemented new function
    rating_input = get_valid_rating()
    print(Style.RESET_ALL)
    if is_in_database:
        index = is_in_database[1]
        movie_storage.update_movie(index, rating_input)
        print(f'The movie {movie_input} is successfully updated.')


def stats_average_and_median_rating(movies):
    """Prints the average rating and the median rating of movies"""
    ratings_list = []
    for movie in movies:
        ratings_list.append(movie['Rating'])
    average_rating = round(sum(ratings_list) / len(ratings_list), 1)
    print(f'Average rating: {average_rating}')
    if len(ratings_list) % 2 != 0:
        print(f'Median rating: {round(ratings_list[int(len(ratings_list) / 2)], 1)}')
    else:
        print(f'Median rating: '
              f'{round((ratings_list[len(ratings_list) // 2 - 1] + ratings_list[len(ratings_list) // 2]) / 2, 1)}')


def stats_best_movies(movies):
    """Prints the movie(s) with the highest rating"""
    best_movie = ''
    best_movie_rating = 0
    best_movies = {}
    for movie in movies:
        if movie['Rating'] > best_movie_rating:
            best_movie = movie['Title']
            best_movie_rating = movie['Rating']
            best_movies = {best_movie: best_movie_rating}
        # checks if there are more than 1 movie with the best rating
        elif movie['Rating'] == best_movie_rating:
            best_movies[movie['Title']] = movie['Rating']
    if len(best_movies) == 1:
        print(f'The movie with the biggest rating: {best_movie}: {best_movie_rating}')
    if len(best_movies) > 1:
        print('Movies with the best rating: ')
        for movie, rating in best_movies.items():
            print(f'{movie}: {rating}')


def stats_worst_movies(movies):
    """Prints the movie(s) with the lowest rating"""
    worst_movie = ''
    worst_movie_rating = movies[0]['Rating']
    worst_movies = {}
    for movie in movies:
        if movie['Rating'] < worst_movie_rating:
            worst_movie = movie['Title']
            worst_movie_rating = movie['Rating']
            worst_movies = {worst_movie: worst_movie_rating}
        # checks if there are more than 1 movie with the worst rating
        elif movie['Rating'] == worst_movie_rating:
            worst_movies[movie['Title']] = movie['Rating']
    if len(worst_movies) == 1:
        print(f'The movie with the lowest rating: {worst_movie}: {worst_movie_rating}')
    if len(worst_movies) > 1:
        print('Movies with the lowest rating: ')
        for movie, rating in worst_movies.items():
            print(f'{movie}: {rating}')


def stats(movies):
    """Executes all stats functions"""
    stats_average_and_median_rating(movies)
    stats_best_movies(movies)
    stats_worst_movies(movies)


def random_movie(movies):
    """Prints the random picked movie"""
    rand_movie = random.choice(movies)
    print(f"Your movie for tonight: {rand_movie['Title']}, it's rated {rand_movie['Rating']}")


def search_movie(movies):
    """
    Searches the movie by the query and if the query is partial,
    suggests the appropriate possible options of movies
    """
    while True:
        try:
            user_query = input(input_colour('Enter your search query: '))
            if len(user_query) == 0 or user_query.isspace():
                raise Exception(error_colour('Movie title must not be blank'))
            break
        except Exception as e:
            print(error_colour(f'The following error has occurred: {e}'))
    print(Style.RESET_ALL)
    movies_list = []
    movie_is_found = False
    for movie in movies:
        if user_query.lower() == movie['Title'].lower():
            print(f"{movie['Title']}: {movie['Rating']}")
            movie_is_found = True
            break
        elif fuzz.token_set_ratio(movie['Title'], user_query) > 50:  # setups the level of responses' similarity,
            # comparing to the sought movie
            movies_list.append(movie['Title'])
    # checks if the similar movies were found
    if len(movies_list) > 0 and not movie_is_found:
        print(error_colour(f'The movie "{user_query}" does not exist. Did you mean:'))
        for movie in movies_list:
            print(movie)
    elif len(movies_list) == 0 and not movie_is_found:
        print(error_colour(f'The movie "{user_query}" does not exist.'))


def movies_sorted_by_rating_descended(movies):
    """Prints movies sorted by rating in descended order"""
    def rating(movie):
        return movie['Rating']

    movies_sorted = sorted(movies, key=rating, reverse=True)
    for movie_sorted in movies_sorted:
        print(f"{movie_sorted['Title']}: {movie_sorted['Rating']}")


def movies_sorted_by_year(movies):
    """
    Asks users whether they want to see the latest movies first or last and
    prints movies sorted by year accordingly
    """
    def year(movie):
        return movie['Year of release']

    while True:
        try:
            user_input = int(input('To see the latest movies first, type "1". To see them last, type "2": '))
            if user_input != 1 and user_input != 2:
                raise Exception('Wrong format of the operation. Only "1" or "2" are allowed.')
            break
        except ValueError:
            print('The field must not be blank. Only integers are allowed.')
        except Exception as e:
            print(error_colour(f'The following error has occurred: {e}'))
    reverse_on = 0
    if user_input == 1:
        reverse_on = True
    elif user_input == 2:
        reverse_on = False
    movies_sorted = sorted(movies, key=year, reverse=reverse_on)
    for movie_sorted in movies_sorted:
        print(f"{movie_sorted['Title']}: rating: {movie_sorted['Rating']}, year: {movie_sorted['Year of release']}")


def rating_histogram(movies):
    """Creates in the directory the png file with the histogram based on movies' ratings"""
    try:
        ratings = []
        for movie in movies:
            ratings.append(round(movie['Rating']))
        plt.hist(ratings)
        file_name = input(input_colour('Enter the file name to save the histogram: '))
        print(Style.RESET_ALL)
        if file_name == '' or file_name == ' ':
            print(error_colour('Invalid file name.'))
        else:
            plt.savefig(file_name + '.png')
        raise Exception('Simulated Matplotlib error')
    except Exception as e:
        print(error_colour(f'The following error has occurred: {e}'))


def filter_movies(movies):
    """
    Prompts the user to input the minimum rating, start year, and end year of movies,
    or leave them blank to skip those filters.
    Prints the movies based on the entered criteria.
    """
    DISABLE_MIN_RATING = -1
    DISABLE_START_YEAR = -1
    DISABLE_END_YEAR = 10000
    #I preserved a distinct input validation in this function because the logic here distinguishes from the logic in get_valid_rating
    #TODO This is correct, however, the function is still a bit too long and could be split into smaller functions. For example, each while loop could be a separate function. this will significantly improve the readability of this function.
    while True:
        while True:
            try:
                minimum_rating = input(input_colour('Enter minimum rating (leave blank for no minimum rating): '))
                if len(minimum_rating) > 0:
                    minimum_rating = float(minimum_rating)
                    if minimum_rating > 10 or minimum_rating < 0:
                        raise Exception(error_colour('Wrong format of the rating. Only 0-10 are allowed.'))
                else:
                    minimum_rating = DISABLE_MIN_RATING
                break
            except ValueError:
                print(error_colour('Only integers are allowed.'))
            except Exception as e:
                print(e)
            finally:
                print(Style.RESET_ALL)
        while True:
            #same here
            try:
                start_year = input(input_colour('Enter start year (leave blank for no start year): '))
                if len(start_year) > 0:
                    if start_year.isdigit() and len(start_year) != 4:
                        raise Exception(error_colour('Wrong format of the year.'))
                    start_year = int(start_year)
                else:
                    start_year = DISABLE_START_YEAR
                break
            except ValueError:
                print(error_colour('Only integers are allowed.'))
            except Exception as e:
                print(e)
            finally:
                print(Style.RESET_ALL)
        while True:
            try:
                end_year = input(input_colour('Enter end year (leave blank for no end year): '))
                if len(end_year) > 0:
                    if end_year.isdigit() and len(end_year) != 4:
                        raise Exception(error_colour('Wrong format of the year.'))
                    end_year = int(end_year)
                else:
                    end_year = DISABLE_END_YEAR
                break
            except ValueError:
                print(error_colour('Only integers are allowed.'))
            except Exception as e:
                print(e)
            finally:
                print(Style.RESET_ALL)
        break

    def filter_settings(movie_item):
        if (movie_item['Rating'] >= minimum_rating and end_year >= movie_item['Year of release'] >= start_year
                and movie_item['Year of release']):
            return True
        else:
            return False

    filtered_movies = filter(filter_settings, movies)
    print('Filtered movies: ')
    for movie in filtered_movies:
        print(f"{movie['Title']} ({movie['Year of release']}): {movie['Rating']}")


def main():
    valid_inputs = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11']
    title()
    while True:
        #moved exceptions logic to movie_storage
        movies = movie_storage.get_movies()
        if not movies:
            break
        menu()
        user_action = input(input_colour('Enter choice (0-11): '))
        print(Style.RESET_ALL)
        while user_action not in valid_inputs:
            print(error_colour('Invalid choice'))
            menu()
            user_action = input(input_colour('Enter choice (0-11): '))
            print(Style.RESET_ALL)
        if user_action == '0':
            print('Bye!')
            break
        if user_action == '1':
            list_movies(movies)
        if user_action == '2':
            add_movie(movies)
        if user_action == '3':
            delete_movie(movies)
        if user_action == '4':
            update_movie(movies)
        if user_action == '5':
            stats(movies)
        if user_action == '6':
            random_movie(movies)
        if user_action == '7':
            search_movie(movies)
        if user_action == '8':
            movies_sorted_by_rating_descended(movies)
        if user_action == '9':
            movies_sorted_by_year(movies)
        if user_action == '10':
            rating_histogram(movies)
        if user_action == '11':
            filter_movies(movies)
        if user_action in valid_inputs:
            return_to_menu()


if __name__ == "__main__":
    main()

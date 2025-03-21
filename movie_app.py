import random
import matplotlib.pyplot as plt
from thefuzz import fuzz
from colorama import init, Fore, Style
from dotenv import load_dotenv
import os
import requests
from template_render import MoviesRender
from storage.istorage import IStorage

load_dotenv()
init()

API_KEY = os.getenv('API_KEY')


class MovieApp:
    def __init__(self, storage):
        try:
            if not isinstance(storage, IStorage):
                raise TypeError('Wrong type of the storage.')
            self._storage = storage
        except (TypeError, Exception) as e:
            print(self.error_colour(f"Such error occurred: {e}"))
            quit()


    def input_colour(self, text):

        """Contains the colour setup used for inputs"""

        return Fore.GREEN + text + Fore.YELLOW


    def error_colour(self, text):

        """Contains the colour setup used for errors"""

        return Fore.RED + text


    def title(self):

        """Prints the title"""

        print('\n********** My Movies Database **********\n')


    def menu(self):

        """Prints the menu"""

        print(f'''{Fore.BLUE}Menu:
    0. Exit    
    1. List movies
    2. Add movie
    3. Delete movie
    4. Generate website
    5. Stats
    6. Random movie
    7. Search movie
    8. Movies sorted by rating
    9. Movies sorted by year
    10. Create rating histogram
    11. Filter movies
    ''')
        print(Style.RESET_ALL)


    def return_to_menu(self):

        """Designed to print the menu after each user's action"""

        input(self.input_colour('Press enter to continue'))
        print(Style.RESET_ALL)


    def list_movies(self):

        """Prints all movies from the database"""

        print(f'{len(self._storage.list_movies)} movies in total\n')
        for movie in self._storage.list_movies:
            name, rating, year, poster = tuple(movie.values())
            print(f"Name: {name}, Rating: {rating}, Year: {year}\nPoster Link: {poster}\n")


    def in_database(self, movies, movie_input):

        """Checks if movie is in database and returns movie's index if it was found"""

        is_found = False
        for movie_index, movie in enumerate(movies):
            if movie_input.lower() == movie['Title'].lower():
                is_found = True
                return is_found, movie_index
        return is_found


    def _get_data_api(self, movie_input, movies):

        """Validates data from the API and returns it"""

        try:
            endpoint = f"http://www.omdbapi.com/?apikey={API_KEY}&t={movie_input}"
            response = requests.get(endpoint)
            parsed_response = response.json()
            if parsed_response == {"Response": "False", "Error": "Movie not found!"}:
                raise ValueError(self.error_colour("Such movie doesn't exist!"))
            title = parsed_response['Title']
            if len(title) == 0 or title == 'N/A':
                print(self.error_colour('Impossible to add the movie!\n'))
                return None
            if self.in_database(movies, title):
                print(self.error_colour('The movie is already in the database.'))
                return None
            year = parsed_response['Year']
            if len(year) == 0 or year == 'N/A':
                print(self.error_colour('Impossible to add the movie!\n'))
                return None
            if '–' in year:
                year = year.split('–')[0]
                year = ''.join(year)
            rating = parsed_response['imdbRating']
            if len(rating) == 0 or rating == 'N/A':
                print(self.error_colour('Impossible to add the movie!\n'))
                return None
            float(rating)
            poster = parsed_response['Poster']
            if len(poster) == 0 or poster == 'N/A':
                print(self.error_colour('Impossible to add the movie!\n'))
                return None
            return title, year, rating, poster
        except requests.exceptions.ConnectionError:
            print(self.error_colour('Impossible to connect to the API!'))
        except requests.exceptions.JSONDecodeError:
            print(self.error_colour('No data from the API'))
        except ValueError and Exception as e:
            print(self.error_colour(f'The following error has occurred: {e}'))


    def add_movie(self, movies):

        """Adds a movie to the database"""

        while True:
            try:
                movie_input = input(self.input_colour('Enter the movie you would like to add: '))
                if len(movie_input) == 0 or movie_input.isspace():
                    raise Exception(self.error_colour('Movie title must not be blank'))
                movie_to_add = self._get_data_api(movie_input, movies)
                if movie_to_add is None:
                    return None
                title, year, rating, poster = movie_to_add
                print(Style.RESET_ALL)
                self._storage.add_movie(title, year, rating, poster)
                print(f'The movie {title} is successfully added.')
                break
            except Exception as e:
                print(self.error_colour(f'The following error has occurred: {e}'))


    def delete_movie(self, movies):

        """Deletes a movie from the database"""

        while True:
            try:
                movie_input = input(self.input_colour('Enter the movie you would like to delete: '))
                if len(movie_input) == 0 or movie_input.isspace():
                    raise Exception(self.error_colour('Movie title must not be blank'))
                break
            except Exception as e:
                print(self.error_colour(f'The following error has occurred: {e}'))
        print(Style.RESET_ALL)
        movie_in_database = self.in_database(movies, movie_input)
        if movie_in_database:
            movie_index = movie_in_database[1]
            self._storage.delete_movie(movie_index)
            print(f'The movie {movie_input} is successfully deleted.')

        else:
            print(self.error_colour('There is no such movie in the database :('))


    def stats_average_and_median_rating(self, movies):

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


    def stats_best_movies(self, movies):

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


    def stats_worst_movies(self, movies):

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

    def stats(self, movies):

        """Executes all stats functions"""

        self.stats_average_and_median_rating(movies)
        self.stats_best_movies(movies)
        self.stats_worst_movies(movies)


    def random_movie(self, movies):

        """Prints the random picked movie"""

        rand_movie = random.choice(movies)
        print(f"Your movie for tonight: {rand_movie['Title']}, it's rated {rand_movie['Rating']}")


    def search_movie(self, movies):

        """
        Searches the movie by the query and if the query is partial,
        suggests the appropriate possible options of movies
        """

        while True:
            try:
                user_query = input(self.input_colour('Enter your search query: '))
                if len(user_query) == 0 or user_query.isspace():
                    raise Exception(self.error_colour('Movie title must not be blank'))
                break
            except Exception as e:
                print(self.error_colour(f'The following error has occurred: {e}'))
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
            print(self.error_colour(f'The movie "{user_query}" does not exist. Did you mean:'))
            for movie in movies_list:
                print(movie)
        elif len(movies_list) == 0 and not movie_is_found:
            print(self.error_colour(f'The movie "{user_query}" does not exist.'))


    def movies_sorted_by_rating_descended(self, movies):

        """Prints movies sorted by rating in descended order"""

        movies_sorted = sorted(movies, key=lambda movie: movie['Rating'], reverse=True)
        for movie_sorted in movies_sorted:
            print(f"{movie_sorted['Title']}: {movie_sorted['Rating']}")


    def movies_sorted_by_year(self, movies):

        """
        Asks users whether they want to see the latest movies first or last and
        prints movies sorted by year accordingly
        """

        while True:
            try:
                user_input = int(input('To see the latest movies first, type "1". To see them last, type "0": '))
                if user_input != 1 and user_input != 0:
                    raise Exception('Wrong format of the operation. Only "1" or "0" are allowed.')
                break
            except ValueError:
                print(self.error_colour('The field must not be blank. Only integers are allowed.'))

            except Exception as e:
                print(self.error_colour(f'The following error has occurred: {e}'))
            finally:
                print(Style.RESET_ALL)
        movies_sorted = sorted(movies, key=lambda movie: movie['Year'], reverse=bool(user_input))
        for movie_sorted in movies_sorted:
            print(f"{movie_sorted['Title']}: rating: {movie_sorted['Rating']}, year: {movie_sorted['Year']}")


    def rating_histogram(self, movies):

        """Creates in the directory the png file with the histogram based on movies' ratings"""

        try:
            ratings = []
            for movie in movies:
                ratings.append(round(movie['Rating']))
            plt.hist(ratings)
            file_name = input(self.input_colour('Enter the file name to save the histogram: '))
            print(Style.RESET_ALL)
            if file_name == '' or file_name == ' ':
                print(self.error_colour('Invalid file name.'))
            else:
                plt.savefig(file_name + '.png')
        except Exception as e:
            print(self.error_colour(f'The following error has occurred: {e}'))
        finally:
            print(Style.RESET_ALL)


    def _get_minimum_rating(self):

        """Prompts the user to input the minimum rating of movies, or leave it blank to skip this filter"""

        DISABLE_MIN_RATING = -1
        while True:
            try:
                minimum_rating = input(self.input_colour('Enter minimum rating (leave blank for no minimum rating): '))
                if len(minimum_rating) > 0:
                    minimum_rating = float(minimum_rating)
                    if minimum_rating > 10 or minimum_rating < 0:
                        raise Exception(self.error_colour('Wrong format of the rating. Only 0-10 are allowed.'))
                    return minimum_rating
                else:
                    minimum_rating = DISABLE_MIN_RATING
                    return minimum_rating
            except ValueError:
                print(self.error_colour('Only integers are allowed.'))
            except Exception as e:
                print(e)
            finally:
                print(Style.RESET_ALL)


    def _get_start_year(self):

        """Prompts the user to input the start year of movies, or leave it blank to skip this filter"""

        DISABLE_START_YEAR = -1
        while True:
            try:
                start_year = input(self.input_colour('Enter start year (leave blank for no start year): '))
                if len(start_year) > 0:
                    if start_year.isdigit() and len(start_year) != 4:
                        raise Exception(self.error_colour('Wrong format of the year.'))
                    start_year = int(start_year)
                    return start_year
                else:
                    start_year = DISABLE_START_YEAR
                    return start_year
            except ValueError:
                print(self.error_colour('Only integers are allowed.'))
            except Exception as e:
                print(e)
            finally:
                print(Style.RESET_ALL)


    def _get_end_year(self):

        """Prompts the user to input the end rating of movies, or leave it blank to skip this filter"""

        DISABLE_END_YEAR = 10000
        while True:
            try:
                end_year = input(self.input_colour('Enter end year (leave blank for no end year): '))
                if len(end_year) > 0:
                    if end_year.isdigit() and len(end_year) != 4:
                        raise Exception(self.error_colour('Wrong format of the year.'))
                    end_year = int(end_year)
                    return end_year
                else:
                    end_year = DISABLE_END_YEAR
                    return end_year
            except ValueError:
                print(self.error_colour('Only integers are allowed.'))
            except Exception as e:
                print(e)
            finally:
                print(Style.RESET_ALL)


    def filter_movies(self, movies):

        """Filters movies and prints them based on the entered criteria."""

        minimum_rating = self._get_minimum_rating()
        end_year = self._get_end_year()
        start_year = self._get_start_year()


        def filter_settings(movie_item):
            if (movie_item['Rating'] >= minimum_rating and end_year >= movie_item['Year'] >= start_year
                    and movie_item['Year']):
                return True
            else:
                return False

        filtered_movies = filter(filter_settings, movies)
        print('Filtered movies: ')
        for movie in filtered_movies:
            print(f"{movie['Title']} ({movie['Year']}): {movie['Rating']}")


    def run(self):

        """Runs the application"""

        valid_inputs = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11']
        self.title()
        while True:
            movies = self._storage.list_movies
            if not movies:
                break
            self.menu()
            user_action = input(self.input_colour('Enter choice (0-11): '))
            print(Style.RESET_ALL)
            while user_action not in valid_inputs:
                print(self.error_colour('Invalid choice'))
                self.menu()
                user_action = input(self.input_colour('Enter choice (0-11): '))
                print(Style.RESET_ALL)
            if user_action == '0':
                print('Bye!')
                break
            if user_action == '1':
                self.list_movies()
            if user_action == '2':
                self.add_movie(movies)
            if user_action == '3':
                self.delete_movie(movies)
            if user_action == '4':
                website_generator = MoviesRender(movies)
                website_generator.render()
            if user_action == '5':
                self.stats(movies)
            if user_action == '6':
                self.random_movie(movies)
            if user_action == '7':
                self.search_movie(movies)
            if user_action == '8':
                self.movies_sorted_by_rating_descended(movies)
            if user_action == '9':
                self.movies_sorted_by_year(movies)
            if user_action == '10':
                self.rating_histogram(movies)
            if user_action == '11':
                self.filter_movies(movies)
            if user_action in valid_inputs:
                self.return_to_menu()

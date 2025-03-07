from storage.istorage import IStorage
import json


class StorageJson(IStorage):
    def __init__(self, file_path):
        self.file_path = file_path
        self._movies = self.get_movies()


    def get_movies(self):
        try:
            with open(self.file_path, 'r') as file:
                return json.loads(file.read())
        except FileNotFoundError:
            print('Can not access the database!')
        except json.decoder.JSONDecodeError:
            print('Database is empty!')
        except Exception as e:
            print(f'The following error has occurred: {e}')


    def list_movies(self):
        print(f'{len(self._movies)} movies in total\n')
        for movie in self._movies:
            name, rating, year, poster = tuple(movie.values())
            print(f'{name}, rating: {rating}, year: {year}, poster: {poster}')


    def add_movie(self, title, year, rating, poster):
        with open(self.file_path, 'w') as file:
            self._movies.append({
                'Title': title,
                'Rating': float(rating),
                'Year': int(year),
                'Poster': poster
            })
            file.write(json.dumps(self._movies))


    def delete_movie(self, index):
        with open(self.file_path, 'w') as file:
            self._movies.pop(index)
            file.write(json.dumps(self._movies))


    def update_movie(self, index, rating):
        with open(self.file_path, 'w') as file:
            self._movies[index]['Rating'] = rating
            file.write(json.dumps(self._movies))

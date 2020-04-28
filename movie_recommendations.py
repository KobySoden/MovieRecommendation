"""
Name: movie_recommendations.py
Date: 4/14/2020
Author: Koby (Soden|Beaulieu)
Description: Takes information about users and ratings that they gave to movies 
            they have seen then predicts what rating they would give to a movie
            they have not seen based on the movies they have seen.
"""

import math
import csv
from scipy.stats import pearsonr

class BadInputError(Exception):
    pass

class Movie_Recommendations:
    # Constructor
    def __init__(self, movie_filename, training_ratings_filename):
        """
        Initializes the Movie_Recommendations object from 
        the files containing movie names and training ratings.  
        The following instance variables should be initialized:
        self.movie_dict - A dictionary that maps a movie id to
               a movie objects (objects the class Movie)
        self.user_dict - A dictionary that maps user id's to a 
               a dictionary that maps a movie id to the rating
               that the user gave to the movie.    
        """
        self.user_dict = {}     #empty dictionary for users dictionary
        self.movie_dict = {}       #empty dictionary for movie dictionary

        #movie Dictionary 
        f = open(movie_filename, encoding='utf-8')    
        csv_reader = csv.reader(f, delimiter = ',', quotechar = '"')
        next(csv_reader)                                 #gets rid of file format line
        for line in csv_reader:                          # creates movie dictionary and Movie object for each movie 
            self.movie_dict[int(line[0])] = Movie(int(line[0]), line[1])

        #Users dictionary 
        f = open(training_ratings_filename, encoding='utf-8')
        csv_reader = csv.reader(f, delimiter = ',', quotechar = '"')
        next(csv_reader) 
        for line in csv_reader:
            """
            if the user already has a key then it does not 
            create a new one and instead just adds to the 
            already existing user
            """
            if int(line[0]) in self.user_dict:               
                more = {int(line[1]):float(line[2])}                
                self.user_dict[int(line[0])].update(more)
            
            else:                                               #if the user doesn't have a dictionary key 
                self.user_dict[int(line[0])] = {int(line[1]):float(line[2])}     # creates nested dictionary for new user
            
            a = self.movie_dict[int(line[1])]                        #sets a equal to movie object
            a.users.append(int(line[0]))                             #adds to list of users who have seen each movie
    

    def predict_rating(self, user_id, movie_id):
        """
        Returns the predicted rating that user_id will give to the
        movie whose id is movie_id. 
        If user_id has already rated movie_id, return
        that rating.
        If either user_id or movie_id is not in the database,
        then BadInputError is raised.
        ------------------------------------------------------------------
        Check to see what movies the user has seen
        Multiply the rating they gave a movie to the similarity between that movie and the movie of interest
        Add up those values for every value that the user has seen
        divide by the sumation of the similarities between movie of interest and the movies the user has seen
        done
        """
        
        if user_id in self.user_dict and movie_id in self.movie_dict:       #checks for valid user and movie ID
            if movie_id in self.user_dict[user_id]:            #if the user has seen the movie return the rating they gave it
                return self.user_dict[user_id][movie_id]        #returns rating user gave to the movie
            else:                   #predicts rating for a user that has not seen the movie
                numerator = 0
                denominator = 0
                movies_seen = self.user_dict[user_id]
                for movie in movies_seen:
                    numerator += (movies_seen[movie]*self.movie_dict[movie_id].get_similarity(movie, self.movie_dict, self.user_dict))
                    denominator += self.movie_dict[movie_id].get_similarity(movie, self.movie_dict, self.user_dict)
                if denominator == 0:
                    prediction = 2.5 
                else:
                    prediction = numerator / denominator
                return prediction     #returns predition 
        else:       
            raise BadInputError
        
    def predict_ratings(self, test_ratings_filename):
        """
        Returns a list of tuples, one tuple for each rating in the
        test ratings file.
        The tuple should contain
        (user id, movie title, predicted rating, actual rating)
        """
        movie_list = []         #creates empty list for tuples 
        f = open(test_ratings_filename)         #opens file in a readable fashion
        csv_reader = csv.reader(f, delimiter = ',', quotechar = '"')
        next(csv_reader)                        #skips first line that tells what each piece is
        for line in csv_reader:                     #creates tuple for every line in file
            prediction = self.predict_rating(int(line[0]), int(line[1]))
            movie_tup = (int(line[0]), self.movie_dict[int(line[1])].title, prediction, float(line[2]))
            movie_list.append(movie_tup)                     #adds tuple to list
        return movie_list       #returns list of movie tuples

    def correlation(self, predicted_ratings, actual_ratings):
        """
        Returns the correlation between the values in the list predicted_ratings
        and the list actual_ratings.  The lengths of predicted_ratings and
        actual_ratings must be the same.
        """
        return pearsonr(predicted_ratings, actual_ratings)[0]
        
class Movie: 
    """
    Represents a movie from the movie database.
    """
    #constructor
    def __init__(self, id, title):
        """ 
        Constructor.
        Initializes the following instances variables.  You
        must use exactly the same names for your instance 
        variables.  (For testing purposes.)
        id: the id of the movie
        title: the title of the movie
        users: list of the id's of the users who have
            rated this movie.  Initially, this is
            an empty list, but will be filled in
            as the training ratings file is read.
        similarities: a dictionary where the key is the
            id of another movie, and the value is the similarity
            between the "self" movie and the movie with that id.
            This dictionary is initially empty.  It is filled
            in "on demand", as the file containing test ratings
            is read, and ratings predictions are made.
        """

        self.id = id
        self.title = title
        self.users = []
        self.similarities = {}
        
    def __str__(self):
        """
        Returns string representation of the movie object.
        Handy for debugging.
        """
        return 'Movie(%s, %s)' % (self.id, self.title)
        

    def __repr__(self):
        """
        Returns string representation of the movie object.
        """
        return '%s, %s, %s, %s' % (self.id, self.title, self.users, self.similarities)

    def get_similarity(self, other_movie_id, movie_dict, user_dict):
        """ 
        Returns the similarity between the movie that 
        called the method (self), and another movie whose
        id is other_movie_id.  (Uses movie_dict and user_dict)
        If the similarity has already been computed, return it.
        If not, compute the similarity (using the compute_similarity
        method), and store it in both
        the "self" movie object, and the other_movie_id movie object.
        Then return that computed similarity.
        If other_movie_id is not valid, raise BadInputError exception.
        """
        try:                            
            if other_movie_id in self.similarities:             #Check if it is similarity has already been calculated
                return self.similarities[other_movie_id]
            if other_movie_id not in movie_dict:            #if movie id is not valid it raises BadInputError
                raise BadInputError
            else:                                       #computes similarity 
                similarity = self.compute_similarity(other_movie_id, movie_dict, user_dict)
                self.similarities[other_movie_id] = similarity
                movie_dict[other_movie_id].similarities[self.id] = similarity       #stores movie similarity into similarity dictionary 
                return similarity
        except BadInputError:
            pass

    def compute_similarity(self, other_movie_id, movie_dict, user_dict):
        """ 
        Computes and returns the similarity between the movie that 
        called the method (self), and another movie whose
        id is other_movie_id.  (Uses movie_dict and user_dict)
        -----------------------------------------------------------------
        -Need to get list of users who have seen movie 1 and Movie 2
        -Then to compare to find the users who have seen both movies
        -Get the ratings that those users gave to each of the movies
        -Find the average difference between ratings of the movies
        -compute similarity= 1 - average difference/4.5
        """
        total = 0       #used for calculating average difference portion
        count = 0       #used to keep track of number of movies seen 
        movie_1_users = self.users                              #get the list of users who have seen the first movie
        movie_2_users = movie_dict[other_movie_id].users       #get the list of users who have seen the second movi

        for user in movie_1_users:                #get the ratings that each user who saw movie 1 gave to movie 1
            if user in movie_2_users:             #Finds the users who have seen both movies
                rating = user_dict[user][self.id]       
                rating2 = user_dict[user][other_movie_id]
                total += abs(rating - rating2)
                count += 1
        if count == 0:
            similarity = 0
        else:
            avg_diff = total / count            #average differnce 
            similarity = 1 - (avg_diff/4.5)     #similarity 
        
        return similarity







if __name__ == "__main__":
    # Create movie recommendations object.
    movie_recs = Movie_Recommendations("movies.csv", "training_ratings.csv")

    # Predict ratings for user/movie combinations
    rating_predictions = movie_recs.predict_ratings("test_ratings.csv")
    print("Rating predictions: ")
    for prediction in rating_predictions:
        print(prediction)
    predicted = [rating[2] for rating in rating_predictions]
    actual = [rating[3] for rating in rating_predictions]
    correlation = movie_recs.correlation(predicted, actual)
    print(f"Correlation: {correlation}")    
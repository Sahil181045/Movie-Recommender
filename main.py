import pickle
import json
from flask import Flask, request
from flask_restful import Api, Resource
from numpy.linalg import norm
from numpy import vdot
from sklearn.feature_extraction.text import CountVectorizer

app = Flask(__name__)
api = Api(app)

movies = pickle.load(open('movie_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

cv = CountVectorizer(max_features=5000, stop_words='english')
vectors = cv.fit_transform(movies['tags']).toarray()


def get_total_tags(liked_movies):
    total_tags = ""
    for i in liked_movies:
        tag = movies.loc[movies['title'] == i, 'tags'].iloc[0]
        list_of_str = [total_tags, tag]
        total_tags = " ".join(list_of_str)
    return total_tags


def recommendLiked(liked_movies):

    tags = get_total_tags(liked_movies)

    recommended_movies_list = []
    similarity = []
    combined_tags = [tags]

    combined_tags_vector = cv.transform(combined_tags).toarray()

    for i in vectors:
        cosine_similarity = (
            vdot([i], combined_tags_vector) / (norm(i) * norm(combined_tags_vector)))
        similarity.append(cosine_similarity)

    recommended_movies_list_index = sorted(list(enumerate(similarity)), reverse=True, key=lambda x: x[1])[
        len(liked_movies):len(liked_movies) + 20]
    # [len(liked_movies):len(liked_movies) + 20] based on the assumption that the liked_movies appear at the beginning of similarity list 

    for i in recommended_movies_list_index:
        recommended_movies_list.append(movies.iloc[i[0]].title)

    return recommended_movies_list

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(
        list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    for i in distances[1:6]:
        recommended_movie_names.append(movies.iloc[i[0]].title)

    return recommended_movie_names


class Recommender(Resource):
    def get(self, selected_movie):
        recommended_movie_names = recommend(selected_movie)
        movie_names = {"movie_1":recommended_movie_names[0],"movie_2":recommended_movie_names[1],"movie_3":recommended_movie_names[2],"movie_4":recommended_movie_names[3],"movie_5":recommended_movie_names[4]}
        
        print(json.dumps(movie_names))
        return json.dumps(movie_names)
        # return movie_names
    
    def post(self):
        json_data = request.get_json(force=True)
        liked_movies = []
        for j in json_data['movies']:
            liked_movies.append(j)
        recommended_movie_names = recommendLiked(liked_movies)
        print(json.dumps(recommended_movie_names))
        return json.dumps(recommended_movie_names)


api.add_resource(Recommender, "/<string:selected_movie>", endpoint="recommend")
api.add_resource(Recommender, "/recommend", endpoint="recommendLiked")

if __name__ == "__main__":
    app.run(debug=True)

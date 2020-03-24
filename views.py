from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3 
from django.http import JsonResponse
import requests

i=0
# Create your views here.
def welcome(request):
	return render(request, 'getmovies.html')

def addMovie(request):
	if request.method == "GET":
		conn = sqlite3.connect('movies.db')
		cursor = conn.cursor()

		movie_name = request.GET['movie_name']
		cursor.execute("CREATE TABLE IF NOT EXISTS user_history(\
		movie_name text,\
		username text\
		);")
		conn.commit()

		cursor.execute("INSERT INTO user_history VALUES('user1',?);",(movie_name,))
		conn.commit()
		return HttpResponse("")

def recommend(request):
	return render(request, 'recommend.html')


def rssFeed(request):
	return render(request, 'rss.html')

# Create your views here.
def getRecommendations(request):  #content-based filtering
	print("g");
	#return render(request, 'home.html')
	#return render(request, 'home.html', {'name':'vinu'})
	df = pd.read_csv(r"C:\Users\SreedharK\Desktop\sixth semester\UE17CS355 - web tech-II lab\WebTech2-master\movie_dataset.csv")
	features = ['keywords','cast','genres','director']
	
	def combine_features(row):
	    return row['keywords'] +" "+row['cast']+" "+row["genres"]+" "+row["director"]
	
	for feature in features:
	    df[feature] = df[feature].fillna('')
	df["combined_features"] = df.apply(combine_features,axis=1)
	cv = CountVectorizer()
	count_matrix = cv.fit_transform(df["combined_features"])
	cosine_sim = cosine_similarity(count_matrix)  #minimum angle in a vector(2-d plane) - 0 to 1(1 is very similar)
	def get_title_from_index(index):
	    return df[df.index == index]["title"].values[0]
	def get_index_from_title(title):
	    return df[df.title == title]["index"].values[0]
	
	conn = sqlite3.connect('movies.db')
	cursor = conn.cursor()
	
	cursor.execute("select * from user_history")
	rows = cursor.fetchall()
	
	list_movies = []
	for row in rows:
		list_movies.append(row[1])
	
	movie_details = dict()
	
	for movie_user_likes in list_movies:
		movies = []
		movie_index = get_index_from_title(movie_user_likes)
		similar_movies =  list(enumerate(cosine_sim[movie_index]))
		sorted_similar_movies = sorted(similar_movies,key=lambda x:x[1],reverse=True)[1:] #highest to lowest similarity
		i=0
		for element in sorted_similar_movies:
			movies.append(get_title_from_index(element[0]))
			i=i+1
			if i>=4:
				break  #take first four
		movie_details[movie_user_likes] = movies
	print(movie_details)
	return JsonResponse(movie_details)

def top_chart(dataset, col, var, votes='vote_count',vote_average='vote_average',percentile=0.85):  #to be used by popularity-based filtering
    
    '''
    This function takes a dataset, column, subset and voting statistics to return a top chart.
    1. Filters the original dataset
    2. Determines the threshold for qualification based on percentile
    3. Returns the top 10 results, sorted by vote_count
    '''
    
    df = dataset[dataset[col] == var]
    vote_counts = df[df[votes].notnull()][votes].astype('int')
    vote_averages = df[df[vote_average].notnull()][vote_average].astype('int')
    C = vote_averages.mean()
    m = vote_counts.quantile(percentile)
    
    qualified = df[(df[votes] >= m) & (df[votes].notnull()) & (df[vote_average].notnull())][['title', votes, vote_average]]
    qualified[votes] = qualified[votes].astype('int')
    qualified[vote_average] = qualified[vote_average].astype('int')
    
    qualified = qualified.sort_values('vote_count', ascending=False).head(250)
    
    return qualified.head(10)

def getPopMovies(request):
	df = pd.read_csv(r"C:\Users\SreedharK\Desktop\sixth semester\UE17CS355 - web tech-II lab\WebTech2-master\movie_dataset.csv")
	list_movies=[]
	movie_votes = dict()
	for dff in df:   
		list_movies.append(dff[20])
	sorted_popular_movies = list_movies.sort(reverse=True)
	movie_detailss[sorted_popular_movies] = movies
	print(movie_detailss)
	print(JsonResponse(movie_detailss))

	#creating separate tables based on popularity of genres
	s = df.apply(lambda x: pd.Series(x['genres']),axis=1).stack().reset_index(level=1, drop=True)
	s.name = 'genre'
	gen_movies = df.drop('genres', axis=1).join(s)

	print(top_chart(gen_movies, 'genre', 'Comedy', votes='vote_count',vote_average='vote_average'))
	print(top_chart(gen_movies, 'genre', 'Animation', votes='vote_count',vote_average='vote_average'))
	print(top_chart(gen_movies, 'genre', 'Romance'))  #the additional common parameters are not necessary
	print(top_chart(gen_movies, 'genre', 'Adventure'))


def getMovies(request):
	movie_details=dict()	
	df = pd.read_csv(r"C:\Users\SreedharK\Desktop\sixth semester\UE17CS355 - web tech-II lab\WebTech2-master\movie_dataset.csv")
	df = df[:10]  #fetching the movie details of the first 25 movies (sending the titles of the movies)(first few movies)
	title = df["title"]
	movies = []
	for i in title:
		movies.append(i)
	movie_details["movies"] = movies
	return JsonResponse(movie_details)
	#return HttpResponse(s)

def user_history(request):
	conn = sqlite3.connect('movies.db')
	cursor = conn.cursor()
	#cursor.execute("delete from user_history")
	#conn.commit()
	cursor.execute("select * from user_history")
	rows = cursor.fetchall()
	user_history=dict()		
	list_users = []
	list_movies = []
	for row in rows:
		list_users.append(row[0])
		list_movies.append(row[1])
	user_history["users"] = list_users
	user_history["movies"] = list_movies
	return JsonResponse(user_history)

def pred_fetch(request):
	return render(request,'prefetch.html')

def fetch(request):
	movie_details=dict()	
	df = pd.read_csv(r"C:\Users\SreedharK\Desktop\sixth semester\UE17CS355 - web tech-II lab\WebTech2-master\movie_dataset.csv")
	title = df["title"]
	global i
	print(title[i])  #list of movies
	movie_details["movies"] = title[i]  
	i=i+1
	return JsonResponse(movie_details)
	
def getRSSFeed(request):
	data = requests.get("https://www.cinemablend.com/rss/topic/reviews/movies")
	#fp = open(r"C:\Users\VINU PC\Desktop\feeds.xml", "r")
	#data = fp.read()
	#fp.close()
	return HttpResponse(data.text, content_type='text/xml')
    #return HttpResponse(open('myxmlfile.xml').read(), content_type='text/xml')




########## get recomm ##########


# https://movieweb.com/rss/movie-reviews/
# https://www.cinemablend.com/rss/topic/reviews/movies
# https://www.cinemablend.com/rss/topic/previews/movies




######## getmovies ###########



"""	conn = sqlite3.connect('movies.db')
	cursor = conn.cursor()

	cursor.execute("CREATE TABLE IF NOT EXISTS movie_details(\
	movie_name text primary key,\
	keywords text,\
	cast text,\
	genres text,\
	director text\
	);")
	conn.commit()

"""
	
"""cursor.execute("INSERT INTO movie_details VALUES
	('Avatar','culture clash future space war space colony society','Sam Worthington Zoe Saldana Sigourney Weaver Stephen Lang Michelle Rodriguez','Action Adventure Fantasy Science Fiction','James Cameron'),\
	('Pirates of the Caribbean: At Worlds End','ocean drug abuse exotic island east india trading company love of ones life','Johnny Depp Orlando Bloom Keira Knightley Stellan Skarsgrd Chow Yun-fat','Adventure Fantasy Action','Gore Verbinski'),\
    ('Spectre','spy based on novel secret agent sequel mi6','Daniel Craig Christoph Waltz La Seydoux Ralph Fiennes Monica Bellucci','Action Adventure Crime','Sam Mendes'),\
    ('The Dark Knight Rises','dc comics crime fighter terrorist secret identity burglar','Christian Bale Michael Caine Gary Oldman Anne Hathaway Tom Hardy','Action Crime Drama Thriller','Christopher Nolan'),\
    ('John Carter','based on novel mars medallion space travel princess','Taylor Kitsch Lynn Collins Samantha Morton Willem Dafoe Thomas Haden Church','Action Adventure Science Fiction','Andrew Stanton'),\
    ('Spider-Man 3','dual identity amnesia sandstorm love of one''s life forgiveness','Tobey Maguire Kirsten Dunst James Franco Thomas Haden Church Topher Grace','Fantasy Action Adventure','Sam Raimi'),\
    ('Tangled','hostage magic horse fairy tale musical','Zachary Levi Mandy Moore Donna Murphy Ron Perlman M.C. Gainey','Animation Family','Byron Howard'),\
    ('Avengers: Age of Ultron','marvel comic sequel superhero based on comic book vision','Robert Downey Jr. Chris Hemsworth Mark Ruffalo Chris Evans Scarlett Johansson','Action Adventure Science Fiction','Joss Whedon'),\
    ('Harry Potter and the Half-Blood Prince','witch magic broom school of witchcraft wizardry','Daniel Radcliffe Rupert Grint Emma Watson Tom Felton Michael Gambon','Adventure Fantasy Family','David Yates'),\
    ('Batman v Superman: Dawn of Justice','dc comics vigilante superhero based on comic book revenge','Ben Affleck Henry Cavill Gal Gadot Amy Adams Jesse Eisenberg','Action Adventure Fantasy','Zack Snyder'),\
    ('Superman Returns','saving the world dc comics invulnerability sequel superhero','Brandon Routh Kevin Spacey Kate Bosworth James Marsden Parker Posey','Adventure Fantasy Action Science Fiction','Bryan Singer'),\
    ('Quantum of Solace','killing undercover secret agent british secret service','Daniel Craig Olga Kurylenko Mathieu Amalric Judi Dench Giancarlo Giannini','Adventure Action Thriller Crime','Marc Forster'),\
    ('Pirates of the Caribbean: Dead Man''s Chest','witch fortune teller bondage exotic island monster','Johnny Depp Orlando Bloom Keira Knightley Stellan Skarsgrd Bill Nighy','Adventure Fantasy Action','Gore Verbinski'),\
    ('The Lone Ranger','texas horse survivor texas ranger partner','Johnny Depp Armie Hammer William Fichtner Helena Bonham Carter James Badge Dale','Action Adventure Western','Gore Verbinski'),\
    ('Man of Steel','saving the world dc comics superhero based on comic book superhuman','Henry Cavill Amy Adams Michael Shannon Kevin Costner Diane Lane','Action Adventure Fantasy Science Fiction','Zack Snyder'),\
    ('The Chronicles of Narnia: Prince Caspian','based on novel fictional place brother sister relationship lion human being','Ben Barnes William Moseley Anna Popplewell Skandar Keynes Georgie Henley','Adventure Family Fantasy','Andrew Adamson'),\
    ('The Avengers','new york shield marvel comic superhero based on comic book','Robert Downey Jr. Chris Evans Mark Ruffalo Chris Hemsworth Scarlett Johansson','Science Fiction Action Adventure','Joss Whedon'),\
    ('Pirates of the Caribbean: On Stranger Tides','sea captain mutiny sword prime minister','Johnny Depp Penlope Cruz Ian McShane Kevin McNally Geoffrey Rush','Adventure Action Fantasy','Rob Marshall'),\
    ('Men in Black 3','time travel time machine alien fictional government agency seeing the future','Will Smith Tommy Lee Jones Josh Brolin Michael Stuhlbarg Emma Thompson','Action Comedy Science Fiction','Barry Sonnenfeld')")
	conn.commit()
	cursor.execute("select * from movie_details")
	rows = cursor.fetchall()
	movie_details=dict()		
	for row in rows:
		movie_name = row[0]
		director = row[4]
		movie_details[movie_name] = director 
"""
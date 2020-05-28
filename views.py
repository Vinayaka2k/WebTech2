#is this the latest one(show from github)
#difference between users table and users1.db
#what is i=12
#can we do unit testing for the (new one) functions
#about creating objects for test functions (do we hardcode it)
#what are the columns of the table/database
#test_views.py line 19 u,p,e or full forms?

from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import sqlite3 
from django.http import JsonResponse
import requests
from django.views.decorators.csrf import csrf_exempt

import unittest
import calc
#from unittest.mock import patchsq

i=12  #number of movies initially fetched before scrolling down
csv_path = r"C:\Users\SreedharK\Desktop\sixth semester\UE17CS355 - web tech-II lab\FINAL WT-2 PROJECT\proj1\movie_dataset.csv"  #change this path

# Create your views here.
def welcome(request):
	return render(request, 'sign_in.html')
def newsFeed(request):
	return render(request, 'rss_news.html')
def home(request):
	return render(request,'getmovies.html')
def usg(request):
	return render(request, 'sign_up.html')
def dyou(request):
	return render(request,'display_vedio.html')
def items(request):
	return render(request,'item.html')
def out(request):
	return render(request,'y.html')
def search_results(request):
	return render(request,'search_results.html')
 
@csrf_exempt 
def user_store(request):
	if request.method == "POST":
		conn = sqlite3.connect('users1.db')
		cursor = conn.cursor()
		username = request.POST['username']
		password= request.POST['password']
		email = request.POST['email']
		cursor.execute("CREATE TABLE IF NOT EXISTS users(username text PRIMARY KEY,password text,email text);")

		conn.commit()
		try:
			cursor.execute("INSERT INTO users VALUES(?,?,?);",(username,password,email))
			conn.commit()
		except:
			return HttpResponse("fail")

		return HttpResponse("succ")
		
	return "out"

	
@csrf_exempt 
def vusers(request):			#if username and password combination is correct 
	conn = sqlite3.connect('users1.db')
	cursor = conn.cursor()
	username = request.POST['username']
	password= request.POST['password']
	cursor.execute("SELECT password FROM users WHERE username=?",(username,))
	rows = cursor.fetchall()
	if(rows == []):
		return HttpResponse("no_user")
	valid_password = rows[0][0]
	if(valid_password == password):
		return 	HttpResponse("succ")
	else:
		return HttpResponse("fail")

@csrf_exempt
def vusername(request):			#if username is valid
	conn = sqlite3.connect('users1.db')
	cursor = conn.cursor()
	username = request.POST['username']
	cursor.execute("SELECT count(*) FROM users WHERE username=?",(username,))
	rows = [item[0] for item in cursor.fetchall()]
	
	if(rows[0] == 0):
		return 	HttpResponse("pass")
	else:
		return 	HttpResponse("fail")



def dis_img(request):
	f = open("mov1.jpg","rb")
	p=f.read()
	return HttpResponse(p, content_type='img/jpg')


def addMovie(request):			#adds movie to database
	if request.method == "GET":
		conn = sqlite3.connect('movie.db')
		cursor = conn.cursor()

		movie_name = request.GET['movie_name']
		username = request.GET['username']
		print(movie_name)
		cursor.execute("CREATE TABLE IF NOT EXISTS user_history(\
		movie_name text,\
		username text\
		);")
		conn.commit()

		cursor.execute("INSERT INTO user_history VALUES(?,?);",(movie_name,username,))
		print("success")
		conn.commit()
		return HttpResponse("")

def get_suggestions(request):
	prefix = request.GET['moviePart']
	prefix = prefix.capitalize()
	result = []
	df = pd.read_csv(csv_path)
	title_list = list(df["title"])
	for title in title_list:
		if(title.startswith(prefix)):
				result.append(title)
	
	return JsonResponse(result,safe=False)

def recommend(request):
	return render(request, 'recommend.html')


def rssFeed(request):
	return render(request, 'rss.html')

# Create your views here.
def jaccard_similarity(list1, list2):
    intersection = len(list(set(list1).intersection(list2)))
    union = (len(list1) + len(list2)) - intersection
    return float(intersection) / union

def collabfilter(request):   #sudhamshu
	username = request.GET['username']
	conn = sqlite3.connect('users1.db')
	cursor = conn.cursor()
	cursor.execute("SELECT username FROM users")
	rows = cursor.fetchall()
	
	list_users = []
	for row in rows:
		list_users.append(row[0])
	
	conn = sqlite3.connect('movie.db')
	cursor = conn.cursor()
	p=dict()
	for i in range(0,len(list_users)):
		cursor.execute("select movie_name from user_history where username=?",(list_users[i],))
		rows = cursor.fetchall()
		list_movies = []
		for row in rows:
			list_movies.append(row[0])
		p[list_users[i]]=list_movies 
	movie_list=[]
	j=dict()	
	u=p[username]
	if(len(p[username])==0):
		return JsonResponse(movie_list,safe=False)

	for i in p:
		if(i!=username):
			j[i]=jaccard_similarity(p[username],p[i])
			print(i,j[i])
	Keymax = max(j, key=j.get)
	
	
	if(j[Keymax]==0):
		return JsonResponse(movie_list,safe=False)
	else:
		res = list(set(p[Keymax])-set(p[username]))
	print(p[Keymax],p[username])
	return JsonResponse(res,safe=False)
	

def getRecommendations(request):  #sudhamshu
	
	#return render(request, 'home.html')
	#return render(request, 'home.html', {'name':'vinu'})
	username = request.GET['username']
	df = pd.read_csv(csv_path)
	features = ['keywords','cast','genres','director']
	
	def combine_features(row):
	    return row['keywords'] +" "+row['cast']+" "+row["genres"]+" "+row["director"]
	
	for feature in features:
	    df[feature] = df[feature].fillna('')
	df["combined_features"] = df.apply(combine_features,axis=1)
	cv = CountVectorizer()
	count_matrix = cv.fit_transform(df["combined_features"])
	cosine_sim = cosine_similarity(count_matrix)
	def get_title_from_index(index):
	    return df[df.index == index]["title"].values[0]
	def get_index_from_title(title):
		return df[df.title == title]["index"].values[0]
	
	
	conn = sqlite3.connect('movie.db')
	cursor = conn.cursor()
	
	cursor.execute("select movie_name from user_history where username=?",(username,))
	rows = cursor.fetchall()
	
	list_movies = []
	for row in rows:
		if(row[0] in list(df["title"])): 	
			list_movies.append(row[0])
	
	movie_details = dict()
	print(list_movies)
	
	for movie_user_likes in list_movies:
		movies = []
		movie_index = get_index_from_title(movie_user_likes)
		
		similar_movies =  list(enumerate(cosine_sim[movie_index]))
		sorted_similar_movies = sorted(similar_movies,key=lambda x:x[1],reverse=True)[1:]
		i=0
		for element in sorted_similar_movies:
			movies.append(get_title_from_index(element[0]))
			i=i+1
			if i>=4:
				break
		movie_details[movie_user_likes] = movies
	for key in movie_details:
		movie_details[key]=list(set(movie_details[key])-set(list_movies))
	return JsonResponse(movie_details)

def getMovies():      #gets the movies from the csv file
	movie_details=dict()	
	df = pd.read_csv(csv_path)
	df = df[0:12]
	title = df["title"]   # takes the title column of the dataframe
	movies = []
	for i in title:
		movies.append(i)
	movie_details["movies"] = movies

	return JsonResponse(movie_details)   #jrmd
	#return HttpResponse(s)

def pred_fetch():   #(new one)
	movie_details=dict()	
	df = pd.read_csv(csv_path)
	global i
	df = df[i:i+4]
	i=i+4
	title = df["title"]
	movies = []
	for j in title:
		movies.append(j)
	movie_details["movies"] = movies
	print(movies)
	return JsonResponse(movie_details)
	
def user_history():
	conn = sqlite3.connect('movie.db')
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


def getRSSFeed():
	data = requests.get("https://www.cinemablend.com/rss/topic/reviews/movies")
	#fp = open(r"C:\Users\VINU PC\Desktop\feeds.xml", "r")
	#data = fp.read()
	#fp.close()
	return HttpResponse(data.text, content_type='text/xml')
    #return HttpResponse(open('myxmlfile.xml').read(), content_type='text/xml')


def getNewsFeed():   #(new one)
	data = requests.get("https://www.filmibeat.com/rss/filmibeat-hollywood-fb.xml")
	return HttpResponse(data.text, content_type='text/xml')
    


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

def test_jaccard_similarity(list1,list2):
    	ans = jaccard_similarity(list1,list2)
        intersection = len(list(set(list1).intersection(list2)))
        union = (len(list1) + len(list2)) - intersection
        pred = float(intersection) / union
        if(ans==pred):
                print("success")
        else:
                print("fail")
test_jaccard_similarity([1,2,3],[4,5,6])

def test_user_store(username,password,email):   
	PARAMS = {'username':username,'password':password,'email':email}
	URL = "http://www.google.com"
  	r = requests.get(url = URL, params = PARAMS)
	user_store(r)#create a request object-username,pwd,email
	r = sqlite3.execute("select * from users")
	if(r[-1]==username):
		print("success")
	else:
		print("fail")
test_user_store("username","password","email")

def test_vusers(username,password,email):   
	#user_store()        #create a request object-username,pwd,email
	PARAMS = {'username':username,'password':password,'email':email} 
  	URL = "http://www.google.com"
  	r = requests.get(url = URL, params = PARAMS) 
  	k = requests.get(url = URL, params = PARAMS) 

	vusers(r) 
	r = sqlite3.execute("select username from users")

	vusers(k)
	k = sqlite3.execute("select password from users")
	if(r[-1]==username and k[-1]==password):  #-1 indicates last entry/row
		print("success")
	else:
		print("fail")
test_vusers("username","password","email")


def test_vusername(username,password,email):   
# sending get request and saving the response as response object 
	PARAMS = {'username':username,'password':password,'email':email} 
  	URL = "http://www.google.com"
	r = requests.get(url = URL, params = PARAMS) 
	vusername(r)        #create a request object-username,pwd,email
	r = sqlite3.execute("select * from users")
	if(r[-1]==username):
		print("success")
	else:
		print("fail")
test_vusername("username","password","email")

def test_addMovie(username,movie_name):   
	PARAMS = {'username':username,'movie_name':movie_name} 
  	URL = "http://www.google.com"
  	r = requests.get(url = URL, params = PARAMS) 
  	k = requests.get(url = URL, params = PARAMS) 

	addMovie(r) 
	r = sqlite3.execute("select username from user_history")

	addMovie(k)
	k = sqlite3.execute("select movie_name from user_history")
	if(r[-1]==username and k[-1]==movie_name):  #-1 indicates last entry/row
		print("success")
	else:
		print("fail")
test_addMovie("username","Avatar")

def test_getMovies(movie_details):
	movie_deta=dict()	
	df = pd.read_csv(csv_path)
	df = df[0:12]
	title = df["title"]   # takes the title column of the dataframe
	movies = []
	for i in title:
		movies.append(i)
	movie_deta["movies"] = movies
	if(JsonResponse(movie_deta)==getMovies()):
		print("success")
	else:
    		print("fail")
test_getMovies(movie_details)

def test_pred_fetch(movie_details):
	movie_deta=dict()	
	df = pd.read_csv(csv_path)
	global i
	df = df[i:i+4]
	i=i+4
	title = df["title"]
	movies = []
	for j in title:
		movies.append(j)
	movie_deta["movies"] = movies
	#print(movies)
	if(JsonResponse(movie_deta)==pred_fetch()):
		print("success")
	else:
    		print("fail")
test_pred_fetch(movie_details)

def test_user_history(user_history):
  	conn = sqlite3.connect('movie.db')
	cursor = conn.cursor()
	#cursor.execute("delete from user_history")
	#conn.commit()
	cursor.execute("select * from user_history")
	rows = cursor.fetchall()
	user_hist=dict()		
	list_users = []
	list_movies = []
	for row in rows:
		list_users.append(row[0])
		list_movies.append(row[1])
	user_hist["users"] = list_users
	user_hist["movies"] = list_movies
	if(JsonResponse(user_history)==user_history()):
		print("success")
	else:
    		print("fail")
test_user_history(user_history)

def test_getRSSFeed():
	data1 = requests.get("https://www.cinemablend.com/rss/topic/reviews/movies")
	#fp = open(r"C:\Users\VINU PC\Desktop\feeds.xml", "r")
	#data = fp.read()
	#fp.close()
	if(HttpResponse(data1.text, content_type='text/xml')==getRSSFeed()):
		print("success")
	else:
    		print("fail")
test_getRSSFeed()


def getNewsFeed():   #(new one)
	data2 = requests.get("https://www.filmibeat.com/rss/filmibeat-hollywood-fb.xml")
	if(HttpResponse(data2.text, content_type='text/xml')==getNewsFeed()):
    		print("success")
	else:
    		print("fail")
test_getNewsFeed()
    #return HttpResponse(open('myxmlfile.xml').read(), content_type='text/xml')

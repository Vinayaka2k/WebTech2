from django.urls import path
from . import views
urlpatterns = [
	path('get_recommendations',views.getRecommendations,name="get_recommendations"),   #for content-based filtering
	path('get_pop_movies',views.getPopMovies,name="get_pop_movies"),   #for popularity-based filtering
	path('getmovies',views.getMovies,name="getmovies"),
	path('welcome',views.welcome,name="welcome"),
	path('add_movie',views.addMovie,name="add_movie"),
	path('recommend',views.recommend,name="recommend"),
	path('user_history',views.user_history,name="user_history"),
	path('get_rss_feed',views.getRSSFeed,name="get_rss_feed"),
	path('rss_feed',views.rssFeed,name="rss_feed"),
	path('pred_fetch',views.pred_fetch,name="pred_fetch"),
	path('fetch',views.fetch,name="fetch")

]
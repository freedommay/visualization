from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('food', views.food_full_page, name='food'),
    path('food/1/', views.food_page_first, name='food1'),
    path('food/2/', views.food_page_second, name='food2'),
    path('food/3/', views.food_page_third, name='food3'),
    path('food/4/', views.food_page_fourth, name='food4'),
    path('food/5/', views.food_page_fifth, name='food5'),
    path('food/6/', views.food_page_six, name='food6'),
    path('spot/1/', views.spot_page_first, name='spot1'),
    path('spot/2/', views.spot_page_second, name='spot2'),
    path('spot/3/', views.spot_page_third, name='spot3'),
    path('spot/4/', views.spot_page_fourth, name='spot4'),
    path('spot/5/', views.spot_page_fifth, name='spot5'),
    path('house/1', views.house_page_first, name='house1'),
    path('house/2', views.house_page_second, name='house2'),
    path('weather/1/', views.weather_page_first, name='weather1'),
    path('weather/2/', views.weather_page_second, name='weather2'),
    path('weather/3/', views.weather_page_third, name='weather3')
]

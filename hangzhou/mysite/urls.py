from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('food/1/', views.food_page_first, name='food1'),
    path('food/2/', views.food_page_second, name='food2'),
    path('food/3/', views.food_page_third, name='food3'),
    path('food/4/', views.food_page_fourth, name='food4'),
    path('food/5/', views.food_page_fifth, name='food5'),
    path('spot/1/', views.spot_page_first, name='spot1'),
    path('house/1', views.house_page_first, name='house1'),
    path('weather/1/', views.weather_page_first, name='weather1'),
    path('weather/2/', views.weather_page_second, name='weather2'),
    path('weather/3/', views.weather_page_third, name='weather3')
]

from django.urls import path
from . import views 

app_name = 'restaurants'

urlpatterns = [
    path('', views.home, name='home'),
    path('list/', views.restaurant_list, name='list'),
    path('create/', views.restaurant_create, name='create'),
    path('r/<int:id>/', views.restaurant_detail_by_id, name='detail_by_id'),  
    path('<slug:slug>/', views.restaurant_detail, name='detail'),
    path('<slug:slug>/edit/', views.restaurant_edit, name='edit'),
    path('<slug:slug>/tables/', views.table_management, name='table_management'),
    path('<slug:slug>/menu/', views.menu_management, name='menu_management'),
    path('chatbot/', views.chatbot_view, name='chatbot'),
]

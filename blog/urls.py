from django.urls import path
from . import views
from . import my_practice_views

app_name = 'blog'  # app_name == namespace  в mysite/urls.py

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('tag/<slug:tag_slug>/', views.post_list, name='post_list_by_tag'),
    path('<int:year>/<int:month>/<int:day>/<slug:slug>/', views.post_detail, name='post_detail'),
    path('<int:post_id>/share/', views.post_share, name='post_share'),
    # path('test/', my_practice_views.post_listed, name='post_list_my'),

]

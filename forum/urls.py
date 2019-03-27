from django.urls import path

from . import views

app_name = 'forum'

urlpatterns = [
    # Outer URLS

    path('government-rules/', views.goverment_rules, name='government_rules'),

    # /login/
    path('login/', views.login, name='login'),

    # /signup/
    path('signup/', views.signup, name='signup'),

    # /home/
    path('home', views.home, name='home'),

    # /
    path('', views.index, name='index'),

    # /farmer/<int:pk>
    path('farmer/<int:pk>', views.FarmerDetailView.as_view(), name='farmer_detail'),
    
    # /question/<int:pk>
    path('question/<int:pk>', views.question_detail_view, name='question_detail'),

    # /logout/
    path("logout/", views.logout, name="logout"),

    # create-question/
    path("create-question/", views.create_question, name="create_question"),

    # specialists/
    path("specialists/", views.specialists, name="specialists"),

    # edit/
    path("edit/", views.FarmerUpdateView.as_view(), name="edit_farmer"),

    # search?q=<search_term>
    path("search", views.search, name="search"),
    
    # AJAX URLS

    # upvote-question/

    path("upvote-question/", views.upvote_question, name="upvote_question"),

    # upvote-answer/
    path("upvote-answer/", views.upvote_answer, name="upvote_answer"),

    path("verify-farmer/<int:phone_number>/<str:account_token>/", views.verify_farmer, name="verify_farmer"),


    ]
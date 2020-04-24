from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    # ex: /polls/
    path('user_register/', views.UserRegister, name="user_register"),
    path('', views.home, name='home'),
    path('buy/', views.buy, name='buy'),
    path('query/', views.query_status, name='query'),
    path('login/', auth_views.LoginView.as_view(template_name='frontEndServer/login.html'), name='login'),
    path('prime_register/', views.PrimeRegiseterView, name='prime_register'),

    # # ex: /polls/5/
    # path('<int:question_id>/', views.detail, name='detail'),
    # # ex: /polls/5/results/
    # path('<int:question_id>/results/', views.results, name='results'),
    # # ex: /polls/5/vote/
    # path('<int:question_id>/vote/', views.vote, name='vote'),
]
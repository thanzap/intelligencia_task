from django.urls import path, re_path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns=[
    path('efoterms/', views.get_efo_terms, name='get_efo_terms'),
    path('efoterm/', views.handle_efo_term, name='handle_efo_term'),
    path('efoterm/<str:efo_term_id>/', views.efo_term, name='get_efo_term'),
    path('efoterm/<str:efo_term_id>/parents', views.get_parents_of_term, name='get_parents_of_term'),
    path('efoterm/<str:efo_term_id>/children', views.get_children_of_term, name='get_children_of_term'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    re_path(r'^token/refresh/$', TokenRefreshView.as_view(), name='token_refresh'),
]
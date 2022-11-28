from django.urls import path, include
from . import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
app_name = "image"

urlpatterns = [

    path('register/', views.RegistrationView.as_view(), name='registration'),
    path('login/', views.ObtainAuthToken.as_view(), name='login'),

    path('logout/', views.LogoutView.as_view(), name='logout'),
   path('upload/', views.FileSharePostView.as_view(), name='upload'),
   path('file/<str:link>/',views.FileSharedView.as_view(),name='file'),
]
urlpatterns += staticfiles_urlpatterns()
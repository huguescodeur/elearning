"""
URL configuration for elearning project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from . import views
from account.views import connexion_view, inscription_view, logout_view, settings_view, update_user_info_view, update_image_view, delete_account_view, premium_account_view, envoie_message_view, forgot_password_view, reset_password_view
from django.conf import settings
from django.conf.urls.static import static
from videos.views import formations_view, playlist_formations_view, tutoriels_view, playlist_tutorial_view, search_suggestions_formations

urlpatterns = [
    path('priscille/', admin.site.urls),
    path('', views.index_view, name="accueil"),
    path('tutoriels/', tutoriels_view, name="tutoriels"),
    path('formations/', formations_view, name="formations"),
    path('formations/playlist/<str:course>/', playlist_formations_view,
         name="mes_formations"),
    path('formations/playlist/<str:course>/<str:selected_slug>/', playlist_formations_view,
         name="mes_formations_slug"),
    path('tutoriels/playlist/<str:course>/<str:selected_slug>/',
         playlist_tutorial_view, name="mes_tutoriels"),
    path('formations/search_suggestions_formations/', search_suggestions_formations,
         name='search_formations'),

    path('blog/', views.blog_view, name="blog"),
    path('contact/', views.contact_view, name="contact"),
    path('connexion/', connexion_view, name="connexion"),
    path('inscription/', inscription_view, name="inscription"),
    path('logout/', logout_view, name='logout'),
    path('settings/edit/', settings_view, name='settings'),
    path('settings/update/', update_user_info_view, name='update_user_info'),
    path('image/update/', update_image_view, name='update_image'),
    path('delete_account/', delete_account_view, name='delete_account'),
    path('premium/', premium_account_view, name='premium'),
    path('envoie_message/', envoie_message_view, name='envoie_message'),
    path('password/', forgot_password_view, name='password_reset'),
    path('reset_password/',
         reset_password_view, name='reset_password'),
    
]

if settings.DEBUG is False:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

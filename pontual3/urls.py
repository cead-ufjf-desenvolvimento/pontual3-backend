from django.urls import path, include

urlpatterns = [
    path('', include('pontualApp.urls')),
    path('api-auth/', include('rest_framework.urls')),
]

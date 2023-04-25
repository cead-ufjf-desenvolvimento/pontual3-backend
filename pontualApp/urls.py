from rest_framework.routers import DefaultRouter
from pontualApp import views
from django.urls import include, path

router = DefaultRouter()
router.register(r'usuario', views.UsuarioViewSet, basename='usuario')
router.register(r'justificativa', views.JustificativaViewSet, basename='justificativa')
router.register(r'login', views.LoginViewSet, basename='login')
router.register(r'ponto', views.PontoViewSet, basename='ponto')
router.register(r'sugestao', views.SugestaoViewSet, basename='sugestao')
router.register(r'justificativaadicional', views.JustificativaAdicionalViewSet, basename='justificativaadicional')

urlpatterns = [
    path('', include(router.urls)),
]

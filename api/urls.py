from django.urls import path

from .views import bbs, BbDetailView, comments, SubRubrics

urlpatterns = [
    path('bbs/<int:pk>/comments/', comments),
    path('bbs/<int:pk>/', BbDetailView.as_view()),
    path('rubrics/', SubRubrics.as_view()),
    path('bbs/', bbs),
]
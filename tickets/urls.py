from django.conf.urls import url
from django.contrib import admin

from .views import (
    ExamTemplateView,
    QuestionDetailView,
    MarathonTemplateView,
    TicketListView,
    ThemeListView,
    
    )


urlpatterns = [
    url(r'^$', TicketListView.as_view(), name='ticket_list'),
    url(r'^(?P<pk>[\d-]+)/$', QuestionDetailView.as_view(), name='question_detail'),
    url(r'^exam/$', ExamTemplateView.as_view(), name='exam'),
    url(r'^marathon/$', MarathonTemplateView.as_view(), name='marathon'),
    url(r'^theme/$', ThemeListView.as_view(), name='theme_list'),

]

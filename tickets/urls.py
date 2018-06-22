from django.conf.urls import url
from django.contrib import admin

from .views import (
    ErrorsReportView,
    ExamTemplateView,
    Errors,
    QuestionDetailView,
    MarathonTemplateView,
    TicketListView,
    TicketReportView,
    ThemeListView,
    ThemeReportView,
    pdddataAdd,
    pdddataClear,
    )


urlpatterns = [
    url(r'^$', TicketListView.as_view(), name='ticket_list'),
    url(r'^(?P<pk>[\d-]+)/$', QuestionDetailView.as_view(), name='question_detail'),
    url(r'^errors/$', Errors.as_view(), name='errors'),
    url(r'^exam/$', ExamTemplateView.as_view(), name='exam'),
    url(r'^marathon/$', MarathonTemplateView.as_view(), name='marathon'),
    url(r'^theme/$', ThemeListView.as_view(), name='theme_list'),

    url(r'^(?P<pk>[\d-]+)/pdddataAdd/$', pdddataAdd, name='pdddataAdd'),
    url(r'^clear/$', pdddataClear, name='pdddataClear'),

    url(r'^errors_report/$', ErrorsReportView.as_view(), name='errors_report'),  
    url(r'^ticket_report/$', TicketReportView.as_view(), name='ticket_report'),
    url(r'^theme_report/$', ThemeReportView.as_view(), name='theme_report'),

]

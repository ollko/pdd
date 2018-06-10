# coding=utf-8


from django.views.generic import (
	DetailView, ListView, TemplateView,
	)
from .models import (
	Ticket,
	Question,
	Theme,
	)

class TicketListView(ListView):
	model = Ticket
	template_name = 'tickets/ticket_list.html'
	context_object_name = 'tickets'


class ThemeListView(ListView):
	model = Theme
	template_name = 'tickets/theme_list.html'
	context_object_name = 'themes'


class QuestionDetailView(DetailView):
	model = Question
	template_name = 'tickets/question_detail.html'	
	context_object_name = 'question'


class ExamTemplateView(TemplateView):
	template_name = 'tickets/exam.html'


class MarathonTemplateView(TemplateView):
	template_name = 'tickets/marathon.html'

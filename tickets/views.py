# coding=utf-8

import re


from django.http import Http404
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import (
    DetailView, ListView, TemplateView,
    )
# from django.views.generic.edit import FormMixin
from django.views.decorators.http import require_POST


from .models import (
    Ticket,
    Question,
    Theme,
    Choice,
    )
from pass_data import Pdddata, Stars, Themedata, Report
from generic.mixins import PddContextMixin


class TicketListView(PddContextMixin, TemplateView):
    template_name = 'tickets/ticket_list.html'


    def get_context_data(self, *args, **kwargs):
        context = super(TicketListView, self).get_context_data(*args, **kwargs) 
        pdddata = Pdddata(self.request).pdddata
        tickets = Ticket.objects.all()
        ticket_with_ans = []
        for ticket in tickets:
            t = ticket.tick_number
            tick_item = [ ticket ]
            if str(t) in pdddata.keys():
                w = len( pdddata[ str(t) ] )
                r = len(ticket.questions.all()) - w
                tick_item.append(r)
                tick_item.append(w)
            ticket_with_ans.append(tick_item)
        context['tickets'] = ticket_with_ans
        return context


class ThemeListView(PddContextMixin, TemplateView):
    template_name = 'tickets/theme_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ThemeListView, self).get_context_data(*args, **kwargs) 
        themedata = Themedata(self.request).themedata
        themes = Theme.objects.all()
        theme_with_ans = []
        for theme in themes:
            theme_id = theme.id
            theme_item = [ theme ]
            if str(theme_id) in themedata.keys():
                w = len( themedata[ str(theme_id) ] )
                r = len(theme.questions.all()) - w
                theme_item.append(r)
                theme_item.append(w)
            theme_with_ans.append(theme_item)
        context['themes'] = theme_with_ans
        return context


class QuestionDetailView(DetailView):
    model = Question
    template_name = 'tickets/question_detail.html'  
    context_object_name = 'question'


    def get_context_data(self, *args, **kwargs):
        context = super(QuestionDetailView, self).get_context_data(*args, **kwargs)

        if re.match(r'\/tickets\/\d+\/', self.request.path):
            tab =  'tickets'
        else:
            tab =  None
        context['tab'] = tab
     
        stars = Stars( self.request )
        context['stars'] = stars.stars
        n = len(self.object.ticket.questions.all()) - len(stars.stars)
        context['grey_stars'] = [None for i in range(n)]
        return context


@require_POST
def pdddataAdd(request, pk):
     # pk - pk вопроса
    pdddata = Pdddata(request)
    stars = Stars(request)
    report = Report(request)
    question = get_object_or_404( Question, pk = pk )
    question_id_list = question.get_question_id_list_in_ticket()
    if int(pk) == question_id_list[0]:
        pdddata.remove_ticket(question)
       

    user_choice = int(request.POST['choice'])
    right_choice = question.get_right_choice
    
    if not user_choice == right_choice:
        pdddata.add_data(question, user_choice)
        stars.add_data(question, data = 'red')
    else:
        stars.add_data(question, data = 'green')
    try:
        next_question_id = question_id_list[ question_id_list.index( int(pk) ) +1 ]
    except IndexError:
        # пройдены все вопросы в билете:
        # записываем число правильных/неправильных вопросов для отчета по билету
        right, wrong = ( 0, 0 )
        for item in stars.stars:
            if item == 'green':
                right += 1
            else:
                wrong += 1
        ticket_id = str(question.ticket.id)
        report.add_data(ticket_id, right, wrong)
        stars.clear()
        return redirect( '/tickets/ticket_report?ticket_id=' + ticket_id )
    return redirect('tickets:question_detail', str(next_question_id))
    


def pdddataClear(request):
    pdddata = Pdddata(request)
    stars = Stars(request)
    report = Report(request)
    pdddata.clear()
    stars.clear()
    report.clear()
    return redirect('tickets:ticket_list')


class TicketReportView(TemplateView):
    template_name = 'tickets/ticket_report.html'
    

    def get_context_data(self, **kwargs):
        context = super(TicketReportView, self).get_context_data(**kwargs)
        report = Report(self.request)
        pdddata = Pdddata(self.request)
        ticket_id = self.request.GET['ticket_id']
        ticket = get_object_or_404(Ticket, id = ticket_id)
        
        try:
            one_ticket_report_data = report.report[ 'ticket_' + ticket_id ]
        except KeyError:
            raise Http404('Билет еще не пройден!')
        context['ticket_number'] = ticket.tick_number
        print 'one_ticket_report_data = ',one_ticket_report_data
        context['right_ans'] = one_ticket_report_data[ 'right' ]
        context['wrong_ans'] = one_ticket_report_data[ 'wrong' ]
        
        # данные для сводки правильный/неправильный ответ
        try:
            pdddata_one_ticket = pdddata.pdddata[ticket_id]
        except KeyError:
            return context

        data = []
        for item in pdddata_one_ticket:
            d = {}
            question = Question.objects.get(id = item['question'])
            d['question'] = question

            d['user_wrong_choice'] = Choice.objects.get(id = item['user_wrong_choice_id']).choice_text
            data.append(d)
        context['data'] = data
        return context


class ExamTemplateView(PddContextMixin, TemplateView):
    template_name = 'tickets/exam.html'


class MarathonTemplateView(PddContextMixin, TemplateView):
    template_name = 'tickets/marathon.html'

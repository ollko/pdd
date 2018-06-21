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
from pass_data import Pdddata, Stars, Themedata, Report, ErrorsPdd
from generic.mixins import PddContextMixin


class TicketListView(PddContextMixin, TemplateView):
    template_name = 'tickets/ticket_list.html'


    def get_context_data(self, *args, **kwargs):
        context = super(TicketListView, self).get_context_data(*args, **kwargs) 
        report = Report(self.request).report
        tickets = Ticket.objects.all()
        ticket_with_result = []
        for ticket in tickets:
            tick_item = report.get( 'ticket_' + str(ticket.id), {} )
            tick_item[ 'ticket' ] = ticket
            ticket_with_result.append(tick_item)
        context['tickets'] = ticket_with_result
        return context

# self.report= {u'ticket_1': {u'wrong': 14, u'right': 6}, u'ticket_2': {'wrong': 1, 'right': 1}}

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
    pdddata, stars, report, errors = (
        Pdddata(request),
        Stars(request),
        Report(request),
        ErrorsPdd(request),
    )
    question = get_object_or_404( Question, pk = pk )
    question_id_list = question.get_question_id_list_in_ticket()
    
    user_choice = int(request.POST['choice'])
    right_choice = question.get_right_choice
    question_id = unicode( question.id )

    if not user_choice == right_choice:
        wrong_text = get_object_or_404( Choice, pk = user_choice ).choice_text
        right_text = get_object_or_404( Choice, pk = right_choice ).choice_text
        errors.add_data( question_id, wrong_text, right_text )
        stars.add_data(question, data = 'red')
    else:
        print 'errors.errors=',errors.errors
        if question_id in errors.errors.keys():
            errors.remove_question_data( question_id )
        stars.add_data(question, data = 'green')
    try:
        next_question_id = question_id_list[ question_id_list.index( int(pk) ) +1 ]
    except IndexError:
        # пройдены все вопросы в билете -> записываем число правильных/неправильных вопросов
        # для отчета по билету
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
    pdddata, stars, report, errors = (
        Pdddata(request),
        Stars(request),
        Report(request),
        ErrorsPdd(request),
    )
    pdddata.clear()
    stars.clear()
    report.clear()
    errors.clear()
    return redirect('tickets:ticket_list')


class TicketReportView(TemplateView):
    template_name = 'tickets/ticket_report.html'
    

    def get_context_data(self, **kwargs):
        context = super(TicketReportView, self).get_context_data(**kwargs)
        pdddata, stars, report, errors = (
            Pdddata(self.request),
            Stars(self.request),
            Report(self.request),
            ErrorsPdd(self.request),
        )
        ticket_id = self.request.GET['ticket_id']
        ticket = get_object_or_404(Ticket, id = ticket_id)
        
        try:
            one_ticket_report_data = report.report[ 'ticket_' + ticket_id ]
        except KeyError:
            raise Http404('Билет еще не пройден!')
        context['ticket_number'] = ticket.tick_number
        context['right_ans'] = one_ticket_report_data[ 'right' ]
        context['wrong_ans'] = one_ticket_report_data[ 'wrong' ]
        
        # данные для сводки правильный/неправильный ответ
        question_id_with_error = set( errors.errors.keys() )
        question_in_current_ticket = set( ticket.get_question_id_list_in_ticket())
        print 'question_id_with_error = ',question_id_with_error
        print 'question_in_current_ticket = ',question_in_current_ticket
        current_question_wrong_answers = question_id_with_error & question_in_current_ticket

        data = []
        for item in current_question_wrong_answers:
            data.append( errors.errors[ item ] )


        # try:
        #     pdddata_one_ticket = pdddata.pdddata[ticket_id]
        # except KeyError:
        #     return context

        # data = []
        # for item in pdddata_one_ticket:
        #     d = {}
        #     question = Question.objects.get(id = item['question'])
        #     d['question'] = question

        #     d['user_wrong_choice'] = Choice.objects.get(id = item['user_wrong_choice_id']).choice_text
        #     data.append(d)
        context['data'] = data
        return context


class ExamTemplateView(PddContextMixin, TemplateView):
    template_name = 'tickets/exam.html'


class MarathonTemplateView(PddContextMixin, TemplateView):
    template_name = 'tickets/marathon.html'

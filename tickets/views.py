# coding=utf-8

import re


from django.http import Http404, HttpResponse, HttpResponseNotAllowed
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
from pass_data import Stars, Report, ErrorsPdd, Timer
from generic.mixins import PddContextMixin

# self.report= {u'ticket_1': {u'wrong': 14, u'right': 6}, u'ticket_2': {'wrong': 1, 'right': 1}}


class TicketListView(PddContextMixin, TemplateView):
    template_name = 'tickets/ticket_list.html'


    def get_context_data(self, *args, **kwargs):
        context = super(TicketListView, self).get_context_data(*args, **kwargs) 
        report = Report(self.request).report
        stars = Stars(self.request)
        stars.clear()
        tickets = Ticket.objects.all()
        ticket_with_result = []
        for ticket in tickets:
            tick_item = report.get( 'ticket_' + str(ticket.id), {} )
            tick_item[ 'tick_number' ] = ticket.tick_number
            tick_item[ 'first_question_num' ] = ticket.get_first_question_num()

            ticket_with_result.append(tick_item)
        # print 'ticket_with_result = ',ticket_with_result
        context['tickets'] = ticket_with_result
        self.request.session['nav_tab'] = 'ticket'
        return context

class ThemeListView(PddContextMixin, TemplateView):
    template_name = 'tickets/theme_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ThemeListView, self).get_context_data(*args, **kwargs)
        report = Report(self.request).report
        stars = Stars(self.request)
        themes = Theme.objects.all()
        theme_with_result = []
        for theme in themes:
            theme_item = report.get( 'theme_' + str(theme.id), {} )
            theme_item[ 'theme_name' ] = theme.name
            theme_item[ 'first_question_num' ] = theme.get_first_question_num()

            theme_item[ 'ticket_number' ] = len(theme.questions.all())
            theme_with_result.append(theme_item)
        context['themes'] = theme_with_result
        self.request.session['nav_tab'] = 'theme'
        return context


class QuestionDetailView(DetailView):
    model = Question
    template_name = 'tickets/question_detail.html'  
    context_object_name = 'question'


    def get_context_data(self, *args, **kwargs):
        context = super(QuestionDetailView, self).get_context_data(*args, **kwargs)

        # if re.match(r'\/tickets\/\d+\/', self.request.path):
        #     tab =  'tickets'
        # else:
        #     tab =  None
        # context['tab'] = tab
     
        stars = Stars( self.request )
        context['stars'] = stars.stars
        nav_tab = self.request.session.get('nav_tab')
        context['nav_tab'] = nav_tab
        if nav_tab == 'ticket':
            star_num = len(self.object.ticket.questions.all())
        elif nav_tab == 'theme':           
            star_num = len(self.object.theme.questions.all())
        else:
            star_num = self.request.session['grey_stars']
        n = star_num - len(stars.stars)  
        context['grey_stars'] = [None for i in range(n)]
        return context


@require_POST
def pdddataAdd(request, pk):
     # pk - pk вопроса
    stars, report, errors = (
        Stars(request),
        Report(request),
        ErrorsPdd(request),
    )

    question = get_object_or_404( Question, pk = pk )
    user_choice = int(request.POST['choice'])
    right_choice = question.get_right_choice
    question_id = unicode( question.id )

    if not user_choice == right_choice:
        wrong_text = get_object_or_404( Choice, pk = user_choice ).choice_text
        right_text = get_object_or_404( Choice, pk = right_choice ).choice_text
        # print 'было неправильных ответов= ',len(errors.errors)
        errors.add_data( question_id, wrong_text, right_text )
        # print 'неправильных ответов после добавления = ',len(errors.errors)
        stars.add_data(question, data = 'red')
    else:
        if question_id in errors.errors.keys():
            # print 'было неправильных ответов= ',len(errors.errors)
            errors.remove_question_data( question_id )
            # print 'неправильных ответов после удаления = ',len(errors.errors)
        stars.add_data(question, data = 'green')

    nav_tab = request.session['nav_tab']
    if nav_tab == 'ticket':
        question_id_list = question.get_question_id_list_in_ticket()
    elif nav_tab == 'theme':
        question_id_list = question.get_question_id_list_in_theme()
    elif nav_tab == 'marathon':
        question_id_list = request.session['marathon_list']
    elif nav_tab == 'errors':
        errors_list = request.session['marathon_list']
        try:
            # print 'errors_list=',errors_list
            next_question_id = errors_list.pop()
            request.session['errors_list'] = errors_list
        except IndexError:
            stars.clear()
            return redirect( '/tickets/errors_report')
        return redirect('tickets:question_detail', str(next_question_id))

    else:
        pass
    try:
        print '22222222222  pk =', pk
        print 'question_id_list=',question_id_list
        next_question_id = question_id_list[ question_id_list.index( int(pk) ) + 1 ]
        print 'next_question_id=', next_question_id

    except IndexError:
        # пройдены все вопросы в билете -> записываем число правильных/неправильных вопросов
        # для отчета по билету
        right, wrong = ( 0, 0 )
        for item in stars.stars:
            if item == 'green':
                right += 1
            else:
                wrong += 1

        if nav_tab == 'ticket':
            ticket_id = str(question.ticket.id)
            val = 'ticket_' + ticket_id
            report.add_data(val, right, wrong)
            stars.clear()
            return redirect( '/tickets/ticket_report?ticket_id=' + ticket_id )
        elif nav_tab == 'theme':
            theme_id = str(question.theme.id)
            val = 'theme_' + theme_id
            report.add_data(val, right, wrong)
            stars.clear()
            return redirect( '/tickets/theme_report?theme_id=' + theme_id )
        elif nav_tab == 'marathon':
            val = 'marathon'
            report.add_data(val, right, wrong)
            stars.clear()
            print 'nav_tab = ', 
            print 'stars.stars = ', stars.stars
            print 'report.report = ', report.report
            return redirect( '/tickets/marathon_report' )
        else:
            return redirect( 'tickets:ticket_list' )

    print '333333333333333'        
    next_question_obj = Question.objects.get( pk = next_question_id )
    print '4444444444444'    
    return redirect(next_question_obj)
    


def pdddataClear(request):
    stars, report, errors, timer = (
        Stars(request),
        Report(request),
        ErrorsPdd(request),
        Timer(request),
    )
    stars.clear()
    report.clear()
    errors.clear()
    timer.clear()
    return redirect('tickets:ticket_list')


class TicketReportView(TemplateView):
    template_name = 'tickets/ticket_report.html'
    

    def get_context_data(self, **kwargs):
        context = super(TicketReportView, self).get_context_data(**kwargs)
        stars, report, errors = (
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
        # print 'question_id_with_error = ',question_id_with_error
        # print 'question_in_current_ticket = ',question_in_current_ticket
        current_question_wrong_answers = question_id_with_error & question_in_current_ticket
        # print 'current_question_wrong_answers = ',current_question_wrong_answers
        data = []
        for item in current_question_wrong_answers:
            question = Question.objects.get( pk = item )
            errors.errors[ item ][ 'question_id' ] = question.id
            errors.errors[ item ][ 'question_text' ] = question.question
            if question.image:
                errors.errors[ item ][ 'question_img' ] = question.image.url
            data.append( errors.errors[ item ] )
        
        context['data'] = data
        context['nav_tab'] = self.request.session['nav_tab']
        return context

class ThemeReportView(TemplateView):
    template_name = 'tickets/theme_report.html'
    

    def get_context_data(self, **kwargs):
        context = super(ThemeReportView, self).get_context_data(**kwargs)
        stars, report, errors = (
            Stars(self.request),
            Report(self.request),
            ErrorsPdd(self.request),
        )
        theme_id = self.request.GET['theme_id']
        theme = get_object_or_404(Theme, id = theme_id)
        
        try:
            one_theme_report_data = report.report[ 'theme_' + theme_id ]
        except KeyError:
            raise Http404('Тема еще не пройдена!')
        context['theme_name'] = theme.name
        context['right_ans'] = one_theme_report_data[ 'right' ]
        context['wrong_ans'] = one_theme_report_data[ 'wrong' ]
        
        # данные для сводки правильный/неправильный ответ
        question_id_with_error = set( errors.errors.keys() )
        question_in_current_theme = set( theme.get_question_id_list_in_theme())
        # print 'question_id_with_error = ',question_id_with_error
        # print 'question_in_current_theme = ',question_in_current_theme
        current_question_wrong_answers = question_id_with_error & question_in_current_theme
        # print 'current_question_wrong_answers = ',current_question_wrong_answers
        data = []
        for item in current_question_wrong_answers:
            question = Question.objects.get( pk = item )
            errors.errors[ item ][ 'question_id' ] = question.id
            errors.errors[ item ][ 'question_text' ] = question.question
            if question.image:
                errors.errors[ item ][ 'question_img' ] = question.image.url
            data.append( errors.errors[ item ] )       
        context['data'] = data
        context['nav_tab'] = self.request.session['nav_tab']
        return context


class Errors(PddContextMixin, TemplateView):
    template_name = 'tickets/errors.html'


    def get_context_data(self, **kwargs):
        context = super(Errors, self).get_context_data(**kwargs)
        errors = ErrorsPdd(self.request)
        errors_keys = errors.errors.keys()
        errors_number = len(errors_keys)
        context['errors'] = errors_number
        try: 
            context['pk'] = errors_keys.pop()
            print 'context[ "pk" ] = ', context['pk']
        except IndexError:
            context['pk'] = None
        self.request.session['nav_tab'] = 'errors'
        self.request.session['errors_list'] = errors_keys
        self.request.session['grey_stars'] = errors_number
        return context


class ErrorsReportView(TemplateView):
    template_name = 'tickets/errors_report.html'


    def get_context_data(self, **kwargs):
        context = super(ErrorsReportView, self).get_context_data(**kwargs)
        errors = ErrorsPdd(self.request)
        errors_keys = errors.errors.keys()
        context['wrong_ans'] = len(errors_keys)
        context['nav_tab'] = self.request.session['nav_tab']
        return context


class MarathonTemplateView(PddContextMixin, TemplateView):
    template_name = 'tickets/marathon.html'


    def get_context_data(self, **kwargs):
        context = super(MarathonTemplateView, self).get_context_data(**kwargs)
        m = Question.objects.values_list('id', flat=True).order_by('?')
        marathon_list = []
        for item in m:
            marathon_list.append(item)
        print 'marathon_list=', marathon_list        
        self.request.session['nav_tab'] = 'marathon'
        self.request.session['marathon_list'] = marathon_list
        self.request.session['grey_stars'] = len(marathon_list)
        timer = Timer(self.request)
        timer.clear()
        # context[ 'first_question_id' ] = marathon_list[ 0 ]
        return context


class MarathonReportView(TemplateView):
    template_name = 'tickets/marathon_report.html'


    def get_context_data(self, **kwargs):
        context = super(MarathonReportView, self).get_context_data(**kwargs)
        stars, report = (
            Stars(self.request),
            Report(self.request),
        )        
        try:
            marathon_report_data = report.report[ 'marathon' ]
        except KeyError:
            stars.clear()
            raise Http404('Но вы еще не прошли марафон!')
        context['right_ans'] = marathon_report_data[ 'right' ]
        context['wrong_ans'] = marathon_report_data[ 'wrong' ]
        timer = Timer(self.request)
        context['time_for_test'] = timer.get_timer_report()
        return context


class ExamTemplateView(PddContextMixin, TemplateView):
    template_name = 'tickets/exam.html'

def start_Timer(request):
    timer = Timer(request)
    return redirect('tickets:question_detail',  
        request.session['marathon_list'][ 0 ])


def toggle_Timer(request):
    if not request.is_ajax() or not request.method=='POST':
        
        return HttpResponseNotAllowed(['POST'])
    else:
        timer = Timer(request)
        timer_state = timer.timer.get( 'suspend', None )
        if timer_state:
            timer.run() 
        else:
            timer.suspend()
        return HttpResponse('Toggle ok!')


# coding=utf-8

import re

from django.http import Http404, HttpResponse, HttpResponseNotAllowed
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import (
    DetailView, ListView, TemplateView,
    )
from django.views.decorators.http import require_POST

from .models import (
    Ticket,
    Question,
    Theme,
    Choice,
    )
from pass_data import Stars, Report, ErrorsPdd, Timer
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
            tick_item[ 'tick_number' ] = ticket.tick_number
            tick_item[ 'first_question_num' ] = ticket.get_first_question_num()
            tick_item[ 'is_whole_ticket' ] = ticket.is_whole_ticket

            ticket_with_result.append(tick_item)
        context['tickets'] = ticket_with_result
        self.request.session['nav_tab'] = 'ticket'
        stars = Stars(self.request)
        stars.clear()       
        return context


class ThemeListView(PddContextMixin, TemplateView):
    template_name = 'tickets/theme_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super(ThemeListView, self).get_context_data(*args, **kwargs)
        report = Report(self.request).report
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
        stars = Stars(self.request)
        stars.clear()
        return context


class QuestionDetailView(DetailView):
    model = Question
    template_name = 'tickets/question_detail.html'  
    context_object_name = 'question'

    def get_context_data(self, *args, **kwargs):
        context = super(QuestionDetailView, self).get_context_data(*args, **kwargs)
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
     
    def count_red_in_exam_errors( stars_list ):
        res = 0
        for i in stars_list:
            if i == 'red':
                res += 1
        return res


    def get_additional_questions( question, question_id_list ):
        theme_id = question.theme.id
        q = Question.objects.values_list( 'theme', 'id', )
        all_question_with_current_theme = []
        for item in q:
            if item[ 0 ] == theme_id:
                all_question_with_current_theme.append( item[ 1 ] )

        set_get_additional_questions = set( all_question_with_current_theme ) - set( question_id_list )
        if len( set_get_additional_questions ) < 5:
            all_question_id_list = Question.objects.values_list( 'id', flat = True)

            unused_questions = set(all_question_id_list) - set_get_additional_questions - set( question_id_list )
            unused_questions_list = list( unused_questions )[ : 5 ]
            additional_questions_list = list( set_get_additional_questions )
            additional_questions_list.extend( unused_questions_list )
            return additional_questions_list[ : 5 ] 
        else:
            return list(set_get_additional_questions)[ : 5 ]

    
    nav_tab = request.session['nav_tab']
    if nav_tab == 'exam':
        question_id_list = request.session['exam_question_list']
        stars, report, timer = (
                Stars(request),
                Report(request),
                Timer(request),
            )
        question = get_object_or_404( Question, pk = pk )
        user_choice = int(request.POST['choice'])
        right_choice = question.get_right_choice
        pk_index = question_id_list.index( int(pk) )
    # если ответ не правильный 
        if not user_choice == right_choice:
            stars.add_data(question, data = 'red')
            # подсчитываем ошибки:
            red_stars = count_red_in_exam_errors( stars.stars )
            
            # экзамен сдан           
            if pk_index == 24  and red_stars == 1:
                report.add_data( 'exam',  24, 1 )               
                timer.stop()
                request.session['exam_result'] = 'Экзамен сдан!'
                return redirect( '/tickets/exam_report' )
            elif pk_index == 29  and red_stars == 2:
                report.add_data( 'exam',  28, 2 )
                timer.stop()
                request.session['exam_result'] = 'Экзамен сдан!'
                return redirect( '/tickets/exam_report' )
            # экзамен не сдан  
            elif pk_index < 20  and red_stars == 3:
                report.add_data( 'exam',  len( stars.stars ) - 3, 3 )
                timer.stop()
                request.session['exam_result'] = 'Экзамен не сдан.'
                return redirect( '/tickets/exam_report' )
            elif pk_index >= 20  and red_stars == 2:
                report.add_data( 'exam',  len( stars.stars ) - 3, 3 )
                timer.stop()
                request.session['exam_result'] = 'Экзамен не сдан.'
                return redirect( '/tickets/exam_report' )
            # добавление 5ти вопросов и продолжение экзамена
            elif(len(question_id_list) == 20 and red_stars == 1) or (len(question_id_list) == 25 and red_stars == 2):

                additional_question_list = get_additional_questions( question, question_id_list )
                question_id_list.extend(additional_question_list)
                request.session['exam_question_list'] = question_id_list
                request.session['grey_stars'] += 5
                next_question_id = question_id_list[ pk_index + 1 ]
                return redirect( 'tickets:question_detail', str(next_question_id) )    
            else:
                pass
        # если ответ правильный 
        else:
            stars.add_data(question, data = 'green')
            red_stars = count_red_in_exam_errors( stars.stars )
            # ответ правильный, экзамен сдан:
            if pk_index == 19  and red_stars == 0:
                report.add_data( 'exam',  20, 0 )
                timer.stop()
                request.session['exam_result'] = 'Экзамен сдан!'
                return redirect( '/tickets/exam_report' )
            elif pk_index == 24  and red_stars == 1:
                report.add_data( 'exam',  24, 1 )
                timer.stop()
                request.session['exam_result'] = 'Экзамен сдан!'
                return redirect( '/tickets/exam_report' )
            elif pk_index == 29  and red_stars == 2:
                report.add_data( 'exam',  29, 2 )
                timer.stop()
                request.session['exam_result'] = 'Экзамен сдан!'
                return redirect( '/tickets/exam_report' )
            # ответ правильный, экзамен продолжается:
            else:
                next_question_id = question_id_list[ pk_index + 1 ]
                return redirect('tickets:question_detail', str(next_question_id))

    if nav_tab == 'ticket' or nav_tab == 'theme' or nav_tab == 'marathon' or nav_tab == 'errors' :
        stars, report, errors , timer = (
            Stars(request),
            Report(request),
            ErrorsPdd(request),
            Timer(request),
        )

        question = get_object_or_404( Question, pk = pk )
        user_choice = int(request.POST['choice'])
        right_choice = question.get_right_choice
        question_id = unicode( question.id )

        if not user_choice == right_choice:
            wrong_text = get_object_or_404( Choice, pk = user_choice ).choice_text
            right_text = get_object_or_404( Choice, pk = right_choice ).choice_text
            errors.add_data( question_id, wrong_text, right_text )
            stars.add_data(question, data = 'red')
        else:
            if question_id in errors.errors.keys():
                errors.remove_question_data( question_id )
            stars.add_data(question, data = 'green')

    
    if nav_tab == 'ticket':
        question_id_list = question.get_question_id_list_in_ticket()
    elif nav_tab == 'theme':
        question_id_list = question.get_question_id_list_in_theme()
    elif nav_tab == 'marathon':
        question_id_list = request.session['marathon_list']
    
    elif nav_tab == 'errors':
        errors_list = request.session['errors_list']
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
        next_question_id = question_id_list[ question_id_list.index( int(pk) ) + 1 ]
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
            timer.stop()
            return redirect( '/tickets/marathon_report' )
        else:
            return redirect( 'tickets:ticket_list' )       
    next_question_obj = Question.objects.get( pk = next_question_id )
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
        stars.clear()
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
        current_question_wrong_answers = question_id_with_error & question_in_current_theme

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
        stars.clear()
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
        stars = Stars(self.request)
        stars.clear()
        return context


class ErrorsReportView(TemplateView):
    template_name = 'tickets/errors_report.html'


    def get_context_data(self, **kwargs):
        context = super(ErrorsReportView, self).get_context_data(**kwargs)
        errors = ErrorsPdd(self.request)
        errors_keys = errors.errors.keys()
        context['wrong_ans'] = len(errors_keys)
        context['nav_tab'] = self.request.session['nav_tab']
        stars = Stars(self.request)
        stars.clear()
        return context


class MarathonTemplateView(PddContextMixin, TemplateView):
    template_name = 'tickets/marathon.html'


    def get_context_data(self, **kwargs):
        context = super(MarathonTemplateView, self).get_context_data(**kwargs)
        m = Question.objects.values_list('id', flat=True).order_by('?')
        marathon_list = []
        for item in m:
            marathon_list.append(item)       
        self.request.session['nav_tab'] = 'marathon'
        self.request.session['marathon_list'] = marathon_list
        self.request.session['grey_stars'] = len(marathon_list)
        timer = Timer(self.request)
        timer.clear()
        stars = Stars(self.request)
        stars.clear()
        return context


class MarathonReportView(PddContextMixin, TemplateView):
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
        context['timer'] = timer.timer
        context['nav_tab'] = self.request.session['nav_tab']

        stars.clear()
        return context


class ExamReportView(PddContextMixin, TemplateView):
    template_name = 'tickets/exam_report.html'


    def get_context_data(self, **kwargs):
        context = super(ExamReportView, self).get_context_data(**kwargs)    
        stars = Stars(self.request)
        stars.clear()
        timer = Timer(self.request)
        report = Report(self.request)

        context['time_for_test'] = timer.get_timer_report()
        context[ 'nav_tab' ] = self.request.session['nav_tab']
        context['exam_result'] = self.request.session['exam_result']
        context[ 'wrong_ans' ] = report.report[ 'exam' ][ 'wrong' ]
        context[ 'right_ans' ] = report.report[ 'exam' ][ 'right' ]
        return context


class ExamTemplateView(PddContextMixin, TemplateView):
    template_name = 'tickets/exam.html'


    def get_context_data(self, **kwargs):
        context = super(ExamTemplateView, self).get_context_data(**kwargs)    
        # t = Ticket.objects.filter( is_whole_ticket = True ).values_list( 'id', flat = True ).order_by( '?' ).first()
        # exam_question_id_list = Question.objects.filter( ticket = t ).values_list( 'id', flat = True ).order_by( '?' )
        
        q = Question.objects.all().order_by( '?' )[:20]
        try:
            q[19]
        except IndexError:
            raise Http404('В базе не достаточно билетов для проведения экзамена')
        exam_question_id_list = q.values_list( 'id', flat = True )

        exam_question_list = []
        for item in exam_question_id_list:
            exam_question_list.append(item)
        self.request.session['nav_tab'] = 'exam'
        self.request.session['exam_question_list'] = exam_question_list
        self.request.session['grey_stars'] = 20

        timer = Timer(self.request)
        timer.clear()
        stars = Stars(self.request)
        stars.clear()
        return context


def start_Timer(request):
    timer = Timer(request)
    nav_tab = request.session.get( 'nav_tab', 'marathon' )
    if nav_tab == 'exam':
        return redirect('tickets:question_detail', request.session['exam_question_list'][ 0 ])
    else:
        return redirect('tickets:question_detail', request.session['marathon_list'][ 0 ])


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


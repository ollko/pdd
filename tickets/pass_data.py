# coding=utf-8

from django.conf import settings
from .models import Ticket, Question


class ErrorsPdd(object):
    def __init__(self, request):
        self.session = request.session
        errors = self.session.get(settings.PDD_ERRORS_SESSION_ID)
        if not errors:
            # Сохраняем объект данных пользователя в сессию
            errors = self.session[settings.PDD_ERRORS_SESSION_ID] = {}
        self.errors = errors


    def add_data( self, question_id, wrong_text, right_text ):
        self.errors[ question_id ] = {}
        self.errors[ question_id ][ 'right_text' ] = right_text
        self.errors[ question_id ][ 'wrong_text' ] = wrong_text
        self.save()


    def __iter__(self):
        question_ids = self.errors.keys()
        questions = Question.objects.filter(id__in = question_ids)
        for question in questions:
            self.errors[str(question.id)]['question'] = question

        for item in self.errors.values():
            yield item


    def remove_question_data( self, question_id ):
        self.errors.pop( question_id )
        self.save()



    # Сохранение данных в сессию
    def save(self):
        self.session[settings.PDD_ERRORS_SESSION_ID] = self.errors
        # Указываем, что сессия изменена
        self.session.modified = True


    def clear(self):
        del self.session[settings.PDD_ERRORS_SESSION_ID]
        self.session.modified = True


class Report(object):
    def __init__(self, request):
        self.session = request.session
        report = self.session.get(settings.REPORT_SESSION_ID)
        if not report:
            # Сохраняем объект данных пользователя в сессию
            report = self.session[settings.REPORT_SESSION_ID] = {}
        self.report = report


    def add_data(self, val, right, wrong):
        self.report[ val ] = {}
        self.report[ val ][ 'right' ] = right
        self.report[ val ][ 'wrong' ] = wrong
        self.save()

    # Сохранение данных в сессию
    def save(self):
        self.session[settings.REPORT_SESSION_ID] = self.report
        # Указываем, что сессия изменена
        self.session.modified = True


    def clear(self):
        del self.session[settings.REPORT_SESSION_ID]
        self.session.modified = True


class Stars(object):
    def __init__(self, request):
        self.session = request.session
        stars = self.session.get(settings.STAR_SESSION_ID)
        if not stars:
            # Сохраняем объект данных пользователя в сессию
            stars = self.session[settings.STAR_SESSION_ID] = []
        self.stars = stars


    def __iter__(self):
        for k in self.pdddata.keys():
            yield { k : self.pdddata[ k ] }


    def add_data(self, question, data):
        self.stars.append( data )
        # print 'self.stars=',self.stars
        self.save()

    # Сохранение данных в сессию
    def save(self):
        self.session[settings.STAR_SESSION_ID] = self.stars
        # Указываем, что сессия изменена
        self.session.modified = True


    def clear(self):
        del self.session[settings.STAR_SESSION_ID]
        self.session.modified = True


class Pdddata(object):


    def __init__(self, request):
    # Инициализация объекта данных пользователя
        self.session = request.session
        pdddata = self.session.get(settings.PDD_SESSION_ID)

        if not pdddata:
            # Сохраняем объект данных пользователя в сессию
            pdddata = self.session[settings.PDD_SESSION_ID] = {}
        self.pdddata = pdddata


    def __iter__(self):
        for k in self.pdddata.keys():
            yield { k : self.pdddata[ k ] }
    # Pdddata = {
    #     'ticket_id':{
    #         'question_id':['user_choice_id',
    #         ...
    #     }

    def add_data(self, question, user_choice_id):
        right_choice_id, ticket_id = (
            question.get_right_choice,
            str(question.ticket.id)
        )
           
        if not ticket_id in self.pdddata.keys():

            self.pdddata[ ticket_id ] = []
        question_data = {}
        question_data['question'] = question.id
        question_data['user_wrong_choice_id'] = user_choice_id
        self.pdddata[ticket_id].append(question_data)
        self.save()


    def __iter__(self):

        for k in self.pdddata.keys():
            yield { k : self.pdddata[ k ] }


    def remove_ticket(self, question):
        ticket_id = str(question.ticket.id)
        if ticket_id in self.pdddata:            
            del self.pdddata[ticket_id]
            self.save()

    # Сохранение данных в сессию
    def save(self):
        self.session[settings.PDD_SESSION_ID] = self.pdddata
        # Указываем, что сессия изменена
        self.session.modified = True


    def clear(self):
        # print 'self.session=', self.session
        del self.session[settings.PDD_SESSION_ID]
        self.session.modified = True


class Themedata(object):


    def __init__(self, request):
    # Инициализация объекта данных пользователя
        self.session = request.session
        themedata = self.session.get(settings.THEME_SESSION_ID)

        if not themedata:
            # Сохраняем объект данных пользователя в сессию
            themedata = self.session[settings.THEME_SESSION_ID] = {}
        self.themedata = themedata


    # Pdddata = {
    #     'ticket_id':{
    #         'question_id':['user_choice_id',
    #         ...
    #     }

    def add_data(self, question, user_choice_id):
        right_choice_id, ticket_id = (
            question.get_right_choice,
            str(question.ticket.id)
        )
           
        if not ticket_id in self.themedata.keys():

            self.themedata[ theme_id ] = []
        question_data = {}
        question_data['question'] = question.id
        question_data['user_wrong_choice_id'] = user_choice_id
        self.themedata[ticket_id].append(question_data)
        self.save()


    def remove_ticket(self, question):
        ticket_id = str(question.ticket.id)
        if ticket_id in self.themedata:            
            del self.themedata[ticket_id]
            self.save()

    # Сохранение данных в сессию
    def save(self):
        self.session[settings.THEME_SESSION_ID] = self.themedata
        # Указываем, что сессия изменена
        self.session.modified = True


    def clear(self):
        # print 'self.session=', self.session
        del self.session[settings.THEME_SESSION_ID]
        self.session.modified = True
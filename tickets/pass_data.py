# coding=utf-8

from django.conf import settings
from .models import Ticket, Question

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
        print 'self.session=', self.session
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
        print 'self.session=', self.session
        del self.session[settings.THEME_SESSION_ID]
        self.session.modified = True
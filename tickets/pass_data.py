# coding=utf-8

from django.conf import settings
from .models import Ticket, Question
from datetime import datetime, timedelta


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


class Timer(object):
    def __init__(self, request):
        self.session = request.session
        timer = self.session.get(settings.TIMER_ID)
        if not timer:
            # Сохраняем объект данных пользователя в сессию
            timer = self.session[settings.TIMER_ID] = { 
                # 'start' : self.seconds_since_midnight(),
                # 'suspend' : False,
                # 'sleep_time': 0,

                }
        self.timer = timer


    def seconds_since_midnight(self):
        now = datetime.now()
        return (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()



    def suspend(self):
        # print "suspend"
        self.timer['suspend_time'] = self.seconds_since_midnight()
        self.timer[ 'suspend' ] = True
        self.save()


    def run(self):
        # print "run"
        self.timer['sleep_time'] += ( self.seconds_since_midnight() - self.timer[ 'suspend_time' ] )
        del self.timer['suspend_time']
        self.timer[ 'suspend' ] = False
        self.save()


    def stop(self):
        # print "stop"
        self.timer['stop_time'] = self.seconds_since_midnight()
        self.save()


    def get_timer_report(self):
        sleep_time = self.timer.get('sleep_time', None)
        stop_time = self.timer.get('stop_time', None)
        result_in_seconds = (stop_time - ( self.timer[ 'start' ] + sleep_time ))
        res = timedelta(seconds=result_in_seconds)
        days = res.days
        seconds = res.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        sec = (seconds % 3600) % 60
        if result_in_seconds / ( 60. ) < 20:
            exam_status = False
        else:
            exam_status = True
        result = ( days, hours, minutes, sec, exam_status )
        return result


    # Сохранение данных в сессию
    def save(self):
        self.session[settings.TIMER_ID] = self.timer
        # Указываем, что сессия изменена
        self.session.modified = True


    def clear(self):
        del self.session[settings.TIMER_ID]
        self.session.modified = True

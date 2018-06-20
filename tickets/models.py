# coding=utf-8
from __future__ import unicode_literals

from django.db import models
from django.contrib.sessions.models import Session
from django.core.urlresolvers import reverse
from django.shortcuts import get_list_or_404


DRIVE_CATEGORY = (('A, B, M', 'A, B, M'), ('C и Д', 'C и Д'))


class Ticket(models.Model):
    tick_number = models.IntegerField()
    drive_category = models.CharField(max_length = 500, choices = DRIVE_CATEGORY,)

    
    def __unicode__(self):
        return 'Билет №'+str(self.tick_number)

    def get_absolute_url(self):
        return reverse('tickets:ticket_detail', args=[self.pk, ])

    def get_first_question_num(self):
        question = self.questions.first()
        if question:
            return str(question.id)
        return None

    # def get_right_wrong_answer_num(self):
    #     print '22222222222222'
    #     pdddata = Session.objects.all().first()
    #     try:
    #         user_ticket_ans = pdddata.get_decoded()['pdd'][str(self.id)]
    #     except KeyError:
    #         return None
    #     if len(user_ticket_ans.keys()) == 20:
    #         right_answer_num = 0
    #         for i in user_ticket_ans.keys():
    #             if int(user_ticket_ans[i]) == self.questions.all().get(id = int(i)).get_right_choice():
    #                 right_answer_num +=1

    #         wrong_answer_num = 20 - right_answer_num
    #         return (right_answer_num, wrong_answer_num)
    #     return None


class Theme(models.Model):
    name = models.CharField(max_length = 500,)

    
    def __unicode__(self):
        return self.name


    def get_absolute_url(self):
        return reverse('tickets:theme_list', args=[self.pk, ])



    def ticket_number(self):
        qs = Question.objects.filter(theme = self)
        return len(qs)


    def get_first_question_num(self):
        question = self.questions.first()

        if question:
            return str(question.id)
        return None


class Question(models.Model):
    ticket = models.ForeignKey(Ticket,
        related_name='questions',
        on_delete = models.CASCADE,
        )
    theme = models.ForeignKey(Theme,
        related_name='questions',
        on_delete = models.CASCADE,
        )
    image = models.ImageField(upload_to='tickets_img/',
                                blank=True, null=True, default=None,)
    question = models.CharField(max_length = 1000,)


    def __unicode__(self):
        return 'Вопрос №%s (%s)' % (str(self.id), self.theme.name,)

    def get_absolute_url(self):
        return reverse('tickets:question_detail', args=[self.pk, ])


    @property
    def get_right_choice(self):
        choices = self.choice_set.all()
        for choice in choices:
            if choice.choice_status:
                return choice.id


    @property
    def get_right_choice_text(self):
        choices = self.choice_set.all()
        for choice in choices:
            if choice.choice_status:
                return choice.choice_text

    def get_question_id_list_in_ticket(self):
        question_list = get_list_or_404(Question, ticket = self.ticket)
        question_id_list = []
        for q in question_list:
            question_id_list.append(q.id)
        return question_id_list


    def next_question_in_ticket_id(self):
        question_id_list = self.get_question_id_list_in_ticket()
        try :
            next_id = question_id_list[question_id_list.index(self.id) + 1]
        except IndexError:
            return None
        return next_id


    def all_question_in_ticket(self):
        return self.ticket.questions.all()
        

class Choice(models.Model):
    question = models.ForeignKey(Question,
        related_name='choice_set',
        on_delete = models.CASCADE,
        )
    choice_text = models.CharField(max_length=1000)
    choice_status = models.BooleanField(default = False)


    def __unicode__(self):
        return self.choice_text


    def save(self, *args, **kwargs):
        instance = self
        if instance.choice_status == True:
            qs = Choice.objects.filter(question = self.question).filter(choice_status = True)
            if qs.exists():
                print 'qs=',qs
                qs.update(choice_status=False)
        super(Choice, self).save(*args, **kwargs)

# coding=utf-8
from __future__ import unicode_literals

from django.db import models


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


class Theme(models.Model):
    name = models.CharField(max_length = 500,)

    
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tickets:theme_list', args=[self.pk, ])


class Question(models.Model):
    ticket = models.ForeignKey(Ticket,
        related_name='questions',
        on_delete = models.CASCADE,
        )
    theme = models.ForeignKey(Theme,
        # related_name='questions',
        on_delete = models.CASCADE,
        )
    image = models.ImageField(upload_to='tickets_img/',
                                blank=True, null=True, default=None,)
    question = models.CharField(max_length = 1000,)


    def __unicode__(self):
        return 'Вопрос №%s (%s)' % (str(self.id), self.theme.name,)

    def get_absolute_url(self):
        return reverse('tickets:question_detail', args=[self.pk, ])


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
        print 'dir(self)=',dir(self)
        instance = self
        if instance.choice_status == True:
            qs = Choice.objects.filter(question = self.question).filter(choice_status = True)
            if qs.exists():
                print 'qs=',qs
                qs.update(choice_status=False)
        super(Choice, self).save(*args, **kwargs)

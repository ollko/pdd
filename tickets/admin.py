# coding=utf-8
from django.contrib import admin

# Register your models here.


from .models import Ticket, Theme, Question, Choice

admin.site.register(Ticket)
admin.site.register(Theme)

class ChoiceItemInline(admin.TabularInline):
    model = Choice
    raw_id_field = ['question',
                    'choice_text',
                    'choice_status',]
    

class QuestionAdmin(admin.ModelAdmin):
    list_display_links = ["question"]
    search_fields = [ "theme__name", 'ticket__tick_number']
    list_display = (
                    'question_number',
                    'ticket',                    
                    'question', 
                    'theme',
                    )

    fields =   ('question_number',
                'question', 
                'ticket',
                'theme',
                )

    inlines = [ChoiceItemInline]

admin.site.register(Question, QuestionAdmin)

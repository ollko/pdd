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
    list_display = (
                    'id',
                    'question', 
                    'ticket',
                    'theme',
                    )

    fields =   ('ticket',
                'theme',
                'image',
                'question',
                )

    inlines = [ChoiceItemInline]

admin.site.register(Question, QuestionAdmin)

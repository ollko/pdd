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


    # def get_max_num(self, request, obj=None, **kwargs):
    #     max_num = 10
    #     if obj.question:
    #         return max_num - 5
    #     return max_num


class QuestionAdmin(admin.ModelAdmin):
    list_display = (
                    'question', 
                    'ticket',
                    'theme',
                    )

    fields =   ('ticket',
                'theme',
                'question',
                )

    inlines = [ChoiceItemInline]

admin.site.register(Question, QuestionAdmin)

admin.site.register(Choice)

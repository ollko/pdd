from django.conf import settings


class Pdddata(object):
    def __init__(self, request):
    # Инициализация корзины пользователя
        self.session = request.session
        pdddata = self.session.get(settings.PDD_SESSION_ID)

        if not pdddata:
            # Сохраняем корзину пользователя в сессию
            pdddata = self.session[settings.PDD_SESSION_ID] = {}
        self.pdddata = pdddata


    def add_ticket(self):
        pass

    def add_question(self):
        pass
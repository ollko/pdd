# coding=utf-8
from django.views.generic.base import ContextMixin


class PddContextMixin(ContextMixin):
	def get_context_data(self, **kwargs):
		context = super(PddContextMixin, self).get_context_data(**kwargs)
		context['current_url']  = self.request.path
		return context
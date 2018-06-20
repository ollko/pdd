from .pass_data import Pdddata


def pdddata(request):
	p = Pdddata(request)
	return {'pdddata': Pdddata(request)}
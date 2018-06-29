from .pass_data import Timer


def timer(request):
	return {'timer': Timer(request)}
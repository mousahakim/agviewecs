from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import requests
from visualizer.models import *

@login_required()
def show_test(request):
	user_data = Ui_MicroChart.objects.filter(user=request.user)

	if request.user.is_authenticated():
		return 	HttpResponse(user_data)
	else:
		return HttpResponse("Nope!")

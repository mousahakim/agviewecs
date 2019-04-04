from visualizer.models import Widgets, Dashboard
from django.contrib.auth.models import User

def adddash(user=None):

	if user is None:
		user = User.objects.all()

	for u in user:
		try:
			dash = Dashboard(user=u, name='Dash 1', active=True)
			dash.save()
		except:
			print e
			print 'error creating Dashboard'
			return

		widgets = Widgets.objects.filter(user=u)

		if widgets.exists():
			try:
				widgets.update(dashboard=dash)
			except:
				print e
				print 'error updating widget.'
			print '1 done.'



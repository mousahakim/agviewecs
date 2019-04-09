import boto3, redis, time
from datetime import datetime
from django.core.management.base import BaseCommand
from visualizer.tasks import async_download, async_update


class Command(BaseCommand):

	NET_CONFIG = {
			'awsvpcConfiguration': {
				'subnets': ['subnet-02a76289d842e47bd'],
				'securityGroups': ['sg-0200f12355b6dca2d'],
				'assignPublicIp':'ENABLED'
			}
		}


	CLUSTER = u'arn:aws:ecs:us-west-2:808765879723:cluster/agview1west'

	SERVICE_NAME = 'agview1_service'

	client = boto3.client('ecs')


	def get_redis_queue_lenght(self, host='localhost', port=6379, db=0, queue='celery'):

		client = redis.Redis(host=host, port=port, db=db)

		q_length = client.llen(queue)

		return q_length


	def run_tasks(self, count=10):

		self.stdout.write('updating desired count to {} tasks'.format(count))
		begin = time.time()

		#update desired count
		service_update_response = self.client.update_service(cluster=self.CLUSTER, desiredCount=count,\
			networkConfiguration=self.NET_CONFIG, service=self.SERVICE_NAME)

		#get list of tasks in running state
		list_running_tasks_response = self.client.list_tasks(cluster=self.CLUSTER,\
		 serviceName=self.SERVICE_NAME, desiredStatus='RUNNING')

		#wait until number of running tasks is at least 90% of count
		while len(list_running_tasks_response['taskArns']) <= (count - count*0.1):

			time.sleep(5)
			list_running_tasks_response = self.client.list_tasks(cluster=self.CLUSTER,\
				 serviceName=self.SERVICE_NAME, desiredStatus='RUNNING')

		running_count = len(list_running_tasks_response['taskArns'])

		end = time.time()
		self.stdout.write(self.style.SUCCESS('{} tasks started in {} seconds'.format(running_count,\
			round(end - begin, 3))))

		return True


	def stop_tasks(self):

		while self.get_redis_queue_lenght() > 0:

			self.stdout.write('Queue Lenght is {}'.format(self.get_redis_queue_lenght()))
			time.sleep(5)

		#update desired count to 0
		service_update_response = self.client.update_service(cluster=self.CLUSTER, desiredCount=0,\
			networkConfiguration=self.NET_CONFIG, service=self.SERVICE_NAME)
		
		#get list of running tasks
		list_running_tasks_response = self.client.list_tasks(cluster=self.CLUSTER,\
		 serviceName=self.SERVICE_NAME, desiredStatus='RUNNING')

		self.stdout.write('{} tasks running'.format(len(list_running_tasks_response['taskArns'])))

		if list_running_tasks_response['taskArns']:

			waiter = self.client.get_waiter('tasks_stopped')

			#wait on on running tasks to stop
			self.stdout.write('waiting for tasks to stop')
			waiter.wait(cluster=self.CLUSTER, tasks=list_running_tasks_response['taskArns'])


		self.stdout.write(self.style.SUCCESS('{} tasks successfully stoped.'.format(len(list_running_tasks_response['taskArns']))))

		return True


	def handle(self, *args, **options):


		self.stdout.write('{} Update started'.format(datetime.now().isoformat(' ')))

		#start tasks
		self.run_tasks(50)

		#download new data
		async_download()

		# wait for download to finish
		while self.get_redis_queue_lenght() > 0:

			self.stdout.write('{} tasks remain in queue.'.format(self.get_redis_queue_lenght()))
			time.sleep(5)


		#update all widgets
		async_update()


		#stop tasks
		self.stop_tasks()

		self.stdout.write(self.style.SUCCESS('{} Update completed'.format(datetime.now().isoformat(' '))))


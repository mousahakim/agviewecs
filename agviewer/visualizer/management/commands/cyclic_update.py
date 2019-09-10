import boto3, redis, time
from datetime import datetime
from django.core.management.base import BaseCommand
from visualizer.tasks import async_download, async_update
from celery import Celery


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

	CELERY_APP = Celery('morph2o', broker='redis://localhost:6379/0', task_ignore_result=True)

	client = boto3.client('ecs')


	def get_active_celery_worker_count(self):

		workers = self.CELERY_APP.control.inspect().active()

		if not workers:
			return 0

		count = 0

		for k, v in workers.items():

			count += len(v)

		return count


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

	def stop_idle_tasks(self):

		workers = self.CELERY_APP.control.inspect().active()

		#return if there's no connected celery worker
		if not workers:
			print 'no active workers'
			return

		idle_worker_ips = []

		for k, v in workers.items():

			if len(v) == 0:
				try:

					dns_address = k.split('@')[1]
					ip_srt = dns_address.split('.')[0]
					ip_lst = ip_srt.split('-')
					ip_lst.pop(0)
					ip_address = '.'.join(ip_lst)
					idle_worker_ips.append(ip_address)
				except Exception as e:
					print e
					continue

		#return if there's no idle worker
		if not idle_worker_ips:
			print 'no active worker ips'
			return

		all_running_tasks = self.client.list_tasks(cluster=self.CLUSTER,\
		 serviceName=self.SERVICE_NAME, desiredStatus='RUNNING')


		if all_running_tasks:

			task_descriptions = self.client.describe_tasks(cluster=self.CLUSTER, tasks=all_running_tasks['taskArns'])

		else:
			print ' no running tasks'
			return

		idle_task_arns = []

		try:

			for task in task_descriptions['tasks']:

				try:
					if task['containers'][0]['networkInterfaces'][0]['privateIpv4Address'] in idle_worker_ips:

						idle_task_arns.append(task['taskArn'])

				except Exception as e:
					print 'failed to get task description', e
					continue

		except Exception as e:
			print 'could not retrieve task description', e

		

		for arn in idle_task_arns:
			try:

				self.client.stop_task(cluster=self.CLUSTER, task=arn, reason='task is idle')

			except Exception as e:
				print 'error stopping tasks', e


		self.stdout.write('{} idle tasks stopped'.format(len(idle_task_arns)))


	def stop_tasks(self):

		#wait for queue size to become 0
		while self.get_redis_queue_lenght() > 0:

			self.stdout.write('Queue Lenght is {}'.format(self.get_redis_queue_lenght()))
			time.sleep(5)

		#waiting for active tasks to finish
		self.stdout.write('Waiting for active tasks to finish')
		while self.get_active_celery_worker_count() > 0:
			#stop idle tasks
			# self.stop_idle_tasks()

			self.stdout.write('{} tasks are active'.format(self.get_active_celery_worker_count()))
			time.sleep(5)

		#update desired count to 0
		self.stdout.write('All tasks finished. Setting desired count to 0')
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

		t1 = time.time()

		self.stdout.write('{} Update started'.format(datetime.now().isoformat(' ')))

		#start tasks
		self.run_tasks(50)

		#download new data
		async_download()

		# wait for download to finish
		while self.get_redis_queue_lenght() > 0:

			self.stdout.write('{} tasks remain in queue.'.format(self.get_redis_queue_lenght()))
			time.sleep(5)

		#wait for active download tasks to finish
		while self.get_active_celery_worker_count() > 0:
			#stop idle tasks
			# self.stop_idle_tasks()

			self.stdout.write('{} tasks are active'.format(self.get_active_celery_worker_count()))
			time.sleep(5)

		t2 = time.time()
		self.stdout.write(self.style.SUCCESS('Download completed in {} minutes.'.format((t2-t1)/60)))
		#update all widgets
		async_update()


		#stop tasks
		self.stop_tasks()

		t2 = time.time()
		self.stdout.write(self.style.SUCCESS('Update completed in {} minutes.'.format((t2-t1)/60)))
		self.stdout.write(self.style.SUCCESS('Time: {}'.format(datetime.now().isoformat(' '))))


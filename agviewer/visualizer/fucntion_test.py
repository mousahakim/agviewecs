from __future__ import division

import json
def get_paw():

	st_data = {'1':{'12':1.5,'13':2, '14':4},'2':{'12':3,'13':4, '14':5},'3':{'12':5,'13':6, '14':7}}
	return_set = {}
	avg_values = {}
	paw_set = {}
	fc=3
	wp=7
	length = len(st_data)
	if len(st_data) > 1:
		for key, value in st_data.iteritems():
			for k, v in value.iteritems():
				if k in return_set:
					return_set[k] += float(v)
				else:
					return_set.update({k:float(v)})
		for k, v in return_set.iteritems():
			avg_values.update({k:(float(v)/float(len(st_data)))})
		for k, v in avg_values.iteritems():
			paw_set.update({k:(100+100*((float(v)-float(fc))/(fc-wp)))})
		return paw_set


	elif len(st_data) ==1:
		for k, v in st_data.iteritems():
			for key, value in st_data[k].iteritems():
				paw_set.update({key:(100+100*(float(value)-fc)/(fc-wp))})
		return paw_set

	else:
		return None 


print json.dumps(get_paw(), sort_keys=True)
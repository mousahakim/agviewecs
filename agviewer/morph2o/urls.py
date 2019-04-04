"""morph2o URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from visualizer import views, test_view, get_records, gis_views
from visualizer.views import ANAuthenticationForm
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
urlpatterns = [
   url(r'^$', views.index, name='index'),
   url(r'^cms', include('cms.urls')),
   url(r'^admin/', include(admin.site.urls)),
   url(r'^visualizer/', views.index, name='index1'),
   url(r'^accounts/login/$', auth_views.login, {'authentication_form': ANAuthenticationForm, 'extra_context':{'next': '/'}}, name='login'),
   url(r'^log_out/',auth_views.logout, {'next_page': 'index'}, name="log_out" ),
   url(r'^test/', get_records.get_widget, name="get_widget"),
   url(r'^gis/', views.gis_view, name="gis_view"),
   url(r'^load_widgets/', views.get_widgets, name="get_widgets"),
   url(r'^load_settings/', views.get_settings, name="get_settings"),
   url(r'^settings/', views.settings_index, name="settings"),
   url(r'^add_station/', views.add_station, name="add_station"),
   url(r'^list_files', views.load_files, name='load_files'),
   url(r'^file_upload', views.file_upload, name='file_upload'),
   url(r'^delete_files', views.delete_files, name='delete_files'),
   url(r'^download_file', views.download_file, name='download_file'), 
   url(r'^get_url', views.get_url, name='get_url'),
   url(r'^remove_widget', views.remove_widget, name='remove_widget'),
   url(r'^change_alias', views.change_alias, name='change_alias'),
   url(r'^widget_lst', views.widget_lst, name='widget_lst'),
   url(r'^widget', views.widget, name='widget'),
   url(r'^remove_station', views.remove_station, name='remove_station'),
   url(r'^change_setting', views.change_setting, name='change_setting'),
   url(r'^alert_action', views.alert_action, name='alert_action'), 
   url(r'^changedaterange', views.changedaterange, name='changedaterange'), 
   url(r'^adddashboard', views.adddashboard, name='adddashboard'),
   url(r'^removedashboard', views.removedashboard, name='removedashboard'),
   url(r'^editdashboard', views.editdashboard, name='editdashboard'), 
   url(r'^snooze_state_change', views.snooze_state_change, name='snooze_state_change'),
   url(r'^add_stat_widget', views.add_stat_widget, name='add_stat_widget'), 
   url(r'^delete_stat_widget', views.delete_stat_widget, name='delete_stat_widget'),
   url(r'^fetch_stat_widget', views.fetch_stat_widget, name='fetch_stat_widget'),
   url(r'^change_stat_widget', views.change_stat_widget, name='change_stat_widget'),
   url(r'^add_stat_data', views.add_stat_data, name='add_stat_data'),
   url(r'^change_stat_data', views.change_stat_data, name='change_stat_data'),
   url(r'^fetch_stat_data', views.fetch_stat_data, name='fetch_stat_data'),
   url(r'^delete_stat_data', views.delete_stat_data, name='delete_stat_data'),
   url(r'^upload', gis_views.upload, name='upload'),
   url(r'^remove', gis_views.remove, name='remove'),
   url(r'^file-list', gis_views.get_file_list, name='file-list'),
   url(r'^save-feature', gis_views.save_feature, name='save-feature'), 
   url(r'^save-map-widget', gis_views.create_map_widget, name='save-map-widget'), 
   url(r'^get-map-widgets', gis_views.get_map_widget_list, name='get-map-widgets'),
   url(r'^get-map-widget', gis_views.get_map_widget, name='get-map-widget'),
   url(r'^delete-map-widget', gis_views.delete_map_widget, name='delete-map-widget'), 
   url(r'^change-map-widget', gis_views.change_map_widget, name='change-map-widget'), 
   url(r'^get-feature-list', gis_views.get_feature_list, name='get-feature-list'), 
   url(r'^get-feature-stats', gis_views.get_feature_stats, name='get-feature-stats'), 
   url(r'^change-paw-feature-stat', gis_views.change_paw_feature_stat, name='change-paw-feature-stat'),
   url(r'^change-feature-stat', gis_views.change_feature_stat, name='change-feature-stat'),
   url(r'^get-feature-stat-widgets', gis_views.get_feature_stat_widgets, name='get-feature-stat-widgets'), 
   url(r'^get-chart-widget-list', gis_views.get_chart_widget_list, name='get-chart-widget-list'),
   url(r'^get-data-widget-list', gis_views.get_data_widget_list, name='get-data-widget-list'), 
   url(r'^resize-map', gis_views.resize_map, name='resize_map'),
   url(r'^resize-chart', views.resize_chart, name='resize_chart')

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# urlpatterns += i18n_patterns(
#     url(r'^cms/', include('cms.urls')),
#   )


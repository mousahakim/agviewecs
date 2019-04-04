from django import forms

class FileUploadForm(forms.Form):
	file = forms.FileField(label='Upload file:')


class FileDownloadForm(forms.Form):
	name = forms.CharField(max_length=200)
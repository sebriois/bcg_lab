from django.contrib.auth.models import Group, User, Permission
from django import forms

class GroupForm(forms.ModelForm):
	users = forms.ModelMultipleChoiceField(
		label		= u"Utilisateurs",
		queryset	= User.objects.filter(is_active = True).order_by("username"),
		required	= False
	)
	
	class Meta:
		model = Group
		fields = ('name',)
		
	def __init__(self, *args, **kwargs):
		super(GroupForm, self).__init__(*args, **kwargs)
		
		permission_list = Permission.objects.filter(codename__startswith = "custom").order_by('id')
		for p in permission_list:
			self.fields[p.codename] = forms.BooleanField(
				label = p.name,
				initial = self.instance.id and p in self.instance.permissions.all(),
				required = False
			)
		
		if self.instance.id:
			self.fields['users'].initial = self.instance.user_set.all()
	

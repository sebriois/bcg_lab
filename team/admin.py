from django.contrib import admin
from team.models import Team, TeamMember

class TeamAdmin(admin.ModelAdmin):
  list_display = ('name',)
admin.site.register(Team, TeamAdmin)

class TeamMemberAdmin(admin.ModelAdmin):
  list_display = ('user', 'team', 'is_chief')
admin.site.register(TeamMember, TeamMemberAdmin)
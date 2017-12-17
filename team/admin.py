from django.contrib import admin
from team.models import Team, TeamMember, TeamNameHistory


class TeamAdmin(admin.ModelAdmin):
  list_display = ('name',)
admin.site.register(Team, TeamAdmin)


class TeamMemberAdmin(admin.ModelAdmin):
  list_display = ('user', 'team')
admin.site.register(TeamMember, TeamMemberAdmin)


class TeamNameHistoryAdmin(admin.ModelAdmin):
  list_display = ('team', 'name', 'fullname')
admin.site.register(TeamNameHistory, TeamNameHistoryAdmin)
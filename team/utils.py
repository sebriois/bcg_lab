from team.models import Team


def get_teams(user):
    return Team.objects.filter(teammember__user = user)


def in_team_secretary(user):
    return user.has_perm('order.custom_goto_status_4') and not user.is_superuser

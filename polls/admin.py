import datetime

from django.contrib import admin

from .models import *


@admin.register(Polls)
class PollAdmin(admin.ModelAdmin):
    list_filter = ['created_by', 'created_on']


@admin.register(Votings)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['poll', 'option_1', 'option_2', 'option_3', 'option_4', 'option_5', "created_by", "active"]
    list_filter = ['poll__created_by']

    empty_value_display = "-null-"

    def created_by(self, obj):
        return obj.poll.created_by

    def active(self, obj):
        return not datetime.datetime.now() - obj.poll.created_on >= timedelta(days=1)

    def has_add_permission(self, request):
        return False

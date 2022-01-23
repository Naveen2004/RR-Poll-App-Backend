from datetime import timedelta

import django.contrib.auth
from django.db import models
from django.utils import timezone


class Polls(models.Model):
    question = models.CharField('question', max_length=100)
    option_1 = models.CharField('option_1', max_length=50)
    option_2 = models.CharField('option_2', max_length=50, null=True)
    option_3 = models.CharField('option_3', max_length=50, null=True)
    option_4 = models.CharField('option_4', max_length=50, null=True)
    option_5 = models.CharField('option_5', max_length=50, null=True)

    poll_id = models.CharField('poll_id', max_length=20)
    created_on = models.DateTimeField('created_on', auto_now=True)
    created_by = models.ForeignKey(django.contrib.auth.get_user_model(), on_delete=models.CASCADE)

    def is_valid(self):
        return self.created_on >= timezone.now() - timedelta(days=1)

    def __str__(self):
        return f"Q: {self.question}"


class Votings(models.Model):
    poll = models.ForeignKey("Polls", on_delete=models.CASCADE)
    option_1 = models.IntegerField("option_1")
    option_2 = models.IntegerField("option_2", null=True)
    option_3 = models.IntegerField("option_3", null=True)
    option_4 = models.IntegerField("option_4", null=True)
    option_5 = models.IntegerField("option_5", null=True)


class GeneralLog(models.Model):
    ip = models.GenericIPAddressField("ip", protocol='both')
    user_agent = models.CharField('user_agent', max_length=200)
    access_time = models.DateTimeField("access_time", auto_now=True)


class VotedLog(models.Model):
    ip = models.GenericIPAddressField("ip", protocol='both')
    user_agent = models.CharField('user_agent', max_length=200)
    time = models.DateTimeField('time', auto_now=True)
    poll = models.ForeignKey('Polls', on_delete=models.CASCADE)

import datetime
import re

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.handlers.wsgi import WSGIRequest as Request
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.generic import View

from .models import *
from .utils import *


class SignUpView(View):
    def get(self, request: Request) -> JsonResponse:
        if request.user.is_authenticated:
            res = {"status": 1}
        else:
            res = {"status": -1}
        res = JsonResponse(res)
        res.set_cookie("csrftoken", get_token(request), domain="rr-polls.herokuapp.com",
                       expires=datetime.datetime.now() + datetime.timedelta(days=365), max_age=1209600, samesite="None",
                       secure=True)
        return res

    def post(self, request: Request) -> JsonResponse:

        try:
            uname = request.POST["uname"]
            email = request.POST["email"]
            pwd = request.POST["pwd"]
            if re.fullmatch(r"^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$", email):
                if not User.objects.filter(username=uname).exists():
                    u = User.objects.create_user(username=uname, email=email, password=pwd)
                    u.save()
                    res = {"status": 1, "message": "User Successfully created.. Please login."}
                else:
                    res = {"status": -1, "message": "User already exists.."}

            else:
                res = {"status": -1, "message": "Email Validation Failed.."}

        except KeyError as e:
            res = {"status": -1, "message": f"Field {str(e)} is not defined"}

        return JsonResponse(res)


class LoginView(View):
    def get(self, request: Request) -> JsonResponse:

        print(get_token(request))
        if request.user.is_authenticated:
            res = {"status": 1}
        else:
            res = {"status": -1}

        res = JsonResponse(res)
        res.set_cookie("csrftoken", get_token(request), domain="rr-polls.herokuapp.com",
                       expires=datetime.datetime.now() + datetime.timedelta(days=365), max_age=1209600, samesite="None",
                       secure=True)
        return res

    def post(self, request: Request) -> JsonResponse:

        try:
            uname = request.POST["uname"]
            pwd = request.POST["pwd"]

            user = authenticate(username=uname, password=pwd)
            if user is not None:
                login(request, user)
                res = {"status": 1, "message": "Authentication Successful.."}
            else:
                res = {"status": -1, "message": "Invalid Credentials"}
        except KeyError as e:
            res = {"status": -1, "message": f"Field {str(e)} is missing.."}

        return JsonResponse(res)


class DashboardView(View):

    def get(self, request: Request) -> JsonResponse:
        if request.user.is_authenticated:
            user = request.user
            recent_polls = []
            polls_by_user = Polls.objects.filter(created_by=user)
            for poll in polls_by_user:
                d = {}
                options = [poll.option_1, poll.option_2, poll.option_3, poll.option_4, poll.option_5]
                voting = Votings.objects.get(poll=poll)
                votes = [voting.option_1, voting.option_2, voting.option_3,
                         voting.option_4, voting.option_5]
                opt_arr = list(filter(lambda x: True if x is not None else False, options))
                d["question"] = poll.question
                d["options"] = opt_arr
                d["votes"] = votes
                d["totalvotes"] = sum([x for x in votes if x is not None])
                d["createdon"] = poll.created_on.strftime("%d-%m-%Y %I:%M %p")
                d["expired"] = datetime.datetime.now() - poll.created_on >= timedelta(days=1)
                d["link"] = poll.poll_id
                recent_polls.append(d)
            res = {"status": 1, "uname": user.username, "recentpolls": recent_polls[::-1][:10]}
        else:
            res = {"status": -1, "message": "unauthenticated"}
        res = JsonResponse(res)
        res.set_cookie("csrftoken", get_token(request), domain="rr-polls.herokuapp.com",
                       expires=datetime.datetime.now() + datetime.timedelta(days=365), max_age=1209600, samesite="None",
                       secure=True)
        return res

    def post(self, request: Request) -> JsonResponse:
        if request.user.is_authenticated:
            user = request.user
            question = request.POST["question"]
            options = dict(request.POST)["options[]"]
            option_1, option_2, option_3, option_4, option_5 = map(lambda x: x if x else None, options)
            p = Polls(question=question, option_1=option_1, option_2=option_2, option_3=option_3, option_4=option_4,
                      option_5=option_5, poll_id=generate_unique_id(), created_by=User.objects.get(username=user))
            p.save()

            option_1, option_2, option_3, option_4, option_5 = map(lambda x: 0 if x else None, options)
            v = Votings(poll=p, option_1=option_1, option_2=option_2, option_3=option_3, option_4=option_4,
                        option_5=option_5)
            v.save()
            res = {"status": 1, "pollid": p.poll_id}

        else:
            res = {"status": -1, "message": "unauthenticated"}

        return JsonResponse(res)

    def put(self, request: Request) -> JsonResponse:
        if request.user.is_authenticated:
            logout(request)
            res = {"status": 1, "message": "logged_out"}
        else:
            res = {"status": -1, "message": "Invalid Operation"}

        return JsonResponse(res)

    def delete(self, request: Request, id="") -> JsonResponse:
        if request.user.is_authenticated:
            user = request.user
            p = Polls.objects.filter(created_by=user, poll_id=id)

            if p.exists():
                p.delete()
                res = {"status": 1, "message": "deleted successfully"}
            else:
                res = {"status": -1, "message": "Unauthorized"}
        else:
            res = {"status": -1, "message": "Unauthorized"}

        return JsonResponse(res)


class PollView(View):

    def get(self, request: Request, id="") -> JsonResponse:
        res = {}
        poll_id = id
        p = Polls.objects.filter(poll_id=poll_id)

        if p and not ((datetime.datetime.now() - p[0].created_on) >= timedelta(days=1)):
            data = {}
            poll = p[0]
            data["question"] = poll.question
            data["options"] = list(filter(lambda x: True if x is not None else False,
                                          [poll.option_1, poll.option_2, poll.option_3, poll.option_4, poll.option_5]))
            data["user"] = poll.created_by.username
            res = {"status": 1, "data": data}
        else:
            res = {"status": -1, "message": "Invalid Poll ID.."}
        res = JsonResponse(res)
        res.set_cookie("csrftoken", get_token(request), domain="rr-polls.herokuapp.com",
                       expires=datetime.datetime.now() + datetime.timedelta(days=365), max_age=1209600, samesite="None",
                       secure=True)
        return res

    def post(self, request: Request, id="") -> JsonResponse:
        poll_id = id
        poll = Polls.objects.filter(poll_id=poll_id)
        if poll and not ((datetime.datetime.now() - poll[0].created_on) >= timedelta(days=1)):
            voted = request.POST["voted"]
            poll = poll[0]
            poll_options = [poll.option_1, poll.option_2, poll.option_3,
                            poll.option_4, poll.option_5]

            voting = Votings.objects.get(poll=poll)
            voting_options = [voting.option_1, voting.option_2, voting.option_3,
                              voting.option_4, voting.option_5]

            for i, j in enumerate(poll_options):
                if j == voted:
                    voting_options[i] += 1

            voting.option_1 = voting_options[0]
            voting.option_2 = voting_options[1]
            voting.option_3 = voting_options[2]
            voting.option_4 = voting_options[3]
            voting.option_5 = voting_options[4]
            voting.save()

            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            user_agent = request.META.get('HTTP_USER_AGENT')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            VotedLog(poll=poll, ip=ip, user_agent=user_agent, time=datetime.datetime.now())
            res = {"status": 1, "votes": voting_options,
                   "totalvotes": sum([x for x in voting_options if x is not None])}
        else:
            res = {"status": -1, "message": "Invalid Poll ID.."}

        return JsonResponse(res)

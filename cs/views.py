import base64
import json
import uuid
from django.contrib import messages
from django.db import transaction
from django.http.response import HttpResponseRedirect, HttpResponse, HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import render, render_to_response, redirect

# Create your views here.
from django.template.context import RequestContext
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from cs.emails import send_wellcome_email, send_lambda_request
from cs.models import Player, Encounter, Battle, timedelta_format


def add_default_data(request):
    data = {
        'logged': 'authtoken' in request.session
    }

    return data

def homepage(request):
    if 'authtoken' in request.session:
        return  redirect("panel")

    return render_to_response("homepage.html", add_default_data(request), context_instance=RequestContext(request))


def register(request):
    if request.method == 'GET':
        return redirect("homepage")

    if not 'email' in request.POST or not 'name' in request.POST:
        messages.error(request, "You need to complete the registration form.")
        return redirect("homepage")

    email = request.POST['email'].strip()
    name = request.POST['name'].strip()

    if email == '' or name == '':
        messages.error(request, "You need to complete the registration form.")
        return redirect("homepage")

    if Player.objects.filter(email=email).exists():
        messages.error(request, "User already registered")
        redirect("homepage")

    player = Player(
        email=email,
        name=name,
        subscribedate=timezone.now(),
        playing=True,
        score=0,
        level=0,
        authtoken=uuid.uuid4().hex
    )

    player.save()

    send_wellcome_email(player)

    if 'authtoken' in request.session:
        del request.session['authtoken']

    request.session['authtoken'] = player.authtoken

    match = player.play_now(online=True)

    return redirect("submission", match.id)




def panel(request):
    if not 'authtoken' in request.session:
        return redirect('homepage')

    if not Player.objects.filter(authtoken=request.session['authtoken']).exists():
        del request.session['authtoken']
        return redirect('homepage')

    player = Player.objects.get(authtoken=request.session['authtoken'])

    data = add_default_data(request)
    data['player'] = player

    return render_to_response("panel.html", data, context_instance=RequestContext(request))




def loguser(request, uuid):
    if not Player.objects.filter(authtoken=uuid).exists():
        if 'authtoken' in request.session:
            del request.session['authtoken']
        return redirect('homepage')

    request.session['authtoken'] = uuid

    return redirect('panel')



def logout(request):
    if 'authtoken' in request.session:
        del request.session['authtoken']
    return redirect('homepage')




@csrf_exempt
def aws_lambda(request):
    if request.method == "GET":
        return HttpResponseForbidden()

    encounter_id = request.POST['encounter_id']
    player = request.POST['player']
    result = request.POST['result']
    timeelapsed = request.POST['elapsedtime']

    if not Encounter.objects.filter(id=encounter_id).exists():
        return HttpResponseNotFound()

    encounter = Encounter.objects.get(id=encounter_id)

    if player == "1":
        encounter.passedtests1 = result == "1"
        encounter.submission1testtime = int(timeelapsed)
    else:
        encounter.passedtests2 = result == "1"
        encounter.submission2testtime = int(timeelapsed)

    encounter.perform_checks()

    return HttpResponse("OK")


@csrf_exempt
def webhook(request):

    return HttpResponse("OK")


@transaction.atomic()
def playnow(request):
    if not 'authtoken' in request.session:
        return redirect('homepage')

    if not Player.objects.filter(authtoken=request.session['authtoken']).exists():
        del request.session['authtoken']
        return redirect('homepage')

    player = Player.objects.get(authtoken=request.session['authtoken'])


    match = player.play_now(online=True)
    return redirect("submission", match.id)


def submission(request, matchid):
    if not 'authtoken' in request.session:
        return redirect('homepage')

    if not Player.objects.filter(authtoken=request.session['authtoken']).exists():
        del request.session['authtoken']
        return redirect('homepage')

    if not Encounter.objects.filter(id=matchid).exists():
        return redirect("panel")

    match = Encounter.objects.get(id=matchid)
    player = Player.objects.get(authtoken=request.session['authtoken'])

    player_no = 0

    data = add_default_data(request)

    if match.player1_id == player.id:
        player_no = 1

        if not match.player1notified:
            match.player1notified = timezone.now()
            match.save()

        data['player_time_left'] = match.player1_time()
        data['player_time_left_str'] = timedelta_format(match.player1_time())

    elif match.player2_id == player.id:
        player_no = 2

        if not match.player2notified:
            match.player2notified = timezone.now()
            match.save()

        data['player_time_left'] = match.player2_time()
        data['player_time_left_str'] = timedelta_format(match.player2_time())

    data['match'] = match
    data['player_no'] = player_no
    data['player'] = player

    data['fn'] = match.submission1 if match.player1 == player else match.submission2
    if data['fn']==None or data['fn'].strip() == '':
        data['fn'] = """
/**
* Dont change the function name
* Just write inside the curly brackets
**/

fn = function(a) {


};
        """

    return render_to_response("submission.html", data, context_instance=RequestContext(request))






def play(request, match, uuid):
    if not Player.objects.filter(authtoken=uuid).exists():
        if 'authtoken' in request.session:
            del request.session['authtoken']
        return redirect('homepage')

    request.session['authtoken'] = uuid

    return redirect('submission', match)


@csrf_exempt
def expire(request):
    matchid = request.POST['encounter']
    player = request.POST['player']

    if not Encounter.objects.filter(id=matchid).exists():
        return HttpResponse(json.dumps({"result":"bad", "error": "Match not found"}), content_type="application/json")

    match = Encounter.objects.get(id=matchid)

    if player == "1":
        match.player1expired = True
    elif player == "2":
        match.player2expired = True

    match.save()

    return HttpResponse(json.dumps({"result":"ok"}), content_type="application/json")


@csrf_exempt
def tests(request):
    battle = Battle.objects.get(id=request.POST['battle'])
    match = Encounter.objects.get(id=request.POST['match'])
    fn = base64.b64decode(request.POST['fn'])

    player = Player.objects.get(authtoken=request.session['authtoken'])

    if match.player1 == player:
        match.submission1 = fn
        match.save()
    else:
        if match.player2 and match.player2 == player:
            match.submission2 = fn
            match.save()

    return HttpResponse(json.dumps({"result": "ok", "tests": battle.visibletests.splitlines()}), content_type="application/json")


@csrf_exempt
def finalize(request):
    battle = Battle.objects.get(id=request.POST['battle'])
    match = Encounter.objects.get(id=request.POST['match'])

    player = Player.objects.get(authtoken=request.session['authtoken'])

    if match.player1 == player:
        match.submission1created = timezone.now()
        match.save()
        send_lambda_request(match.submission1, battle.invisibletests.splitlines(), match.id, 1)
    else:
        if match.player2 and match.player2 == player:
            match.submission2created = timezone.now()
            match.save()
            send_lambda_request(match.submission2, battle.invisibletests.splitlines(), match.id, 2)

    return HttpResponse(json.dumps({"result": "ok"}), content_type="application/json")


def leaderboard(request):
    data = add_default_data(request)

    if 'authtoken' in request.session:
        data['player'] = Player.objects.get(authtoken=request.session['authtoken'])

    data['players'] = Player.objects.all().order_by('-score','-level')[:15]

    return render_to_response("leaderboard.html", data, context_instance=RequestContext(request))




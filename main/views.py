from django.shortcuts import render, HttpResponseRedirect, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django_twilio.decorators import twilio_view
from twilio.twiml import Response
from django.contrib import auth
from django.core.context_processors import csrf
from django.contrib.auth.forms import UserCreationForm
from main.models import User, Workout
# from forms import MyRegistrationForm

# Create your views here.
def index(request):
  return render(request, 'main/index.html')

#signin/login views

def login(request):
  c = {}
  c.update(csrf(request))
  return render_to_response('login.html', c)

def auth_view(request):
  username = request.POST.get('username', '')
  password = request.POST.get('password', '')
  user = auth.authenticate(username=username, password=password)

  if user is not None:
    auth.login(request, user)
    return HttpResponseRedirect('/accounts/loggedin')
  else:
    return HttpResponseRedirect('/accounts/invalid')

def loggedin(request):
  return render_to_response('loggedin.html', {'full_name': request.user.username})

def invalid_login(request):
  return render_to_response('invalid_login.html')

def logout(request):
  auth.logout(request)
  return render_to_response('logout.html')

#user registration
def register_user(request):
  if request.method == 'POST':
    form = MyRegistrationForm(request.POST)
    if form.is_valid():
      form.save()
      return HttpResponseRedirect('/accounts/register_success')

  args = {}
  args.update(csrf(request))

  args['form'] = MyRegistrationForm()
  print (args)
  return render_to_response('register.html', args)

def register_success(request):
  return render_to_response('register_success.html')

@twilio_view
def sms(request):
  incomingMessage = request.POST.get('Body', '')
  incomingMessage = "0" + incomingMessage
  incomingDigits = ''.join(x for x in incomingMessage if x.isdigit())
  incomingNumber = request.POST.get('From', 0)[2:]
  try:
    user = User.objects.get(phoneNumber=incomingNumber)
  except:
    r = Response()
    r.message("This number isn't registered. To get in on the pushups, go to lpgpushups.herokuapp.com")
    return r
  try:
    workout = Workout.objects.get(participantID=user,status="pending")
  except:
    r = Response()
    r.message("Too late! " + user.firstName + ", next time text back how many pushups you did within 5 minutes.")
    return r
  workout.score = int(incomingDigits)
  workout.status = "completed"
  workout.save()
  r = Response()
  return r

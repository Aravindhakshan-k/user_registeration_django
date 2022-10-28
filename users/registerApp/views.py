from email import message
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator 
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from users import settings
from django.core.mail import EmailMessage, send_mail

from users.settings import EMAIL_HOST_USER

# Create your views here.
def welcome(request):
    return render(request, 'welcome.html')

def signup(request):
    if request.method == "POST":
        username = request.POST['username'] # this is one method
        fname = request.POST.get('fname') # this is another method(both will work)
        lname = request.POST.get('lname')
        email = request.POST.get('email')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')

        if User.objects.filter(username=username):
            messages.error(request, 'Username already Exist')
            return redirect('welcome')

        if User.objects.filter(email=email):
            messages.error(request, 'This Email is already Exist')
            return redirect('welcome')

        
        if pass1!=pass2:
            messages.error(request, 'Password didnt match')
            return redirect('welcome')


        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.is_active = False
        myuser.save()

        messages.success(request, 'your account has been created.')

        #Email confirmation mail
        current_site = get_current_site(request)
        email_subject = "verification mail"
        message = render_to_string('email_auth.html',{
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': default_token_generator.make_token(myuser),
        })
        email=EmailMessage(
            email_subject,
            message,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        email.fail_silently = True
        email.send()
        

        return redirect('signin')

    return render(request, 'signup.html')

def signin(request):

    if request.method == 'POST':
        username = request.POST['username']
        pass1 = request.POST['pass1']

        user = authenticate(username=username, password=pass1)

        if user is not None:
            login(request,user)
            fname=user.first_name
            return render(request, 'welcome.html', {'fname':fname})
        else:
            messages.error(request,'Wrong credentials')
            return redirect('welcome')

    return render(request, 'signin.html')

def signout(request):
    logout(request)
    messages.success(request, 'Logged out Successfully.')
    return redirect('welcome')

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None

    if myuser is not None and default_token_generator.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        return redirect('welcome')

    else:
        return render(request, 'activation_fail.html')
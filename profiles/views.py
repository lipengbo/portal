from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db import transaction, IntegrityError
from django.http import HttpResponse, HttpResponseRedirect,Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.template import RequestContext
from django.utils.translation import ugettext, ugettext as _
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.conf import settings

from account.models import SignupCode, EmailAddress
import account.views
import profiles.forms

class SignupView(account.views.SignupView):

   form_class = profiles.forms.SignupForm

   def after_signup(self, form):
       self.create_profile(form)
       super(SignupView, self).after_signup(form)

   def create_profile(self, form):
       profile = self.created_user.get_profile()
       profile.phone = form.cleaned_data["phone"]
       profile.realm = form.cleaned_data["realm"]
       profile.organization = form.cleaned_data["organization"]
       profile.save()

@staff_member_required
def reject(request, id=None):
    if request.method == 'GET':
        user = get_object_or_404(User, id=id)
        form = profiles.forms.RejectForm(initial={"user": user})
        context = {}
        context['email'] = user.email
        context['form'] = form
        context['success_url'] = '/'
        #: send mail
        profile = user.get_profile()
        profile.state = 2
        profile.save()
        send_mail(_("Account Review Result"), _("Sorry, we cannot let you pass the review according to your profile.If you have any question about the result, you can contact us by replying this email."), settings.DEFAULT_FROM_EMAIL, [user.email])
        return redirect('notifications:all')
    else:
        form = profiles.forms.RejectForm(request.POST)
        #if form.is_valid():
        reason = request.POST.get('reason')
    return render(request, 'profiles/reject.html', context)

@staff_member_required
def send_confirmation(request, id):
    user = get_object_or_404(User, id=id)
    email_address = EmailAddress.objects.get_primary(user)
    if not email_address.verified:
        email_address.send_confirmation()
    profile = user.get_profile()
    profile.state = 2
    profile.save()
    context = {}
    context['email'] = email_address.email
    context['success_url'] = '/'
    return redirect('notifications:all')
    return render(request, 'profiles/email_confirmation_sent.html', context)


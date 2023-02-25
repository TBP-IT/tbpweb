import random

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMessage
from django.core.mail import make_msgid
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView

from base.models import Officer
from base.models import Term
from emailer.forms import ContactCaptcha
from emailer.forms import ContactForm
from emailer.forms import EventContactForm
from events.models import Event


class EmailerView(FormView):
    """EmailerView class for sending emails

    DO NOT USE THIS CLASS WITH as_view(). IT DOESN'T SET template_name
    OR EMAIL RECIPIENTS AND WILL PROBABLY NOT WORK. EXTEND IT

    See documentation on FormView:
    https://docs.djangoproject.com/en/1.5/ref/class-based-views/\
    generic-editing/#django.views.generic.edit.FormView

    Override dispatch for instance variables that require the use of
    variables from the url dispatcher (self.request, self.args
    and self.kwargs) to be calculated, or for views that require special
    permissions to view

    form_valid is called when the form is valid and the request is a POST.
    The original form_valid redirected to self.success_url, but this doesn't
    allow setting context variables in a confirmation message, since it gets
    handled by another view, so it has been overridden to render the template
    with render. It also now calls form.send_email() with kwargs
    to override form field data

    form_invalid has been overridden to simply set the success and
    result_message context variables (FormView already returns the form with
    error messages)

    get_context_data should be overridden to add any custom context variables.
    EmailerView already adds result_message and success

    The form_id instance variable is used for header information in sending the
    email.
    """
    form_class = ContactForm
    result_messages = {True: 'Successfully sent!',
                       False: 'Your message could not be sent for an unknown '
                              'reason. Please try again later.'}
    result_message = ''
    success = False
    form_id = ''

    def form_valid(self, form, **kwargs):
        # called when valid data is posted, should return HttpResponse kwargs
        # can be to_email, cc_list, bcc_list, headers, and overrides for form
        # field data (see ContactForm). At least one of to, cc, or bcc must
        # be given or a BadHeaderError will be raised

        ip_addr = self.request.META.get('HTTP_X_FORWARDED_FOR',
                                        self.request.META.get('REMOTE_ADDR',
                                                              'None provided'))
        useragent = self.request.META.get('HTTP_USER_AGENT',
                                          'None provided')

        form_id = ('-' + self.form_id) if self.form_id else self.form_id
        headers = kwargs.get('headers', {})
        headers['X{}-IP-Address'.format(form_id)] = ip_addr
        headers['X{}-UserAgent'.format(form_id)] = useragent
        kwargs['headers'] = headers

        self.success = form.send_email(**kwargs)
        self.result_message = self.result_messages[self.success]
        # return empty form if success = False
        # pylint: disable=E1102
        new_form = self.form_class() if self.success else form

        # override default behavior of redirecting to success url in order to
        # pass context variables for successful submission
        return render(self.request, self.template_name,
            self.get_context_data(form=new_form))

    def form_invalid(self, form):
        self.result_message = ''
        self.success = False
        return super(EmailerView, self).form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(EmailerView, self).get_context_data(**kwargs)
        context['result_message'] = self.result_message
        context['success'] = self.success
        return context

    def handle_spam(self, form, to_email, from_email, send_spam_notice,
                    send_spam, headers):
        form_id = ('-' + self.form_id) if self.form_id else self.form_id
        headers['X{}-WasSpam'.format(form_id)] = 'Yes'
        headers['X{}-Author'.format(form_id)] = form.cleaned_data['author']
        ip_addr = headers.get('X{}-IP-Address'.format(form_id), False)
        if not ip_addr:
            ip_addr = self.request.META.get('HTTP_X_FORWARDED_FOR',
                                            self.request.META.get('REMOTE_ADDR',
                                                                    'None provided'))

        if send_spam_notice:
            sender = 'root@{}'.format(settings.HOSTNAME)
            spamnotice = EmailMessage(
                subject='[{source} spam] {subject}'.format(
                    source=self.form_id,
                    subject=form.cleaned_data['subject']),
                body=('Help! We have been spammed by "{email}" from '
                      '{ip_addr}!\n\n------------\n\n{message}'.format(
                          email=from_email,
                          ip_addr=ip_addr,
                          message=form.cleaned_data['message'])),
                from_email=sender,
                to=to_email,
                headers=headers)
            # server will return 500 error if spamnotice cannot be sent.
            spamnotice.send()

        if send_spam:
            return self.form_valid(form,
                                   from_email=from_email,
                                   to_email=to_email,
                                   headers=headers)
        else:
            self.success = True
            self.result_message = self.result_messages[True]
            return render(self.request, self.template_name,
                self.get_context_data(form=self.form_class()))

class EventEmailerView(EmailerView):
    form_class = EventContactForm
    template_name = 'events/email.html'
    form_id = 'EventContact'

    # to be set by dispatch using request variables
    event = None
    event_signups = None
    cc_email = None

    @method_decorator(login_required)
    @method_decorator(
        permission_required('events.contact_participants',
                            raise_exception=True))
    def dispatch(self, request, *args, **kwargs):
        event_pk = kwargs['event_pk']
        self.event = get_object_or_404(Event, pk=event_pk)
        self.initial = {
            'name': request.user.get_full_name(),
            'email': request.user.email,
            'subject': '[{}] {}: Important announcement'.format(
                settings.SITE_TAG, self.event.name)}

        if not self.event.can_user_view(request.user):
            raise PermissionDenied
        self.event_signups = self.event.eventsignup_set.filter(
            unsignup=False).order_by('name')
        self.cc_email = [
            '{}@{}'.format(self.event.committee.mailing_list, settings.HOSTNAME)
        ]
        return super(EventEmailerView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form, **kwargs):
        bcc_list = []
        for signup in self.event_signups:
            # Check if the person has an account or if they signed up
            # "anonymously" with their email address
            if signup.user:
                bcc_list.append(signup.user.email)
            else:
                bcc_list.append(signup.email)

        if len(bcc_list) == 0:
            # empty recipients list, most likely due to no participants
            self.result_message = ('Your email was not sent because the '
                                   'recipient list for this email was empty.')
            self.success = False

            return render(self.request, self.template_name,
                self.get_context_data(form=form))
        
        return super(EventEmailerView, self).form_valid(
            form,
            cc_list=self.cc_email,
            bcc_list=bcc_list,
            **kwargs)

    def get_context_data(self, **kwargs):
        context = super(EventEmailerView, self).get_context_data(**kwargs)
        context['event'] = self.event
        context['event_signups'] = self.event_signups
        context['cc_list'] = self.cc_email
        return context


class CompanyEmailerView(EmailerView):
    template_name = 'companies/contact.html'
    form_id = 'CompanyContact'
    check_spam = False

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            name = request.user.get_full_name()
            email = request.user.email
        else:
            name = ''
            email = ''
            self.form_class = ContactCaptcha
            self.check_spam = True
        self.initial = {
            'name': name,
            'email': email}

        return super(CompanyEmailerView, self).dispatch(request, *args,
                                                        **kwargs)

    def form_valid(self, form, **kwargs):
        email = form.cleaned_data['email']
        name = form.cleaned_data['name']

        from_email = '"{}" <{}>'.format(name, email)
        reply_to = from_email

        headers = {'Reply-To': reply_to,
                   'Message-Id': make_msgid()}

        if self.check_spam and form.cleaned_data['author']:
            return self.handle_spam(form, from_email, headers)

        return super(CompanyEmailerView, self).form_valid(
            form,
            to_email=[settings.INDREL_ADDRESS],
            **kwargs)

    def handle_spam(self, form, from_email, headers, **kwargs):
        to_email = kwargs.get('to_email', [settings.INDREL_SPAM_TO])
        send_spam_notice = kwargs.get('send_spam_notice',
                                      settings.INDREL_SEND_SPAM_NOTICE)
        send_spam = kwargs.get('send_spam', settings.INDREL_SEND_SPAM)

        return super(CompanyEmailerView, self).handle_spam(
            form,
            to_email=to_email,
            from_email=from_email,
            send_spam_notice=send_spam_notice,
            send_spam=send_spam,
            headers=headers)

import random
from datetime import date

from django.core.mail import EmailMultiAlternatives
from django.core.management import BaseCommand
from django.template.loader import render_to_string
from django.utils import timezone

from base.models import Officer
from base.models import OfficerPosition
from base.models import Term
from project_reports.models import ProjectReport
from project_reports.models import ProjectReportFromEmail
from settings import HOSTNAME
from shortcuts import get_object_or_none


class Command(BaseCommand):
    def handle(self, *args, **options):
        # exclude reports from just today or reports that can't possibly be in
        # the current academic year
        current_date = timezone.localtime(timezone.now()).date()
        if current_date.month >= 8: # if we've started the next school year
            academic_year_start_date = date(current_date.year, 8, 1)
        else: # otherwise we're still in the previous school year
            academic_year_start_date = date(current_date.year - 1, 8, 1)

        unfinished_reports = ProjectReport.objects.filter(
            complete=False, term__year__gte=academic_year_start_date,
            date__lt=current_date)

        reports_by_committee = {}

        for report in unfinished_reports:
            committee = report.committee
            if committee not in reports_by_committee:
                reports_by_committee[committee] = []
            reports_by_committee[committee].append(report)

        from_emails = []
        for from_email in ProjectReportFromEmail.objects.all():
            email_str = '"{}" <{}@{}>'.format(
                from_email.name, from_email.email_prefix, HOSTNAME)
            from_emails.append(email_str)
        random.shuffle(from_emails)

        rsec = get_object_or_none(Officer,
                                  term=Term.objects.get_current_term(),
                                  position__short_name='rsec')
        rsec_mailing_list = OfficerPosition.objects.get(
            short_name='rsec').mailing_list
        if rsec:
            signature_lines = [rsec.user.userprofile.get_common_name(),
                               'Recording Secretary']
        else:
            signature_lines = ['IT Committee']

        for i, committee in enumerate(reports_by_committee.keys()):
            reports = reports_by_committee[committee]
            context = {'committee': committee.long_name,
                       'reports': reports,
                       'signature_lines': signature_lines}

            subject_format = '[TBP] {} Project Report Reminders as of {:%m/%d}'
            complete_message = EmailMultiAlternatives(
                subject=subject_format.format(
                    committee.long_name, timezone.localtime(timezone.now())),
                body=render_to_string('project_reports/email_reminder.txt',
                                      context),
                from_email=from_emails[i % len(from_emails)],
                to=list(set(['{}@{}'.format(report.author.username, HOSTNAME)
                             for report in reports])),
                cc=['{}@{}'.format(committee.mailing_list, HOSTNAME),
                    '{}@{}'.format(rsec_mailing_list, HOSTNAME)],
                headers={'Reply-to': '{}@{}'.format(
                    rsec_mailing_list, HOSTNAME)})
            complete_message.attach_alternative(render_to_string(
                'project_reports/email_reminder.html', context), 'text/html')
            complete_message.content_subtype = 'html'
            complete_message.send()

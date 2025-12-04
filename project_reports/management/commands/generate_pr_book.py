from django.conf import settings
from django.core.management import BaseCommand
from django.template.loader import render_to_string

from base.models import Officer
from candidates.models import Candidate
from project_reports.exceptions import DelayedException
from project_reports.models import ProjectReport
from project_reports.models import ProjectReportBook

import codecs
import collections
import itertools
import os
import pypandoc
import shutil
import subprocess
import tblib.pickling_support
import tempfile
import threading

tblib.pickling_support.install()


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('pr_book_id')

    def handle(self, *args, **options):
        # Save the PDF to the PR book object, or save the exception if there
        # there was a failure
        try:
            self.unwrapped_handle(*args, **options)
        except Exception as e:  # pylint: disable=broad-except
            pr_book = ProjectReportBook.objects.get(id=options['pr_book_id'])
            pr_book.exception = DelayedException(e)
            pr_book.save()

    def unwrapped_handle(self, *args, **options):
        pr_book = ProjectReportBook.objects.get(id=options['pr_book_id'])

        terms = pr_book.terms.order_by('id')
        president = Officer.objects.get(
            position__long_name='President',
            term=terms.last())

        pandoc_header = self.get_pandoc_header(terms)
        presidents_letter = self.generate_presidents_letter(
            pr_book.presidents_letter, president)
        pr_sections = self.export_project_reports(terms)
        membership_timeline_summaries = [self.membership_timeline_summary(term)
                                         for term in terms]
        membership_timeline_summary = \
            '# Membership Timeline Summary\n\n\\newpage\n\n' + \
            '\n'.join(membership_timeline_summaries)

        markdown = '\n\n'.join([
            pandoc_header,
            presidents_letter,
            pr_sections,
            membership_timeline_summary
        ])

        dirname = tempfile.mkdtemp()
        orig_dir = os.getcwd()
        module_dir = os.path.dirname(__file__)
        os.chdir(dirname)
        with codecs.open('book.tex', 'w', 'utf-8') as fileobj:
            latex = pypandoc.convert(
                markdown,
                'latex',
                format='markdown',
                extra_args=(
                    '--template',
                    os.path.join(module_dir, 'template.tex'),
                    '--toc',
                    '--toc-depth=2'
                )
            )
            fileobj.write(latex)

        def run(context):
            # Run LaTeX, storing information in the `context` dictionary
            pdflatex_command = ['pdflatex', 'book.tex']
            context['proc'] = subprocess.run(
                pdflatex_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                input=b'R')
            proc = context['proc']
            if not os.path.isfile('book.pdf'):
                output_result="NOTE: No book.log - Generally means pdflatex failed to start"
                if os.path.isfile('book.log'):
                    output_result = open('book.log').read()
                context['exception'] = subprocess.CalledProcessError(
                    cmd=" ".join(pdflatex_command),
                    returncode=proc.returncode,
                    output=output_result,
                )

        def run_thread(timeout=100):
            context = dict()
            thread = threading.Thread(target=lambda: run(context))
            thread.start()
            thread.join(timeout)
            if thread.is_alive():
                context['proc'].terminate()
                thread.join()
                raise Exception('Command pdflatex timed out')
            elif 'exception' in context.keys():
                raise context['exception']

        run_thread()
        run_thread()  # run LaTeX twice to create table of contents

        pr_book_name = '{}.pdf'.format(pr_book.pk)
        pr_book.pdf.name = pr_book.pdf.field.upload_to + pr_book_name
        shutil.copyfile(src=os.path.join(os.getcwd(), 'book.pdf'), dst=os.path.join(settings.PRIVATE_STORAGE_ROOT, pr_book.pdf.name))

        pr_book.save()

        os.chdir(orig_dir)
        shutil.rmtree(dirname)

    def get_pandoc_header(self, terms):
        return render_to_string(
            'project_reports/pandoc_header.txt',
            {'first_term': list(terms)[0], 'last_term': list(terms)[-1]})

    def generate_presidents_letter(self, text, president):
        return render_to_string(
            'project_reports/presidents_letter.txt',
            {'text': text, 'president': president})

    def export_project_reports(self, terms):
        reports = ProjectReport.objects.filter(
            term__in=terms,
            event__cancelled=False,
            complete=True,
        ).order_by('area', 'date')
        area_names = dict(ProjectReport.PROJECT_AREA_CHOICES)
        prs_by_area_name = dict()
        for report in reports:
            area_name = area_names[report.area]
            if area_name not in prs_by_area_name.keys():
                prs_by_area_name[area_name] = dict()
            prs_by_term = prs_by_area_name[area_name]
            if report.term not in prs_by_term:
                prs_by_term[report.term] = [report]
            else:
                prs_by_term[report.term].append(report)

        for key, value in prs_by_area_name.items():
            prs_by_area_name[key] = sorted(value.items(), key=lambda x: x[0])

        return render_to_string(
            'project_reports/pr_sections_export.txt',
            {'prs_by_area_name': prs_by_area_name})

    def membership_timeline_summary(self, term):
        reports = ProjectReport.objects.filter(
            term=term, complete=True).prefetch_related(
            'officer_list', 'member_list', 'candidate_list')
        officer_counts = collections.Counter()
        member_counts = collections.Counter()
        candidate_counts = collections.Counter()

        # Many participants are misclassified (e.g. candidates as members),
        # so they must be checked again
        officer_users = Officer.objects.filter(term=term).values_list(
            'user', flat=True)
        candidate_users = Candidate.objects.filter(term=term).values_list(
            'user', flat=True)

        for report in reports:
            participants = itertools.chain(report.officer_list.all(),
                                           report.member_list.all(),
                                           report.candidate_list.all())
            for participant in participants:
                # Many participants are misclassified (e.g. candidates as
                # members), so they must be checked again
                if participant.id in officer_users:
                    officer_counts[participant] += 1
                elif participant.id in candidate_users:
                    candidate_counts[participant] += 1
                else:
                    member_counts[participant] += 1
        return render_to_string(
            'project_reports/membership_timeline_export.txt',
            {'term': term,
             'officer_counts': officer_counts.most_common(),
             'member_counts': member_counts.most_common(),
             'candidate_counts': candidate_counts.most_common()})

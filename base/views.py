import collections
import csv

from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.views.generic.base import TemplateView
from django.views.generic.base import View

from quark.base.models import Officer
from quark.base.models import Term
from quark.events.models import Event
from quark.newsreel.models import News
from quark.user_profiles.models import UserProfile


class HomePageView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        context['event_list'] = Event.objects.get_user_viewable(
            self.request.user).get_upcoming()[:3]
        context['news_list'] = News.objects.all()[:5]
        return context


class OfficerPortalView(TemplateView):
    template_name = 'base/officer_portal.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        if not self.request.user.userprofile.is_officer():
            raise PermissionDenied
        return super(OfficerPortalView, self).dispatch(*args, **kwargs)


class ITToolsView(TemplateView):
    template_name = 'base/it_tools.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        is_staff = self.request.user.is_staff
        is_superuser = self.request.user.is_superuser
        if not is_staff and not is_superuser:
            raise PermissionDenied
        return super(ITToolsView, self).dispatch(*args, **kwargs)


class ProcrastinationView(TemplateView):
    template_name = 'base/procrastination.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(ProcrastinationView, self).dispatch(*args, **kwargs)


class TermParameterMixin(object):
    """View mixin that adds a 'display_term' variable to the view class and
    term variables to the context data.

    The display_term is pulled from a "term" URL get request parameter, where
    the term is specified in URL-friendly form (for instance, term=sp2012 for
    Spring 2012). If there is no term parameter, display_term is set to the
    current term. If the term parameter is invalid, the server returns a 400
    error response.

    Also adds an is_current field to the view, which is True if display_term
    is the current term.

    Recommended use with a template that includes "term-selection.html".
    """
    display_term = None  # The Term that the view is displaying/featuring
    is_current = False  # True if display_term is the current term

    def dispatch(self, request, *args, **kwargs):
        term = request.GET.get('term', '')
        current_term = Term.objects.get_current_term()
        if not term:
            self.display_term = current_term
        else:
            self.display_term = Term.objects.get_by_url_name(term)
            if self.display_term is None:
                # Bad request, since their term URL parameter doesn't match a
                # term of ours
                return render(request, template_name='400.html', status=400)

        if self.display_term.pk == current_term.pk:
            self.is_current = True

        return super(TermParameterMixin, self).dispatch(
            request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TermParameterMixin, self).get_context_data(**kwargs)
        context['display_term'] = self.display_term
        context['display_term_name'] = self.display_term.verbose_name()
        context['display_term_url_name'] = self.display_term.get_url_name()
        context['is_current'] = self.is_current

        # Add queryset of all Terms up to and including the current term,
        # ordered from current to oldest
        context['terms'] = Term.objects.get_terms(reverse=True)
        return context


class OfficersListView(TermParameterMixin, ListView):
    context_object_name = 'officers'
    model = Officer
    template_name = "base/officers.html"

    def get_queryset(self):
        return Officer.objects.filter(term=self.display_term).order_by(
            'position__rank', '-is_chair').select_related(
            'user__userprofile', 'user__studentorguserprofile', 'position')


class OfficerContactExportView(View):

    # Gmail expects these columns to be present in the CSV
    COLUMN_NAMES = ['Name',
                    'Given Name',
                    'Additional Name',
                    'Family Name',
                    'Birthday',
                    'Gender',
                    'E-mail 1 - Type',
                    'E-mail 1 - Value',
                    'E-mail 2 - Type',
                    'E-mail 2 - Value',
                    'Phone 1 - Type',
                    'Phone 1 - Value',
                    'Address 1 - Type',
                    'Address 1 - Formatted',
                    'Address 1 - Street',
                    'Address 1 - City',
                    'Address 1 - PO Box',
                    'Address 1 - Region',
                    'Address 1 - Postal Code',
                    'Address 1 - Country',
                    'Address 1 - Extended Address',
                    'Organization 1 - Type',
                    'Organization 1 - Name',
                    'Organization 1 - Yomi Name',
                    'Organization 1 - Title',
                    'Organization 1 - Department',
                    'Organization 1 - Symbol',
                    'Organization 1 - Location',
                    'Organization 1 - Job Description']

    @method_decorator(login_required)
    @method_decorator(permission_required(
        'view_officer_contacts', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(OfficerContactExportView, self).dispatch(*args, **kwargs)

    # Formats one row of the CSV with the given arguments.
    # pylint: disable=R0913
    @staticmethod
    def get_row(common_name='', first_name='', last_name='', birthday='',
                gender='', tbp_email='', alt_email='', cell_phone='',
                local_address='', local_city='', local_state='', local_zip='',
                officer_position=''):
        row_dict = collections.OrderedDict()
        for column_name in OfficerContactExportView.COLUMN_NAMES:
            row_dict[column_name] = ''

        row_dict['Name'] = common_name
        row_dict['Given Name'] = first_name
        row_dict['Family Name'] = last_name
        row_dict['Birthday'] = birthday
        row_dict['Gender'] = gender
        row_dict['E-mail 1 - Type'] = 'TBP Email'
        row_dict['E-mail 1 - Value'] = tbp_email
        row_dict['E-mail 2 - Type'] = 'Other Email'
        row_dict['E-mail 2 - Value'] = alt_email
        row_dict['Phone 1 - Value'] = cell_phone
        row_dict['Address 1 - Type'] = 'Local Address'
        row_dict['Address 1 - Street'] = local_address
        row_dict['Address 1 - City'] = local_city
        row_dict['Address 1 - Region'] = local_state
        row_dict['Address 1 - Postal Code'] = local_zip
        row_dict['Organization 1 - Name'] = 'Tau Beta Pi CA-A'
        row_dict['Organization 1 - Title'] = officer_position

        return row_dict.values()

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="officers.csv"'
        current_term = Term.objects.get_current_term()
        officers = Officer.objects.filter(term=current_term).order_by(
            'position', '-is_chair')
        officers_by_profile_id = collections.OrderedDict()
        for officer in officers:
            profile_id = officer.user.userprofile.id
            if profile_id not in officers_by_profile_id:
                officers_by_profile_id[profile_id] = [officer]
            else:
                officers_by_profile_id[profile_id].append(officer)

        writer = csv.writer(response)
        writer.writerow(OfficerContactExportView.COLUMN_NAMES)
        for profile_id, profile_officers in officers_by_profile_id.items():
            profile = UserProfile.objects.get(id=profile_id)
            full_gender = dict(UserProfile.GENDER_CHOICES)[profile.gender]
            local_address_summary = profile.local_address1
            position_names = [off.position_name() for off in profile_officers]
            position_summary = '/'.join(position_names)
            if profile.local_address2:
                local_address_summary += ', {}'.format(profile.local_address2)
            row = OfficerContactExportView.get_row(
                common_name=profile.get_common_name(),
                first_name=profile.user.first_name,
                last_name=profile.user.last_name,
                birthday=profile.birthday,
                gender=full_gender,
                tbp_email=profile.get_preferred_email(),
                alt_email=profile.user.email,
                cell_phone=profile.cell_phone,
                local_address=local_address_summary,
                local_city=profile.local_city,
                local_state=profile.local_state,
                local_zip=profile.local_zip,
                officer_position=position_summary)
            writer.writerow(row)

        return response

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.db.models import Max, Q
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import ListView

from quark.base.models import Officer
from quark.base.models import OfficerPosition
from quark.base.models import Term
from quark.base.views import TermParameterMixin
from quark.houses.models import House
from quark.houses.models import HouseMember
from quark.shortcuts import get_object_or_none
from quark.utils.ajax import json_response


class HouseMembersEditView(TermParameterMixin, ListView):
    context_object_name = 'eligible_house_members'
    current_term = Term.objects.get_current_term()
    model = get_user_model()
    template_name = 'houses/edit.html'

    @method_decorator(login_required)
    @method_decorator(permission_required('houses.add_housemember',
                      raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(HouseMembersEditView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        # Select all users who are either officers or candidates this term
        return get_user_model().objects.filter(
            Q(officer__term=self.display_term) |
            Q(candidate__term=self.display_term)).select_related(
            'userprofile').order_by('userprofile').distinct()

    def get_context_data(self, **kwargs):
        context = super(HouseMembersEditView, self).get_context_data(
            **kwargs)

        context['houses'] = House.objects.all()

        # Find house leaders and candidates to check groups without querying DB
        house_leader = get_object_or_none(OfficerPosition,
                                          short_name='house-leaders')

        context['house_leaders'] = get_user_model().objects.filter(
            officer__term=self.display_term,
            officer__position=house_leader)

        context['candidates'] = get_user_model().objects.filter(
            candidate__term=self.display_term)

        # Create a dict with user ids as keys mapping to house names to identify
        # users who are already members of a house.
        house_members = HouseMember.objects.filter(
            user__in=context['eligible_house_members'],
            term=self.display_term).select_related('house', 'user')
        user_house_dict = {}

        for member in house_members:
            user_house_dict[member.user.id] = member.house.mailing_list

        context['user_houses'] = user_house_dict

        return context


class HouseMembersListView(TermParameterMixin, ListView):
    context_object_name = 'house_members'
    model = HouseMember
    template_name = 'houses/list.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(HouseMembersListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        # Display house leader first, then candidates, then others
        return HouseMember.objects.filter(term=self.display_term).annotate(
            has_initiated=Max('user__candidate__initiated')).order_by(
            'house__name', '-is_leader', 'has_initiated').select_related(
            'user__userprofile', 'user__studentorguserprofile', 'house')

    def get_context_data(self, **kwargs):
        context = super(HouseMembersListView, self).get_context_data(**kwargs)

        # Find candidates in this term to check groups without querying the DB
        context['candidates'] = get_user_model().objects.filter(
            candidate__term=self.display_term)

        return context


@require_POST
@permission_required('houses.add_housemember', raise_exception=True)
def assign_house(request):
    """Assign an officer or candidate to a house for the current semester.

    The user is specified by a userPK post parameter, the house is specified by
    a houseName post parameter, and the term is specified by a term post
    parameter which is the url name of the display term.
    """
    user_pk = request.POST.get('userPK')
    user = get_user_model().objects.get(pk=user_pk)
    house_name = request.POST.get('houseName')
    house = House.objects.get(mailing_list=house_name)
    term = Term.objects.get_by_url_name(request.POST.get('term'))

    house_member, created = HouseMember.objects.get_or_create(
        user=user, term=term, defaults={'house': house})

    # Find out if the user is a house leader for setting is_leader correctly
    user_house_leader = get_object_or_none(
        Officer, position__short_name='house-leaders',
        user__id=user_pk, term=term)

    if user_house_leader is not None:
        # Find out if there is already a house leader for this house
        existing_house_leader = get_object_or_none(
            HouseMember, house=house, is_leader=True, term=term)

        if existing_house_leader is not None:
            # If there is already a house leader in that house and we're trying
            # to add a house leader, delete any newly created HouseMember object
            # and return a 400 error to be handled by jQuery
            if created:
                house_member.delete()

            return json_response(status=400)
        else:
            house_member.is_leader = True

    # If an object was gotten, the user was in a different house previously
    if not created:
        house_member.house = house

    house_member.save()

    return json_response()


@require_POST
@permission_required('houses.delete_housemember', raise_exception=True)
def unassign_house(request):
    """Remove an officer or candidate from his or her house this semester.

    The user is specified by a userPK post parameter, and the house doesn't
    matter as a user can only be in one house in a given semester. The term
    is specified by a term post parameter which is the url name of the display
    term.
    """
    user_pk = request.POST.get('userPK')
    term = Term.objects.get_by_url_name(request.POST.get('term'))
    # Delete the HouseMember object for this user/term if it exists
    try:
        HouseMember.objects.get(user__pk=user_pk, term=term).delete()
    except HouseMember.DoesNotExist:
        # Fine if the HouseMember does not exist since we wanted to remove it
        pass
    return json_response()

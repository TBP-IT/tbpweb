from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import CreateView
from django.views.generic import DetailView
from django.views.generic import ListView

from quark.quote_board.forms import QuoteForm
from quark.quote_board.models import Quote
from quark.shortcuts import create_leaderboard


class QuoteCreateView(CreateView):
    form_class = QuoteForm
    template_name = 'quote_board/add.html'

    @method_decorator(login_required)
    @method_decorator(
        permission_required('quote_board.add_quote', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(QuoteCreateView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.submitter = self.request.user
        obj.save()
        return super(QuoteCreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('quote-board:list')


class QuoteDetailView(DetailView):
    context_object_name = 'quote'
    model = Quote
    pk_url_kwarg = 'quote_pk'
    template_name = 'quote_board/detail.html'

    @method_decorator(login_required)
    @method_decorator(
        permission_required('quote_board.view_quotes', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(QuoteDetailView, self).dispatch(*args, **kwargs)


class QuoteLeaderboardListView(ListView):
    context_object_name = 'leader_list'
    template_name = 'quote_board/leaderboard.html'
    paginate_by = 50

    @method_decorator(login_required)
    @method_decorator(
        permission_required('quote_board.view_quotes', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(QuoteLeaderboardListView, self).dispatch(*args, **kwargs)

    def get_queryset(self):
        # Get list of users who have been quoted
        speakers = Quote.objects.values_list('speakers')

        # Because quotes map to multiple users (speaker and submitter), use
        # extra to obtain the leaders ordered by number of times quoted
        querystring = 'SELECT COUNT(*) FROM quote_board_quote_speakers WHERE ' \
            'quote_board_quote_speakers.user_id = auth_user.id'

        leaders = get_user_model().objects.filter(id__in=speakers).extra(
            select={'score': querystring}).extra(
            order_by=['-score']).select_related('userprofile')

        return create_leaderboard(leaders, 70)


class QuoteListView(ListView):
    context_object_name = 'quote_list'
    queryset = Quote.objects.select_related(
        'submitter__userprofile').prefetch_related('speakers__userprofile')
    template_name = 'quote_board/list.html'

    @method_decorator(login_required)
    @method_decorator(
        permission_required('quote_board.view_quotes', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        return super(QuoteListView, self).dispatch(*args, **kwargs)


class SpeakerQuoteListView(ListView):
    context_object_name = 'quote_list'
    display_user = None
    template_name = 'quote_board/speaker.html'

    @method_decorator(login_required)
    @method_decorator(
        permission_required('quote_board.view_quotes', raise_exception=True))
    def dispatch(self, *args, **kwargs):
        self.display_user = get_object_or_404(
            get_user_model(), id=self.kwargs['user_id'])
        return super(SpeakerQuoteListView, self).dispatch(*args, **kwargs)

    def get_queryset(self, *args, **kwargs):
        queryset = Quote.objects.filter(
            speakers__pk=self.kwargs['user_id']).select_related(
            'submitter__userprofile').prefetch_related('speakers__userprofile')

        return queryset

    def get_context_data(self, **kwargs):
        context = super(SpeakerQuoteListView, self).get_context_data(**kwargs)
        context['display_user'] = self.display_user
        context['num_quotes'] = context['quote_list'].count()

        return context

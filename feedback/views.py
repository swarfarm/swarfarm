from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseForbidden
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.views.generic.edit import FormMixin
from django.db.models import Q

from .forms import IssueForm, CommentForm, SearchForm
from .models import Issue, Discussion


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)


class ProfileNameMixin(object):
    def get_context_data(self, **kwargs):
        context = super(ProfileNameMixin, self).get_context_data(**kwargs)
        context['profile_name'] = self.request.user.username
        return context


class IssueList(LoginRequiredMixin, ProfileNameMixin, FormMixin, ListView):
    model = Issue
    paginate_by = 25
    form_class = SearchForm
    search_term = None

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        if form.is_valid():
            self.search_term = form.cleaned_data['search']
        else:
            self.search_term = None

        return self.get(request, *args, **kwargs)

    def get_queryset(self):
        mode = self.kwargs.get('mode', None)

        if self.request.user.is_superuser:
            issues = Issue.objects.all()
        else:
            issues = Issue.objects.filter(Q(user=self.request.user) | Q(public=True))

        if self.search_term and not mode == 'mine':
            issues = issues.filter(Q(subject__icontains=self.search_term) | Q(description__icontains=self.search_term) | Q(discussion__comment__icontains=self.search_term)).distinct()

        if mode == 'mine':
            return issues.filter(user=self.request.user)
        elif mode == 'closed':
            return issues.filter(closed=True)
        else:
            return issues.filter(closed=False)

    def get_context_data(self, **kwargs):
        context = super(IssueList, self).get_context_data(**kwargs)
        context['mode'] = self.kwargs.get('mode', None)
        context['search_form'] = self.get_form()
        return context

    def get_success_url(self):
        return reverse('feedback:index')


class IssueCreate(LoginRequiredMixin, ProfileNameMixin, CreateView):
    model = Issue
    form_class = IssueForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(IssueCreate, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(IssueCreate, self).get_context_data(**kwargs)
        context['mode'] = self.kwargs.get('mode', None)
        return context


class IssueDetail(LoginRequiredMixin, ProfileNameMixin, DetailView):
    model = Issue

    def get(self, request, *args, **kwargs):
        issue = self.get_object()
        if issue.user == self.request.user or issue.public or self.request.user.is_superuser:
            return super(IssueDetail, self).get(request, *args, **kwargs)
        else:
            return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        context = super(IssueDetail, self).get_context_data(**kwargs)
        comment_form = CommentForm()
        comment_form.helper.form_action = reverse('feedback:comment_add', kwargs={'issue_pk': self.kwargs['pk']})
        context['comment_form'] = comment_form

        return context


class CommentCreate(LoginRequiredMixin, ProfileNameMixin, CreateView):
    model = Discussion
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.feedback = Issue.objects.get(pk=self.kwargs['issue_pk'])
        return super(CommentCreate, self).form_valid(form)

    def get_success_url(self):
        return reverse('feedback:issue_detail', kwargs={'pk': self.kwargs['issue_pk']})

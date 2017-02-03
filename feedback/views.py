from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.db.models import Q

from .forms import IssueForm, CommentForm
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


class IssueList(LoginRequiredMixin, ProfileNameMixin, ListView):
    model = Issue
    paginate_by = 25

    def get_queryset(self):
        mode = self.kwargs.get('mode', None)
        if mode == 'mine':
            return Issue.objects.filter(user=self.request.user)
        elif mode == 'all':
            if self.request.user.is_superuser:
                return Issue.objects.all()
            else:
                return Issue.objects.filter(Q(user=self.request.user) | Q(public=True))
        else:
            if self.request.user.is_superuser:
                return Issue.objects.filter(closed=False)
            else:
                return Issue.objects.filter(closed=False).filter(Q(user=self.request.user) | Q(public=True))

    def get_context_data(self, **kwargs):
        context = super(IssueList, self).get_context_data(**kwargs)
        context['mode'] = self.kwargs.get('mode', None)
        return context


def issue_search(request):
    from django.db.models import Q
    from django.shortcuts import render, redirect

    query = request.GET.get('query', None)

    if query:
        results = Issue.objects.filter(Q(subject__icontains=query) | Q(description__icontains=query))

        return render(request, 'feedback/issue_list.html', {'issue_list': results, 'query': query})
    else:
        return redirect('feedback:index')


class IssueCreate(LoginRequiredMixin, ProfileNameMixin, CreateView):
    model = Issue
    form_class = IssueForm

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.status = Issue.STATUS_UNREVIEWED
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

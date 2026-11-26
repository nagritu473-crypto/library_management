from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, CreateView, FormView, TemplateView
from django.urls import reverse_lazy
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import Book, Issue
from .forms import CustomUserCreationForm, BookSearchForm

class CustomLoginView(LoginView):
    template_name = 'library/login.html'

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return redirect('login')

class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'library/register.html'

    def form_valid(self, form):
        messages.success(self.request, 'Registration successful! Please log in.')
        response = super().form_valid(form)
        return response

# ... rest unchanged ...

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'library/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        issues = Issue.objects.filter(user=user).select_related('book')
        issued_count = issues.filter(status='issued').count()
        returned_count = issues.filter(status='returned').count()
        context['issues'] = issues
        context['issued_count'] = issued_count
        context['returned_count'] = returned_count
        return context

class SearchView(FormView):
    form_class = BookSearchForm
    template_name = 'library/search.html'

    def form_valid(self, form):
        query = form.cleaned_data['query']
        books = Book.objects.filter(
            Q(title__icontains=query) | Q(author__icontains=query)
        )
        return self.render_to_response(
            self.get_context_data(form=form, books=books)
        )

    def form_invalid(self, form):
        return self.render_to_response(
            self.get_context_data(form=form, books=Book.objects.none())
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'books' not in context:
            context['books'] = Book.objects.none()
        return context

class IssueListView(LoginRequiredMixin, ListView):
    model = Issue
    template_name = 'library/issues.html'
    context_object_name = 'issues'
    paginate_by = 10

    def get_queryset(self):
        queryset = Issue.objects.select_related('user', 'book').all()
        issued_count = queryset.filter(status='issued').count()
        returned_count = queryset.filter(status='returned').count()
        overdue_count = queryset.filter(status='overdue').count()
        self.extra_context = {
            'issued_count': issued_count,
            'returned_count': returned_count,
            'overdue_count': overdue_count,
        }
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.extra_context or {})
        return context

def issue_book(request, book_id):
    if request.method == 'POST':
        book = get_object_or_404(Book, id=book_id)
        if book.available_copies > 0:
            Issue.objects.create(
                user=request.user,
                book=book,
                expected_return_date=timezone.now().date() + timedelta(days=14)
            )
            messages.success(request, 'Book issued successfully!')
            return redirect('dashboard')
    return redirect('search')

def return_book(request, issue_id):
    if request.method == 'POST':
        issue = get_object_or_404(Issue, id=issue_id, user=request.user)
        if issue.status == 'issued':
            issue.status = 'returned'
            issue.save()
            messages.success(request, 'Book returned successfully!')
            return redirect('dashboard')
    return redirect('issues')

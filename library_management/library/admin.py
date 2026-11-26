from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Book, Issue

# Unregister default User admin
admin.site.unregister(User)

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_superuser', 'date_joined')

admin.site.register(User, CustomUserAdmin)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'total_copies', 'available_copies')
    search_fields = ('title', 'author', 'isbn')
    list_filter = ('total_copies',)

@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'issue_date', 'expected_return_date', 'status')
    list_filter = ('status', 'issue_date', 'expected_return_date')
    search_fields = ('user__username', 'book__title')

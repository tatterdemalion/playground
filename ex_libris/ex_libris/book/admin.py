from django.contrib import admin
from book.models import Author, Book


class AuthorAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


class BookAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}

admin.site.register(Author, AuthorAdmin)
admin.site.register(Book, BookAdmin)

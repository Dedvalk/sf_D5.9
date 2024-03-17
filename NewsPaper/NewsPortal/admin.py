from django.contrib import admin
from .models import Category, Post

# Register your models here.

class PostAdmin(admin.ModelAdmin):
    
    list_display = [field.name for field in Post._meta.get_fields()]

admin.site.register(Category)
admin.site.register(Post)

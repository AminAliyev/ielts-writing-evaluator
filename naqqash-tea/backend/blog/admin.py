from django.contrib import admin
from .models import Post, PostCategory, Tag

admin.site.register(Post)
admin.site.register(PostCategory)
admin.site.register(Tag)

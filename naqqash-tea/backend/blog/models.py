from django.db import models
from django.utils.text import slugify


class PostCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)


class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)


class Post(models.Model):
    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(PostCategory, on_delete=models.SET_NULL, null=True, related_name="posts")
    tags = models.ManyToManyField(Tag, blank=True)
    excerpt = models.TextField(max_length=500)
    content = models.TextField()
    hero_image = models.ImageField(upload_to="blog/", blank=True)
    author = models.CharField(max_length=100, default="Naqqash Tea")
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def read_time(self):
        return max(1, len(self.content.split()) // 200)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

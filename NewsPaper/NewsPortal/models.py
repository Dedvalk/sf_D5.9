from django.contrib.auth.forms import UserCreationForm
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django import forms
from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group

article = 'A'
news = 'N'
TYPES = [
    (article, 'Статья'),
    (news, 'Новость')
]


class Author(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

    def update_rating(self):
        articles_rating = 0
        news_rating = 0
        comments_rating = 0
        post_keys = self.post_set.all()
        comment_keys = self.user.comment_set.all()
        for post in post_keys:
            articles_rating += post.rating*3
        for comment in comment_keys:
            news_rating += comment.rating
        for rate in Comment.objects.filter(post__in=post_keys).values('rating'):
            comments_rating += rate['rating']

        self.rating = articles_rating + news_rating + comments_rating
        self.save()


class Post(models.Model):

    title = models.CharField(max_length=255)
    content = models.TextField()
    type = models.CharField(max_length=1,
                            choices=TYPES,
                            default=news)
    creation_date = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)
    author = models.ForeignKey('Author', on_delete=models.CASCADE)
    categories = models.ManyToManyField('Category', through='PostCategory')

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        if len(self.content) > 124:
            return self.content[:125] + '...'
        else:
            return self.content

    def __str__(self):
        return f'{self.title.title()}: {self.content[:20]} by {self.author_id}'

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])


class Category(models.Model):

    name = models.CharField(max_length=255, unique=True)
    subscribers = models.ManyToManyField(User, through='CategorySubscriber')

    def __str__(self):
        return self.name.title()

class PostCategory(models.Model):

    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)

class CategorySubscriber(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)


class Comment(models.Model):

    content = models.TextField()
    creation_date = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()


class BaseRegisterForm(UserCreationForm):

    email = forms.EmailField(label = "Email")
    first_name = forms.CharField(label = "Имя")
    last_name = forms.CharField(label = "Фамилия")

    class Meta:
        model = User
        fields = ("username",
                  "first_name",
                  "last_name",
                  "email",
                  "password1",
                  "password2", )


class BasicSignupForm(SignupForm):

    def save(self, request):
        user = super(BasicSignupForm, self).save(request)
        basic_group = Group.objects.get(name='common')
        basic_group.user_set.add(user)
        return user

import os
import datetime

from celery import shared_task
import time

from NewsPortal.models import Post, Category
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

JUST_EMAIL = os.getenv('JUST_EMAIL')
JUST_ANOTHER_EMAIL = os.getenv('JUST_ANOTHER_EMAIL')
LOCAL_HOST = os.getenv('LOCALHOST')

def send():
    print('AAAAA!')

@shared_task
def post_creation_notify(id):

    post = Post.objects.get(pk=id)
    subscribers = []
    categories = post.categories.all()
    for category in categories:
        subs = category.subscribers.all()
        for sub in subs:
            subscribers.append(sub.email)

    html_content = render_to_string('post_created.html',
                                    {
                                        'post': post,
                                        'url': f'{LOCAL_HOST}/newsportal/{post.pk}'
                                    })

    msg = EmailMultiAlternatives(
        subject=f'{post.title}',
        body=post.content,
        from_email=JUST_ANOTHER_EMAIL,
        to=subscribers,
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()

@shared_task
def post_week_notify():

    week = datetime.datetime.now() - datetime.timedelta(days=7)

    categories = Category.objects.all()
    for category in categories:
        subscribers = category.subscribers.all()
        newposts = Post.objects.filter(creation_date__gte=week, categories=category)
        if len(newposts) > 0:
            for subscriber in subscribers:
                html_content = render_to_string(
                    'week_posts.html',
                    {
                        'username': subscriber.username,
                        'category': category.name,
                        'url': f'{LOCAL_HOST}/newsportal/',
                        'posts': newposts,
                    }
                )
                msg = EmailMultiAlternatives(
                    subject=f'NewsPortal: публикации за неделю',
                    body=f'Добрый день! За последнюю неделю вышли новые публикации из категории {category.name}.',
                    from_email=JUST_ANOTHER_EMAIL,
                    to=[subscriber.email]
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send()
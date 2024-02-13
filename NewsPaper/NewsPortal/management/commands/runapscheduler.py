import datetime
import logging
import os

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from NewsPortal.models import Post, Category

LOCAL_HOST = os.getenv('LOCALHOST')
JUST_ANOTHER_EMAIL = os.getenv('JUST_ANOTHER_EMAIL')

logger = logging.getLogger(__name__)


# наша задача по выводу текста на экран
def my_job():

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


# функция, которая будет удалять неактуальные задачи
def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # добавляем работу нашему задачнику
        scheduler.add_job(
            my_job,
            trigger=CronTrigger(
                #second="*/20"
                day_of_week="mon", hour="09", minute="00"
            ),
            # То же, что и интервал, но задача тригера таким образом более понятна django
            id="my_job",  # уникальный айди
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            # Каждую неделю будут удаляться старые задачи, которые либо не удалось выполнить, либо уже выполнять не надо.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
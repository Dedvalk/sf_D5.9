import os

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail, EmailMultiAlternatives
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView

from .forms import PostForm
from .models import Post, Author, BaseRegisterForm, Category, CategorySubscriber
from datetime import datetime, UTC
from .filters import PostFilter
from django.shortcuts import render


JUST_EMAIL = os.getenv('JUST_EMAIL')
JUST_ANOTHER_EMAIL = os.getenv('JUST_ANOTHER_EMAIL')
LOCAL_HOST = os.getenv('LOCALHOST')

class PostsList(ListView):

    model = Post
    ordering = '-creation_date'
    template_name = 'posts.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.now(UTC)
        context['next_post'] = None
        context['filterset'] = self.filterset
        context['posttype'] = self.request.path.split('/')[2]
        return context

    def get_queryset(self):

        type = self.request.path.split('/')[2]
        filter = {
            'news': 'N',
            'articles': 'A'
        }
        if type:
            queryset = Post.objects.filter(type=filter[type]).order_by('-creation_date')
        else:
            queryset = Post.objects.order_by('-creation_date')
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

class PostDetail(DetailView):

    model = Post
    template_name = 'post.html'
    context_object_name = 'post'


class PostSearch(ListView):

    model = Post
    template_name = 'post_search.html'
    ordering = '-creation_date'
    context_object_name = 'posts_search'
    paginate_by = 10

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context

    def get_queryset(self):

        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

class PostCreate(PermissionRequiredMixin, CreateView):

    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'
    permission_required = ('NewsPortal.add_post')

    def form_valid(self, form):

        post = form.save(commit=False)
        type = self.request.path.split('/')[2]
        post.author_id = Author.objects.filter(user=self.request.user.pk).first().pk
        if type == 'articles':
            post.type = 'A'
        elif type == 'news':
            post.type = 'N'

        response = super().form_valid(form)

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

        return response


class PostEdit(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):

    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'
    permission_required = ('NewsPortal.add_change')

    def get_queryset(self):

        type = self.request.path.split('/')[2]
        if type == 'articles':
            filter = 'A'
        else:
            filter = 'N'
        queryset = Post.objects.filter(type=filter)
        return queryset


class PostDelete(DeleteView):

    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('post_list')

    def get_queryset(self):

        type = self.request.path.split('/')[2]
        if type == 'articles':
            filter = 'A'
        else:
            filter = 'N'
        queryset = Post.objects.filter(type=filter)
        return queryset

@method_decorator(login_required, name='dispatch')
class ProtectedView(TemplateView):

    template_name = 'prodected_page.html'

class BaseRegisterView(CreateView):

    model = User
    form_class = BaseRegisterForm
    success_url = '/'

class IndexView(LoginRequiredMixin, TemplateView):

    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = CategorySubscriber.objects.filter(user=self.request.user)
        context['is_not_author'] = not self.request.user.groups.filter(name='authors').exists()
        return context

class CategoriesList(ListView):

    model = Category
    template_name = 'categories.html'
    context_object_name = 'categories'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #subscribed = Category.objects.filter(subscribers__user=self.request.user)
        categories = Category.objects.all()
        context['subscribed'] = []
        for category in categories:
            if category.subscribers.filter(id=self.request.user.id):
                context['subscribed'].append(category.pk)
        #context['is_subscribed'] = self.request.user not in self.category.subscribers.all()
        #context['category'] = self.category
        return context

# def create_post(request):
#     form = PostForm()
#     if request.method == 'POST':
#         form = PostForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return HttpResponseRedirect('/news/')
#
#     return render(request, 'post_edit.html', {'form': form })

@login_required
def upgrade_me(request):

    user = request.user
    author = Author()
    author_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        author_group.user_set.add(user)
        author.user = user
        author.rating = 0
        author.save()
    return redirect('/newsportal/index')

@login_required
def subscribe(request, category_id):

    cat_subs = CategorySubscriber()
    cat_subs.category = Category.objects.get(id=category_id)
    cat_subs.user = request.user
    cat_subs.save()

    send_mail(
        subject=f'NewsPortal: подписка на категорию',
        message=f'Добрый день!\nВы подписаны на категорию {cat_subs.category.name}!',
        from_email=JUST_ANOTHER_EMAIL,
        recipient_list=[request.user.email]
    )

    return redirect('/newsportal/categories')

@login_required
def unsubscribe(request, category_id):

    user = request.user
    category = Category.objects.get(id=category_id)
    cat_subs = CategorySubscriber.objects.filter(user=user, category_id=category_id)
    cat_subs.delete()

    send_mail(
        subject=f'NewsPortal: подписка на категорию',
        message=f'Добрый день!\nВы отписаны от категории {category.name}!',
        from_email=JUST_ANOTHER_EMAIL,
        recipient_list=[request.user.email]
    )

    return redirect('/newsportal/categories')







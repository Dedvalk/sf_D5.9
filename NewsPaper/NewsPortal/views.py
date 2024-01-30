from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .forms import PostForm
from .models import Post
from datetime import datetime, UTC
from .filters import PostFilter
from django.shortcuts import render

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
        return context

    def get_queryset(self):

        type = self.request.path.split('/')[2]
        if type == 'articles':
            filter = 'A'
        else:
            filter = 'N'
        queryset = Post.objects.filter(type=filter).order_by('-creation_date')
        #queryset = super().get_queryset()
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

class PostCreate(CreateView):

    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def form_valid(self, form):

        post = form.save(commit=False)
        type = self.request.path.split('/')[2]
        if type == 'articles':
            post.type = 'A'
        elif type == 'news':
            post.type = 'N'
        return super().form_valid(form)


class PostEdit(UpdateView):

    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'
    
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
        print(queryset)
        return queryset


# def create_post(request):
#     form = PostForm()
#     if request.method == 'POST':
#         form = PostForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return HttpResponseRedirect('/news/')
#
#     return render(request, 'post_edit.html', {'form': form })

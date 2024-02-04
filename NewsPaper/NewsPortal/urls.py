from django.urls import path, re_path
from .views import PostsList, PostDetail, PostCreate, PostEdit, PostDelete, PostSearch, BaseRegisterView, IndexView, \
    upgrade_me
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [

    path('<int:pk>', PostDetail.as_view(), name='post_detail'),
    path('index/', IndexView.as_view()),
    path('upgrade/', upgrade_me, name='upgrade'),
    path('', PostsList.as_view(), name='post_list'),
    re_path('news/search', PostSearch.as_view(), name='post_search'),
    re_path(r'(news|articles)/create', PostCreate.as_view(), name='post_create'),
    re_path(r'(news|articles)/(?P<pk>[0-9]{1,})/edit', PostEdit.as_view(), name='post_edit'),
    re_path(r'(news|articles)/(?P<pk>[0-9]{1,})/delete', PostDelete.as_view(), name='post_delete'),
    re_path(r'(news|articles)', PostsList.as_view(), name='post_list'),
    #path('login/', LoginView.as_view(template_name = 'login.html'), name='login'),
    #path('logout/', LogoutView.as_view(template_name = 'logout.html'), name='logout'),
    #path('signup/', BaseRegisterView.as_view(template_name = 'signup.html'), name='signup'),
    # path('create/', PostCreate.as_view(), name='post_create'),
    # path('search/', PostSearch.as_view(), name='post_search'),
    # path('<int:pk>/edit/', PostEdit.as_view(), name='post_edit'),
    # path('<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),


]
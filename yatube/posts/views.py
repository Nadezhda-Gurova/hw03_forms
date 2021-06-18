from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.core.paginator import Paginator

from .forms import PostForm
from .models import Group
from .models import Post
from .models import User


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'misc/index.html', {'page': page, })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group)
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "posts/group.html", {
        "group": group, "page": page,
    })


def profile(request, username):
    user = get_object_or_404(User, username=username)
    number_of_posts = Post.objects.filter(author_id=user.id).count()
    post_list = Post.objects.filter(author_id=user.id)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    if number_of_posts == 0:
        return render(request, 'misc/profile.html', {
            'number_of_posts': number_of_posts, 'user_profile': user,
            'page': page,
        })
    last_post = Post.objects.filter(author_id=user.id).latest('pub_date')
    last_post_text = last_post.text
    pub_date = last_post.pub_date
    return render(request, 'misc/profile.html', {
        'number_of_posts': number_of_posts, 'last_post_text': last_post_text,
        'latest_post_id': last_post.id, 'pub_date': pub_date,
        'page': page, 'user_profile': user,
    })


def post_view(request, username, post_id):
    user = get_object_or_404(User, username=username)
    full_name = f'{user.first_name} {user.last_name}'
    number_of_posts = Post.objects.filter(author_id=user.id).count()
    post = Post.objects.get(id=post_id)
    return render(request, 'posts/post.html', {
        'username': username, 'full_name': full_name,
        'number_of_posts': number_of_posts, 'posts': post
    })


@login_required
def new_post(request):
    if request.method == 'GET':
        form = PostForm()
        return render(request, 'posts/new.html', {'form': form, })
    elif request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post: Post = form.save(False)
            post.author = request.user
            post.save()
            return redirect('index')
        return render(request, 'posts/new.html', {'form': form})


@login_required
def post_edit(request, username, post_id):
    user = get_object_or_404(User, username=username)
    user_check_id = Post.objects.get(id=post_id).author.id
    if request.method == 'GET' and (request.user.id
                                    == user_check_id):
        post = Post.objects.get(id=post_id)
        form = PostForm(instance=post)
        return render(request, 'posts/new.html', {'form': form})
    elif request.method == 'POST' and (request.user.id
                                       == user_check_id):
        form = PostForm(request.POST)
        if form.is_valid():
            post: Post = form.save(False)
            post_to_edit = Post.objects.get(id=post_id)
            post_to_edit.text = post.text
            post_to_edit.group = post.group
            post_to_edit.save()
            return redirect('post_edit', username=username, post_id=post_id)
        return render(request, 'posts/new.html', {'form': form})
    return redirect('post_edit', username=user.username, post_id=post_id)

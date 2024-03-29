from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from django.contrib.postgres.search import SearchVector, TrigramSimilarity
from .models import Post, Comment
from .forms import EmailPostForm, CommentForm, SearchForm
from taggit.models import Tag


def post_list(request, tag_slug=None):
    """Получаем список опубликованных статей"""

    object_list = Post.published.all()
    tag = None
    # Фильтр статей по тегу
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        object_list = object_list.filter(tags__in=[tag])
    # Пагинация
    paginator = Paginator(object_list, 1)  # по 3 статьи на каждой странице
    # извлекаем из request GET-параметр page, который указывает текущую страницу (blog/?page=2)
    page = request.GET.get('page')  # int = 1 или 2 или 3 и тд.
    try:
        # Получаем список объектов на нужной странице
        # Покажи посты на странице Х, paginator знает, что на 1й странице 3 поста,
        # значит на 2й будут следующие 3 поста, т.е 4,5,6
        posts = paginator.page(page)
    except PageNotAnInteger:
        # Если страница не является целым числом, возвращаем первую страницу.
        # Если сработало исключение, покажи посты для первой страницы.
        posts = paginator.page(1)
    except EmptyPage:
        # Если номер страницы больше, чем общее количество страниц, возвращаем последнюю.
        posts = paginator.page(paginator.num_pages)
    return render(request, 'blog/post/list.html', {'page': page, 'posts': posts, 'tag': tag})


def post_detail(request, year, month, day, slug):
    """Получаем детальное отображение статьи"""

    post = get_object_or_404(Post, slug=slug, status='published', publish__year=year,
                             publish__month=month, publish__day=day)
    # Список активных комментариев для этой статьи.
    comments = post.comments.filter(active=True)  # post.comments. - это related_name в таблице Comment в поле post.
    new_comment = None
    if request.method == 'POST':
        # Пользователь отправил комментарий.
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Создаем комментарий, но пока не сохраняем в базе данных.
            new_comment = comment_form.save(commit=False)
            # Привязываем комментарий к текущей статье. Это просто ООП. Поменяли атрибут внутри экземпляра класса.
            new_comment.post = post
            # Сохраняем комментарий в базе данных.
            new_comment.save()
    else:  # если GET, отображаем пустую форму.
        comment_form = CommentForm()
    # Формирование списка похожих статей.
    post_tags_ids = post.tags.values_list('id', flat=True)  # получает все ID тегов текущей статьи.
    # получает все статьи, содержащие хоть один тег из полученных ранее, исключая текущую статью.
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    # использует функцию агрегации Count для формирования вычисляемого поля same_tags, которое содержит определенное
    # количество совпадающих тегов.
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]
    return render(request, 'blog/post/detail.html', {'post': post,
                                                     'comments': comments,
                                                     'new_comment': new_comment,
                                                     'comment_form': comment_form,
                                                     'similar_posts': similar_posts})


def post_share(request, post_id):
    """Получение данных формы и отправки их на почту, если они корректны"""

    # Получение статьи по идентификатору
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method == 'POST':
        # Форма была отправлена на сохранение.
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Все поля формы прошли валидацию.
            cd = form.cleaned_data  # dict
            # Отправка электронной почты.
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = '{}({}) recommends you reading "{}"'.format(cd['name'], cd['email'], post.title)
            message = 'Read "{}" at {}\n\n{}\'s comments:{}'.format(
                post.title, post_url, cd['name'], cd['comments']
            )
            send_mail(subject, message, cd['email'], [cd['to']])
            sent = True  # используем его в HTML-шаблоне share.html для изменения отображения шаблона.
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})


# def post_search(request):
#     """Обрабатывает поисковый запрос - Поиск по нескольким полям"""
#     form = SearchForm()
#     query = None
#     results = []
#     # Поисковый запрос будет отправляться методом GET,
#     # чтобы результирующий URL содержал в себе фразу поиска в параметре query.
#     if 'query' in request.GET:   # определяем, что форма отправлена (тут нет ошибок!)
#         form = SearchForm(request.GET)  # инициируем объект формы с параметрами из request.GET
#         if form.is_valid():
#             # Если форма валидна,формируем запрос на поиск статей с использованием
#             # объекта SearchVector по двум полям: title и body.
#             query = form.cleaned_data['query']
#             results = Post.objects.annotate(search=SearchVector('title', 'body')).filter(search=query)
#     return render(request, 'blog/post/search.html', {'form': form, 'query': query, 'results': results})

def post_search(request):
    """Обрабатывает поисковый запрос - Поиск по триграммам"""
    form = SearchForm()
    query = None
    results = []
    # Поисковый запрос будет отправляться методом GET,
    # чтобы результирующий URL содержал в себе фразу поиска в параметре query.
    if 'query' in request.GET:  # определяем, что форма отправлена (тут нет ошибок!)
        form = SearchForm(request.GET)  # инициируем объект формы с параметрами из request.GET
        if form.is_valid():
            # Если форма валидна,формируем запрос на поиск статей с использованием
            # объекта SearchVector по двум полям: title и body.
            query = form.cleaned_data['query']
            results = Post.objects.annotate(similarity=TrigramSimilarity('body', query)).filter(
                similarity__gt=0.01).order_by('-similarity')  # при similarity__gt=0.02 не работает.
    return render(request, 'blog/post/search.html', {'form': form, 'query': query, 'results': results})

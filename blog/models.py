from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from taggit.managers import TaggableManager


class PublishedManager(models.Manager):
    """Кастомный менеджер модели, который показывает только published посты"""

    def get_queryset(self):
        return super().get_queryset().filter(status='published')


class Post(models.Model):
    """Модель данных для статей блога"""
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published')
    )
    title = models.CharField(max_length=250)
    # Генерим уникальный url используя уникальный slug.
    # unique_for_date - нельзя создать слаг с одинаковым текстом в один и тот же день.
    slug = models.SlugField(max_length=250, unique_for_date='publish')
    # Связь one to many, каждый User может быть автором любого кол-ва статей.
    # Еще проще - один User - автор многих Post.
    # Cascade - при удалении пользователя, будут удалены связанные с ним статьи.
    # related_name - имя обратной связи от User к Post, чтобы получить доступ к связанным объектам автора
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    body = models.TextField()
    # дата публикации статьи
    publish = models.DateTimeField(default=timezone.now)
    # дата создания статьи. auto_now_add - дата будет сохраняться автоматически при создании объекта
    created = models.DateTimeField(auto_now_add=True)
    # auto_now - дата будет сохраняться автоматически при сохранении объекта.
    updated = models.DateTimeField(auto_now=True)
    # статус статьи
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    # Менеджеры моделей
    objects = models.Manager()  # Менеджер по умолчанию
    published = PublishedManager()  # Новый менеджер
    tags = TaggableManager()  # менеджер тэгов

    class Meta:
        ordering = ('-publish',)  # сортировка по убыванию, самые свежие статьи сверху.

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """
        Метод get_absolute_url() возвращает каноничный URL.

        Cтроим каноничный URL ипользуя URL post_detail (из blog/urls.py)
        Ф-я reverse() дает возможность получать URL, указав имя URL-шаблона и параметры.
        В шаблоне вызываем этот метод {{post.get_absolute_url}}, метод определяет URL-шаблон по name='post_detail',
        на основании URL-шаблона формирует url и возвращает его в HTML-шаблон при помощии ф-и reverse,
        подставляя url вместо записи {{post.get_absolute_url}}

        """
        return reverse('blog:post_detail', args=[self.publish.year, self.publish.month,
                                                 self.publish.day, self.slug])


class Comment(models.Model):
    """Комментирование блога"""
    # Атрибут related_name позволяет получить доступ к комментариям конкретной статьи.
    # Теперь мы сможем обращаться к статье из комментария, используя запись comment.post,
    # и к комментариям статьи при помощи post.comments.all()
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    # Создали поле created для сортировки комментариев в хронологическом порядке
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    # Добавили булевое поле active, для того чтобы была возможность скрыть
    # некоторые комментарии (например, содержащие оскорбления)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('-created',)  # самые новые комменты - сверху.

    def __str__(self):
        return 'Comment by {} on {}'.format(self.name, self.post)

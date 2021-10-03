from django.contrib import admin
from .models import Post, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # поля, которые будут отображены в админке
    list_display = ('title', 'slug', 'author', 'publish', 'status')
    # поля, по которым фильтруется таблица (справа на странице появился блок фильтрации)
    list_filter = ('status', 'created', 'publish', 'author')
    # Строка поиска. Поиск по полям title и body
    search_fields = ('title', 'body')
    # slug генерируется автоматически благодаря этому полю
    prepopulated_fields = {'slug': ('title',)}
    # Теперь при создании статьи поле автор содержит поле поиска
    raw_id_fields = ('author',)
    # Добавляет под строкой поиска ссылки для навигации по датам
    date_hierarchy = 'publish'
    ordering = ('status', 'publish')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'post', 'created', 'active')
    list_filter = ('active', 'created', 'updated')
    search_fields = ('name', 'email', 'body')

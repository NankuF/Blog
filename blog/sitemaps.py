from django.contrib.sitemaps import Sitemap
from .models import Post


class PostSitemap(Sitemap):
    changefreq = 'weekly'  # частота обновления страниц статей
    priority = 0.9  # степень совпадения статей с тематикой сайта (max = 1 )

    def items(self):
        """Возвращает Queryset объектов, которые будут отображаться в карте сайта"""
        return Post.published.all()

    def lastmod(self, obj):
        """Принимает каждый объект из результата вызова items() и
        возвращает время последней модификации статьи."""
        return obj.updated

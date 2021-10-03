from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords
from .models import Post


class LatestPostsFeed(Feed):
    title = 'My blog'
    link = '/blog/'
    description = 'New posts of my blog.'

    def items(self):
        """Метод получает объекты, которые будут включены в рассылку"""
        return Post.published.all()[:5]

    def item_title(self, item):
        """Для каждого объекта из результата items() получаем заголовок"""
        return item.title

    def item_description(self, item):
        """Для каждого объекта из результата items() получаем описание, ограниченное 30 словами"""
        return truncatewords(item.body, 30)

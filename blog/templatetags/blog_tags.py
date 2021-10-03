"""Мощь собственных шаблонных тегов заключается в том, что мы можем об-
рабатывать любые данные системы и добавлять их в шаблон при его форми-
ровании. Можно выполнять запросы в базу данных или вычислять какие-то
значения и отображать это в наших шаблонах."""

from django import template
from django.db.models import Count
from django.utils.safestring import mark_safe
import markdown

from ..models import Post

# используется для регистрации пользовательских тегов и фильтров в системе
register = template.Library()


# simple_tag – обрабатывает данные и возвращает строку;
# inclusion_tag – обрабатывает данные и возвращает сформированный фрагмент шаблона.


@register.simple_tag  # @register.simple_tag(name='my_tag') -так можно указать, как обращаться к тегу из шаблонов
def total_posts():  # текущее название тега для вызова из шаблонов
    """Шаблонный тег, возвращающий кол-во опубликованных в блоге статей."""
    return Post.published.count()


@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5):
    """Возвращает отсортированный список последних постов в кол-ве равном count"""
    latest_posts = Post.published.order_by('-publish')[:count]
    return {'latest_posts': latest_posts}


@register.simple_tag
def get_most_commented_posts(count=5):
    """В этом фрагменте кода мы формируем QuerySet, используя метод annotate()
        для добавления к каждой статье количества ее комментариев. Count использу-
        ется в качестве функции агрегации, которая вычисляет количество коммента-
        риев total_comments для каждого объекта Post. Также мы сортируем QuerySet по
        этому полю в порядке убывания. Как и в предыдущем примере, тег принима-
        ет дополнительный аргумент count, чтобы ограничить количество выводимых
        статей."""
    return Post.published.annotate(total_comments=Count('comments')).order_by('-total_comments')[:count]



@register.filter(name='markdown')
def markdown_format(text):
    """Мы используем функцию mark_safe, чтобы пометить результат работы
        фильтра как HTML-код, который нужно учитывать при построении шаблона.
        По умолчанию Django не доверяет любому HTML, получаемому из переменных
        контекста или фильтров. Единственное исключение – фрагменты, помеченные
        с помощью mark_safe. Это условие предотвращает отображение потенциально
        опасного HTML, но в то же время позволяет обработать код, которому вы до-
        веряете."""
    return mark_safe(markdown.markdown(text))


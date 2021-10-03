#Приложение "Блог", сделано по книге "Django 2 в примерах" Антонио Меле.

##Список фич:
- Список статей
- Детальное отображение статьи
- Формирование каноничного URL
- Пагинация
- Комментирование статьи
- Поделиться статьей по e-mail
- Тэги и фильтрация по тэгу
- Рекомендованные статьи

###Список статей
Чтобы отобразить список статей необходимо:
1. Модель
2. HTML-шаблон
3. URL-шаблон
4. View

####Принцип действия:
Cписок статей - это обыкновенная модель из бд, поля которой отображаются в HTML-шаблоне.
URL-шаблон используется, чтобы запустить вьюху, по которой будет генерироваться HTML-шаблон.

###Детальное отображение статьи
Для детального отображения статьи необходимо:
1. Model `Post`
2. Метод get_absolute_url в модели `Post`
3. HTMl-шаблон `detail.html`
4. URL-шаблон
5. View `post_detail`

####Принцип действия:
- Чтобы отобразить 1 статью из множества, необходимо использовать метод `get` менеджера контекста.
Однако чтобы отобразить 1 *опубликованную* статью, необходимо вначале изменить менеджер контекста с `objects` на 
`published` написав класс `PublishedManager` и создать поле в модели `Post` - `published = PublishedManager()`
- Необходимо сформировать каноничный URL, по которому мы будем переходить на страницу детального отображения статьи.
Для этого в модели `Post` определяем метод `get_absolute_url`, который формирует каноничный URL из полей модели 'Post':
`publish.year`, `publish.month`, `publish.day`, `slug`

###Формирование каноничного URL
Для формирования каноничного URL необходимо:
1. Модель `Post`
2. Метод `get_absolute_url` с ф-ей `reverse`
3. HTML-шаблон
4. URL-шаблон

####Принцип действия:
Создаем модель. Внутри модели создаем метод `get_absolute_url`. В методе используем ф-ю reverse(URL-шаблон, поля модели).
Прокидываем метод `get_absolute_url` в HTML-шаблон.
Ф-я `reverse` собирает URL по URL-шаблону используя переданные в нее поля модели.


###Пагинация
*Пагинация* - ограничивает кол-во отображаемых статей на странице, с возможностью листать вперед-назад.
![img.png](img.png) <br>

Чтобы сделать пагинацию необходимо в приложении blog создать:
1. Model `Post` 
2. Функция-обработчик (`post_list` in views)
3. HTML-шаблон для пагинации (`pagination.html`)
4. HTML-шаблон для списка, к которому применим пагинацию через {% include 'pagination.html' with post=posts %}

####Принцип действия:
- Берем список опубликованных статей `Post.publish.all()`, помещаем его в переменную `object_list` и 
передаем в класс `Paginator`, указав, сколько статей мы хотим отображать на странице - `Paginator(object_list,3)`.
- Определяем текущую страницу через request - `request.GET.get('page')`
(в словаре request есть словарь GET, в котором по ключу 'page' определяем номер страницы)
- Через `try except` определяем, когда все сработало нормально, то показываем те статьи,
которые соответствуют странице взятой из request `posts = paginator.page(page)`,
и описываем два исключения `EmptyList` - когда пользователь ввел страницу, которая больше максимальной страницы - 
перекидываем его на последнюю страницу `paginator.page(paginator.num_pages)`,
и `PageNotAnInteger` - когда пользователь ввел не число, то перекидываем его на первую страницу `paginator.page(1)`

###Комментирование статьи
Для реализации комментирования, нам понадобятся:
1. Model `Comment`
2. ModelForm `CommentForm`
3. HTML-шаблон в котором отображается детально статья и куда мы прокинем форму.
4. URL-шаблон, по которому будет формироваться view `post_detail`
5. View `post_detail`

####Принцип действия:
Чтобы комментирование статьи работало, нам нужна форма, в которой мы будем писать коммент. После отправки этой формы
сработает вьюха `post_detail` и комментарий будет отображен на странице через HTML-шаблон.
Используем `ModelForm`, чтобы поля подтянулись из `Model`, тип полей для формы указываем в `Model`.

###Поделиться статьей по e-mail
Для реализации данной фичи необходимо:
1. Настройки smtp-сервера в setting.py
2. View
3. HTML-шаблон `detail.html` - здесь разместим ссылку на форму.
4. HTML-шаблон `share.html` - здесь разместим саму форму отправки на e-mail.
5. URL-шаблон
6. Form

####Принцип действия:
- В Django есть свой `EMAIL_BACKEND`, он позволяет отправлять данные на e-mail.
- Прописываем `EMAIL_BACKEND` и настройки smtp-сервера в setting.py
- Создаем форму используя `forms.Form` (т.к нам не нужна модель для отправки статьи на e-mail).
- Создаем URL-шаблон `path('<int:post_id>/share/', views.post_share, name='post_share')` и вьюху `post_share`.
- Во вьюхе получаем queryset модели по id переданному на вход ф-и через URL-шаблон.
- Пишем стандартную логику для отправки письма используя `if request.method == 'POST'` и `is.valid()`
- Если данные валидны - собираем тело письма для ф-ии `sendmail`, которую мы импортируем из встроенного модуля
`django.core.mail` и отправляем письмо.
- Если данные не валидны - показываем пустую форму заново.

###Тэги
Для реализации системы тэгов необходимо:
1. Установить стороннее приложение django-taggit `pip install django-taggit`
2. Прописать приложение `taggit` в `INSTALLED_APPS`
3. Добавить в модель `Post` менеджер контекста `TaggableManager`
4. Сделать миграции
5. В админке появится строка Tags, в нее добавить теги для поста. ![img_1.png](img_1.png)
6. URL-шаблон c `slug:tag_slug`
7. HTML-шаблон `list.html` в котором п
8. View `post_list` с аргументом `tag_slug`

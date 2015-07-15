from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Article


def latest_news(request):
    news_posts = Article.objects.all().order_by('-sticky', '-created')

    paginator = Paginator(news_posts, 5)
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    context = {
        'posts': posts,
        'page_range': paginator.page_range,
    }

    return render(request, 'news/latest_news.html', context)


def post(request, article_id):
    article = get_object_or_404(Article, pk=article_id)

    return render(request, 'news/article.html', {'article': article})

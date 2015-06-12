from django.shortcuts import render, get_object_or_404
from django.views.decorators.cache import cache_page

from .models import Article

def latest_news(request):
    news_posts = Article.objects.all().order_by('-created')

    news_posts_ids = [o.id for o in news_posts if o.is_active()]
    news_posts = news_posts.filter(id__in=news_posts_ids)

    return render(request, 'news/latest_news.html', {'posts': news_posts})

def post(request, article_id):
    article = get_object_or_404(Article, pk=article_id)

    return render(request, 'news/article.html', {'article': article})

from django.shortcuts import render, get_object_or_404
from django.views.decorators.cache import cache_page

from .models import Article

@cache_page(60 * 60)
def latest_news(request):
    news_posts = Article.objects.all().order_by('-created')

    return render(request, 'news/latest_news.html', {'posts': news_posts})

def post(request, article_id):
    article = get_object_or_404(Article, pk=article_id)

    return render(request, 'news/article.html', {'article': article})

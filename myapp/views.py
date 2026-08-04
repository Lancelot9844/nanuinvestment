from django.shortcuts import render

from .models import Banner, Download, NewsActivity, Notice


def serialize_item(item):
    data = {
        "title": item.title,
        "description": item.description,
        "published_at": item.published_at.strftime("%d %b %Y"),
    }

    document = getattr(item, "document", None)
    if document:
        data["document_url"] = document.url

    image = getattr(item, "image", None)
    if image:
        data["image_url"] = image.url

    return data


def serialize_banner(banner):
    return {
        "title": banner.title,
        "image": banner.image.url,
    }


def home(request):
    site_content = {
        "banners": [serialize_banner(item) for item in Banner.objects.filter(is_active=True)[:10]],
        "news": [serialize_item(item) for item in NewsActivity.objects.filter(is_active=True)[:6]],
        "notices": [serialize_item(item) for item in Notice.objects.filter(is_active=True)[:6]],
        "downloads": [serialize_item(item) for item in Download.objects.filter(is_active=True)[:6]],
    }
    return render(request, "index_react.html", {"site_content": site_content})


def login_page(request):
    return render(request, "login.html")

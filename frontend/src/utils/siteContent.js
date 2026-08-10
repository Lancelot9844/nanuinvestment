import { fallbackContent } from '../data/siteData'

export function normalizeSiteContent(content = {}) {
  return {
    banners:
      Array.isArray(content.banners) && content.banners.length
        ? content.banners
        : fallbackContent.banners,

    news:
      Array.isArray(content.news) && content.news.length
        ? content.news
        : fallbackContent.news,

    notices:
      Array.isArray(content.notices) && content.notices.length
        ? content.notices
        : fallbackContent.notices,

    downloads:
      Array.isArray(content.downloads) && content.downloads.length
        ? content.downloads
        : fallbackContent.downloads,

    popup: content.popup || null,
  }
}

export function readSiteContent() {
  const node = document.getElementById('site-content')

  if (!node?.textContent) {
    return fallbackContent
  }

  try {
    return normalizeSiteContent(JSON.parse(node.textContent))
  } catch (error) {
    console.error('Failed to parse site content:', error)
    return fallbackContent
  }
}
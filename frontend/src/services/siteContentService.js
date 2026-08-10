import { normalizeSiteContent } from '../utils/siteContent'

export async function fetchSiteContent() {
  const response = await fetch('/api/site-content/')

  if (!response.ok) {
    throw new Error('Failed to load site content')
  }

  const data = await response.json()

  return normalizeSiteContent(data)
}
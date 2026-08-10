export function addSeoSchema() {
    const schema = {
      '@context': 'https://schema.org',
      '@type': 'LocalBusiness',
  
      name: 'Nanu Investment',
  
      description:
        'Saving and Credit Co-operative Society Ltd.',
  
      address: {
        '@type': 'PostalAddress',
        streetAddress: 'Barahathawa-12',
        addressLocality: 'Sarlahi',
        addressRegion: 'Sarlahi',
        addressCountry: 'NP',
      },
  
      telephone: '+977-9744360267',
  
      email: 'info@nanuinvestment.com',
  
      image:
        'https://nanuinvestment.com/static/logo.jpeg',
  
      url: 'https://nanuinvestment.com',
  
      areaServed: 'NP',
    }
  
    const script = document.createElement('script')
  
    script.type = 'application/ld+json'
  
    script.textContent =
      JSON.stringify(schema)
  
    document.head.appendChild(script)
  
    return () => {
      script.remove()
    }
  }
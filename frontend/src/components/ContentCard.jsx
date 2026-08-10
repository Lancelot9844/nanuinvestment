function ContentCard({ item, actionLabel }) {
    return (
      <article className="content-card">
  
        <div className="content-card-date">
          {item.published_at}
        </div>
  
        {item.image_url && (
          <img
            src={item.image_url}
            alt={item.title}
            className="content-card-image"
          />
        )}
  
        <h3>{item.title}</h3>
  
        {item.description && (
          <p>{item.description}</p>
        )}
  
        {item.document_url && (
          <a
            href={item.document_url}
            target="_blank"
            rel="noopener noreferrer"
            className="content-card-button"
          >
            {actionLabel}
          </a>
        )}
  
      </article>
    )
  }
  
  export default ContentCard
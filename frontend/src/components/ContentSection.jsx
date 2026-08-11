import ContentCard from "./ContentCard";

function ContentSection({ id, title, items, actionLabel, compact = false }) {
  return (
    <section
      className={`content-section ${compact ? "compact-section" : ""}`}
      id={id}
    >
      <div className="section-heading">
        <h2>{title}</h2>
      </div>

      <div className="content-grid">
        {items.map((item, index) => (
          <ContentCard
            key={`${item.title}-${item.published_at}-${index}`}
            item={item}
            actionLabel={actionLabel}
          />
        ))}
      </div>
    </section>
  );
}

export default ContentSection;

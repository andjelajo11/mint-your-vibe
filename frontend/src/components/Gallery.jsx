export default function Gallery({ items }) {
  return (
    <div className="gallery">
      <div className="gallery-header">
        <h3>Gallery</h3>
        <span>{items.length} minted</span>
      </div>

      {items.length === 0 ? (
        <p className="gallery-empty">Nothing minted yet — be the first.</p>
      ) : (
        <div className="gallery-grid">
          {items.map((item) => (
            <div className="gallery-item" key={item.id} title={item.metadata.name}>
              <img
                src={`data:image/png;base64,${item.image_base64}`}
                alt={item.metadata.name}
              />
              <span className="gallery-name">{item.metadata.name}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

import { useEffect, useState } from "react";
import "./Popup.css";

function Popup({ popup, onClose }) {
  const [pdfPreviewUrl, setPdfPreviewUrl] = useState("");
  const [pdfPreviewFailed, setPdfPreviewFailed] = useState(false);

  if (!popup) {
    return null;
  }

  const API_BASE_URL =
    import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

  const getMediaUrl = (url) => {
    if (!url) return "";

    // Already absolute
    if (url.startsWith("http://") || url.startsWith("https://")) {
      return url;
    }

    // Protocol-relative
    if (url.startsWith("//")) {
      return `${window.location.protocol}${url}`;
    }

    // Django /media/ or /static/
    if (url.startsWith("/")) {
      return `${API_BASE_URL}${url}`;
    }

    return `${API_BASE_URL}/${url}`;
  };

  const imageUrl = getMediaUrl(popup.image_url);
  const pdfUrl = getMediaUrl(popup.pdf_url);
  const documentUrl = getMediaUrl(popup.document_url);

  useEffect(() => {
    if (popup.file_type !== "pdf" || !pdfUrl) {
      return;
    }

    let cancelled = false;
    let objectUrl = "";

    const loadPdf = async () => {
      try {
        const response = await fetch(pdfUrl);

        if (!response.ok) {
          throw new Error(`PDF request failed: ${response.status}`);
        }

        const blob = await response.blob();

        objectUrl = URL.createObjectURL(
          new Blob([blob], {
            type: "application/pdf",
          })
        );

        if (!cancelled) {
          setPdfPreviewUrl(objectUrl);
          setPdfPreviewFailed(false);
        }
      } catch (error) {
        console.error("PDF preview failed:", error);

        if (!cancelled) {
          setPdfPreviewFailed(true);
          setPdfPreviewUrl("");
        }
      }
    };

    loadPdf();

    return () => {
      cancelled = true;

      if (objectUrl) {
        URL.revokeObjectURL(objectUrl);
      }
    };
  }, [popup.file_type, pdfUrl]);

  const handleBackdropClick = (event) => {
    if (event.target === event.currentTarget) {
      onClose();
    }
  };

  return (
    <div
      className="website-popup-backdrop"
      role="dialog"
      aria-modal="true"
      aria-labelledby="website-popup-title"
      onClick={handleBackdropClick}
    >
      <article
        className="website-popup"
        onClick={(event) => event.stopPropagation()}
      >
        {/* Close button */}
        <button
          type="button"
          className="website-popup-close"
          onClick={onClose}
          aria-label="Close popup"
        >
          &times;
        </button>

        {/* IMAGE */}
        {popup.file_type === "image" && imageUrl && (
          <div className="website-popup-media website-popup-image-wrapper">
            <img
              src={imageUrl}
              alt={popup.title || "Popup"}
              className="website-popup-image"
              onError={(event) => {
                console.error("Popup image failed to load:", imageUrl);

                event.currentTarget.style.display = "none";
              }}
            />
          </div>
        )}

        {/* PDF */}
        {popup.file_type === "pdf" && pdfUrl && (
          <div className="website-popup-media website-popup-pdf">
            {pdfPreviewUrl && !pdfPreviewFailed ? (
              <iframe
                src={pdfPreviewUrl}
                title={popup.title || "PDF Preview"}
                className="website-popup-pdf-frame"
              />
            ) : (
              <div className="website-popup-pdf-fallback">
                <strong>{popup.file_name || "PDF Notice"}</strong>

                <a href={pdfUrl} target="_blank" rel="noopener noreferrer">
                  Open PDF
                </a>
              </div>
            )}
          </div>
        )}

        {/* OTHER DOCUMENT */}
        {popup.file_type !== "image" &&
          popup.file_type !== "pdf" &&
          documentUrl && (
            <div className="website-popup-media website-popup-document">
              <strong>{popup.file_name || "Uploaded file"}</strong>

              <a href={documentUrl} target="_blank" rel="noopener noreferrer">
                Open uploaded file
              </a>
            </div>
          )}

        {/* TITLE */}
        {popup.title && (
          <div className="website-popup-content">
            <h2 id="website-popup-title">{popup.title}</h2>
          </div>
        )}
      </article>
    </div>
  );
}

export default Popup;

import { useEffect, useState } from 'react'

function PopupMedia({ popup }) {
  const [pdfPreviewUrl, setPdfPreviewUrl] = useState('')
  const [pdfPreviewFailed, setPdfPreviewFailed] = useState(false)

  useEffect(() => {
    if (
      popup.file_type !== 'pdf' ||
      !popup.pdf_url
    ) {
      return undefined
    }

    let ignore = false
    let objectUrl = ''

    async function loadPdfPreview() {
      try {
        const response = await fetch(popup.pdf_url)

        if (!response.ok) {
          throw new Error('PDF preview failed')
        }

        const blob = await response.blob()

        objectUrl = URL.createObjectURL(
          new Blob([blob], {
            type: 'application/pdf',
          })
        )

        if (!ignore) {
          setPdfPreviewUrl(objectUrl)
          setPdfPreviewFailed(false)
        }
      } catch {
        if (!ignore) {
          setPdfPreviewFailed(true)
        }
      }
    }

    loadPdfPreview()

    return () => {
      ignore = true

      if (objectUrl) {
        URL.revokeObjectURL(objectUrl)
      }
    }
  }, [popup.file_type, popup.pdf_url])

  if (
    popup.file_type === 'image' &&
    popup.image_url
  ) {
    return (
      <img
        src={popup.image_url}
        alt={popup.title || 'Notice'}
        className="popup-image"
      />
    )
  }

  if (
    popup.file_type === 'pdf' &&
    popup.pdf_url
  ) {
    return (
      <div className="popup-pdf">

        {pdfPreviewUrl && !pdfPreviewFailed ? (
          <iframe
            src={pdfPreviewUrl}
            title={popup.title || 'PDF preview'}
            className="popup-pdf-preview"
          />
        ) : (
          <div className="popup-file-fallback">

            <p>
              {popup.file_name || 'PDF notice'}
            </p>

            <a
              href={popup.pdf_url}
              target="_blank"
              rel="noopener noreferrer"
            >
              Open PDF
            </a>

          </div>
        )}

      </div>
    )
  }

  if (popup.document_url) {
    return (
      <div className="popup-file-fallback">

        <p>
          {popup.file_name || 'Uploaded file'}
        </p>

        <a
          href={popup.document_url}
          target="_blank"
          rel="noopener noreferrer"
        >
          Open uploaded file
        </a>

      </div>
    )
  }

  return null
}

function Popup({ popup, onClose }) {
  if (!popup) {
    return null
  }

  return (
    <div
      className="website-popup-overlay"
      onClick={onClose}
    >
      <article
        className="website-popup"
        onClick={(event) =>
          event.stopPropagation()
        }
      >

        <button
          type="button"
          className="popup-close"
          onClick={onClose}
          aria-label="Close popup"
        >
          ×
        </button>

        <h2>{popup.title}</h2>

        {popup.description && (
          <p>{popup.description}</p>
        )}

        <PopupMedia popup={popup} />

      </article>
    </div>
  )
}

export default Popup
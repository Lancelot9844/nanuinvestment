import { useEffect, useState } from 'react'

function Slider({ slides }) {
  const [activeSlide, setActiveSlide] = useState(0)
  const [dragStartX, setDragStartX] = useState(null)

  useEffect(() => {
    if (!slides.length) {
      return undefined
    }

    const timer = window.setInterval(() => {
      setActiveSlide(
        (current) => (current + 1) % slides.length
      )
    }, 4000)

    return () => {
      window.clearInterval(timer)
    }
  }, [slides.length])

  useEffect(() => {
    if (activeSlide >= slides.length) {
      setActiveSlide(0)
    }
  }, [slides.length, activeSlide])

  const showPreviousSlide = () => {
    setActiveSlide(
      (current) =>
        (current - 1 + slides.length) % slides.length
    )
  }

  const showNextSlide = () => {
    setActiveSlide(
      (current) => (current + 1) % slides.length
    )
  }

  const handleSlideStart = (clientX) => {
    setDragStartX(clientX)
  }

  const handleSlideEnd = (clientX) => {
    if (dragStartX === null) {
      return
    }

    const distance = clientX - dragStartX
    const minimumSwipeDistance = 50

    if (Math.abs(distance) >= minimumSwipeDistance) {
      if (distance > 0) {
        showPreviousSlide()
      } else {
        showNextSlide()
      }
    }

    setDragStartX(null)
  }

  if (!slides.length) {
    return null
  }

  const currentSlide = slides[activeSlide]

  return (
    <section
      className="slider-container"
      aria-label="Nanu Investment highlights"
    >
      <div
        className="slides"
        onMouseDown={(event) =>
          handleSlideStart(event.clientX)
        }
        onMouseUp={(event) =>
          handleSlideEnd(event.clientX)
        }
        onMouseLeave={() => setDragStartX(null)}
        onTouchStart={(event) =>
          handleSlideStart(event.touches[0].clientX)
        }
        onTouchEnd={(event) =>
          handleSlideEnd(event.changedTouches[0].clientX)
        }
      >
        <div className="slide active">
          <img
            src={currentSlide.image}
            alt={currentSlide.title}
            className="img-fluid w-100"
          />
        </div>
      </div>

      <div className="slider-dots">
        {slides.map((slide, index) => (
          <button
            key={`${slide.title}-${index}`}
            className={
              index === activeSlide
                ? 'dot active'
                : 'dot'
            }
            onClick={() => setActiveSlide(index)}
            aria-label={`Show ${slide.title}`}
            type="button"
          />
        ))}
      </div>
    </section>
  )
}

export default Slider
import { useState } from 'react'

function ContactForm() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    message: '',
  })

  const [formStatus, setFormStatus] = useState('')

  const handleFormChange = (event) => {
    const { name, value } = event.target

    setFormData((previous) => ({
      ...previous,
      [name]: value,
    }))
  }

  const handleFormSubmit = async (event) => {
    event.preventDefault()

    setFormStatus('Sending...')

    try {
      const response = await fetch(
        'https://api.web3forms.com/submit',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            access_key:
              import.meta.env.VITE_WEB3FORMS_ACCESS_KEY,

            subject:
              'New Contact Inquiry from Nanu Investment',

            name: formData.name,
            email: formData.email,
            phone: formData.phone,
            message: formData.message,
          }),
        }
      )

      const data = await response.json()

      if (data.success) {
        setFormStatus(
          'Message sent successfully.'
        )

        setFormData({
          name: '',
          email: '',
          phone: '',
          message: '',
        })

        setTimeout(() => {
          setFormStatus('')
        }, 3000)
      } else {
        setFormStatus(
          'Error sending message. Please try again.'
        )
      }
    } catch {
      setFormStatus(
        'Error sending message. Please try again.'
      )
    }
  }

  return (
    <form
      onSubmit={handleFormSubmit}
      className="contact-form"
    >
      <input
        type="text"
        className="form-control"
        name="name"
        placeholder="Your name"
        value={formData.name}
        onChange={handleFormChange}
        required
      />

      <input
        type="email"
        className="form-control"
        name="email"
        placeholder="Your email"
        value={formData.email}
        onChange={handleFormChange}
        required
      />

      <input
        type="tel"
        className="form-control"
        name="phone"
        placeholder="Your phone number"
        value={formData.phone}
        onChange={handleFormChange}
        required
      />

      <textarea
        className="form-control"
        name="message"
        rows="4"
        placeholder="Your message"
        value={formData.message}
        onChange={handleFormChange}
        required
      />

      <button
        type="submit"
        className="btn btn-custom w-100"
      >
        Send Message
      </button>

      {formStatus && (
        <p
          className="form-message mt-2 text-center fw-bold"
          aria-live="polite"
        >
          {formStatus}
        </p>
      )}
    </form>
  )
}

export default ContactForm
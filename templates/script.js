const menuToggle = document.querySelector('.menu-toggle');
const navLinks = document.querySelector('.nav-links');

if (menuToggle && navLinks) {
  menuToggle.addEventListener('click', () => {
    navLinks.classList.toggle('active');
  });
}

const slides = document.querySelectorAll('.slide');
const nextBtn = document.querySelector('.next-btn');
const prevBtn = document.querySelector('.prev-btn');
const dots = document.querySelectorAll('.dot');
let currentSlide = 0;
let slideInterval;

if (slides.length > 0) {
  function showSlide(index) {
    slides.forEach((slide, i) => {
      slide.classList.remove('active');
      if (dots[i]) {
        dots[i].classList.remove('active');
      }
    });

    slides[index].classList.add('active');
    if (dots[index]) {
      dots[index].classList.add('active');
    }
    currentSlide = index;
  }

  function nextSlide() {
    let index = (currentSlide + 1) % slides.length;
    showSlide(index);
  }

  function prevSlideFunc() {
    let index = (currentSlide - 1 + slides.length) % slides.length;
    showSlide(index);
  }

  if (nextBtn) {
    nextBtn.addEventListener('click', () => {
      nextSlide();
      resetTimer();
    });
  }

  if (prevBtn) {
    prevBtn.addEventListener('click', () => {
      prevSlideFunc();
      resetTimer();
    });
  }

  dots.forEach(dot => {
    dot.addEventListener('click', (e) => {
      let index = parseInt(e.target.getAttribute('data-slide'));
      showSlide(index);
      resetTimer();
    });
  });

  function startSlider() {
    slideInterval = setInterval(nextSlide, 4000);
  }

  function resetTimer() {
    clearInterval(slideInterval);
    startSlider();
  }

  startSlider();
}

const footerForm = document.getElementById('footer-contact-form');
const formMessage = document.querySelector('.form-message');

if (footerForm) {
  footerForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    const submitButton = footerForm.querySelector('.form-submit');
    const originalText = submitButton.textContent;

    submitButton.disabled = true;
    submitButton.textContent = 'Sending...';

    if (formMessage) {
      formMessage.textContent = '';
      formMessage.className = 'form-message';
    }

    try {
      const response = await fetch(footerForm.action, {
        method: footerForm.method,
        body: new FormData(footerForm),
        headers: {
          Accept: 'application/json'
        }
      });

      if (response.ok) {
        footerForm.reset();
        if (formMessage) {
          formMessage.textContent = 'Message sent successfully. Thank you!';
          formMessage.classList.add('success');
        }
      } else {
        throw new Error('Unable to send the message right now.');
      }
    } catch (error) {
      if (formMessage) {
        formMessage.textContent = 'Something went wrong. Please try again.';
        formMessage.classList.add('error');
      }
    } finally {
      submitButton.disabled = false;
      submitButton.textContent = originalText;
    }
  });
}
const menuToggle = document.querySelector('.menu-toggle');
const navLinks = document.querySelector('.nav-links');

// Toggles the 'active' class when the menu button is clicked
menuToggle.addEventListener('click', () => {
  navLinks.classList.toggle('active');
});

const slides = document.querySelectorAll('.slide');
const nextBtn = document.querySelector('.next-btn');
const prevBtn = document.querySelector('.prev-btn');
const dots = document.querySelectorAll('.dot');
let currentSlide = 0;
let slideInterval;

// Function to show a specific slide
function showSlide(index) {
  slides.forEach((slide, i) => {
    slide.classList.remove('active');
    dots[i].classList.remove('active');
  });
  
  slides[index].classList.add('active');
  dots[index].classList.add('active');
  currentSlide = index;
}

// Next slide logic
function nextSlide() {
  let index = (currentSlide + 1) % slides.length;
  showSlide(index);
}

// Previous slide logic
function prevSlideFunc() {
  let index = (currentSlide - 1 + slides.length) % slides.length;
  showSlide(index);
}

// Event listeners for arrows
nextBtn.addEventListener('click', () => {
  nextSlide();
  resetTimer();
});

prevBtn.addEventListener('click', () => {
  prevSlideFunc();
  resetTimer();
});

// Event listeners for dots
dots.forEach(dot => {
  dot.addEventListener('click', (e) => {
    let index = parseInt(e.target.getAttribute('data-slide'));
    showSlide(index);
    resetTimer();
  });
});

// Auto slide every 4 seconds
function startSlider() {
  slideInterval = setInterval(nextSlide, 4000);
}

function resetTimer() {
  clearInterval(slideInterval);
  startSlider();
}

// Initialize automatic slideshow
startSlider();
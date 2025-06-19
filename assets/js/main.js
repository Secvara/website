import { FloatingCircles } from './circlesAnimation.js';

document.addEventListener('DOMContentLoaded', () => {
  // UI handlers for header/menu
  const menu = document.querySelector('.menu');
  const menuToggler = document.querySelector('.menu-toggler');
  const header = document.querySelector('header');

  if (window.scrollY > 1) {
    header.classList.remove('py-5');
    header.classList.add('py-1', 'bg-light-alt', 'shadow');
  } else {
    header.classList.remove('py-1', 'bg-light-alt', 'shadow');
    header.classList.add('py-5'); 
  }

  window.addEventListener('scroll', () => {

    if (window.scrollY > 1) {
      header.classList.remove('py-5');
      header.classList.add('py-1', 'bg-light-alt', 'shadow');
    } else {
      header.classList.remove('py-1', 'bg-light-alt', 'shadow');
      header.classList.add('py-5');
    }
    if (!menu.classList.contains('translate-x-full')) {
      menu.classList.add('translate-x-full');
      menuToggler.children[0].classList.remove('rotate-45');
      menuToggler.children[0].classList.remove('translate-y-2');
      menuToggler.children[1].classList.remove('scale-0');
      menuToggler.children[2].classList.remove('-rotate-45');
      menuToggler.children[2].classList.remove('-translate-y-2');
    };
  });

  menuToggler.addEventListener('click', () => {
    menu.classList.toggle('translate-x-full');
    menuToggler.children[0].classList.toggle('rotate-45');
    menuToggler.children[0].classList.toggle('translate-y-2');
    menuToggler.children[1].classList.toggle('scale-0');
    menuToggler.children[2].classList.toggle('-rotate-45');
    menuToggler.children[2].classList.toggle('-translate-y-2');
  });

  // Start floating animation
  new FloatingCircles('#animation-container', '.circle', {
    speed: 2,
    easing: 'ease-in-out',
    delay: 1000
  });
});

import { FloatingCircles } from './circlesAnimation.js';

document.addEventListener('DOMContentLoaded', () => {
  // UI handlers for header/menu
  const menu = document.querySelector('.menu');
  const menuToggler = document.querySelector('.menu-toggler');
  const header = document.querySelector('header');
  const isInner = document.body.classList.contains('page-inner');

  const setHeaderState = () => {
    if (isInner || window.scrollY > 1) {
      header.classList.remove('py-5');
      header.classList.add('py-1', 'bg-light-alt', 'shadow');
    } else {
      header.classList.remove('py-1', 'bg-light-alt', 'shadow');
      header.classList.add('py-5');
    }
  };

  // Initial header state
  setHeaderState();

  window.addEventListener('scroll', () => {
    setHeaderState();
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

  // Alternate background blocks for inner page content
  if (isInner) {
    const content = document.querySelector('.content-body');
    if (content) {
      try {
        const nodes = Array.from(content.childNodes).filter(n => (
          n.nodeType === 1 || (n.nodeType === 3 && n.textContent.trim().length)
        ));

        // Split into segments by H2 headings (like sections)
        const segments = [];
        let current = [];
        nodes.forEach(n => {
          if (n.nodeType === 1 && n.matches('h2')) {
            if (current.length) { segments.push(current); current = []; }
            current.push(n);
          } else {
            current.push(n);
          }
        });
        if (current.length) segments.push(current);

        if (segments.length) {
          const parent = content.parentNode;
          segments.forEach((seg, idx) => {
            const wrapper = document.createElement('div');
            wrapper.className = (idx % 2 === 0)
              ? 'bg-white py-8 rounded-lg'
              : 'bg-light-alt py-8 rounded-lg';
            const inner = document.createElement('div');
            inner.className = 'content-body';
            seg.forEach(node => inner.appendChild(node));
            wrapper.appendChild(inner);
            parent.insertBefore(wrapper, content);
          });
          content.remove();
        }
      } catch (e) {
        console.warn('Alt sections error', e);
      }
    }
  }
});

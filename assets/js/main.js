import { FloatingCircles } from './circlesAnimation.js';

document.addEventListener('DOMContentLoaded', () => {
  // UI handlers for header/menu
  const menu = document.querySelector('.menu');
  const menuToggler = document.querySelector('.menu-toggler');
  const header = document.querySelector('header');
  if (!header) return;
  const isInner = document.body.classList.contains('page-inner');
  const navLinks = document.querySelectorAll('header nav a');

  const setHeaderState = () => {
    const atTop = window.scrollY <= 1;
    if (!isInner && atTop) {
      header.classList.remove('bg-white', 'shadow', 'py-1');
      header.classList.add('bg-transparent', 'py-5');
      navLinks.forEach(a => { a.classList.remove('text-black'); a.classList.add('text-white'); });
    } else {
      header.classList.remove('bg-transparent', 'py-5');
      header.classList.add('bg-white', 'shadow', 'py-1');
      navLinks.forEach(a => { a.classList.remove('text-white'); a.classList.add('text-black'); });
    }
  };

  // Initial header state
  setHeaderState();

  window.addEventListener('scroll', () => {
    setHeaderState();
    if (menu && menuToggler && !menu.classList.contains('translate-x-full')) {
      menu.classList.add('translate-x-full');
      if (menuToggler.children[0]) menuToggler.children[0].classList.remove('rotate-45', 'translate-y-2');
      if (menuToggler.children[1]) menuToggler.children[1].classList.remove('scale-0');
      if (menuToggler.children[2]) menuToggler.children[2].classList.remove('-rotate-45', '-translate-y-2');
    }
  });

  if (menu && menuToggler) {
    menuToggler.addEventListener('click', () => {
      menu.classList.toggle('translate-x-full');
      const isOpen = !menu.classList.contains('translate-x-full');
      if (isOpen) {
        navLinks.forEach(a => { a.classList.remove('text-white'); a.classList.add('text-black'); });
      } else {
        setHeaderState();
      }
      if (menuToggler.children[0]) { menuToggler.children[0].classList.toggle('rotate-45'); menuToggler.children[0].classList.toggle('translate-y-2'); }
      if (menuToggler.children[1]) { menuToggler.children[1].classList.toggle('scale-0'); }
      if (menuToggler.children[2]) { menuToggler.children[2].classList.toggle('-rotate-45'); menuToggler.children[2].classList.toggle('-translate-y-2'); }
    });
  }

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

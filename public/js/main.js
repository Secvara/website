(() => {
  // ns-hugo-imp:D:\work\mudassir\secvara\assets\js\circlesAnimation.js
  var FloatingCircles = class {
    constructor(containerSelector, circleSelector, options = {}) {
      this.container = document.querySelector(containerSelector);
      this.circles = Array.from(this.container.querySelectorAll(circleSelector));
      this.options = {
        speed: options.speed || 0.5,
        easing: options.easing || "linear",
        delay: options.delay || 0,
        // NEW: Animation start delay (in ms)
        debug: options.debug || false,
        zones: options.zones || [
          [0.1, 0.1],
          // top-left
          [0.9, 0.1],
          // top-right
          [0.1, 0.9],
          // bottom-left
          [0.9, 0.9]
          // bottom-right
        ]
      };
      this.circleData = [];
      this.usedZones = /* @__PURE__ */ new Set();
      if (this.container && this.circles.length) {
        setTimeout(() => this.init(), 50);
      } else {
        console.warn("FloatingCircles: Container or circles not found.");
      }
    }
    init() {
      const containerRect = this.container.getBoundingClientRect();
      this.circleData = this.circles.map((circle, i) => {
        const zoneIndex = this.getZoneIndex(i);
        const [xf, yf] = this.options.zones[zoneIndex];
        const width = circle.offsetWidth;
        const height = circle.offsetHeight;
        const x = xf * (containerRect.width - width);
        const y = yf * (containerRect.height - height);
        circle.style.transform = `translate(${x}px, ${y}px)`;
        circle.style.transitionTimingFunction = this.options.easing;
        return {
          el: circle,
          x,
          y,
          vx: (Math.random() - 0.5) * this.options.speed,
          vy: (Math.random() - 0.5) * this.options.speed,
          width,
          height
        };
      });
      setTimeout(() => this.animate(), this.options.delay);
    }
    getZoneIndex(index) {
      const totalZones = this.options.zones.length;
      if (this.usedZones.size < totalZones) {
        let zone;
        do {
          zone = Math.floor(Math.random() * totalZones);
        } while (this.usedZones.has(zone));
        this.usedZones.add(zone);
        return zone;
      }
      return Math.floor(Math.random() * totalZones);
    }
    animate() {
      const containerRect = this.container.getBoundingClientRect();
      this.circleData.forEach((c) => {
        c.x += c.vx;
        c.y += c.vy;
        if (c.x <= 0 || c.x + c.width >= containerRect.width) c.vx *= -1;
        if (c.y <= 0 || c.y + c.height >= containerRect.height) c.vy *= -1;
        c.el.style.transform = `translate(${c.x}px, ${c.y}px)`;
      });
      requestAnimationFrame(() => this.animate());
    }
  };

  // <stdin>
  document.addEventListener("DOMContentLoaded", () => {
    const menu = document.querySelector(".menu");
    const menuToggler = document.querySelector(".menu-toggler");
    const header = document.querySelector("header");
    let scrolled;
    if (window.scrollY > 1) {
      header.classList.remove("py-5");
      header.classList.add("py-1", "bg-background", "shadow");
    } else {
      header.classList.remove("py-1", "bg-background", "shadow");
      header.classList.add("py-5");
    }
    window.addEventListener("scroll", function() {
      if (this.oldScroll < this.scrollY) {
        header.classList.add("-translate-y-full");
      } else {
        header.classList.remove("-translate-y-full");
      }
      this.oldScroll = this.scrollY;
      if (window.scrollY > 1) {
        header.classList.remove("py-5");
        header.classList.add("py-1", "bg-background", "shadow");
      } else {
        header.classList.remove("py-1", "bg-background", "shadow");
        header.classList.add("py-5");
      }
      if (!menu.classList.contains("translate-x-full")) {
        menu.classList.add("translate-x-full");
        menuToggler.children[0].classList.remove("rotate-45");
        menuToggler.children[0].classList.remove("translate-y-2");
        menuToggler.children[1].classList.remove("scale-0");
        menuToggler.children[2].classList.remove("-rotate-45");
        menuToggler.children[2].classList.remove("-translate-y-2");
      }
      ;
    });
    menuToggler.addEventListener("click", () => {
      menu.classList.toggle("translate-x-full");
      menuToggler.children[0].classList.toggle("rotate-45");
      menuToggler.children[0].classList.toggle("translate-y-2");
      menuToggler.children[1].classList.toggle("scale-0");
      menuToggler.children[2].classList.toggle("-rotate-45");
      menuToggler.children[2].classList.toggle("-translate-y-2");
    });
    new FloatingCircles("#animation-container", ".circle", {
      speed: 2,
      easing: "ease-in-out",
      delay: 1e3
    });
  });
})();

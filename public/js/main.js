(() => {
  // ns-hugo-imp:/home/pi/website/assets/js/circlesAnimation.js
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
    const isInner = document.body.classList.contains("page-inner");
    const setHeaderState = () => {
      if (isInner || window.scrollY > 1) {
        header.classList.remove("py-5");
        header.classList.add("py-1", "bg-light-alt", "shadow");
      } else {
        header.classList.remove("py-1", "bg-light-alt", "shadow");
        header.classList.add("py-5");
      }
    };
    setHeaderState();
    window.addEventListener("scroll", () => {
      setHeaderState();
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
    if (isInner) {
      const content = document.querySelector(".content-body");
      if (content) {
        try {
          const nodes = Array.from(content.childNodes).filter((n) => n.nodeType === 1 || n.nodeType === 3 && n.textContent.trim().length);
          const segments = [];
          let current = [];
          nodes.forEach((n) => {
            if (n.nodeType === 1 && n.matches("h2")) {
              if (current.length) {
                segments.push(current);
                current = [];
              }
              current.push(n);
            } else {
              current.push(n);
            }
          });
          if (current.length) segments.push(current);
          if (segments.length) {
            const parent = content.parentNode;
            segments.forEach((seg, idx) => {
              const wrapper = document.createElement("div");
              wrapper.className = idx % 2 === 0 ? "bg-white py-8 rounded-lg" : "bg-light-alt py-8 rounded-lg";
              const inner = document.createElement("div");
              inner.className = "content-body";
              seg.forEach((node) => inner.appendChild(node));
              wrapper.appendChild(inner);
              parent.insertBefore(wrapper, content);
            });
            content.remove();
          }
        } catch (e) {
          console.warn("Alt sections error", e);
        }
      }
    }
  });
})();

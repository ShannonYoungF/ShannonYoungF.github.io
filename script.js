const root = document.documentElement;
const themeButton = document.querySelector(".theme-button");
const menuButton = document.querySelector(".menu-button");
const nav = document.querySelector(".site-nav");
const header = document.querySelector(".site-header");
const languageSwitch = document.querySelector(".language-switch");

if (languageSwitch && window.location.pathname.endsWith("blog.html") && window.location.search) {
  const target = new URL(languageSwitch.href, window.location.href);
  target.search = window.location.search;
  languageSwitch.href = target.toString();
}

themeButton?.addEventListener("click", () => {
  const next = root.dataset.theme === "dark" ? "light" : "dark";
  root.dataset.theme = next;
  localStorage.setItem("site-theme", next);
});

menuButton?.addEventListener("click", () => {
  const open = menuButton.getAttribute("aria-expanded") === "true";
  menuButton.setAttribute("aria-expanded", String(!open));
  nav.classList.toggle("is-open", !open);
});

nav?.querySelectorAll("a").forEach((link) => {
  link.addEventListener("click", () => {
    menuButton?.setAttribute("aria-expanded", "false");
    nav.classList.remove("is-open");
  });
});

const updateHeader = () => header?.classList.toggle("is-scrolled", window.scrollY > 10);
updateHeader();
window.addEventListener("scroll", updateHeader, { passive: true });

const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add("is-visible");
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0 });

document.querySelectorAll(".reveal").forEach((element) => observer.observe(element));
document.querySelector("#year").textContent = new Date().getFullYear();

const filterButtons = [...document.querySelectorAll(".filter-button")];
const entryCards = [...document.querySelectorAll(".entry-card")];
const searchInput = document.querySelector("#post-search");
const emptyState = document.querySelector("#empty-state");

if (filterButtons.length && entryCards.length) {
  const params = new URLSearchParams(window.location.search);
  let activeCategory = params.get("category") || "all";
  if (!filterButtons.some((button) => button.dataset.filter === activeCategory)) activeCategory = "all";

  const applyFilters = () => {
    const query = searchInput?.value.trim().toLowerCase() || "";
    let visibleCount = 0;
    entryCards.forEach((card) => {
      const categoryMatch = activeCategory === "all" || card.dataset.category === activeCategory;
      const searchMatch = !query || card.dataset.search.includes(query);
      card.hidden = !(categoryMatch && searchMatch);
      if (!card.hidden) visibleCount += 1;
    });
    filterButtons.forEach((button) => button.classList.toggle("is-active", button.dataset.filter === activeCategory));
    if (emptyState) emptyState.hidden = visibleCount !== 0;
  };

  filterButtons.forEach((button) => {
    button.addEventListener("click", () => {
      activeCategory = button.dataset.filter;
      const nextUrl = activeCategory === "all" ? window.location.pathname : `?category=${activeCategory}`;
      history.replaceState(null, "", nextUrl);
      applyFilters();
    });
  });
  searchInput?.addEventListener("input", applyFilters);
  applyFilters();
}

const progress = document.querySelector("#reading-progress");
const articleBody = document.querySelector(".post-body");
if (progress && articleBody) {
  const updateProgress = () => {
    const start = articleBody.offsetTop;
    const distance = articleBody.offsetHeight - window.innerHeight;
    const value = distance <= 0 ? 1 : Math.min(1, Math.max(0, (window.scrollY - start) / distance));
    progress.style.width = `${value * 100}%`;
  };
  updateProgress();
  window.addEventListener("scroll", updateProgress, { passive: true });
  window.addEventListener("resize", updateProgress, { passive: true });
}

const canvas = document.querySelector("#constellation");
const context = canvas?.getContext("2d");
const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

if (canvas && context && !reduceMotion) {
  let points = [];
  let frame;
  let width = 0;
  let height = 0;

  const resize = () => {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
    context.setTransform(dpr, 0, 0, dpr, 0, 0);

    const count = Math.max(7, Math.min(15, Math.floor(width / 95)));
    points = Array.from({ length: count }, () => ({
      x: Math.random() * width,
      y: Math.random() * height,
      vx: (Math.random() - 0.5) * 0.16,
      vy: (Math.random() - 0.5) * 0.16,
      r: Math.random() * 1.5 + 0.8,
    }));
  };

  const draw = () => {
    context.clearRect(0, 0, width, height);
    const dark = root.dataset.theme === "dark";
    const dot = dark ? "140, 198, 181" : "41, 107, 93";

    points.forEach((point, index) => {
      point.x += point.vx;
      point.y += point.vy;
      if (point.x < -10 || point.x > width + 10) point.vx *= -1;
      if (point.y < -10 || point.y > height + 10) point.vy *= -1;

      context.beginPath();
      context.arc(point.x, point.y, point.r, 0, Math.PI * 2);
      context.fillStyle = `rgba(${dot}, .24)`;
      context.fill();

      points.slice(index + 1).forEach((other) => {
        const distance = Math.hypot(point.x - other.x, point.y - other.y);
        if (distance < 145) {
          context.beginPath();
          context.moveTo(point.x, point.y);
          context.lineTo(other.x, other.y);
          context.strokeStyle = `rgba(${dot}, ${0.075 * (1 - distance / 145)})`;
          context.lineWidth = 0.7;
          context.stroke();
        }
      });
    });

    frame = requestAnimationFrame(draw);
  };

  resize();
  draw();
  window.addEventListener("resize", resize, { passive: true });
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) cancelAnimationFrame(frame);
    else draw();
  });
}

/* The complete SVG and explanations are present before this enhancement runs. */
(() => {
  "use strict";
  const english = document.documentElement.lang.startsWith("en");
  const reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
  const labels = english ? {
    play: "Play 3 steps", resume: "Resume", pause: "Pause", full: "Full view · explore in 3 steps",
    step: n => `Step ${n} of 3`, reduced: "Reduced motion · use Next step", paused: " · paused"
  } : {
    play: "播放三步", resume: "继续播放", pause: "暂停", full: "全图 · 可分三步阅读",
    step: n => `第 ${n} / 3 步`, reduced: "已减少动态效果 · 请用下一步", paused: " · 已暂停"
  };
  const states = [];
  document.querySelectorAll(".formula-figure").forEach(figure => {
    const play = figure.querySelector("[data-ff-play]");
    const status = figure.querySelector("[data-ff-status]");
    const layers = figure.querySelectorAll("[data-ff-layer]");
    const steps = figure.querySelectorAll("[data-ff-step]");
    const terms = figure.querySelectorAll("[data-ff-term]");
    let current = -1;
    let running = false;
    let timer = null;
    let animationTimer = null;
    let animationFrame = null;

    const announce = () => {
      play.textContent = running ? labels.pause : current < 0 || current === 2 ? labels.play : labels.resume;
      play.setAttribute("aria-pressed", String(running));
      status.textContent = current < 0 ? labels.full : `${labels.step(current+1)}${running ? "" : labels.paused}`;
      if (reduced.matches && current >= 0) status.textContent = `${labels.step(current+1)} · ${labels.reduced}`;
    };
    const stop = () => {
      clearTimeout(timer);
      timer = null;
      running = false;
      clearTimeout(animationTimer);
      cancelAnimationFrame(animationFrame);
      figure.classList.remove("ff-animate");
      announce();
    };
    const render = (step, animate = false) => {
      clearTimeout(animationTimer);
      cancelAnimationFrame(animationFrame);
      figure.classList.remove("ff-animate");
      current = step;
      figure.classList.toggle("is-stepping", step >= 0);
      layers.forEach(layer => {
        layer.classList.toggle("is-current", Number(layer.dataset.ffLayer) === step);
        layer.classList.toggle("is-past", step >= 0 && Number(layer.dataset.ffLayer) < step);
      });
      steps.forEach(li => {
        const active = Number(li.dataset.ffStep) === step;
        li.classList.toggle("is-current", active);
        if (active) li.setAttribute("aria-current", "step");
        else li.removeAttribute("aria-current");
      });
      terms.forEach(term => term.classList.toggle("is-current", Number(term.dataset.ffTerm) === step));
      if (animate && !reduced.matches) {
        // Starting the class in a new frame also restarts a repeated manual step.
        animationFrame = requestAnimationFrame(() => {
          if (current !== step) return;
          figure.classList.add("ff-animate");
          animationTimer = setTimeout(() => figure.classList.remove("ff-animate"), 1250);
        });
      }
      announce();
    };
    const schedule = () => {
      timer = setTimeout(() => {
        if (!running) return;
        if (current === 2) { stop(); return; }
        render(current+1, true);
        schedule();
      }, 6500);
    };
    play.addEventListener("click", () => {
      if (running) { stop(); return; }
      if (reduced.matches) { render(current < 0 || current === 2 ? 0 : current); return; }
      running = true;
      render(current < 0 || current === 2 ? 0 : current, true);
      schedule();
    });
    figure.querySelector("[data-ff-next]").addEventListener("click", () => {
      stop();
      render((current+1)%3, true);
    });
    figure.querySelector("[data-ff-reset]").addEventListener("click", () => { stop(); render(-1); });
    figure.querySelector(".ff-controls").hidden = false;
    states.push({ stop });
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(entries => {
        if (!entries[0].isIntersecting) stop();
      }).observe(figure);
    }
    if ("ResizeObserver" in window) {
      const svg = figure.querySelector("svg");
      new ResizeObserver(entries => {
        const width = entries[0].contentRect.width;
        if (width > 0) svg.style.setProperty("--ff-label-size", `${Math.min(25, Math.max(13, 12*600/width))}px`);
      }).observe(svg);
    }
  });
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) states.forEach(state => state.stop());
  });
  reduced.addEventListener("change", () => states.forEach(state => state.stop()));
  window.addEventListener("beforeprint", () => states.forEach(state => state.stop()));
})();

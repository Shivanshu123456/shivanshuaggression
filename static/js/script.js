document.addEventListener("DOMContentLoaded", function () {
    // ✅ 1. Chart: Maintenance Reports Bar
    const maintenanceEl = document.getElementById('maintenanceChart');
    if (maintenanceEl) {
        const ctx = maintenanceEl.getContext('2d');
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Maintenance Reports',
                    data: [5, 8, 4, 7, 6, 9],
                    backgroundColor: [
                        '#3b82f6', '#60a5fa', '#93c5fd',
                        '#2563eb', '#1d4ed8', '#1e40af'
                    ],
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                animation: {
                    duration: 1000,
                    easing: 'easeInOutQuart'
                },
                plugins: {
                    legend: { position: 'top' },
                    tooltip: {
                        enabled: true,
                        callbacks: {
                            label: context => `Total: ${context.raw}`
                        }
                    },
                    title: {
                        display: true,
                        text: 'Monthly Maintenance Reports',
                        font: { size: 16 }
                    }
                },
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    }

    // ✅ 2. Chart: Operational Health Line
    const healthEl = document.getElementById('healthChart');
    if (healthEl) {
        const ctx2 = healthEl.getContext('2d');
        new Chart(ctx2, {
            type: 'line',
            data: {
                labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
                datasets: [{
                    label: 'Operational Health (%)',
                    data: [95, 97, 92, 98],
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.2)',
                    tension: 0.3,
                    fill: true,
                    pointBackgroundColor: '#059669',
                    pointBorderColor: '#047857',
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Weekly System Health Overview'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                },
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    }

    // ✅ 3–20: Theme Toggle (Dark/Light)
    const toggle = document.getElementById('darkModeToggle');
    if (toggle) {
        toggle.addEventListener('change', function () {
            document.body.classList.toggle('dark-mode', this.checked);
            localStorage.setItem('dark-mode', this.checked);
        });
        const saved = localStorage.getItem('dark-mode') === 'true';
        toggle.checked = saved;
        document.body.classList.toggle('dark-mode', saved);
    }

    // ✅ 21–30: Scroll to Top Button
    const scrollBtn = document.getElementById("scrollToTop");
    if (scrollBtn) {
        window.addEventListener("scroll", () => {
            scrollBtn.classList.toggle("hidden", window.scrollY < 200);
        });
        scrollBtn.addEventListener("click", () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // ✅ 31–40: Smooth Anchor Navigation
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener("click", e => {
            e.preventDefault();
            const target = document.querySelector(anchor.getAttribute("href"));
            if (target) target.scrollIntoView({ behavior: "smooth" });
        });
    });

    // ✅ 41–50: Flash Message Auto-Dismiss
    document.querySelectorAll(".alert").forEach(alert => {
        setTimeout(() => alert.classList.add("fade", "hidden"), 5000);
    });

    // ✅ 51–60: Spinner Loader Toggle Function
    window.toggleLoader = function (show = true) {
        const loader = document.getElementById("loading");
        if (loader) loader.classList.toggle("hidden", !show);
    };

    // ✅ 61–70: Image Lazy Loading Enhancement
    document.querySelectorAll("img").forEach(img => img.loading = "lazy");

    // ✅ 71–80: Add skip to content for a11y
    const skipLink = document.createElement('a');
    skipLink.href = "#main";
    skipLink.className = "sr-only focus:not-sr-only";
    skipLink.textContent = "Skip to content";
    document.body.prepend(skipLink);

    // ✅ 81–85: Keyboard Navigation Hint
    document.addEventListener('keydown', e => {
        if (e.altKey && e.key === 'd') {
            document.getElementById("darkModeToggle")?.focus();
        }
    });

    // ✅ 86–90: Live Clock in Footer
    const clock = document.getElementById('liveClock');
    if (clock) {
        setInterval(() => {
            const now = new Date();
            clock.textContent = now.toLocaleTimeString();
        }, 1000);
    }

    // ✅ 91–95: Tooltip Utility
    document.querySelectorAll("[data-tooltip]").forEach(el => {
        el.addEventListener("mouseenter", () => {
            const tooltip = document.createElement("div");
            tooltip.className = "tooltip";
            tooltip.textContent = el.dataset.tooltip;
            document.body.appendChild(tooltip);
            const rect = el.getBoundingClientRect();
            tooltip.style.top = `${rect.top + window.scrollY - 30}px`;
            tooltip.style.left = `${rect.left}px`;
        });
        el.addEventListener("mouseleave", () => {
            document.querySelectorAll(".tooltip").forEach(t => t.remove());
        });
    });

    // ✅ 96–100: Auto-focus First Input in Modal
    document.querySelectorAll(".modal").forEach(modal => {
        modal.addEventListener("shown.bs.modal", () => {
            modal.querySelector("input, textarea, select")?.focus();
        });
    });
});

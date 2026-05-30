document.addEventListener('DOMContentLoaded', () => {
    const themeToggle = document.getElementById('themeToggle');
    const html = document.documentElement;
    const icon = themeToggle?.querySelector('.toggle-icon');

    const savedTheme = localStorage.getItem('theme') || 'light';
    html.setAttribute('data-theme', savedTheme);
    if (icon) {
        icon.textContent = savedTheme === 'dark' ? '☀️' : '🌙';
    }

    themeToggle?.addEventListener('click', () => {
        const current = html.getAttribute('data-theme');
        const next = current === 'dark' ? 'light' : 'dark';
        html.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);
        if (icon) {
            icon.textContent = next === 'dark' ? '☀️' : '🌙';
        }
    });

    // Mobile Navbar Menu Toggle
    const navToggle = document.getElementById('navToggle');
    const navLinks = document.getElementById('navLinks');

    navToggle?.addEventListener('click', () => {
        navToggle.classList.toggle('open');
        navLinks?.classList.toggle('active');
    });

    // Close menu when clicking on any link
    const navLinksList = navLinks?.querySelectorAll('a');
    navLinksList?.forEach(link => {
        link.addEventListener('click', () => {
            navToggle?.classList.remove('open');
            navLinks?.classList.remove('active');
        });
    });

    const contactForm = document.getElementById('contactForm');
    contactForm?.addEventListener('submit', (e) => {
        e.preventDefault();
        const btn = contactForm.querySelector('button[type="submit"]');
        const original = btn.textContent;
        btn.textContent = '✅ Mensaje enviado';
        btn.disabled = true;
        contactForm.reset();
        setTimeout(() => {
            btn.textContent = original;
            btn.disabled = false;
        }, 3000);
    });

    // Scroll Spy: Highlight active menu item on scroll
    const sections = document.querySelectorAll('section[id]');
    const navAnchors = document.querySelectorAll('.nav-link-anchor');

    function highlightMenuItem() {
        const scrollPosition = window.scrollY || window.pageYOffset || document.documentElement.scrollTop;
        let current = '';

        sections.forEach(section => {
            const sectionTop = section.offsetTop - 120; // Account for fixed header height
            const sectionHeight = section.offsetHeight;
            if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
                current = section.getAttribute('id');
            }
        });

        // Fallback for top of page
        if (scrollPosition < 100) {
            current = 'inicio';
        }

        navAnchors.forEach(anchor => {
            anchor.classList.remove('active');
            if (anchor.getAttribute('href').endsWith('#' + current)) {
                anchor.classList.add('active');
            }
        });
    }

    window.addEventListener('scroll', highlightMenuItem);
    highlightMenuItem(); // Trigger once on load to highlight the current section

    const skillBars = document.querySelectorAll('.skill-bar-fill');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.width = entry.target.style.width;
            }
        });
    }, { threshold: 0.5 });

    skillBars.forEach(bar => observer.observe(bar));
});

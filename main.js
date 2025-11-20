(function () {
    const nav = document.querySelector('[data-nav]');
    const navToggle = document.querySelector('[data-nav-toggle]');
    const navClose = document.querySelector('[data-nav-close]');
    const navLinks = nav ? nav.querySelectorAll('a') : [];

    const setBodyScrollState = () => {
        const hasOpenModal = document.querySelector('.modal.is-open');
        const navIsOpen = nav?.classList.contains('is-open');
        document.body.classList.toggle('no-scroll', Boolean(hasOpenModal || navIsOpen));
    };

    const openModal = (modal) => {
        if (!modal) return;
        modal.classList.add('is-open');
        setBodyScrollState();
    };

    const closeModal = (modal) => {
        if (!modal) return;
        modal.classList.remove('is-open');
        setBodyScrollState();
    };

    const setNavState = (open) => {
        if (!nav) return;
        nav.classList.toggle('is-open', open);
        navToggle?.setAttribute('aria-expanded', String(open));
        setBodyScrollState();
    };

    navToggle?.addEventListener('click', () => {
        const isOpen = nav?.classList.contains('is-open');
        setNavState(!isOpen);
    });

    navClose?.addEventListener('click', () => setNavState(false));

    navLinks.forEach((link) =>
        link.addEventListener('click', () => setNavState(false))
    );

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            setNavState(false);
            document.querySelectorAll('.modal.is-open').forEach((modal) => {
                closeModal(modal);
            });
        }
    });

    document.querySelectorAll('[data-modal-target]').forEach((trigger) => {
        trigger.addEventListener('click', (event) => {
            event.preventDefault();
            const modalId = trigger.getAttribute('data-modal-target');
            const modal = document.getElementById(modalId);
            openModal(modal);
        });
    });

    document.querySelectorAll('.modal').forEach((modal) => {
        modal.addEventListener('click', (event) => {
            if (event.target === modal) {
                closeModal(modal);
            }
        });

        modal.querySelectorAll('[data-modal-close]').forEach((button) => {
            button.addEventListener('click', () => closeModal(modal));
        });
    });
})();


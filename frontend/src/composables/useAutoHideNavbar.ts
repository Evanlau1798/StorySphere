import { onMounted, onUnmounted } from 'vue';

export function useAutoHideNavbar() {
    let lastScrollY = 0;

    const handleNavbarScroll = () => {
        const currentScrollY = window.scrollY;

        // Logic:
        // Hide if scrolling down > 50px (to avoid jitter)
        // Show ONLY if at the very top (currentScrollY === 0)

        if (currentScrollY > lastScrollY && currentScrollY > 50) {
            document.body.classList.add('hide-navbar');
        } else if (currentScrollY === 0) {
            document.body.classList.remove('hide-navbar');
        }

        lastScrollY = currentScrollY;
    };

    onMounted(() => {
        window.addEventListener('scroll', handleNavbarScroll);
    });

    onUnmounted(() => {
        window.removeEventListener('scroll', handleNavbarScroll);
        document.body.classList.remove('hide-navbar'); // Ensure navbar is shown when leaving
    });
}

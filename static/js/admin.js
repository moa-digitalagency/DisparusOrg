document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileSidebar = document.getElementById('mobile-sidebar');
    const mobileSidebarContent = document.getElementById('mobile-sidebar-content');
    const mobileOverlay = document.getElementById('mobile-overlay');
    const closeMobileMenu = document.getElementById('close-mobile-menu');

    function openMobileMenu() {
        if (mobileSidebar) {
            mobileSidebar.classList.remove('hidden');
            setTimeout(() => {
                mobileSidebarContent.classList.remove('-translate-x-full');
            }, 10);
        }
    }

    function closeMobileMenuFn() {
        if (mobileSidebarContent) {
            mobileSidebarContent.classList.add('-translate-x-full');
            setTimeout(() => {
                mobileSidebar.classList.add('hidden');
            }, 300);
        }
    }

    if (mobileMenuBtn) mobileMenuBtn.addEventListener('click', openMobileMenu);
    if (mobileOverlay) mobileOverlay.addEventListener('click', closeMobileMenuFn);
    if (closeMobileMenu) closeMobileMenu.addEventListener('click', closeMobileMenuFn);
});

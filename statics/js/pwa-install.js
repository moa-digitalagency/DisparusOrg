(function() {
    let deferredPrompt;
    const isIos = () => {
        const userAgent = window.navigator.userAgent.toLowerCase();
        return /iphone|ipad|ipod/.test(userAgent);
    };
    const isInStandaloneMode = () =>
        (window.matchMedia && window.matchMedia('(display-mode: standalone)').matches) ||
        (window.navigator.standalone) ||
        document.referrer.includes('android-app://');

    // Pull to refresh logic for PWA
    function initPullToRefresh() {
        let ts;
        window.addEventListener('touchstart', function(e) {
            if (window.scrollY <= 5) {
                ts = e.touches[0].clientY;
            } else {
                ts = null;
            }
        }, {passive: true});

        window.addEventListener('touchend', function(e) {
            if (ts !== null) {
                let te = e.changedTouches[0].clientY;
                if (te - ts > 150) {
                    window.location.reload();
                }
            }
        }, {passive: true});
    }

    // Check if already installed
    if (isInStandaloneMode()) {
        console.log('App is already in standalone mode');
        initPullToRefresh();
        return;
    }

    // Check if user already dismissed it (persists across sessions)
    if (localStorage.getItem('pwa-dismissed')) {
        return;
    }

    // Check if already shown in this session (to avoid showing on every refresh)
    if (sessionStorage.getItem('pwa-prompt-shown')) {
        return;
    }

    // Android / Desktop
    window.addEventListener('beforeinstallprompt', (e) => {
        console.log('beforeinstallprompt fired');
        e.preventDefault();
        deferredPrompt = e;
        showInstallPromotion();
    });

    // iOS
    if (isIos()) {
        showIosInstallPromotion();
    }

    function showInstallPromotion() {
        const promotion = document.getElementById('pwa-install-promotion');
        const installBtn = document.getElementById('pwa-install-btn');
        if (promotion && installBtn) {
            promotion.classList.remove('hidden');
            sessionStorage.setItem('pwa-prompt-shown', 'true');

            installBtn.addEventListener('click', async () => {
                if (deferredPrompt) {
                    deferredPrompt.prompt();
                    const { outcome } = await deferredPrompt.userChoice;
                    console.log(`User response to the install prompt: ${outcome}`);
                    deferredPrompt = null;
                    promotion.classList.add('hidden');
                }
            });

            const closeBtn = document.getElementById('pwa-install-close');
            if (closeBtn) {
                closeBtn.addEventListener('click', () => {
                    promotion.classList.add('hidden');
                    localStorage.setItem('pwa-dismissed', 'true');
                });
            }
        }
    }

    function showIosInstallPromotion() {
        const iosBanner = document.getElementById('pwa-ios-banner');
        if (iosBanner) {
            iosBanner.classList.remove('hidden');
            sessionStorage.setItem('pwa-prompt-shown', 'true');
        }
    }

    // Dismiss logic for iOS banner
    const closeIosBtn = document.getElementById('pwa-ios-close');
    if (closeIosBtn) {
        closeIosBtn.addEventListener('click', () => {
            const iosBanner = document.getElementById('pwa-ios-banner');
            if (iosBanner) {
                iosBanner.classList.add('hidden');
                localStorage.setItem('pwa-dismissed', 'true');
            }
        });
    }
})();

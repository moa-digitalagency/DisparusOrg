(function() {
    let deferredPrompt;
    const isIos = () => {
        const userAgent = window.navigator.userAgent.toLowerCase();
        return /iphone|ipad|ipod/.test(userAgent);
    };
    const isInStandaloneMode = () => ('standalone' in window.navigator) && (window.navigator.standalone);

    // Check if already installed
    if (window.matchMedia('(display-mode: standalone)').matches || isInStandaloneMode()) {
        console.log('App is already in standalone mode');
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
        const installBtn = document.getElementById('pwa-install-btn');
        if (installBtn) {
            installBtn.classList.remove('hidden');
            installBtn.addEventListener('click', async () => {
                if (deferredPrompt) {
                    deferredPrompt.prompt();
                    const { outcome } = await deferredPrompt.userChoice;
                    console.log(`User response to the install prompt: ${outcome}`);
                    deferredPrompt = null;
                    installBtn.classList.add('hidden');
                }
            });
        }
    }

    function showIosInstallPromotion() {
        const iosBanner = document.getElementById('pwa-ios-banner');
        if (iosBanner) {
            // Check if user already dismissed it in this session
            if (!sessionStorage.getItem('pwa-ios-dismissed')) {
                iosBanner.classList.remove('hidden');
            }
        }
    }

    // Dismiss logic for iOS banner
    const closeIosBtn = document.getElementById('pwa-ios-close');
    if (closeIosBtn) {
        closeIosBtn.addEventListener('click', () => {
            const iosBanner = document.getElementById('pwa-ios-banner');
            if (iosBanner) {
                iosBanner.classList.add('hidden');
                sessionStorage.setItem('pwa-ios-dismissed', 'true');
            }
        });
    }
})();

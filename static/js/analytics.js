document.addEventListener('DOMContentLoaded', function() {
    const gaIdMeta = document.querySelector('meta[name="google-analytics-id"]');
    const gtmIdMeta = document.querySelector('meta[name="google-tag-manager-id"]');

    // Google Analytics
    if (gaIdMeta && gaIdMeta.content) {
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', gaIdMeta.content);

        // Load script
        const script = document.createElement('script');
        script.async = true;
        script.src = `https://www.googletagmanager.com/gtag/js?id=${gaIdMeta.content}`;
        document.head.appendChild(script);
    }

    // Google Tag Manager
    if (gtmIdMeta && gtmIdMeta.content) {
        (function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
        new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
        j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
        'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
        })(window,document,'script','dataLayer', gtmIdMeta.content);
    }
});

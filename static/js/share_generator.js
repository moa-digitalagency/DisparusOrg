/**
 * Nom de l'application : DISPARUS.ORG
 * Description : Générateur d'image pour partage social (Story)
 */

if (!CanvasRenderingContext2D.prototype.roundRect) {
    CanvasRenderingContext2D.prototype.roundRect = function (x, y, w, h, r) {
        if (w < 2 * r) r = w / 2;
        if (h < 2 * r) r = h / 2;
        this.beginPath();
        this.moveTo(x + r, y);
        this.arcTo(x + w, y, x + w, y + h, r);
        this.arcTo(x + w, y + h, x, y + h, r);
        this.arcTo(x, y + h, x, y, r);
        this.arcTo(x, y, x + w, y, r);
        this.closePath();
        return this;
    };
}

/**
 * Generates a social media story image (1080x1920) and triggers download.
 * @param {Object} data - The data object.
 * @param {string} data.photoUrl - URL of the photo.
 * @param {string} data.name - Name of the person.
 * @param {string} data.city - City and Country.
 * @param {string} data.status - Status (e.g., 'missing', 'found').
 * @param {string} data.appName - Name of the app (default: DISPARU.ORG).
 */
async function generateStoryImage(data) {
    const canvas = document.createElement('canvas');
    canvas.width = 1080;
    canvas.height = 1920;
    const ctx = canvas.getContext('2d');

    // Background Gradient (Red to Dark Red)
    const gradient = ctx.createLinearGradient(0, 0, 0, 1920);
    gradient.addColorStop(0, '#b91c1c'); // red-700
    gradient.addColorStop(1, '#7f1d1d'); // red-900
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, 1080, 1920);

    // Header: App Name
    ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
    ctx.font = 'bold 40px Inter, sans-serif'; // Fallback to sans-serif
    ctx.textAlign = 'center';
    ctx.fillText(data.appName || 'DISPARU.ORG', 540, 100);

    // Status Banner
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(100, 200, 880, 120);

    ctx.fillStyle = '#b91c1c';
    ctx.font = 'bold 80px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';

    let statusText = 'DISPARU';
    if (data.status === 'found' || data.status === 'found_alive') statusText = 'RETROUVÉ';
    else if (data.status === 'deceased' || data.status === 'found_deceased') statusText = 'DÉCÉDÉ';
    else if (data.status === 'seen') statusText = 'APERÇU';

    ctx.fillText(statusText, 540, 260);

    // Card Container
    const cardY = 380;
    const cardHeight = 1000;
    const cardWidth = 900;
    const cardX = (1080 - cardWidth) / 2;

    ctx.fillStyle = '#ffffff';
    ctx.fillRect(cardX, cardY, cardWidth, cardHeight);

    // Load Image
    const img = new Image();
    img.crossOrigin = "Anonymous";

    // Use a placeholder if no photo URL
    if (!data.photoUrl) {
        // Create a simple placeholder canvas as image source
        const pCanvas = document.createElement('canvas');
        pCanvas.width = 500;
        pCanvas.height = 500;
        const pCtx = pCanvas.getContext('2d');
        pCtx.fillStyle = '#e5e7eb';
        pCtx.fillRect(0, 0, 500, 500);
        img.src = pCanvas.toDataURL();
    } else {
        img.src = data.photoUrl;
    }

    try {
        await new Promise((resolve, reject) => {
            if (img.complete) resolve();
            img.onload = resolve;
            img.onerror = () => {
                console.warn('Failed to load image for canvas, using placeholder');
                // Fallback to placeholder color
                resolve();
            };
        });
    } catch (e) {
        console.error(e);
    }

    // Draw Image (Cover)
    const imgHeight = 800;
    const imgWidth = cardWidth;

    if (img.width > 0) {
        // Aspect Ratio Calculation (Cover)
        const scale = Math.max(imgWidth / img.width, imgHeight / img.height);
        const x = (imgWidth / scale - img.width) / 2;
        const y = (imgHeight / scale - img.height) / 2;

        ctx.save();
        ctx.beginPath();
        ctx.rect(cardX, cardY, imgWidth, imgHeight);
        ctx.clip();
        ctx.drawImage(img, (x * scale) + cardX, (y * scale) + cardY, img.width * scale, img.height * scale);
        ctx.restore();
    } else {
        ctx.fillStyle = '#e5e7eb';
        ctx.fillRect(cardX, cardY, imgWidth, imgHeight);
        ctx.fillStyle = '#9ca3af';
        ctx.font = '40px Inter, sans-serif';
        ctx.fillText('Photo non disponible', 540, cardY + imgHeight/2);
    }

    // Text Details below image
    ctx.fillStyle = '#1f2937'; // gray-800
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';

    // Name
    ctx.font = 'bold 60px Inter, sans-serif';
    ctx.fillText(data.name, 540, cardY + imgHeight + 40);

    // City
    ctx.fillStyle = '#4b5563'; // gray-600
    ctx.font = '50px Inter, sans-serif';
    ctx.fillText(data.city, 540, cardY + imgHeight + 120);

    // Call Button Simulation
    const btnY = 1500;
    const btnWidth = 600;
    const btnHeight = 120;
    const btnX = (1080 - btnWidth) / 2;

    ctx.save();
    ctx.fillStyle = '#ffffff';
    ctx.shadowColor = 'rgba(0, 0, 0, 0.3)';
    ctx.shadowBlur = 20;
    ctx.shadowOffsetY = 10;
    if (ctx.roundRect) {
        ctx.roundRect(btnX, btnY, btnWidth, btnHeight, 60);
    } else {
        ctx.rect(btnX, btnY, btnWidth, btnHeight); // Fallback
    }
    ctx.fill();
    ctx.restore();

    ctx.fillStyle = '#b91c1c';
    ctx.font = 'bold 50px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('APPELER / CONTACTER', 540, btnY + btnHeight/2);

    // Footer
    ctx.fillStyle = 'rgba(255, 255, 255, 0.6)';
    ctx.font = '30px Inter, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('Aidez-nous à les retrouver sur disparus.org', 540, 1800);

    // Export
    canvas.toBlob((blob) => {
        if (!blob) {
            console.error('Canvas to Blob failed');
            return;
        }
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `disparu-${data.name.replace(/\s+/g, '-').toLowerCase()}.png`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }, 'image/png');
}

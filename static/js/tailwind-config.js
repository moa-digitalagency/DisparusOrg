tailwind.config = {
    darkMode: 'class',
    theme: {
        extend: {
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
            },
            colors: {
                primary: {
                    DEFAULT: '#b91c1c',
                    dark: '#991b1b',
                    foreground: '#ffffff',
                },
            },
            screens: {
                'xs': '400px',
            },
        },
    },
}

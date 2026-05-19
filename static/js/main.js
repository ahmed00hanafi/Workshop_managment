document.addEventListener('DOMContentLoaded', function() {
    const toggleBtn = document.getElementById('theme-toggle');
    if (!toggleBtn) return;

    // قراءة الثيم من الكوكيز
    function getCookie(name) {
        let value = "; " + document.cookie;
        let parts = value.split("; " + name + "=");
        if (parts.length === 2) return parts.pop().split(";").shift();
    }

    function setTheme(theme) {
        document.body.classList.toggle('dark-mode', theme === 'dark');
        document.cookie = `theme=${theme}; path=/; max-age=${60*60*24*30}`;
    }

    let currentTheme = getCookie('theme') || 'light';
    setTheme(currentTheme);

    toggleBtn.addEventListener('click', () => {
        let newTheme = document.body.classList.contains('dark-mode') ? 'light' : 'dark';
        setTheme(newTheme);
    });
});
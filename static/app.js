document.addEventListener("DOMContentLoaded", () => {
    // 1. Theme Toggle Logic
    const themeToggleBtn = document.getElementById("theme-toggle-btn");
    const currentTheme = localStorage.getItem("theme") || "dark";
    
    // Apply initial theme
    document.documentElement.setAttribute("data-theme", currentTheme);
    updateThemeIcon(currentTheme);
    
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener("click", () => {
            let activeTheme = document.documentElement.getAttribute("data-theme");
            let newTheme = activeTheme === "dark" ? "light" : "dark";
            
            document.documentElement.setAttribute("data-theme", newTheme);
            localStorage.setItem("theme", newTheme);
            updateThemeIcon(newTheme);
        });
    }
    
    function updateThemeIcon(theme) {
        if (!themeToggleBtn) return;
        const icon = themeToggleBtn.querySelector("i");
        if (icon) {
            if (theme === "dark") {
                icon.className = "bi bi-sun-fill";
            } else {
                icon.className = "bi bi-moon-stars-fill";
            }
        }
    }
    
    // 2. Responsive Mobile Sidebar Toggle
    const sidebarToggleBtn = document.getElementById("sidebar-toggle");
    const sidebar = document.querySelector(".sidebar");
    
    if (sidebarToggleBtn && sidebar) {
        sidebarToggleBtn.addEventListener("click", () => {
            sidebar.classList.toggle("open");
        });
    }
    
    // Close sidebar on clicking outside in mobile view
    document.addEventListener("click", (e) => {
        if (sidebar && sidebar.classList.contains("open") && 
            !sidebar.contains(e.target) && 
            sidebarToggleBtn && !sidebarToggleBtn.contains(e.target)) {
            sidebar.classList.remove("open");
        }
    });
    
    // 3. Auto dismiss alert messages after 5 seconds
    setTimeout(() => {
        const alerts = document.querySelectorAll(".alert");
        alerts.forEach(alert => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
});

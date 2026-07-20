/* ==========================================================================
   FitFuel AI - Advanced Dark Mode Controller
   File: theme.js
   ========================================================================== */

(function() {
    // 1. Instant class application to prevent FOUT (Flash of Unstyled Theme)
    function applyThemeFromStorage() {
        const isDark = localStorage.getItem("pref-dark-mode") === "true";
        if (isDark) {
            document.documentElement.classList.add("dark-theme-mode");
            if (document.body) {
                document.body.classList.add("dark-theme-mode");
            }
        } else {
            document.documentElement.classList.remove("dark-theme-mode");
            if (document.body) {
                document.body.classList.remove("dark-theme-mode");
            }
        }
    }

    applyThemeFromStorage();

    // 2. DOM Ready Handler to setup toggle buttons and listeners
    document.addEventListener("DOMContentLoaded", function() {
        applyThemeFromStorage();

        const themeToggleBtn = document.getElementById("theme-toggle-btn");
        const settingsDarkModeCheckbox = document.getElementById("pref-dark-mode");

        // Function to sync UI elements (icon & checkbox) with current theme state
        function syncUIState(isDark) {
            // Sync navbar button icon
            if (themeToggleBtn) {
                const icon = themeToggleBtn.querySelector("i");
                if (icon) {
                    if (isDark) {
                        icon.className = "fa-solid fa-sun";
                        themeToggleBtn.setAttribute("title", "Switch to Light Mode");
                    } else {
                        icon.className = "fa-solid fa-moon";
                        themeToggleBtn.setAttribute("title", "Switch to Dark Mode");
                    }
                }
            }

            // Sync settings checkbox
            if (settingsDarkModeCheckbox) {
                settingsDarkModeCheckbox.checked = isDark;
            }
        }

        // Initialize UI state
        const initialDarkState = localStorage.getItem("pref-dark-mode") === "true";
        syncUIState(initialDarkState);

        // Toggle Theme Function
        function toggleTheme(targetState) {
            const isDark = targetState !== undefined ? targetState : !(localStorage.getItem("pref-dark-mode") === "true");
            
            if (isDark) {
                document.documentElement.classList.add("dark-theme-mode");
                document.body.classList.add("dark-theme-mode");
                localStorage.setItem("pref-dark-mode", "true");
            } else {
                document.documentElement.classList.remove("dark-theme-mode");
                document.body.classList.remove("dark-theme-mode");
                localStorage.setItem("pref-dark-mode", "false");
            }

            syncUIState(isDark);
        }

        // Add Click Listener to Header Toggle Button
        if (themeToggleBtn) {
            themeToggleBtn.addEventListener("click", function(e) {
                e.preventDefault();
                // Add rotation animation class
                this.style.transform = "rotate(360deg) scale(1.15)";
                setTimeout(() => {
                    this.style.transform = "";
                }, 400);

                toggleTheme();
            });
        }

        // Add Listener to Settings Checkbox if present
        if (settingsDarkModeCheckbox) {
            settingsDarkModeCheckbox.addEventListener("change", function() {
                toggleTheme(this.checked);
            });
        }
    });
})();

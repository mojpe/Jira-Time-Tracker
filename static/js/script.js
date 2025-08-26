document.addEventListener("DOMContentLoaded", function () {
    const dateRange = document.getElementById("date-range");
    const customDatePicker = document.getElementById("custom-date-picker");
    const startDate = document.getElementById("start_date");
    const endDate = document.getElementById("end_date");

    // Restore previous selection from localStorage
    const savedDateRange = localStorage.getItem("selectedDateRange");
    if (savedDateRange) {
        dateRange.value = savedDateRange;
        if (savedDateRange === "custom") {
            customDatePicker.style.display = "block";
            startDate.value = localStorage.getItem("startDate") || "";
            endDate.value = localStorage.getItem("endDate") || "";
        }
    }

    // Listen for changes in the dropdown and toggle the custom date picker
    dateRange.addEventListener("change", function () {
        localStorage.setItem("selectedDateRange", dateRange.value);
        customDatePicker.style.display = dateRange.value === "custom" ? "block" : "none";
    });

    // Save custom date range if selected
    startDate.addEventListener("change", () => localStorage.setItem("startDate", startDate.value));
    endDate.addEventListener("change", () => localStorage.setItem("endDate", endDate.value));

    // Handle expand/collapse icon rotation
    const expandableRows = document.querySelectorAll('.issue-row.expandable');
    
    expandableRows.forEach(row => {
        row.addEventListener('click', function() {
            const icon = this.querySelector('.expand-icon');
            const targetId = this.getAttribute('data-bs-target');
            const targetElements = document.querySelectorAll(targetId);
            
            // Check if any of the target elements are being shown
            const isExpanding = Array.from(targetElements).some(el => 
                !el.classList.contains('show')
            );
            
            if (icon) {
                if (isExpanding) {
                    icon.classList.add('expanded');
                } else {
                    icon.classList.remove('expanded');
                }
            }
        });
    });

    // Handle Bootstrap collapse events for more precise icon control
    document.addEventListener('shown.bs.collapse', function (e) {
        const collapseId = '.' + e.target.classList[1]; // Get the details-{issueKey} class
        const expandableRow = document.querySelector(`[data-bs-target="${collapseId}"]`);
        if (expandableRow) {
            const icon = expandableRow.querySelector('.expand-icon');
            if (icon) {
                icon.classList.add('expanded');
            }
        }
    });

    document.addEventListener('hidden.bs.collapse', function (e) {
        const collapseId = '.' + e.target.classList[1]; // Get the details-{issueKey} class
        const expandableRow = document.querySelector(`[data-bs-target="${collapseId}"]`);
        if (expandableRow) {
            const icon = expandableRow.querySelector('.expand-icon');
            if (icon) {
                icon.classList.remove('expanded');
            }
        }
    });
});

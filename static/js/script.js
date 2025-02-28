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

    // Listen for changes in the dropdown
    dateRange.addEventListener("change", function () {
        localStorage.setItem("selectedDateRange", dateRange.value);
        if (dateRange.value === "custom") {
            customDatePicker.style.display = "block";
        } else {
            customDatePicker.style.display = "none";
        }
    });

    // Save custom date range if selected
    startDate.addEventListener("change", function () {
        localStorage.setItem("startDate", startDate.value);
    });

    endDate.addEventListener("change", function () {
        localStorage.setItem("endDate", endDate.value);
    });

    document.querySelectorAll(".issue-row").forEach(row => {
        row.addEventListener("click", function () {
            const issueKey = this.getAttribute("data-issue");
            const detailsRows = document.querySelectorAll(`.details.${issueKey}`);
            const arrow = this.querySelector(".arrow");

            if (detailsRows.length > 0) {
                if (detailsRows[0].style.display === "none" || detailsRows[0].style.display === "") {
                    detailsRows.forEach(row => row.style.display = "table-row");
                    arrow.textContent = "▼"; // Open state
                } else {
                    detailsRows.forEach(row => row.style.display = "none");
                    arrow.textContent = "▶"; // Closed state
                }
            }
        });
    });
    
});



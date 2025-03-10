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
});

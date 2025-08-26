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

    // Search functionality
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const tableRows = document.querySelectorAll('.issue-row');
            
            tableRows.forEach(row => {
                const issueKey = row.getAttribute('data-issue') || '';
                if (issueKey.includes(searchTerm)) {
                    row.style.display = '';
                    // Also show detail rows if parent is visible
                    const detailRows = document.querySelectorAll(`.details-${issueKey.toUpperCase()}`);
                    detailRows.forEach(detailRow => {
                        detailRow.style.display = '';
                    });
                } else {
                    row.style.display = 'none';
                    // Hide detail rows if parent is hidden
                    const detailRows = document.querySelectorAll(`.details-${issueKey.toUpperCase()}`);
                    detailRows.forEach(detailRow => {
                        detailRow.style.display = 'none';
                    });
                }
            });
        });
    }
});

// Quick filter functionality
function quickFilter(range) {
    const dateRange = document.getElementById('date-range');
    if (dateRange) {
        dateRange.value = range;
        
        // Update button states
        document.querySelectorAll('.btn-group .btn').forEach(btn => {
            btn.classList.remove('active');
        });
        event.target.classList.add('active');
        
        // Submit form automatically
        const form = document.querySelector('form');
        if (form) {
            form.submit();
        }
    }
}

// CSV Export functionality
function exportToCSV() {
    const table = document.getElementById('issuesTable');
    if (!table) return;
    
    let csvContent = "data:text/csv;charset=utf-8,";
    
    // Add headers
    csvContent += "Issue Key,Time Spent,Date,Time of Day\n";
    
    // Get all visible rows (non-detail, non-collapsed)
    const rows = table.querySelectorAll('tbody tr:not(.collapse)');
    
    rows.forEach(row => {
        if (row.style.display !== 'none') {
            const cells = row.querySelectorAll('td');
            if (cells.length >= 2) {
                const issueKey = cells[0].textContent.trim().replace(/\s+/g, ' ');
                const timeSpent = cells[1].textContent.trim();
                
                // For expandable rows, also get detail data
                if (row.classList.contains('expandable')) {
                    const issueKeyClean = issueKey.split(' ')[0]; // Remove badge text
                    const detailRows = document.querySelectorAll(`.details-${issueKeyClean}`);
                    
                    detailRows.forEach(detailRow => {
                        const detailCells = detailRow.querySelectorAll('td');
                        if (detailCells.length >= 3) {
                            const detailIssue = detailCells[0].textContent.trim();
                            const detailTime = detailCells[1].textContent.trim();
                            const detailDate = detailCells[0].querySelector('small')?.textContent.trim() || '';
                            const detailTimeOfDay = detailCells[2].textContent.trim();
                            
                            csvContent += `"${detailIssue}","${detailTime}","${detailDate}","${detailTimeOfDay}"\n`;
                        }
                    });
                } else {
                    csvContent += `"${issueKey}","${timeSpent}",,\n`;
                }
            }
        }
    });
    
    // Download CSV
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    
    const today = new Date().toISOString().split('T')[0];
    link.setAttribute("download", `jira-time-log-${today}.csv`);
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Auto-refresh last updated time
function updateLastUpdatedTime() {
    const lastUpdatedElement = document.getElementById('lastUpdated');
    if (lastUpdatedElement) {
        const now = new Date();
        const timeString = now.toLocaleString();
        lastUpdatedElement.textContent = timeString;
    }
}

// Toggle date picker visibility
function toggleDatePicker() {
    const dateRange = document.getElementById('date-range');
    const customDatePicker = document.getElementById('custom-date-picker');
    
    if (dateRange && customDatePicker) {
        customDatePicker.style.display = dateRange.value === 'custom' ? 'block' : 'none';
    }
}

// Enhanced form submission with loading state
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> Loading...';
                submitBtn.disabled = true;
            }
            
            // Add loading class to table if it exists
            const table = document.getElementById('issuesTable');
            if (table) {
                table.classList.add('loading');
            }
        });
    }
});

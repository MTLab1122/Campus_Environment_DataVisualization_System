// Campus Environment Data Visualization System Client Utilities
document.addEventListener("DOMContentLoaded", () => {
  // 1. Auto-dismiss flash alerts with smooth fade
  const flashAlerts = document.querySelectorAll(".alert-dismissible");
  flashAlerts.forEach((alert) => {
    setTimeout(() => {
      try {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
      } catch (e) {
        alert.style.display = "none";
      }
    }, 6000);
  });

  // 2. Initialize live table instant search filter if input exists
  const searchInput = document.getElementById("tableSearchInput");
  if (searchInput) {
    searchInput.addEventListener("input", function () {
      const filter = this.value.toLowerCase().trim();
      const table = document.querySelector(".filter-target-table");
      if (!table) return;
      const rows = table.querySelectorAll("tbody tr");
      let visibleCount = 0;

      rows.forEach((row) => {
        // Skip empty placeholder row if any
        if (row.classList.contains("empty-placeholder-row")) return;
        const text = row.textContent.toLowerCase();
        const matches = text.includes(filter);
        row.style.display = matches ? "" : "none";
        if (matches) visibleCount++;
      });

      // Update badge count if element exists
      const countBadge = document.getElementById("searchResultCount");
      if (countBadge) {
        countBadge.textContent = `${visibleCount} visible`;
      }

      // Show/hide empty search state message
      const noResultsRow = document.getElementById("noSearchResultsRow");
      if (noResultsRow) {
        noResultsRow.style.display = visibleCount === 0 ? "" : "none";
      }
    });
  }

  // 3. Sensor status filter tabs
  const statusFilterBtns = document.querySelectorAll("[data-status-filter]");
  statusFilterBtns.forEach((btn) => {
    btn.addEventListener("click", function () {
      statusFilterBtns.forEach((b) => b.classList.remove("active", "btn-primary"));
      statusFilterBtns.forEach((b) => b.classList.add("btn-outline-secondary"));
      this.classList.remove("btn-outline-secondary");
      this.classList.add("active", "btn-primary");

      const targetStatus = this.getAttribute("data-status-filter").toLowerCase();
      const table = document.querySelector(".filter-target-table");
      if (!table) return;
      const rows = table.querySelectorAll("tbody tr");
      let visibleCount = 0;

      rows.forEach((row) => {
        if (row.classList.contains("empty-placeholder-row")) return;
        const rowStatus = (row.getAttribute("data-row-status") || "").toLowerCase();
        const matches = targetStatus === "all" || rowStatus === targetStatus;
        row.style.display = matches ? "" : "none";
        if (matches) visibleCount++;
      });

      const countBadge = document.getElementById("searchResultCount");
      if (countBadge) {
        countBadge.textContent = `${visibleCount} records`;
      }
    });
  });

  // 4. Form submission spinner on primary buttons
  const forms = document.querySelectorAll("form:not(.no-spin)");
  forms.forEach((form) => {
    form.addEventListener("submit", function () {
      const submitBtn = this.querySelector("button[type='submit']:not(.no-spin)");
      if (submitBtn && !submitBtn.disabled) {
        submitBtn.setAttribute("data-original-html", submitBtn.innerHTML);
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Processing...';
        // Auto-re-enable after 6 seconds in case of client-side abort
        setTimeout(() => {
          submitBtn.disabled = false;
          if (submitBtn.getAttribute("data-original-html")) {
            submitBtn.innerHTML = submitBtn.getAttribute("data-original-html");
          }
        }, 6000);
      }
    });
  });
});

// Helper: Toggle Password Visibility
function togglePasswordVisibility(inputId, buttonEl) {
  const input = document.getElementById(inputId);
  if (!input) return;
  const icon = buttonEl.querySelector("i");
  if (input.type === "password") {
    input.type = "text";
    if (icon) {
      icon.className = "bi bi-eye-slash text-primary";
    }
  } else {
    input.type = "password";
    if (icon) {
      icon.className = "bi bi-eye text-muted";
    }
  }
}

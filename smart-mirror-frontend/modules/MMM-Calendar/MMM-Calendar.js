Module.register("MMM-Calendar", {
  defaults: {
    mode: "fourWeeks",
    firstDayOfWeek: "Sunday",
    locale: "zh-CN"
  },

  start: function () {
    this.now = new Date();
    this.updateTimer = setInterval(() => {
      this.now = new Date();
      this.updateDom(300);
    }, 60 * 1000);
  },

  getStyles: function () {
    return ["MMM-Calendar.css"];
  },

  getWeekdayHeaders: function (locale) {
    const baseDate = new Date(2024, 0, 7); // Sunday
    return Array.from({ length: 7 }, (_, index) => {
      const date = new Date(baseDate);
      date.setDate(baseDate.getDate() + index);
      return date.toLocaleDateString(locale, { weekday: "short" });
    });
  },

  getMatrix: function (year, month, firstDayOfWeekIndex) {
    const firstDay = new Date(year, month, 1);
    const startOffset = (firstDay.getDay() - firstDayOfWeekIndex + 7) % 7;
    const startDate = new Date(year, month, 1 - startOffset);

    return Array.from({ length: 6 }, (_, week) =>
      Array.from({ length: 7 }, (_, day) => {
        const d = new Date(startDate);
        d.setDate(startDate.getDate() + week * 7 + day);
        return d;
      })
    );
  },

  getDom: function () {
    const wrapper = document.createElement("div");
    wrapper.className = "monthly-calendar";

    const locale = config.locale || this.config.locale || "zh-CN";
    const today = this.now;
    const year = today.getFullYear();
    const month = today.getMonth();

    const header = document.createElement("div");
    header.className = "monthly-calendar-title";
    header.textContent = today.toLocaleDateString(locale, { year: "numeric", month: "long" });
    wrapper.appendChild(header);

    const table = document.createElement("table");
    table.className = "monthly-calendar-table";

    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");
    this.getWeekdayHeaders(locale).forEach((name) => {
      const th = document.createElement("th");
      th.textContent = name;
      headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);

    const tbody = document.createElement("tbody");
    const matrix = this.getMatrix(year, month, 0);
    matrix.forEach((week) => {
      const tr = document.createElement("tr");
      week.forEach((d) => {
        const td = document.createElement("td");
        const inMonth = d.getMonth() === month;
        const isToday =
          d.getDate() === today.getDate() &&
          d.getMonth() === today.getMonth() &&
          d.getFullYear() === today.getFullYear();

        td.textContent = String(d.getDate());
        if (!inMonth) {
          td.classList.add("is-out");
        }
        if (isToday) {
          td.classList.add("is-today");
        }
        tr.appendChild(td);
      });
      tbody.appendChild(tr);
    });
    table.appendChild(tbody);

    wrapper.appendChild(table);
    return wrapper;
  },

  stop: function () {
    clearInterval(this.updateTimer);
  }
});


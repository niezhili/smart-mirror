Module.register("MMM-Calendar", {
  defaults: {
    mode: "fourWeeks",
    firstDayOfWeek: "Sunday",
    locale: "zh-CN"
  },

  start: function () {
    this.now = new Date();
    this.lastRenderDateKey = this.getDateKey(this.now);
    this.updateTimer = setInterval(() => {
      const latest = new Date();
      const nextDateKey = this.getDateKey(latest);
      this.now = latest;

      // 此处已重构，改为仅在跨天时重绘，避免每分钟整块日历重复渲染。
      if (nextDateKey !== this.lastRenderDateKey) {
        this.lastRenderDateKey = nextDateKey;
        this.updateDom(0);
      }
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

  getDateKey: function (date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
  },

  getFirstDayOfWeekIndex: function () {
    const mapping = {
      Sunday: 0,
      Monday: 1,
      Tuesday: 2,
      Wednesday: 3,
      Thursday: 4,
      Friday: 5,
      Saturday: 6
    };

    return mapping[this.config.firstDayOfWeek] ?? 0;
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

    const globalLocale = typeof config !== "undefined" ? config.locale : null;
    const locale = this.config.locale || globalLocale || "zh-CN";
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
    const matrix = this.getMatrix(year, month, this.getFirstDayOfWeekIndex());
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


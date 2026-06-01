Module.register("MMM-MonthCalendar", {
	defaults: {
		firstDayOfWeek: 0, // 0 = Sunday, 1 = Monday
		showWeekNumbers: false,
		highlightToday: true,
	},

	getStyles () {
		return ["MMM-MonthCalendar.css"];
	},

	start () {
		Log.info("MMM-MonthCalendar started");
		this.today = new Date();
		this.currentMonth = this.today.getMonth();
		this.currentYear = this.today.getFullYear();

		// Listen for language changes
		this.lang = config.language || "En-us";

		// Update every minute to keep "today" accurate
		setInterval(() => {
			const now = new Date();
			if (now.getDate() !== this.today.getDate()) {
				this.today = now;
				this.currentMonth = now.getMonth();
				this.currentYear = now.getFullYear();
				this.updateDom(0);
			}
		}, 60 * 1000);
	},

	notificationReceived (notification, payload) {
		if (notification === "LANGUAGE_CHANGED") {
			this.lang = payload.language;
			this.updateDom(0);
		}
	},

	getDom () {
		const wrapper = document.createElement("div");
		wrapper.className = "month-calendar-wrapper";

		const isChinese = this.lang === "Zh-cn";

		// Day-of-week headers
		const daysEn = ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"];
		const daysZh = ["日", "一", "二", "三", "四", "五", "六"];
		const dayLabels = isChinese ? daysZh : daysEn;

		const dowRow = document.createElement("div");
		dowRow.className = "dow-row";

		const startDay = this.config.firstDayOfWeek;
		for (let i = 0; i < 7; i++) {
			const idx = (startDay + i) % 7;
			const cell = document.createElement("div");
			cell.className = "dow-cell";
			cell.innerHTML = dayLabels[idx];

			if (idx === 0 || idx === 6) {
				cell.classList.add("weekend");
			}
			dowRow.appendChild(cell);
		}
		wrapper.appendChild(dowRow);

		// Build the day grid
		const grid = document.createElement("div");
		grid.className = "day-grid";

		const firstDay = new Date(this.currentYear, this.currentMonth, 1);
		let startOffset = firstDay.getDay() - startDay;
		if (startOffset < 0) startOffset += 7;

		const daysInMonth = new Date(this.currentYear, this.currentMonth + 1, 0).getDate();
		const daysInPrevMonth = new Date(this.currentYear, this.currentMonth, 0).getDate();

		const totalCells = Math.ceil((startOffset + daysInMonth) / 7) * 7;

		const todayStr = `${this.today.getFullYear()}-${this.today.getMonth()}-${this.today.getDate()}`;

		for (let i = 0; i < totalCells; i++) {
			const cell = document.createElement("div");
			cell.className = "day-cell";

			let dayNum;
			if (i < startOffset) {
				dayNum = daysInPrevMonth - startOffset + i + 1;
				cell.classList.add("other-month");
			} else if (i >= startOffset + daysInMonth) {
				dayNum = i - startOffset - daysInMonth + 1;
				cell.classList.add("other-month");
			} else {
				dayNum = i - startOffset + 1;
				const cellDate = `${this.currentYear}-${this.currentMonth}-${dayNum}`;
				if (cellDate === todayStr && this.config.highlightToday) {
					cell.classList.add("today");
				}
			}

			const dowIdx = (startDay + i) % 7;
			if (dowIdx === 0 || dowIdx === 6) {
				cell.classList.add("weekend");
			}

			cell.innerHTML = dayNum;
			grid.appendChild(cell);
		}

		wrapper.appendChild(grid);

		return wrapper;
	}
});

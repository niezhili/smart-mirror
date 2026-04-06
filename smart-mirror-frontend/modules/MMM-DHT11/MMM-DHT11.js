/**
 * Magic Mirror
 * Module: MMM-DHT11
 * 
 * By NTADI Marrion Joseph
 * MIT Licensed
 */

Module.register("MMM-DHT11", {
    // Default module configuration
    defaults: {
        updateInterval: 500, // Update every minute
        temperatureUnit: "C", // C or F
        sensorPin: 4, // GPIO pin (BCM numbering) connected to DHT11 data pin
        showHumidity: true,
        showTemperature: true,
        maxAgeSeconds: 10, 
        decimalPlaces: 1, 
        labelTemp: "",
        labelHumidity: ""
    },

    getTranslations: function() {
        return {
            en: "translations/en.json",
            "zh-cn": "translations/zh-cn.json"
        };
    },

    // Define required scripts
    getScripts: function() {
        return [];
    },

    // Define required styles
    getStyles: function() {
        return ["MMM-DHT11.css"];
    },

    // Override start method
    start: function() {
        Log.info("Starting module: " + this.name);
        
        this.temperature = null;
        this.humidity = null;
        this.lastUpdate = null;
        
        this.sendSocketNotification("DHT11_CONFIG", this.config);
        
        var self = this;
        setInterval(function() {
            self.sendSocketNotification("GET_DHT11_DATA", {});
        }, this.config.updateInterval);
    },

    // Override socket notification handler
    socketNotificationReceived: function(notification, payload) {
        if (notification === "DHT11_DATA") {
            this.temperature = payload.temperature;
            this.humidity = payload.humidity;
            this.lastUpdate = new Date();
            this.updateDom();
        }
    },

    // Override dom generator
    getDom: function() {
        var wrapper = document.createElement("div");
        wrapper.className = "dht11-container";

        // Check if we have data
        if (this.temperature === null || this.humidity === null) {
            wrapper.textContent = this.translate("WAITING_FOR_SENSOR", "Waiting for sensor data...");
            wrapper.className = "dimmed light small";
            return wrapper;
        }

        // Check for stale data
        var now = new Date();
        var dataAge = (now - this.lastUpdate) / 1000; // Age in seconds
        var isStale = dataAge > this.config.maxAgeSeconds;

        // Create temperature display
        // Temperature Display
        // Create temperature display
        if (this.config.showTemperature) {
            var tempWrapper = document.createElement("div");
            tempWrapper.className = "dht11-temp" + (isStale ? " dimmed" : "");
            tempWrapper.style.display = "flex";
            tempWrapper.style.alignItems = "center";
            tempWrapper.style.marginBottom = "8px"; // Add spacing between elements

            // Temperature icon
            var tempIcon = document.createElement("i");
            tempIcon.className = "fas fa-temperature-half";
            tempIcon.style.marginRight = "8px"; // Add spacing between icon and text
            tempIcon.style.fontSize = "1.2em"; // Slightly larger icon
            tempWrapper.appendChild(tempIcon);

            // Temperature value container
            var tempValueContainer = document.createElement("div");
            tempValueContainer.style.display = "flex";
            tempValueContainer.style.flexDirection = "column";
            
            // Temperature label
            var tempLabel = document.createElement("span");
            tempLabel.style.fontSize = "0.8em";
            tempLabel.style.opacity = "0.8";
            tempLabel.textContent = this.config.labelTemp || this.translate("INDOOR_TEMPERATURE", "Room Temperature");
            tempValueContainer.appendChild(tempLabel);

            // Temperature value
            var tempValue = document.createElement("span");
            tempValue.style.fontSize = "1.2em";
            tempValue.style.fontWeight = "500";
            var formattedTemp = this.temperature.toFixed(this.config.decimalPlaces);
            var tempUnit = "°" + this.config.temperatureUnit;

            // Set color based on temperature
            if (this.temperature >= 35) {
                tempValue.style.color = "#ff0000"; // Red for very hot (≥35°C)
                tempValue.style.fontWeight = "bold"
            } else if (this.temperature >= 30) {
                tempValue.style.color = "#ff4500"; // Orange-red for hot (30-34.9°C)
                tempValue.style.fontWeight = "bold"
            } else if (this.temperature >= 25) {
                tempValue.style.color = "#ffa500"; // Orange for warm (25-29.9°C)
                tempValue.style.fontWeight = "bold"
            } else if (this.temperature >= 20) {
                tempValue.style.color = "#ffff00"; // Yellow for mild (20-24.9°C)
                tempValue.style.fontWeight = "bold"
            } else if (this.temperature >= 15) {
                tempValue.style.color = "#90ee90"; // Light green for cool (15-19.9°C)
                tempValue.style.fontWeight = "bold"
            } else {
                tempValue.style.color = "#add8e6"; // Light blue for cold (<15°C)
                tempValue.style.fontWeight = "bold"
            }

            tempValue.textContent = formattedTemp + tempUnit;
            tempValueContainer.appendChild(tempValue);
            tempWrapper.appendChild(tempValueContainer);
            
            wrapper.appendChild(tempWrapper);
        }

        // Create humidity display
        if (this.config.showHumidity) {
            var humidityWrapper = document.createElement("div");
            humidityWrapper.className = "dht11-humidity" + (isStale ? " dimmed" : "");
            humidityWrapper.style.display = "flex";
            humidityWrapper.style.alignItems = "center";
            humidityWrapper.style.marginBottom = "8px"; // Add spacing between elements

            // Humidity icon
            var humidityIcon = document.createElement("i");
            humidityIcon.className = "fas fa-tint";
            humidityIcon.style.marginRight = "8px"; // Add spacing between icon and text
            humidityIcon.style.fontSize = "1.2em"; // Slightly larger icon
            humidityWrapper.appendChild(humidityIcon);

            // Humidity value container
            var humidityValueContainer = document.createElement("div");
            humidityValueContainer.style.display = "flex";
            humidityValueContainer.style.flexDirection = "column";
            
            // Humidity label
            var humidityLabel = document.createElement("span");
            humidityLabel.style.fontSize = "0.8em";
            humidityLabel.style.opacity = "0.8";
            humidityLabel.textContent = this.config.labelHumidity || this.translate("INDOOR_HUMIDITY", "Room Humidity");
            humidityValueContainer.appendChild(humidityLabel);

            // Humidity value
            var humidityValue = document.createElement("span");
            humidityValue.style.fontSize = "1.2em";
            humidityValue.style.fontWeight = "500";
            var formattedHumidity = this.humidity.toFixed(this.config.decimalPlaces);
            
            // Set color based on humidity levels
            if (this.humidity >= 80) {
                humidityValue.style.color = "#4169e1"; // Royal Blue (too humid)
                humidityValue.style.fontWeight = "bold"
            } else if (this.humidity >= 60) {
                humidityValue.style.color = "#32cd32"; // Lime Green (comfortable - upper range)
                humidityValue.style.fontWeight = "bold"
            } else if (this.humidity >= 40) {
                humidityValue.style.color = "#228b22"; // Forest Green (ideal range)
                humidityValue.style.fontWeight = "bold"
            } else if (this.humidity >= 30) {
                humidityValue.style.color = "#ffa500"; // Orange (dry)
                humidityValue.style.fontWeight = "bold"
            } else {
                humidityValue.style.color = "#ff4500"; // OrangeRed (too dry)
                humidityValue.style.fontWeight = "bold"
            }

            humidityValue.textContent = formattedHumidity + "%";
            humidityValueContainer.appendChild(humidityValue);
            humidityWrapper.appendChild(humidityValueContainer);
            
            wrapper.appendChild(humidityWrapper);
        }
        return wrapper;
    }
});

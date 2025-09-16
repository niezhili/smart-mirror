/**
 * Magic Mirror
 * Node Helper: MMM-DHT11
 * 
 * By NTADI Marrion Joseph
 * MIT Licensed
 */

const NodeHelper = require("node_helper");
const { exec } = require("child_process");
const sensor = require("node-dht-sensor");

module.exports = NodeHelper.create({
    start: function () {
        console.log("Starting node helper for: " + this.name);
        this.started = false;
        this.config = {
            sensorPin: 4,  // Default value
            temperatureUnit: "C"
        };
    },

    socketNotificationReceived: function (notification, payload) {
        if (notification === "DHT11_CONFIG") {
            this.config = payload;
            if (!this.started) {
                this.started = true;
                console.log("DHT11 sensor configured on GPIO pin " + this.config.sensorPin);
            }
        } else if (notification === "GET_DHT11_DATA") {
            this.readSensor();
        }
    },

    readSensor: function () {
        // Check if config is available
        if (!this.config) {
            console.log("DHT11 sensor config not yet received, using defaults");
            return;
        }

        const self = this;

        // Initialize the sensor
        // sensor.initialize({
        //     pin: this.config.sensorPin,
        //     type: 22  // DHT11 sensor
        // });

        if (!this.sensorInitialized) {
            sensor.initialize({ pin: this.config.sensorPin, type: 22 });
            this.sensorInitialized = true;
        }
        // sensor.read(11, this.config.sensorPin, callback);


        // Read data from sensor
        sensor.read(22, this.config.sensorPin, function (err, temperature, humidity) {
            if (err) {
                console.error("Error reading from DHT22 sensor:", err);
                return;
            }

            // Convert temperature if needed
            if (self.config.temperatureUnit === "F") {
                temperature = (temperature * 9 / 5) + 32;
            }

            // Send data to the front end
            self.sendSocketNotification("DHT11_DATA", {
                temperature: temperature,
                humidity: humidity
            });
        });
    }
});

const fs = require("node:fs");
const http = require("node:http");
const https = require("node:https");
const path = require("node:path");
const express = require("express");
const rateLimit = require("express-rate-limit"); // 替换 ipfilter
const helmet = require("helmet");
const socketio = require("socket.io");

const Log = require("logger");
const { cors, getConfig, getHtml, getVersion, getStartup, getEnvVars } = require("./server_functions");

/**
 * Server
 * @param {object} config The MM config
 * @class
 */
function Server(config) {
    const app = express();
    const port = process.env.MM_PORT || config.port;
    const serverSockets = new Set();
    let server = null;

    /**
     * Opens the server for incoming connections
     * @returns {Promise} A promise that is resolved when the server listens to connections
     */
    this.open = function () {
        return new Promise((resolve) => {
            if (config.useHttps) {
                const options = {
                    key: fs.readFileSync(config.httpsPrivateKey),
                    cert: fs.readFileSync(config.httpsCertificate)
                };
                server = https.Server(options, app);
            } else {
                server = http.Server(app);
            }
            const io = socketio(server, {
                cors: {
                    origin: /.*$/,
                    credentials: true
                },
                allowEIO3: true
            });

            server.on("connection", (socket) => {
                serverSockets.add(socket);
                socket.on("close", () => {
                    serverSockets.delete(socket);
                });
            });

            Log.log(`Starting server on port ${port} ... `);
            server.listen(port, config.address || "localhost");

            // 配置速率限制（替换 IP 白名单逻辑）
            // 从配置中获取速率限制参数，默认 15 分钟内最多 100 个请求
            const limiter = rateLimit({
                windowMs: config.rateLimitWindowMs || 15 * 60 * 1000, // 15分钟
                max: config.rateLimitMax || 100, // 每个IP的最大请求数
                standardHeaders: true, // 返回速率限制信息在 `RateLimit-*` 头中
                legacyHeaders: false, // 禁用 `X-RateLimit-*` 头
                message: {
                    status: 429,
                    message: "Too many requests from this IP, please try again later."
                },
                // 可选：如果需要保留白名单功能，可以添加skip选项
                skip: (req, res) => {
                    // 如果配置了ipWhitelist，允许白名单内的IP不受限制
                    if (config.ipWhitelist instanceof Array && config.ipWhitelist.length > 0) {
                        const clientIp = req.ip;
                        return config.ipWhitelist.includes(clientIp);
                    }
                    return false;
                }
            });

            // 应用速率限制中间件
            app.use(limiter);

            app.use(function (req, res, next) {
                res.header("Access-Control-Allow-Origin", "*");
                next();
            });

            app.use(helmet(config.httpHeaders));
            app.use("/js", express.static(__dirname));

            let directories = ["/config", "/css", "/fonts", "/modules", "/vendor", "/translations", "/tests/configs", "/tests/mocks"];
            for (const directory of directories) {
                app.use(directory, express.static(path.resolve(global.root_path + directory)));
            }

            app.get("/cors", async (req, res) => await cors(req, res));

            app.get("/version", (req, res) => getVersion(req, res));

            app.get("/config", (req, res) => getConfig(req, res));

            app.get("/startup", (req, res) => getStartup(req, res));

            app.get("/env", (req, res) => getEnvVars(req, res));

            app.get("/", (req, res) => getHtml(req, res));

            server.on("listening", () => {
                resolve({
                    app,
                    io
                });
            });
        });
    };

    /**
     * Closes the server and destroys all lingering connections to it.
     * @returns {Promise} A promise that resolves when server has successfully shut down
     */
    this.close = function () {
        return new Promise((resolve) => {
            for (const socket of serverSockets.values()) {
                socket.destroy();
            }
            server.close(resolve);
        });
    };
}

module.exports = Server;
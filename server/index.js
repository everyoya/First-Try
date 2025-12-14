/* eslint-disable no-console */
const express = require("express");
const path = require("path");
require("dotenv").config();

const app = express();
const port = process.env.PORT || 4000;
const dbUrl = process.env.DB_URL || "postgres://localhost:5432/app";
const storagePath = process.env.STORAGE_PATH || path.join(__dirname, "..", "storage");

app.get("/health", (_req, res) => {
  res.json({
    status: "ok",
    dbUrl,
    storagePath,
  });
});

app.use(express.static(path.join(__dirname, "..", "public")));

app.listen(port, () => {
  console.log(`Express server listening on http://localhost:${port}`);
});

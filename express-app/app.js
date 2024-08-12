const express = require('express');
const path = require('path');
const mysql = require('mysql');
const app = express();
require('dotenv').config();

// 設置模板引擎為 EJS
app.set('view engine', 'ejs');

// 設置靜態文件目錄
app.use(express.static(path.join(__dirname, 'public')));

// 設置 MySQL 連接
const db = mysql.createConnection({
    host: process.env.DB_HOST,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    database: process.env.DB_DATABASE
});

// 連接到 MySQL
db.connect(err => {
    if (err) {
        console.error('Error connecting to MySQL:', err);
        return;
    }
    console.log('Connected to MySQL');
});

// 路由
app.get('/', (req, res) => {
    res.render('index');
});

app.get('/search', (req, res) => {
    const { host_name, host_ip, system_type, level, log_time_start, log_time_end } = req.query;
    let query = 'SELECT * FROM log_data WHERE 1=1';
    
    if (host_name) {
        query += ` AND HOST_NAME LIKE '%${host_name}%'`;
    }
    if (host_ip) {
        query += ` AND HOST_IP LIKE '%${host_ip}%'`;
    }
    if (system_type) {
        query += ` AND SYSTEM_TYPE LIKE '%${system_type}%'`;
    }
    // if (level) {
    //     query += ` AND LEVEL = '${level}'`;
    // }
    if (level) {
        const levels = Array.isArray(level) ? level : [level];
        const levelsPlaceholder = levels.map(lvl => `'${lvl}'`).join(',');
        query += ` AND LEVEL IN (${levelsPlaceholder})`;
    }
    if (log_time_start && log_time_end) {
        query += ` AND LOG_TIME BETWEEN '${log_time_start}' AND '${log_time_end}'`;
    } else if (log_time_start) {
        query += ` AND LOG_TIME >= '${log_time_start}'`;
    } else if (log_time_end) {
        query += ` AND LOG_TIME <= '${log_time_end}'`;
    }
    
    db.query(query, (err, results) => {
        if (err) {
            console.error('Error executing query:', err);
            return res.status(500).send('Server Error');
        }
        res.json(results);
    });
});


// 啟動伺服器
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});


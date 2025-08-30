const express = require('express');
const cors = require('cors');
const mysql = require('mysql2/promise');
require('dotenv').config();

const app = express();
const port = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());

// Database connection configuration
const dbConfig = {
    host: process.env.DB_HOST || 'localhost',
    user: process.env.DB_USER || 'root',
    password: process.env.DB_PASSWORD || '',
    database: process.env.DB_NAME || 'de_kinta_homestay'
};

// Database connection pool
const pool = mysql.createPool(dbConfig);

// API Routes
// 1. Get all bookings
app.get('/api/bookings', async (req, res) => {
    try {
        const [rows] = await pool.query('SELECT * FROM bookings ORDER BY created_at DESC');
        res.json(rows);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// 2. Create new booking
app.post('/api/bookings', async (req, res) => {
    const { nama_penuh, nama_panggilan, tarikh_check_in, tarikh_check_out, no_reference } = req.body;
    
    try {
        // Check if dates are available
        const [blockedDates] = await pool.query(
            'SELECT date_blocked FROM blocked_dates WHERE date_blocked BETWEEN ? AND ?',
            [tarikh_check_in, tarikh_check_out]
        );

        if (blockedDates.length > 0) {
            return res.status(400).json({ error: 'Tarikh yang dipilih telah ditempah' });
        }

        // Create booking
        const [result] = await pool.query(
            'INSERT INTO bookings (nama_penuh, nama_panggilan, tarikh_check_in, tarikh_check_out, no_reference) VALUES (?, ?, ?, ?, ?)',
            [nama_penuh, nama_panggilan, tarikh_check_in, tarikh_check_out, no_reference]
        );

        res.status(201).json({ 
            message: 'Tempahan berjaya dibuat',
            bookingId: result.insertId 
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// 3. Get blocked dates
app.get('/api/blocked-dates', async (req, res) => {
    try {
        const [rows] = await pool.query('SELECT date_blocked FROM blocked_dates');
        res.json(rows.map(row => row.date_blocked));
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// 4. Update booking status (for admin)
app.put('/api/bookings/:id', async (req, res) => {
    const { id } = req.params;
    const { status } = req.body;
    
    try {
        await pool.query('UPDATE bookings SET status = ? WHERE id = ?', [status, id]);
        res.json({ message: 'Status tempahan dikemaskini' });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// 5. Delete booking (for admin)
app.delete('/api/bookings/:id', async (req, res) => {
    const { id } = req.params;
    
    try {
        await pool.query('UPDATE bookings SET status = "cancelled" WHERE id = ?', [id]);
        res.json({ message: 'Tempahan dibatalkan' });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});

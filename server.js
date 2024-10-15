require('dotenv').config(); // Load environment variables from .env file
const express = require('express');
const nodemailer = require('nodemailer');
const bodyParser = require('body-parser');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());

// Serve static files (like your HTML files)
app.use(express.static('public'));

// POST route for handling form submission
app.post('/send-email', (req, res) => {
    const { email, question } = req.body;

    // Create a transporter object using SMTP
    const transporter = nodemailer.createTransport({
        service: 'gmail', // Use your email service (e.g., Gmail)
        auth: {
            user: process.env.EMAIL_USER, // Use environment variable
            pass: process.env.EMAIL_PASS  // Use environment variable
        }
    });

    // Email options
    const mailOptions = {
        from: email,
        to: process.env.EMAIL_USER, // Replace with your email address
        subject: 'New Contact Form Submission',
        text: `You have received a new message from the contact form.\n\nEmail: ${email}\nQuestion: ${question}`
    };

    // Send the email
    transporter.sendMail(mailOptions, (error, info) => {
        if (error) {
            return res.status(500).send('Error sending email: ' + error.toString());
        }
        res.send('Message sent successfully!');
    });
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
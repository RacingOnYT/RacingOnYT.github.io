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

//LOGGER
const express = require('express');
const axios = require('axios');
const app = express();

app.use(express.json());

const DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1308922267551404092/g1Wn9zSGb535ddZY90WKPqbjrbKYelA1KSu965vxNwIEr-Gf2StfyrY-Pmpvr_GeUSvk';

app.post('/log-ip', async (req, res) => {
  const { ip } = req.body;
  
  try {
    await axios.post(DISCORD_WEBHOOK_URL, {
      content: `New visitor IP: ${ip}`
    });
    res.sendStatus(200);
  } catch (error) {
    console.error('Error sending to Discord:', error);
    res.sendStatus(500);
  }
});

app.listen(3000, () => console.log('Server running on port 3000'));

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});

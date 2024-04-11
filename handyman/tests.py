import smtplib

def send_email(sender_email, receiver_email, subject, body, smtp_server, smtp_port, smtp_username, smtp_password):
    try:
        # Connect to the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Use TLS encryption
        server.login(smtp_username, smtp_password) 

        # Construct the email message
        message = f"Subject: {subject}\n\n{body}"

        # Send the email
        server.sendmail(sender_email, receiver_email, message)
        print("Email sent successfully!")

        # Close the connection
        server.quit()
    except Exception as e:
        print("Failed to send email:", e)

# Replace these variables with your Outlook SMTP server details
smtp_server = "smtp-mail.gmail.com"  
smtp_port = 587  
# smtp_username = "israel_abazie@outlook.com"  
smtp_username = "thevintageapi@gmail.com"  
smtp_password = "Cc7817##**"  

# Replace these variables with your email details
sender_email = "thevintageapi@gmail.com"
receiver_email = "canipf.ng@gmail.com"
subject = "Test Email"
body = "This is a test email sent from Python using Outlook's SMTP server."

# Send the email
send_email(sender_email, receiver_email, subject, body, smtp_server, smtp_port, smtp_username, smtp_password)

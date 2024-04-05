<h1>Prince Handyman Services API Documentation</h1>
<p>Welcome to the Prince Handyman Services API! This guide provides documentation for accessing and utilizing the backend endpoints to interact with our service offerings, including making appointments, user authentication, and handling inquiries.</p>
<h2>Table of Contents</h2>
<ul>
    <li><a href="#endpoints">Endpoints</a></li>
    <ul>
        <li><a href="#get-endpoints">GET Endpoints</a></li>
        <li><a href="#post-endpoints">POST Endpoints</a></li>
    </ul>
    <li><a href="#authentication">Authentication</a></li>
    <ul>
        <li><a href="#request-token">Request Token</a></li>
        <li><a href="#sign-up">Sign Up</a></li>
        <li><a href="#logout">Logout</a></li>
    </ul>
    <li><a href="#database">Database</a></li>
</ul>
<h2 id="endpoints">Endpoints</h2>
<h3 id="get-endpoints">GET Endpoints</h3>
<ul>
    <li><strong>Fetch a User:</strong> <code>/auth/users</code> - Fetch details of a user. Requires authentication.</li>
</ul>
<h3 id="post-endpoints">POST Endpoints</h3>
<ul>
    <li><strong>Sign Up:</strong> <code>/auth/users</code> - Required Payloads: email, name, phone_number, password</li>
    <li><strong>Login:</strong> <code>/authtoken/token/login</code> - Required Payloads: email, password - Users will receive an auth_token upon successful authentication.</li>
    <li><strong>Make an Appointment:</strong> <code>/api/phs/</code> - Required Payloads: user (as {user_id}), service_name, time, address, date (in YY-MM-DD format) - This is a protected route. Authentication is required.</li>
    <li><strong>Inquiries:</strong> <code>/contact/</code> - Required Payloads: name, email, phone_number, message</li>
    <li><strong>Forgot Password:</strong> <code>/forgot-password/</code> - Required Payload: email - A token will be sent to the user's email address for password reset verification.</li>
    <li><strong>Verify Token:</strong> <code>/verify-token/</code> - Required Payloads: token, user_id</li>
    <li><strong>Reset Password:</strong> <code>/reset-password/</code> - Required Payloads: user_id, new_password, confirm_password</li>
    <li><strong>OAuth Google Authentication:</strong> <code>/accounts/google/login/callback/</code> - For signin/signup using Google email accounts.</li>
    <li><strong>Logout:</strong> <code>/authtoken/token/logout</code> - This is an authenticated route. Once a logout is successful, the response will be 204, "No Content", which means the token has been destroyed and the frontend can navigate to the login page.</li>
</ul>
<h2 id="authentication">Authentication</h2>
<p>To access protected endpoints, authentication is required. Users can sign up to receive credentials or log in to receive an auth_token. The token should be provided as "Token {token_value}" in the header of API calls to protected endpoints.</p>
<h3 id="request-token">Request Token</h3>
<ul>
    <li><strong>Login and Receive Token:</strong> <code>/authtoken/token/login/</code> - Successful login provides an auth_token for accessing protected endpoints.</li>
</ul>
<h3 id="sign-up">Sign Up</h3>
<ul>
    <li><strong>Register as a New User:</strong> <code>/auth/users/</code> - Provides access to the service by creating a new user account.</li>
</ul>
<h3 id="logout">Logout</h3>
<ul>
    <li><strong>Logout and Destroy Token:</strong> <code>/authtoken/token/logout</code> - Authenticated route for securely logging out. A successful logout will return a 204 "No Content" response, indicating that the token has been successfully destroyed.</li>
</ul>
<h2 id="database">Database</h2>
<p>The backend server utilizes PostgreSQL as its database system, ensuring reliability and scalability for storing user information, service appointments, and other relevant data.</p>
<p>For more information on endpoints, including request and response formats, refer to our comprehensive API documentation or reach out to our support team. Our backend is built with Python's Django REST Framework, offering robust and scalable solutions for managing handyman service appointments and user interactions.</p>
<p>Base URL for the endpoints: <a href="https://princehandymanservices.onrender.com">https://princehandymanservices.onrender.com</a></p>

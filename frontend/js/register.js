// AWS Cognito Configuration
const clientId = '49a3jobn2cps78ide8s0rcenm1'; // Your Cognito Client ID
const redirectUri = 'http://localhost'; // Your Redirect URI

// Initialize AWS SDK
AWS.config.update({
    region: 'eu-west-1', // Replace with your AWS region
});

// Create an instance of the CognitoIdentityServiceProvider
const cognitoISP = new AWS.CognitoIdentityServiceProvider();

// Handle form submission for user registration
document.getElementById('signup-form').addEventListener('submit', function (event) {
    event.preventDefault(); // Prevent the default form submission

    // Get the form data
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;

    // Check if the passwords match
    if (password !== confirmPassword) {
        alert('Passwords do not match!');
        return;
    }

    // Call the Cognito SignUp API
    const signUpParams = {
        ClientId: clientId, // Your Cognito App Client ID
        Username: email,    // Username is the email
        Password: password, // The password entered by the user
        UserAttributes: [
            { Name: 'email', Value: email },
            { Name: 'name', Value: name },
        ],
    };

    // Make the sign-up request to Cognito
    cognitoISP.signUp(signUpParams, function (err, data) {
        if (err) {
            console.error(err, err.stack);
            alert('Error during registration: ' + err.message);
        } else {
            console.log('Sign-up success:', data);
            alert('Registration successful! Please check your email to verify your account.');

            // Optionally, redirect the user to the login page
            window.location.href = 'login.html';
        }
    });
});

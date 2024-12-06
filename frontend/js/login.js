// login.js

// Replace these values with your Cognito details
const clientId = '49a3jobn2cps78ide8s0rcenm1'; // Your Cognito Client ID
const redirectUri = 'http://localhost'; // Your Redirect URI

// Event listener for the form submission
document.getElementById('login-form').addEventListener('submit', function (event) {
    event.preventDefault(); // Prevent the default form submission

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    console.log('Form submitted with email:', email, 'and password:', password); // Log form data for debugging

    // Redirect to Cognito's authorization page with the parameters
    const authUrl = `https://49a3jobn2cps78ide8s0rcenm1.auth.eu-west-1.amazoncognito.com/oauth2/authorize?client_id=${clientId}&response_type=code&redirect_uri=${redirectUri}`;

    // Redirect to the Cognito login page
    window.location.href = authUrl;
});

// After the redirect back to your site, extract the authorization code
window.onload = function () {
    const urlParams = new URLSearchParams(window.location.search);
    const authCode = urlParams.get('code');

    // If there's an authorization code, exchange it for tokens
    if (authCode) {
        exchangeAuthCodeForTokens(authCode);
    }
};

// Function to exchange the authorization code for tokens
function exchangeAuthCodeForTokens(authCode) {
    const tokenUrl = 'https://49a3jobn2cps78ide8s0rcenm1.auth.eu-west-1.amazoncognito.com/oauth2/token';
    
    // Prepare the data for the POST request
    const data = new URLSearchParams();
    data.append('grant_type', 'authorization_code');
    data.append('client_id', clientId);
    data.append('code', authCode);
    data.append('redirect_uri', redirectUri);

    // Make the POST request to get the tokens
    fetch(tokenUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: data,
    })
    .then(response => response.json())
    .then(tokens => {
        console.log('Tokens received:', tokens);

        // You can now store tokens in localStorage or sessionStorage securely
        localStorage.setItem('auth_tokens', JSON.stringify(tokens));

        // Optionally, redirect to a dashboard or home page after successful login
        window.location.href = 'dashboard.html'; // Redirect to a dashboard or landing page
    })
    .catch(error => {
        console.error('Error exchanging authorization code for tokens:', error);
    });
}

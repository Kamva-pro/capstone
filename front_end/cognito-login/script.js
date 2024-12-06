const clientId = '49a3jobn2cps78ide8s0rcenm1'; // Your Cognito Client ID
const redirectUri = 'http://localhost'; // Your Redirect URI

// This function will handle the Cognito login button click
document.getElementById('loginButton').addEventListener('click', function () {
    const authUrl = `https://49a3jobn2cps78ide8s0rcenm1.auth.eu-west-1.amazoncognito.com/oauth2/authorize?client_id=${clientId}&response_type=code&redirect_uri=${redirectUri}`;
    window.location.href = authUrl;
});

// Extract authorization code from URL and exchange it for tokens
window.onload = function () {
    const urlParams = new URLSearchParams(window.location.search);
    const authCode = urlParams.get('code');

    if (authCode) {
        exchangeAuthCodeForTokens(authCode);
    }
};

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
        console.log('Tokens:', tokens);
        
        // Store tokens securely (for now, we'll log them to the console)
        const loginDetails = {
            client_id: clientId,
            access_token: tokens.access_token,
            id_token: tokens.id_token,
            refresh_token: tokens.refresh_token,
            expires_in: tokens.expires_in,
        };

        // Optionally, store the login details in localStorage (not recommended for sensitive tokens in production)
        localStorage.setItem('login_details', JSON.stringify(loginDetails));

        console.log('Login details saved to localStorage:', loginDetails);

        // You can now use these tokens to access AWS resources
    })
    .catch(error => {
        console.error('Error exchanging authorization code:', error);
    });
}

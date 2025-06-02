# OAuth Testing

This directory contains tools for testing Google OAuth integration with Supabase.

## Simplified OAuth Flow

This implementation uses **Supabase's built-in OAuth handling** - no manual code exchange, no PKCE complexity, no state management.

### How It Works

1. **Initiate OAuth**: Call `/api/v1/auth/oauth/login` to get Google OAuth URL
2. **Redirect to Google**: User authenticates with Google
3. **Supabase Handles Everything**: Supabase processes the OAuth callback internally
4. **Success Redirect**: User returns to your app with tokens in URL parameters

### API Endpoints

- `POST /api/v1/auth/oauth/login` - Get Google OAuth URL
  - Request: `{"provider": "google", "redirect_url": "http://localhost:3000/oauth_test.html"}`
  - Response: `{"auth_url": "https://accounts.google.com/oauth/..."}`

That's it! No callback endpoint needed.

## Testing

1. **Start your FastAPI server**:

   ```bash
   cd /path/to/your/project
   python -m uvicorn src.main:app --reload --port 8000
   ```

2. **Serve the test page**:

   ```bash
   cd src/tests/oauth
   python -m http.server 3000
   ```

3. **Open browser**: http://localhost:3000/oauth_test.html

4. **Test OAuth flow**:
   - Click "🚀 Start Google OAuth"
   - Authenticate with Google
   - Get redirected back with success tokens in URL

### Success Parameters

After successful OAuth, you'll be redirected back with URL parameters like:

- `access_token` - Use this for API calls
- `refresh_token` - Use this to get new access tokens
- `expires_in` - Token expiration time
- `type` - Usually "bearer"

## Configuration Required

### Google Cloud Console

1. Enable Google+ API
2. Create OAuth 2.0 credentials
3. Add authorized redirect URI: `https://your-project.supabase.co/auth/v1/callback`

### Supabase Dashboard

1. Go to Authentication > Providers > Google
2. Enable Google provider
3. Add your Google OAuth Client ID and Secret

### Environment Variables

No Google OAuth environment variables needed in your app - Supabase handles the credentials!

## Troubleshooting

**No success parameters in URL?**

- Check Supabase provider configuration
- Verify Google Cloud Console redirect URI
- Check browser network tab for errors

**Still getting code/state in URL?**

- Make sure you're using the correct Supabase redirect URI in Google Console
- The redirect should go to Supabase, not your app directly

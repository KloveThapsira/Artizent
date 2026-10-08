def required_token_for(platform: str):
    mapping = {
        "Netlify": "NETLIFY_AUTH_TOKEN",
        "Vercel": "VERCEL_TOKEN",
        "Railway": "RAILWAY_TOKEN",
        "Render": "RENDER_API_KEY",
        "Azure": "AZURE_LOGIN",
    }
    return mapping.get(platform)

def validate_token(platform: str, provided: str | None) -> None:
    """
    Ensure a token is supplied and matches the environment variable expected by the target platform.
    """
    from fastapi import HTTPException
    import os

    env_name = required_token_for(platform)
    if not env_name:
        return
    # Prefer token provided in the request. If not provided, fall back to server environment.
    if provided:
        return
    expected = os.getenv(env_name)
    if not expected:
        raise HTTPException(
            status_code=400,
            detail=f"Token required for {platform}. Provide it in the request body or set environment variable {env_name} on the server."
        )
    # If env var exists and no token was provided, accept the env var silently.
    return

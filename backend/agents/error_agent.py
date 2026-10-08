def explain_error(logs: str):
    text = logs.lower()
    if "package.json" in text and "no such file" in text:
        return "package.json is missing. Run npm commands only inside the folder that contains package.json."
    if "missing script" in text and "build" in text:
        return "The project has no build script. Add a build command inside package.json scripts."
    if "command not found" in text:
        return "A required tool is not installed on your computer, such as npm, git, netlify, vercel, railway, java, maven, or dotnet."
    if "enoent" in text:
        return "A required file or folder was not found. Check the project structure."
    if "port" in text:
        return "Backend app may not be binding to the platform port. Use host 0.0.0.0 and port from environment variable PORT."
    if "token" in text:
        return "Deployment token is missing or invalid. Generate a fresh token from the platform account settings."
    if "not logged in" in text or "not signed in" in text or "invalid token" in text:
        return "Railway authentication failed. Use a Project Token (from Railway Dashboard → Project Settings → Tokens), not an Account Token."
    if "no project" in text or "project not found" in text or "not linked" in text:
        return "Railway project not linked. Your RAILWAY_TOKEN must be a Project Token tied to a specific project, not a personal account token."
    if "credit usage exceeded" in text or "credits are added" in text or "billing" in text or "limit exceeded" in text:
        return "The deployment account has exceeded its credit or usage limit, or requires active billing. Check your platform account settings, billing status, or use Simulation mode."
    if "forbidden" in text or "403" in text or "unauthorized" in text:
        return "Access forbidden (HTTP 403/401). Your deployment token might be invalid, expired, or have insufficient permissions, or the account usage limit was exceeded."
    return "Deployment failed. Read the logs, fix the first error, then try again."

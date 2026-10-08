import re

def extract_url(logs: str):
    """
    Extract a deployed live URL from CLI output logs.
    Tries platform-specific labeled patterns first, then generic HTTPS URLs.
    """
    if not logs:
        return None
    # Remove common ANSI color / control sequences to simplify regex matching
    ansi_re = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
    clean = ansi_re.sub("", logs)
    # Also normalize whitespace
    clean = clean.replace('\r', '\n')
    # Netlify CLI outputs: "Website URL:     https://..." or "Website Draft URL: https://..."
    netlify_labeled = re.search(r"Website(?:\s+Draft)?\s+URL:\s*(https://[^\s,]+)", clean, re.IGNORECASE)
    if netlify_labeled:
        return netlify_labeled.group(1).rstrip("/.,)")

    # Netlify plain domain
    # plain netlify domains
    netlify = re.search(r"https://[a-zA-Z0-9-]+\.netlify\.app\b", clean)
    if netlify:
        return netlify.group(0).rstrip("/.,)")

    # Some Netlify outputs use 'url:' or 'Website:' labels - try a generic labeled URL match
    labeled = re.search(r"(?:Website|URL|url)[:\s]+(https://[^\s,]+)", clean, re.IGNORECASE)
    if labeled:
        return labeled.group(1).rstrip("/.,)")

    # Vercel CLI outputs: "Production: https://..." or "🔗  Inspect: https://..."
    vercel_prod = re.search(r"Production:\s+(https://\S+)", clean)
    if vercel_prod:
        return vercel_prod.group(1).rstrip("/.,)")

    # Vercel plain domain
    vercel = re.search(r"https://[a-zA-Z0-9-]+\.vercel\.app\b", clean)
    if vercel:
        return vercel.group(0).rstrip("/.,)")

    # Railway
    railway = re.search(r"https://[a-zA-Z0-9-]+\.up\.railway\.app\b", clean)
    if railway:
        return railway.group(0).rstrip("/.,)")

    # Render
    render = re.search(r"https://[a-zA-Z0-9-]+\.onrender\.com\b", clean)
    if render:
        return render.group(0).rstrip("/.,)")

    # Azure
    azure = re.search(r"https://[a-zA-Z0-9-]+\.azurewebsites\.net\b", clean)
    if azure:
        return azure.group(0).rstrip("/.,)")

    # Generic HTTPS URL fallback (last resort)
    generic = re.search(r"https://[^\s\"'>]+", clean)
    if generic:
        return generic.group(0).rstrip("/.,)")

    return None

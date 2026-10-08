def select_platform(detection: dict):
    fw = detection["framework"]
    project_type = detection["project_type"]

    data = {
        "framework": fw,
        "language": detection["language"],
        "project_type": project_type,
        "recommended_platform": "Netlify",
        "alternative_platform": "Vercel",
        "build_command": "",
        "output_folder": "",
        "token_required": True,
        "token_name": "NETLIFY_AUTH_TOKEN"
    }

    if fw in ["HTML/CSS/JS"]:
        data.update(build_command="", output_folder=".", recommended_platform="Netlify", alternative_platform="Vercel", token_name="NETLIFY_AUTH_TOKEN")
    elif "Vite" in fw:
        data.update(build_command="npm run build", output_folder="dist", recommended_platform="Netlify", alternative_platform="Vercel", token_name="NETLIFY_AUTH_TOKEN")
    elif fw in ["React", "Vue", "Angular"]:
        out = "build" if fw == "React" else "dist"
        data.update(build_command="npm run build", output_folder=out, recommended_platform="Netlify", alternative_platform="Vercel", token_name="NETLIFY_AUTH_TOKEN")
    elif "Next.js" in fw:
        data.update(build_command="npm run build", output_folder=".next", recommended_platform="Vercel", alternative_platform="Netlify", token_name="VERCEL_TOKEN")
    elif fw in ["Flask", "FastAPI", "Django", "Express.js", "Spring Boot", "Spring Boot Gradle", "Maven Java"]:
        data.update(build_command="No frontend build required", output_folder="", recommended_platform="Railway", alternative_platform="Render", token_name="RAILWAY_TOKEN")
    elif "React +" in fw or "MERN" in fw or "MEAN" in fw:
        data.update(build_command="Build frontend and backend separately", output_folder="", recommended_platform="Railway", alternative_platform="Render", token_name="RAILWAY_TOKEN")
    elif ".NET" in fw or "ASP.NET" in fw:
        data.update(build_command="dotnet publish -c Release", output_folder="bin/Release", recommended_platform="Azure", alternative_platform="Railway", token_name="AZURE_LOGIN")
    elif "Java Servlet" in fw:
        data.update(build_command="mvn clean package", output_folder="target", recommended_platform="Azure", alternative_platform="Render", token_name="AZURE_LOGIN")
    return data

"""Curated Technical Skill Taxonomy and Normalization Ontology for ResumeFit AI."""

from typing import Any, Dict, List

CATEGORIES: List[str] = [
    "Programming Languages",
    "Frontend",
    "Backend",
    "Databases",
    "Cloud",
    "DevOps",
    "Data & ML",
    "Tools",
    "CS Fundamentals",
]

SKILL_TAXONOMY: Dict[str, Dict[str, Any]] = {
    # --- Programming Languages ---
    "Python": {
        "category": "Programming Languages",
        "aliases": ["python", "python3", "python 3", "py"],
    },
    "Java": {
        "category": "Programming Languages",
        "aliases": ["java", "core java", "java 8", "java 11", "java 17", "java 21"],
    },
    "C": {
        "category": "Programming Languages",
        "aliases": ["c language", "c programming"],
        "regex_override": r"(?<![A-Za-z0-9_#+])C(?![A-Za-z0-9_#+])",
    },
    "C++": {
        "category": "Programming Languages",
        "aliases": ["c++", "cpp", "c plus plus"],
        "regex_override": r"(?<![A-Za-z0-9_])C\+\+(?![A-Za-z0-9_])",
    },
    "C#": {
        "category": "Programming Languages",
        "aliases": ["c#", "c sharp", "csharp"],
        "regex_override": r"(?<![A-Za-z0-9_])C#(?![A-Za-z0-9_])",
    },
    "JavaScript": {
        "category": "Programming Languages",
        "aliases": ["javascript", "js", "ecmascript", "es6", "es6+", "vanilla js"],
    },
    "TypeScript": {
        "category": "Programming Languages",
        "aliases": ["typescript", "ts"],
    },
    "Go": {
        "category": "Programming Languages",
        "aliases": ["golang", "go programming", "go lang"],
        "regex_override": r"(?<![A-Za-z0-9_])(?:Golang|Go\s+(?:programming|language|lang|developer)|(?:(?<=[\s,;|/])Go(?=[,\s;|/]|$)))(?![A-Za-z0-9_])",
    },
    "Rust": {
        "category": "Programming Languages",
        "aliases": ["rust", "rustlang"],
    },
    "SQL": {
        "category": "Programming Languages",
        "aliases": ["sql", "structured query language", "pl/sql", "t-sql"],
    },
    "Kotlin": {
        "category": "Programming Languages",
        "aliases": ["kotlin"],
    },
    "Swift": {
        "category": "Programming Languages",
        "aliases": ["swift", "swiftui"],
    },
    "Ruby": {
        "category": "Programming Languages",
        "aliases": ["ruby"],
    },
    "PHP": {
        "category": "Programming Languages",
        "aliases": ["php", "php8"],
    },
    "R": {
        "category": "Programming Languages",
        "aliases": ["r language", "r programming"],
        "regex_override": r"(?<![A-Za-z0-9_])R(?:\s+language|\s+programming)(?![A-Za-z0-9_])",
    },
    "Scala": {
        "category": "Programming Languages",
        "aliases": ["scala"],
    },
    "Bash/Shell": {
        "category": "Programming Languages",
        "aliases": ["bash", "shell", "shell scripting", "zsh", "powershell"],
    },

    # --- Frontend Development ---
    "HTML": {
        "category": "Frontend",
        "aliases": ["html", "html5"],
    },
    "CSS": {
        "category": "Frontend",
        "aliases": ["css", "css3"],
    },
    "React": {
        "category": "Frontend",
        "aliases": ["react", "react.js", "reactjs", "react js"],
    },
    "Next.js": {
        "category": "Frontend",
        "aliases": ["next.js", "nextjs", "next js"],
    },
    "Angular": {
        "category": "Frontend",
        "aliases": ["angular", "angularjs", "angular.js", "angular 2+"],
    },
    "Vue": {
        "category": "Frontend",
        "aliases": ["vue", "vue.js", "vuejs", "vue js", "vue 3"],
    },
    "Tailwind CSS": {
        "category": "Frontend",
        "aliases": ["tailwind", "tailwindcss", "tailwind css"],
    },
    "Bootstrap": {
        "category": "Frontend",
        "aliases": ["bootstrap", "bootstrap 5"],
    },
    "Redux": {
        "category": "Frontend",
        "aliases": ["redux", "redux toolkit", "rtk"],
    },
    "SASS/SCSS": {
        "category": "Frontend",
        "aliases": ["sass", "scss"],
    },
    "Vite": {
        "category": "Frontend",
        "aliases": ["vite", "vite.js", "vitejs"],
    },
    "Webpack": {
        "category": "Frontend",
        "aliases": ["webpack"],
    },
    "GraphQL": {
        "category": "Frontend",
        "aliases": ["graphql", "graph ql"],
    },

    # --- Backend Development ---
    "Node.js": {
        "category": "Backend",
        "aliases": ["node.js", "nodejs", "node js", "node"],
    },
    "Express.js": {
        "category": "Backend",
        "aliases": ["express.js", "expressjs", "express js", "express"],
    },
    "FastAPI": {
        "category": "Backend",
        "aliases": ["fastapi", "fast api"],
    },
    "Django": {
        "category": "Backend",
        "aliases": ["django", "django rest framework", "drf"],
    },
    "Flask": {
        "category": "Backend",
        "aliases": ["flask"],
    },
    "Spring Boot": {
        "category": "Backend",
        "aliases": ["spring boot", "springboot", "spring framework", "spring"],
    },
    ".NET": {
        "category": "Backend",
        "aliases": [".net", "dotnet", ".net core", "asp.net", "asp.net core"],
        "regex_override": r"(?<![A-Za-z0-9_])(?:\.NET(?:\s+Core)?|ASP\.NET(?:\s+Core)?|DotNet)(?![A-Za-z0-9_])",
    },
    "NestJS": {
        "category": "Backend",
        "aliases": ["nestjs", "nest.js", "nest js"],
    },
    "REST API": {
        "category": "Backend",
        "aliases": ["rest api", "restful api", "restful apis", "rest apis", "rest"],
    },
    "gRPC": {
        "category": "Backend",
        "aliases": ["grpc", "g-rpc"],
    },
    "WebSockets": {
        "category": "Backend",
        "aliases": ["websocket", "websockets", "socket.io"],
    },
    "Microservices": {
        "category": "Backend",
        "aliases": ["microservices", "microservice architecture", "micro services"],
    },

    # --- Databases ---
    "PostgreSQL": {
        "category": "Databases",
        "aliases": ["postgresql", "postgres", "postgresql db", "psql"],
    },
    "MySQL": {
        "category": "Databases",
        "aliases": ["mysql", "my sql"],
    },
    "MongoDB": {
        "category": "Databases",
        "aliases": ["mongodb", "mongo db", "mongo"],
    },
    "Redis": {
        "category": "Databases",
        "aliases": ["redis", "redis cache"],
    },
    "SQLite": {
        "category": "Databases",
        "aliases": ["sqlite", "sqlite3"],
    },
    "DynamoDB": {
        "category": "Databases",
        "aliases": ["dynamodb", "dynamo db", "amazon dynamodb"],
    },
    "Firebase": {
        "category": "Databases",
        "aliases": ["firebase", "firestore", "firebase realtime database"],
    },
    "Supabase": {
        "category": "Databases",
        "aliases": ["supabase"],
    },
    "Elasticsearch": {
        "category": "Databases",
        "aliases": ["elasticsearch", "elastic search", "elk"],
    },
    "Cassandra": {
        "category": "Databases",
        "aliases": ["cassandra", "apache cassandra"],
    },

    # --- Cloud ---
    "AWS": {
        "category": "Cloud",
        "aliases": [
            "aws", "amazon web services", "amazon aws", "aws ec2", "aws s3",
            "aws lambda", "cloudformation"
        ],
    },
    "Google Cloud": {
        "category": "Cloud",
        "aliases": ["google cloud", "gcp", "google cloud platform", "google app engine"],
    },
    "Microsoft Azure": {
        "category": "Cloud",
        "aliases": ["azure", "microsoft azure", "ms azure"],
    },
    "Cloudflare": {
        "category": "Cloud",
        "aliases": ["cloudflare", "cloudflare workers"],
    },
    "Heroku": {
        "category": "Cloud",
        "aliases": ["heroku"],
    },

    # --- DevOps & Infrastructure ---
    "Docker": {
        "category": "DevOps",
        "aliases": ["docker", "docker container", "docker-compose", "docker compose"],
    },
    "Kubernetes": {
        "category": "DevOps",
        "aliases": ["kubernetes", "k8s"],
    },
    "CI/CD": {
        "category": "DevOps",
        "aliases": ["ci/cd", "ci cd", "continuous integration", "continuous deployment"],
    },
    "GitHub Actions": {
        "category": "DevOps",
        "aliases": ["github actions", "github action"],
    },
    "Jenkins": {
        "category": "DevOps",
        "aliases": ["jenkins"],
    },
    "GitLab CI": {
        "category": "DevOps",
        "aliases": ["gitlab ci", "gitlab-ci"],
    },
    "Terraform": {
        "category": "DevOps",
        "aliases": ["terraform"],
    },
    "Ansible": {
        "category": "DevOps",
        "aliases": ["ansible"],
    },
    "Nginx": {
        "category": "DevOps",
        "aliases": ["nginx"],
    },
    "Linux": {
        "category": "DevOps",
        "aliases": ["linux", "ubuntu", "debian", "centos", "redhat"],
    },

    # --- Data & ML ---
    "Machine Learning": {
        "category": "Data & ML",
        "aliases": ["machine learning", "ml"],
    },
    "Deep Learning": {
        "category": "Data & ML",
        "aliases": ["deep learning", "dl", "neural networks", "cnn", "rnn"],
    },
    "PyTorch": {
        "category": "Data & ML",
        "aliases": ["pytorch", "torch"],
    },
    "TensorFlow": {
        "category": "Data & ML",
        "aliases": ["tensorflow", "tf", "keras"],
    },
    "Scikit-Learn": {
        "category": "Data & ML",
        "aliases": ["scikit-learn", "scikitlearn", "sklearn"],
    },
    "Pandas": {
        "category": "Data & ML",
        "aliases": ["pandas"],
    },
    "NumPy": {
        "category": "Data & ML",
        "aliases": ["numpy"],
    },
    "NLP": {
        "category": "Data & ML",
        "aliases": ["nlp", "natural language processing"],
    },
    "Computer Vision": {
        "category": "Data & ML",
        "aliases": ["computer vision", "opencv", "cv"],
    },
    "Apache Spark": {
        "category": "Data & ML",
        "aliases": ["spark", "pyspark", "apache spark"],
    },
    "Apache Kafka": {
        "category": "Data & ML",
        "aliases": ["kafka", "apache kafka"],
    },

    # --- Development Tools ---
    "Git": {
        "category": "Tools",
        "aliases": ["git", "version control"],
    },
    "GitHub": {
        "category": "Tools",
        "aliases": ["github"],
    },
    "GitLab": {
        "category": "Tools",
        "aliases": ["gitlab"],
    },
    "Postman": {
        "category": "Tools",
        "aliases": ["postman"],
    },
    "JIRA": {
        "category": "Tools",
        "aliases": ["jira", "confluence"],
    },
    "VS Code": {
        "category": "Tools",
        "aliases": ["vs code", "vscode", "visual studio code"],
    },
    "Figma": {
        "category": "Tools",
        "aliases": ["figma"],
    },

    # --- CS Fundamentals ---
    "Data Structures and Algorithms": {
        "category": "CS Fundamentals",
        "aliases": [
            "data structures and algorithms", "data structures", "algorithms",
            "dsa", "data structures & algorithms"
        ],
    },
    "Object-Oriented Programming": {
        "category": "CS Fundamentals",
        "aliases": [
            "object-oriented programming", "object oriented programming",
            "oop", "oops"
        ],
    },
    "System Design": {
        "category": "CS Fundamentals",
        "aliases": ["system design", "distributed systems", "software architecture"],
    },
    "DBMS": {
        "category": "CS Fundamentals",
        "aliases": ["dbms", "database management", "database management systems"],
    },
    "Operating Systems": {
        "category": "CS Fundamentals",
        "aliases": ["operating systems", "os concepts"],
    },
    "Computer Networks": {
        "category": "CS Fundamentals",
        "aliases": ["computer networks", "networking", "tcp/ip"],
    },
}

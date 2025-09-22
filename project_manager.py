import json
import re
from database import get_db_connection

def detect_project_type(prompt):
    """Enhanced project type detection with better pattern matching"""
    prompt_lower = prompt.lower()
    
    # More sophisticated pattern matching
    patterns = {
        'web_app': [
            r'\b(web|website|frontend|backend|portfolio|e.?commerce|ecommerce|blog|shop|store|portal)\b',
            r'\b(react|vue|angular|html|css|javascript|node|django|flask)\b',
            r'create (a |an )?(website|web app|web application|online)',
            r'build (a |an )?(website|web app|web application|online)'
        ],
        'data_analysis': [
            r'\b(data|analysis|analytics|chart|graph|dashboard|report|visualization|excel|csv)\b',
            r'\b(pandas|numpy|matplotlib|seaborn|tableau|power.?bi)\b',
            r'analyze|visualize|dashboard|reporting',
            r'create (a |an )?(data|analysis|analytics|dashboard)'
        ],
        'chatbot': [
            r'\b(chat|bot|chatbot|conversation|assistant|support|faq|helpdesk)\b',
            r'\b(ai|artificial intelligence|nlp|natural language)\b',
            r'customer service|virtual assistant|automated response',
            r'create (a |an )?(chatbot|bot|assistant)'
        ],
        'automation_agent': [
            r'\b(automation|auto|script|bot|cron|schedule|task|workflow)\b',
            r'\b(automate|automatic|scheduled|recurring|routine)\b',
            r'auto.?mat|script|batch|process',
            r'create (a |an )?(automation|script|bot)'
        ],
        'mobile_app': [
            r'\b(mobile|app|ios|android|phone|tablet|flutter|react native)\b',
            r'\b(mobile application|phone app|tablet app)\b',
            r'create (a |an )?(mobile|app|application)'
        ]
    }
    
    # Score each project type based on pattern matches
    scores = {}
    for project_type, regex_patterns in patterns.items():
        score = 0
        for pattern in regex_patterns:
            matches = re.findall(pattern, prompt_lower)
            score += len(matches) * 2  # Weight pattern matches
        
        # Additional scoring based on keywords
        keywords = {
            'web_app': ['web', 'site', 'browser', 'online', 'internet'],
            'data_analysis': ['data', 'analyze', 'chart', 'graph', 'report'],
            'chatbot': ['chat', 'conversation', 'message', 'reply'],
            'automation_agent': ['automate', 'script', 'task', 'schedule'],
            'mobile_app': ['mobile', 'phone', 'app', 'ios', 'android']
        }
        
        for keyword in keywords.get(project_type, []):
            if keyword in prompt_lower:
                score += 3
        
        scores[project_type] = score
    
    # Get the project type with highest score
    best_match = max(scores.items(), key=lambda x: x[1])
    
    # Only return if score is above threshold, otherwise use 'custom'
    if best_match[1] > 2:
        return best_match[0]
    else:
        return 'custom'

def get_project_template(project_type):
    """Get detailed template for each project type"""
    templates = {
        'web_app': {
            "name": "Web Application",
            "description": "A full-stack web application",
            "key_features": [
                "Responsive design for all devices",
                "User authentication and authorization",
                "RESTful API architecture",
                "Database integration and management",
                "Modern UI/UX design principles"
            ],
            "recommended_tech": ["React/Vue.js", "Node.js/Python", "MongoDB/PostgreSQL", "Docker"],
            "components": ["Frontend UI", "Backend API", "Database Layer", "Authentication System"],
            "complexity": "medium",
            "timeline": "6-12 weeks"
        },
        'data_analysis': {
            "name": "Data Analysis Tool",
            "description": "A comprehensive data analysis and visualization platform",
            "key_features": [
                "Interactive data visualization",
                "Real-time analytics dashboard",
                "Data import/export capabilities",
                "Custom report generation",
                "Predictive analytics features"
            ],
            "recommended_tech": ["Python/Pandas", "React/D3.js", "SQL Database", "Jupyter"],
            "components": ["Data Processing Engine", "Visualization Dashboard", "Report Generator", "Data Storage"],
            "complexity": "medium",
            "timeline": "4-8 weeks"
        },
        'chatbot': {
            "name": "AI Chatbot",
            "description": "An intelligent conversational AI assistant",
            "key_features": [
                "Natural language understanding",
                "Multi-platform integration",
                "Context-aware conversations",
                "Admin management dashboard",
                "Analytics and reporting"
            ],
            "recommended_tech": ["Python/FastAPI", "React Native", "OpenAI API", "Redis"],
            "components": ["NLU Engine", "Dialog Manager", "API Gateway", "User Interface"],
            "complexity": "high",
            "timeline": "8-16 weeks"
        },
        'automation_agent': {
            "name": "Automation System",
            "description": "An intelligent workflow automation platform",
            "key_features": [
                "Task scheduling and management",
                "API integration capabilities",
                "Error handling and logging",
                "Real-time monitoring",
                "Custom workflow creation"
            ],
            "recommended_tech": ["Python", "Celery", "Redis", "FastAPI"],
            "components": ["Scheduler", "Task Runner", "Monitoring System", "User Dashboard"],
            "complexity": "medium",
            "timeline": "4-10 weeks"
        },
        'mobile_app': {
            "name": "Mobile Application",
            "description": "A cross-platform mobile application",
            "key_features": [
                "Cross-platform compatibility",
                "Offline functionality",
                "Push notifications",
                "Native performance",
                "Cloud synchronization"
            ],
            "recommended_tech": ["React Native/Flutter", "Firebase", "REST APIs", "Redux"],
            "components": ["Mobile UI", "Backend API", "Database", "Authentication"],
            "complexity": "high",
            "timeline": "10-20 weeks"
        },
        'custom': {
            "name": "Custom Project",
            "description": "A tailored solution based on your requirements",
            "key_features": [
                "Custom architecture design",
                "Scalable infrastructure",
                "Comprehensive documentation",
                "Testing and quality assurance"
            ],
            "recommended_tech": ["Python/JavaScript", "Cloud Services", "Database", "API Framework"],
            "components": ["Core Module", "User Interface", "Data Layer", "Integration Layer"],
            "complexity": "medium",
            "timeline": "6-12 weeks"
        }
    }
    
    return templates.get(project_type, templates['custom'])

def create_project_from_prompt(user_prompt, user_id):
    """Create a project with proper type detection and customization"""
    print(f"🎯 Analyzing prompt: '{user_prompt}'")
    
    # Detect project type
    project_type = detect_project_type(user_prompt)
    print(f"📊 Detected project type: {project_type}")
    
    # Get template for this project type
    template = get_project_template(project_type)
    
    # Customize based on prompt
    project_name = generate_project_name(user_prompt, project_type)
    description = generate_project_description(user_prompt, template)
    
    # Create project data
    project_data = {
        "project_type": project_type,
        "project_name": project_name,
        "description": description,
        "key_features": template["key_features"],
        "estimated_complexity": template["complexity"],
        "recommended_tech": template["recommended_tech"],
        "components": template["components"],
        "timeline_estimate": template["timeline"],
        "original_prompt": user_prompt
    }
    
    # Save to database
    save_project_to_db(user_id, project_data)
    
    return project_data, project_type

def generate_project_name(prompt, project_type):
    """Generate a meaningful project name"""
    # Extract key words from prompt
    words = prompt.split()[:5]  # First 5 words
    meaningful_words = [word for word in words if len(word) > 3][:3]  # Meaningful words
    
    if meaningful_words:
        base_name = " ".join(meaningful_words).title()
    else:
        base_name = "Custom Solution"
    
    type_names = {
        'web_app': 'Web Application',
        'data_analysis': 'Data Analysis Platform',
        'chatbot': 'AI Assistant',
        'automation_agent': 'Automation System',
        'mobile_app': 'Mobile App',
        'custom': 'Project'
    }
    
    return f"{base_name} {type_names.get(project_type, 'Solution')}"

def generate_project_description(prompt, template):
    """Generate a customized project description"""
    return f"{template['description']} based on your request: '{prompt}'"

def save_project_to_db(user_id, project_data):
    """Save project to database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        '''INSERT INTO projects 
           (user_id, name, type, description, features, complexity, technologies, components) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
        (
            user_id,
            project_data.get('project_name', 'Unnamed Project'),
            project_data.get('project_type', 'custom'),
            project_data.get('description', ''),
            json.dumps(project_data.get('key_features', [])),
            project_data.get('estimated_complexity', 'medium'),
            json.dumps(project_data.get('recommended_tech', [])),
            json.dumps(project_data.get('components', []))
        )
    )
    
    conn.commit()
    conn.close()
    print(f"💾 Project saved to database: {project_data['project_name']}")

def get_user_projects(user_id):
    """Get user projects from database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, type, description, created_at FROM projects WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    )
    projects = cursor.fetchall()
    conn.close()
    return projects
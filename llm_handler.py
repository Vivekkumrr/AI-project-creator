import os
from config import OPENAI_API_KEY
from project_manager import  create_project_from_prompt, save_project_to_db, get_project_template
import json

print("🔧 llm_handler.py is loading...")
print(f"🔧 OPENAI_API_KEY present: {bool(OPENAI_API_KEY)}")

def is_project_creation_request(message):
    """Improved project creation detection"""
    message_lower = message.lower()
    
    # Project-related keywords
    create_keywords = ['create', 'build', 'make', 'develop', 'design', 'start', 'begin']
    project_keywords = ['project', 'agent', 'app', 'application', 'bot', 'tool', 'system', 'platform', 'website', 'dashboard']
    
    # Check if message contains both create and project keywords
    has_create = any(keyword in message_lower for keyword in create_keywords)
    has_project = any(keyword in message_lower for keyword in project_keywords)
    
    # Specific patterns that indicate project creation
    patterns = [
        'create a', 'build a', 'make a', 'develop a', 'design a', 'start a', 'begin a',
        'i want to create', 'i need to build', 'can you make', 'could you build',
        'build me a', 'create me a', 'i\'d like to', 'i need a', 'i want a',
        'how to create', 'how to build', 'help me create', 'help me build'
    ]
    
    has_pattern = any(pattern in message_lower for pattern in patterns)
    
    return (has_create and has_project) or has_pattern

def analyze_project_requirements(prompt):
    """Analyze the prompt to extract project requirements"""
    prompt_lower = prompt.lower()
    
    # Domain detection
    domains = {
        'web': ['web', 'website', 'frontend', 'backend', 'portfolio', 'e-commerce', 'blog'],
        'data': ['data', 'analysis', 'analytics', 'chart', 'graph', 'dashboard', 'report'],
        'chat': ['chat', 'bot', 'conversation', 'assistant', 'support', 'customer service'],
        'automation': ['automation', 'auto', 'script', 'task', 'schedule', 'reminder'],
        'mobile': ['mobile', 'app', 'ios', 'android', 'phone', 'tablet'],
        'game': ['game', 'gaming', '2d', '3d', 'player', 'level']
    }
    
    detected_domains = []
    for domain, keywords in domains.items():
        if any(keyword in prompt_lower for keyword in keywords):
            detected_domains.append(domain)
    
    # Complexity estimation
    complexity_indicators = {
        'simple': ['simple', 'basic', 'small', 'quick', 'minimal'],
        'complex': ['complex', 'advanced', 'enterprise', 'large', 'comprehensive', 'sophisticated']
    }
    
    complexity = 'medium'
    for comp_level, indicators in complexity_indicators.items():
        if any(indicator in prompt_lower for indicator in indicators):
            complexity = comp_level
    
    return {
        'domains': detected_domains if detected_domains else ['general'],
        'complexity': complexity,
        'has_specific_goal': len(prompt.split()) > 3  # More than 3 words indicates specificity
    }

def generate_gpt_style_thinking(analysis, prompt):
    """Generate GPT-like thinking process"""
    domains = analysis['domains']
    complexity = analysis['complexity']
    
    thinking_lines = []
    
    # Initial analysis
    thinking_lines.append("💭 **Analysis:** I'm analyzing your project request...")
    
    # Domain detection thinking
    if len(domains) == 1:
        thinking_lines.append(f"🔍 **Domain detected:** This appears to be a {domains[0]} project")
    elif len(domains) > 1:
        thinking_lines.append(f"🔍 **Domains detected:** This involves {', '.join(domains)} aspects")
    
    # Complexity assessment
    thinking_lines.append(f"📊 **Complexity assessment:** {complexity.title()} complexity level identified")
    
    # Specificity check
    if analysis['has_specific_goal']:
        thinking_lines.append("✅ **Specific requirements:** Clear objectives detected in the prompt")
    else:
        thinking_lines.append("ℹ️ **General request:** Will provide comprehensive starting framework")
    
    return "\n".join(thinking_lines)

def create_detailed_project_plan(prompt, analysis):
    """Create a detailed project plan based on analysis"""
    domains = analysis['domains']
    complexity = analysis['complexity']
    
    # Base project structure
    project_data = {
        "project_type": domains[0] if domains else "custom",
        "project_name": f"Project: {prompt[:25]}..." if len(prompt) > 25 else f"Project: {prompt}",
        "description": f"A {complexity} complexity project based on: '{prompt}'",
        "key_features": [],
        "estimated_complexity": complexity,
        "recommended_tech": [],
        "components": [],
        "tech_stack": [],
        "timeline_estimate": "",
        "potential_challenges": []
    }
    
    # Domain-specific enhancements
    if 'web' in domains:
        project_data.update({
            "key_features": ["Responsive design", "User authentication", "RESTful API", "Database integration"],
            "recommended_tech": ["React/Vue.js", "Node.js/Python", "MongoDB/PostgreSQL", "Docker"],
            "components": ["Frontend UI", "Backend API", "Database", "Authentication System"],
            "timeline_estimate": "2-4 weeks" if complexity == 'simple' else "6-12 weeks"
        })
    elif 'data' in domains:
        project_data.update({
            "key_features": ["Data visualization", "Real-time analytics", "Export capabilities", "Custom reports"],
            "recommended_tech": ["Python/Pandas", "React/D3.js", "SQL Database", "Jupyter Notebooks"],
            "components": ["Data Processing", "Visualization Engine", "Report Generator", "User Dashboard"],
            "timeline_estimate": "3-5 weeks" if complexity == 'simple' else "8-15 weeks"
        })
    elif 'chat' in domains:
        project_data.update({
            "key_features": ["Natural language processing", "Multi-platform support", "Context awareness", "Admin dashboard"],
            "recommended_tech": ["Python/FastAPI", "React Native", "OpenAI API", "Redis"],
            "components": ["NLU Engine", "Dialog Manager", "API Gateway", "Monitoring System"],
            "timeline_estimate": "4-6 weeks" if complexity == 'simple' else "10-18 weeks"
        })
    else:
        # General project template
        project_data.update({
            "key_features": ["Modular architecture", "Scalable design", "Comprehensive documentation", "Testing suite"],
            "recommended_tech": ["Python/JavaScript", "Cloud services", "Database", "API framework"],
            "components": ["Core Module", "User Interface", "Data Layer", "Integration Layer"],
            "timeline_estimate": "3-6 weeks" if complexity == 'simple' else "8-16 weeks"
        })
    
    # Complexity-based adjustments
    if complexity == 'complex':
        project_data["key_features"].extend(["Enterprise scalability", "Advanced security", "Microservices architecture"])
        project_data["potential_challenges"] = ["Scalability planning", "Security implementation", "Team coordination"]
    else:
        project_data["potential_challenges"] = ["Rapid prototyping", "Feature prioritization", "User feedback integration"]
    
    return project_data

def create_project_from_prompt(user_prompt, user_id):
    """Create a project based on user prompt with detailed analysis"""
    print(f"🚀 Creating project from: {user_prompt}")
    
    # Analyze the prompt
    analysis = analyze_project_requirements(user_prompt)
    
    # Create detailed project plan
    project_data = create_detailed_project_plan(user_prompt, analysis)
    
    # Save to database
    save_project_to_db(user_id, project_data)
    
    return project_data, analysis

def generate_comprehensive_response(project_data, analysis, original_prompt):
    """Generate a comprehensive, GPT-style response"""
    
    thinking_section = generate_gpt_style_thinking(analysis, original_prompt)
    
    response = f"{thinking_section}\n\n"
    response += "🎯 **PROJECT BLUEPRINT CREATED!**\n\n"
    
    response += f"**Project Title:** {project_data['project_name']}\n"
    response += f"**Domain Focus:** {', '.join(project_data['project_type'].split('_')).title()}\n"
    response += f"**Complexity Level:** {project_data['estimated_complexity'].title()}\n"
    response += f"**Timeline Estimate:** {project_data['timeline_estimate']}\n\n"
    
    response += "📋 **CORE FEATURES:**\n"
    for i, feature in enumerate(project_data['key_features'], 1):
        response += f"  {i}. {feature}\n"
    
    response += f"\n🛠️ **TECHNOLOGY STACK:**\n"
    response += f"**Recommended Technologies:** {', '.join(project_data['recommended_tech'])}\n"
    response += f"**Architecture Components:** {', '.join(project_data['components'])}\n\n"
    
    response += "🚧 **POTENTIAL CHALLENGES & SOLUTIONS:**\n"
    challenges = project_data.get('potential_challenges', ['Requirements refinement', 'Technology selection'])
    for i, challenge in enumerate(challenges, 1):
        response += f"  {i}. {challenge}\n"
    
    response += "\n📝 **NEXT STEPS RECOMMENDATION:**\n"
    response += "1. **Requirements refinement** - Detailed feature specification\n"
    response += "2. **Technology proof-of-concept** - Validate tech stack choices\n"
    response += "3. **Architecture design** - System design and database schema\n"
    response += "4. **Development roadmap** - Sprint planning and milestones\n"
    response += "5. **MVP definition** - Minimum viable product scope\n\n"
    
    response += "💡 **PRO TIPS:**\n"
    response += "• Start with a minimum viable product (MVP)\n"
    response += "• Use agile methodology for iterative development\n"
    response += "• Focus on user experience from day one\n"
    response += "• Implement continuous integration/deployment\n\n"
    
    response += "🔍 **Would you like me to elaborate on any specific aspect?**\n"
    response += "• Technical architecture details\n"
    response += "• Feature prioritization strategy\n"
    response += "• Development timeline breakdown\n"
    response += "• Technology alternatives\n"
    
    return response

def advanced_llm_response(user_message, user_id=None):
    """Enhanced LLM response function with proper project detection"""
    print(f"📨 Received message: '{user_message}'")
    
    try:
        # Check if this is a project creation request (use your existing detection)
        if is_project_creation_request(user_message):
            print("🎯 Detected project creation request")
            
            # Create the project with enhanced detection
            project_data, detected_type = create_project_from_prompt(user_message, user_id)
            print(f"🔧 Created project of type: {detected_type}")
            
            # Generate analysis
            analysis = {
                'domains': [detected_type],
                'complexity': project_data['estimated_complexity'],
                'has_specific_goal': len(user_message.split()) > 3
            }
            
            # Generate comprehensive response
            response = generate_comprehensive_response(project_data, analysis, user_message)
            
            return response
        
        else:
            # Enhanced conversational responses with GPT-style thinking
            responses = {
                "hello": """💭 **Thinking:** User is initiating conversation. Should provide warm greeting and guide toward project creation.

👋 **Hello! I'm your AI Project Architect!** 

I specialize in helping transform ideas into detailed project plans. I can analyze your requirements, suggest architectures, and create comprehensive project blueprints.

**Try me with:** "Create a [your project idea]" or "Build a [specific tool]" """,

                "hi": """💭 **Analysis:** Casual greeting detected. Should maintain friendly tone while demonstrating capabilities.

👋 **Hi there!** I'm excited to help you bring your project ideas to life! 

I can create detailed plans for:
• 🌐 Web applications & platforms
• 📊 Data analysis & visualization tools  
• 💬 AI chatbots & assistants
• ⚙️ Automation systems & workflows

**What would you like to build today?**""",

                "how are you": """💭 **Context:** User is checking system status. Should confirm operational status while redirecting to project focus.

🤖 **I'm functioning optimally and ready to architect your next project!** 

My systems are:
✅ Project analysis engine: **Online**
✅ Architecture generator: **Active** 
✅ Tech stack recommender: **Operational**
✅ Timeline estimator: **Ready**

**What project shall we design together?**""",

                "project": """💭 **Analysis:** User mentioned projects. Should provide comprehensive project creation guidance.

💡 **PROJECT CREATION MODE ACTIVATED!**

I can help you design and plan various types of projects:

🌐 **Web Applications**
- E-commerce platforms, SaaS products, portfolios
- *Example: "Create a task management web app"*

📊 **Data Tools** 
- Dashboards, analytics platforms, reporting systems
- *Example: "Build a sales data analyzer"*

💬 **AI Assistants**
- Chatbots, customer support agents, virtual assistants
- *Example: "Make a FAQ chatbot for my website"*

⚙️ **Automation Systems**
- Workflow automators, scheduled tasks, integration tools
- *Example: "Develop a social media scheduler"*

**What specific project would you like to create?**""",

                "create": """💭 **Thinking:** User is interested in creation. Should provide clear examples and encouragement.

🚀 **EXCELLENT! Let's create something amazing together!**

Here's how I can help you:

1. **Describe your idea** in natural language
2. **I'll analyze** requirements and complexity
3. **Generate a blueprint** with features and tech stack
4. **Provide timeline** and development guidance

**Quick Start Examples:**
- "Create a mobile app for fitness tracking"
- "Build a dashboard for website analytics" 
- "Make an automation tool for email marketing"
- "Develop a platform for online courses"

**What's your project idea?**""",

                "what can you do": """💭 **Analysis:** User wants to understand capabilities. Should provide comprehensive overview.

🛠️ **I'm a comprehensive Project Design Assistant!**

**MY CAPABILITIES:**

📋 **Project Analysis**
- Requirement extraction from natural language
- Complexity assessment and scope definition
- Domain-specific architecture planning

🔧 **Technical Architecture** 
- Technology stack recommendations
- System component identification
- Scalability and security considerations

⏱️ **Project Planning**
- Timeline estimation and milestone planning
- Resource requirement assessment
- Risk identification and mitigation

💡 **Feature Design**
- Core functionality specification
- User experience considerations
- Integration point identification

**Try me with any project idea!**"""
            }
            
            lower_msg = user_message.lower().strip()
            print(f"🔍 Processing message: '{lower_msg}'")
            
            # Enhanced keyword matching with context awareness
            matched_response = None
            for key, response_text in responses.items():
                if key in lower_msg:
                    matched_response = response_text
                    break
            
            if matched_response:
                print(f"✅ Found contextual response")
                return matched_response
            
            # Enhanced default response with thinking process
            thinking_process = """💭 **Analysis:** User input doesn't match predefined patterns. 
Should provide helpful guidance while demonstrating project creation capabilities.

🔍 **I understand you're looking for assistance.** Let me help you get started!"""
            
            default_response = f"{thinking_process}\n\n"
            default_response += "🎯 **I SPECIALIZE IN PROJECT CREATION & ARCHITECTURE**\n\n"
            default_response += "**I can help you design:**\n"
            default_response += "• Complete web applications 🌐\n"
            default_response += "• Data analysis platforms 📈\n"
            default_response += "• AI-powered chatbots 🤖\n"
            default_response += "• Automation workflows ⚙️\n"
            default_response += "• Mobile applications 📱\n"
            default_response += "• Game prototypes 🎮\n\n"
            
            default_response += "💡 **Simply describe what you want to build:**\n"
            default_response += "- \"Create a [your idea]\"\n"
            default_response += "- \"Build a [specific tool]\"\n"
            default_response += "- \"I need a [type of application]\"\n\n"
            
            default_response += "**Example:** \"Create a recipe sharing platform with user profiles and ratings\""
            
            print("✅ Using enhanced default response")
            return default_response
            
    except Exception as e:
        error_response = f"""💭 **System Notice:** An error occurred during processing.

❌ **Technical Issue Detected:** {str(e)}

But don't worry! I can still help you create projects. 

**Try a simple project request like:** "Create a web application for [your purpose]"

The system will continue functioning in basic mode."""
        
        print(f"❌ Error in advanced_llm_response: {e}")
        return error_response

print("✅ llm_handler.py loaded successfully with enhanced responses")
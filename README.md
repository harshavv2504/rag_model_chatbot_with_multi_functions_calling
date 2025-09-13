# ☕ Langchain Coffee Business Chatbot UI

A sophisticated AI-powered chatbot built with FastAPI and Langchain, designed specifically for coffee business consultation and sales qualification. Features Logan, an expert coffee business consultant from Abbotsford Road Coffee Specialists, who provides intelligent responses based on a comprehensive knowledge base and handles sales qualification workflows.

## 🚀 Features

### 🤖 **Intelligent Coffee Business Assistant**
- **Expert Knowledge Base**: 25+ comprehensive MDX files covering coffee business strategies, operations, and best practices
- **Natural Conversation**: Logan introduces himself and maintains a professional, helpful persona throughout interactions
- **Real-time WebSocket Communication**: Instant responses with live typing indicators
- **Function Calling**: Advanced AI capabilities for data extraction, sales qualification, and business logic
- **Knowledge Base Search**: Intelligent search across all coffee business topics with fuzzy matching
- **Topic Discovery**: Dynamic topic listing and specific entry retrieval

### 📊 **Sales Qualification System**
- **Multi-Persona Support**: Handles three distinct user types:
  - **Normal Users**: General coffee business information
  - **New Café Entrepreneurs**: Complete startup qualification workflow
  - **Existing Business Owners**: Service improvement and supplier evaluation
- **Structured Data Collection**: Automated extraction of business details, contact information, and requirements
- **Lead Scoring**: Intelligent prioritization (HIGH/MEDIUM/LOW) based on qualification data
- **Sales Handoff**: Professional summary generation for sales team follow-up
- **Lead Management**: High-priority lead retrieval and comprehensive lead summaries
- **Data Persistence**: JSON-based storage with automatic data integrity validation

### 🎯 **Conversation Management**
- **Intent Classification**: Automatically detects user intent and business context
- **Dynamic Flow Control**: Adapts conversation strategy based on user responses
- **One-Question-at-a-Time**: Structured qualification process prevents overwhelming users
- **Context Awareness**: Maintains conversation history and business context
- **Conversation Rules**: Strict guidelines preventing generic advice and maintaining business focus

### 👥 **Customer Management System**
- **Customer Lookup**: Find customers by phone, email, or customer ID with intelligent format recognition
- **Account Creation**: New customer registration with comprehensive validation
- **Customer Data**: Access to customer profiles, appointment history, and order records
- **Data Validation**: Phone number, email, and name format validation with error handling

### 📅 **Appointment & Meeting Management**
- **Appointment Scheduling**: Complete workflow from customer identification to booking confirmation
- **Availability Checking**: Real-time slot availability with business hours validation
- **Meeting Rescheduling**: Flexible appointment modification with conflict detection
- **Status Management**: Appointment status updates (Scheduled, Completed, Cancelled)
- **Calendar Integration**: Automatic Google Calendar event creation with timezone detection
- **Email Notifications**: Personalized meeting confirmations via Gmail API
- **Workflow Enforcement**: Mandatory sequence: find customer → check availability → present options → book appointment

### 🔧 **Advanced Business Logic**
- **Mock Data System**: Comprehensive test data generation with 100+ customers, appointments, and orders
- **Data Integrity**: Automatic validation for duplicate IDs and orphaned records
- **Memory Management**: Persistent data storage with automatic sync and reload capabilities
- **Error Handling**: Robust error management with detailed logging and graceful degradation
- **Performance Optimization**: Artificial delay simulation for realistic API response times

### 📈 **Analytics & Reporting**
- **Lead Analytics**: Comprehensive lead scoring and priority analysis
- **Sales Pipeline**: Visual representation of lead distribution by priority
- **Performance Metrics**: Lead conversion tracking and qualification success rates
- **Data Export**: JSON-based data export for external analysis and CRM integration

### 🔐 **Security & Integration**
- **Google API Integration**: Gmail and Google Calendar API integration for meeting management
- **OAuth2 Authentication**: Secure token-based authentication for Google services
- **Data Encryption**: Secure data transmission and storage
- **API Rate Limiting**: Intelligent rate limiting and error handling for external APIs

## 🏗️ Architecture

### **Core Components**

```
├── knowledge_based_chatbot.py     # Main chatbot logic with function calling
├── web_knowledge_chatbot.py      # FastAPI web interface with WebSocket support
├── static/                        # Frontend assets
│   ├── index.html                # Chat interface
│   ├── script.js                 # WebSocket client logic
│   └── style.css                 # Modern UI styling
├── knowledge/                     # MDX knowledge base
│   ├── enhanced_coffee_knowledge_handler.py
│   └── *.mdx                     # 25+ coffee business knowledge files
└── common/                        # Shared business logic
    ├── agent_functions.py        # Function definitions and mappings
    ├── business_logic.py         # Data storage and lead scoring
    ├── agent_templates.py        # Dynamic prompt generation
    └── prompt_templates.py       # Core AI personality and instructions
```

### **Technology Stack**
- **Backend**: FastAPI, Python 3.8+
- **AI/ML**: Langchain, OpenAI GPT-3.5-turbo
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Communication**: WebSocket for real-time chat
- **Data Storage**: JSON files for conversation and qualification data
- **Knowledge Base**: MDX format for structured content

## 🛠️ Installation

### **Prerequisites**
- Python 3.8 or higher
- OpenAI API key
- Git

### **Setup Instructions**

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/langchain-coffee-chatbot.git
   cd langchain-coffee-chatbot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   Create a `.env` file in the root directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Run the application**
   ```bash
   python web_knowledge_chatbot.py
   ```

5. **Access the chatbot**
   Open your browser and navigate to `http://localhost:8000`

## 📚 Knowledge Base

The chatbot is powered by a comprehensive knowledge base containing 25+ MDX files covering:

### **Business Strategies**
- Coffee menu design and optimization
- Sales improvement strategies
- Pricing strategies and profit optimization
- Customer experience and retention
- Operational efficiency

### **Technical Expertise**
- Specialty coffee journey and origins
- Equipment selection and maintenance
- Quality control and calibration
- Storage and freshness techniques
- Team training and development

### **Case Studies & Success Stories**
- Real-world implementation examples
- Profit improvement case studies
- Equipment selection guidance
- Brand development strategies

## 🎭 Logan's Character

**Logan from Abbotsford Road Coffee Specialists** is the AI assistant's persona:

- **Professional**: Expert coffee business consultant with deep industry knowledge
- **Helpful**: Always provides actionable advice tied to business success
- **Conversational**: Natural, friendly tone that builds rapport
- **Sales-Focused**: Intelligently qualifies leads and guides toward solutions
- **Knowledge-Driven**: Only provides information from the knowledge base

### **Conversation Rules**
- Introduces himself once at the start of each conversation
- Never gives generic advice without tying to offerings
- Asks one question at a time during qualification
- Maintains professional business focus throughout
- Extracts and stores qualification data automatically

## 🔧 API Reference

### **WebSocket Endpoints**

#### `ws://localhost:8000/ws`
Real-time chat communication endpoint.

**Message Types:**
- `user_message`: User input
- `ai_message`: Bot responses
- `system_message`: System notifications
- `function_result`: Function execution results

### **Function Calling**

The chatbot supports 20+ advanced functions across multiple categories:

#### **Sales Qualification Functions**
- `extract_qualification_data`: Collects business information and stores qualification data
- `generate_sales_handoff`: Creates professional sales team summaries
- `get_high_priority_leads`: Retrieves high-priority qualified leads
- `get_lead_summary`: Provides comprehensive lead overview and analytics

#### **Customer Management Functions**
- `find_customer`: Intelligent customer lookup by phone, email, or ID with format recognition
- `create_customer_account`: New customer registration with comprehensive validation
- `get_customer_appointments`: Retrieves customer appointment history
- `get_customer_orders`: Accesses customer order history and status

#### **Appointment & Meeting Functions**
- `start_meeting_scheduling`: Initiates meeting scheduling workflow with availability checking
- `finish_meeting_scheduling`: Completes appointment booking after customer selection
- `check_availability`: Real-time slot availability checking with business hours validation
- `reschedule_appointment`: Flexible appointment modification with conflict detection
- `update_appointment_status`: Updates appointment status (Scheduled, Completed, Cancelled)

#### **Knowledge Base Functions**
- `search_knowledge_base`: Intelligent search across coffee business topics with fuzzy matching
- `get_knowledge_base_topics`: Lists all available coffee business topics
- `get_knowledge_base_entry`: Retrieves specific knowledge base entries by topic or title

#### **System Functions**
- `end_call`: Graceful conversation termination with farewell messages

## 📊 Sales Qualification Workflow

### **New Café Entrepreneurs**
1. **Timeline**: When are you planning to open?
2. **Coffee Style**: What kind of experience do you want to create?
3. **Equipment**: Starting fresh or have existing equipment?
4. **Volume**: Expected daily customer count?
5. **Contact Info**: Name, email, phone for follow-up

### **Existing Business Owners**
1. **Pain Points**: Current supplier frustrations?
2. **Scale**: Number of locations?
3. **Support Needs**: Training, service, menu development?
4. **Coffee Preferences**: Current style satisfaction?
5. **Contact Info**: Contact details for proposals

### **Lead Scoring System**
- **HIGH Priority (80-100)**: Complete contact info + urgent timeline + clear pain points
- **MEDIUM Priority (60-79)**: Partial info + medium timeline + some requirements
- **LOW Priority (0-59)**: Basic info + no timeline + general interest

## 🎨 UI Features

### **Modern Chat Interface**
- Clean, professional design
- Real-time message delivery
- Typing indicators
- Connection status monitoring
- Responsive layout for all devices

### **User Experience**
- Instant responses via WebSocket
- Smooth scrolling message history
- Clear visual distinction between user and bot messages
- Professional color scheme and typography

## 🧪 Testing

The project includes comprehensive testing capabilities:

### **Test Categories**
- **Knowledge Base Tests**: Verify information accuracy and response quality
- **Sales Qualification Tests**: Validate lead collection and scoring
- **Function Calling Tests**: Ensure proper AI function execution
- **Conversation Flow Tests**: Test natural dialogue progression
- **Customer Management Tests**: Validate customer lookup and account creation
- **Appointment Tests**: Test scheduling, rescheduling, and status management
- **Integration Tests**: Verify Google API integration and email/calendar functionality

### **Mock Data System**
- **100+ Test Customers**: Generated with realistic data for comprehensive testing
- **Appointment History**: Multiple appointment types and statuses for testing
- **Order Records**: Complete order history with various statuses
- **Data Integrity**: Automatic validation and duplicate detection
- **Sample Data**: Curated sample data for demonstration and testing

### **Running Tests**
```bash
# Example test execution
python test_knowledge_base.py
python test_sales_qualification.py
python test_customer_management.py
python test_appointment_system.py
```

## 🔒 Security & Privacy

- **API Key Protection**: Environment variable storage
- **Data Encryption**: Secure data transmission via WebSocket
- **Privacy Compliance**: No personal data stored beyond conversation context
- **Input Validation**: Sanitized user inputs and function parameters
- **OAuth2 Integration**: Secure Google API authentication with token management
- **Data Integrity**: Automatic validation and duplicate detection
- **Error Handling**: Comprehensive error management with graceful degradation

## 🔗 Google API Integration

### **Gmail Integration**
- **Meeting Confirmations**: Automatic personalized email notifications
- **Professional Templates**: Branded email templates for meeting confirmations
- **Multi-Attendee Support**: Send emails to multiple meeting participants
- **Error Handling**: Robust error management for email delivery failures

### **Google Calendar Integration**
- **Automatic Event Creation**: Seamless calendar event generation
- **Timezone Detection**: Intelligent timezone handling for global users
- **Meeting Details**: Complete event information with descriptions and locations
- **Attendee Management**: Automatic attendee invitation and calendar updates
- **Reminder Settings**: Default reminder configuration for all meetings

### **Setup Requirements**
```bash
# Required Google API credentials
- Gmail API credentials (credentials.json)
- Google Calendar API credentials
- OAuth2 token files (token_gmail.json, token_calendar.json)
```

## 🚀 Deployment

### **Production Deployment**
1. Set up production environment variables
2. Configure reverse proxy (nginx recommended)
3. Set up SSL certificates
4. Configure monitoring and logging
5. Deploy using Docker or direct Python deployment

### **Docker Support**
```dockerfile
# Example Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "web_knowledge_chatbot.py"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### **Development Guidelines**
- Follow PEP 8 Python style guidelines
- Add comprehensive tests for new features
- Update documentation for API changes
- Maintain backward compatibility

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### **Common Issues**

**Q: The chatbot isn't responding**
A: Check your OpenAI API key and internet connection. Ensure the API key has sufficient credits.

**Q: WebSocket connection fails**
A: Verify the server is running on port 8000 and check firewall settings.

**Q: Knowledge base not loading**
A: Ensure all MDX files are in the `knowledge/` directory and check file permissions.

### **Getting Help**
- Create an issue on GitHub
- Check the troubleshooting section
- Review the API documentation
- Contact the development team

## 🎯 Roadmap

### **Planned Features**
- [ ] Voice input/output support
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] CRM integration
- [ ] Mobile app development
- [ ] Advanced lead nurturing workflows

### **Version History**
- **v1.0.0**: Initial release with basic chatbot functionality
- **v1.1.0**: Added sales qualification system
- **v1.2.0**: Implemented function calling and lead scoring
- **v1.3.0**: Enhanced UI and conversation management

## 🙏 Acknowledgments

- **Langchain**: For the powerful AI framework
- **FastAPI**: For the high-performance web framework
- **OpenAI**: For the GPT-3.5-turbo model
- **Coffee Industry Experts**: For the comprehensive knowledge base content

---

**Built with ❤️ for the coffee business community**

*Transform your coffee business with AI-powered insights and intelligent sales qualification.*

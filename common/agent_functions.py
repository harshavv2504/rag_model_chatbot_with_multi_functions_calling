import json
from datetime import datetime, timedelta
import asyncio
from common.business_logic import (
    get_customer,
    get_customer_appointments,
    get_customer_orders,
    schedule_appointment,
    get_available_appointment_slots,
    reschedule_appointment,
    update_appointment_status,
    prepare_farewell_message,
    handle_meeting_scheduling_request,
    complete_meeting_scheduling,
    store_qualification_data,
    create_sales_handoff_summary,
    get_qualification_data,
    get_high_priority_leads,
    get_lead_summary,
)

# Import coffee knowledge base handler
try:
    from knowledge.enhanced_coffee_knowledge_handler import EnhancedCoffeeKnowledgeBase
    coffee_kb = EnhancedCoffeeKnowledgeBase("knowledge")
except ImportError:
    coffee_kb = None


async def find_customer(params):
    """Look up a customer by phone, email, or ID."""
    phone = params.get("phone")
    email = params.get("email")
    customer_id = params.get("customer_id")

    result = await get_customer(phone=phone, email=email, customer_id=customer_id)
    return result


async def get_appointments(params):
    """Get appointments for a customer."""
    customer_id = params.get("customer_id")
    if not customer_id:
        return {"error": "customer_id is required"}

    result = await get_customer_appointments(customer_id)
    return result


async def get_orders(params):
    """Get orders for a customer."""
    customer_id = params.get("customer_id")
    if not customer_id:
        return {"error": "customer_id is required"}

    result = await get_customer_orders(customer_id)
    return result


async def create_appointment(params):
    """Schedule a new appointment."""
    customer_id = params.get("customer_id")
    date = params.get("date")
    service = params.get("service")

    if not all([customer_id, date, service]):
        return {"error": "customer_id, date, and service are required"}

    result = await schedule_appointment(customer_id, date, service)
    return result


async def check_availability(params):
    """Check available appointment slots."""
    start_date = params.get("start_date")
    end_date = params.get(
        "end_date", (datetime.fromisoformat(start_date) + timedelta(days=7)).isoformat()
    )

    if not start_date:
        return {"error": "start_date is required"}

    result = await get_available_appointment_slots(start_date, end_date)
    return result


async def reschedule_appointment_func(params):
    """Reschedule an existing appointment."""
    appointment_id = params.get("appointment_id")
    new_date = params.get("new_date")
    new_service = params.get("new_service")

    if not all([appointment_id, new_date, new_service]):
        return {"error": "appointment_id, new_date, and new_service are required"}

    result = await reschedule_appointment(appointment_id, new_date, new_service)
    return result


# Removed cancel_appointment_func - not needed for coffee business chatbot


async def update_appointment_status_func(params):
    """Update the status of an existing appointment."""
    appointment_id = params.get("appointment_id")
    new_status = params.get("new_status")

    if not all([appointment_id, new_status]):
        return {"error": "appointment_id and new_status are required"}

    result = await update_appointment_status(appointment_id, new_status)
    return result




async def end_call(websocket, params):
    """
    End the conversation and close the connection.
    """
    farewell_type = params.get("farewell_type", "general")
    result = await prepare_farewell_message(websocket, farewell_type)
    return result


async def search_knowledge_base(params):
    """Search the coffee business knowledge base for specific information."""
    if not coffee_kb:
        return {"error": "Knowledge base not available"}
    
    query = params.get("query", "")
    if not query:
        return {"error": "Search query is required"}
    
    try:
        results = coffee_kb.search_knowledge_base(query)
        if results:
            # Return the most relevant result
            best_match = results[0]
            return {
                "found": True,
                "title": best_match.get("title", ""),
                "topic": best_match.get("topic", ""),
                "content": best_match.get("content_raw", ""),
                "tags": best_match.get("tags", []),
                "total_results": len(results)
            }
        else:
            return {"found": False, "message": "No information found for that query"}
    except Exception as e:
        return {"error": f"Error searching knowledge base: {str(e)}"}


async def get_knowledge_base_topics(params):
    """Get all available topics in the coffee business knowledge base."""
    if not coffee_kb:
        return {"error": "Knowledge base not available"}
    
    try:
        topics = coffee_kb.get_topics()
        return {
            "topics": topics,
            "total_topics": len(topics)
        }
    except Exception as e:
        return {"error": f"Error getting topics: {str(e)}"}


async def get_knowledge_base_entry(params):
    """Get a specific entry from the coffee business knowledge base by topic or title."""
    if not coffee_kb:
        return {"error": "Knowledge base not available"}
    
    topic = params.get("topic", "")
    title = params.get("title", "")
    
    if not topic and not title:
        return {"error": "Either topic or title is required"}
    
    try:
        if topic:
            # Search by topic using fuzzy search
            results = coffee_kb.search_knowledge_base(topic)
            if results:
                # Return the first result for this topic
                entry = results[0]
                return {
                    "found": True,
                    "title": entry.get("title", ""),
                    "topic": entry.get("topic", ""),
                    "content": entry.get("content_raw", ""),
                    "tags": entry.get("tags", [])
                }
            else:
                return {"found": False, "message": f"No entries found for topic: {topic}"}
        else:
            # Search by title - try exact match first, then fuzzy search
            entries = coffee_kb._get_entries_cached()
            if not entries:
                return {"found": False, "message": "Knowledge base is empty"}
            
            # First try exact title match
            title_lower = title.lower().strip()
            for entry in entries:
                entry_title = entry.get("title", "").lower().strip()
                if entry_title == title_lower:
                    return {
                        "found": True,
                        "title": entry.get("title", ""),
                        "topic": entry.get("topic", ""),
                        "content": entry.get("content_raw", ""),
                        "tags": entry.get("tags", [])
                    }
            
            # If no exact match, try fuzzy search as fallback
            results = coffee_kb.search_knowledge_base(title)
            if results:
                entry = results[0]
                return {
                    "found": True,
                    "title": entry.get("title", ""),
                    "topic": entry.get("topic", ""),
                    "content": entry.get("content_raw", ""),
                    "tags": entry.get("tags", [])
                }
            else:
                return {"found": False, "message": f"No entries found for title: {title}"}
    except Exception as e:
        return {"error": f"Error getting entry: {str(e)}"}


async def create_customer_account(params):
    """Create a new customer account with proper validation."""
    # Import here to avoid circular import issues
    try:
        from common.business_logic import create_new_customer
    except ImportError:
        return {"error": "Customer creation service temporarily unavailable"}
    
    name = params.get("name", "").strip()
    phone = params.get("phone", "").strip()
    email = params.get("email", "").strip()
    
    # Validate required fields
    if not name:
        return {"error": "Customer name is required"}
    if not phone:
        return {"error": "Phone number is required"}
    if not email:
        return {"error": "Email address is required"}
    
    # Basic format validation
    if len(name) < 2:
        return {"error": "Name must be at least 2 characters long"}
    
    # Phone validation (basic)
    if not phone.startswith("+") or len(phone) < 10:
        return {"error": "Phone number must be in international format (e.g., +15551234567)"}
    
    # Email validation (basic)
    if "@" not in email or "." not in email:
        return {"error": "Please provide a valid email address"}
    
    try:
        result = await create_new_customer(name, phone, email)
        return result
    except Exception as e:
        return {"error": f"Error creating customer: {str(e)}"}


async def start_meeting_scheduling(params):
    """
    Start the meeting scheduling process with proper workflow enforcement.
    This function enforces the correct sequence: find customer -> check availability -> present options.
    """
    customer_id = params.get("customer_id")
    phone = params.get("phone")
    email = params.get("email")
    
    # Determine identifier type and value
    if customer_id:
        identifier = customer_id
        identifier_type = "customer_id"
    elif phone:
        identifier = phone
        identifier_type = "phone"
    elif email:
        identifier = email
        identifier_type = "email"
    else:
        return {"error": "Customer identification required (customer_id, phone, or email)"}
    
    try:
        result = await handle_meeting_scheduling_request(identifier, identifier_type)
        return result
    except Exception as e:
        return {"error": f"Error starting meeting scheduling: {str(e)}"}


async def finish_meeting_scheduling(params):
    """
    Complete the meeting scheduling process after customer has selected a time slot.
    """
    customer_id = params.get("customer_id")
    selected_slot = params.get("selected_slot")
    service_type = params.get("service_type", "Consultation")
    
    if not customer_id:
        return {"error": "Customer ID is required"}
    if not selected_slot:
        return {"error": "Selected time slot is required"}
    
    try:
        result = await complete_meeting_scheduling(customer_id, selected_slot, service_type)
        return result
    except Exception as e:
        return {"error": f"Error completing meeting scheduling: {str(e)}"}


# Sales Qualification Functions
async def extract_qualification_data(params):
    """
    Extract and store business qualification data from conversation.
    """
    try:
        # Extract data from parameters
        qualification_data = {
            "business_type": params.get("business_type", ""),
            "timeline": params.get("timeline", ""),
            "pain_points": params.get("pain_points", ""),
            "business_scale": params.get("business_scale", ""),
            "coffee_style": params.get("coffee_style", ""),
            "equipment_needs": params.get("equipment_needs", ""),
            "volume": params.get("volume", ""),
            "support_needs": params.get("support_needs", ""),
            "contact_name": params.get("contact_name", ""),
            "contact_phone": params.get("contact_phone", ""),
            "contact_email": params.get("contact_email", ""),
            "contact_role": params.get("contact_role", ""),
            "timestamp": datetime.now().isoformat()
        }
        
        # Store the data using business logic
        result = await store_qualification_data(qualification_data)
        
        return {
            "success": True,
            "message": f"Qualification data stored for {qualification_data.get('contact_name', 'Unknown')}",
            "data": qualification_data
        }
        
    except Exception as e:
        return {"error": f"Error extracting qualification data: {str(e)}"}


async def generate_sales_handoff(params):
    """
    Generate a professional sales handoff summary.
    """
    try:
        qualification_id = params.get("qualification_id")
        conversation_summary = params.get("conversation_summary", "")
        
        if not qualification_id:
            return {"error": "Qualification ID is required"}
        
        # Get the qualification data
        qualification_data = await get_qualification_data(qualification_id)
        
        if not qualification_data:
            return {"error": "Qualification data not found"}
        
        # Generate handoff summary
        handoff_summary = await create_sales_handoff_summary(qualification_data, conversation_summary)
        
        return {
            "success": True,
            "message": "Sales handoff summary generated successfully",
            "handoff_summary": handoff_summary
        }
        
    except Exception as e:
        return {"error": f"Error generating sales handoff: {str(e)}"}

async def get_high_priority_leads(params):
    """
    Get all high-priority leads for sales team follow-up.
    """
    try:
        leads = await get_high_priority_leads()
        
        return {
            "success": True,
            "message": f"Found {len(leads)} high-priority leads",
            "leads": leads
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error retrieving high-priority leads: {str(e)}"
        }

async def get_lead_summary(params):
    """
    Get a summary of all leads with counts by priority.
    """
    try:
        summary = await get_lead_summary()
        
        return {
            "success": True,
            "message": "Lead summary retrieved successfully",
            "summary": summary
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error retrieving lead summary: {str(e)}"
        }

async def get_qualification_data(qualification_id):
    """
    Retrieve qualification data by ID.
    """
    try:
        # This would typically query a database
        # For now, we'll use file-based storage
        import json
        import os
        
        data_file = "sales_qualification_data.json"
        if os.path.exists(data_file):
            with open(data_file, 'r') as f:
                data = json.load(f)
                qualifications = data.get('qualifications', [])
                
                # Find the qualification by ID (using timestamp as ID for now)
                for qual in qualifications:
                    if qual.get('timestamp') == qualification_id:
                        return qual
        
        return None
        
    except Exception as e:
        print(f"Error retrieving qualification data: {str(e)}")
        return None


# Function definitions that will be sent to the Voice Agent API
FUNCTION_DEFINITIONS = [
    {
        "type": "function",
        "name": "find_customer",
        "description": """Look up a customer's account information. Use context clues to determine what type of identifier the user is providing:

        Customer ID formats:
        - Numbers only (e.g., '169', '42') → Format as 'CUST0169', 'CUST0042'
        - With prefix (e.g., 'CUST169', 'customer 42') → Format as 'CUST0169', 'CUST0042'
        
        Phone number recognition:
        - Standard format: '555-123-4567' → Format as '+15551234567'
        - With area code: '(555) 123-4567' → Format as '+15551234567'
        - Spoken naturally: 'five five five, one two three, four five six seven' → Format as '+15551234567'
        - International: '+1 555-123-4567' → Use as is
        - Always add +1 country code if not provided
        
        Email address recognition:
        - Spoken naturally: 'my email is john dot smith at example dot com' → Format as 'john.smith@example.com'
        - With domain: 'john@example.com' → Use as is
        - Spelled out: 'j o h n at example dot com' → Format as 'john@example.com'
        
        IMPORTANT: If the customer wants to schedule a meeting and you successfully find their account, you MUST immediately call check_availability() next!""",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "Customer's ID. Format as CUSTXXXX where XXXX is the number padded to 4 digits with leading zeros. Example: if user says '42', pass 'CUST0042'",
                },
                "phone": {
                    "type": "string",
                    "description": """Phone number with country code. Format as +1XXXXXXXXXX:
                    - Add +1 if not provided
                    - Remove any spaces, dashes, or parentheses
                    - Convert spoken numbers to digits
                    Example: 'five five five one two three four five six seven' → '+15551234567'""",
                },
                "email": {
                    "type": "string",
                    "description": """Email address in standard format:
                    - Convert 'dot' to '.'
                    - Convert 'at' to '@'
                    - Remove spaces between spelled out letters
                    Example: 'j dot smith at example dot com' → 'j.smith@example.com'""",
                },
            },
        },
    },
    {
        "type": "function",
        "name": "get_appointments",
        "description": """Retrieve all appointments for a customer. Use this function when:
        - A customer asks about their upcoming appointments
        - A customer wants to know their appointment schedule
        - A customer asks 'When is my next appointment?'
        
        Always verify you have the customer's account first using find_customer before checking appointments.""",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "Customer's ID in CUSTXXXX format. Must be obtained from find_customer first.",
                }
            },
            "required": ["customer_id"],
        },
    },
    {
        "type": "function",
        "name": "get_orders",
        "description": """Retrieve order history for a customer. Use this function when:
        - A customer asks about their orders
        - A customer wants to check order status
        - A customer asks questions like 'Where is my order?' or 'What did I order?'
        
        Always verify you have the customer's account first using find_customer before checking orders.""",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "Customer's ID in CUSTXXXX format. Must be obtained from find_customer first.",
                }
            },
            "required": ["customer_id"],
        },
    },
    {
        "type": "function",
        "name": "create_appointment",
        "description": """Schedule a new appointment for a customer. Use this function when:
        - A customer wants to book a new appointment
        - A customer asks to schedule a service
        
        CRITICAL WORKFLOW - MUST FOLLOW THIS ORDER:
        1. FIRST: Use find_customer to identify the customer (phone, email, or customer_id)
        2. SECOND: Use check_availability to find available time slots
        3. THIRD: Confirm date/time and service type with customer
        4. FOURTH: Use create_appointment with the verified customer_id
        
        NEVER schedule an appointment without first identifying the customer!""",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "Customer's ID in CUSTXXXX format. Must be obtained from find_customer first.",
                },
                "date": {
                    "type": "string",
                    "description": "Appointment date and time in ISO format (YYYY-MM-DDTHH:MM:SS). Must be a time slot confirmed as available.",
                },
                "service": {
                    "type": "string",
                    "description": "Type of service requested. Must be one of the following: Consultation, Follow-up, Review, or Planning",
                    "enum": ["Consultation", "Follow-up", "Review", "Planning"],
                },
            },
            "required": ["customer_id", "date", "service"],
        },
    },
    {
        "type": "function",
        "name": "check_availability",
        "description": """Check available appointment slots within a date range. Use this function when:
        - A customer wants to know available appointment times
        - Before scheduling a new appointment
        - A customer asks 'When can I come in?' or 'What times are available?'
        
        MANDATORY WORKFLOW: After finding a customer who wants to schedule a meeting, you MUST call this function before asking them about their preferred time.
        
        After checking availability, present options to the customer in a natural way, like:
        'I have openings on [date] at [time] or [date] at [time]. Which works better for you?'""",
        "parameters": {
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "description": "Start date in ISO format (YYYY-MM-DDTHH:MM:SS). Usually today's date for immediate availability checks.",
                },
                "end_date": {
                    "type": "string",
                    "description": "End date in ISO format. Optional - defaults to 7 days after start_date. Use for specific date range requests.",
                },
            },
            "required": ["start_date"],
        },
    },
    {
        "type": "function",
        "name": "end_call",
        "description": """End the conversation and close the connection. Call this function when:
        - User says goodbye, thank you, etc.
        - User indicates they're done ("that's all I need", "I'm all set", etc.)
        - User wants to end the conversation
        
        Examples of triggers:
        - "Thank you, bye!"
        - "That's all I needed, thanks"
        - "Have a good day"
        - "Goodbye"
        - "I'm done"
        
        Do not call this function if the user is just saying thanks but continuing the conversation.""",
        "parameters": {
            "type": "object",
            "properties": {
                "farewell_type": {
                    "type": "string",
                    "description": "Type of farewell to use in response",
                    "enum": ["thanks", "general", "help"],
                }
            },
            "required": ["farewell_type"],
        },
    },
    {
        "type": "function",
        "name": "search_knowledge_base",
        "description": """Search the coffee business knowledge base for specific information. Use this function when:
        - Users ask questions about coffee business strategies, operations, sales, or management
        - Users want to know about specific topics like menu design, pricing, equipment, or customer retention
        - Users ask "How can I improve my coffee shop?" or "Tell me about coffee business strategies"
        - Users want information about specific areas like sales improvement, operational efficiency, or team building
        
        DO NOT use this function for:
        - Questions about other industries (restaurants, retail, etc.)
        - Topics unrelated to coffee business
        - General business questions not specific to coffee shops
        
        This function searches across all available topics in the coffee business knowledge base only.""",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query or question from the user. Should be specific and relevant to coffee business strategies and operations.",
                }
            },
            "required": ["query"],
        },
    },
    {
        "type": "function",
        "name": "get_knowledge_base_topics",
        "description": """Get all available topics in the coffee business knowledge base. Use this function when:
        - Users ask "What topics can you tell me about?" or "What information do you have?"
        - Users want to know what areas of coffee business you can discuss
        - Users ask for an overview of available information
        - You need to show users what topics are available for discussion""",
        "parameters": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "type": "function",
        "name": "get_knowledge_base_entry",
        "description": """Get a specific entry from the coffee business knowledge base by topic or title. Use this function when:
        - Users ask for specific information about a particular coffee business topic
        - Users want detailed information about a specific area like "menu design" or "pricing strategies"
        - Users ask "Tell me more about [specific coffee business topic]"
        - You need to provide comprehensive information about a particular coffee business subject
        
        DO NOT use this function for:
        - Questions about other industries (restaurants, retail, etc.)
        - Topics unrelated to coffee business""",
        "parameters": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "The specific topic to search for (e.g., 'Sales Strategies', 'Menu Design', 'Pricing')",
                },
                "title": {
                    "type": "string",
                    "description": "The specific title to search for (e.g., 'Strategy One: Elevate Your Coffee Game')",
                }
            },
        },
    },
    {
        "type": "function",
        "name": "create_customer_account",
        "description": """Create a new customer account when they don't have one. Use this function when:
        - A customer says they need to create an account
        - A customer asks to sign up or register
        - A customer doesn't exist in the system and needs to be added
        - A customer wants to become a new client
        
        INITIAL RESPONSE: When a customer asks to create an account, respond with: "I can certainly help you with that! I just need a few details to do it."
        
        IMPORTANT: Always ask customers to spell out their details due to transcription accuracy issues.
        - Ask them to spell their name letter by letter
        - Ask them to spell their phone number digit by digit
        - Ask them to spell their email address letter by letter
        - Confirm all details before creating the account""",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Customer's full name. Ask them to spell it out letter by letter for accuracy.",
                },
                "phone": {
                    "type": "string",
                    "description": "Phone number in international format (e.g., +15551234567). Ask them to spell it digit by digit.",
                },
                "email": {
                    "type": "string",
                    "description": "Email address. Ask them to spell it out letter by letter for accuracy.",
                }
            },
            "required": ["name", "phone", "email"],
        },
    },
    {
        "type": "function",
        "name": "start_meeting_scheduling",
        "description": """Start the meeting scheduling process with proper workflow enforcement. Use this function when:
        - A customer wants to schedule a meeting and has provided their identification
        - A customer says "schedule a meeting" and you have their customer ID, phone, or email
        
        This function enforces the correct workflow:
        1. Finds the customer in the system
        2. Checks availability for the next 7 days
        3. Returns available time slots for the customer to choose from
        
        MANDATORY: Use this function instead of the old create_appointment function for meeting scheduling!""",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "Customer's ID in CUSTXXXX format. Use if customer provided their ID.",
                },
                "phone": {
                    "type": "string",
                    "description": "Phone number in international format (e.g., +15551234567). Use if customer provided their phone.",
                },
                "email": {
                    "type": "string",
                    "description": "Email address. Use if customer provided their email.",
                }
            },
        },
    },
    {
        "type": "function",
        "name": "finish_meeting_scheduling",
        "description": """Complete the meeting scheduling process after customer has selected a time slot. Use this function when:
        - A customer has chosen a specific time slot from the available options
        - A customer says "I'll take [time slot]" or "I want [time slot]"
        - A customer confirms their selection after you've shown them available slots
        - You need to book the appointment after presenting availability
        
        IMPORTANT: Use this function when the customer makes a selection, NOT start_meeting_scheduling again!
        
        This function creates the actual appointment in the system.""",
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "Customer's ID in CUSTXXXX format. Must be obtained from start_meeting_scheduling first.",
                },
                "selected_slot": {
                    "type": "string",
                    "description": "The time slot the customer selected in ISO format (YYYY-MM-DDTHH:MM:SS).",
                },
                "service_type": {
                    "type": "string",
                    "description": "Type of service for the appointment. Defaults to 'Consultation'.",
                    "enum": ["Consultation", "Follow-up", "Review", "Planning"],
                }
            },
            "required": ["customer_id", "selected_slot"],
        },
    },
    {
        "type": "function",
        "name": "reschedule_appointment",
        "description": """Reschedule an existing appointment to a new date and time. Use this function when:
        - A customer wants to change their appointment time
        - A customer asks to move their appointment to a different date
        - A customer needs to reschedule due to conflicts
        
        Before rescheduling:
        1. Get the appointment ID from get_appointments
        2. Check new availability using check_availability
        3. Confirm the new date/time and service with customer""",
        "parameters": {
            "type": "object",
            "properties": {
                "appointment_id": {
                    "type": "string",
                    "description": "The appointment ID (e.g., APT0001) to reschedule. Must be obtained from get_appointments first.",
                },
                "new_date": {
                    "type": "string",
                    "description": "New appointment date and time in ISO format (YYYY-MM-DDTHH:MM:SS). Must be a confirmed available time slot.",
                },
                "new_service": {
                    "type": "string",
                    "description": "Type of service for the rescheduled appointment. Must be one of: Consultation, Follow-up, Review, or Planning",
                    "enum": ["Consultation", "Follow-up", "Review", "Planning"],
                },
            },
            "required": ["appointment_id", "new_date", "new_service"],
        },
    },
    # Removed cancel_appointment function definition - not needed for coffee business chatbot
    {
        "type": "function",
        "name": "update_appointment_status",
        "description": """Update the status of an existing appointment. Use this function when:
        - Marking an appointment as completed after the meeting
        - Changing appointment status for administrative purposes
        - Updating appointment status based on customer feedback
        
        Valid statuses: Scheduled, Completed, Cancelled""",
        "parameters": {
            "type": "object",
            "properties": {
                "appointment_id": {
                    "type": "string",
                    "description": "The appointment ID (e.g., APT0001) to update. Must be obtained from get_appointments first.",
                },
                "new_status": {
                    "type": "string",
                    "description": "New status for the appointment",
                    "enum": ["Scheduled", "Completed", "Cancelled"],
                },
            },
            "required": ["appointment_id", "new_status"],
        },
    },
    {
        "type": "function",
        "name": "extract_qualification_data",
        "description": """Extract and store business qualification data from conversation. Use this function when:
        - User mentions they are opening a new café or coffee shop
        - User mentions they run an existing coffee business
        - User provides business information (timeline, scale, pain points, contact info)
        - User shows signs of being a business owner or decision maker
        
        This function helps collect key information for sales qualification and follow-up.""",
        "parameters": {
            "type": "object",
            "properties": {
                "business_type": {
                    "type": "string",
                    "description": "Type of business: new_cafe, existing_business, or unknown",
                    "enum": ["new_cafe", "existing_business", "unknown"]
                },
                "timeline": {
                    "type": "string",
                    "description": "When opening/switching (e.g., '2 weeks', 'next month', 'soon')"
                },
                "pain_points": {
                    "type": "string",
                    "description": "Current supplier issues or business challenges"
                },
                "business_scale": {
                    "type": "string",
                    "description": "Number of locations or business size"
                },
                "coffee_style": {
                    "type": "string",
                    "description": "Coffee preference (specialty, dark, consistent, etc.)"
                },
                "equipment_needs": {
                    "type": "string",
                    "description": "What equipment they need or have"
                },
                "volume": {
                    "type": "string",
                    "description": "Expected daily coffee volume or customer count"
                },
                "support_needs": {
                    "type": "string",
                    "description": "Training, service, or menu development needs"
                },
                "contact_name": {
                    "type": "string",
                    "description": "Contact person's name"
                },
                "contact_phone": {
                    "type": "string",
                    "description": "Phone number"
                },
                "contact_email": {
                    "type": "string",
                    "description": "Email address"
                },
                "contact_role": {
                    "type": "string",
                    "description": "Their role or title"
                }
            },
            "required": ["business_type"]
        },
    },
    {
        "type": "function",
        "name": "generate_sales_handoff",
        "description": """Generate a professional sales handoff summary. Use this function when:
        - You have collected sufficient qualification data
        - User is ready for sales team follow-up
        - You want to create a summary for the sales team
        
        This function creates a structured handoff document for the sales team.""",
        "parameters": {
            "type": "object",
            "properties": {
                "qualification_id": {
                    "type": "string",
                    "description": "ID of the qualification data to generate handoff for"
                },
                "conversation_summary": {
                    "type": "string",
                    "description": "Summary of the conversation and key points discussed"
                }
            },
            "required": ["qualification_id"]
        },
    },
    {
        "name": "get_high_priority_leads",
        "description": "Get all high-priority leads for sales team follow-up. Use this when sales team needs to see urgent leads.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_lead_summary",
        "description": "Get a summary of all leads with counts by priority. Use this to get an overview of lead pipeline.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
]

# Map function names to their implementations
FUNCTION_MAP = {
    "find_customer": find_customer,
    "get_appointments": get_appointments,
    "get_orders": get_orders,
    "create_appointment": create_appointment,
    "check_availability": check_availability,
    "reschedule_appointment": reschedule_appointment_func,
    "update_appointment_status": update_appointment_status_func,
    "end_call": end_call,
    "search_knowledge_base": search_knowledge_base,
    "get_knowledge_base_topics": get_knowledge_base_topics,
    "get_knowledge_base_entry": get_knowledge_base_entry,
    "create_customer_account": create_customer_account,
    "start_meeting_scheduling": start_meeting_scheduling,
    "finish_meeting_scheduling": finish_meeting_scheduling,
    "extract_qualification_data": extract_qualification_data,
    "generate_sales_handoff": generate_sales_handoff,
    "get_high_priority_leads": get_high_priority_leads,
    "get_lead_summary": get_lead_summary,
}

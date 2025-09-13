#!/usr/bin/env python3

import os
import sys
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional

# Import agent functions for sales qualification
from common.agent_functions import FUNCTION_MAP
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from openai import OpenAIError, RateLimitError, APIError, AuthenticationError

# Import our enhanced knowledge base
from knowledge.enhanced_coffee_knowledge_handler import EnhancedCoffeeKnowledgeBase

class KnowledgeBasedChatBot:
    """Chatbot with integrated coffee knowledge base using function calling"""
    
    def __init__(self):
        """Initialize the knowledge-based chatbot"""
        load_dotenv()
        
        # OpenAI API key (required)
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            print("❌ Error: OPENAI_API_KEY not found!")
            print("Please set your OpenAI API key in a .env file:")
            print("OPENAI_API_KEY=your_key_here")
            sys.exit(1)
        
        # Initialize the enhanced knowledge base
        self.knowledge_base = EnhancedCoffeeKnowledgeBase("knowledge")
        
        # Initialize LangChain ChatOpenAI with function calling
        self.chat_model = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7,
            openai_api_key=self.api_key
        )
        
        # Store conversation history
        self.conversation_history = []
        
        # Initialize data storage for qualification data
        self.data_file = "sales_qualification_data.json"
        self.load_stored_data()
        
        
        # Define function calling schema
        self.functions = self._define_functions()
        
        print("✅ Knowledge-based chatbot initialized")
        print(f"📚 Knowledge base loaded with {len(self.knowledge_base._get_entries_cached())} entries")
    
    def _define_functions(self) -> List[Dict[str, Any]]:
        """Define function calling schema for knowledge base operations"""
        return [
            {
                "name": "search_coffee_knowledge",
                "description": "Search the coffee knowledge base for relevant information about coffee business, strategies, equipment, sales, and operations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query to find relevant coffee knowledge"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results to return (default: 5)",
                            "default": 5
                        },
                        "min_score": {
                            "type": "number",
                            "description": "Minimum relevance score for results (default: 1.0)",
                            "default": 1.0
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "get_similar_knowledge",
                "description": "Find similar knowledge entries based on a specific topic or entry",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "entry_id": {
                            "type": "string",
                            "description": "The ID of the entry to find similar content for"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of similar results to return (default: 3)",
                            "default": 3
                        }
                    },
                    "required": ["entry_id"]
                }
            },
            {
                "name": "search_by_topic",
                "description": "Search knowledge base entries by specific topic",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "The topic to search for (e.g., 'Sales & Revenue', 'Menu Design', 'Equipment')"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results to return (default: 5)",
                            "default": 5
                        }
                    },
                    "required": ["topic"]
                }
            },
            {
                "name": "get_available_topics",
                "description": "Get all available topics in the knowledge base",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "get_knowledge_entry",
                "description": "Get a specific knowledge entry by its ID",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "entry_id": {
                            "type": "string",
                            "description": "The ID of the knowledge entry to retrieve"
                        }
                    },
                    "required": ["entry_id"]
                }
            },
            {
                "name": "extract_qualification_data",
                "description": "Extract business qualification data from conversation",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "business_type": {
                            "type": "string",
                            "description": "Type of business: new_cafe, existing_business, or unknown"
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
                            "description": "What equipment they need"
                        },
                        "volume": {
                            "type": "string",
                            "description": "Expected daily coffee volume"
                        },
                        "support_needs": {
                            "type": "string",
                            "description": "Training, service, menu help needed"
                        },
                        "contact_name": {
                            "type": "string",
                            "description": "Person's name"
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
                            "description": "Their role/title"
                        }
                    },
                    "required": ["business_type"]
                }
            },
            {
                "name": "generate_sales_handoff",
                "description": "Generate professional sales handoff summary",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "collected_data": {
                            "type": "object",
                            "description": "All collected qualification data"
                        },
                        "conversation_summary": {
                            "type": "string",
                            "description": "Brief summary of key conversation points"
                        }
                    },
                    "required": ["collected_data", "conversation_summary"]
                }
            }
        ]
    
    def load_stored_data(self):
        """Load previously stored qualification data"""
        try:
            with open(self.data_file, 'r') as f:
                self.stored_data = json.load(f)
        except FileNotFoundError:
            self.stored_data = {
                "qualifications": [],
                "last_updated": datetime.now().isoformat()
            }
    
    def save_data(self):
        """Save qualification data to file"""
        self.stored_data["last_updated"] = datetime.now().isoformat()
        with open(self.data_file, 'w') as f:
            json.dump(self.stored_data, f, indent=2)
    
    def store_qualification_data(self, data):
        """Store qualification data"""
        data["timestamp"] = datetime.now().isoformat()
        self.stored_data["qualifications"].append(data)
        self.save_data()
        return f"Qualification data stored for {data.get('contact_name', 'Unknown')}"
    
    
    def _call_function(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call the specified function with given arguments"""
        try:
            if function_name == "search_coffee_knowledge":
                query = arguments.get("query", "")
                max_results = arguments.get("max_results", 5)
                min_score = arguments.get("min_score", 1.0)
                
                results = self.knowledge_base.search_knowledge_base(
                    query=query,
                    max_results=max_results,
                    min_score=min_score
                )
                
                return {
                    "success": True,
                    "results": [
                        {
                            "id": result["id"],
                            "title": result["title"],
                            "topic": result["topic"],
                            "tags": result["tags"],
                            "content_preview": result["content_raw"][:200] + "..." if len(result["content_raw"]) > 200 else result["content_raw"],
                            "filename": result["filename"]
                        }
                        for result in results
                    ],
                    "total_found": len(results)
                }
            
            elif function_name == "get_similar_knowledge":
                entry_id = arguments.get("entry_id", "")
                max_results = arguments.get("max_results", 3)
                
                similar_entries = self.knowledge_base.get_similar_entries(
                    entry_id=entry_id,
                    max_results=max_results
                )
                
                return {
                    "success": True,
                    "similar_entries": [
                        {
                            "id": entry["id"],
                            "title": entry["title"],
                            "topic": entry["topic"],
                            "tags": entry["tags"],
                            "filename": entry["filename"]
                        }
                        for entry in similar_entries
                    ]
                }
            
            elif function_name == "search_by_topic":
                topic = arguments.get("topic", "")
                max_results = arguments.get("max_results", 5)
                
                topic_results = self.knowledge_base.search_by_topic(
                    topic=topic,
                    max_results=max_results
                )
                
                return {
                    "success": True,
                    "topic": topic,
                    "results": [
                        {
                            "id": result["id"],
                            "title": result["title"],
                            "topic": result["topic"],
                            "tags": result["tags"],
                            "filename": result["filename"]
                        }
                        for result in topic_results
                    ],
                    "total_found": len(topic_results)
                }
            
            elif function_name == "get_available_topics":
                topics = self.knowledge_base.get_topics()
                return {
                    "success": True,
                    "topics": topics,
                    "total_topics": len(topics)
                }
            
            elif function_name == "get_knowledge_entry":
                entry_id = arguments.get("entry_id", "")
                entry = self.knowledge_base.get_entry_by_id(entry_id)
                
                if entry:
                    return {
                        "success": True,
                        "entry": {
                            "id": entry["id"],
                            "title": entry["title"],
                            "topic": entry["topic"],
                            "tags": entry["tags"],
                            "content": entry["content_raw"],
                            "filename": entry["filename"]
                        }
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Entry with ID '{entry_id}' not found"
                    }
            
            elif function_name in ["extract_qualification_data", "generate_sales_handoff"]:
                # Use agent functions for sales qualification
                if function_name in FUNCTION_MAP:
                    try:
                        # Call the async function directly
                        import asyncio
                        
                        # Check if there's already an event loop running
                        try:
                            loop = asyncio.get_running_loop()
                            # If we're in an async context, we need to run in a thread
                            import concurrent.futures
                            with concurrent.futures.ThreadPoolExecutor() as executor:
                                future = executor.submit(asyncio.run, FUNCTION_MAP[function_name](arguments))
                                result = future.result()
                        except RuntimeError:
                            # No event loop running, we can create one
                            result = asyncio.run(FUNCTION_MAP[function_name](arguments))
                        
                        return result
                    except Exception as e:
                        return {
                            "success": False,
                            "error": f"Error calling {function_name}: {str(e)}"
                        }
                else:
                    return {
                        "success": False,
                        "error": f"Function {function_name} not found in agent functions"
                    }
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown function: {function_name}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Function call failed: {str(e)}"
            }
    
    def get_initial_greeting(self) -> str:
        """Get Logan's initial greeting for new conversations"""
        from common.agent_templates import AgentTemplates
        agent_templates = AgentTemplates(industry="coffee_business")
        
        system_message = SystemMessage(content=agent_templates.prompt)
        messages = [system_message] + [HumanMessage(content="Hello")]
        
        response = self.chat_model.invoke(messages)
        self.conversation_history.append(response)
        return response.content

    def chat_with_user(self, user_message: str) -> str:
        """Process user message with knowledge base integration"""
        try:
            # Use the proper prompt template from common folder
            from common.agent_templates import AgentTemplates
            agent_templates = AgentTemplates(industry="coffee_business")
            
            # Check if this is the first message in the conversation
            if not self.conversation_history:
                # This is the first message - use the prompt template for proper greeting
                system_message = SystemMessage(content=agent_templates.prompt)
                messages = [system_message] + [HumanMessage(content=user_message)]
                
                # Get response with function calling
                response = self.chat_model.invoke(
                    messages,
                    functions=self.functions,
                    function_call="auto"
                )
                
                # Handle function calling if needed
                if hasattr(response, 'additional_kwargs') and 'function_call' in response.additional_kwargs:
                    function_call = response.additional_kwargs['function_call']
                    function_name = function_call['name']
                    function_args = json.loads(function_call['arguments'])
                    
                    # Call the function
                    function_result = self._call_function(function_name, function_args)
                else:
                    # No function calling needed, return direct response
                    self.conversation_history.append(HumanMessage(content=user_message))
                    self.conversation_history.append(response)
                    return response.content
                
                # Add function result to conversation
                function_message = AIMessage(
                    content=f"Function call result: {json.dumps(function_result, indent=2)}"
                )
                messages.append(function_message)
                
                # Get final response with function results (include system message)
                final_response = self.chat_model.invoke([system_message] + messages[1:])
                
                # Add both messages to conversation history
                self.conversation_history.append(HumanMessage(content=user_message))
                self.conversation_history.append(final_response)
                
                return final_response.content
            
            system_message = SystemMessage(content=agent_templates.prompt)
            
            
            # Prepare messages for function calling
            messages = [system_message] + self.conversation_history + [HumanMessage(content=user_message)]
            
            # Get response with function calling
            response = self.chat_model.invoke(
                messages,
                functions=self.functions,
                function_call="auto"
            )
            
            # Check if function calling is needed
            if hasattr(response, 'additional_kwargs') and 'function_call' in response.additional_kwargs:
                function_call = response.additional_kwargs['function_call']
                function_name = function_call['name']
                function_args = json.loads(function_call['arguments'])
                
                # Call the function
                function_result = self._call_function(function_name, function_args)
                
                # Add function result to conversation
                function_message = AIMessage(
                    content=f"Function call result: {json.dumps(function_result, indent=2)}"
                )
                messages.append(function_message)
                
                # Get final response with function results (include system message)
                final_response = self.chat_model.invoke([system_message] + messages[1:])
                
                # Add both messages to conversation history
                self.conversation_history.append(HumanMessage(content=user_message))
                self.conversation_history.append(final_response)
                
                return final_response.content
            else:
                # No function calling needed, return direct response
                self.conversation_history.append(HumanMessage(content=user_message))
                self.conversation_history.append(response)
                
                return response.content
                
        except Exception as e:
            print(f"Error in chat_with_user: {str(e)}")
            return f"I apologize, but I encountered an error: {str(e)}"
    
    def start_chat(self):
        """Start the interactive chat session"""
        print("🤖 Coffee Business Knowledge Chatbot")
        print("=" * 50)
        print("Ask me anything about coffee business strategies, operations, sales, and more!")
        print("I have access to a comprehensive knowledge base with 25+ topics.")
        print("\nExample questions:")
        print("• How can I improve my coffee shop sales?")
        print("• What are the best menu design strategies?")
        print("• How do I maintain espresso equipment?")
        print("• What pricing strategies work best?")
        print("• How can I improve customer retention?")
        print("\nType 'quit', 'exit', or 'bye' to end the conversation.")
        print("Type 'topics' to see available knowledge topics.")
        print("=" * 50)
        
        while True:
            try:
                # Get user input
                user_input = input("\n👤 You: ").strip()
                
                # Check for exit commands
                if user_input.lower() in ['quit', 'exit', 'bye', 'q']:
                    print("\n👋 Thanks for chatting! Goodbye!")
                    break
                
                # Check for topics command
                elif user_input.lower() == 'topics':
                    topics = self.knowledge_base.get_topics()
                    print(f"\n📚 Available Knowledge Topics ({len(topics)}):")
                    for i, topic in enumerate(topics, 1):
                        print(f"   {i}. {topic}")
                    continue
                
                # Skip empty messages
                elif not user_input:
                    print("💭 Please enter a message.")
                    continue
                
                # Process the message
                print("\n🤖 AI: ", end="", flush=True)
                response = self.chat_with_user(user_input)
                print(response)
                
            except KeyboardInterrupt:
                print("\n\n👋 Chat interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {e}")
                break

def main():
    """Main entry point"""
    try:
        chatbot = KnowledgeBasedChatBot()
        chatbot.start_chat()
    except Exception as e:
        print(f"❌ Failed to start chatbot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

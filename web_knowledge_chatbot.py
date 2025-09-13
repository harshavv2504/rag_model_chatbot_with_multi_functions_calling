#!/usr/bin/env python3
"""
Web Knowledge-Based Chatbot with Function Calling
Web interface for the coffee knowledge base chatbot with real-time function calling
"""

import os
import json
import time
import asyncio
from typing import List, Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

# Import the knowledge-based chatbot
from knowledge_based_chatbot import KnowledgeBasedChatBot

# Import common function definitions and business logic
from common.agent_functions import FUNCTION_DEFINITIONS, FUNCTION_MAP
from common.business_logic import (
    get_customer,
    get_customer_appointments,
    get_customer_orders,
    schedule_appointment,
    get_available_appointment_slots,
    reschedule_appointment,
    update_appointment_status,
    create_new_customer,
    handle_meeting_scheduling_request,
    complete_meeting_scheduling
)
from common.agent_templates import AgentTemplates
from common.prompt_templates import COFFEE_BUSINESS_PROMPT_TEMPLATE

class WebKnowledgeChatBot(KnowledgeBasedChatBot):
    """Web-based knowledge chatbot with WebSocket support"""
    
    def __init__(self):
        """Initialize the web knowledge chatbot"""
        super().__init__()
        self.active_connections: List[WebSocket] = []
        
        # Initialize agent templates for better prompt handling
        self.agent_templates = AgentTemplates(industry="coffee_business")
        
        # Add customer service functions to existing functions
        self.functions.extend(FUNCTION_DEFINITIONS)
        
        # Update the prompt to include sales qualification instructions
        self.prompt = self.agent_templates.prompt
        
        # Create combined function map
        self.function_map = {
            # Existing knowledge base functions
            "search_coffee_knowledge": self._call_function,
            "get_similar_knowledge": self._call_function,
            "search_by_topic": self._call_function,
            "get_available_topics": self._call_function,
            "get_knowledge_entry": self._call_function,
            # New customer service functions
            **FUNCTION_MAP
        }
    
    async def connect_websocket(self, websocket: WebSocket):
        """Accept and store WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        # Send welcome message using agent templates
        welcome_data = {
            "type": "system_message",
            "content": self.agent_templates.first_message + "\n\n" +
                      f"📚 Knowledge base loaded with {len(self.knowledge_base._get_entries_cached())} entries\n" +
                      f"🔧 {self.agent_templates.capabilities}\n\n" +
                      "I can help with:\n" +
                      "• Coffee business strategies and operations\n" +
                      "• Sales improvement and menu design\n" +
                      "• Equipment maintenance and pricing\n" +
                      "• Customer account management\n" +
                      "• Appointment scheduling\n" +
                      "• Order tracking and more!",
            "metadata": {
                "timestamp": time.time(),
                "knowledge_base_entries": len(self.knowledge_base._get_entries_cached()),
                "available_functions": len(self.functions),
                "personality": self.agent_templates.personality
            }
        }
        await websocket.send_text(json.dumps(welcome_data))
    
    def disconnect_websocket(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    def check_exit_command(self, message: str) -> bool:
        """Check if message is an exit command"""
        return message.lower().strip() in ['quit', 'exit', 'bye', 'q']
    
    async def handle_chat_message(self, message: str, websocket: WebSocket):
        """Process chat message with knowledge base integration"""
        try:
            # Check for exit commands
            if self.check_exit_command(message):
                await self.handle_exit_command(websocket)
                return
            
            # Check for topics command
            if message.lower().strip() == 'topics':
                await self.handle_topics_command(websocket)
                return
            
            # Skip empty messages
            if not message.strip():
                error_data = {
                    "type": "error",
                    "content": "💭 Please enter a message.",
                    "metadata": {"timestamp": time.time()}
                }
                await websocket.send_text(json.dumps(error_data))
                return
            
            # Process with knowledge base
            await self.process_knowledge_message(message, websocket)
            
        except Exception as e:
            error_data = {
                "type": "error",
                "content": f"❌ Error: {str(e)}",
                "metadata": {"timestamp": time.time(), "error_details": str(e)}
            }
            await websocket.send_text(json.dumps(error_data))
    
    async def handle_topics_command(self, websocket: WebSocket):
        """Handle topics command and send available topics"""
        topics = self.knowledge_base.get_topics()
        
        topics_data = {
            "type": "topics_list",
            "content": f"📚 Available Knowledge Topics ({len(topics)}):",
            "topics": topics,
            "metadata": {"timestamp": time.time(), "total_topics": len(topics)}
        }
        await websocket.send_text(json.dumps(topics_data))
    
    async def handle_exit_command(self, websocket: WebSocket):
        """Handle exit command and send goodbye message"""
        goodbye_data = {
            "type": "session_end",
            "content": "👋 Thanks for chatting! Goodbye!",
            "metadata": {"timestamp": time.time()}
        }
        await websocket.send_text(json.dumps(goodbye_data))
    
    async def process_knowledge_message(self, user_message: str, websocket: WebSocket):
        """Process message with knowledge base integration and stream response"""
        from langchain.schema import HumanMessage, AIMessage, SystemMessage
        
        start_time = time.time()
        
        try:
            # Send typing indicator
            typing_data = {
                "type": "ai_typing",
                "content": "",
                "metadata": {"timestamp": time.time()}
            }
            await websocket.send_text(json.dumps(typing_data))
            
            # No special greeting handling needed - let the normal flow handle all messages
            
            # Use the comprehensive prompt template from common folder
            system_message = SystemMessage(content=self.agent_templates.prompt)
            
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
                
                # Send function call notification
                function_notification = {
                    "type": "function_call",
                    "content": f"🔍 Processing request: {function_name}",
                    "metadata": {
                        "timestamp": time.time(),
                        "function_name": function_name,
                        "function_args": function_args
                    }
                }
                await websocket.send_text(json.dumps(function_notification))
                
                # Call the appropriate function
                function_result = await self._call_enhanced_function(function_name, function_args, websocket)
                
                # Send function result
                function_result_data = {
                    "type": "function_result",
                    "content": f"✅ Function completed: {function_name}",
                    "metadata": {
                        "timestamp": time.time(),
                        "function_result": function_result
                    }
                }
                await websocket.send_text(json.dumps(function_result_data))
                
                # Add function result to conversation
                function_message = AIMessage(
                    content=f"Function call result: {json.dumps(function_result, indent=2)}"
                )
                messages.append(function_message)
                
                # Get final response with function results
                final_response = self.chat_model.invoke(messages)
                
                # Stream the final response
                await self.stream_response_content(final_response.content, websocket)
                
                # Add both messages to conversation history
                self.conversation_history.append(HumanMessage(content=user_message))
                self.conversation_history.append(final_response)
                
            else:
                # No function calling needed, stream direct response
                await self.stream_response_content(response.content, websocket)
                
                # Add both messages to conversation history
                self.conversation_history.append(HumanMessage(content=user_message))
                self.conversation_history.append(response)
            
            # Calculate metrics
            response_time = time.time() - start_time
            
            # Send completion signal
            complete_data = {
                "type": "ai_complete",
                "content": "",
                "metadata": {
                    "timestamp": time.time(),
                    "response_time": response_time
                }
            }
            await websocket.send_text(json.dumps(complete_data))
                    
        except Exception as e:
            # Log the error for debugging
            print(f"Error in process_knowledge_message: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            
            # Handle various errors
            error_message = "❌ Sorry, I encountered an error. Please try again."
            
            if "rate limit" in str(e).lower():
                error_message = "⏱️ Rate limit exceeded. Please wait a moment and try again."
            elif "authentication" in str(e).lower():
                error_message = "🔐 Authentication error. Please check your API key."
            elif "api" in str(e).lower():
                error_message = "🌐 OpenAI API error. Please try again later."
            elif "function" in str(e).lower():
                error_message = "🔧 Function calling error. Please try rephrasing your question."
            
            error_data = {
                "type": "error",
                "content": error_message,
                "metadata": {
                    "timestamp": time.time(),
                    "error_details": str(e),
                    "error_type": type(e).__name__
                }
            }
            await websocket.send_text(json.dumps(error_data))
    
    async def stream_response_content(self, content: str, websocket: WebSocket):
        """Stream response content in sentence chunks"""
        # Split content into sentences for more natural chunking
        sentences = content.split('. ')
        
        for i, sentence in enumerate(sentences):
            # Clean up the sentence
            if not sentence.endswith('.') and i < len(sentences) - 1:
                sentence += '.'
            
            # Skip empty sentences
            if not sentence.strip():
                continue
            
            chunk_data = {
                "type": "ai_chunk",
                "content": sentence + " ",
                "metadata": {
                    "timestamp": time.time(),
                    "chunk_index": i,
                    "is_sentence": True
                }
            }
            await websocket.send_text(json.dumps(chunk_data))
            
            # Delay between sentences for natural reading pace
            await asyncio.sleep(0.3)
    
    async def _call_enhanced_function(self, function_name: str, arguments: Dict[str, Any], websocket: WebSocket) -> Dict[str, Any]:
        """Call the appropriate function (knowledge base or customer service)"""
        try:
            # Check if it's a customer service function
            if function_name in FUNCTION_MAP:
                # Call customer service function
                function_func = FUNCTION_MAP[function_name]
                if asyncio.iscoroutinefunction(function_func):
                    result = await function_func(arguments)
                else:
                    result = function_func(arguments)
                return result
            else:
                # Call knowledge base function
                return self._call_function(function_name, arguments)
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Function call failed: {str(e)}"
            }

# Initialize the web knowledge chatbot
web_knowledge_chatbot = WebKnowledgeChatBot()

# Create FastAPI app
app = FastAPI(title="Coffee Knowledge Chatbot", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def serve_index():
    """Serve the main chat interface"""
    return FileResponse("static/index.html")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "knowledge_base_entries": len(web_knowledge_chatbot.knowledge_base._get_entries_cached()),
        "available_functions": len(web_knowledge_chatbot.functions),
        "timestamp": time.time()
    }

@app.get("/api/topics")
async def get_topics():
    """Get available knowledge topics"""
    topics = web_knowledge_chatbot.knowledge_base.get_topics()
    return {
        "topics": topics,
        "total_topics": len(topics)
    }

@app.get("/api/functions")
async def get_functions():
    """Get available functions"""
    return {
        "functions": [func["name"] for func in web_knowledge_chatbot.functions],
        "total_functions": len(web_knowledge_chatbot.functions)
    }

@app.get("/api/customer/{customer_id}")
async def get_customer_info(customer_id: str):
    """Get customer information by ID"""
    try:
        result = await get_customer(customer_id=customer_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/customer/{customer_id}/appointments")
async def get_customer_appointments_endpoint(customer_id: str):
    """Get customer appointments by ID"""
    try:
        result = await get_customer_appointments(customer_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/customer/{customer_id}/orders")
async def get_customer_orders_endpoint(customer_id: str):
    """Get customer orders by ID"""
    try:
        result = await get_customer_orders(customer_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time knowledge-based chat"""
    await web_knowledge_chatbot.connect_websocket(websocket)
    
    # Send initial greeting from Logan
    try:
        initial_greeting = web_knowledge_chatbot.get_initial_greeting()
        greeting_data = {
            "type": "ai_message",
            "content": initial_greeting,
            "metadata": {"timestamp": time.time(), "is_initial_greeting": True}
        }
        await websocket.send_text(json.dumps(greeting_data))
    except Exception as e:
        print(f"Error sending initial greeting: {e}")
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data.get("type") == "user_message":
                user_message = message_data.get("content", "")
                await web_knowledge_chatbot.handle_chat_message(user_message, websocket)
                
    except WebSocketDisconnect:
        web_knowledge_chatbot.disconnect_websocket(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        web_knowledge_chatbot.disconnect_websocket(websocket)

if __name__ == "__main__":
    uvicorn.run("web_knowledge_chatbot:app", host="0.0.0.0", port=8000, reload=True)

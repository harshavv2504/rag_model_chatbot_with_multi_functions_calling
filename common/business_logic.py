import asyncio
import json
from datetime import datetime, timedelta
import random
from common.config import ARTIFICIAL_DELAY, MOCK_DATA_SIZE
import pathlib


def save_mock_data(data):
    """Save mock data to a consistent file in mock_data_outputs directory."""
    global CURRENT_DATA_FILE
    
    # Create mock_data_outputs directory if it doesn't exist
    output_dir = pathlib.Path("mock_data_outputs")
    output_dir.mkdir(exist_ok=True)

    # Use a consistent filename instead of timestamped files
    output_file = output_dir / "mock_data.json"

    # Save the data with pretty printing
    try:
        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)
        print(f"\nMock data saved to: {output_file}")
        
        # Update current data file
        CURRENT_DATA_FILE = output_file
    except Exception as e:
        print(f"ERROR: Failed to save mock data: {e}")
        raise


# Note: cleanup_mock_data_files function removed - no longer needed
# Data files are preserved to maintain consistency


# Mock data generation
def generate_mock_data():
    customers = []
    appointments = []
    orders = []

    # Generate customers
    for i in range(MOCK_DATA_SIZE["customers"]):
        customer = {
            "id": f"CUST{i:04d}",
            "name": f"Customer {i}",
            "phone": f"+1555{i:07d}",
            "email": f"customer{i}@example.com",
            "joined_date": (
                datetime.now() - timedelta(days=random.randint(0, 7))
            ).isoformat(),
        }
        customers.append(customer)

    # Generate appointments
    for i in range(MOCK_DATA_SIZE["appointments"]):
        customer = random.choice(customers)
        appointment = {
            "id": f"APT{i:04d}",
            "customer_id": customer["id"],
            "customer_name": customer["name"],
            "date": (datetime.now() + timedelta(days=random.randint(0, 7))).isoformat(),
            "service": random.choice(
                ["Consultation", "Follow-up", "Review", "Planning"]
            ),
            "status": random.choice(["Scheduled", "Completed", "Cancelled"]),
        }
        appointments.append(appointment)

    # Generate orders
    for i in range(MOCK_DATA_SIZE["orders"]):
        customer = random.choice(customers)
        order = {
            "id": f"ORD{i:04d}",
            "customer_id": customer["id"],
            "customer_name": customer["name"],
            "date": (datetime.now() - timedelta(days=random.randint(0, 7))).isoformat(),
            "items": random.randint(1, 5),
            "total": round(random.uniform(10.0, 500.0), 2),
            "status": random.choice(["Pending", "Shipped", "Delivered", "Cancelled"]),
        }
        orders.append(order)

    # Format sample data for display
    sample_data = []
    sample_customers = random.sample(customers, 3)
    for customer in sample_customers:
        customer_data = {
            "Customer": customer["name"],
            "ID": customer["id"],
            "Phone": customer["phone"],
            "Email": customer["email"],
            "Appointments": [],
            "Orders": [],
        }

        # Add appointments
        customer_appointments = [
            a for a in appointments if a["customer_id"] == customer["id"]
        ]
        for apt in customer_appointments[:2]:
            customer_data["Appointments"].append(
                {
                    "Service": apt["service"],
                    "Date": apt["date"][:10],
                    "Status": apt["status"],
                }
            )

        # Add orders
        customer_orders = [o for o in orders if o["customer_id"] == customer["id"]]
        for order in customer_orders[:2]:
            customer_data["Orders"].append(
                {
                    "ID": order["id"],
                    "Total": f"${order['total']}",
                    "Status": order["status"],
                    "Date": order["date"][:10],
                    "# Items": order["items"],
                }
            )

        sample_data.append(customer_data)

    # Create data object
    mock_data = {
        "customers": customers,
        "appointments": appointments,
        "orders": orders,
        "sample_data": sample_data,
    }

    # Save the mock data
    save_mock_data(mock_data)

    return mock_data


def regenerate_sample_data():
    """Regenerate sample data to reflect current state of customers, appointments, and orders."""
    if not MOCK_DATA["customers"]:
        MOCK_DATA["sample_data"] = []
        return
    
    # Get up to 3 customers for sample display
    sample_customers = MOCK_DATA["customers"][:3]
    sample_data = []
    
    for customer in sample_customers:
        customer_data = {
            "Customer": customer["name"],
            "ID": customer["id"],
            "Phone": customer["phone"],
            "Email": customer["email"],
            "Appointments": [],
            "Orders": [],
        }

        # Add appointments for this customer
        customer_appointments = [
            a for a in MOCK_DATA["appointments"] if a["customer_id"] == customer["id"]
        ]
        for apt in customer_appointments[:2]:  # Show up to 2 appointments
            customer_data["Appointments"].append({
                "Service": apt["service"],
                "Date": apt["date"][:10],
                "Status": apt["status"],
            })

        # Add orders for this customer
        customer_orders = [o for o in MOCK_DATA["orders"] if o["customer_id"] == customer["id"]]
        for order in customer_orders[:2]:  # Show up to 2 orders
            customer_data["Orders"].append({
                "ID": order["id"],
                "Total": f"${order['total']}",
                "Status": order["status"],
                "Date": order["date"][:10],
                "# Items": order["items"],
            })

        sample_data.append(customer_data)
    
    MOCK_DATA["sample_data"] = sample_data
    print(f"✅ Sample data regenerated for {len(sample_data)} customers")


def validate_loaded_data_structure(data):
    """Validate that loaded data has the correct structure."""
    required_keys = ["customers", "appointments", "orders", "sample_data"]
    
    # Check if all required keys exist
    if not all(key in data for key in required_keys):
        print(f"❌ Missing required keys: {[key for key in required_keys if key not in data]}")
        return False
    
    # Check if values are lists
    if not all(isinstance(data[key], list) for key in required_keys):
        print(f"❌ Required keys must be lists: {[key for key in required_keys if not isinstance(data[key], list)]}")
        return False
    
    # Check if customers have required fields
    if data["customers"]:
        required_customer_fields = ["id", "name", "phone", "email", "joined_date"]
        first_customer = data["customers"][0]
        missing_fields = [field for field in required_customer_fields if field not in first_customer]
        if missing_fields:
            print(f"❌ Customer missing required fields: {missing_fields}")
            return False
    
    print("✅ Loaded data structure validation passed")
    return True


def load_or_generate_mock_data():
    """Load existing data or generate new if none exists."""
    try:
        # Try to load the consistent mock data file
        output_dir = pathlib.Path("mock_data_outputs")
        data_file = output_dir / "mock_data.json"
        
        if data_file.exists():
            print(f"Loading existing data from: {data_file}")
            with open(data_file, 'r') as f:
                loaded_data = json.load(f)
                print(f"Successfully loaded {len(loaded_data.get('customers', []))} customers, {len(loaded_data.get('appointments', []))} appointments, {len(loaded_data.get('orders', []))} orders")
                
                # Validate loaded data structure
                if not validate_loaded_data_structure(loaded_data):
                    print("WARNING: Loaded data structure is invalid, generating new data instead")
                    return generate_mock_data()
                
                # Regenerate sample data to ensure consistency
                loaded_data["sample_data"] = []  # Clear old sample data
                return loaded_data
    except Exception as e:
        print(f"Error loading existing data: {e}")
        print("Will generate new mock data instead")
    
    # Generate new data only if none exists
    print("No existing data found, generating new mock data...")
    return generate_mock_data()


# Initialize mock data
MOCK_DATA = load_or_generate_mock_data()

# Track current data file
CURRENT_DATA_FILE = None


async def simulate_delay(delay_type):
    """Simulate processing delay based on operation type."""
    await asyncio.sleep(ARTIFICIAL_DELAY[delay_type])


async def get_customer(phone=None, email=None, customer_id=None):
    """Look up a customer by phone, email, or ID."""
    await simulate_delay("database")

    if phone:
        customer = next(
            (c for c in MOCK_DATA["customers"] if c["phone"] == phone), None
        )
    elif email:
        customer = next(
            (c for c in MOCK_DATA["customers"] if c["email"] == email), None
        )
    elif customer_id:
        customer = next(
            (c for c in MOCK_DATA["customers"] if c["id"] == customer_id), None
        )
    else:
        return {"error": "No search criteria provided"}

    return customer if customer else {"error": "Customer not found"}


async def get_customer_appointments(customer_id):
    """Get all appointments for a customer."""
    await simulate_delay("database")

    appointments = [
        a for a in MOCK_DATA["appointments"] if a["customer_id"] == customer_id
    ]
    return {"customer_id": customer_id, "appointments": appointments}


async def get_customer_orders(customer_id):
    """Get all orders for a customer."""
    await simulate_delay("database")

    orders = [o for o in MOCK_DATA["orders"] if o["customer_id"] == customer_id]
    return {"customer_id": customer_id, "orders": orders}


def generate_unique_appointment_id():
    """Generate unique appointment ID that doesn't conflict with existing IDs."""
    existing_ids = {a["id"] for a in MOCK_DATA["appointments"]}
    counter = 0
    while True:
        new_id = f"APT{counter:04d}"
        if new_id not in existing_ids:
            return new_id
        counter += 1


async def schedule_appointment(customer_id, date, service):
    """Schedule a new appointment."""
    await simulate_delay("database")

    # Verify customer exists
    customer = await get_customer(customer_id=customer_id)
    if "error" in customer:
        return customer

    # Validate appointment date and time
    try:
        appointment_datetime = datetime.fromisoformat(date)
        current_time = datetime.now()
        
        # Check if appointment is in the past
        if appointment_datetime <= current_time:
            return {"error": "Cannot schedule appointments in the past"}
        
        # Check if appointment is within business hours (9 AM - 5 PM)
        if appointment_datetime.hour < 9 or appointment_datetime.hour >= 17:
            return {"error": "Appointments can only be scheduled between 9 AM and 5 PM"}
        
        # Check if appointment is on a weekend (Saturday = 5, Sunday = 6)
        if appointment_datetime.weekday() >= 5:
            return {"error": "Appointments can only be scheduled on weekdays"}
            
    except ValueError:
        return {"error": "Invalid date format. Please use ISO format (YYYY-MM-DDTHH:MM:SS)"}

    # Check if time slot is already taken
    existing_appointment = next(
        (a for a in MOCK_DATA["appointments"] if a["date"] == date), None
    )
    if existing_appointment:
        return {"error": "This time slot is already booked. Please choose another time."}

    # Create new appointment with unique ID
    appointment_id = generate_unique_appointment_id()
    appointment = {
        "id": appointment_id,
        "customer_id": customer_id,
        "customer_name": customer["name"],
        "date": date,
        "service": service,
        "status": "Scheduled",
    }

    MOCK_DATA["appointments"].append(appointment)
    
    # Regenerate sample data to reflect new appointment
    regenerate_sample_data()
    
    # Automatically send email and calendar invite
    try:
        await send_meeting_invite(appointment, customer)
        print(f"✅ Meeting invite sent for appointment {appointment_id}")
    except Exception as e:
        print(f"WARNING: Could not send meeting invite: {e}")
        # Don't fail the appointment creation if email fails
    
    return appointment


async def send_meeting_invite(appointment, customer):
    """Send automatic email and calendar invite for scheduled appointments."""
    try:
        # Import meeting modular functions
        from common.meeting_modular import generate_meeting_json, schedule_meeting_from_json
        
        # Generate meeting data in required format
        meeting_data = generate_meeting_json(appointment, customer)
        
        # Send email and create calendar event
        schedule_meeting_from_json(meeting_data)
        
        print(f"✅ Meeting invite sent successfully to {customer['email']}")
        return True
        
    except ImportError as e:
        print(f"❌ Error importing meeting modular functions: {e}")
        return False
    except Exception as e:
        print(f"❌ Error sending meeting invite: {e}")
        return False


async def get_available_appointment_slots(start_date, end_date):
    """Get available appointment slots."""
    await simulate_delay("database")

    try:
        # Convert dates to datetime objects
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        
        # Validate date range
        current_time = datetime.now()
        if start < current_time:
            start = current_time.replace(minute=0, second=0, microsecond=0)
            start = start.replace(hour=start.hour + 1)  # Start from next hour
        
        if end <= start:
            return {"error": "End date must be after start date"}
            
    except ValueError:
        return {"error": "Invalid date format. Please use ISO format (YYYY-MM-DDTHH:MM:SS)"}

    # Generate available slots (9 AM to 5 PM, 1-hour slots, weekdays only)
    slots = []
    current = start
    
    while current <= end:
        # Only include weekdays (Monday = 0, Friday = 4)
        if current.weekday() < 5 and current.hour >= 9 and current.hour < 17:
            slot_time = current.isoformat()
            # Check if slot is already taken
            taken = any(a["date"] == slot_time for a in MOCK_DATA["appointments"])
            if not taken:
                slots.append(slot_time)
        current += timedelta(hours=1)

    return {"available_slots": slots}


async def reschedule_appointment(appointment_id, new_date, new_service):
    """Reschedule an existing appointment."""
    await simulate_delay("database")
    
    # Find the existing appointment
    appointment = next(
        (a for a in MOCK_DATA["appointments"] if a["id"] == appointment_id), None
    )
    
    if not appointment:
        return {"error": "Appointment not found"}
    
    # Check if appointment is already cancelled or completed
    if appointment["status"] in ["Cancelled", "Completed"]:
        return {"error": f"Cannot reschedule appointment with status: {appointment['status']}"}
    
    # Validate new appointment date and time
    try:
        appointment_datetime = datetime.fromisoformat(new_date)
        current_time = datetime.now()
        
        # Check if appointment is in the past
        if appointment_datetime <= current_time:
            return {"error": "Cannot schedule appointments in the past"}
        
        # Check if appointment is within business hours (9 AM - 5 PM)
        if appointment_datetime.hour < 9 or appointment_datetime.hour >= 17:
            return {"error": "Appointments can only be scheduled between 9 AM and 5 PM"}
        
        # Check if appointment is on a weekend (Saturday = 5, Sunday = 6)
        if appointment_datetime.weekday() >= 5:
            return {"error": "Appointments can only be scheduled on weekdays"}
            
    except ValueError:
        return {"error": "Invalid date format. Please use ISO format (YYYY-MM-DDTHH:MM:SS)"}
    
    # Check if new time slot is already taken (excluding current appointment)
    existing_appointment = next(
        (a for a in MOCK_DATA["appointments"] 
         if a["date"] == new_date and a["id"] != appointment_id), None
    )
    if existing_appointment:
        return {"error": "This time slot is already booked. Please choose another time."}
    
    # Get customer info for meeting invite
    customer = await get_customer(customer_id=appointment["customer_id"])
    if "error" in customer:
        return {"error": "Customer not found"}
    
    # Update the appointment
    old_date = appointment["date"]
    appointment["date"] = new_date
    appointment["service"] = new_service
    appointment["status"] = "Scheduled"  # Reset to scheduled when rescheduled
    
    # Regenerate sample data to reflect changes
    regenerate_sample_data()
    
    # Send updated meeting invite
    try:
        await send_meeting_invite(appointment, customer)
        print(f"✅ Meeting invite updated for appointment {appointment_id}")
    except Exception as e:
        print(f"WARNING: Could not send updated meeting invite: {e}")
        # Don't fail the reschedule if email fails
    
    return {
        "message": "Appointment rescheduled successfully",
        "appointment": appointment,
        "old_date": old_date,
        "new_date": new_date
    }



# Removed cancel_appointment function - not needed for coffee business chatbot


async def update_appointment_status(appointment_id, new_status):
    """Update the status of an existing appointment."""
    await simulate_delay("database")
    
    # Validate status
    valid_statuses = ["Scheduled", "Completed", "Cancelled"]
    if new_status not in valid_statuses:
        return {"error": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"}
    
    # Find the existing appointment
    appointment = next(
        (a for a in MOCK_DATA["appointments"] if a["id"] == appointment_id), None
    )
    
    if not appointment:
        return {"error": "Appointment not found"}
    
    # Store old status for response
    old_status = appointment["status"]
    
    # Update appointment status
    appointment["status"] = new_status
    
    # Regenerate sample data to reflect changes
    regenerate_sample_data()
    
    return {
        "message": f"Appointment status updated from {old_status} to {new_status}",
        "appointment": appointment,
        "old_status": old_status,
        "new_status": new_status
    }


async def prepare_agent_filler_message(websocket, message_type):
    """
    Handle agent filler messages while maintaining proper function call protocol.
    Returns a simple confirmation first, then sends the actual message to the client.
    """
    # First prepare the result that will be the function call response
    result = {"status": "queued", "message_type": message_type}

    # Prepare the inject message but don't send it yet
    if message_type == "lookup":
        inject_message = {
            "type": "InjectAgentMessage",
            "message": "Let me look that up for you...",
        }
    else:
        inject_message = {
            "type": "InjectAgentMessage",
            "message": "One moment please...",
        }

    # Return the result first - this becomes the function call response
    # The caller can then send the inject message after handling the function response
    return {"function_response": result, "inject_message": inject_message}


def generate_unique_customer_id():
    """Generate unique customer ID that doesn't conflict with existing IDs."""
    existing_ids = {c["id"] for c in MOCK_DATA["customers"]}
    counter = 0
    while True:
        new_id = f"CUST{counter:04d}"
        if new_id not in existing_ids:
            return new_id
        counter += 1


async def create_new_customer(name, phone, email):
    """Create a new customer account."""
    await simulate_delay("database")
    
    # Validate required fields
    if not all([name, phone, email]):
        return {"error": "Name, phone, and email are required"}
    
    # Check if customer already exists
    existing_customer = await get_customer(phone=phone, email=email)
    if "error" not in existing_customer:
        return {"error": "Customer already exists with this phone or email"}
    
    # Generate unique customer ID (prevents conflicts)
    new_id = generate_unique_customer_id()
    
    # Create new customer
    new_customer = {
        "id": new_id,
        "name": name.strip(),
        "phone": phone.strip(),
        "email": email.strip(),
        "joined_date": datetime.now().isoformat()
    }
    
    # Add to mock data
    MOCK_DATA["customers"].append(new_customer)
    
    # Regenerate sample data to reflect current state
    regenerate_sample_data()
    
    # Save updated mock data
    save_mock_data(MOCK_DATA)
    
    return {
        "success": True,
        "customer": new_customer,
        "message": f"Customer {name} created successfully with ID {new_id}"
    }


async def handle_meeting_scheduling_request(customer_identifier, identifier_type="customer_id"):
    """
    Handle a complete meeting scheduling request with proper workflow enforcement.
    This function enforces the correct sequence: find customer -> check availability -> present options.
    """
    await simulate_delay("database")
    
    # Step 1: Find the customer
    if identifier_type == "customer_id":
        customer = await get_customer(customer_id=customer_identifier)
    elif identifier_type == "phone":
        customer = await get_customer(phone=customer_identifier)
    elif identifier_type == "email":
        customer = await get_customer(email=customer_identifier)
    else:
        return {"error": "Invalid identifier type"}
    
    if "error" in customer:
        return {"error": "Customer not found", "customer": None, "available_slots": []}
    
    # Step 2: Check availability (next 7 days)
    start_date = datetime.now().isoformat()
    end_date = (datetime.now() + timedelta(days=7)).isoformat()
    
    availability_result = await get_available_appointment_slots(start_date, end_date)
    
    if "error" in availability_result:
        return {
            "customer": customer,
            "available_slots": [],
            "error": availability_result["error"]
        }
    
    # Step 3: Return customer info and available slots
    return {
        "customer": customer,
        "available_slots": availability_result.get("available_slots", []),
        "message": f"Found customer {customer['name']}. Here are the available appointment slots:",
        "next_step": "present_availability"
    }


async def complete_meeting_scheduling(customer_id, selected_slot, service_type="Consultation"):
    """
    Complete the meeting scheduling process after customer has selected a time slot.
    """
    await simulate_delay("database")
    
    # Schedule the appointment
    result = await schedule_appointment(customer_id, selected_slot, service_type)
    
    if "error" in result:
        return result
    
    return {
        "success": True,
        "appointment": result,
        "message": f"Meeting scheduled successfully for {result['date']}",
        "customer_id": customer_id
    }


async def prepare_farewell_message(websocket, farewell_type):
    """End the conversation with an appropriate farewell message and close the connection."""
    # Prepare farewell message based on type
    if farewell_type == "thanks":
        message = "Thank you for calling! Have a great day!"
    elif farewell_type == "help":
        message = "I'm glad I could help! Have a wonderful day!"
    else:  # general
        message = "Goodbye! Have a nice day!"

    # Prepare messages but don't send them
    inject_message = {"type": "InjectAgentMessage", "message": message}

    close_message = {"type": "close"}

    # Return both messages to be sent in correct order by the caller
    return {
        "function_response": {"status": "closing", "message": message},
        "inject_message": inject_message,
        "close_message": close_message,
    }


def get_current_data_file():
    """Get the path to the current data file being used."""
    global CURRENT_DATA_FILE
    if CURRENT_DATA_FILE is None:
        # Use the consistent mock data file
        output_dir = pathlib.Path("mock_data_outputs")
        data_file = output_dir / "mock_data.json"
        if data_file.exists():
            CURRENT_DATA_FILE = data_file
    return CURRENT_DATA_FILE


def reload_mock_data():
    """Manually reload mock data from disk."""
    global MOCK_DATA, CURRENT_DATA_FILE
    try:
        MOCK_DATA = load_or_generate_mock_data()
        CURRENT_DATA_FILE = get_current_data_file()
        
        # Regenerate sample data after reloading
        regenerate_sample_data()
        
        print(f"Mock data reloaded successfully. Current file: {CURRENT_DATA_FILE}")
        return True
    except Exception as e:
        print(f"Error reloading mock data: {e}")
        return False


def validate_data_integrity():
    """Check for data integrity issues like duplicate IDs."""
    issues = []
    
    # Check for duplicate customer IDs
    customer_ids = [c["id"] for c in MOCK_DATA["customers"]]
    if len(customer_ids) != len(set(customer_ids)):
        duplicate_customer_ids = [id for id in customer_ids if customer_ids.count(id) > 1]
        issues.append(f"Duplicate customer IDs found: {duplicate_customer_ids}")
    
    # Check for duplicate appointment IDs
    appointment_ids = [a["id"] for a in MOCK_DATA["appointments"]]
    if len(appointment_ids) != len(set(appointment_ids)):
        duplicate_appointment_ids = [id for id in appointment_ids if appointment_ids.count(id) > 1]
        issues.append(f"Duplicate appointment IDs found: {duplicate_appointment_ids}")
    
    # Check for duplicate order IDs
    order_ids = [o["id"] for o in MOCK_DATA["orders"]]
    if len(order_ids) != len(set(order_ids)):
        duplicate_order_ids = [id for id in order_ids if order_ids.count(id) > 1]
        issues.append(f"Duplicate order IDs found: {duplicate_order_ids}")
    
    # Check for orphaned appointments/orders (customers that don't exist)
    customer_ids_set = set(c["id"] for c in MOCK_DATA["customers"])
    orphaned_appointments = [a for a in MOCK_DATA["appointments"] if a["customer_id"] not in customer_ids_set]
    if orphaned_appointments:
        issues.append(f"Orphaned appointments found: {len(orphaned_appointments)} appointments with non-existent customers")
    
    orphaned_orders = [o for o in MOCK_DATA["orders"] if o["customer_id"] not in customer_ids_set]
    if orphaned_orders:
        issues.append(f"Orphaned orders found: {len(orphaned_orders)} orders with non-existent customers")
    
    if issues:
        print("WARNING: DATA INTEGRITY ISSUES FOUND:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    else:
        print("✅ Data integrity check passed - no issues found")
        return True


def sync_memory_with_disk():
    """Ensure memory data matches disk data by reloading if needed."""
    global MOCK_DATA, CURRENT_DATA_FILE
    
    try:
        current_file = get_current_data_file()
        if current_file and current_file.exists():
            # Check if disk file is newer than memory data
            file_mtime = current_file.stat().st_mtime
            
            # If we don't have a current file tracked, reload
            if CURRENT_DATA_FILE is None:
                print("RELOADING: No current file tracked, reloading data from disk...")
                return reload_mock_data()
            
            # If disk file is newer, reload
            if current_file != CURRENT_DATA_FILE:
                print(f"RELOADING: Disk file changed from {CURRENT_DATA_FILE} to {current_file}, reloading...")
                return reload_mock_data()
            
            print("✅ Memory data is in sync with disk")
            return True
            
    except Exception as e:
        print(f"WARNING: Error checking disk sync: {e}")
        return False


def force_save_and_sync():
    """Force save current memory data and ensure sync."""
    try:
        # Save current data
        save_mock_data(MOCK_DATA)
        
        # Verify sync
        if sync_memory_with_disk():
            print("✅ Data saved and synced successfully")
            return True
        else:
            print("WARNING: Data saved but sync verification failed")
            return False
    except Exception as e:
        print(f"❌ Error in force save and sync: {e}")
        return False


def refresh_sample_data():
    """Manually refresh sample data to reflect current state."""
    try:
        regenerate_sample_data()
        print("✅ Sample data refreshed successfully")
        return True
    except Exception as e:
        print(f"❌ Error refreshing sample data: {e}")
        return False


# Sales Qualification Business Logic
def calculate_lead_score(qualification_data):
    """
    Calculate lead score based on qualification data (0-100 scale).
    Higher scores indicate better qualified leads.
    """
    score = 0
    
    # Business type scoring
    business_type = qualification_data.get('business_type', '')
    if business_type == 'new_cafe':
        score += 20
    elif business_type == 'existing_business':
        score += 25
    
    # Timeline scoring (urgency)
    timeline = qualification_data.get('timeline', '').lower()
    if 'week' in timeline or 'month' in timeline:
        score += 15
    elif 'day' in timeline:
        score += 20
    elif 'soon' in timeline or 'immediate' in timeline:
        score += 25
    
    # Contact information completeness
    contact_fields = ['contact_email', 'contact_phone', 'contact_name']
    contact_score = sum(10 for field in contact_fields if qualification_data.get(field))
    score += contact_score
    
    # Business scale (existing businesses)
    business_scale = qualification_data.get('business_scale', '').lower()
    if 'location' in business_scale or 'cafe' in business_scale:
        if any(num in business_scale for num in ['3', '4', '5', '6', '7', '8', '9']):
            score += 15
        elif any(num in business_scale for num in ['1', '2']):
            score += 10
    
    # Volume expectations (new cafes)
    volume = qualification_data.get('volume', '').lower()
    if any(num in volume for num in ['200', '300', '400', '500']):
        score += 15
    elif any(num in volume for num in ['100', '150']):
        score += 10
    
    # Pain points (existing businesses - shows urgency)
    pain_points = qualification_data.get('pain_points', '').lower()
    if pain_points and len(pain_points) > 10:  # Substantial pain points
        score += 10
    
    return min(score, 100)  # Cap at 100

async def store_qualification_data(qualification_data):
    """
    Store qualification data in the sales qualification data file.
    """
    try:
        data_file = "sales_qualification_data.json"
        
        # Load existing data
        try:
            with open(data_file, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {
                "qualifications": [],
                "last_updated": datetime.now().isoformat()
            }
        
        # Calculate lead score and priority
        lead_score = calculate_lead_score(qualification_data)
        qualification_data["lead_score"] = lead_score
        
        if lead_score >= 80:
            qualification_data["priority"] = "HIGH"
        elif lead_score >= 60:
            qualification_data["priority"] = "MEDIUM"
        else:
            qualification_data["priority"] = "LOW"
        
        # Add new qualification data
        data["qualifications"].append(qualification_data)
        data["last_updated"] = datetime.now().isoformat()
        
        # Save updated data
        with open(data_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        return {
            "success": True,
            "message": f"Qualification data stored for {qualification_data.get('contact_name', 'Unknown')}",
            "qualification_id": qualification_data.get('timestamp'),
            "lead_score": lead_score,
            "priority": qualification_data["priority"]
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error storing qualification data: {str(e)}"
        }


async def get_qualification_data(qualification_id):
    """
    Retrieve qualification data by ID.
    """
    try:
        data_file = "sales_qualification_data.json"
        
        # Load existing data
        try:
            with open(data_file, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            return None
        
        # Find the qualification data by ID
        for entry in data.get('qualifications', []):
            if entry.get('id') == qualification_id:
                return entry
        
        return None
        
    except Exception as e:
        print(f"Error retrieving qualification data: {e}")
        return None

async def get_high_priority_leads():
    """
    Get all high-priority leads for sales team follow-up.
    """
    try:
        data_file = "sales_qualification_data.json"
        
        # Load existing data
        try:
            with open(data_file, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            return []
        
        # Filter high-priority leads
        high_priority_leads = [
            lead for lead in data.get('qualifications', [])
            if lead.get('priority') == 'HIGH'
        ]
        
        # Sort by lead score (highest first)
        high_priority_leads.sort(key=lambda x: x.get('lead_score', 0), reverse=True)
        
        return high_priority_leads
        
    except Exception as e:
        print(f"Error retrieving high-priority leads: {e}")
        return []

async def get_lead_summary():
    """
    Get a summary of all leads with counts by priority.
    """
    try:
        data_file = "sales_qualification_data.json"
        
        # Load existing data
        try:
            with open(data_file, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            return {"total": 0, "high": 0, "medium": 0, "low": 0}
        
        leads = data.get('qualifications', [])
        
        summary = {
            "total": len(leads),
            "high": len([l for l in leads if l.get('priority') == 'HIGH']),
            "medium": len([l for l in leads if l.get('priority') == 'MEDIUM']),
            "low": len([l for l in leads if l.get('priority') == 'LOW'])
        }
        
        return summary
        
    except Exception as e:
        print(f"Error retrieving lead summary: {e}")
        return {"total": 0, "high": 0, "medium": 0, "low": 0}


async def create_sales_handoff_summary(qualification_data, conversation_summary=""):
    """
    Create a professional sales handoff summary.
    """
    try:
        business_type = qualification_data.get('business_type', 'Unknown')
        contact_name = qualification_data.get('contact_name', 'Unknown')
        contact_email = qualification_data.get('contact_email', 'No email provided')
        contact_phone = qualification_data.get('contact_phone', 'No phone provided')
        
        # Create handoff summary
        handoff_summary = f"""
**Sales Handoff Data Collected**

**Business Profile:**
- Business Type: {business_type.replace('_', ' ').title()}
- Scale: {qualification_data.get('business_scale', 'Not specified')}
- Timeline: {qualification_data.get('timeline', 'Not specified')}

**Current Situation:**
- Pain Points: {qualification_data.get('pain_points', 'Not specified')}
- Support Needs: {qualification_data.get('support_needs', 'Not specified')}
- Coffee Style: {qualification_data.get('coffee_style', 'Not specified')}

**Contact Information:**
- Name: {contact_name}
- Phone: {contact_phone}
- Email: {contact_email}
- Role: {qualification_data.get('contact_role', 'Not specified')}

**Additional Details:**
- Equipment Needs: {qualification_data.get('equipment_needs', 'Not specified')}
- Volume: {qualification_data.get('volume', 'Not specified')}

**Conversation Summary:**
{conversation_summary if conversation_summary else 'No additional conversation details provided.'}

**Next Steps:**
Our sales team will reach out within 24 hours to discuss your specific needs and create a customized coffee program proposal.
"""
        
        return handoff_summary.strip()
        
    except Exception as e:
        return f"Error creating handoff summary: {str(e)}"


async def get_qualification_summary():
    """
    Get a summary of all stored qualification data.
    """
    try:
        data_file = "sales_qualification_data.json"
        
        with open(data_file, 'r') as f:
            data = json.load(f)
        
        qualifications = data.get('qualifications', [])
        
        summary = {
            "total_qualifications": len(qualifications),
            "last_updated": data.get('last_updated'),
            "qualifications": []
        }
        
        for qual in qualifications:
            summary["qualifications"].append({
                "business_type": qual.get('business_type'),
                "contact_name": qual.get('contact_name'),
                "contact_email": qual.get('contact_email'),
                "timeline": qual.get('timeline'),
                "timestamp": qual.get('timestamp')
            })
        
        return summary
        
    except Exception as e:
        return {"error": f"Error retrieving qualification summary: {str(e)}"}




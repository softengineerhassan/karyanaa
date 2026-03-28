from datetime import time, datetime, timedelta, date, timezone
from typing import List, Tuple, Optional

from uuid import UUID

def compute_available_slots(
    open_time: time,
    close_time: time,
    booking_date: date,
    duration_minutes: int,
    step_minutes: int,
    booked_intervals: List[dict],
    total_capacity: int,
    resource_id: Optional[UUID] = None
) -> List[dict]:
    """
    Computes available time slots in HH:MM Format with capacity info.
    """
    available_slots = []
    
    current_dt = datetime.combine(booking_date, open_time)
    end_limit_dt = datetime.combine(booking_date, close_time)
    
    parsed_booked = []
    for b in booked_intervals:
        b_s_dt = datetime.combine(booking_date, b["start_time"])
        b_e_dt = b_s_dt + timedelta(minutes=b["duration_minutes"])
        parsed_booked.append((b_s_dt, b_e_dt, b["reserved_capacity"]))

    while current_dt + timedelta(minutes=duration_minutes) <= end_limit_dt:
        slot_start = current_dt
        slot_end = current_dt + timedelta(minutes=duration_minutes)
        
        reserved_capacity = 0
        for b_s, b_e, b_cap in parsed_booked:
            if slot_start < b_e and slot_end > b_s:
                reserved_capacity += b_cap
        
        available_capacity = max(0, total_capacity - reserved_capacity)
        
        available_slots.append({
            "time": slot_start.time(),
            "time_str": slot_start.time().strftime("%I:%M %p"),
            "reserved_capacity": reserved_capacity,
            "available_capacity": available_capacity,
            "total_capacity": total_capacity
        })
            
        current_dt += timedelta(minutes=step_minutes)
        
    return available_slots

def merge_slots_into_intervals(slots: List[dict], step_minutes: int) -> List[Tuple[time, time]]:
    """
    Groups available slots (capacity > 0) into continuous [start, end] intervals.
    """
    if not slots:
        return []
        
    # Filter slots that have at least some capacity
    available_slots = [s for s in slots if s["available_capacity"] > 0]
    if not available_slots:
        return []
        
    # Sort by time just in case
    available_slots.sort(key=lambda x: x["time"])
    
    intervals = []
    if not available_slots:
        return intervals
        
    start_time = available_slots[0]["time"]
    current_time = start_time
    
    for i in range(1, len(available_slots)):
        prev_time = available_slots[i-1]["time"]
        curr_time = available_slots[i]["time"]
        
        # Convert to datetime for delta calculation
        dummy_date = date(2000, 1, 1)
        prev_dt = datetime.combine(dummy_date, prev_time)
        curr_dt = datetime.combine(dummy_date, curr_time)
        
        # If the gap is exactly step_minutes, they are continuous
        if (curr_dt - prev_dt).total_seconds() / 60 == step_minutes:
            current_time = curr_time
        else:
            # End of an interval
            # Note: The interval ends at current_time + step_minutes (approx)
            # But for Operating Hours, we usually show the window.
            # However, if it's a "slot", the last available slot is the LAST START TIME.
            # We add step_minutes to represent the full block.
            end_dt = datetime.combine(dummy_date, current_time) + timedelta(minutes=step_minutes)
            intervals.append((start_time, end_dt.time()))
            start_time = curr_time
            current_time = curr_time
            
    # Final interval
    end_dt = datetime.combine(dummy_date, current_time) + timedelta(minutes=step_minutes)
    intervals.append((start_time, end_dt.time()))
    
    return intervals

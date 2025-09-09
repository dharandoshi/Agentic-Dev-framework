#!/usr/bin/env python3
"""
Utilities MCP Server - Common Utilities for Agent Army Framework

Provides essential utility functions for all agents including:
- Date and time operations
- Timezone handling
- Timestamp formatting
- Date calculations
"""

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import pytz
from zoneinfo import ZoneInfo

from mcp import types
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio


# Initialize server
server = Server("utilities-server")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List all available utility tools."""
    return [
        types.Tool(
            name="get_current_time",
            description="Get current date and time in various formats",
            inputSchema={
                "type": "object",
                "properties": {
                    "format": {
                        "type": "string",
                        "enum": ["iso", "unix", "readable", "date_only", "time_only", "custom"],
                        "default": "iso",
                        "description": "Output format for the timestamp"
                    },
                    "custom_format": {
                        "type": "string",
                        "description": "Custom strftime format (used when format='custom')"
                    },
                    "timezone": {
                        "type": "string",
                        "default": "UTC",
                        "description": "Timezone (e.g., 'UTC', 'US/Eastern', 'Asia/Tokyo')"
                    }
                }
            }
        ),
        
        types.Tool(
            name="calculate_date",
            description="Add or subtract time from a date",
            inputSchema={
                "type": "object",
                "properties": {
                    "base_date": {
                        "type": "string",
                        "description": "Base date (ISO format or 'now' for current time)"
                    },
                    "operation": {
                        "type": "string",
                        "enum": ["add", "subtract"],
                        "description": "Whether to add or subtract time"
                    },
                    "days": {
                        "type": "integer",
                        "default": 0,
                        "description": "Number of days"
                    },
                    "hours": {
                        "type": "integer",
                        "default": 0,
                        "description": "Number of hours"
                    },
                    "minutes": {
                        "type": "integer",
                        "default": 0,
                        "description": "Number of minutes"
                    },
                    "weeks": {
                        "type": "integer",
                        "default": 0,
                        "description": "Number of weeks"
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["iso", "readable", "date_only"],
                        "default": "iso"
                    }
                },
                "required": ["operation"]
            }
        ),
        
        types.Tool(
            name="date_difference",
            description="Calculate the difference between two dates",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date (ISO format or 'now')"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date (ISO format or 'now')"
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["days", "hours", "minutes", "seconds", "all"],
                        "default": "all",
                        "description": "Unit for the difference"
                    }
                },
                "required": ["start_date", "end_date"]
            }
        ),
        
        types.Tool(
            name="convert_timezone",
            description="Convert time between timezones",
            inputSchema={
                "type": "object",
                "properties": {
                    "time": {
                        "type": "string",
                        "description": "Time to convert (ISO format or 'now')"
                    },
                    "from_timezone": {
                        "type": "string",
                        "default": "UTC",
                        "description": "Source timezone"
                    },
                    "to_timezone": {
                        "type": "string",
                        "description": "Target timezone"
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["iso", "readable", "time_only"],
                        "default": "iso"
                    }
                },
                "required": ["to_timezone"]
            }
        ),
        
        types.Tool(
            name="get_week_info",
            description="Get week number and day of week information",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "Date to check (ISO format or 'now')"
                    }
                }
            }
        ),
        
        types.Tool(
            name="format_timestamp",
            description="Format a timestamp for use in filenames or logs",
            inputSchema={
                "type": "object",
                "properties": {
                    "timestamp": {
                        "type": "string",
                        "description": "Timestamp to format (ISO format or 'now')"
                    },
                    "purpose": {
                        "type": "string",
                        "enum": ["filename", "log", "display", "sortable"],
                        "default": "display",
                        "description": "Purpose of the formatted timestamp"
                    }
                }
            }
        ),
        
        types.Tool(
            name="is_business_day",
            description="Check if a date is a business day (Mon-Fri)",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "Date to check (ISO format or 'now')"
                    },
                    "timezone": {
                        "type": "string",
                        "default": "UTC",
                        "description": "Timezone for the check"
                    }
                }
            }
        ),
        
        types.Tool(
            name="get_next_business_day",
            description="Get the next business day from a given date",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "Starting date (ISO format or 'now')"
                    },
                    "timezone": {
                        "type": "string",
                        "default": "UTC",
                        "description": "Timezone for the calculation"
                    }
                }
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls."""
    
    if name == "get_current_time":
        return await get_current_time(arguments)
    elif name == "calculate_date":
        return await calculate_date(arguments)
    elif name == "date_difference":
        return await date_difference(arguments)
    elif name == "convert_timezone":
        return await convert_timezone(arguments)
    elif name == "get_week_info":
        return await get_week_info(arguments)
    elif name == "format_timestamp":
        return await format_timestamp(arguments)
    elif name == "is_business_day":
        return await is_business_day(arguments)
    elif name == "get_next_business_day":
        return await get_next_business_day(arguments)
    else:
        return [types.TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]


async def get_current_time(args: dict) -> list[types.TextContent]:
    """Get current time in specified format and timezone."""
    format_type = args.get("format", "iso")
    tz_name = args.get("timezone", "UTC")
    custom_format = args.get("custom_format", "%Y-%m-%d %H:%M:%S")
    
    try:
        tz = pytz.timezone(tz_name)
        now = datetime.now(tz)
        
        if format_type == "iso":
            result = now.isoformat()
        elif format_type == "unix":
            result = str(int(now.timestamp()))
        elif format_type == "readable":
            result = now.strftime("%B %d, %Y at %I:%M %p %Z")
        elif format_type == "date_only":
            result = now.strftime("%Y-%m-%d")
        elif format_type == "time_only":
            result = now.strftime("%H:%M:%S")
        elif format_type == "custom":
            result = now.strftime(custom_format)
        else:
            result = now.isoformat()
        
        return [types.TextContent(
            type="text",
            text=result
        )]
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


async def calculate_date(args: dict) -> list[types.TextContent]:
    """Add or subtract time from a date."""
    base = args.get("base_date", "now")
    operation = args.get("operation")
    days = args.get("days", 0)
    hours = args.get("hours", 0)
    minutes = args.get("minutes", 0)
    weeks = args.get("weeks", 0)
    output_format = args.get("output_format", "iso")
    
    try:
        if base == "now":
            base_date = datetime.now(timezone.utc)
        else:
            base_date = datetime.fromisoformat(base)
        
        delta = timedelta(
            days=days,
            hours=hours,
            minutes=minutes,
            weeks=weeks
        )
        
        if operation == "add":
            result_date = base_date + delta
        else:
            result_date = base_date - delta
        
        if output_format == "readable":
            result = result_date.strftime("%B %d, %Y at %I:%M %p")
        elif output_format == "date_only":
            result = result_date.strftime("%Y-%m-%d")
        else:
            result = result_date.isoformat()
        
        return [types.TextContent(
            type="text",
            text=result
        )]
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


async def date_difference(args: dict) -> list[types.TextContent]:
    """Calculate difference between two dates."""
    start = args.get("start_date")
    end = args.get("end_date")
    unit = args.get("unit", "all")
    
    try:
        if start == "now":
            start_date = datetime.now(timezone.utc)
        else:
            start_date = datetime.fromisoformat(start)
        
        if end == "now":
            end_date = datetime.now(timezone.utc)
        else:
            end_date = datetime.fromisoformat(end)
        
        diff = end_date - start_date
        total_seconds = diff.total_seconds()
        
        if unit == "days":
            result = f"{diff.days} days"
        elif unit == "hours":
            result = f"{total_seconds / 3600:.2f} hours"
        elif unit == "minutes":
            result = f"{total_seconds / 60:.2f} minutes"
        elif unit == "seconds":
            result = f"{total_seconds:.0f} seconds"
        else:  # all
            days = diff.days
            hours = int((total_seconds % 86400) / 3600)
            minutes = int((total_seconds % 3600) / 60)
            seconds = int(total_seconds % 60)
            result = f"{days} days, {hours} hours, {minutes} minutes, {seconds} seconds"
        
        return [types.TextContent(
            type="text",
            text=result
        )]
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


async def convert_timezone(args: dict) -> list[types.TextContent]:
    """Convert time between timezones."""
    time_str = args.get("time", "now")
    from_tz = args.get("from_timezone", "UTC")
    to_tz = args.get("to_timezone")
    output_format = args.get("output_format", "iso")
    
    try:
        from_timezone = pytz.timezone(from_tz)
        to_timezone = pytz.timezone(to_tz)
        
        if time_str == "now":
            dt = datetime.now(from_timezone)
        else:
            dt = datetime.fromisoformat(time_str)
            if dt.tzinfo is None:
                dt = from_timezone.localize(dt)
        
        converted = dt.astimezone(to_timezone)
        
        if output_format == "readable":
            result = converted.strftime("%B %d, %Y at %I:%M %p %Z")
        elif output_format == "time_only":
            result = converted.strftime("%H:%M:%S %Z")
        else:
            result = converted.isoformat()
        
        return [types.TextContent(
            type="text",
            text=result
        )]
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


async def get_week_info(args: dict) -> list[types.TextContent]:
    """Get week information for a date."""
    date_str = args.get("date", "now")
    
    try:
        if date_str == "now":
            dt = datetime.now()
        else:
            dt = datetime.fromisoformat(date_str)
        
        week_number = dt.isocalendar()[1]
        day_of_week = dt.strftime("%A")
        day_number = dt.weekday()  # 0 = Monday
        
        result = {
            "week_number": week_number,
            "day_of_week": day_of_week,
            "day_number": day_number + 1,  # 1-based
            "is_weekend": day_number >= 5
        }
        
        return [types.TextContent(
            type="text",
            text=str(result)
        )]
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


async def format_timestamp(args: dict) -> list[types.TextContent]:
    """Format timestamp for specific purposes."""
    timestamp = args.get("timestamp", "now")
    purpose = args.get("purpose", "display")
    
    try:
        if timestamp == "now":
            dt = datetime.now()
        else:
            dt = datetime.fromisoformat(timestamp)
        
        if purpose == "filename":
            result = dt.strftime("%Y%m%d_%H%M%S")
        elif purpose == "log":
            result = dt.strftime("[%Y-%m-%d %H:%M:%S]")
        elif purpose == "sortable":
            result = dt.strftime("%Y-%m-%d_%H-%M-%S")
        else:  # display
            result = dt.strftime("%Y-%m-%d %H:%M:%S")
        
        return [types.TextContent(
            type="text",
            text=result
        )]
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


async def is_business_day(args: dict) -> list[types.TextContent]:
    """Check if date is a business day."""
    date_str = args.get("date", "now")
    tz_name = args.get("timezone", "UTC")
    
    try:
        tz = pytz.timezone(tz_name)
        
        if date_str == "now":
            dt = datetime.now(tz)
        else:
            dt = datetime.fromisoformat(date_str)
            if dt.tzinfo is None:
                dt = tz.localize(dt)
        
        is_business = dt.weekday() < 5  # Monday = 0, Friday = 4
        day_name = dt.strftime("%A")
        
        result = {
            "is_business_day": is_business,
            "day_of_week": day_name,
            "date": dt.strftime("%Y-%m-%d")
        }
        
        return [types.TextContent(
            type="text",
            text=str(result)
        )]
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


async def get_next_business_day(args: dict) -> list[types.TextContent]:
    """Get next business day from given date."""
    date_str = args.get("date", "now")
    tz_name = args.get("timezone", "UTC")
    
    try:
        tz = pytz.timezone(tz_name)
        
        if date_str == "now":
            dt = datetime.now(tz)
        else:
            dt = datetime.fromisoformat(date_str)
            if dt.tzinfo is None:
                dt = tz.localize(dt)
        
        # Move to next day
        next_day = dt + timedelta(days=1)
        
        # Skip weekends
        while next_day.weekday() >= 5:
            next_day += timedelta(days=1)
        
        result = {
            "next_business_day": next_day.strftime("%Y-%m-%d"),
            "day_of_week": next_day.strftime("%A"),
            "days_added": (next_day - dt).days
        }
        
        return [types.TextContent(
            type="text",
            text=str(result)
        )]
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


async def main():
    """Run the utilities server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="utilities-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
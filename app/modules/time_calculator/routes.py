from datetime import datetime
from datetime import timedelta

from flask import Blueprint
from flask import jsonify
from flask import render_template
from flask import request
import pytz

time_calculator_bp = Blueprint(
    'time_calculator',
    __name__,
    template_folder='templates',
    static_folder='static',
    url_prefix='/time-calculator',
)

# Constants for time unit conversions
SECONDS_PER_MINUTE = 60
SECONDS_PER_HOUR = 3600
SECONDS_PER_DAY = 86400
SECONDS_PER_WEEK = 604800
SECONDS_PER_MONTH = 2592000  # Approximation: 30 days
SECONDS_PER_YEAR = 31536000  # Approximation: 365 days

# Conversion factors to seconds
TIME_UNIT_TO_SECONDS = {
    'seconds': 1,
    'minutes': SECONDS_PER_MINUTE,
    'hours': SECONDS_PER_HOUR,
    'days': SECONDS_PER_DAY,
    'weeks': SECONDS_PER_WEEK,
    'months': SECONDS_PER_MONTH,
    'years': SECONDS_PER_YEAR,
}


# Helper functions
def convert_to_seconds(value, unit):
    """Convert a time value from specified unit to seconds."""
    return value * TIME_UNIT_TO_SECONDS.get(unit, 0)


def convert_from_seconds(seconds, unit):
    """Convert seconds to specified time unit."""
    return seconds / TIME_UNIT_TO_SECONDS.get(unit, 1)


@time_calculator_bp.route('/')
def index():
    """Render the time calculator homepage.

    Returns:
        str: Rendered HTML template for the time calculator interface.
    """
    # Get all timezone data for the timezone converter
    timezones = sorted(pytz.common_timezones)

    # If it's an AJAX request, render only the content
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('time_calculator/content.html', timezones=timezones)

    # Normal rendering for full page load
    return render_template('time_calculator.html', timezones=timezones)


@time_calculator_bp.route('/calculate', methods=['POST'])
def calculate():
    """Handle all time calculation operations.

    Supports various calculation types:
    - add_subtract: Add or subtract time
    - difference: Calculate time difference
    - convert_units: Convert between time units
    - divide_interval: Divide time interval into equal parts
    - timezone_convert: Convert time between timezones

    Returns:
        str/json: Rendered HTML template or JSON with the calculation result
    """
    calculation_type = request.form.get('calculation_type')
    response_format = request.form.get('format', 'html')

    # Common context to be extended by each calculation type
    context = {
        'calculation_type': calculation_type,
    }

    try:
        # Router to different calculation handlers based on type
        if calculation_type == 'add_subtract':
            result = handle_add_subtract()
        elif calculation_type == 'difference':
            result = handle_difference()
        elif calculation_type == 'convert_units':
            result = handle_convert_units()
        elif calculation_type == 'divide_interval':
            result = handle_divide_interval()
        elif calculation_type == 'timezone_convert':
            result = handle_timezone_convert()
        else:
            result = {'error': 'Tipo de cálculo inválido'}

        # Merge results with common context
        context.update(result)

    except Exception as e:
        context['error'] = f'Erro: {str(e)}'

    # Return JSON if requested, otherwise render template
    if response_format == 'json':
        return jsonify(context)

    # Determine which template to use based on request type
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('time_calculator/content.html', **context)
    return render_template('time_calculator.html', **context)


def handle_add_subtract():
    """Handle time addition/subtraction calculations.

    Returns:
        dict: Results of the calculation
    """
    start_time = request.form.get('start_time', '')
    operation = request.form.get('operation', 'add')
    time_input = request.form.get('time_input', '')
    time_unit = request.form.get('time_unit', 'hours')

    # Parse the input time
    start_datetime = datetime.strptime(start_time, '%H:%M')

    # Convert input to appropriate timedelta
    time_value = float(time_input)
    if time_unit == 'seconds':
        time_delta = timedelta(seconds=time_value)
    elif time_unit == 'minutes':
        time_delta = timedelta(minutes=time_value)
    elif time_unit == 'hours':
        time_delta = timedelta(hours=time_value)
    elif time_unit == 'days':
        time_delta = timedelta(days=time_value)
    elif time_unit == 'weeks':
        time_delta = timedelta(weeks=time_value)

    # Apply the operation
    if operation == 'add':
        result_datetime = start_datetime + time_delta
    else:  # subtract
        result_datetime = start_datetime - time_delta

    # Format the result
    result_time = result_datetime.strftime('%H:%M')

    return {
        'start_time': start_time,
        'operation': operation,
        'time_input': time_input,
        'time_unit': time_unit,
        'result_time': result_time,
    }


def handle_difference():
    """Handle time difference calculations.

    Handles cases where the end time is on the next day by checking if
    the end time is earlier than the start time.

    Returns:
        dict: Results of the calculation with difference in various units
    """
    start_time = request.form.get('start_time_diff', '')
    end_time = request.form.get('end_time_diff', '')
    include_date = request.form.get('include_date', 'false') == 'true'

    if include_date:
        # Parse with date and time
        start_datetime = datetime.strptime(start_time, '%Y-%m-%d %H:%M')
        end_datetime = datetime.strptime(end_time, '%Y-%m-%d %H:%M')
    else:
        # Parse the input times (time only)
        start_datetime = datetime.strptime(start_time, '%H:%M')
        end_datetime = datetime.strptime(end_time, '%H:%M')

        # Handle cases where end time is on the next day
        if end_datetime < start_datetime:
            # Add a day to end_datetime
            end_datetime = end_datetime.replace(day=2)  # Arbitrary day change to represent next day
            start_datetime = start_datetime.replace(day=1)  # Ensure consistent day reference

    # Calculate the difference
    time_diff = end_datetime - start_datetime

    # Calculate differences in various units
    total_seconds = time_diff.total_seconds()
    total_minutes = total_seconds / 60
    total_hours = total_minutes / 60
    total_days = total_hours / 24
    total_weeks = total_days / 7

    # Format for display
    diff_hours = int(total_seconds // 3600)
    diff_minutes = int((total_seconds % 3600) // 60)
    diff_seconds = int(total_seconds % 60)

    return {
        'start_time_diff': start_time,
        'end_time_diff': end_time,
        'include_date': include_date,
        'diff_hours': diff_hours,
        'diff_minutes': diff_minutes,
        'diff_seconds': diff_seconds,
        'total_seconds': round(total_seconds, 2),
        'total_minutes': round(total_minutes, 2),
        'total_hours': round(total_hours, 2),
        'total_days': round(total_days, 2),
        'total_weeks': round(total_weeks, 2),
    }


def handle_convert_units():
    """Handle time unit conversions.

    Returns:
        dict: Results of the unit conversion
    """
    value = float(request.form.get('value', 0))
    from_unit = request.form.get('from_unit')
    to_unit = request.form.get('to_unit')

    # Convert to seconds first, then to target unit
    seconds = convert_to_seconds(value, from_unit)
    result = convert_from_seconds(seconds, to_unit)

    return {'value': value, 'from_unit': from_unit, 'to_unit': to_unit, 'result': round(result, 4)}


def handle_divide_interval():
    """Handle dividing a time interval into equal parts.

    Returns:
        dict: Results with the divided intervals
    """
    start_time = request.form.get('start_interval', '')
    end_time = request.form.get('end_interval', '')
    divisions = int(request.form.get('divisions', 2))
    include_date = request.form.get('include_date_interval', 'false') == 'true'

    if include_date:
        # Parse with date and time
        start_datetime = datetime.strptime(start_time, '%Y-%m-%d %H:%M')
        end_datetime = datetime.strptime(end_time, '%Y-%m-%d %H:%M')
        time_format = '%Y-%m-%d %H:%M'
    else:
        # Parse the input times (time only)
        start_datetime = datetime.strptime(start_time, '%H:%M')
        end_datetime = datetime.strptime(end_time, '%H:%M')
        time_format = '%H:%M'

        # Handle cases where end time is on the next day
        if end_datetime < start_datetime:
            end_datetime = end_datetime.replace(day=2)
            start_datetime = start_datetime.replace(day=1)

    # Calculate the total duration
    total_duration = end_datetime - start_datetime

    # Calculate the duration of each division
    division_duration = total_duration / divisions

    # Calculate each interval
    intervals = []
    for i in range(divisions + 1):
        current_time = start_datetime + (division_duration * i)
        intervals.append(current_time.strftime(time_format))

    # Calculate duration in readable format
    duration_seconds = division_duration.total_seconds()
    hours = int(duration_seconds // 3600)
    minutes = int((duration_seconds % 3600) // 60)
    seconds = int(duration_seconds % 60)
    readable_duration = f'{hours}h {minutes}m {seconds}s'

    return {
        'start_interval': start_time,
        'end_interval': end_time,
        'divisions': divisions,
        'include_date_interval': include_date,
        'intervals': intervals,
        'division_duration': readable_duration,
    }


def handle_timezone_convert():
    """Handle timezone conversion.

    Returns:
        dict: Results of the timezone conversion
    """
    source_time = request.form.get('source_time', '')
    source_timezone = request.form.get('source_timezone')
    target_timezones = request.form.getlist('target_timezones[]')

    # Parse the input time in the source timezone
    source_tz = pytz.timezone(source_timezone)

    # If time includes date use different format
    if len(source_time) > 5:
        source_datetime = datetime.strptime(source_time, '%Y-%m-%d %H:%M')
    else:
        # If just time, use today's date
        source_datetime = datetime.strptime(source_time, '%H:%M')
        source_datetime = datetime.now().replace(
            hour=source_datetime.hour, minute=source_datetime.minute, second=0, microsecond=0
        )

    # Localize the datetime to the source timezone
    source_datetime = source_tz.localize(source_datetime)

    # Convert to target timezones
    conversions = []
    for target_tz_name in target_timezones:
        target_tz = pytz.timezone(target_tz_name)
        target_datetime = source_datetime.astimezone(target_tz)

        # Check if DST is in effect
        is_dst = target_datetime.dst() != timedelta(0)

        conversions.append(
            {
                'timezone': target_tz_name,
                'time': target_datetime.strftime('%H:%M'),
                'full_datetime': target_datetime.strftime('%Y-%m-%d %H:%M'),
                'dst_active': is_dst,
            }
        )

    return {
        'source_time': source_time,
        'source_timezone': source_timezone,
        'target_timezones': target_timezones,
        'conversions': conversions,
    }


@time_calculator_bp.route('/timer', methods=['GET', 'POST'])
def timer():
    """Handle timer functionality.

    GET: Return timer page
    POST: Store timer state

    Returns:
        str/json: Rendered template or JSON response
    """
    if request.method == 'POST':
        return jsonify({'success': True})

    # For GET requests, render the timer page
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('time_calculator/timer.html')
    return render_template('time_calculator/timer_full.html')


@time_calculator_bp.route('/stopwatch', methods=['GET', 'POST'])
def stopwatch():
    """Handle stopwatch functionality.

    GET: Return stopwatch page
    POST: Store lap times

    Returns:
        str/json: Rendered template or JSON response
    """
    if request.method == 'POST':
        return jsonify({'success': True})

    # For GET requests, render the stopwatch page
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render_template('time_calculator/stopwatch.html')
    return render_template('time_calculator/stopwatch_full.html')

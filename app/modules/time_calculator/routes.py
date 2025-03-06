from datetime import datetime, timedelta

from flask import Blueprint, render_template, request

time_calculator_bp = Blueprint(
    "time_calculator",
    __name__,
    template_folder="templates",
    static_folder="static",
    url_prefix="/time-calculator",
)


@time_calculator_bp.route("/")
def index():
    return render_template("time_calculator.html")


@time_calculator_bp.route("/calculate", methods=["POST"])
def calculate_time():
    calculation_type = request.form.get("calculation_type", "add_subtract")
    start_time = request.form.get("start_time", "")
    operation = request.form.get("operation", "add")
    hours = int(request.form.get("hours", 0))
    minutes = int(request.form.get("minutes", 0))

    try:
        # Parse the input time
        start_datetime = datetime.strptime(start_time, "%H:%M")

        # Calculate the time difference
        time_delta = timedelta(hours=hours, minutes=minutes)

        # Apply the operation
        if operation == "add":
            result_datetime = start_datetime + time_delta
        else:  # subtract
            result_datetime = start_datetime - time_delta

        # Format the result
        result_time = result_datetime.strftime("%H:%M")

        return render_template(
            "time_calculator.html",
            calculation_type=calculation_type,
            start_time=start_time,
            operation=operation,
            hours=hours,
            minutes=minutes,
            result_time=result_time,
        )
    except ValueError:
        return render_template(
            "time_calculator.html",
            calculation_type=calculation_type,
            error="Formato de hora inválido. Use HH:MM",
        )


@time_calculator_bp.route("/calculate-difference", methods=["POST"])
def calculate_time_difference():
    calculation_type = request.form.get("calculation_type", "difference")
    start_time = request.form.get("start_time_diff", "")
    end_time = request.form.get("end_time_diff", "")

    try:
        # Parse the input times
        start_datetime = datetime.strptime(start_time, "%H:%M")
        end_datetime = datetime.strptime(end_time, "%H:%M")

        # Handle cases where end time is on the next day
        if end_datetime < start_datetime:
            # Add a day to end_datetime
            end_datetime = end_datetime.replace(day=2)  # Arbitrary day change to represent next day
            start_datetime = start_datetime.replace(day=1)  # Ensure consistent day reference

        # Calculate the difference
        time_diff = end_datetime - start_datetime

        # Extract hours and minutes
        total_seconds = time_diff.total_seconds()
        diff_hours = int(total_seconds // 3600)
        diff_minutes = int((total_seconds % 3600) // 60)

        return render_template(
            "time_calculator.html",
            calculation_type=calculation_type,
            start_time_diff=start_time,
            end_time_diff=end_time,
            diff_hours=diff_hours,
            diff_minutes=diff_minutes,
        )
    except ValueError:
        return render_template(
            "time_calculator.html",
            calculation_type=calculation_type,
            error="Formato de hora inválido. Use HH:MM",
        )

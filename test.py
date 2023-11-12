from datetime import datetime, timedelta
def check_if_one_week_passed(reference_date_str):
    # Convert the reference date string to a datetime object
    reference_date = datetime.strptime(reference_date_str, '%d-%m-%Y')

    # Calculate one week from the reference date
    one_week_later = reference_date + timedelta(days=7)

    # Get the current date
    current_date = datetime.now()

    # Check if today is exactly one week from the reference date
    if current_date.day == one_week_later.day:
        print(f"Today is exactly one week from {reference_date_str}.")
    else:
        print(f"Today is NOT exactly one week from {reference_date_str}.")
        

# Example usage:
reference_date_str = "05-11-2023"  # Replace with your reference date string
check_if_one_week_passed(reference_date_str)
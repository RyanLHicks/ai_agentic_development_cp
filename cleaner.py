import pandas as pd
import re

def clean_phone_number(phone):
    # Strip all non-numeric characters
    numeric_phone = re.sub(r'[^0-9]', '', str(phone))
    
    # Check if the remaining number is 10 digits
    if len(numeric_phone) == 10:
        # Format as (XXX) XXX-XXXX
        return f"({numeric_phone[0:3]}) {numeric_phone[3:6]}-{numeric_phone[6:10]}"
    else:
        return 'INVALID'

def validate_email(email):
    # Basic regex for email validation
    # This pattern checks for: 
    # 1. Alphanumeric characters, plus periods, underscores, percent, plus, or hyphens before the @
    # 2. An @ symbol
    # 3. Alphanumeric characters, plus periods or hyphens after the @
    # 4. A period
    # 5. 2 to 4 alphanumeric characters for the domain extension
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$'
    return bool(re.match(pattern, str(email)))

def main():
    # Load the messy data
    try:
        df = pd.read_csv('messy_leads.csv')
        print("Messy data loaded successfully.")
    except FileNotFoundError:
        print("Error: messy_leads.csv not found. Please ensure the file exists.")
        return

    # 1. Clean Names: Convert Full_Name to Title Case
    df['Full_Name'] = df['Full_Name'].str.title()
    print("Full_Name column cleaned to Title Case.")

    # 2. Standardize Phones: Strip non-numeric and format or mark as INVALID
    df['Phone_Number'] = df['Phone_Number'].apply(clean_phone_number)
    print("Phone_Number column standardized.")

    # 3. Parse Dates: Standardize Signup_Date to YYYY-MM-DD, coerce errors to NaT
    df['Signup_Date'] = pd.to_datetime(df['Signup_Date'], errors='coerce').dt.strftime('%Y-%m-%d')
    print("Signup_Date column parsed and standardized.")

    # 4. Validate Emails: Create a boolean column for valid emails
    df['is_valid_email'] = df['Email'].apply(validate_email)
    print("Email column validated.")

    # Identify rows with any invalid data (invalid email, invalid phone, or NaT date)
    # Note: Signup_Date will be a string 'NaT' if coerced, so we check for that.
    invalid_data_mask = (~df['is_valid_email']) | \
                        (df['Phone_Number'] == 'INVALID') | \
                        (df['Signup_Date'] == 'NaT')

    # Split data into clean and error DataFrames
    clean_df = df[~invalid_data_mask].copy()
    error_df = df[invalid_data_mask].copy()

    # Drop the temporary 'is_valid_email' column from the clean DataFrame
    clean_df = clean_df.drop(columns=['is_valid_email'])

    # Save the cleaned data
    clean_df.to_csv('clean_data.csv', index=False)
    print(f"Clean data saved to clean_data.csv ({len(clean_df)} rows).")

    # Save the error log
    # For the error log, it's useful to keep `is_valid_email` to see why it was invalid
    error_df.to_csv('error_log.csv', index=False)
    print(f"Error log saved to error_log.csv ({len(error_df)} rows).")

    print("Data cleaning process completed!")

if __name__ == "__main__":
    main()

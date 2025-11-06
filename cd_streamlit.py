import streamlit as st
import re

# --- CORE NL2CODE LOGIC (Copied from nl2code_converter.py) ---

def convert_nl_to_code(nl_input: str) -> str:
    """
    Converts a natural language command into a Python code string using rule-based parsing.
    """
    input_lower = nl_input.strip().lower()

    # Helper to format values for Python output (string vs. numeric)
    def format_value(val):
        # Checks if the value is purely numeric (handles floats and integers)
        return val if val.replace('.', '', 1).isdigit() else f"'{val}'"

    # 1. Command: Basic Arithmetic (Add, Subtract)
    if input_lower.startswith("add") or input_lower.startswith("subtract"):
        numbers = [float(n) for n in re.findall(r'\b\d+\.?\d*\b', input_lower)]
        if len(numbers) >= 2:
            num1 = numbers[0]
            num2 = numbers[1]
            if input_lower.startswith("add"):
                operation = " + "
                result_var = "sum_result"
            else:
                operation = " - "
                result_var = "diff_result"
            return f"# Python Arithmetic\n{result_var} = {num1}{operation}{num2}\nprint(f\"The result is: {{{result_var}}}\")"

    # 2. Command: Loop (Iteration) - Print all numbers from X to Y
    if input_lower.startswith("print all numbers from"):
        match = re.search(r'from (\d+) to (\d+)', input_lower)
        if match:
            start = int(match.group(1))
            end = int(match.group(2))
            return f"# Python Loop (inclusive end)\nfor i in range({start}, {end + 1}):\n    print(i)"

    # 3. Command: List Creation
    if input_lower.startswith("create a list named"):
        name_match = re.search(r'named (\w+)', input_lower)
        if name_match:
            list_name = name_match.group(1)
            with_index = input_lower.find('with')
            if with_index != -1:
                item_string = input_lower[with_index + 4:].strip()
                items = re.split(r'\s+', item_string)
                quoted_items = [f"'{item.replace(r'[^a-z0-9]', '')}'" for item in items if item]
                return f"# Python List Creation\n{list_name} = [{', '.join(quoted_items)}]\nprint(f\"Created list {list_name}: {{{list_name}}}\")"
        
    # 4. Command: Function Definition
    if input_lower.startswith("define a function named"):
        name_match = re.search(r'named (\w+)', input_lower)
        message_match = re.search(r'prints (.*)', input_lower)
        if name_match and message_match:
            func_name = name_match.group(1)
            message = message_match.group(1).strip().strip("'").strip('"').replace("'", "\\'")
            return f"# Python Function Definition\ndef {func_name}():\n    print('{message}')\n\n# Call the function to test\n{func_name}()"
        
    # 5. Conditional (If/Else) - If X is greater than Y, print Z, else print W
    if input_lower.startswith("if"):
        match = re.search(r'if (\d+) is greater than (\d+), print (.+?), else print (.*)', input_lower)
        if match:
            num1 = match.group(1)
            num2 = match.group(2)
            msg1 = match.group(3).strip().strip("'").strip('"').replace("'", "\\'")
            msg2 = match.group(4).strip().strip("'").strip('"').replace("'", "\\'")
            return f"# Python Conditional Statement\nif {num1} > {num2}:\n    print('{msg1}')\nelse:\n    print('{msg2}')"

    # 6. Dictionary Creation - Create a dictionary named N with key K1 set to V1 and key K2 set to V2
    if input_lower.startswith("create a dictionary named"):
        match = re.search(r'create a dictionary named (\w+) with key (\w+) set to (.+?) and key (\w+) set to (.+)', input_lower)
        if match:
            dict_name = match.group(1)
            key1 = match.group(2)
            val1 = match.group(3).strip()
            key2 = match.group(4)
            val2 = match.group(5).strip()
            
            code = (
                f"# Python Dictionary Creation\n"
                f"{dict_name} = {{'{key1}': {format_value(val1)}, '{key2}': {format_value(val2)}}}"
                f"\nprint(f\"Created dictionary {dict_name}: {{{dict_name}}}\")"
            )
            return code

    # 7. String Reversal - Reverse the string 'text'
    if input_lower.startswith("reverse the string"):
        match = re.search(r"reverse the string ['\"](.*?)['\"]", input_lower)
        if match:
            original_string = match.group(1)
            var_name = "original_string"
            reversed_var_name = "reversed_string"
            
            return (
                f"# Python String Reversal using slicing\n"
                f"{var_name} = '{original_string}'\n"
                f"{reversed_var_name} = {var_name}[::-1]\n"
                f"print(f\"Original: {{{var_name}}}\")\n"
                f"print(f\"Reversed: {{{reversed_var_name}}}\")"
            )

    return "# Error: Command not recognized or invalid format.\n# Please check the list of supported commands."


# --- STREAMLIT APP LAYOUT ---

st.set_page_config(page_title="NL2Code Demo", layout="wide")

st.title("🐍 Natural Language to Python Code Converter (Streamlit)")
st.markdown("Enter a command below and click **Convert** to generate the corresponding Python code.")

col1, col2 = st.columns(2)

with col1:
    st.header("1. Enter Command")
    
    # Text area for user input
    user_input = st.text_area(
        "Natural Language Command:",
        placeholder="Example: Create a dictionary named profile with key city set to London and key population set to 8000000",
        height=150
    )
    
    # Conversion button
    if st.button("Convert to Code", type="primary"):
        # Process the input if the button is clicked
        if user_input:
            generated_code = convert_nl_to_code(user_input)
            st.session_state['generated_code'] = generated_code
        else:
            st.session_state['generated_code'] = "# Please enter a command."

with col2:
    st.header("2. Generated Python Code")
    
    # Display the output code
    if 'generated_code' in st.session_state:
        st.code(st.session_state['generated_code'], language='python')
    else:
        st.code("# Code will appear here after conversion.", language='python')

st.markdown("---")

st.subheader("Supported Commands")
st.markdown(
    """
* **Arithmetic:** `Add 10 and 5` / `Subtract 20 and 3`
* **Loop:** `Print all numbers from 1 to 5`
* **List:** `Create a list named animals with dog cat bird`
* **Function:** `Define a function named greeting that prints hello world`
* **Conditional:** `If 20 is greater than 10, print big, else print small`
* **Dictionary:** `Create a dictionary named user with key name set to Alice and key age set to 30`
* **String:** `Reverse the string 'programming'`
"""
)
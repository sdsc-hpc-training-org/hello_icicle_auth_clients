from prompt_toolkit.formatted_text import HTML
from prompt_toolkit import prompt
from prompt_toolkit import Form
from prompt_toolkit import print_formatted_text as print_text

def submit(form):
    # Access form data
    username = form['username'].text
    password = form['password'].text
    
    # Perform some action with the submitted data
    print_text(HTML(f"<ansigreen>Submitted:</ansigreen> Username={username}, Password={password}"))

def main():
    # Define the form fields
    form = Form(
        [
            ("Username: ", "username"),
            ("Password: ", "password"),
        ],
        submit=submit,
        style="class:form",
    )

    # Run the form
    print_text(HTML("<b>Please enter your credentials:</b>"))
    form.run()

if __name__ == '__main__':
    main()
import requests
from jira import JIRA

# JIRA Configuration
JIRA_SERVER = 'https://your_jira_instance.atlassian.net'
JIRA_USERNAME = 'your_jira_username'
JIRA_API_TOKEN = 'your_jira_api_token'

# Splunk Configuration
SPLUNK_API_BASE = 'https://your_splunk_instance/services/search/jobs'
SPLUNK_API_KEY = 'your_splunk_api_key'
SPLUNK_USER = 'your_splunk_username'
SPLUNK_PASSWORD = 'your_splunk_password'

# Initialize JIRA client
jira_options = {'server': JIRA_SERVER}
jira = JIRA(options=jira_options, basic_auth=(JIRA_USERNAME, JIRA_API_TOKEN))

def get_jira_issues_with_spl(jql_query):
    # Fetch Jira issues based on a JQL query
    return jira.search_issues(jql_query)

def extract_spl_from_issue(issue):
    # Extract SPL from a specific custom field in the Jira issue
    # Assuming the SPL query is stored in a custom field 'customfield_12345'
    return issue.fields.customfield_12345

def run_spl_query(spl_query):
    # Run the SPL query using Splunk API
    headers = {
        'Authorization': f'Bearer {SPLUNK_API_KEY}',
    }
    
    data = {
        'search': spl_query,
        'output_mode': 'json'
    }
    
    response = requests.post(SPLUNK_API_BASE, headers=headers, data=data, auth=(SPLUNK_USER, SPLUNK_PASSWORD))
    
    if response.status_code == 201:
        job = response.json()
        return job  # Returning the job details for further checks
    else:
        return None  # Handle the failure case

def add_comment_to_jira(issue_key, comment):
    # Add a comment to a Jira issue
    jira.add_comment(issue_key, comment)

def block_jira_issue(issue_key):
    # Transition the issue to a blocked state, assuming you know the transition ID for blocking
    transition_id = 'block_transition_id'  # Replace with the actual transition ID
    jira.transition_issue(issue_key, transition=transition_id)

def process_jira_issues():
    # Example JQL Query to find issues with SPL queries
    jql_query = 'project = YOURPROJECT AND "SPL Query" IS NOT EMPTY'
    issues = get_jira_issues_with_spl(jql_query)

    for issue in issues:
        issue_key = issue.key
        spl_query = extract_spl_from_issue(issue)

        if spl_query:
            result = run_spl_query(spl_query)
            
            if result:  # If Splunk query succeeded
                add_comment_to_jira(issue_key, "SPL query ran successfully.")
            else:  # If Splunk query failed
                add_comment_to_jira(issue_key, "SPL query failed to run. Blocking the issue.")
                block_jira_issue(issue_key)

if __name__ == "__main__":
    process_jira_issues()

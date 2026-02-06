from google_auth_oauthlib.flow import InstalledAppFlow

auth_flow = InstalledAppFlow.from_client_secrets_file(
    client_secrets_file="client_secret.json",
    scopes=["https://www.googleapis.com/auth/drive"]
)

creds = auth_flow.run_local_server(port=8080, prompt="consent")

with open("token.json", "w") as f:
    f.write(creds.to_json())

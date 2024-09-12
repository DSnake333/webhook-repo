# GitHub Webhook Events Tracker

This project tracks GitHub webhook events such as pushes, pull requests, and merges, and displays them on a local web server.

## Getting Started

### Prerequisites

- Python 3.x
- `pip` (Python package installer)

### Setup

1. **Clone the Repositories**

   Clone both the `action-repo` and `webhook-repo` repositories to your local machine.

   ```bash
   git clone <URL-to-action-repo>
   git clone <URL-to-webhook-repo>
   
2. **Create a Virtual Environment**

Navigate to the webhook-repo directory and create a virtual environment:
```bash
python -m venv myenv
```
Activate the virtual environment:

On Windows:
```bash
.\myenv\Scripts\activate
```
On macOS/Linux:
```bash
source myenv/bin/activate
```

3. **Install Dependencies**

Install the required Python packages:
```bash
pip install -r requirements.txt
```
4. **Run the Flask Server**

Start the Flask server:
```bash
flask run
```
5. **Forward Webhooks with smee.io**

Go to smee.io, create a new channel and copy the Webhook Proxy URL

Open another terminal and run the following command to forward GitHub webhook payloads to your locally running application:
```bash
smee --url <Webhook Proxy URL> --target <The local address your flask server runs on>/webhook
```
This allows GitHub to send webhook events to your local server, as GitHub does not support localhost URLs for webhooks.

Usage
Access the web server at local flask server address (example: http://127.0.0.1:5000) to view the latest events.
The events endpoint at /events provides a JSON response with all recorded events.

*Notes*

Ensure that the webhook-repo contains the necessary code for handling GitHub webhooks.
The action-repo is used for GitHub actions and does not need specific configuration for this setup.

*Troubleshooting*

If you encounter issues with dependencies or module imports, ensure that the virtual environment is activated and dependencies are installed correctly.
For issues with smee.io, make sure the URL and target are correctly specified. You can contact me if you have any other queries.

**License**

This project is licensed under the MIT License - see the LICENSE file for details.

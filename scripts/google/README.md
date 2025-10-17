# Google Marketing Automation Toolkit

This folder contains scripts that wire Google Tag Manager, GA4, and Google Ads together for the `book_appointment_conversion` event. Populate `config.yaml` with the required credentials and IDs, then run the scripts.

---

## Setup Log (Why things look the way they do)
1. **Initial YAML** – started with many manual fields (IDs, hints). That proved noisy and redundant.
2. **Partial automation** – added `configure.py` to auto-discover GTM/GA4/Ads resources using the APIs, keeping the IDs in `config.yaml` so repeat runs are silent.
3. **Credential reduction** – eliminated manually copied client IDs/secrets; the scripts now read them directly from the OAuth desktop client JSON.
4. **Auto refresh-token fetch** – if `oauth.refresh_token` is missing, `configure.py` launches the OAuth consent flow and stores the token for you.
5. **Optional Ads** – Ads discovery only runs when a developer token is present. You can add it later and rerun.
6. **Inline sourcing guidance** – key fields in `config.yaml` contain comments showing exactly where to obtain the credentials (service account key, OAuth JSON, developer token).
7. **Minimal file structure** – `scripts/google/credentials/` is created automatically (and git-ignored) so you can drop the JSON files there with no extra setup.

---

## 1. Prepare Your Environment
1. Open a terminal at the project root.
2. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r scripts/google/requirements.txt
   ```
3. Run the configurator once to generate `scripts/google/config.yaml`:
   ```bash
   python scripts/google/configure.py
   ```
   The first run does two things:
   - Creates `config.yaml` with placeholders (and comments pointing to the right consoles).
   - Builds `scripts/google/credentials/` if it doesn’t already exist.

4. **Populate the critical secrets** (everything else stays blank and will be filled in for you):
   1. **GA4 service account key** – In Google Cloud Console:
      - Go to **IAM & Admin → Service Accounts**.
      - Pick the service account that has Editor access to your GA4 property.
      - Click **Keys → Add Key → Create new key → JSON**.
      - Save the file to `scripts/google/credentials/service-account.json` (or adjust `project.service_account_key`).
   2. **OAuth desktop client JSON** – In Google Cloud Console:
      - Navigate to **APIs & Services → Credentials**.
      - Click **Create Credentials → OAuth client ID → Desktop app**.
      - Download the JSON and save it to `scripts/google/credentials/oauth-client.json` (or adjust `oauth.client_secrets_file`).
   3. **Google Ads developer token (optional but required for Ads automation)**:
      - Sign in to [ads.google.com](https://ads.google.com/).
      - Open **Tools & settings → Setup → API Center**.
      - Copy the **Developer token** into `ads.developer_token`.
      - If you use a manager account (MCC), note the ID (top-right header) and place it in `ads.login_customer_id` (no dashes).

5. **Run the configurator again**:
   ```bash
   python scripts/google/configure.py
   ```
   - If `oauth.refresh_token` is blank, a browser window opens, you log in with the Google user that manages GTM/Ads, approve the scopes, and the script saves the refresh token into `config.yaml`.
   - GTM, GA4, and (if the developer token is present) Ads resources are discovered. When multiple options exist you’ll select from a menu once; the IDs are stored for subsequent runs.
   - If you skip the Ads developer token, the script configures GTM and GA4 and prints a reminder that Ads was skipped.

---

## 2. Google Cloud Project + Service Account (GA4 Admin API)
Populate `project.id` and `project.service_account_key`.

1. Visit [Google Cloud Console](https://console.cloud.google.com/).
2. Choose the project you already use for marketing automation or create a new one.
3. Enable the **Google Analytics Admin API** (`APIs & Services` → `Library`).
4. Go to `IAM & Admin` → `Service Accounts` → **Create service account**.
   - Name it (e.g., `ga4-automation`).
   - Grant the **Editor** role (or a custom role with GA Admin permissions).
5. Open the new service account → **Keys** → **Add key** → **Create new key** → JSON.
6. Save the JSON to `scripts/google/credentials/service-account.json` (or adjust the path in `config.yaml`).
7. In GA4 (`Admin` → `Property Access Management`), add the service-account email with **Editor** access.
8. Update `config.yaml`:
   ```yaml
   project:
     id: "<cloud-project-id>"
     service_account_key: "./scripts/google/credentials/service-account.json"
   ```

---

## 3. OAuth Client + Refresh Token (for GTM + Ads APIs)
Populate the `oauth` section.

1. In Google Cloud Console go to `APIs & Services` → `Credentials`.
2. Create an **OAuth client ID**:
   - Type: **Desktop app**.
   - Download the JSON (contains the client ID/secret).
3. Enable these APIs in the project:
   - **Google Tag Manager API**
   - **Google Ads API**
4. Generate a refresh token:
   ```bash
   source .venv/bin/activate
   python - <<'PY'
   from google_auth_oauthlib.flow import InstalledAppFlow
   scopes = [
       "https://www.googleapis.com/auth/tagmanager.edit.containers",
       "https://www.googleapis.com/auth/adwords",
   ]
   flow = InstalledAppFlow.from_client_secrets_file(
       "path/to/oauth-client.json",
       scopes=scopes,
   )
   creds = flow.run_local_server(port=0, success_message="Tokens received. Copy them from the terminal.")
   print("REFRESH_TOKEN:", creds.refresh_token)
   PY
   ```
   - Replace `path/to/oauth-client.json` with the downloaded file path.
   - Log in with the Google account that has both GTM and Ads access.
5. Copy the values into `config.yaml` and rerun the configurator.

---

## 4. Google Tag Manager IDs
Populate the `gtm` section.

Leave every field in `gtm` blank on first run; the configurator will list your accounts and remember the selection once you make it. If there is only one option it auto-selects it. The stored IDs let subsequent runs proceed without prompts.

---

## 5. Google Analytics 4 Property Details
Populate the `ga4` section.

Make sure the service account has GA4 access. Then rerun the configurator; it will auto-select if only one property/stream exists or ask you once and remember the choice.

---

## 6. Google Ads Credentials
Populate the `ads` section.

1. In [ads.google.com](https://ads.google.com/) click the tools icon.
2. `Billing` → **Account settings** → copy the Customer ID, remove dashes (the configurator can locate this after the developer token is set).
3. If you operate through a manager account (MCC), copy that ID (no dashes) for `login_customer_id`. Leave blank otherwise.
4. `Tools & settings` → `Setup` → **API Center** → copy the **Developer token** (must be at least Basic status).
Add the developer token (and MCC login ID if you use one) to `config.yaml`, then rerun the configurator. It will discover all accessible customers, let you pick one once, and remember it.

---

## 7. Optional: Quota Project
If you want to bill API quota usage to a specific Google Cloud project (different from `project.id`), set:
```yaml
quota_project: "my-alt-project"
```
Otherwise leave it empty.

---

## 8. Verify `config.yaml`
Before running anything confirm:
- The secrets section (`project`, `oauth`, `ads.developer_token`) is populated.
- The configurator has filled in the IDs under `gtm`, `ga4`, and `ads.customer_id`.
- The service-account JSON path is correct and readable.

---

## 9. Run the Toolkit
Activate the virtual environment if necessary:
```bash
source .venv/bin/activate
```

### Run Everything
```bash
python scripts/google/setup_all.py
```

### Run Individually
```bash
python -m scripts.google.gtm_sync
python -m scripts.google.ga4_setup --event book_appointment_conversion --secret-name "Server MP Secret"
python -m scripts.google.google_ads_setup --name "Book appointment conversion"
```

Each script prints success details or API error messages. Share any errors verbatim so we can debug them together.

---

## 10. Post-Run Validation
1. GTM: Publish or review the workspace changes.
2. GA4: `Configure` → `Conversions` should list `book_appointment_conversion`. If you created a Measurement Protocol secret, capture the `secret_value` printed by the script.
3. Google Ads: `Tools & settings` → `Measurement` → `Conversions` should show the action (initially “No recent conversions”). Ensure GA4↔Ads linking/import is set up.

---

## Keep Credentials Secure
- `.gitignore` excludes `scripts/google/config.yaml`, `scripts/google/credentials/`, and `.venv/`.
- Rotate service-account keys or refresh tokens as needed; update `config.yaml` and rerun `setup_all.py`.
- Never commit the populated `config.yaml` or credential files to version control.

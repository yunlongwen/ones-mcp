# Quick Start Guide ⚡

> 📌 This project uses **multi-user authentication mode**. Server only needs 2 configuration fields, user credentials are provided by clients.

## 🎯 Two-Step Configuration

### Step 1: Server Deployment (Done once by DevOps)

```bash
# 1. Navigate to project directory
cd ~/mcp-server

# 2. Configure server (only 2 fields required)
cp config.example.json config.json
nano config.json

# Edit content:
{
  "ones_api_url": "http://172.16.81.11:30011/project/api",
  "team_uuid": "y7bXyZLk"
}

# 3. One-click deployment
bash deploy.sh
```

> ✅ **Server config requires only 2 fields**: API URL and team UUID  
> ❌ **No need to configure**: User email, password, or other credentials

---

### Step 2: Client Configuration (Each User Configures Independently)

Edit Cursor's `~/.cursor/mcp.json` (Windows: `%APPDATA%\Cursor\mcp.json`):

```json
{
  "mcpServers": {
    "ones-wiki": {
      "url": "http://127.0.0.1:8000/sse",
      "description": "ONES Wiki Knowledge Base",
      "headers": {
        "x-user-email": "your_email@company.com",
        "x-user-password": "your_password",
        "x-default-space-uuid": "PLWdQVb5",
        "x-accessible-spaces": "C7ReCVYN,PLWdQVb5,Vj2fPcS7"
      }
    }
  }
}
```

**Configuration Parameters**:
- `url`: Server address (ask your DevOps team)
- `x-user-email`: **Your own** ONES email
- `x-user-password`: **Your own** ONES password
- `x-default-space-uuid`: Your frequently used space UUID (optional)
- `x-accessible-spaces`: All spaces you can access (comma-separated, optional)

> ⚠️ **Important**: Each user should use their own account credentials, do not share!

---

## ✅ Verify Configuration

### Server Verification

```bash
# Check if service is running
curl http://localhost:8000/health
# Should return: {"status":"healthy"}
```

### Client Verification

In Cursor:
1. Restart Cursor
2. Open AI chat
3. Type: `Search wiki for documents about inspection`
4. You should see search results

---

## 🔍 How to Get Configuration Parameters

### Get Server Address

Ask your DevOps team for the server IP, format: `http://<IP>:8000/sse`

### Get Space UUID

1. Open any ONES Wiki page
2. Look at the browser address bar
3. Format: `http://xxx/wiki/#/team/y7bXyZLk/space/PLWdQVb5/page/xxx`
4. Copy the `PLWdQVb5` part (space UUID)

### Get Multiple Space UUIDs

If you can access multiple spaces, list them all (comma-separated):

```json
"x-accessible-spaces": "space1,space2,space3"
```

---

## 🎉 Advantages of Multi-User Authentication

- ✅ **Simple Server**: Only 2 configuration fields (API URL and team UUID)
- ✅ **Centralized Deployment**: Only one server needed, shared by all users
- ✅ **User Independence**: Each user uses their own ONES account
- ✅ **Permission Isolation**: Based on ONES system permission control
- ✅ **Security Audit**: All operations traceable to specific users
- ✅ **No Installation**: Users don't need to install Python or other dependencies

---

## 📝 Complete Example

### Server `config.json` (DevOps Configuration)

```json
{
  "ones_api_url": "http://172.16.81.11:30011/project/api",
  "team_uuid": "y7bXyZLk"
}
```

**Note**: Server does not need to configure user email and password!

### Client `mcp.json` (User Configuration)

```json
{
  "mcpServers": {
    "ones-wiki": {
      "url": "http://127.0.0.1:8000/sse",
      "description": "ONES Wiki Knowledge Base (Multi-user Auth)",
      "headers": {
        "x-user-email": "your_email@company.com",
        "x-user-password": "your_password",
        "x-default-space-uuid": "PLWdQVb5",
        "x-accessible-spaces": "C7ReCVYN,PLWdQVb5,Vj2fPcS7"
      }
    }
  }
}
```

---

## 🛠️ FAQ

### Q: Why don't we need `client_config_example.json`?

A: Because we now configure directly in `mcp.json`, no need for a separate config file.

### Q: Does server's `config.json` need user information?

A: **No!** Only need to configure ONES API URL and team UUID. User information is passed via HTTP Headers.

### Q: Can multiple users use the same server?

A: **Yes!** This is the advantage of HTTP/SSE mode. Each user configures their own credentials in their `mcp.json`.

### Q: How to update password?

A: Simply modify `x-user-password` in `mcp.json`, then restart Cursor.

---

## 📞 Need Help?

- **Deployment Issues**: See [DEPLOY.md](DEPLOY.md)
- **Configuration Issues**: See [MCP_CLIENT_CONFIG.md](MCP_CLIENT_CONFIG.md)
- **Feature Usage**: See [README.md](../README.md)

---

**Summary**: Configure server once, each user configures their own, it's that simple! 🚀


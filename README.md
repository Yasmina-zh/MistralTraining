# Neon PostgreSQL MCP Server

A FastMCP server that connects to your Neon PostgreSQL database and exposes it as tools for AI agents (Mistral, Claude, etc.).

## Tools Available

| Tool | Description |
|------|-------------|
| `list_tables` | Lists all tables in your database |
| `describe_table(table_name)` | Shows columns and data types for a table |
| `sample_table(table_name, limit)` | Returns sample rows from a table |
| `query_database(sql)` | Runs a read-only SELECT query |

## Deploy to Horizon (fastmcp.cloud)

### Step 1 – Push this repo to GitHub
1. Create a new repository on [github.com](https://github.com)
2. Push this folder to it

### Step 2 – Deploy on Horizon
1. Go to [horizon.prefect.io](https://horizon.prefect.io) and sign in with GitHub
2. Click **+ Add server** → select your GitHub repository
3. Set the **Entrypoint** to `server.py:mcp`
4. Click **Deploy Server**

### Step 3 – Add your DATABASE_URL
1. In Horizon, open your server → **Settings** → **Environment**
2. Click **Add New Variable**
3. Name: `DATABASE_URL`
4. Value: your full Neon connection string, e.g.:
   ```
   postgresql://user:password@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require
   ```

### Step 4 – Get your URL
Your server will be live at:
```
https://your-server-name.fastmcp.app/mcp
```

### Step 5 – Add to Mistral
In Mistral, add a custom connector and paste the URL above.

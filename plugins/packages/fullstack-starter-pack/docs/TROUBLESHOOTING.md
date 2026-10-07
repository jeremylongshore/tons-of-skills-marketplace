# Troubleshooting Guide - Fullstack Starter Pack

Common issues and solutions when using the Fullstack Starter Pack.

---

## Installation Issues

### Issue: Plugins not appearing after installation

**Symptoms:**

- Installed pack but commands don't work
- Agents don't activate
- `/plugin list` doesn't show fullstack plugins

**Solutions:**

```bash
# 1. Verify installation
/plugin list | grep fullstack

# 2. Reload Claude Code
# Restart Claude Code CLI

# 3. Reinstall pack
/plugin uninstall fullstack-starter-pack
/plugin install fullstack-starter-pack@claude-code-plugins-plus

# 4. Check Claude Code version
# Requires Claude Code >=0.1.0
claude --version
```

### Issue: "Marketplace not found" error

**Solution:**

```bash
# Add marketplace first
/plugin marketplace add jeremylongshore/claude-code-plugins

# Then install pack
/plugin install fullstack-starter-pack@claude-code-plugins-plus
```

---

## Command Issues

### Issue: `/cg` command not working

**Symptoms:**

- Command not recognized
- "Unknown command" error

**Solutions:**

```bash
# 1. Use full command name
/component-generator "Button component"

# 2. Check for shortcut conflicts
/plugin list  # Look for other plugins using /cg

# 3. Verify plugin loaded
/plugin list | grep component-generator
```

### Issue: Generated code has syntax errors

**Cause:** Incomplete generation or interrupted process

**Solution:**

```bash
# 1. Re-run the command
/component-generator "Button component"

# 2. Be more specific in description
/component-generator "Button with props: variant (primary/secondary), size (sm/md/lg), onClick handler"

# 3. Review and fix manually
# Generated code is a starting point—customize as needed
```

---

## Agent Issues

### Issue: React Specialist not activating

**Symptoms:**

- Ask about React but general Claude responds
- Agent doesn't provide specialized advice

**Solutions:**

```bash
# 1. Be explicit with keywords
#  BAD: "Help me with my app"
#  GOOD: "Help me optimize React component performance"

# 2. Use activation keywords
# Keywords: react, hooks, component, state management, performance

# 3. Mention agent explicitly
"React Specialist: Review this component for best practices"
```

### Issue: Agent provides generic advice instead of code

**Cause:** Request was too vague

**Solution:**

```bash
# Be specific about what you want
#  BAD: "Help with database"
#  GOOD: "Design a PostgreSQL schema for a blog with users, posts, and comments"

#  BAD: "Make my API faster"
#  GOOD: "Review this Express API endpoint for N+1 query problems and suggest optimizations"
```

---

## Development Environment Issues

### Issue: Docker containers won't start

**Symptoms:**

- `docker-compose up` fails
- Port already in use errors

**Solutions:**

```bash
# 1. Check if ports are in use
lsof -i :3000  # Backend port
lsof -i :5173  # Frontend port
lsof -i :5432  # PostgreSQL port

# 2. Stop conflicting services
# Kill process using port or change port in docker-compose.yml

# 3. Clean Docker state
docker-compose down -v  # Remove volumes
docker system prune     # Clean up

# 4. Rebuild containers
docker-compose up --build -d
```

### Issue: Database migrations failing

**Symptoms:**

- `prisma migrate dev` fails
- "Table already exists" errors

**Solutions:**

```bash
# 1. Reset database (development only!)
npx prisma migrate reset

# 2. Check DATABASE_URL in .env
# Ensure correct format: postgresql://user:password@host:port/database

# 3. Ensure PostgreSQL is running
docker ps | grep postgres
# Or: pg_isready -h localhost -p 5432

# 4. Create database manually if needed
psql -U postgres -c "CREATE DATABASE myapp_dev;"
```

---

## Generated Project Issues

### Issue: npm install fails in generated project

**Symptoms:**

- Dependency conflicts
- Package not found errors

**Solutions:**

```bash
# 1. Clear cache
rm -rf node_modules package-lock.json
npm cache clean --force
npm install

# 2. Use correct Node version
nvm use 20  # Or version specified in package.json
node --version  # Verify

# 3. Update dependencies
npm update

# 4. Check npm registry
npm config get registry  # Should be https://registry.npmjs.org/
```

### Issue: TypeScript errors in generated code

**Symptoms:**

- Type errors in generated files
- "Cannot find module" errors

**Solutions:**

```bash
# 1. Regenerate types
npx prisma generate  # For Prisma projects

# 2. Install missing types
npm install --save-dev @types/node @types/react

# 3. Check tsconfig.json
# Ensure "strict": true and correct "include" paths

# 4. Restart TypeScript server (VS Code)
# Cmd+Shift+P → "TypeScript: Restart TS Server"
```

---

## Performance Issues

### Issue: Agent responses are slow

**Cause:** Complex requests requiring extensive analysis

**Solutions:**

```bash
# 1. Break down large requests
# Instead of: "Build complete e-commerce platform"
# Try: "/project-scaffold E-commerce" then incremental features

# 2. Use commands for code generation
# Commands are faster than asking agents to write code

# 3. Be specific to reduce analysis time
# "Generate Express API with user and post endpoints"
# vs. "Help me build a backend"
```

---

## Integration Issues

### Issue: Authentication not working in generated project

**Symptoms:**

- JWT tokens invalid
- Login fails
- Protected routes accessible without auth

**Solutions:**

```bash
# 1. Check JWT_SECRET in .env
# Must be at least 32 characters
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"

# 2. Verify token expiration
# Check JWT_EXPIRES_IN in .env (default: 15m)

# 3. Check middleware order
# Ensure authenticate middleware runs before route handlers

# 4. Verify CORS settings
# Ensure frontend origin is allowed in CORS config
```

### Issue: Database connection fails in production

**Symptoms:**

- Works locally, fails in production
- Connection timeout errors

**Solutions:**

```bash
# 1. Check DATABASE_URL format
# Production might need SSL: postgresql://user:pass@host:5432/db?sslmode=require

# 2. Verify database accessible
# Check firewall rules and security groups

# 3. Connection pooling
# Ensure proper pool settings for production load

# 4. Check environment variables
# Verify DATABASE_URL is set in production environment
```

---

## Getting Help

### Still Having Issues?

**1. Check Documentation:**

- `docs/INSTALLATION.md` - Installation steps
- `docs/QUICK_START.md` - Getting started guide
- `docs/USE_CASES.md` - Real-world examples

**2. Review Generated Code:**

- All generated code includes comments and examples
- Check README files in generated projects

**3. Ask Agents:**

- Agents can help debug issues: "Deployment Specialist: Why is my Docker build failing?"

**4. Community Support:**

- GitHub Discussions: https://github.com/jeremylongshore/claude-code-plugins/discussions
- GitHub Issues: https://github.com/jeremylongshore/claude-code-plugins/issues

**5. Report Bugs:**

```bash
# Include:
# - Claude Code version (claude --version)
# - Plugin version (/plugin list | grep fullstack)
# - Command or agent being used
# - Error message
# - Steps to reproduce
```

---

**Most issues are resolved with reinstallation or correct environment setup.**

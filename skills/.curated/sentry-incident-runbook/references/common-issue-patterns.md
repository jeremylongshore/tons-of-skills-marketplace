# Common Issue Patterns

## Common Issue Patterns

### Pattern 1: Deployment-Related Spike

**Symptoms:**

- Errors started immediately after deployment
- New error types not seen before
- Affected release matches latest deploy

**Resolution:**

1. Check commit associated with release
2. Rollback if critical
3. Hotfix if minor

### Pattern 2: Third-Party Service Failure

**Symptoms:**

- Network/timeout errors
- Errors reference external API
- Multiple users, single failure point

**Resolution:**

1. Check third-party status page
2. Enable fallback/cache if available
3. Add circuit breaker
4. Contact vendor if needed

### Pattern 3: Data/State Corruption

**Symptoms:**

- Unexpected null values
- Type errors
- Specific to certain users/records

**Resolution:**

1. Identify affected records
2. Check data migration history
3. Fix corrupted data
4. Add validation

### Pattern 4: Resource Exhaustion

**Symptoms:**

- Memory/timeout errors
- Gradual degradation
- Affects all users eventually

**Resolution:**

1. Check resource metrics
2. Identify memory leaks
3. Scale horizontally
4. Optimize resource usage

